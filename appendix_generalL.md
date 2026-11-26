# Appendix. Lu's construction for an arbitrary walk length L

Lu states and carries out his construction for closed walks of length 14. In this appendix we go through it for a walk length L, with the embedding step te in {3, ..., L-1}, and show that nothing in the argument depends on L = 14, te = 7 beyond arithmetic that we redo. The headline certificate uses L = 17, te = 8. Section numbers refer to [Lu]. Throughout, a row is a 14-bit mask with port bits 0 (source) and 6 (target, complemented), ten seven-dimensional real slots (bits 1-5, 7-11), and two scalar real slots (bits 12, 13); i(r) = r_0, j(r) = 1 - r_6.

## 1. Setting

Let R be a family of rows. A closed walk of length L is a sequence r(0), ..., r(L-1) in R with j(r(t)) = i(r(t+1)), indices mod L; its word is the array of real bits (1 for T, 0 for O). Three walks are compatible if no real slot at any step carries exactly two 1s among the three rows at that step. We assume that R has the witness property: any three rows of R, not all equal (repetition allowed), have a coordinate among all 14 bits with exactly two 1s. Equivalently, R is an antichain without 3-sunflowers. For T_s (s = 1, 2) we take the set of multisets {a, b, c} of rows with no real coordinate carrying exactly two 1s, with s ones among the three source ports and s ones among the three target ports. A row is live if it lies in some triple of T_1, and blocking otherwise; we require that it lies in some triple of T_1 if and only if it lies in some triple of T_2.

## 2. Port-state conservation for every L

**Lemma 1.** Let three compatible closed walks of length L over R be not all identical. Then there is s in {1, 2} such that, at every step t, exactly s of the three source ports equal 1 and exactly s of the three target ports equal 1. In particular the three rows at every step are not all equal, and the three rows at every step form a triple of T_s.

*Proof.* Let s_t be the number of 1s among the three source ports at step t. If the rows at step t are not all equal, the witness property gives a coordinate with exactly two 1s; compatibility excludes real slots, so it is a port bit. If it is the source bit, s_t = 2. If it is the target bit, two of the rows have r_6 = 1, exactly one target equals 1, and since the source ports at step t+1 are the targets at step t, s_{t+1} = 1. Hence

(*) if the rows at step t are not all equal, then s_t = 2 or s_{t+1} = 1.

Suppose s_t = 2 for some t. The targets at step t-1 are the sources at step t, so they are mixed and the rows at step t-1 are not all equal. By (*) at t-1, s_{t-1} = 2 or s_t = 1; the second is false, so s_{t-1} = 2. Going backwards around the cycle gives s_t = 2 for all t. Otherwise s_t is never 2. The walks are not identical, so some step t_0 has unequal rows, and (*) gives s_{t_0+1} = 1. Then the sources at step t_0+1 are mixed, so the rows there are unequal, and (*) gives s_{t_0+2} = 1. Going forward around the cycle gives s_t = 1 for all t. The target counts at step t equal s_{t+1} = s. A step with s in {1, 2} cannot have three equal rows, since their source ports would sum to 0 or 3. Finally each step has no real slot with exactly two 1s, so the step triple lies in T_s. The cycle length enters only through the indices modulo L. []

Rows that lie in no triple of T_1 (equivalently of T_2) therefore never occur in a compatible non-identical triple. We call them blocking and admit every walk that contains one.

## 3. The base family for every L

Let e: live rows -> {0, 1, 2} satisfy e(a)+e(b)+e(c) = 4 for every triple in T_1 and 2 for every triple in T_2. (The choice e = 2 - i - j always satisfies this, since the sum over a triple of T_s is 6 - 2s.) The head of a walk consists of its rows at steps 0 and 1, and a head type is the pair of row types of these two rows. For a blocking-free walk let G = e(r(2)) + ... + e(r(L-1)) be its suffix score, a sum of L - 2 terms. For each head type h fix integers l_h, u_h. Let W_0 consist of all walks that contain a blocking row together with all blocking-free walks with l_h <= G <= u_h.

Let H_s be the set of unordered triples of head types that occur at steps 0, 1 of three compatible walks in state s, that is, pairs of ordered triples of T_s with j(a(0)) = i(a(1)) for each of the three walks. We assume

(3) sum of u over every triple in H_1 is at most 4(L-2) - 1; sum of l over every triple in H_2 is at least 2(L-2) + 1.

For L = 14 this is Lu's (3.2), since 4*12 = 48 and 2*12 = 24.

**Proposition 2.** Any three compatible walks in W_0 are identical, and a word is carried by at most one walk of W_0.

*Proof.* Suppose three compatible walks in W_0 are not all identical. By Lemma 1 they lie in a state s, all their step triples are in T_s, so none of the walks contains a blocking row and the head types of the three walks form a triple of H_s. For each step t >= 2 the three rows form a triple of T_s, so their scores add up to 4 (s = 1) or 2 (s = 2). Summing over the L - 2 steps t = 2, ..., L-1, the three suffix scores add up to 4(L-2) or 2(L-2). In state 1 admission gives G <= u_h for each walk, so the total is at most 4(L-2) - 1 by (3), a contradiction; in state 2, G >= l_h gives a total of at least 2(L-2) + 1, again a contradiction. For the second claim, if two different walks of W_0 had the same word w, the triple (w, w, w') would be compatible and not identical. []

Compatibility of words is the same as compatibility of any walks above them, so Proposition 2 is the hypothesis of Proposition 2.3 of [Lu] for the family of words of W_0 on the 12 L real positions. (We also check that the real projection of the 372 rows is injective, so that words and walks correspond one to one; this is not needed for the argument above.)

## 4. Recursion, dimension and the spectral bound

Each row has 10 * 7 + 2 = 72 real coordinates. At depth n we glue L rows. The slot of bit 5 at step te is replaced by the whole construction of depth n-1, whose colour is the bit of that row, and the scalar of bit 12 at step 0 is deleted as in Proposition 2.3(2). The hypotheses of that proposition concern the family of words and the slot axioms; they do not refer to the number of positions. The embedded slot is a two-color slot in its own right (induction), the remaining nine seven-dimensional slots of that row and the ten of every other row carry the alphabets U and M. The dimension added per level is

D = 72 L - 7 - 1 = 72 L - 8,

which is 1000 for L = 14 and 1216 for L = 17. The matrix K(X, Y) is defined as in Section 4.2 by the weights of closed walks of W_0 with output colour a (read from bit 12 of step 0) and embedded colour b (bit 5 at step te), where every other real slot contributes X, 64 + Y, 2 or 1 as in [Lu]. The proof of Theorem 4.1 carries over word for word. For records of depth n with outermost and innermost colour O and counts (A, B), the weight in (K_0^n)_{00} is X^A Y^B; tilting by t^{9B - 718A} or t^{6A - 137B} multiplies it by more than 1 outside the cone (4.1), so the records in the cone have total weight at least (K_0^n)_{00} - (K_-^n)_{00} - (K_+^n)_{00}; Proposition 5.2 supplies a cap set of size at least c X^A Y^B for each of them, the cap sets for different records are disjoint and their union is a cap set in F_3^{Dn} by Propositions 2.3 and 2 above; Perron-Frobenius for K_0 > 0 gives

Lambda >= rho(K_0)^{1/D}   whenever rho(K_0) > max(rho(K_-), rho(K_+)).

Neither Section 5 nor Appendices B and C involve L. Lemma 5.1 is a statement about grouped nodes of b inputs, b in {144, 182, 183, 252, 641}; Proposition 5.2 fills every record whose counts (A, B) lie in the cone, with a constant independent of (A, B), of the order of the open positions and of the nesting depth, because all open seven-dimensional positions of a record are pooled once across all levels. The prices X = Np, Y = 128q depend only on the seed z < Lambda, through (5.1). So the only place where L enters Section 5 is through the pair (A, B) of a record, which is exactly what K tracks.

## 5. The integer certificate for every L

Appendix A.3 of [Lu] uses a product of fourteen row tables of scale S, and weights with denominator f^{13*72+65} = f^{1001}. For general L the product of L row tables has scale S^L, and the denominator is f^{72(L-1) + 65} = f^{72L-7}: every row contributes f^{-72}, except that the embedded step contributes f^{-65} because the seven-dimensional slot is replaced. The entry is P_ab = R(f L_ab / S^{L-1}), which has scale S and carries f^{-(72L-8)}. The recursion runs over d = 2, ..., L-1. Since every L_ab is a polynomial with nonnegative integer coefficients in the rounded one-row entries, floor in the table for K_0 and ceiling in those for K_-, K_+ give

P_0 <= S f^{-D} K_0,   P_1 >= S f^{-D} K_-,   P_2 >= S f^{-D} K_+

entrywise, as in (A.5). With J = floor(rho(P_0)), P_0 > 0 and the two integer tests of A.4 for P_1 and P_2, we get max(rho(K_-), rho(K_+)) < f^D J / S <= rho(K_0), hence Lambda >= f (J/S)^{1/D}, which is compared with the target by integers. The chaining of seeds is unchanged, because a seed is used only as some proven z < Lambda.

## 6. What was checked by machine for L = 17, te = 8

For the 372 rows and the certificates L17c1 to L17c3, the checkers verify from the raw rows the witness property (0 violations over all multisets of three rows), the sets T_1, T_2 (1125 and 1800 triples), equal live sets (346 rows) in the two states, conservation of the score on every triple, inequalities (3) over all 353 and 656 head-type triples derived from the raw ordered triples (extreme sums 58 against 59 and 32 against 31), the four price inequalities, positivity of P_0, the rounding directions, the integer tests and the final inequality with D = 1216. Two further checks, not part of the certificates, were run for this appendix: with windows opened wide the matrix recursion agrees to 118 digits with the closed form f * trace(M_0 M_1 ... M_{16}) of the 2 x 2 port-weight matrices, with the embedded slot at step 8; and a direct search of the graph on triples of port bits, with an edge for each ordered triple of rows without a real slot carrying exactly two 1s, finds, for L = 2, 3, 5, 8, 14, 17 and 20, no closed walk with a non-identical step that leaves one of the states s = 1, s = 2, in agreement with Lemma 1.

[Lu] ZeHua Lu, *A Constructive Lower Bound for the Growth Constant of Ternary Cap Sets: Two-Color Recursion and Closed-Walk Synchronization*, arXiv:2611.30110.
