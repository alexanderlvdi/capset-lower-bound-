#!/usr/bin/env python3
"""[independent referee checker; generalized from the referee original by walk length L / embedding step te read from the certificate (defaults 14, 7)]
[redteam2] independent checker for Lu (arXiv 2611.30110) style synchronizer family + spectral certificate.
Pure stdlib, exact int/Fraction.  Written from Lu's text only (Sec 2-5, App A) -- no import of authors' code.
usage: python3 -I redteam2_chk.py CERT.json [--lu appendix_a_data.json] [--z2]  (see main())
Provides functions used by redteam2_mut.py."""
import sys, json, itertools, collections
from fractions import Fraction as Fr
from math import isqrt

PS, PT = 0, 6
LW, TE, DD = 14, 7, 1000     # walk length, embedding step, dimension per level (72*LW-8); set from the certificate in full()
DS = (1, 2, 3, 4, 5, 7, 8, 9, 10, 11)          # ten 7-dim slots (bit 5 = embedding slot at step 7)
SC = (12, 13)                                  # scalars (bit 12 = output scalar at step 0)
REALMASK = sum(1 << b for b in DS + SC)
ALL14 = (1 << 14) - 1
bit = lambda r, k: (r >> k) & 1
src = lambda r: r & 1
tgt = lambda r: 1 - ((r >> 6) & 1)

def fr(x):
    if isinstance(x, int): return Fr(x)
    if x.startswith('10**'): return Fr(10 ** int(x[4:]))
    return Fr(x)

# ---------------------------------------------------------------- family structure
def family(rowscore):
    """rowscore: list of (mask, e or None).  Returns dict with all derived facts.  Independent derivation."""
    rows = [r for r, e in rowscore]; sc = dict(rowscore)
    n = len(rows); R = sorted(rows)
    out = {'n': n, 'distinct': len(set(rows)) == n and all(0 <= r <= ALL14 for r in rows)}
    # (a) C1 witness: every multiset {a,b,c}, not all equal, has a coordinate (ports incl.) with exactly two 1s
    bad = 0; T = {1: [], 2: []}
    for ia in range(n):
        A = R[ia]
        for ib in range(ia, n):
            B = R[ib]
            AB, AnB, nAB = A & B, A & ~B, ~A & B
            sab, tab = src(A) + src(B), tgt(A) + tgt(B)
            for ic in range(ib, n):
                C = R[ic]
                two = ((AB & ~C) | (AnB & C) | (nAB & C))   # coordinates with exactly two ones
                if ia == ib == ic: continue
                if not (two & ALL14): bad += 1
                s = sab + src(C)
                if (s == 1 or s == 2) and tab + tgt(C) == s and not (two & REALMASK):
                    T[s].append((A, B, C))
    out['C1_viol'] = bad; out['T'] = T
    out['live'] = {s: {x for t in T[s] for x in t} for s in (1, 2)}
    return out

def check_scores(fam, rowscore):
    sc = dict(rowscore); D = {1: 4, 2: 2}; bad = 0; rng = True
    for s in (1, 2):
        for t in fam['T'][s]:
            es = [sc[x] for x in t]
            if None in es or sum(es) != D[s]: bad += 1
    live_any = fam['live'][1] | fam['live'][2]
    for r, e in rowscore:
        if (r in live_any) != (e is not None): bad += 1000000
        if e is not None and e not in (0, 1, 2): rng = False
    return bad, rng

def injective(rowscore):
    return len({r & REALMASK for r, e in rowscore}) == len(rowscore)

# ---------------------------------------------------------------- types / heads / thresholds
def type_tuple(r, e):
    return (src(r), tgt(r), sum(bit(r, d) for d in DS), 2 - bit(r, 12) - bit(r, 13), 1 - bit(r, 12), e)

def types_heads(rowscore):
    tt = {r: type_tuple(r, e) for r, e in rowscore if e is not None}
    types = sorted(set(tt.values()))
    xt = {r: types.index(t) for r, t in tt.items()}
    heads = [(x, y) for x in range(len(types)) for y in range(len(types)) if types[x][1] == types[y][0]]
    H = {h: i for i, h in enumerate(heads)}
    return types, xt, heads, H

def head_triples(fam, xt, H):
    """all unordered head-type triples (multiset, repeats counted) that can occur at steps 0,1 of 3 compatible,
    non-identical closed walks, state s.  Derived from RAW rows (no type-uniformity assumption)."""
    res = {}
    for s in (1, 2):
        ordered = set()
        for t in fam['T'][s]:
            for p in itertools.permutations(t): ordered.add(p)
        by_src = collections.defaultdict(list)
        for p in ordered: by_src[tuple(src(r) for r in p)].append(p)
        hts = set()
        for p0 in ordered:
            for p1 in by_src[tuple(tgt(r) for r in p0)]:
                hts.add(tuple(sorted(H[(xt[p0[w]], xt[p1[w]])] for w in range(3))))
        res[s] = hts
    return res

def check_thresholds(hts, upper, lower):
    u1 = max(sum(upper[h] for h in t) for t in hts[1])
    l2 = min(sum(lower[h] for h in t) for t in hts[2])
    return u1, l2   # need u1 <= 47 and l2 >= 25

# ---------------------------------------------------------------- prices (Lu A.1 / Prop 5.2)
def prices_ok(nr, seed):
    z = fr(seed['z']); s, v, p, q = (fr(seed[k]) for k in 'svpq'); beta = z / 3
    def below(b, u, h):
        eta, B = nr[b]
        return h > 0 and h * (h - beta * eta * u) < beta ** 2 * eta * B
    D = 12 + 44 * s; N = 48 + 2 * D * v; x = (4 + 4 * z) / N; y = Fr(1, 16)
    e183, B183 = nr[183]; U0 = beta * e183 * (3 * x + 180 * y); R0 = beta * B183 / U0
    ok = (z > 1 and min(s, v, p, q) > 0 and below(252, Fr(251, 22), s ** 251) and below(641, 640 / D, v ** 640)
          and below(144, 137 * x + 6 * y, p ** 137 * q ** 6) and below(182, 3 * R0 + 178 * y, p ** 9 * q ** 718 / U0 ** 3))
    return ok, N, p, q

# ---------------------------------------------------------------- matrices (Lu A.2-A.4, W0 only)
def fl(q): return q.numerator // q.denominator
def ce(q): return -((-q.numerator) // q.denominator)

def row_tables(rowscore, xt, H, m, o, f, S, rnd):
    """A_d tables: for each step d, color req (a at d=0, b at d=7) -> dict key -> int.  Lu A.3 eq (A.2),(A.3)."""
    sc = dict(rowscore)
    tabs = {}
    for d in range(LW):
        for req in ((0, 1) if d in (0, TE) else (None,)):
            acc = collections.defaultdict(Fr)
            for r, e in rowscore:
                a_r = 1 - bit(r, 12); nu = 2 - bit(r, 12) - bit(r, 13); k = sum(bit(r, c) for c in DS)
                if d == 0 and a_r != req: continue
                if d == TE:
                    if bit(r, 5) != req: continue
                    k -= req
                delta = 1 if d == TE else 0
                ex = nu - (req if d == 0 else 0)
                W = Fr(2) ** ex * m ** k * o ** (10 - delta - k) / f ** (7 * (10 - delta) + 2)
                if d in (0, 1): key = (src(r), tgt(r), xt[r] if e is not None else 'B')
                else: key = (src(r), tgt(r), e if e is not None else 'B')
                acc[key] += W
            tabs[(d, req)] = {k: rnd(S * v) for k, v in acc.items()}
    return tabs

def matrix(rowscore, xt, H, upper, lower, m, o, f, S, rnd, exact=False):
    """returns 2x2 integer matrix P (rows: output colour a; cols: embedded colour b). W0 only.
    exact=True: rows tables unrounded (Fractions) -> exact K entries scaled by S/f^1000."""
    if exact: rnd_ = lambda q: q
    else: rnd_ = rnd
    tabs = row_tables(rowscore, xt, H, m, o, f, S, rnd_)
    P = [[None, None], [None, None]]
    for a in (0, 1):
        for b in (0, 1):
            # forward DP over d = 0..13.  state: (start port i, current port, head idx or 'B', g or 'B') -> weight
            st = collections.defaultdict(lambda: 0)
            for (i, j, x), w in tabs[(0, a)].items(): st[(i, j, x, None)] += w
            # step 1: combine head
            st2 = collections.defaultdict(lambda: 0)
            for (i, p, x, _), w in st.items():
                for (p2, j, y), w1 in tabs[(1, None)].items():
                    if p2 != p: continue
                    hh = 'B' if (x == 'B' or y == 'B') else H[(x, y)]
                    st2[(i, j, hh, 0)] += w * w1
            st = st2
            for d in range(2, LW):
                tb = tabs[(d, b if d == TE else None)]
                nst = collections.defaultdict(lambda: 0)
                for (i, p, hh, g), w in st.items():
                    for (p3, q3, e), w3 in tb.items():
                        if p3 != p: continue
                        ng = 'B' if (g == 'B' or e == 'B') else g + e
                        nst[(i, q3, hh, ng)] += w * w3
                st = nst
            L = 0
            for (i, p, hh, g), w in st.items():
                if p != i: continue                      # closed walk
                if hh == 'B' or g == 'B' or lower[hh] <= g <= upper[hh]: L += w
            q = f * L / Fr(S) ** (LW - 1)
            P[a][b] = q if exact else rnd(q)
    return P

def J_of(P):
    a, b, c, d = P[0][0], P[0][1], P[1][0], P[1][1]
    return (a + d + isqrt((a - d) ** 2 + 4 * b * c)) // 2

def tails_ok(J, Q):
    u, v, w, x = Q[0][0], Q[0][1], Q[1][0], Q[1][1]
    return J > max(u, x) and (J - u) * (J - x) > v * w

def final_ok(J, f, S, target):
    tg = fr(target)
    return J * f.numerator ** DD * tg.denominator ** DD > S * f.denominator ** DD * tg.numerator ** DD

def best_grid(J, f, S, G=10 ** 14):
    lo, hi = 0, 3 * G
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if J * f.numerator ** DD * G ** DD > S * f.denominator ** DD * mid ** DD: lo = mid
        else: hi = mid - 1
    return lo, G

def full(cert, verbose=True, fam_cache={}):
    global LW, TE, DD
    LW = cert.get('L', 14); TE = cert.get('te', LW // 2); DD = 72 * LW - 8
    assert 3 <= TE <= LW - 1, 'FAIL te range: need 3 <= te <= L-1'
    rs = [tuple(x) for x in cert['rows']]
    key = tuple(rs)
    if key not in fam_cache:
        fam_cache[key] = family(rs)
    fam = fam_cache[key]
    res = {}
    P = print if verbose else (lambda *a, **k: None)
    res['distinct'] = fam['distinct']
    res['C1_viol'] = fam['C1_viol']
    P('n', fam['n'], 'distinct', fam['distinct'], 'C1 violations', fam['C1_viol'], 'T1,T2', len(fam['T'][1]), len(fam['T'][2]),
      'live', len(fam['live'][1]), len(fam['live'][2]), 'live equal', fam['live'][1] == fam['live'][2])
    sb, rng = check_scores(fam, rs); res['score_bad'] = sb; res['score_rng'] = rng
    res['inj'] = injective(rs)
    P('score violations', sb, 'e in 0..2', rng, 'real-bit injective', res['inj'])
    types, xt, heads, H = types_heads(rs)
    P('types', len(types), 'heads', len(heads))
    upper, lower = cert['upper'], cert['lower']
    res['thr_len'] = len(upper) == len(lower) == len(heads)
    hts = head_triples(fam, xt, H)
    P('head-type triples/state', len(hts[1]), len(hts[2]))
    u1, l2 = check_thresholds(hts, upper, lower)
    res['u1'], res['l2'] = u1, l2
    P('max sum u (s=1)', u1, '(need<=%d)  min sum l (s=2)' % (4 * (LW - 2) - 1), l2, '(need>=%d)' % (2 * (LW - 2) + 1))
    # every head type in some triple? (informational, tightness)
    nr = {int(b): (fr(v[0]), fr(v[1])) for b, v in cert['node_rates'].items()}
    ok, N, p, q = prices_ok(nr, cert['seed']); res['prices'] = ok
    X = N * p; Y = 128 * q
    f = fr(cert['f']); S = int(fr(cert['S'])); t = fr(cert['t'])
    mats = {}
    for nm, (m, o, rnd) in {'P0': (X, 64 + Y, fl), 'P1': (X * t ** -718, 64 + Y * t ** 9, ce), 'P2': (X * t ** 6, 64 + Y * t ** -137, ce)}.items():
        mats[nm] = matrix(rs, xt, H, upper, lower, m, o, f, S, rnd)
    res['mats'] = mats
    P0 = mats['P0']
    res['pos'] = all(P0[a][b] > 0 for a in (0, 1) for b in (0, 1))
    J = J_of(P0); res['J'] = J
    # J <= rho(P0) < J+1 check via char poly
    cp = lambda x: (x - P0[0][0]) * (x - P0[1][1]) - P0[0][1] * P0[1][0]
    res['J_floor'] = (2 * J <= P0[0][0] + P0[1][1] or cp(J) <= 0) and (2 * (J + 1) > P0[0][0] + P0[1][1] and cp(J + 1) > 0)
    res['tail1'] = tails_ok(J, mats['P1']); res['tail2'] = tails_ok(J, mats['P2'])
    res['final'] = final_ok(J, f, S, cert['target'])
    res['best'] = best_grid(J, f, S)
    P('prices', ok, 'P0>0', res['pos'], 'J', J, 'floor ok', res['J_floor'], 'tails', res['tail1'], res['tail2'], 'final', res['final'])
    P('best grid', res['best'][0], '/1e14 =', res['best'][0] / 1e14)
    res['_ctx'] = (fam, rs, types, xt, heads, H)
    return res

def verdict(res):
    return (res['distinct'] and res['C1_viol'] == 0 and res['score_bad'] == 0 and res['inj'] and res['thr_len']
            and res['u1'] <= 4 * (LW - 2) - 1 and res['l2'] >= 2 * (LW - 2) + 1 and res['prices'] and res['pos'] and res['J_floor']
            and res['tail1'] and res['tail2'] and res['final'])

if __name__ == '__main__':
    cert = json.load(open(sys.argv[1]))
    try:
        res = full(cert)
    except (KeyError, AssertionError, ValueError, TypeError, IndexError) as ex:
        print('VERDICT FAIL (malformed certificate or family: %s: %s)' % (type(ex).__name__, ex)); sys.exit(1)
    print('VERDICT', 'PASS' if verdict(res) else 'FAIL')
    print('J', res['J'])
    sys.exit(0 if verdict(res) else 1)
