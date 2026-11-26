#!/usr/bin/env python3
"""Check that the shipped family files (family_372.json = the 372 rows, family_372.score.json = raw type scores)
agree with the rows/scores embedded in every certificate: same rows in the same order; score equal on live rows,
null on blocking rows (blocking = no score).  Exit 0 iff all certificates agree."""
import json, sys, os
d = os.path.dirname(os.path.abspath(__file__))
fam = json.load(open(os.path.join(d, 'family_372.json')))
sc = json.load(open(os.path.join(d, 'family_372.score.json')))
ok = sc['rows'] == fam and len(set(fam)) == len(fam) == 372 and len(sc['e']) == 372
print('PASS' if ok else 'FAIL', 'family file and score file are aligned (372 distinct rows)')
for name in sys.argv[1:]:
    c = json.load(open(os.path.join(d, name)))
    rows = [r for r, e in c['rows']]
    same_rows = rows == fam
    same_e = all(e is None or e == sc['e'][i] for i, (r, e) in enumerate(c['rows']))
    n_null = sum(e is None for r, e in c['rows'])
    good = same_rows and same_e and n_null == 26
    ok &= good
    print('PASS' if good else 'FAIL', name, 'rows == family file, live scores == score file, blocking (null) rows =', n_null)
print('RESULT', 'PASS' if ok else 'FAIL'); sys.exit(0 if ok else 1)
