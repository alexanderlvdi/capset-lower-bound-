#!/usr/bin/env python3
"""Alternative stage (optional, slow): iterate the certificate from the trivial seed z = 2 (9-point cap set) with the
NEW thresholds, using independent_check.py; each round's witnesses s,v,p,q are re-derived (Decimal, then rounded
DOWN by 1e-24 relative and made exact rationals) and every decision is exact.  Shows the final bound does not
depend on Lu's seed z0 or Lu's published witnesses/widening (it still uses Lu Sec 2,4,5, App B, C data; the family is the 372-row family of cert.json).
Writes nothing.  usage: python3 -I chain_from_z2.py [BASE_CERT [THRESHOLD]]   defaults: L17c1.json 2.2296357841
BASE_CERT supplies rows, thresholds, L, te, node_rates only (its seed/target are ignored).  exit 0 iff the chain certifies Lambda > THRESHOLD"""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import independent_check as mychk
from independent_check import *
from decimal import Decimal as Dc, getcontext, ROUND_FLOOR
getcontext().prec = 120
BASE = sys.argv[1] if len(sys.argv) > 1 else 'L17c1.json'
THR = Fr(sys.argv[2]) if len(sys.argv) > 2 else Fr('2.2296357841')
cert0 = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), BASE)))
DDm = 72 * cert0.get('L', 14) - 8   # rows / thresholds (new) / node_rates only
assert rates.verify_node_rates(cert0['node_rates'], quiet=True)
nr = {int(b): (D_(fr(v[0])), D_(fr(v[1]))) for b, v in cert0['node_rates'].items()}
def Hroot(b, beta, u):
    eta, B = nr[b]; a = beta * eta * u
    return (a + (a * a + 4 * beta * beta * eta * B).sqrt()) / 2
def witnesses(z):          # z: Decimal
    beta = z / 3
    s = (Hroot(252, beta, Dc(251) / 22).ln() / 251).exp()
    Dd = 12 + 44 * s
    v = (Hroot(641, beta, 640 / Dd).ln() / 640).exp()
    N = 48 + 2 * Dd * v; x = (4 + 4 * z) / N; y = Dc(1) / 16
    e183, B183 = nr[183]
    U0 = beta * e183 * (3 * x + 180 * y); R0 = beta * B183 / U0
    a1 = Hroot(144, beta, 137 * x + 6 * y).ln()
    a2 = 3 * U0.ln() + Hroot(182, beta, 3 * R0 + 178 * y).ln()
    # 137 lp + 6 lq = a1 ; 9 lp + 718 lq = a2
    det = 137 * 718 - 6 * 9
    lp = (a1 * 718 - 6 * a2) / det; lq = (137 * a2 - 9 * a1) / det
    return s, v, lp.exp(), lq.exp()
def rat(dc, margin):
    q = (dc * (1 - Dc(margin))) * Dc(10) ** 30
    return Fr(int(q.to_integral_value(rounding=ROUND_FLOOR)), 10 ** 30)
def mk(z_fr):
    s, v, p, q = witnesses(D_(z_fr))
    return {'z': str(z_fr.numerator) + '/' + str(z_fr.denominator), 's': str(rat(s, '1e-24')), 'v': str(rat(v, '1e-24')), 'p': str(rat(p, '1e-24')), 'q': str(rat(q, '1e-24'))}
if __name__ == '__main__':
    z = Fr(2); G = 10 ** 12
    st = structure(cert0); best = None
    for rd in range(12):
        sd = mk(z)
        c = dict(cert0); c['seed'] = sd; c.pop('claimed', None); c['target'] = '1/1'
        pc, pt, (X, Y) = prices_check(c)
        assert pc, pt
        fc = final_check(c, st, X, Y)
        ok = fc['round0'] and fc['round1'] and fc['round2'] and fc['pos'] and fc['J_le_rho'] and all(fc['tails'])
        J = fc['J']; f = fr(c['f']); S = fr(c['S'])
        lo, hi = 0, 3 * 10 ** 12
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if J * f.numerator ** DDm * G ** DDm > int(S) * f.denominator ** DDm * mid ** DDm: lo = mid
            else: hi = mid - 1
        print('round', rd, 'seed', float(z), 'ok', ok, 'J', J, 'certified lower bound', lo / G, flush=True)
        if not ok: print('RESULT FAIL'); sys.exit(1)
        best = Fr(lo, G)
        if best <= z: break
        z = best
    good = best > THR
    print('final certified from z=2:', float(best), '>', float(THR), ':', good)
    print('RESULT', 'PASS' if good else 'FAIL'); sys.exit(0 if good else 1)
