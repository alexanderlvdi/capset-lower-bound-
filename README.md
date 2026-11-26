# Cap-set capacity: certified Lambda > 2.2296357841

Improvement of ZeHua Lu's bound (arXiv:2611.30110, Lambda > 2.229206468135675727981404) by a new 372-row synchronizer family on Lu's 14 bits, re-optimised head windows, and walk length L = 17 (embedding step 8, 1216 dimensions per level). The mathematics is in `note.md`. Nothing here has been posted or submitted anywhere.

## Contents
- `note.md` - the note: result, the new family, what is unchanged from Lu, certificate format, verification, limitations.
- `verify/` - everything needed to check the claim offline.
  - `family_372.json`, `family_372.score.json` - the 372 rows and their raw type scores (`check_family_file.py` checks them against every certificate).
  - Certificates (all L = 14 unless noted; a chain is a list of certificates each pinning its predecessor by SHA-256):
    - `L17c1.json`, `L17c2.json`, `L17c3.json` - **headline**, L = 17, te = 8: Lambda > 2.2296357841
    - `cb_0.json`, `cb_1.json`, `cb_2.json` - L = 14, re-optimised windows (restart basin): > 2.2296193028
    - `cert4.json`, `cert4b.json` - L = 14, lower windows re-optimised from the first run: > 2.2295965590
    - `cert.json`, `cert2.json`, `cert3.json` - L = 14, first 372-row run (binary lower windows): > 2.2295940190
  - `check_cert.py` (first certificate of a chain) and `check_cert2.py` (chained certificates): stdlib-only exact checkers. `rates.py` recomputes the node rates eta_b, B_b exactly from Lu's Appendix C tables (`appendix_c_data/`, unmodified copies, SHA-256 pinned). Positivity hypotheses are asserted.
  - `independent_check.py` (referee 1, needs numpy) and `independent_check2.py` (referee 2, stdlib; the referee's original, generalised only to read L, te from the certificate).
  - `chain_from_z2.py` - optional seed-free chain from the trivial seed z = 2 (does not use Lu's Theorem 1.1).
  - `verify.sh`, `SHA256SUMS`.
- `controls/` - negative controls: `make_controls.py`, `run_controls.sh`, `manifest.tsv`, outputs, `RESULTS.md`.
- `verify_run.out` - recorded output of `./verify.sh` (headline chain; PASS, 46 min 54 s wall / 13 min CPU on a loaded 2-core machine).
- `logs/` - recorded runs of the other chains (`verify_extra_*.out`, same three checkers on every certificate, all PASS) and of the z = 2 chain for the headline family (`chain_z2_run.out`: certifies > 2.229635784112 without Lu's seed, 11 min wall).

## Reproduce
Python 3 (tested 3.13), no network. Only `independent_check.py` needs numpy (`verify.sh` says SKIP if numpy is missing).

    cd verify
    sha256sum -c SHA256SUMS
    ./verify.sh            # headline chain, all three checkers; prints ALL STAGES PASS, exit 0 iff every stage passes
    ./verify.sh --all      # also the three earlier chains
    ./verify.sh --chain    # also the z = 2 chain for the headline family (slow)

    cd ../controls
    python3 -I make_controls.py && ./run_controls.sh   # every control must exit with status 1

Run times are in `controls/RESULTS.md` and `verify_run.out`. Negative controls: 43 altered certificates, all rejected (`controls/RESULTS.md`); `run_controls.sh` stops the check_cert*.py runs at their first FAIL line.

## What is and is not checked
Checked from the raw data in exact arithmetic: the witness property of the 372 rows, the compatible-triple structure, conservation of the score, injectivity of the real-bit projection, the window condition (4.1) of the note, Lu's price inequalities at each seed, the integer matrices and spectral comparisons, the final bound, the SHA-256 chain, and the node rates (recomputed from Lu's tables).

Taken from Lu and not re-derived: Lemma 5.1/Appendix C (the probabilistic construction and the two rule tables), Proposition 5.2/Appendix B, Proposition 2.3, Theorem 4.1, the rounding argument A.5, and, for the headline chain, the validity of his construction at walk length L = 17 instead of 14 (the note gives the general-L proof of port-state conservation; the rest is argued to have no L-specific step). A reader who wants to stay inside Lu's stated L = 14 setting should use the `cb_*` chain (> 2.2296193028). None of Lu's code was run.

Computations assisted by AI tools (Claude).
