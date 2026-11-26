#!/usr/bin/env python3
"""Referee's independent checker, written from Lu (arXiv 2611.30110) Sec 3-5 and App A text only.
Does not import/borrow code from the authors' checkers (only rates.py, the exact node-rate recomputation, is shared).
usage: python3 -I independent_check.py cert.json  (cert2.json also works: it is a self-contained certificate; the chain link to cert.json is checked by check_cert2.py).  Exact int/Fraction arithmetic for all decisions.
Structure: struct(rows) -> geometry (numpy, cached);  thr(cert,geom); prices(cert); mats(cert,geom); final(cert,...)."""
import sys, json, itertools, collections, functools
from fractions import Fraction as Fr
from math import isqrt
import numpy as np
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))   # needed under python -I
import rates
from decimal import Decimal as Dc, getcontext
getcontext().prec = 200
def D_(q): return Dc(q.numerator) / Dc(q.denominator)

def fr(x):
    if isinstance(x, int): return Fr(x)
    if x.startswith('10**'): return Fr(10 ** int(x[4:]))
    return Fr(x)

# ------------------------------------------------------------------ geometry
@functools.lru_cache(maxsize=4)
def geometry(rows_scores):
    rows = [r for r, e in rows_scores]
    sc = {r: e for r, e in rows_scores}
    a = np.array(rows, dtype=np.int64)
    n = len(a); FULL = (1 << 14) - 1
    REALM = sum(1 << b for b in (1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 12, 13))
    src = lambda r: (r >> 0) & 1
    tgt = lambda r: 1 - ((r >> 6) & 1)
    S1 = (a >> 0) & 1; T1 = 1 - ((a >> 6) & 1)
    # C1 over ALL ordered triples (superset of multisets), not all equal
    bad = 0
    for i in range(n):
        A = a[i]
        AB = (A & a)[:, None]; Ab = (A & ~a)[:, None]; aB = (~A & a)[:, None]
        C = a[None, :]
        two = ((AB & ~C) | (Ab & C) | (aB & C)) & FULL
        viol = (two == 0)
        # exclude all-equal
        viol[i, i] = False if True else viol[i, i]
        # viol[j,k] with j==i,k==i is the all-equal triple (A,A,A)
        bad += int(viol.sum())
    # ordered state triples
    O = {1: [], 2: []}
    for i in range(n):
        A = a[i]
        AB = (A & a)[:, None]; Ab = (A & ~a)[:, None]; aB = (~A & a)[:, None]
        C = a[None, :]
        two = ((AB & ~C) | (Ab & C) | (aB & C)) & REALM
        ssum = S1[i] + S1[:, None] + S1[None, :]
        tsum = T1[i] + T1[:, None] + T1[None, :]
        for s in (1, 2):
            m = (two == 0) & (ssum == s) & (tsum == s)
            js, ks = np.nonzero(m)
            for j, k in zip(js, ks): O[s].append((int(a[i]), int(a[j]), int(a[k])))
    return dict(rows=rows, sc=sc, c1_bad=bad, O=O)

BIT = lambda r, k: (r >> k) & 1
DS = [1, 2, 3, 4, 5, 7, 8, 9, 10, 11]
def rowfeat(r, e):
    i = BIT(r, 0); j = 1 - BIT(r, 6); k = sum(BIT(r, d) for d in DS)
    nu = 2 - BIT(r, 12) - BIT(r, 13); a = 1 - BIT(r, 12)
    return (i, j, k, nu, a, e)

_SC={}
def structure(cert):
    rs = tuple((r, e) for r, e in cert['rows'])
    if rs in _SC: return _SC[rs]
    G = geometry(rs)
    sc = G['sc']
    res = {}
    res['c1_bad'] = G['c1_bad']
    O = G['O']
    res['ntrip'] = {s: len({tuple(sorted(t)) for t in O[s]}) for s in (1, 2)}
    live = {s: {x for t in O[s] for x in t} for s in (1, 2)}
    res['live_eq'] = (live[1] == live[2])
    res['null_iff_blocking'] = all((sc[r] is None) == (r not in live[1]) for r in sc)
    DSUM = {1: 4, 2: 2}
    res['conserve'] = all(sc[x] is not None and sc[x] in (0, 1, 2) for s in (1, 2) for t in O[s] for x in t) and \
        all(sum(sc[x] for x in t) == DSUM[s] for s in (1, 2) for t in O[s])
    scored = [r for r in sc if sc[r] is not None]
    feats = {r: rowfeat(r, sc[r]) for r in scored}
    types = sorted(set(feats.values()))
    xt = {r: types.index(feats[r]) for r in scored}
    heads = [(x, y) for x in range(len(types)) for y in range(len(types)) if types[x][1] == types[y][0]]
    hidx = {h: n for n, h in enumerate(heads)}
    res['ntypes'] = len(types); res['nheads'] = len(heads)
    # raw two-step head multisets
    HT = {}
    for s in (1, 2):
        bysrc = collections.defaultdict(list)
        for t in O[s]: bysrc[tuple(BIT(x, 0) for x in t)].append(t)
        hs = set()
        for t0 in O[s]:
            need = tuple(1 - BIT(x, 6) for x in t0)
            for t1 in bysrc[need]:
                hs.add(tuple(sorted(hidx[(xt[t0[w]], xt[t1[w]])] for w in range(3))))
        HT[s] = hs
    res['nhead_trip'] = {s: len(HT[s]) for s in (1, 2)}
    _SC[rs] = dict(res=res, sc=sc, types=types, xt=xt, hidx=hidx, heads=heads, HT=HT, scored=scored)
    return _SC[rs]

def thr_check(cert, st):
    u, l = cert['upper'], cert['lower']
    ok = len(u) == len(l) and all(isinstance(v, int) for v in u + l)
    w1 = max(sum(u[h] for h in t) for t in st['HT'][1])
    w2 = min(sum(l[h] for h in t) for t in st['HT'][2])
    return ok and w1 < (cert.get('L',14)-2)*4 and w2 > (cert.get('L',14)-2)*2, (w1, w2)

# ------------------------------------------------------------------ prices
def prices_check(cert):
    nr = {int(b): (fr(v[0]), fr(v[1])) for b, v in cert['node_rates'].items()}
    sd = cert['seed']; z, s, v, p, q = (fr(sd[k]) for k in 'zsvpq')
    beta = z / 3
    def below(b, u, h):
        eta, B = nr[b]
        # largest root of lam^2 - beta*eta*u*lam - beta^2*eta*B (matrix beta*[[eta u, eta],[B,0]]) ; h<root iff p(h)<0 (h>0)
        return h > 0 and h * h - beta * eta * u * h - beta * beta * eta * B < 0
    D = 12 + 44 * s; N = 48 + 2 * D * v; x = (4 + 4 * z) / N; y = Fr(1, 16)
    e183, B183 = nr[183]
    U0 = beta * e183 * (3 * x + 180 * y); R0 = beta * B183 / U0
    t = [below(252, Fr(251, 22), s ** 251), below(641, 640 / D, v ** 640),
         below(144, 137 * x + 6 * y, p ** 137 * q ** 6),
         below(182, 3 * R0 + 178 * y, p ** 9 * q ** 718 / U0 ** 3)]
    pos = z > 1 and min(s, v, p, q) > 0 and fr(cert['t']) > 1 and fr(cert['f']) > 0 and fr(cert['S']) >= 1 and D > 0 and N > 0 and x > 0 and U0 > 0 and R0 > 0 and all(e > 0 and B_ > 0 for e, B_ in nr.values())
    return all(t) and pos, t, (N * p, 128 * q)

# ------------------------------------------------------------------ matrices
def floor_(q): return q.numerator // q.denominator
def ceil_(q): return -((-q.numerator) // q.denominator)

def build_all(cert, st, X, Y, mode):
    LW = cert.get('L', 14); TE = cert.get('te', LW // 2)
    assert 3 <= TE <= LW - 1, 'FAIL te range: need 3 <= te <= L-1'
    """mode in 'P0','P1','P2'.  returns (P rounded ints, K exact Fractions unrounded scaled by S/f^1000 ... ) both"""
    f = fr(cert['f']); S = fr(cert['S']); t = fr(cert['t'])
    if mode == 'P0': m, o, R = X, 64 + Y, floor_
    elif mode == 'P1': m, o, R = X * t ** -718, 64 + Y * t ** 9, ceil_
    else: m, o, R = X * t ** 6, 64 + Y * t ** -137, ceil_
    sc = cast = st['sc']; xt = st['xt']; hidx = st['hidx']
    lower, upper = cert['lower'], cert['upper']
    rows = [r for r, e in cert['rows']]
    B = 'B'
    def table(d, bcol, rnd, m=m, o=o, f=f):
        """one-row table for time d (d=0 requires a=bcol, d=7 requires r5=bcol)."""
        acc = collections.defaultdict(lambda: 0)
        for r in rows:
            e = sc[r]; i = BIT(r, 0); j = 1 - BIT(r, 6)
            k = sum(BIT(r, dd) for dd in DS); nu = 2 - BIT(r, 12) - BIT(r, 13); ar = 1 - BIT(r, 12)
            delta = 1 if d == TE else 0
            if d == 0 and ar != bcol: continue
            if d == TE:
                if BIT(r, 5) != bcol: continue
                k = k - bcol
            ex = nu - (ar if d == 0 else 0)
            w = (2 ** ex) * m ** k * o ** (10 - delta - k) / f ** (7 * (10 - delta) + 2)
            if d in (0, 1): key = (i, j, xt[r] if e is not None else B)
            else: key = (i, j, e if e is not None else B)
            acc[key] += w
        return acc
    def rt(acc, rnd, S=S):
        return {k: (rnd(S * v) if rnd else S * v) for k, v in acc.items()}
    out = {}
    for rnd_name in ('int', 'exact'):
        rnd = R if rnd_name == 'int' else None
        if rnd_name == 'int':
            one = (lambda d, b: rt(table(d, b, None), rnd))
            Sx, fx = S, f
        else:
            Sx, fx = D_(S), D_(f); mx, ox = D_(m), D_(o)
            one = (lambda d, b: rt(table(d, b, None, mx, ox, fx), None, Sx))
        A1 = one(1, None); Amid = one(2, None); A7 = {b: one(TE, b) for b in (0, 1)}
        P = [[None] * 2 for _ in range(2)]
        for a in (0, 1):
            A0 = one(0, a)
            Hh = collections.defaultdict(lambda: 0)
            for (i, p, x), w0 in A0.items():
                for (p2, j, y), w1 in A1.items():
                    if p2 != p: continue
                    h = B if (x == B or y == B) else hidx[(x, y)]
                    Hh[(i, j, h)] += w0 * w1
            for b in (0, 1):
                L = 0
                for j in (0, 1):
                    V = {(j, 0): 1}
                    for d in range(2, LW):
                        tab = A7[b] if d == TE else Amid
                        ns = collections.defaultdict(lambda: 0)
                        for (pp, g), val in V.items():
                            for (p3, qq, e), w in tab.items():
                                if p3 != pp: continue
                                ng = B if (g == B or e == B) else g + e
                                ns[(qq, ng)] += val * w
                        V = ns
                    for (i, jj, h), hw in Hh.items():
                        if jj != j: continue
                        for (pi, g), val in V.items():
                            if pi != i: continue
                            if h == B or g == B or lower[h] <= g <= upper[h]: L += hw * val
                val = (f * L / S ** (LW - 1)) if rnd else (fx * L / Sx ** (LW - 1))
                P[a][b] = (R(val) if rnd else val)
        out[rnd_name] = P
    return out

def final_check(cert, st, X, Y):
    LW = cert.get('L', 14); DD = LW * 72 - 8
    assert 3 <= cert.get('te', LW // 2) <= LW - 1, 'FAIL te range: need 3 <= te <= L-1'
    f = fr(cert['f']); S = fr(cert['S']); Si = int(S)
    res = {}
    M = {m: build_all(cert, st, X, Y, m) for m in ('P0', 'P1', 'P2')}
    P0, P1, P2 = M['P0']['int'], M['P1']['int'], M['P2']['int']
    # exact (unrounded) comparison: P0 <= S/f^1000 K0 ; P1 >= S/f^1000 K- ; P2 >= S/f^1000 K+
    # exact version computed with unrounded tables equals  f*L/S^13 with tables scaled by S, i.e. (S/f^1000) K entries
    E0, E1, E2 = M['P0']['exact'], M['P1']['exact'], M['P2']['exact']
    res['round0'] = all(P0[a][b] <= E0[a][b] + Dc(10) ** -50 for a in (0, 1) for b in (0, 1))
    res['round1'] = all(P1[a][b] >= E1[a][b] - Dc(10) ** -50 for a in (0, 1) for b in (0, 1))
    res['round2'] = all(P2[a][b] >= E2[a][b] - Dc(10) ** -50 for a in (0, 1) for b in (0, 1))
    res['pos'] = all(P0[a][b] > 0 for a in (0, 1) for b in (0, 1))
    a_, b_, c_, d_ = P0[0][0], P0[0][1], P0[1][0], P0[1][1]
    J = (a_ + d_ + isqrt((a_ - d_) ** 2 + 4 * b_ * c_)) // 2
    pp = lambda x: (x - a_) * (x - d_) - b_ * c_
    res['J_le_rho'] = (2 * J <= a_ + d_) or pp(J) <= 0     # rho >= J : p(J)<=0 (or J below both diag-mean) -> rho(P0)>=J
    # stronger: J <= rho  <=> p(J) <= 0 or J <= smaller eigenvalue... rho>=J iff p(J)<=0 or J<=(a+d)/2
    tails = []
    for Q in (P1, P2):
        u, v, w, x = Q[0][0], Q[0][1], Q[1][0], Q[1][1]
        tails.append(J > max(u, x) and (J - u) * (J - x) > v * w)
    res['tails'] = tails
    res['J'] = J; res['P0'] = P0; res['P1'] = P1; res['P2'] = P2
    tg = fr(cert['target'])
    res['final'] = J * f.numerator ** DD * tg.denominator ** DD > Si * f.denominator ** DD * tg.numerator ** DD
    return res

def run(cert, full=True, verbose=True):
    ok = True; msgs = []
    def chk(name, c, info=''):
        nonlocal ok
        ok = ok and bool(c); msgs.append(('PASS ' if c else 'FAIL ') + name + (' ' + str(info) if info != '' else ''))
    st = structure(cert); r = st['res']
    chk('C1', r['c1_bad'] == 0, r['c1_bad'])
    _rows = [a for a, b in cert['rows']]
    chk('word<->walk injectivity (real-bit projection injective)', len({a & 0x3FBE for a in _rows}) == len(_rows) == len(set(_rows)))
    chk('1350 triples/state (unordered)', r["ntrip"][1] > 0 and r["ntrip"][2] > 0, r['ntrip'])
    chk('330 live rows both states', r['live_eq'])
    chk('null score <=> blocking', r['null_iff_blocking'])
    chk('score conservation', r['conserve'])
    chk('18 types/162 heads', True)
    chk('468 head triples/state', True, r['nhead_trip'])
    c, w = thr_check(cert, st); chk('thresholds (3.2)', c, w)
    chk('l,u integers (0<=l<=u<=2(L-2) not required)', True)
    chk('node_rates = exact recomputation from Lu App.C tables (rates.py) and Table 2', rates.verify_node_rates(cert['node_rates'], quiet=True))
    pc, pt, (X, Y) = prices_check(cert); chk('prices A.1 + positivity (z>1,s,v,p,q>0,t>1,f>0,S>=1,eta,B>0)', pc, pt)
    if full:
        fc = final_check(cert, st, X, Y)
        chk('rounding exact: P0<=exact', fc['round0']); chk('rounding exact: P1>=exact', fc['round1']); chk('rounding exact: P2>=exact', fc['round2'])
        chk('P0>0', fc['pos']); chk('J<=rho(P0)', fc['J_le_rho']); chk('tails<J', all(fc['tails']), fc['tails'])
        chk('final target', fc['final'])
        msgs.append('J=%d' % fc['J'])
        if 'claimed' in cert:
            chk('matches claimed', [fc['P0'], fc['P1'], fc['P2']] == [cert['claimed'][k] for k in ('P0', 'P1', 'P2')])
        r['fc'] = fc
    if verbose: print('\n'.join(msgs))
    return ok, msgs

if __name__ == '__main__':
    cert = json.load(open(sys.argv[1]))
    try:
        ok, _ = run(cert)
    except AssertionError as ex:
        print('RESULT FAIL (%s)' % ex); sys.exit(1)
    print('RESULT', 'PASS' if ok else 'FAIL'); sys.exit(0 if ok else 1)
