# Builds the negative-control certificates from ../verify/*.json (inputs are never modified) and manifest.tsv.
# usage: python3 -I make_controls.py        (needs no heavy computation, except that tight-head selection imports
#        ../verify/independent_check2.py for L17c1 and cb_0 and takes a few minutes)
import json, copy, sys, os, hashlib
from fractions import Fraction as F
V = '../verify/'
sys.path.insert(0, V)
ld = lambda n: json.load(open(V + n + '.json'))
man = []                       # (file, checker, description)
KEEP = set('''L17c1_u_plus1 L17c1_l_minus1 L17c1_perturbed_p L17c1_target_up L17c1_node_rate_eta183 L17c1_score_tamper L17c1_flip_bit
L17c1_injectivity L17c1_subset_row L17c1_blocking_scored L17c1_live_blocked L17c1_t_eq_1 L17c1_f_negative L17c1_v_negative
L17c1_L_changed L17c1_single_u_up L17c1_single_l_down
L17c3_wrong_prior_hash L17c3_wrong_seed L17c3_target_up L17c3_u_plus1 L17c3_chain_inconsistent
cb_0_u_plus1 cb_0_l_minus1 cb_0_target_up cb_0_score_tamper cb_0_node_rate_eta183 cb_2_wrong_prior_hash cb_2_target_up
cert4_u_plus1 cert4_target_up cert4b_wrong_prior_hash cert4b_target_up cert_u_plus1 cert_target_up cert3_wrong_prior_hash cert3_target_up'''.split())
def save(name, c, chk, desc):
    if name not in KEEP: return
    json.dump(c, open(name + '.json', 'w')); man.append((name + '.json', chk, desc))
def bump(c):
    e = F(c['node_rates']['183'][0]) * F(10001, 10000); c['node_rates']['183'][0] = '%d/%d' % (e.numerator, e.denominator); return c
def pert_p(c):
    p, d = c['seed']['p'].split('/'); c['seed']['p'] = str(int(p) + 10 ** 26) + '/' + d; return c
def target_up(c, d=F(1, 10 ** 6)):
    t = c['target']; t = F(t) if isinstance(t, str) else F(t); c['target'] = '%d/%d' % ((t + d).numerator, (t + d).denominator); return c
def tight_heads(cert):
    import independent_check2 as R
    rs = [tuple(x) for x in cert['rows']]; fam = R.family(rs); types, xt, heads, H = R.types_heads(rs); hts = R.head_triples(fam, xt, H)
    LW = cert.get('L', 14); U1 = 4 * (LW - 2) - 1; L2 = 2 * (LW - 2) + 1
    mu = max(sum(cert['upper'][i] for i in t) for t in hts[1]); ml = min(sum(cert['lower'][i] for i in t) for t in hts[2])
    tu = sorted({h for t in hts[1] if sum(cert['upper'][i] for i in t) == mu for h in t})
    tl = sorted({h for t in hts[2] if sum(cert['lower'][i] for i in t) == ml for h in t})
    return tu, tl, U1 - mu + 1, ml - L2 + 1     # heads on an extreme triple, and the amounts that break it
def stage1(base, tag, full):
    c = ld(base); chk = 'check_cert.py'
    save(tag + '_u_plus1', (lambda d: (d.__setitem__('upper', [u + 1 for u in d['upper']]), d)[1])(copy.deepcopy(c)), chk, 'all upper thresholds +1')
    save(tag + '_l_minus1', (lambda d: (d.__setitem__('lower', [l - 1 for l in d['lower']]), d)[1])(copy.deepcopy(c)), chk, 'all lower thresholds -1')
    save(tag + '_perturbed_p', pert_p(copy.deepcopy(c)), chk, 'price witness p + 1e-4 relative')
    save(tag + '_target_up', target_up(copy.deepcopy(c)), chk, 'target + 1e-6 (above the certified value)')
    save(tag + '_node_rate_eta183', bump(copy.deepcopy(c)), chk, 'eta_183 * 1.0001 (referee mutation)')
    d = copy.deepcopy(c); i = next(k for k, (r, e) in enumerate(d['rows']) if e == 1); d['rows'][i][1] = 2
    save(tag + '_score_tamper', d, chk, 'one live row: score 1 -> 2')
    if not full: return
    d = copy.deepcopy(c); a = next(k for k, (r, e) in enumerate(d['rows']) if e == 0); b = next(k for k, (r, e) in enumerate(d['rows']) if e == 2)
    d['rows'][a][1], d['rows'][b][1] = 2, 0; save(tag + '_scores_swapped', d, chk, 'scores of two live rows swapped (0 <-> 2)')
    d = copy.deepcopy(c); i = next(k for k, (r, e) in enumerate(d['rows']) if e is not None and k > 10); d['rows'][i][0] ^= 1 << 3
    save(tag + '_flip_bit', d, chk, 'bit 3 of one live row flipped')
    d = copy.deepcopy(c); d['rows'].append(list(d['rows'][5])); save(tag + '_duplicate_row', d, chk, 'a row duplicated')
    d = copy.deepcopy(c); r = next(r for r, e in d['rows'] if (r & 1) != ((r >> 6) & 1)); d['rows'].append([r ^ 1 ^ 64, None])
    save(tag + '_injectivity', d, chk, 'added row with the same 12 real bits and swapped port bits')
    d = copy.deepcopy(c); r = d['rows'][5][0]; d['rows'].append([r & ~(1 << 2) if r & 4 else r & ~(1 << 3), None])
    save(tag + '_subset_row', d, chk, 'added row that is a subset of an existing row (violates the witness property)')
    d = copy.deepcopy(c); i = next(k for k, (r, e) in enumerate(d['rows']) if e is None); d['rows'][i][1] = 1
    save(tag + '_blocking_scored', d, chk, 'a blocking row given a score')
    d = copy.deepcopy(c); i = next(k for k, (r, e) in enumerate(d['rows']) if e is not None); d['rows'][i][1] = None
    save(tag + '_live_blocked', d, chk, 'a live row marked blocking (score null)')
    x = copy.deepcopy(c); x['t'] = '1'; save(tag + '_t_eq_1', x, chk, 't = 1')
    x = copy.deepcopy(c); x['f'] = '-' + x['f']; save(tag + '_f_negative', x, chk, 'f < 0')
    x = copy.deepcopy(c); n, dd = x['seed']['v'].split('/'); x['seed']['v'] = '-' + n + '/' + dd; save(tag + '_v_negative', x, chk, 'v -> -v')
    if 'L' in c:
        x = copy.deepcopy(c); x['L'] = c['L'] - 1; save(tag + '_L_changed', x, chk, 'L lowered by 1 with the same thresholds')
        x = copy.deepcopy(c); x['te'] = c['te'] - 1; save(tag + '_te_changed', x, chk, 'embedding step te lowered by 1')
    if tag + '_single_u_up' not in KEEP: return
    tu, tl, au, al = tight_heads(c)
    d = copy.deepcopy(c); d['upper'][tu[0]] += au; save(tag + '_single_u_up', d, chk, 'single head %d on the extreme triple: upper + %d (smallest increase violating (3.1))' % (tu[0], au))
    d = copy.deepcopy(c); d['lower'][tl[0]] -= al; save(tag + '_single_l_down', d, chk, 'single head %d on the extreme triple: lower - %d (smallest decrease violating (3.1))' % (tl[0], al))
def stage2(base, tag, full):
    c = ld(base); chk = 'check_cert2.py'
    save(tag + '_u_plus1', (lambda d: (d.__setitem__('upper', [u + 1 for u in d['upper']]), d)[1])(copy.deepcopy(c)), chk, 'all upper thresholds +1')
    save(tag + '_target_up', target_up(copy.deepcopy(c)), chk, 'target + 1e-6')
    d = copy.deepcopy(c); d['prior_cert_sha256'] = '0' * 64; save(tag + '_wrong_prior_hash', d, chk, 'prior_cert_sha256 = 0...0')
    d = copy.deepcopy(c); d['seed']['z'] = d['seed']['z'][:-1] + ('1' if d['seed']['z'][-1] != '1' else '2'); save(tag + '_wrong_seed', d, chk, 'seed z changed in the last digit')
    if not full: return
    save(tag + '_perturbed_p', pert_p(copy.deepcopy(c)), chk, 'price witness p + 1e-4 relative')
    save(tag + '_node_rate_eta183', bump(copy.deepcopy(c)), chk, 'eta_183 * 1.0001')
    d = copy.deepcopy(c); d['upper'][0] -= 1; save(tag + '_chain_inconsistent', d, chk, 'upper[0] - 1 (sound, but differs from the pinned prior certificate)')
    x = copy.deepcopy(c); x['t'] = '1'; save(tag + '_t_eq_1', x, chk, 't = 1')
    x = copy.deepcopy(c); x['f'] = '-' + x['f']; save(tag + '_f_negative', x, chk, 'f < 0')
    x = copy.deepcopy(c); n, dd = x['seed']['v'].split('/'); x['seed']['v'] = '-' + n + '/' + dd; save(tag + '_v_negative', x, chk, 'v -> -v')
stage1('L17c1', 'L17c1', True); stage1('cb_0', 'cb_0', True); stage1('cert4', 'cert4', False); stage1('cert', 'cert', False)
stage2('L17c3', 'L17c3', True); stage2('cb_2', 'cb_2', True); stage2('L17c2', 'L17c2', False); stage2('cb_1', 'cb_1', False)
stage2('cert4b', 'cert4b', False); stage2('cert3', 'cert3', False); stage2('cert2', 'cert2', False)
# referee-checker (independent_check2.py) runs on a subset of the stage-1 controls of the headline family
for n in ('L17c1_u_plus1', 'L17c1_l_minus1', 'L17c1_score_tamper', 'L17c1_injectivity', 'L17c1_subset_row', 'L17c1_flip_bit'):
    man.append((n + '.json', 'independent_check2.py', 'same file, referee checker (independent_check2.py)'))
with open('manifest.tsv', 'w') as fh:
    for m in man: fh.write('\t'.join(m) + '\n')
print(len(man), 'controls')
