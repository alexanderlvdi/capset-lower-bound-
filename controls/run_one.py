#!/usr/bin/env python3
"""usage: run_one.py CERT.json CHECKER.py  -> writes CERT.<checker>.out and .exit
For check_cert.py / check_cert2.py the run is stopped at the first line starting with FAIL (these checkers latch failure,
so their final status could only be RESULT FAIL; stopping early saves hours).  independent_check*.py run to the end.
Verdict recorded: REJECTED (a FAIL line, RESULT FAIL or VERDICT FAIL was seen), ACCEPTED (RESULT/VERDICT PASS: control
did NOT fail), CRASH (no verdict at all)."""
import subprocess, sys, os
cert, chk = sys.argv[1:3]
d = os.path.dirname(os.path.abspath(__file__)); name = cert[:-5] + '.' + chk[:-3]
early = chk.startswith('check_cert'); first = None; accepted = False; lines = []
p = subprocess.Popen([sys.executable, '-I', os.path.join(d, '..', 'verify', chk), cert], cwd=d, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
for line in p.stdout:
    lines.append(line)
    if line.startswith('FAIL') or line.startswith('RESULT FAIL') or line.startswith('VERDICT FAIL'):
        first = first or line.strip()
        if early: p.kill(); break
    if line.startswith('RESULT PASS') or line.startswith('VERDICT PASS'): accepted = True
p.wait()
open(os.path.join(d, name + '.out'), 'w').writelines(lines)
verdict = 'REJECTED' if first else ('ACCEPTED' if accepted else 'CRASH')
open(os.path.join(d, name + '.exit'), 'w').write('%s\t%s\t%s\t%s\n' % (cert, chk, verdict, first or ''))
print(cert, chk, verdict, first or '', flush=True)
