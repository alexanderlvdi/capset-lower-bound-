#!/usr/bin/env python3
"""Standalone exact checker (stdlib only; ints / fractions only for every decision).
usage: python3 -I check_cert.py cert.json
Mirrors Lu (arXiv 2611.30110) Sections 3.1-3.2, 4.2, 5.3 and Appendix A.1-A.4 for the base family W0
(no companion-path widening) with NEW head thresholds.  Prints PASS/FAIL per step; exit code 0 iff all pass."""
import sys, json, itertools, collections, os, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))   # needed under python -I
import rates
from fractions import Fraction as Fr
from math import isqrt

cert = json.load(open(sys.argv[1]))
LW = cert.get('L', 14); TE = cert.get('te', LW // 2); DD = LW * 72 - 8; U1 = (LW - 2) * 4 - 1; L2 = (LW - 2) * 2 + 1
if not (LW >= 4 and 3 <= TE <= LW - 1):
    print('FAIL te range: need 3 <= te <= L-1 (L=%s, te=%s)' % (LW, TE)); sys.exit(1)
ok_all = True
def check(name, cond, info=''):
    global ok_all
    print(('PASS ' if cond else 'FAIL ') + name + (' ' + str(info) if info != '' else ''), flush=True)
    ok_all = ok_all and bool(cond)
    return cond

def parse_fr(s):
    if isinstance(s, int): return Fr(s)
    if s.startswith('10**'): return Fr(10 ** int(s[4:]))
    return Fr(s)

bit = lambda r, k: (r >> k) & 1
rows = [r for r, e in cert['rows']]; score = {r: e for r, e in cert['rows']}
N = len(rows)
check('distinct 14-bit rows (N=%d)'%N, len(set(rows)) == N and all(0 <= r < 1 << 14 for r in rows))
check('word<->walk injectivity: real-bit projection injective on rows', len({r & 0x3FBE for r in rows}) == N)
PS, PT = 0, 6                       # port bits
DS = [1, 2, 3, 4, 5, 7, 8, 9, 10, 11]   # ten 7-dim slots; bits 12,13 scalars; bit 12 output; bit 5 embedding
REAL = sum(1 << b for b in DS + [12, 13])
FULL = (1 << 14) - 1
src = lambda r: bit(r, PS); tgt = lambda r: 1 - bit(r, PT)

# ---- (1) C1 witness property + (2) one-step compatible state triples, one pass over all multisets
bad = 0; T = {1: [], 2: []}
R = sorted(rows)
for ia in range(N):
    A = R[ia]
    for ib in range(ia, N):
        B = R[ib]; AB = A & B; Ab = A & ~B; aB = ~A & B
        for ic in range(ib, N):
            C = R[ic]
            if ia == ib == ic: continue
            two = (AB & ~C) | (Ab & C) | (aB & C)
            if not (two & FULL): bad += 1
for ia in range(N):
    A = R[ia]
    for ib in range(ia, N):
        B = R[ib]; AB = A & B; Ab = A & ~B; aB = ~A & B
        sab = src(A) + src(B); tab = tgt(A) + tgt(B)
        for ic in range(ib, N):
            C = R[ic]
            s = sab + src(C)
            if s not in (1, 2) or tab + tgt(C) != s: continue
            if ((AB & ~C) | (Ab & C) | (aB & C)) & REAL: continue
            T[s].append((A, B, C))
check('C1: any 3 rows (rep. allowed), not all equal, have a coordinate with exactly two 1s', bad == 0, f'violations={bad}')
check('state triples counted', len(T[1]) > 0 and len(T[2]) > 0, (len(T[1]), len(T[2])))
live = {s: {x for t in T[s] for x in t} for s in (1, 2)}
check('live rows identical in both states', live[1] == live[2], len(live[1]))
check('score is null exactly on the blocking rows', all((score[r] is None) == (r not in live[1]) for r in rows) )
DSUM = {1: 4, 2: 2}
check('score conservation e(a)+e(b)+e(c)=4 (s=1), 2 (s=2) on every triple, e in {0,1,2}',
      all(sum(score[x] for x in t) == DSUM[s] for s in (1, 2) for t in T[s]) and all(score[r] in (0, 1, 2) for r in rows if score[r] is not None))

# ---- (3) head types and threshold constraints
tup = lambda r: (src(r), tgt(r), sum(bit(r, k) for k in DS), 2 - bit(r, 12) - bit(r, 13), 1 - bit(r, 12), score[r])
live_rows = [r for r in rows if score[r] is not None]
types = sorted({tup(r) for r in live_rows}); xt = {r: types.index(tup(r)) for r in live_rows}
heads = [(a, b) for a in range(len(types)) for b in range(len(types)) if types[a][1] == types[b][0]]
H = {hb: i for i, hb in enumerate(heads)}
check('row/head types', True, (len(types), len(heads)))
upper, lower = cert['upper'], cert['lower']
check('thresholds: one integer per head type', len(upper) == len(lower) == len(heads) and all(isinstance(v, int) for v in upper + lower))
cnt = {}
for s in (1, 2):
    ordered = set()
    for t in T[s]:
        for p in itertools.permutations(t): ordered.add(p)
    by_src = collections.defaultdict(list)
    for p in ordered: by_src[tuple(src(r) for r in p)].append(p)
    hts = set()
    for p0 in ordered:
        for p1 in by_src[tuple(tgt(r) for r in p0)]:
            hts.add(tuple(sorted(H[(xt[p0[w]], xt[p1[w]])] for w in range(3))))
    cnt[s] = len(hts)
    if s == 1: worst = max(sum(upper[h] for h in t) for t in hts); good = worst <= U1
    else: worst = min(sum(lower[h] for h in t) for t in hts); good = worst >= L2
    check(f'state {s}: all head-type triples satisfy ' + (f'sum u <= {U1}' if s == 1 else f'sum l >= {L2}'), good, f'triples={len(hts)} extreme={worst}')
print('INFO head-type triples per state', cnt)
print('INFO 0<=l<=u<=%d sanity (not needed for soundness):' % (2 * (LW - 2)), all(0 <= l <= u <= 2 * (LW - 2) for l, u in zip(lower, upper)))

# ---- (4) prices (Lu A.1, Prop 5.2) in exact rationals
nr = {int(b): (parse_fr(v[0]), parse_fr(v[1])) for b, v in cert['node_rates'].items()}
sd = cert['seed']; z = parse_fr(sd['z']); s_, v_, p_, q_ = (parse_fr(sd[k]) for k in 'svpq')
beta = z / 3
def below(b, u, h):          # h < H_b(u)  <=>  h(h - beta*eta*u) < beta^2*eta*B   (h>0)
    eta, B = nr[b]; return h > 0 and h * (h - beta * eta * u) < beta ** 2 * eta * B
D_ = 12 + 44 * s_; Nn = 48 + 2 * D_ * v_; x_ = (4 + 4 * z) / Nn; y_ = Fr(1, 16)
eta183, B183 = nr[183]; U0 = beta * eta183 * (3 * x_ + 180 * y_); R0 = beta * B183 / U0
w1 = below(252, Fr(251, 22), s_ ** 251); w2 = below(641, 640 / D_, v_ ** 640)
w3 = below(144, 137 * x_ + 6 * y_, p_ ** 137 * q_ ** 6); w4 = below(182, 3 * R0 + 178 * y_, p_ ** 9 * q_ ** 718 / U0 ** 3)
check('seed z is Lu Thm 1.1 bound 2.229206468135675727981404 (an input from Lu, not proved here)', z == Fr(2229206468135675727981404, 10 ** 24))
check('(A.1) witness s: s^251 < H252(251/22)', w1); check('(A.1) witness v: v^640 < H641(640/D)', w2)
check('(A.1) witness p,q: p^137 q^6 < H144(137x+6y)', w3); check('(A.1) witness p,q: p^9 q^718/U0^3 < H182(3R0+178y)', w4)
X = Nn * p_; Y = 128 * q_
# ---- (4a) node rates: exact recomputation from Lu's Appendix C tables + Lu Table 2 floors (not taken on trust)
check('node_rates: all five (eta_b, B_b) equal exact recomputation from Appendix C tables and Table 2 floors',
      rates.verify_node_rates(cert['node_rates'], quiet=True))
check('node_rates: exactly b in {144,182,183,252,641}, all eta_b, B_b > 0', sorted(nr) == [144, 182, 183, 252, 641] and all(e > 0 and B > 0 for e, B in nr.values()))
check('positivity hypotheses: z > 1, s, v, p, q > 0, hence D, N, x, U0, R0 > 0',
      z > 1 and min(s_, v_, p_, q_) > 0 and D_ > 0 and Nn > 0 and x_ > 0 and U0 > 0 and R0 > 0)

# ---- (5) integer matrices P0 (floor), P1, P2 (ceil) for the base family W0 (Lu A.3 minus the two extensions)
f = parse_fr(cert['f']); S = parse_fr(cert['S']); Si = int(S); t = parse_fr(cert['t'])
check('positivity hypotheses: t > 1, f > 0, S >= 1 integer', t > 1 and f > 0 and S >= 1 and S == Si)
def build(m, o, rnd):
    pw_m = [m ** k for k in range(11)]; pw_o = [o ** k for k in range(11)]
    def Atable(d, req):        # req = a (d=0), b (d=7) or None ; returns {key: int}
        grp = collections.defaultdict(lambda: collections.Counter())
        for r in rows:
            nu = 2 - bit(r, 12) - bit(r, 13); k = sum(bit(r, c) for c in DS)
            dl = 1 if d == TE else 0
            if d == 0 and (1 - bit(r, 12)) != req: continue
            if d == TE:
                if bit(r, 5) != req: continue
                k -= req
            e = score[r]
            key = (src(r), tgt(r), (xt[r] if e is not None else 'B') if d in (0, 1) else (e if e is not None else 'B'))
            grp[key][(nu - ((1 - bit(r, 12)) if d == 0 else 0), k, dl)] += 1
        out = {}
        for key, cn in grp.items():
            tot = Fr(0)
            for (ex, k, dl), c in cn.items():
                tot += c * Fr(2) ** ex * pw_m[k] * pw_o[10 - dl - k] / f ** (7 * (10 - dl) + 2)
            out[key] = rnd(S * tot)
        return out
    flo = lambda q: q.numerator // q.denominator
    return Atable
def make_P(m, o, rnd):
    At = build(m, o, rnd)
    A1 = At(1, None); A_mid = At(2, None); A7 = {b: At(TE, b) for b in (0, 1)}
    P = [[None, None], [None, None]]
    # d=2..13 tables keyed (p,q,e) with e score or 'B'
    def Amid(d, b):
        return A7[b] if d == TE else A_mid
    for a in (0, 1):
        A0 = At(0, a)
        Hh = collections.defaultdict(int)       # (i,j,h) -> int
        for (i, p, x), w0 in A0.items():
            for (p2, j, y), w1_ in A1.items():
                if p2 != p: continue
                hh = 'B' if (x == 'B' or y == 'B') else H[(x, y)]
                Hh[(i, j, hh)] += w0 * w1_
        for b in (0, 1):
            L = 0
            for j in (0, 1):
                Vt = {(j, 0): 1}
                for d in range(2, LW):
                    tab = Amid(d, b); ns = collections.defaultdict(int)
                    for (pp, g), val in Vt.items():
                        for (p3, qq, e), w in tab.items():
                            if p3 != pp: continue
                            ng = 'B' if (g == 'B' or e == 'B') else g + e
                            ns[(qq, ng)] += val * w
                    Vt = ns
                for (i, jj, hh), hw in Hh.items():
                    if jj != j: continue
                    for (pi, g), val in Vt.items():
                        if pi != i: continue
                        if hh == 'B' or g == 'B' or lower[hh] <= g <= upper[hh]: L += hw * val
            q = f * L / S ** (LW - 1)
            P[a][b] = rnd2(q, rnd)
    return P
def floor_(q): return q.numerator // q.denominator
def ceil_(q): return -((-q.numerator) // q.denominator)
def rnd2(q, rnd): return floor_(q) if rnd is floor_ else ceil_(q)

mats = {}
for name, (m, o, rnd) in {'P0': (X, 64 + Y, floor_), 'P1': (X * t ** -718, 64 + Y * t ** 9, ceil_), 'P2': (X * t ** 6, 64 + Y * t ** -137, ceil_)}.items():
    mats[name] = make_P(m, o, rnd)
    print(name, mats[name], flush=True)
claimed = cert.get('claimed')
if claimed:
    check('matrices equal cert.json claimed values', all(mats[n] == claimed[n] for n in mats))
P0, P1, P2 = mats['P0'], mats['P1'], mats['P2']
check('P0 entries strictly positive (K0 strictly positive)', all(P0[a][b] > 0 for a in (0, 1) for b in (0, 1)))
a_, b_, c_, d_ = P0[0][0], P0[0][1], P0[1][0], P0[1][1]
J = (a_ + d_ + isqrt((a_ - d_) ** 2 + 4 * b_ * c_)) // 2           # = floor(rho(P0))
# Lu A.4: J <= rho(P0) exactly: J^2 - (a+d)J + ad - bc <= 0 with J >= (a+d)/2-ish; verify directly
pp = lambda x: (x - a_) * (x - d_) - b_ * c_      # char. poly of P0 (nonneg matrix, real roots)
check('J <= rho(P0)  (2J <= a+d or p(J) <= 0)', 2 * J <= a_ + d_ or pp(J) <= 0)
check('rho(P0) < J+1 (2(J+1) > a+d and p(J+1) > 0)', 2 * (J + 1) > a_ + d_ and pp(J + 1) > 0)
for nm, Q in (('P1 (K-)', P1), ('P2 (K+)', P2)):
    u, v, w, x = Q[0][0], Q[0][1], Q[1][0], Q[1][1]
    check(f'tail {nm}: J > max(u,x) and (J-u)(J-x) > vw  (rho(tail) < J <= rho(P0))', J > max(u, x) and (J - u) * (J - x) > v * w,
          f'J/S={J / Si:.6f}, rho(tail)/S<={((u + x + (((u - x) ** 2 + 4 * v * w) ** 0.5)) / 2) / Si:.6f} (float, informational)')
# ---- (6) final value, Lu A.6 style: Lambda >= f (J/S)^(1/DD) > target
tg = parse_fr(cert['target'])
final = J * f.numerator ** DD * tg.denominator ** DD > Si * f.denominator ** DD * tg.numerator ** DD
check(f'Lambda >= f (J/S)^(1/DD) > target = {cert["target"]} ({float(tg):.12f})', final)
lu = Fr(2229206468135675727981404, 10 ** 24)
check('target > Lu seed/bound 2.229206468135675727981404', tg > lu)
# largest 1e-14-grid value certified (informational)
lo, hi = 0, 10 ** 15 * 3
G = 10 ** 14
while lo < hi:
    mid = (lo + hi + 1) // 2
    ok = J * f.numerator ** DD * G ** DD > Si * f.denominator ** DD * mid ** DD
    lo, hi = (mid, hi) if ok else (lo, mid - 1)
print(f'INFO max certified u/1e14 grid value: {lo}/10^14 = {lo / G:.14f}; J = {J}')
print('RESULT', 'PASS' if ok_all else 'FAIL')
sys.exit(0 if ok_all else 1)
