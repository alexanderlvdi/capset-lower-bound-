# A larger synchronizer family and re-tuned windows for Lu's cap-set bound

## 1. Result

Let r_3(d) be the maximum size of a cap set in F_3^d and Λ = lim r_3(d)^{1/d}. ZeHua Lu [Lu, arXiv:2611.30110] proved Λ > 2.229206468135675727981404. In this note we prove

**Theorem.** Λ > 2.2296357841.

This is an improvement of about 4.3·10^-4 over Lu's bound. The method is his; the changes are in the finite data he feeds to it. Three things differ from [Lu]:

1. a new family of 372 rows on the same 14 bits (Lu uses 352), found by an orbit-level integer program that keeps Lu's conserved scores on his row types;
2. head windows (the integer thresholds that cut down the admitted walks) that are re-optimised for that family, with genuine two-sided windows in the second state instead of an all-or-nothing choice;
3. the walk length, which is a free parameter of the construction: we use L = 17 (embedding step 7 replaced by 8) instead of L = 14, so each level costs 72L − 8 = 1216 dimensions instead of 1000.

The proof is a finite computation in exact integer and rational arithmetic. Everything that is checked is checked by standalone scripts (Section 5); everything that is not checked is listed in Section 6.

For the record, the bounds certified along the way, all with the same 372 rows, are:

| chain (files) | L | windows | certified Λ > |
|---|---|---|---|
| `cert`, `cert2`, `cert3` | 14 | first 372-row run, binary lower windows | 2.2295940190 |
| `cert4`, `cert4b` | 14 | lower windows re-optimised | 2.2295965590 |
| `cb_0`, `cb_1`, `cb_2` | 14 | restart basin of the window search | 2.2296193028 |
| `L17c1`, `L17c2`, `L17c3` | 17 | window search at L = 17 | **2.2296357841** |

An earlier, smaller result of ours kept Lu's 352 rows and only re-optimised his head thresholds, giving Λ > 2.2292065969977 (a gain of 1.3·10^-7). It is superseded by everything above and is not part of this package.

## 2. What is taken from Lu unchanged

Section and lemma numbers refer to [Lu].

1. *Proposition 2.3* (gluing and coordinate deletion).
2. *Lemma 3.1* (port-state conservation): three compatible closed walks that are not all identical have a constant number s ∈ {1, 2} of source ports equal to 1. The proof is an induction around the cycle and does not use L = 14 (see the discussion of L in Section 6).
3. The witness property: any three rows, not all equal, have a coordinate carrying exactly two 1s. We re-check it directly on our 372 rows.
4. The format of the score: an integer e ∈ {0, 1, 2} on every non-blocking row, with e(a) + e(b) + e(c) = 4 (s = 1) or 2 (s = 2) on every compatible triple of rows in that state. Our rows have their own scores; the conservation law is re-checked on all triples.
5. *Lemma 5.1* and Appendix C (fixed-sum grouped nodes and the node rates η_b, B_b), *Proposition 5.2* and Appendix B (the two seven-dimensional alphabets and the price inequalities A.1), taken as stated. The node rates are recomputed from Lu's two Appendix C tables, see Section 5.
6. *Theorem 4.1*: if ρ(K_0) > max(ρ(K_−), ρ(K_+)), then Λ ≥ ρ(K_0)^{1/D}. Parameters f = 5573/2500, S = 10^28, t = 1000001/1000000 are Lu's. For general walk length L the exponent D is the net number of new dimensions per level, 72L − 8 (Lu: L = 14, D = 1000).
7. The integer-matrix recursion of A.3 and the comparisons of A.4–A.6, including the rounding argument of A.5.
8. The cone (4.1) of record counts (137, 6), (9, 718), the tilted matrices K_±, and the price witnesses; also *Theorem 1.1* as a starting seed (an alternative seed-free route is given in Section 5).

Not used: the companion-path widening of Section 3.3. Our family is a base family W_0 only.

## 3. The new family

**What the rows are.** As in [Lu], a row is a 14-bit mask: bit 0 is the source port, bit 6 the (complemented) target port, bits 1–5 and 7–11 are ten seven-dimensional slots (bit 5 hosts the embedded previous level), bits 12 and 13 are scalars (bit 12 is the output scalar deleted at step 0). A closed walk of length L is a sequence of rows whose ports chain around a cycle. A row is *blocking* if one of its two blocks of five seven-dimensional slots is entirely T (26 of our 372 rows); blocking rows are always admitted and are given no score. Our family has 372 rows: 346 live and 26 blocking. It shares only 31 rows with Lu's 352.

**How it was found.** The search is a CP-SAT integer program over orbits of 14-bit rows under a group C_5 × C_5 of slot permutations (a subgroup of the order-100 automorphism group of Lu's family; 784 orbits). The variables are

* one Boolean per orbit (all rows of an orbit are in or out together);
* one integer score e_τ ∈ {0, 1, 2} for each *row type* τ, a type being (source port, target port, number of T's in each block of five slots, the two scalar bits);
* for every orbit triple that can occur as a compatible state triple, the conservation law e_a + e_b + e_c = 4 (state 1) or 2 (state 2) whenever the three orbits are chosen.

The witness property is imposed lazily (a conflicting orbit triple becomes a clause "not all three chosen" when found; about 2.2 million orbit triples are enumerated by a C helper). The objective is the first-order change of the *ceiling*, i.e. the value 2.22930… that Theorem 4.1 would give if no walk were ever rejected by a window, linearised at the current family with the Perron weights of the 2×2 transfer matrix and the price vector at the seed z. We iterate: solve, relinearise, solve. The decisive modelling step is to fix the scores e_τ to Lu's on every row type that Lu also uses. With scores left free the solver returns a family with a larger ceiling (2.2293134) but no non-trivial score: the only solutions of the conservation equations are the trivial ones, a + b·i + c·j, which depend on the ports alone, and the resulting windows are useless (the family drops to 2.229187 after window optimisation, below Lu). With Lu's scores fixed the solver returns the 372 rows; after the 18 new row types it introduces have received scores, the ceiling is 2.2297982 against 2.2293016 for Lu's rows.

Checks of the result, all re-done from the raw rows by the checkers: the witness property (0 violations over all multisets of three rows), conservation of the score on all state triples (1125 triples in state 1 and 1800 in state 2, against 1350 and 1350 for Lu), the same 346 live rows in both states, and injectivity of the projection onto the twelve non-port bits (372 distinct real parts, needed for the word-to-walk correspondence).

**Why it beats Lu's family: an unbalanced port diagonal.** Let (i, j) ∈ {0,1}² be the port class of a row and let M be the 2×2 matrix whose (i, j) entry is the total weight of the live rows of that class (weights at the seed prices). The matrix K of Theorem 4.1 behaves like a power M^12 of it, and the ceiling is z·ρ(K)^{1/1000}, so to first order it depends on ρ(M) through ln ρ(K) ≈ 14.4·ln ρ(M) + 0.156 (a fit that holds for Lu's family, for his family's automorphic variants and for ours). For Lu's family M ≈ [[0.5148, 0.3159], [0.7212, 0.5148]]: the diagonal is balanced and ρ(M) = 0.9921. For ours, M ≈ [[0.4493, 0.3518], [0.6545, 0.5951]] and ρ(M) = 1.0076, although the total mass is slightly *smaller* (2.051 against 2.066). The gain comes entirely from the diagonal being unbalanced: with ρ = (a + d)/2 + √(((a − d)/2)² + bc), a difference between a and d increases ρ quadratically. Concretely the family has 130 rows in class (1,1) and 66 in class (0,0), where Lu has 90 and 90. The share of the weight carried by rows with e = 1 rises from 0.36 to 0.47, and on 93% of the weight the new score is the trivial one, 2 − i − j.

The price is paid in the windows. A walk is rejected if its suffix score G = Σ e leaves the window of its head; with e = 2 − i − j this is the count of port occupancy along the walk, which for an unbalanced chain has a skewed distribution. In the L = 14 pipeline the windows cost 2.0·10^-4 of the ceiling (Lu: 0.95·10^-4), but the ceiling gain is 5·10^-4, so the family wins by 3.9·10^-4 before any re-tuning. A small model (loss proportional to the Perron mass of walks whose suffix score leaves [9, 15], reduced by the fraction of walks that touch a blocking row, which are exempt) reproduces the value for the new family to about 6·10^-6, and predicts that Λ increases monotonically with the diagonal imbalance. We did not push the family further in that direction: no single row can be added (all 16012 candidates violate the witness property), and no one-for-one swap exists.

## 4. Windows and walk length

**Windows.** A head is the pair of rows at steps 0 and 1; the 372 rows give 18 row types and 162 head types h. Each head type carries integers ℓ_h and u_h; a blocking-free walk of head type h and suffix score G is admitted iff ℓ_h ≤ G ≤ u_h. Walks that contain a blocking row are always admitted. The only property of the windows used in the proof is

  Σ u_h over any compatible head-type triple of state 1 ≤ 4(L − 2) − 1,  Σ ℓ_h over any compatible head-type triple of state 2 ≥ 2(L − 2) + 1.   (4.1)

Indeed, three compatible walks that are not all identical lie in a state s, none contains a blocking row, and their L − 2 suffix steps contribute 4 (s = 1) or 2 (s = 2) per step to the total of the three suffix scores, i.e. 4(L − 2) or 2(L − 2); (4.1) makes this impossible. The checker derives the head-type triples from the raw rows.

Our first window run for the 372 rows (`cert`, `cert2`, `cert3`) ended in a degenerate state: in state 2 every ℓ_h was 0 (head type unconstrained) or 26 (head type excluded outright), the extreme triple sum in (4.1) was 26 against the required 25, so there was slack that the trust-region search, which moves a threshold by at most a few units, could not use. A referee pointed this out. Re-solving the window integer program from this start (CP-SAT, objective: the Perron-weighted mass of admitted walks, alternating states, with exact ρ(K_0) acceptance) gives genuine two-sided windows (ℓ_h between 2 and 13 after one pass, u_h between 12 and 19) and raised the certified value to 2.2295965590 (`cert4`, `cert4b`). Restarting the same search from other points gave very different local optima; the best one we found at L = 14 (found by an independent restart search, `cb_0`–`cb_2`) certifies 2.2296193028. We make no claim of optimality for any of these windows. As they affect nothing but which walks are admitted, soundness rests only on (4.1), which is rechecked.

**Lemma 3.1 for general L.** Let three compatible closed walks over a family with the witness property be not all identical. At a step t where the three rows differ, the witness gives a coordinate with exactly two 1s; compatibility forbids it to be a real slot, so it is a port bit. If it is the source port, s_t = 2 (s_t = number of 1s among the three source ports at step t); if it is the target port, exactly one target equals 1, hence s_{t+1} = 1. So whenever the rows at t differ, s_t = 2 or s_{t+1} = 1. If some s_t = 2, the targets at t−1 contain two 1s, so the rows at t−1 differ, and the same rule gives s_{t−1} = 2; going round the cycle s ≡ 2. Otherwise take t_0 with differing rows: s_{t_0+1} = 1, the sources at t_0+1 are then mixed, the rows there differ, and inductively s ≡ 1. Nothing here depends on the length of the cycle. (Walks and words correspond one-to-one because the projection of the rows onto their twelve real bits is injective, which the checkers verify; so compatible words give compatible walks and three compatible words are identical.)

**Walk length.** The construction is stated by Lu for L = 14, but L enters only through the number of steps. With 14 bits per row the dimension per level is 72L − 8, the cycle has L steps, the embedded slot sits at step te, and (4.1) holds with the sums above. Increasing L lowers the ceiling of both families (for Lu's rows: 2.22944 at L = 10 to 2.22926 at L = 16) but lowers the window loss of the *new* family faster, until it flattens out near L = 16–20. For the 372 rows, fixed-score pipeline at the Lu seed:

| L | 10 | 11 | 12 | 14 | 15 | 16 | 17 | 18 | 20 |
|---|---|---|---|---|---|---|---|---|---|
| Λ | 2.2294764 | 2.2295279 | 2.2295790 | 2.2295848 | 2.2296260 | 2.2296310 | 2.2296352 | 2.2296345 | 2.2296321 |

(L = 14 with the longer search of the previous section is 2.2295935; the table uses one fixed search effort for all L.) So L = 17 is the best of these for this family, but the optimum depends on the family: for Lu's own 352 rows we saw no such gain from longer walks. The family was not re-optimised for L = 17, and the window search at L = 17 was a single run; both are likely to leave something on the table.

## 5. The certificate and how it is checked

A certificate is a JSON file with the fields

| field | content |
|---|---|
| `rows` | the 372 rows as 14-bit integers with their scores (`null` for the 26 blocking rows) |
| `upper`, `lower` | the 162 thresholds u_h, ℓ_h, in head-type order |
| `L`, `te` | walk length and embedding step (absent means 14 and 7) |
| `node_rates` | pairs (η_b, B_b) of Lemma 5.1 for b ∈ {144, 182, 183, 252, 641}; not trusted, recomputed on every run |
| `seed` | z and four rational price witnesses s, v, p, q, rounded down at 10^-30 |
| `f`, `S`, `t` | 5573/2500, 10^28, 1000001/1000000 |
| `target` | the rational lower bound claimed |
| `prior_cert`, `prior_cert_sha256` | (chained certificates) file name and SHA-256 of the predecessor |

*Chaining.* Proposition 5.2 needs a proven seed z < Λ. The first certificate of each chain (`cert`, `cert4`, `cb_0`, `L17c1`) uses Lu's z = 2.229206468135675727981404 (his Theorem 1.1). Every later certificate pins its predecessor by SHA-256, reads the predecessor's `target` from that file and requires it to equal its own seed z, and requires rows, thresholds, L, te, f, S, t and node rates to be identical to the predecessor's. The three certificates of the headline chain are therefore bound together: `L17c3` → `L17c2` → `L17c1`, and `verify.sh` checks every link. A fourth step would gain about 10^-12, since dΛ/dz ≈ 1.4·10^-3.

*The checkers.* All use exact `int` and `Fraction` arithmetic.

* `check_cert.py` (first certificate of a chain) and `check_cert2.py` (chained certificates), standard library only. Steps: (0) `rates.py` recomputes the ten rationals η_b, B_b from Lu's Appendix C rule tables (`appendix_c_data/matching.tsv`, `reader_rows.tsv`, unmodified, SHA-256 pinned) by the formulas C.1–C.5 and demands exact equality with `node_rates` and with Lu's Table 2 floors; (1) distinct rows, injectivity of the real projection, and the witness property over all multisets of three rows; (2) the state triple sets T_1, T_2, the live and blocking rows; (3) conservation of the score on every triple, e ∈ {0,1,2}, score null exactly on blocking rows; (4) row types, head types, the head-type triples of each state from the raw rows, and (4.1); (5) the four price inequalities of A.1 at the seed, together with explicit positivity assertions (z > 1; s, v, p, q > 0; t > 1; f > 0; S a positive integer; η_b, B_b > 0), since the inequalities alone would not exclude, for instance, v < 0; (6) the integer matrices P_0 (rounded down), P_1, P_2 (rounded up) of A.3 for the family, with strict positivity of P_0; (7) J = ⌊ρ(P_0)⌋ by integer square root, the exact tests J ≤ ρ(P_0) < J + 1 and, for P_1 and P_2, J > max(diagonal) and (J − P[0][0])(J − P[1][1]) > P[0][1]P[1][0], i.e. ρ < J; (8) f(J/S)^{1/D} > target by comparison of integers, D = 72L − 8; (for chains) the hash, seed and consistency checks above.
* `independent_check.py` (numpy), written by an outside referee from Lu's text without reading our checkers (all ordered triples, different DP); in addition it verifies the rounding directions of A.5 directly (P_0 ≤ exact, P_1, P_2 ≥ exact), and reproduces J exactly. It shares only `rates.py` with the others.
* `independent_check2.py` (standard library), a second referee's checker with a fully separate implementation (own C1 search, own head-triple enumeration,, own enumeration of the compatible triples and head-type triples); the copy in this package differs from the referee's original only by reading L and te from the certificate (six places, all in the matrix DP and the final comparison; marked in the file header). It does not recompute node rates; the other two do.
* `check_family_file.py` confirms that the shipped family files (`family_372.json`, `family_372.score.json`) agree with every certificate.
* `chain_from_z2.py` (optional, slow): starts from the trivial seed z = 2 (the 9-point cap set), re-derives the witnesses each round (Decimal, rounded down, exact rationals), certifies the round with `independent_check.py` and feeds the grid-rounded bound to the next round. It shows that the theorem does not depend on Lu's Theorem 1.1 or his published witnesses; the family of `L17c1` certifies **2.229635784112** from z = 2 in six rounds (2.2292942, 2.2296353, 2.2296357834, 2.229635784111, …), which exceeds the headline 2.2296357841.

For the headline chain the checkers give (J is the integer ⌊ρ(P_0)⌋ at scale S = 10^28; the largest 10^-14-grid value that passes is also recorded):

| certificate | seed z | target | J | largest passing 10^-14 value |
|---|---|---|---|---|
| `L17c1` | Lu's z | 2.2296351755 | 12678968535999539658924507151 | 2.22963517554093 |
| `L17c2` | 2.2296351755 | 2.2296357832 | 12683171459391555327095816355 | 2.22963578325021 |
| `L17c3` | 2.2296357832 | **2.2296357841** | 12683177417578758081062492743 | 2.22963578411157 |

The extreme head-type triple sums at L = 17 are 58 (limit 59) in state 1 and 32 (limit 31) in state 2, and ρ(K_±)/S stays below 1.2607 against J/S = 1.2683. The other chains pass in the same way (`verify.sh --all`; integers J and grid values are in `logs/verify_extra_*.out`): 2.22959346936825, 2.22959401829737, 2.22959401907588 for `cert`–`cert3`; 2.22959600733089, 2.22959655966991 for `cert4`, `cert4b`; 2.22961871758521, 2.22961930198329 and 2.2296193028 for `cb_0`–`cb_2`.

All checkers agree, and in particular the two referee implementations reproduce the integer J of ours. `verify.sh` runs everything with `python3 -I` and exits 0 only if every stage prints PASS; the recorded run is `verify_run.out` (46 min 54 s wall, 13 min CPU on a shared two-core machine under load; the three checkers on three certificates; the z = 2 chain took a further 11 min wall).

*Negative controls.* Forty-three altered certificates (`controls/`, `RESULTS.md`) are rejected, none accepted: for the headline family all of u + 1, ℓ − 1 (on all heads and on a single extreme head), a perturbed price p, a target 10^-6 above the certified value, η_183 raised by 0.01%, a changed score, swapped or null scores, a flipped bit in a live row, a duplicated row, an added row with the same real bits (injectivity) or one that is a subset of an existing row (witness), t = 1, f < 0, v < 0, L or te lowered; for the chain: wrong prior hash, wrong seed, target above the certified value, an inconsistent threshold edit; and the corresponding basic controls for each of the other chains. `independent_check2.py` rejects or throws an exception on all of the six structural controls it was given and never prints PASS.

## 6. Limitations and what is not covered

* Still taken from Lu and not re-derived by anyone here: the probabilistic construction behind Lemma 5.1 (we recompute the numerical node rates from his two rule tables, which are themselves taken as data, using our own implementation of his formulas C.1–C.5), Appendix B and Proposition 5.2 (alphabets and the price inequalities' meaning), Proposition 2.3, Theorem 4.1, and the rounding argument of A.5 (the second referee checks the rounding directions numerically). The z = 2 chain removes only Lu's Theorem 1.1 as a dependency.
* The family and its scores are our own, not Lu's: we check the witness property, the compatible-triple structure, score conservation, injectivity and (4.1) from the raw rows, and nothing else about them is used.
* **Walk length.** Lu carries out the construction at L = 14; the headline chain uses L = 17 with the embedding at step te = 8. Every step of his argument that mentions L is redone for general L in the appendix below, and the L-dependent bookkeeping is also checked numerically at L = 17. The L = 14 chains (`cb_0`–`cb_2`) remain in the package for comparison.
* The windows are not claimed optimal and the family was not optimised for L = 17; the thresholds in the certificates are simply those the search returned.
* Certificates with l > 24 (`cert`, `cert2`, `cert3`) or l > u violate Lu's sanity range 0 ≤ ℓ ≤ u ≤ 24; this is sound (such a head type is excluded outright), the checkers print it as information. The re-optimised windows lie within the range.
* Widening (Lu §3.3) is not used. A floating-point estimate suggests about 4·10^-11 from it for the earlier family, far below the changes reported here.
* Lu's own code was not run; his data files are read as plain data.

## Appendix. Lu's construction for an arbitrary walk length L

Lu states and carries out his construction for closed walks of length 14. In this appendix we go through it for a walk length L, with the embedding step te in {3, ..., L-1}, and show that nothing in the argument depends on L = 14, te = 7 beyond arithmetic that we redo. The headline certificate uses L = 17, te = 8. Section numbers refer to [Lu]. Throughout, a row is a 14-bit mask with port bits 0 (source) and 6 (target, complemented), ten seven-dimensional real slots (bits 1-5, 7-11), and two scalar real slots (bits 12, 13); i(r) = r_0, j(r) = 1 - r_6.

### 1. Setting

Let R be a family of rows. A closed walk of length L is a sequence r(0), ..., r(L-1) in R with j(r(t)) = i(r(t+1)), indices mod L; its word is the array of real bits (1 for T, 0 for O). Three walks are compatible if no real slot at any step carries exactly two 1s among the three rows at that step. We assume that R has the witness property: any three rows of R, not all equal (repetition allowed), have a coordinate among all 14 bits with exactly two 1s. Equivalently, R is an antichain without 3-sunflowers. For T_s (s = 1, 2) we take the set of multisets {a, b, c} of rows with no real coordinate carrying exactly two 1s, with s ones among the three source ports and s ones among the three target ports. A row is live if it lies in some triple of T_1, and blocking otherwise; we require that it lies in some triple of T_1 if and only if it lies in some triple of T_2.

### 2. Port-state conservation for every L

**Lemma 1.** Let three compatible closed walks of length L over R be not all identical. Then there is s in {1, 2} such that, at every step t, exactly s of the three source ports equal 1 and exactly s of the three target ports equal 1. In particular the three rows at every step are not all equal, and the three rows at every step form a triple of T_s.

*Proof.* Let s_t be the number of 1s among the three source ports at step t. If the rows at step t are not all equal, the witness property gives a coordinate with exactly two 1s; compatibility excludes real slots, so it is a port bit. If it is the source bit, s_t = 2. If it is the target bit, two of the rows have r_6 = 1, exactly one target equals 1, and since the source ports at step t+1 are the targets at step t, s_{t+1} = 1. Hence

(*) if the rows at step t are not all equal, then s_t = 2 or s_{t+1} = 1.

Suppose s_t = 2 for some t. The targets at step t-1 are the sources at step t, so they are mixed and the rows at step t-1 are not all equal. By (*) at t-1, s_{t-1} = 2 or s_t = 1; the second is false, so s_{t-1} = 2. Going backwards around the cycle gives s_t = 2 for all t. Otherwise s_t is never 2. The walks are not identical, so some step t_0 has unequal rows, and (*) gives s_{t_0+1} = 1. Then the sources at step t_0+1 are mixed, so the rows there are unequal, and (*) gives s_{t_0+2} = 1. Going forward around the cycle gives s_t = 1 for all t. The target counts at step t equal s_{t+1} = s. A step with s in {1, 2} cannot have three equal rows, since their source ports would sum to 0 or 3. Finally each step has no real slot with exactly two 1s, so the step triple lies in T_s. The cycle length enters only through the indices modulo L. []

Rows that lie in no triple of T_1 (equivalently of T_2) therefore never occur in a compatible non-identical triple. We call them blocking and admit every walk that contains one.

### 3. The base family for every L

Let e: live rows -> {0, 1, 2} satisfy e(a)+e(b)+e(c) = 4 for every triple in T_1 and 2 for every triple in T_2. (The choice e = 2 - i - j always satisfies this, since the sum over a triple of T_s is 6 - 2s.) The head of a walk consists of its rows at steps 0 and 1, and a head type is the pair of row types of these two rows. For a blocking-free walk let G = e(r(2)) + ... + e(r(L-1)) be its suffix score, a sum of L - 2 terms. For each head type h fix integers l_h, u_h. Let W_0 consist of all walks that contain a blocking row together with all blocking-free walks with l_h <= G <= u_h.

Let H_s be the set of unordered triples of head types that occur at steps 0, 1 of three compatible walks in state s, that is, pairs of ordered triples of T_s with j(a(0)) = i(a(1)) for each of the three walks. We assume

(3) sum of u over every triple in H_1 is at most 4(L-2) - 1; sum of l over every triple in H_2 is at least 2(L-2) + 1.

For L = 14 this is Lu's (3.2), since 4*12 = 48 and 2*12 = 24.

**Proposition 2.** Any three compatible walks in W_0 are identical, and a word is carried by at most one walk of W_0.

*Proof.* Suppose three compatible walks in W_0 are not all identical. By Lemma 1 they lie in a state s, all their step triples are in T_s, so none of the walks contains a blocking row and the head types of the three walks form a triple of H_s. For each step t >= 2 the three rows form a triple of T_s, so their scores add up to 4 (s = 1) or 2 (s = 2). Summing over the L - 2 steps t = 2, ..., L-1, the three suffix scores add up to 4(L-2) or 2(L-2). In state 1 admission gives G <= u_h for each walk, so the total is at most 4(L-2) - 1 by (3), a contradiction; in state 2, G >= l_h gives a total of at least 2(L-2) + 1, again a contradiction. For the second claim, if two different walks of W_0 had the same word w, the triple (w, w, w') would be compatible and not identical. []

Compatibility of words is the same as compatibility of any walks above them, so Proposition 2 is the hypothesis of Proposition 2.3 of [Lu] for the family of words of W_0 on the 12 L real positions. (We also check that the real projection of the 372 rows is injective, so that words and walks correspond one to one; this is not needed for the argument above.)

### 4. Recursion, dimension and the spectral bound

Each row has 10 * 7 + 2 = 72 real coordinates. At depth n we glue L rows. The slot of bit 5 at step te is replaced by the whole construction of depth n-1, whose colour is the bit of that row, and the scalar of bit 12 at step 0 is deleted as in Proposition 2.3(2). The hypotheses of that proposition concern the family of words and the slot axioms; they do not refer to the number of positions. The embedded slot is a two-color slot in its own right (induction), the remaining nine seven-dimensional slots of that row and the ten of every other row carry the alphabets U and M. The dimension added per level is

D = 72 L - 7 - 1 = 72 L - 8,

which is 1000 for L = 14 and 1216 for L = 17. The matrix K(X, Y) is defined as in Section 4.2 by the weights of closed walks of W_0 with output colour a (read from bit 12 of step 0) and embedded colour b (bit 5 at step te), where every other real slot contributes X, 64 + Y, 2 or 1 as in [Lu]. The proof of Theorem 4.1 carries over word for word. For records of depth n with outermost and innermost colour O and counts (A, B), the weight in (K_0^n)_{00} is X^A Y^B; tilting by t^{9B - 718A} or t^{6A - 137B} multiplies it by more than 1 outside the cone (4.1), so the records in the cone have total weight at least (K_0^n)_{00} - (K_-^n)_{00} - (K_+^n)_{00}; Proposition 5.2 supplies a cap set of size at least c X^A Y^B for each of them, the cap sets for different records are disjoint and their union is a cap set in F_3^{Dn} by Propositions 2.3 and 2 above; Perron-Frobenius for K_0 > 0 gives

Lambda >= rho(K_0)^{1/D}   whenever rho(K_0) > max(rho(K_-), rho(K_+)).

Neither Section 5 nor Appendices B and C involve L. Lemma 5.1 is a statement about grouped nodes of b inputs, b in {144, 182, 183, 252, 641}; Proposition 5.2 fills every record whose counts (A, B) lie in the cone, with a constant independent of (A, B), of the order of the open positions and of the nesting depth, because all open seven-dimensional positions of a record are pooled once across all levels. The prices X = Np, Y = 128q depend only on the seed z < Lambda, through (5.1). So the only place where L enters Section 5 is through the pair (A, B) of a record, which is exactly what K tracks.

### 5. The integer certificate for every L

Appendix A.3 of [Lu] uses a product of fourteen row tables of scale S, and weights with denominator f^{13*72+65} = f^{1001}. For general L the product of L row tables has scale S^L, and the denominator is f^{72(L-1) + 65} = f^{72L-7}: every row contributes f^{-72}, except that the embedded step contributes f^{-65} because the seven-dimensional slot is replaced. The entry is P_ab = R(f L_ab / S^{L-1}), which has scale S and carries f^{-(72L-8)}. The recursion runs over d = 2, ..., L-1. Since every L_ab is a polynomial with nonnegative integer coefficients in the rounded one-row entries, floor in the table for K_0 and ceiling in those for K_-, K_+ give

P_0 <= S f^{-D} K_0,   P_1 >= S f^{-D} K_-,   P_2 >= S f^{-D} K_+

entrywise, as in (A.5). With J = floor(rho(P_0)), P_0 > 0 and the two integer tests of A.4 for P_1 and P_2, we get max(rho(K_-), rho(K_+)) < f^D J / S <= rho(K_0), hence Lambda >= f (J/S)^{1/D}, which is compared with the target by integers. The chaining of seeds is unchanged, because a seed is used only as some proven z < Lambda.

### 6. What was checked by machine for L = 17, te = 8

For the 372 rows and the certificates L17c1 to L17c3, the checkers verify from the raw rows the witness property (0 violations over all multisets of three rows), the sets T_1, T_2 (1125 and 1800 triples), equal live sets (346 rows) in the two states, conservation of the score on every triple, inequalities (3) over all 353 and 656 head-type triples derived from the raw ordered triples (extreme sums 58 against 59 and 32 against 31), the four price inequalities, positivity of P_0, the rounding directions, the integer tests and the final inequality with D = 1216. Two further checks, not part of the certificates, were run for this appendix: with windows opened wide the matrix recursion agrees to 118 digits with the closed form f * trace(M_0 M_1 ... M_{16}) of the 2 x 2 port-weight matrices, with the embedded slot at step 8; and a direct search of the graph on triples of port bits, with an edge for each ordered triple of rows without a real slot carrying exactly two 1s, finds, for L = 2, 3, 5, 8, 14, 17 and 20, no closed walk with a non-identical step that leaves one of the states s = 1, s = 2, in agreement with Lemma 1.

[Lu] ZeHua Lu, *A Constructive Lower Bound for the Growth Constant of Ternary Cap Sets: Two-Color Recursion and Closed-Walk Synchronization*, arXiv:2611.30110.

## Reference

[Lu] ZeHua Lu, *A Constructive Lower Bound for the Growth Constant of Ternary Cap Sets: Two-Color Recursion and Closed-Walk Synchronization*, arXiv:2611.30110v1 [math.CO], 23 November 2026.

Computations assisted by AI tools (Claude).
