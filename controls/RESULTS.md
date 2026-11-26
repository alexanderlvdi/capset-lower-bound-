# Negative controls (run 25 Nov 2026)

Every file below is an altered copy of a certificate in `../verify/` (built by `make_controls.py`; inputs are never modified). Each was run with the checker named; `REJECTED` means the checker printed a failing check (the first one is shown) and, for `check_cert*.py`, the run was stopped there (these checkers latch failure, so the final status could only be `RESULT FAIL`; `run_one.py`). `independent_check2.py` runs to the end. `CRASH` means the checker raised an exception on the malformed family and printed no PASS (see below). No control was accepted.

Whole run of 43 controls, six in parallel on a loaded 2-core machine: 81 min wall, 29 min CPU.

| control | checker | alteration | outcome | first failing check |
|---|---|---|---|---|
| L17c1_L_changed | check_cert.py | L lowered by 1 with the same thresholds | REJECTED | state 1: all head-type triples satisfy sum u <= 55 triples=353 extreme=58 |
| L17c1_blocking_scored | check_cert.py | a blocking row given a score | REJECTED | score is null exactly on the blocking rows |
| L17c1_f_negative | check_cert.py | f < 0 | REJECTED | positivity hypotheses: t > 1, f > 0, S >= 1 integer |
| L17c1_flip_bit | check_cert.py | bit 3 of one live row flipped | REJECTED | C1: any 3 rows (rep. allowed), not all equal, have a coordinate with exactly two 1s violations=63 |
| L17c1_flip_bit | independent_check2.py | same file, referee checker (independent_check2.py) | CRASH |  |
| L17c1_injectivity | check_cert.py | added row with the same 12 real bits and swapped port bits | REJECTED | word<->walk injectivity: real-bit projection injective on rows |
| L17c1_injectivity | independent_check2.py | same file, referee checker (independent_check2.py) | CRASH |  |
| L17c1_l_minus1 | check_cert.py | all lower thresholds -1 | REJECTED | state 2: all head-type triples satisfy sum l >= 31 triples=656 extreme=29 |
| L17c1_l_minus1 | independent_check2.py | same file, referee checker (independent_check2.py) | REJECTED | VERDICT FAIL |
| L17c1_live_blocked | check_cert.py | a live row marked blocking (score null) | REJECTED | score is null exactly on the blocking rows |
| L17c1_node_rate_eta183 | check_cert.py | eta_183 * 1.0001 (referee mutation) | REJECTED | node_rates: all five (eta_b, B_b) equal exact recomputation from Appendix C tables and Table 2 floors |
| L17c1_perturbed_p | check_cert.py | price witness p + 1e-4 relative | REJECTED | (A.1) witness p,q: p^137 q^6 < H144(137x+6y) |
| L17c1_score_tamper | check_cert.py | one live row: score 1 -> 2 | REJECTED | score conservation e(a)+e(b)+e(c)=4 (s=1), 2 (s=2) on every triple, e in {0,1,2} |
| L17c1_score_tamper | independent_check2.py | same file, referee checker (independent_check2.py) | CRASH |  |
| L17c1_single_l_down | check_cert.py | single head 0 on the extreme triple: lower - 2 (smallest decrease violating (3.1)) | REJECTED | state 2: all head-type triples satisfy sum l >= 31 triples=656 extreme=30 |
| L17c1_single_u_up | check_cert.py | single head 0 on the extreme triple: upper + 2 (smallest increase violating (3.1)) | REJECTED | state 1: all head-type triples satisfy sum u <= 59 triples=353 extreme=62 |
| L17c1_subset_row | check_cert.py | added row that is a subset of an existing row (violates the witness property) | REJECTED | C1: any 3 rows (rep. allowed), not all equal, have a coordinate with exactly two 1s violations=67 |
| L17c1_subset_row | independent_check2.py | same file, referee checker (independent_check2.py) | CRASH |  |
| L17c1_t_eq_1 | check_cert.py | t = 1 | REJECTED | positivity hypotheses: t > 1, f > 0, S >= 1 integer |
| L17c1_target_up | check_cert.py | target + 1e-6 (above the certified value) | REJECTED | Lambda >= f (J/S)^(1/DD) > target = 4459272351/2000000000 (2.229636175500) |
| L17c1_u_plus1 | check_cert.py | all upper thresholds +1 | REJECTED | state 1: all head-type triples satisfy sum u <= 59 triples=353 extreme=61 |
| L17c1_u_plus1 | independent_check2.py | same file, referee checker (independent_check2.py) | REJECTED | VERDICT FAIL |
| L17c1_v_negative | check_cert.py | v -> -v | REJECTED | (A.1) witness p,q: p^137 q^6 < H144(137x+6y) |
| L17c3_chain_inconsistent | check_cert2.py | upper[0] - 1 (sound, but differs from the pinned prior certificate) | REJECTED | chain consistency: same rows, thresholds, f, S, t, node_rates as prior certificate |
| L17c3_target_up | check_cert2.py | target + 1e-6 | REJECTED | Lambda >= f (J/S)^(1/DD) > target = 22296367841/10000000000 (2.229636784100) |
| L17c3_u_plus1 | check_cert2.py | all upper thresholds +1 | REJECTED | state 1: all head-type triples satisfy sum u <= 59 triples=353 extreme=61 |
| L17c3_wrong_prior_hash | check_cert2.py | prior_cert_sha256 = 0...0 | REJECTED | prior certificate file hash matches pinned sha256 (L17c2.json) |
| L17c3_wrong_seed | check_cert2.py | seed z changed in the last digit | REJECTED | seed z equals the certified target read from the prior certificate (chain; prior cert must pass check_cert.py) |
| cb_0_l_minus1 | check_cert.py | all lower thresholds -1 | REJECTED | state 2: all head-type triples satisfy sum l >= 25 triples=656 extreme=22 |
| cb_0_node_rate_eta183 | check_cert.py | eta_183 * 1.0001 (referee mutation) | REJECTED | node_rates: all five (eta_b, B_b) equal exact recomputation from Appendix C tables and Table 2 floors |
| cb_0_score_tamper | check_cert.py | one live row: score 1 -> 2 | REJECTED | score conservation e(a)+e(b)+e(c)=4 (s=1), 2 (s=2) on every triple, e in {0,1,2} |
| cb_0_target_up | check_cert.py | target + 1e-6 (above the certified value) | REJECTED | Lambda >= f (J/S)^(1/DD) > target = 891847887/400000000 (2.229619717500) |
| cb_0_u_plus1 | check_cert.py | all upper thresholds +1 | REJECTED | state 1: all head-type triples satisfy sum u <= 47 triples=353 extreme=49 |
| cb_2_target_up | check_cert2.py | target + 1e-6 | REJECTED | Lambda >= f (J/S)^(1/DD) > target = 5574050757/2500000000 (2.229620302800) |
| cb_2_wrong_prior_hash | check_cert2.py | prior_cert_sha256 = 0...0 | REJECTED | prior certificate file hash matches pinned sha256 (cb_1.json) |
| cert3_target_up | check_cert2.py | target + 1e-6 | REJECTED | Lambda >= f (J/S)^(1/DD) > target = 2229595019/1000000000 (2.229595019000) |
| cert3_wrong_prior_hash | check_cert2.py | prior_cert_sha256 = 0...0 | REJECTED | prior certificate file hash matches pinned sha256 (cert2.json) |
| cert4_target_up | check_cert.py | target + 1e-6 (above the certified value) | REJECTED | Lambda >= f (J/S)^(1/DD) > target = 22295970073/10000000000 (2.229597007300) |
| cert4_u_plus1 | check_cert.py | all upper thresholds +1 | REJECTED | state 1: all head-type triples satisfy sum u <= 47 triples=353 extreme=49 |
| cert4b_target_up | check_cert2.py | target + 1e-6 | REJECTED | Lambda >= f (J/S)^(1/DD) > target = 2229597559/1000000000 (2.229597559000) |
| cert4b_wrong_prior_hash | check_cert2.py | prior_cert_sha256 = 0...0 | REJECTED | prior certificate file hash matches pinned sha256 (cert4.json) |
| cert_target_up | check_cert.py | target + 1e-6 (above the certified value) | REJECTED | Lambda >= f (J/S)^(1/DD) > target = 22295944693/10000000000 (2.229594469300) |
| cert_u_plus1 | check_cert.py | all upper thresholds +1 | REJECTED | state 1: all head-type triples satisfy sum u <= 47 triples=353 extreme=50 |

Notes.
* Referee mutation classes (referee 2 listed: single threshold +1 / +2, lower -1 / -2, flipping any bit of a live row, e +/- 1, swapped scores, added subset row, added row with the same real bits, duplicated row, a blocking row given a score, a live row marked blocking): all are represented above for the headline family (`L17c1_*`); the threshold ones both as "all heads" and as the smallest single-head change that breaks (3.1) (`single_u_up`, `single_l_down`; for L17c1 the extreme triple sums are 58 and 32 against the limits 59 and 31, so +2 and -2 on one extreme head are needed). Mutations that merely remove a row are not controls: a subfamily is a legitimate family and is accepted by design.
* `independent_check2.py` raised `KeyError` (blocking/unknown row looked up in the type table) on four structurally broken families (flip_bit, injectivity, score_tamper, subset_row). It never prints PASS for them; the same files are rejected with a clean FAIL by `check_cert.py` (rows above).
* Chain controls (`*_wrong_prior_hash`, `*_wrong_seed`, `*_chain_inconsistent`) test the SHA-256 chaining: a changed hash, a seed that is not the predecessor's target, and a (sound) threshold edit that differs from the pinned predecessor are all rejected.
* `*_target_up`: target raised by 1e-6, above the largest certified value.
* Controls for the earlier 352-row package (`../release`) are not repeated here.
