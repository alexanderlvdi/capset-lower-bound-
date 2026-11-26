#!/bin/sh
# Runs every control in manifest.tsv (6 at a time, about 0.5 GB each).  Every control must come out REJECTED.
# check_cert*.py runs are stopped at the first FAIL line (see run_one.py); independent_check*.py run to completion.
cd "$(dirname "$0")"
cut -f1,2 manifest.tsv | xargs -P6 -L1 python3 -I run_one.py
cat *.exit | sort > summary.tsv; cat summary.tsv; echo; echo "controls not REJECTED:"; awk -F'\t' '$3!="REJECTED"' summary.tsv | grep . || echo none
