#!/bin/sh
# Exit status 0 iff every stage prints PASS.  Usage:  ./verify.sh [--all] [--chain]
#   default : file hashes; family files vs certificates; the headline chain L17c1 -> L17c2 -> L17c3 (L = 17, te = 8,
#             Lambda > 2.2296357841) with all three checkers (check_cert*.py, independent_check.py [numpy],
#             independent_check2.py [stdlib]).
#   --all   : additionally the three earlier chains (cert/cert2/cert3 -> 2.2295940190, cert4/cert4b -> 2.2295965590,
#             cb_0/cb_1/cb_2 -> 2.2296193028, all L = 14), with all three checkers.
#   --chain : additionally the seed-free chain from z = 2 for the headline family (slow, tens of minutes).
# Every checker recomputes the node rates (eta_b, B_b) from Lu's Appendix C tables (rates.py, hash-pinned) and asserts
# the positivity hypotheses.  Chained certificates pin their predecessor by SHA-256 and take the seed z from its target.
set -e
export PYTHONDONTWRITEBYTECODE=1
cd "$(dirname "$0")"
ALL=0; CHAIN=0
for a in "$@"; do case $a in --all) ALL=1;; --chain) CHAIN=1;; esac; done
sha256sum -c SHA256SUMS
python3 -I check_family_file.py cert.json cert2.json cert3.json cert4.json cert4b.json cb_0.json cb_1.json cb_2.json L17c1.json L17c2.json L17c3.json
HAVE_NP=1; python3 -I -c "import numpy" 2>/dev/null || HAVE_NP=0
chain() {   # chain NAME1 NAME2 [NAME3]: first file is a stage-1 certificate, the others are chained
  first=$1
  for c in "$@"; do
    echo "=== $c"
    if [ "$c" = "$first" ]; then python3 -I check_cert.py $c.json; else python3 -I check_cert2.py $c.json; fi
    if [ $HAVE_NP = 1 ]; then python3 -I independent_check.py $c.json; else echo "SKIP independent_check.py (numpy missing)"; fi
    python3 -I independent_check2.py $c.json
  done
}
chain L17c1 L17c2 L17c3
if [ $ALL = 1 ]; then chain cert cert2 cert3; chain cert4 cert4b; chain cb_0 cb_1 cb_2; fi
if [ $CHAIN = 1 ]; then python3 -I chain_from_z2.py L17c1.json 2.2296357841; fi
echo "ALL STAGES PASS"
