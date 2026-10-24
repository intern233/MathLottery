> Public showcase edition: private runtime details were redacted and paths made portable; the original conclusions and evidence levels are unchanged. Hashes and byte sizes in the report body, appendices and historical materials identify the original frozen inputs. Redaction, link edits and provenance notices change the public copies. To check files in this directory, use `files[].sha256` and `files[].bytes` in the [publication manifest](manifest.json), rather than treating differences from the original appendix hashes as corruption. The manifest distinguishes original and public hashes and byte sizes.

# MathLottery expert reading report

> This is an editorial reconstruction of saved research, not a new independent verification. Formatting does not upgrade proof status or certify open status or novelty.

Source task: `reviewed-source`; frozen revision: 16; captured: 2026-10-24T04:21:32.659285+00:00.

## Recorded verification outcomes

- `candidate-record-006` · `SELF_CHECKED` · scope `UNKNOWN`; verdict `NO_ISSUES_FOUND`, coverage `UNKNOWN`, novelty `UNKNOWN`

[Evidence manifest](manifest.json)

### Evidence scope and limitations

- This is an editorial reconstruction of visible saved evidence, not hidden reasoning, an independent mathematical verification, or a certification of novelty.
- reviewed-source: only saved answers, named notes, proof/formal files and source receipts are included; arbitrary workspace files, binaries and caches are excluded.
- This historical Verify has no saved solver linkage. The original Solve history is unavailable; matching titles or proofs were not used to guess it.

---

# Weighted distance powers in a medial triangle: expert report on Zeng–Fei–Yang Conjecture 5

**Abstract and exact conclusion.** The saved solution gives an affirmative proof of the original conjecture: the stated strict upper bound holds for every nondegenerate Euclidean plane triangle satisfying the side order, every point strictly inside its medial triangle, all positive real weights, and every positive integer exponent. The same submission proves a stronger closed-hull version, including the medial triangle's boundary, for suitable triples in any real inner product space. This report develops that existing proof in full rather than merely listing research events. The historical independent AI review returned `NO_ISSUES_FOUND`; independent recompilation of the three Lean sources, the complete geometry-to-algebra bridge, kernel replay, and a separate portable build have recorded historical successes. These facts coexist with the legacy database fields `SELF_CHECKED`, `scope=UNKNOWN`, and `original_problem_coverage=UNKNOWN`, which this report does not upgrade. Novelty and confirmed current open status remain `UNKNOWN`; there is no external expert certification.[D1] [H2] [S2]

**Sources and editorial scope.** This report uses only the Verify dossier frozen on 2026-10-24, the files in its manifest, and the explicitly supplied showcase supplement dated 2026-10-21. The supplement contains existing presentation documents and historical audit summaries; it is not newly collected review evidence in the native manifest. Literature status is reported only through 2026-10-21. This editorial session performed no online literature check, numerical experiment, Lean/Lake execution, or new independent review. Numbering, explanatory transitions, and translation are editorial exposition, not repairs to the candidate. References below to reviewing, compiling, or searching identify their historical source. The original candidate, review, and formal sources remain unchanged.

**1. Original problem, provenance, and evidence status.** Shanpeng Zeng, Hongliang Fei, and Xuezhi Yang, *Tracing the Origins and Generalizations of a Class of Moving Point Inequalities*, 19(1), 42–52, March 2026 issue; the publication record gives 2025-11-30 as the online publication date. The target appears in §4, “Open Problem,” on printed page 51, PDF page 10, as Conjecture 5; the preceding introduction also calls it Conjecture 5.5. The historical account records the positive-integer convention on page 43 and the first-power Inequality J on page 45. Publication as a conjecture at that time does not certify that it remained open on the date of this editorial work.[Publication record][B1] [Original PDF][B1PDF] [D1]

The following faithfully restates the frozen mathematical problem; it is not presented as a verbatim quotation obtained by rereading the PDF in this session.

**Theorem 1 (submitted conclusion for the original conjecture).** Let \(A,B,C\) be the vertices of a nondegenerate Euclidean plane triangle. Write \(|UV|\) for Euclidean distance and put

\[
a=|BC|,\qquad b=|CA|,\qquad c=|AB|,\qquad a\ge b\ge c>0,
\qquad s=\frac{b+c}{2}.
\]
\[
A'=\frac{B+C}{2},\qquad B'=\frac{A+C}{2},\qquad C'=\frac{A+B}{2},
\qquad M=\operatorname{conv}\{A',B',C'\}.
\]

For every \(P\in\operatorname{int}_{\mathbb R^2}M\), every \(x,y,z\in\mathbb R_{>0}\), and every \(n\in\mathbb Z_{\ge1}\),

\[
x|PA|^n+y|PB|^n+z|PC|^n
<\max\{x,y\}\left(\frac{b+c}{2}\right)^n+\max\{y,z\}a^n.
\tag{1}
\]

The weight–vertex pairing is fixed as \((x,A),(y,B),(z,C)\). The first maximum is exactly \(\max\{x,y\}\), and the second is \(\max\{y,z\}\). Replacing \(b+c\) by \(c+b\) changes nothing; replacing the first maximum by \(\max\{x,z\}\) changes the problem. The claim is not restricted to one exponent or to isosceles triangles, and no assertion is made for arbitrary real exponents.

**Status ledger.** The scope of the mathematical statement, legacy database fields, historical formal evidence, and novelty must be read separately.

| Item | Frozen record and interpretation |
|---|---|
| Discovery status | `UNKNOWN`; the recorded status-check date is 2026-10-21. It must not be rewritten as certified `OPEN`. |
| Candidate level and scope field | `level=SELF_CHECKED`, `scope=UNKNOWN`; the candidate's text explicitly claims the entire original problem and the closed-hull extension. |
| Historical independent review | `verdict=NO_ISSUES_FOUND`, `issues=[]`; this is an LLM review verdict. |
| Original-problem coverage field | `original_problem_coverage=UNKNOWN`, with an empty `coverage_explanation`; the legacy record lacks explicit coverage data and must not be filled in as newly certified `FULL` coverage. |
| Mathematical obligations field | Both candidate and review have `remaining_obligations=[]`; the review narrative identifies no substantive mathematical gap. Empty arrays do not supply missing historical materials or expert certification. |
| Formal record | Historical compilation and replay successes are described, while the old structure has `formal_check=null`, `formal_receipt=null`, `checks=[]`, and the dossier has `evidence_receipts=[]`. No harness-issued formal receipt may be invented; the historical Lean evidence must also not be erased. |
| Legacy evidence assessment | `evidence_assessment.supported=false`, with empty policy and checking information; this is not a failed Lean execution result. |
| Novelty and expert certification | `novelty=UNKNOWN`; there is no external mathematical expert review or external certification of natural-language/formal-statement equivalence. |

These entries come from the frozen candidate, review, and supplementary summary.[D1] [S2] The original candidate's opening statement that independent Verify was still pending describes its submission stage; the subsequent review was completed. Both time-ordered records are preserved without rewriting the earlier text.

**2. Notation, stronger statement, and proof dependencies.** For the extension, let \(E\) be any real inner product space and set \(|UV|=\|U-V\|\). The side lengths must be actual distances between three points, not arbitrary incompatible positive numbers. Assume \(A\ne B\) and the stated side order, giving precisely \(a\ge b\ge c>0\). Midpoints are defined by vector operations. The finite convex hull is

\[
M=\left\{\lambda_1A'+\lambda_2B'+\lambda_3C':
\lambda_i\ge0,\quad\lambda_1+\lambda_2+\lambda_3=1\right\}.
\tag{2}
\]

Zero coefficients are allowed, so edges and vertices are included. The convex hull of finitely many points is compact, hence closed; a formal declaration also establishes this explicitly.[F3] No completeness or finite-dimensionality assumption on \(E\) is required: this finite hull lies in a finite-dimensional affine subspace.

**Theorem 2 (submitted closed-hull extension).** Under the real-inner-product-space and actual-distance assumptions above, with \(a\ge b\ge c>0\), every \(P\in M\), all \(x,y,z>0\), and every integer \(n\ge1\) satisfy (1). This extension does not require the three points to be noncollinear. Theorem 1 follows because nondegeneracy implies \(A\ne B\), and the strict interior is contained in the convex hull.

For the proof, write

\[
u=|AA'|,\quad v=|BB'|,\quad w=|CC'|,
\qquad p=|PA|,\quad q=|PB|,\quad r=|PC|.
\]

The dependencies are as follows. Lemma 1 gives median estimates; Lemma 2 transfers them by convexity to geometric distance bounds. Lemma 3 supplies the two-term power bound used in the strict three-term bound of Lemma 4. Lemma 5 combines these results by ordering the two maximum weights, proving Theorem 2 and then Theorem 1. The method uses Apollonius' identity, convexity of the norm, convexity of integer powers, and an elementary weight decomposition. An initial unverified route was suggested by the controller; the solution explicitly credits that assistance and proves each step. The suggestion is not an axiom, and the controller is not the independent reviewer.[D1] [S1]

**3. Complete ordinary proof.** The lemmas below renumber the submitted proof's three steps and expand the transitions needed to follow them. This is not a new Solve, a replacement for failed reasoning, or a reconstruction of unsaved proof steps.

**Lemma 1 (strict median and midpoint-sum estimates).** The hypotheses of Theorem 2 imply \(0<s\le a\) and

\[
u<s,\qquad v<a,\qquad w<a,
\qquad u+a<a+s,\quad v+b<a+s,\quad w+c<a+s.
\tag{3}
\]

Proof. Expanding the inner product gives Apollonius' identities:

\[
4u^2=2b^2+2c^2-a^2,\qquad
4v^2=2a^2+2c^2-b^2,\qquad
4w^2=2a^2+2b^2-c^2.
\tag{4}
\]

For example, put \(X=B-A\) and \(Y=C-A\). Then \(2(A'-A)=X+Y\) and \(X-Y=B-C\), so

\[
4u^2=\|X+Y\|^2
=2\|X\|^2+2\|Y\|^2-\|X-Y\|^2
=2c^2+2b^2-a^2.
\]

Expanding at the other two vertices gives the remaining identities. The side order gives \(0<s\le a\), and

\[
4(s^2-u^2)=a^2-(b-c)^2
=(a-b+c)(a+b-c)>0.
\tag{5}
\]

The two factors are at least \(c>0\) and \(a>0\), respectively. Since \(u\ge0\) and \(s>0\), comparison of squares gives \(u<s\). Likewise,

\[
\begin{aligned}
4(a^2-v^2)&=2a^2+b^2-2c^2
\ge2a^2-b^2\ge a^2>0,\\
4(a^2-w^2)&=2a^2-2b^2+c^2\ge c^2>0.
\end{aligned}
\tag{6}
\]

Thus \(v<a\) and \(w<a\). To control the distance sums, set

\[
R_b=a+\frac{c-b}{2},\qquad R_c=a+\frac{b-c}{2}.
\]
\[
R_b\ge\frac{a+c}{2}>0,\qquad R_c\ge a>0,
\]
\[
\begin{aligned}
4(R_b^2-v^2)&=2(a-b)^2+c(4a-2b-c)>0,\\
4(R_c^2-w^2)&=2(a-c)^2+b(4a-2c-b)>0.
\end{aligned}
\tag{7}
\]

Equation (7) results from substituting (4) and expanding. Strictness follows from \(4a-2b-c\ge a>0\), \(4a-2c-b\ge a>0\), and \(b,c>0\). Hence \(v<R_b\) and \(w<R_c\), giving \(v+b<a+s\) and \(w+c<a+s\). Finally, \(u<s\) gives \(u+a<a+s\). No strict triangle inequality has been used, so the argument includes the collinear configurations allowed by the extension. This proves the lemma.[D1] [S1] [F2]

**Lemma 2 (actual geometric distance bounds on the closed hull).** Every \(P\in M\) satisfies

\[
0\le p,q,r\le a,\qquad p\le s,\qquad p+q+r<a+s.
\tag{8}
\]

Proof. The distance table at the three actual midpoints is:

| Point | Distance to \(A\) | Distance to \(B\) | Distance to \(C\) | Distance sum |
|---|---:|---:|---:|---:|
| \(A'\) | \(u\) | \(a/2\) | \(a/2\) | \(u+a<a+s\) |
| \(B'\) | \(b/2\) | \(v\) | \(b/2\) | \(v+b<a+s\) |
| \(C'\) | \(c/2\) | \(c/2\) | \(w\) | \(w+c<a+s\) |

The three distances to \(A\) do not exceed \(s\), because \(u<s\), \(b/2\le s\), and \(c/2\le s\). All entries are at most \(a\), by Lemma 1 and the side order.

For any fixed point \(X\), the triangle inequality and nonnegative homogeneity of the norm give

\[
\left|\sum_{i=1}^3\lambda_iQ_i-X\right|
=\left\|\sum_{i=1}^3\lambda_i(Q_i-X)\right\|
\le\sum_{i=1}^3\lambda_i|Q_i-X|,
\qquad \lambda_i\ge0,\quad\sum_{i=1}^3\lambda_i=1.
\tag{9}
\]

Taking \((Q_1,Q_2,Q_3)=(A',B',C')\) transfers the individual bounds to all of \(M\). The sum of distances is also convex. To make the strictness explicit, put

\[
D=\max\{u+a,v+b,w+c\}<a+s.
\]
\[
p+q+r\le\lambda_1(u+a)+\lambda_2(v+b)+\lambda_3(w+c)
\le D<a+s.
\tag{10}
\]

Only nonnegative coefficients are needed; they need not all be positive. Thus the strict bound also holds on edges and at vertices. Distances are nonnegative, proving (8). The auxiliary \(D\) merely makes the submitted argument about a convex combination of finitely many strict bounds explicit; it adds no assumption.[D1] [S1] [F2]

**Lemma 3 (endpoint bound for two powers).** Let \(0<s\le a\), \(t\in[s,a]\), and let \(n\ge1\) be an integer. Then

\[
t^n+(a+s-t)^n\le a^n+s^n.
\tag{11}
\]

Proof. The function \(f(t)=t^n+(a+s-t)^n\) is convex on \([s,a]\): both bases are nonnegative, and positive integer powers are convex on the nonnegative reals. For \(n=1\) the power function is linear; for \(n\ge2\) this is polynomial convexity from a nonnegative second derivative. If \(s=a\), the interval is a singleton and the conclusion is equality. If \(s<a\), set \(\theta=(t-s)/(a-s)\in[0,1]\). Then

\[
t=(1-\theta)s+\theta a,\qquad
f(t)\le(1-\theta)f(s)+\theta f(a)=a^n+s^n.
\]

The endpoint values are equal, giving (11). This case split expands the convexity argument already present in the submitted proof; its Lean counterpart is `two_power_le`.[D1] [S1] [F1]

**Lemma 4 (strict three-term power bound for every positive integer exponent).** Suppose \(0<s\le a\), \(p,q,r\in[0,a]\), and \(p+q+r<a+s\). For every integer \(n\ge1\),

\[
p^n+q^n+r^n<a^n+s^n.
\tag{12}
\]

Proof splits into two cases. If all three numbers are at most \(s\), then \(p^n\le p s^{n-1}\), with the same argument for the other two terms. Therefore

\[
\begin{aligned}
p^n+q^n+r^n
&\le(p+q+r)s^{n-1}\\
&<(a+s)s^{n-1}\\
&=a s^{n-1}+s^n\le a^n+s^n.
\end{aligned}
\tag{13}
\]

Strictness uses \(s^{n-1}>0\), and the final step uses \(s\le a\). For \(n=1\), \(s^{n-1}=1\), so the strict step remains valid.

Otherwise, call one number exceeding \(s\) by \(t\), and call the other two \(d,e\). There is no need to assume \(d,e\le s\). We have

\[
s<t\le a,\qquad 0\le d+e<a+s-t,\qquad a+s-t\ge s>0.
\]
\[
(d+e)^n-d^n-e^n
=\sum_{k=1}^{n-1}\binom{n}{k}d^k e^{n-k}\ge0.
\tag{14}
\]

For \(n=1\), the sum in (14) is empty and both sides are zero. Positive integer powers are strictly increasing on the nonnegative reals, so Lemma 3 gives

\[
t^n+d^n+e^n
\le t^n+(d+e)^n
<t^n+(a+s-t)^n
\le a^n+s^n.
\tag{15}
\]

This proves the lemma, including the endpoint \(t=a\). Strictness comes from the strict total-sum bound, not from requiring Lemma 3 to be strict. Lemma 4 itself does not use \(p\le s\); that individual bound is reserved for the weight argument.[D1] [S1] [F1]

**Lemma 5 (combining the two maximum weights).** Under the conditions of Lemmas 2 and 4, every \(x,y,z>0\) gives (1). Proof: put

\[
U=\max\{x,y\}>0,\qquad V=\max\{y,z\}>0,
\qquad T=p^n+q^n+r^n<a^n+s^n.
\]
\[
p^n\le s^n,\qquad r^n\le a^n.
\tag{16}
\]

If \(V\le U\), then \(x\le U\), \(y,z\le V\), and \(U-V\ge0\). Hence

\[
\begin{aligned}
xp^n+yq^n+zr^n
&\le Up^n+Vq^n+Vr^n\\
&=VT+(U-V)p^n\\
&<V(a^n+s^n)+(U-V)s^n\\
&=Us^n+Va^n.
\end{aligned}
\tag{17}
\]

Strictness follows from \(V>0\) and \(T<a^n+s^n\); the individual bound is multiplied by the nonnegative quantity \(U-V\).

If \(U\le V\), then \(x,y\le U\), \(z\le V\), and \(V-U\ge0\), so

\[
\begin{aligned}
xp^n+yq^n+zr^n
&\le Up^n+Uq^n+Vr^n\\
&=UT+(V-U)r^n\\
&<U(a^n+s^n)+(V-U)a^n\\
&=Us^n+Va^n.
\end{aligned}
\tag{18}
\]

Here strictness follows from \(U>0\). The two orderings exhaust all positive weights, including \(U=V\), proving (1).[D1] [S1] [F1]

**Completion of the proofs of Theorems 2 and 1.** Apply Lemmas 1 and 2 to the actual geometric distances, then Lemmas 3 and 4 to obtain (12), and finally Lemma 5 to prove Theorem 2. For Theorem 1, a nondegenerate plane triangle has \(A\ne B\); with the side order this gives \(c>0\). A strict interior point belongs to \(M\), so every hypothesis of Theorem 2 is satisfied. No finite numerical test is used, and the geometric bounds are not added as assumptions. The formal counterparts are exactly `conjecture5_closed` and its corollary `conjecture5_original`.[F3]

**4. Boundary, equality, and parameter endpoints.**

| Case | Treatment in the submitted proof |
|---|---|
| \(n=1\) | The zeroth power in (13) is 1, the sum in (14) is empty, and strictness still comes from (8). |
| \(s=a\), in particular an equilateral triangle | The interval in Lemma 3 is a singleton; under the side order, \(s=a\) implies \(a=b=c\). The branch of Lemma 4 with a term exceeding \(s\) cannot occur. |
| \(a=b\) or \(b=c\) | The positive terms in Lemma 1 remain positive because \(a,c>0\); distinct side lengths are unnecessary. |
| Tied weights, especially \(U=V\) | The correction term in (17) or (18) may vanish, but the weight multiplying the strict total-sum bound remains positive. |
| \(P\) on an edge or at a vertex of the medial triangle | Equations (2), (9), and (10) permit zero coefficients; (1) remains strict. |
| Collinear or degenerate configurations | Excluded from the original problem; included in the extension when actual distances still satisfy \(a\ge b\ge c>0\). No strict triangle inequality is needed. The historical review also examined degenerate limits, without extending the claim to \(c=0\). |
| Equality | Equality in (1) never occurs within the domains of Theorems 1 and 2, including boundary points. No uniform positive gap across excluded degeneracies or optimal-constant result is asserted. |
| Domains not claimed | \(n=0\), noninteger real exponents, nonpositive weights, \(c=0\), and points outside the hull are outside the report's conclusion. |

These endpoint explanations interpret the saved argument and review scope; they are not new extensions.[D1] [H2] [S1]

**5. Formal files, original-problem coverage, and correspondence of claims.** The three frozen Lean sources are directly available. Their counterparts in the review build have the same manifest hashes as the input copies; the supplement lists the same three source hashes. Versions are pinned to Lean 4.35.0 and mathlib commit `56a005855ea17e0b0958f73ec801ae140b0a1679`; the historical solution also records Lean commit `eb6cafb7290e8bd5f2937522d8d804f58f02bafc`.[F1] [F2] [F3] [F4] [F5] [S2]

| Mathematical content | Formal declarations and actual scope |
|---|---|
| Lemma 1, (4)–(7) | `median_estimates` in `MedialGeometry.lean` derives the estimates from median identities and side order; the enclosing `medial_distance_bounds` proves those identities from actual points using mathlib's Apollonius theorem. |
| Lemma 2, (8) | `convex_le_on_hull`, `convex_lt_on_hull`, and `medial_distance_bounds`; actual midpoint distances, individual bounds, and the strict total bound are all derived in Lean. |
| Lemmas 3 and 4 | `two_power_le`, `three_power_lt_of_large`, and `three_power_lt` in `MedialAlgebra.lean`; the final strict result requires `n : ℕ` and `1 ≤ n`, with no real-exponent theorem asserted. |
| Lemma 5 | `weighted_lt` combines already exponentiated nonnegative quantities; the final theorem substitutes the \(n\)-th powers of geometric distances, without omitting exponentiation. |
| Theorem 2 | `ZengFeiYang.conjecture5_closed`: any real inner product space, `A ≠ B`, two side-order relations, membership in the hull of the three actual midpoints, three positive real weights, and a positive integer exponent. |
| Closedness | `medialTriangle_isClosed` proves closedness using compactness of a finite convex hull; the closed-hull description does not omit the boundary. |
| Theorem 1 | `ZengFeiYang.conjecture5_original` derives the original statement from the closed-hull theorem; (8) is not an additional hypothesis. |

The written proof uses finite convex combinations for Lemma 2. The formal source instead uses convexity of strict/non-strict sublevel sets and `convexHull_min` to transfer the bounds. These express the same proof transition. The original-scope theorem directly uses the `interior` of the midpoint convex hull, so it needs no extra assumption equating strict interior with all-positive barycentric coordinates. Early problem metadata listed that equivalence as a feasibility concern; the final implementation avoids the additional representation obligation, without turning the concern into a newly proved lemma.[D1] [F2] [F3]

| Original condition | Expression in the frozen Lean theorem | Scope explanation |
|---|---|---|
| Euclidean plane and distance | `EuclideanSpace ℝ (Fin 2)`, `dist` | The independent scope file checks the coordinate formulas for the Euclidean norm and squared distance. |
| Nondegenerate triangle | `AffineIndependent ℝ ![A, B, C]` | The scope file checks equivalence with noncollinearity; injectivity gives `A ≠ B` in the main proof. |
| \(a\ge b\ge c\) | `dist A B ≤ dist C A`, `dist C A ≤ dist B C` | Vertex–side correspondence is preserved. |
| Three side midpoints | `midpoint ℝ B C`, `midpoint ℝ A C`, `midpoint ℝ A B` | The scope file checks the vector midpoint formula. |
| Strict interior | `P ∈ interior (convexHull ℝ {...})` | `interior_subset` supplies membership required by the closed-hull theorem. |
| All positive real weights | `x y z : ℝ`, `0 < x`, `0 < y`, `0 < z` | There is no normalization or distinct-weight restriction. |
| All positive integers | `n : ℕ`, `1 ≤ n` | This is not a finite list of exponents. |
| Strict upper bound and maxima | `<`, `max x y`, `max y z` | The original \((c+b)/2\) and the closed-hull version's \((b+c)/2\) are connected only by commutativity of addition. |

The saved independent `AuditScope.lean` also states the expected original type separately, using noncollinearity, and applies the submitted theorem. It is a review auxiliary, not one of the immutable candidate's three proof modules.[R1] The table explains the full scope of the written statements while retaining historical database coverage as `UNKNOWN`. The historical AI correspondence check and the Lean coordinate examples support this reading; they do not replace external expert certification of natural-language equivalence.

**6. Recorded verification results and tool trust boundaries.** The solution reports successful compilation of three modules, module replay, and fresh replay including dependencies. The historical independent review then recompiled the same sources in its own build directory, without reusing the solver's three compiled module objects. The table below records saved execution results, not output produced in this editorial session.[D1] [H2] [S2]

| Stage or check | Historical result | Evidence limit |
|---|---|---|
| Solver's three-module compilation and both replay modes | Reported exit codes all 0; both main theorem types and axioms printed | Reported in the solution; the complete original logs are not included in this bundle. |
| Independent review's three source compilations | All three exit codes 0 | Recorded in the exact review fields and supplement; source files are in the frozen manifest. |
| Independent review's module replay | `leanchecker --verbose MedialAlgebra MedialGeometry Conjecture5`, exit 0 | Uses Lean's own kernel. |
| Independent scope check | `AuditScope.lean` compiled with exit 0 | Source is retained; the log is represented by a summary and hash. |
| First independent fresh replay | Interrupted, `exit_code=null` | Not counted as a pass; the review says its interrupted log was separately saved, but that raw log is absent from this bundle. |
| Resumed independent fresh replay | `leanchecker --fresh --verbose Conjecture5`, exit 0 | Includes imported dependencies; success must not be backdated to the interrupted attempt. |
| Lake scope of the original independent review | Static checking of the pinned configuration; no separate online build from an empty cache | This original review limitation is preserved. |
| Later controller portable build | Initially failed, then succeeded after dependency-cache recovery | Explicit showcase supplement only; not attributed to the original independent review. |

The later portable sequence was: `lake update` exited 0; ordinary `lake exe cache get` exited 0; `lake build` exited **1**. The supplementary summary attributes the failure to an empty dependency `Name.ir.sig` and some empty `.trace` files left by an earlier interruption, producing invalid-header errors. A forced fetch of the required official dependency closure then exited 0; the retried `lake build` exited 0; `lake env lean Conjecture5.lean` exited 0. No proof source changed during recovery. This failed build and the interrupted fresh replay are distinct events, both retained.[S2] [S3]

The historical output lists only `propext`, `Classical.choice`, and `Quot.sound` as transitive axioms of the two main theorems. The historical source scan reports no `sorry`, `admit`, `sorryAx`, added `axiom`, `unsafe`, `native_decide`, or `Lean.ofReduceBool`; all three modules disable automatic implicit variables. Ordinary `decide` in the source only separates two indices of `Fin 3`.[D1] [F3] These records support successful Lean checking of the full stated formal theorem. They do not mean that the kernel proved natural-language equivalence or novelty. `leanchecker` still relies on Lean's kernel and implementation, rather than a different proof assistant; dependencies, toolchain, and axioms remain within the formal evidence's trust boundary.

**Role of finite computations.** The frozen problem's selection rationale records 12,000 fixed-seed floating-point instances with no violation, used for feasibility screening. The independent review records five symbolic expansions whose differences were zero and 5,040 edge-case instances at 120-digit precision with no violation. These are not finite certificates for the universal claim: numerical results do not cover infinitely many triangles, weights, and exponents or certify every limiting case of a strict inequality. The universal argument is the derivation above and its Lean counterpart. The native manifest does not supply the experimental scripts, exact seed, complete sampling domains, or raw result files, so the exact samples cannot be reproduced from the available materials. No missing commands or outputs are invented here.[D1]

**7. Existing methods, literature relations, and novelty limits.** The method combines classical median identities, convexity, and weight comparison; no novelty is claimed for these basic methods. Inequality J in the source paper gives the first-power medial-triangle version, whereas the conjecture asks for every positive integer exponent. The whole-triangle upper bound in the 2019 author text and the bound here are, respectively,

\[
B_{2019}=\max\{y,z\}a^n+\max\{x,z\}b^n,
\qquad
B_{\mathrm{medial}}=\max\{x,y\}s^n+\max\{y,z\}a^n.
\tag{19}
\]

Although \(s\le b\), the other maximum-weight factor differs, so \(B_{\mathrm{medial}}\le B_{2019}\) cannot be asserted for all positive weights. The early selection rationale described the older bound as weaker, and the solution described the medial bound as smaller. The historical independent review explicitly clarified that there is **no uniform ordering**. This report preserves that review finding rather than promoting the earlier wording to a proved comparison; it does not modify the original candidate. The 2019 result is not an immediate complete proof of the present statement: domains and weight correspondence still require comparison.[D1] [H2] [2019 author-text republication][B2]

The historical search through 2026-10-21 identified no prior public complete solution matching the entire original statement. This describes the recorded search only. Searches involving titles, Chinese and English author names, formula keywords, corrections, arXiv, GitHub, and public discussions do not exclude unsearched, unindexed, or unread results. Two specific unresolved sources are particularly material:

- For Hongliang Fei's 2025 *Guggenheimer 不等式的局部加强形式*, only the official acceptance list and the source paper's citation were obtained, not the full text. The historical review records reference [8] of the source paper as 2025(08), 43–44; this is cited bibliographic information. April 2025 is the acceptance-list date, not a publication date newly verified here. Neither the list nor the first-power citation rules out further results in the full paper.[B3] [D1]
- For *A Generalization of an Inequality for Moving Points in a Triangle*, dated 2026-09-15, DOI `10.51846/jnhm.v2i2.5387`, the historical materials obtained the official abstract, which discusses powers and multiple moving points for Erdős' 1935 Problem 3746. Direct access to the formal PDF and other full-text endpoints returned HTTP 403, and the web tool also failed to fetch the full text. The full paper was not read, and overlap with this problem was not excluded.[Official record][B4] [Formal PDF endpoint whose historical access failed][B4PDF] [D1]

The visible 2019 author republication was read through web tools/cache; direct HTTP download also returned 403. Acquisition of the journal-original full text was not claimed. In contrast, independent downloading of the source conjecture paper is recorded as HTTP 200, 11 pages, 222,898 bytes, with visual inspection of printed pages 45 and 51. Those PDF bytes are absent from the native manifest here; these facts are reported from the saved review.[D1]

Accordingly, `novelty=UNKNOWN` and discovery status `UNKNOWN` remain unchanged. A complete written proof, successful formal checking, literary priority, and certification that a problem remains open today are separate questions. The authors' published conjecture, the historical search date, and this report's date must not be conflated.[S2] [S3]

**8. Missing materials, unresolved matters, and editorial changes.** The saved review identifies no substantive mathematical gap in Theorems 1 and 2; both candidate and review have empty mathematical-obligation arrays. This report faithfully presents that outcome without adding a new passing verdict. Outstanding matters are the specific missing full texts and priority question, absence of external expert and statement-equivalence certification, and limits on the inspectability of historical evidence. More complete formatting cannot remove them.

The native dossier has `visible_research_notes=[]` and `review_source=null`. Its manifest contains one Verify dossier, two saved answers, and formal sources/configuration. The manifest explicitly states that solver linkage was not saved, so the original Solve history is unavailable. Matching titles, proofs, or similar hashes cannot be used to invent session connections. The available evidence is the solution embedded in the candidate and the explicit supplement, not a reconstructed Solve-session lineage.[D1]

Most historical files mentioned in the original text are not in this bundle: the full review report, original PDF and images, source audits, experiment directory, compilation/replay logs, archive manifests, solver wrapper, and source archive. Named examples are `review/report.md`, `review/evidence.json`, `review/edge-checks.json`, `review/sources/`, `review/logs/`, and, from the solution, `inputs/run_lean.py`, `notes/formal-source.tar`, `notes/literature/`, `experiments/`, `logs/validation.json`, `logs/artifact-manifest.json`, and `logs/SHA256SUMS`. These are historical filenames, **not links to attached materials**. Old machine-local paths cannot substitute for supplied material, and an empty answer cannot reveal reasoning preceding an interruption. The manifest's `omitted=[]` does not mean that every historical file is present.

The showcase `proof.md` is not byte-identical to the original candidate proof. Earlier presentation editing replaced the introduction and references, moved verification/literature appendix content into accompanying documentation, and corrected three mathematical typesetting errors by replacing misplaced dollar signs inside display mathematics with the intended parentheses. The mathematical route and the three Lean modules were unchanged. The supplement states that the current proof was then copied byte-for-byte from the preceding portable presentation; that relation between presentation versions does not imply identity with the original candidate text. The candidate-content hash, original-review-report hash, and presentation-proof hash are separately identified below. Preparing English/Chinese documentation and the bilingual exposition here is not a new proof review.[S1] [S2]

No proof repair is proposed or implemented in this report. If a substantive defect is later found, any possible repair must be presented separately as a proposal requiring a new Solve/Verify, not silently inserted into this organization report.

**Appendix A: concise chronology of saved attempts.** Times are UTC. Missing times are left unspecified rather than inferred from the narrative.

| Time or order | Saved content and outcome |
|---|---|
| 2026-10-21 04:50:45, problem status record | Discovery status `UNKNOWN`; feasibility ranking and 12,000 floating-point samples were exploratory only. Early `lean_feasibility=unknown` and text saying compilation had not yet occurred remain historical metadata, without negating later formal evidence. |
| Solution stage; independent timestamp and session linkage absent | A complete affirmative proof and closed-hull extension were submitted, with successful compilation and both replay modes reported. Independent Verify was still pending, and the candidate was `SELF_CHECKED`. Earlier failed explorations were said to be kept in experiments and numbered logs, but these are not attached; their counts, steps, and exit codes cannot be invented. |
| 2026-10-21 05:04:24 to 10:09:59, Verify container creation/last update | These are outer workflow timestamps, not the execution times of individual commands. |
| Historical independent review, first saved attempt | Status `INTERRUPTED`, with a zero-byte saved answer; no final conclusion can be extracted from it. The review narrative separately records the interrupted first fresh replay with a null exit code, not a pass.[H1] |
| Historical independent review, resumed saved attempt | Status `COMPLETED`; the answer and review fields record `NO_ISSUES_FOUND`, novelty `UNKNOWN`, and successful independent source compilation, module replay, scope checking, and resumed fresh replay. Exact per-check timestamps are not provided.[H2] [D1] |
| Later portable build; individual times absent | The controller built in another source directory; damaged cache caused exit 1, followed by exit 0 after forced recovery. This appears only in the explicit supplement and cannot be attributed retrospectively to the original independent review.[S2] |
| Existing presentation preparation; supplementary evidence date 2026-10-21 | Three typesetting corrections and documentation/appendix editing; the three Lean modules were unchanged. No new Lean build occurred during showcase export.[S2] |
| 2026-10-24 04:21:32, evidence freeze | Capture time of the native manifest; the explicit supplement accompanies the user's instructions. This is not a new verification or literature-status check. |
| This Organize session | Reading frozen material, explaining the mathematics, and checking bilingual formulas, scope, references, and evidence status; no Solve, Verify, or new Lean/Lake execution. |

**Appendix B: reproduction steps and bibliography.** The commands below are for later reproduction after obtaining the attached sources and official toolchain; none was executed during this Organize session. First compare the source hashes and version pins in Appendix C. The main procedure comes from the supplied formalization documentation. Run the first line from the report release bundle's root, then the remaining commands in that formal project directory.[S7] [S8]

```sh
cd materials/showcase/formal
lake update
lake exe cache get
lake build
lake env lean Conjecture5.lean
```

The version pins require `leanprover/lean4:v4.35.0` and the mathlib commit stated above. Network access retrieves toolchains and dependencies; the source package excludes large build products. The last command prints the main theorem types and transitive axioms; the historical result lists only `propext`, `Classical.choice`, and `Quot.sound`. After a successful build, the supplied documentation gives:

```sh
lake env leanchecker --verbose MedialAlgebra MedialGeometry Conjecture5
lake env leanchecker --fresh --verbose Conjecture5
```

This version requires explicit module names; the supplied documentation notes that it has no `--help` option. `--fresh` also replays imported dependencies and may take several minutes; it still uses Lean's kernel. The historical independent review records these original commands in an environment with dependency search paths configured:

```sh
lean -R . -o MedialAlgebra.olean MedialAlgebra.lean
lean -R . -o MedialGeometry.olean MedialGeometry.lean
lean -R . -o Conjecture5.olean Conjecture5.lean
lean -R . AuditScope.lean
```

`AuditScope.lean` must be obtained from the independent review auxiliary [R1]; it is not one of the showcase's three candidate proof modules. The old solver wrapper and complete environment are not supplied. The Lake procedure above is the supplied portable entry point, rather than a purported exact reconstruction of the old environment.

To preserve the actual recovery after failure, the supplementary summary records the following forced-cache command. It is a historical recovery action, not an additional check required after a successful build.[S2]

```sh
lake exe cache get! \
  Mathlib.Analysis.Convex.Jensen \
  Mathlib.Analysis.Convex.Mul \
  Mathlib.Analysis.Convex.Topology \
  Mathlib.Analysis.InnerProductSpace.PiL2 \
  Mathlib.Analysis.Normed.Module.Convex \
  Mathlib.Basic.Real.Basic \
  Mathlib.Geometry.Euclidean.Triangle \
  Mathlib.Tactic.Linarith \
  Mathlib.Tactic.Positivity \
  Mathlib.Tactic.Ring
lake build
```

The ordinary proof can be audited directly through Lemmas 1–5 without numerical experimentation. Scripts needed to reproduce exactly the 12,000 or 5,040 samples are absent, so no experimental reproduction commands are invented. Results of future executions should be recorded separately, without backfilling the historical chronology.

**Bibliography and source status (through 2026-10-21).**

| Reference | Bibliographic information and role in this report |
|---|---|
| [B1], [B1PDF] | Shanpeng Zeng, Hongliang Fei, Xuezhi Yang, *Tracing the Origins and Generalizations of a Class of Moving Point Inequalities*, 19(1), 42–52, March 2026 issue; online date 2025-11-30. Original target: §4, p.51; definitions pp.43–45. Source of the conjecture and cited first-power prior result; historical accounts report reading the full text, with no new download here. |
| [B2] | Hongliang Fei, Shanpeng Zeng, Xuezhi Yang, 《Guggenheimer 不等式的高次加权推广》, 《数学通报》58(5), 58–59, 2019; republication date 2019-07-09. The historically visible author text gives a whole-triangle bound with different weights, not certification of a complete solution to this problem. |
| [B3] | Official April 2025 acceptance list of the teachers' edition of 《数学通讯》, listing Hongliang Fei's 《Guggenheimer 不等式的局部加强形式》. List only, full text missing; 2025(08), 43–44 is information cited in the source paper's bibliography. |
| [B4], [B4PDF] | Shanpeng Zeng, Jing Liu, Xuezhi Yang, *A Generalization of an Inequality for Moving Points in a Triangle*, 2026-09-15, DOI `10.51846/jnhm.v2i2.5387`. Only the official abstract was historically read; full-text access failed and overlap remains unexcluded. |
| [B5] | mathlib documentation, `Mathlib.Analysis.Normed.Module.Convex`: foundational tools such as convexity of distance, not a prior proof of Conjecture 5. |
| [B6] | mathlib documentation, `Mathlib.Analysis.Convex.Mul`: tools for natural powers of nonnegative convex functions. The documentation URL is a historical reference; reproduction is pinned by the source commit. |

**Appendix C: material index, hash domains, and absent items.** Native materials below link to their actual relative paths in the frozen manifest. Visible labels describe evidence roles; link targets locate the original materials. Input and review-build copies of identical content receive separate links without being treated as new mathematical discoveries.

| Reference | Native frozen material | Bytes |
|---|---|---:|
| [D1] | Frozen dossier: problem, exact candidate proof, review fields, and two saved attempts | 32022 |
| [H1] | Interrupted historical review answer; empty file | 0 |
| [H2] | Completed historical review answer; its old machine-local paths are not material links in this report | 2150 |
| [F1] | Candidate input: Power-sum and weight proofs | 4564 |
| [R2] | Review-build copy: Power-sum and weight proofs | 4564 |
| [F2] | Candidate input: Actual geometric distance bounds | 6895 |
| [R3] | Review-build copy: Actual geometric distance bounds | 6895 |
| [F3] | Candidate input: Closed-hull theorem and original-scope corollary | 3376 |
| [R4] | Review-build copy: Closed-hull theorem and original-scope corollary | 3376 |
| [F4] | Candidate input: Project and pinned mathlib commit | 320 |
| [R5] | Review-build copy: Project and pinned mathlib commit | 320 |
| [F5] | Candidate input: Pinned Lean version | 25 |
| [R6] | Review-build copy: Pinned Lean version | 25 |
| [R1] | Independent scope-check auxiliary; not a candidate module | 2040 |

**Explicitly supplied showcase supplement.** These 14 files belong to the user's frozen supplementary inventory, **not** to the native collection entries of `organization-context/manifest.json`. The publication step is to attach the same presentation sources under `materials/showcase/`; links follow that convention. Directly supplied inline texts comprise the English overview, English review summary, English formalization instructions, ordinary proof, and an abridged `verification.json`. Other items are identified from the supplied inventory without claiming to have read unprovided full contents. The three Lean modules and two version/configuration files also have readable native copies above.

The inline `verification.json` explicitly omits a redundant file-hash index. Its inline text and the listed complete 8,058-byte file are different hash inputs; this is neither an evidential contradiction nor a reason to represent the abridged text as the complete attachment.

| Reference | Supplementary file and role | Listed bytes |
|---|---|---:|
| [S1] | `proof.md`: Existing presentation of the ordinary proof; Chinese original | 6573 |
| [S2] | `verification.json`: Historical verification summary; full file has the hash index omitted inline | 8058 |
| [S3] | `review.md`: Independent-review and later-build summary, English | 2460 |
| [S4] | `review.cn.md`: Review summary, Chinese | 1910 |
| [S5] | `README.md`: Case overview, English | 2253 |
| [S6] | `README.cn.md`: Case overview, Chinese | 1910 |
| [S7] | `formal/README.md`: Formalization notes and reproduction commands, English | 2679 |
| [S8] | `formal/README.cn.md`: Formalization notes and reproduction commands, Chinese | 2253 |
| [S9] | `formal/Conjecture5.lean`: Unchanged main-theorem source | 3376 |
| [S10] | `formal/MedialAlgebra.lean`: Unchanged algebra source | 4564 |
| [S11] | `formal/MedialGeometry.lean`: Unchanged geometry source | 6895 |
| [S12] | `formal/lake-manifest.json`: Portable-project dependency manifest | 3176 |
| [S13] | `formal/lakefile.toml`: Project configuration and pinned mathlib commit | 320 |
| [S14] | `formal/lean-toolchain`: Lean toolchain pin | 25 |

**Hash objects must be distinguished.** The table retains SHA-256 values from the source records. Original-evidence hashes identify their original objects; later presentation hashes identify only presentation bytes. A formal receipt's `problem_sha256`, when present, hashes the UTF-8 `Problem.statement`; the organization manifest's field with the same name is `discovery.problem_fingerprint` of the full canonical Problem record, including metadata and legacy-field normalization. These inputs differ and must not be compared across domains. The legacy review here has no `formal_receipt`; listing the statement-text hash does not create one. Hash agreement identifies bytes or canonical records, not mathematical correctness or natural-language correspondence.

| Object and domain | SHA-256 |
|---|---|
| Original Problem.statement text domain | `d5fb1e963dbeea8fba358cc4876e8f6714073af0f24b2c8df76e0ee941d9d59b` |
| Organization manifest: full Problem record fingerprint domain | `9bafa78c693f12e1337d3be7b391320fccfb9770326966c177a7415750549ddd` |
| Original candidate-content hash; not the presentation proof.md byte hash | `8a1a465483ee0d4b4417caa826e81a510a3060418209cb7305f31bdced5d1267` |
| Original full-review-report hash; report absent, distinct from the saved-answer hash | `6c1ad072da86a2538c8cd008400030150ac4c92d9bdbd3aede021e3b1fcbca9b` |
| Frozen dossier file bytes [D1] | `24a3b3d93149c23f32a7c30ce945f0a14f130e6cad2d2aa51667acb69cd0edbf` |
| Original downloaded PDF hash; PDF absent | `0d96143c1a8b348cbebcdc760f1547e7eaf85ab04448796bcb9324dfe531fd3b` |
| Later presentation ordinary proof [S1] | `fdd130c5ce90d2497196c9c03e1c42841b4422594e8852820fad25092b671833` |
| Later complete presentation verification summary [S2]; not the inline abridgment | `20285e38b8c9f430ecdf0f96f8de3bb4cc527a68299280b24f0f10aaa2662ee5` |

Original inputs, review copies, and presentation sources of the three proof modules share these recorded hashes:

| File | Materials | SHA-256 |
|---|---|---|
| `MedialAlgebra.lean` | [F1], [R2], [S10] | `676684cccd71e6c2a6294bc9f702137426e02fd68f6a8020d632a4dba9f013b1` |
| `MedialGeometry.lean` | [F2], [R3], [S11] | `e6879f933d7753421312220f7ad821e968d4a333aadf2139db0344460628bc94` |
| `Conjecture5.lean` | [F3], [R4], [S9] | `a3bfe87f49abf11394fc1b76c51c54b705c5c4f380273d0018955bbe20d6d5d9` |

Recorded historical independent-check log hashes follow. The raw logs are absent; these identifiers allow later matching to the original logs and are not execution receipts from this session.

| Historical check (each recorded exit 0) | Log SHA-256 |
|---|---|
| Algebra-module compilation | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| Geometry-module compilation | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| Main-module compilation | `8180a32f21764c0f771085a34f9d6baf4311b9fac2bf42b2cc7f84ec33f8ef74` |
| Three-module replay | `8b8ae13cfba362649c71276db63bb616b5e1b939480b3066bda681cafca679e8` |
| Independent scope check | `44c78b9a16092e0d5bacf72aa66c9fa857fcd9f315a63df23c6c6e275b930f11` |
| Resumed fresh replay | `77ff926b9f6cb12cf5f78e7cf26af53b2a11495e6a1d789e0a8646386a72d311` |

The first two hashes are those of empty byte strings. Historical records pair these empty logs with exit 0; absence of log text alone does not establish success. The interrupted replay and failed Lake build are not among the successful entries in this table; their outcomes remain explicit in section 6 and Appendix A. Listed sizes and hashes for all supplementary files come from the user's frozen inventory, and the complete presentation summary also contains a file index. No attachments have been invented for unavailable raw logs.

**Bilingual consistency statement.** Each language edition independently contains the full original problem, Theorems 1–2, Lemmas 1–5, equations (1)–(19), proof, boundary discussion, status ledger, failures and omissions, literature limits, chronology, reproduction commands, and material index. Both were generated from the same frozen sources. Numbering, all mathematical formulas, parameter domains, material/source links, key hashes, commands, and evidence status have been checked for editorial consistency. This comparison adds no mathematical review, formal execution, original-problem coverage certification, or novelty conclusion.

[D1]: materials/reviewed-source/dossier.json
[H1]: materials/reviewed-source/tasks/task-record-003/attempt-record-004/answer.md
[H2]: materials/reviewed-source/tasks/task-record-003/attempt-record-005/answer.md
[F1]: materials/reviewed-source/review-workspaces/candidate-record-006/inputs/final-formal/MedialAlgebra.lean
[R2]: materials/reviewed-source/review-workspaces/candidate-record-006/review-build/MedialAlgebra.lean
[F2]: materials/reviewed-source/review-workspaces/candidate-record-006/inputs/final-formal/MedialGeometry.lean
[R3]: materials/reviewed-source/review-workspaces/candidate-record-006/review-build/MedialGeometry.lean
[F3]: materials/reviewed-source/review-workspaces/candidate-record-006/inputs/final-formal/Conjecture5.lean
[R4]: materials/reviewed-source/review-workspaces/candidate-record-006/review-build/Conjecture5.lean
[F4]: materials/reviewed-source/review-workspaces/candidate-record-006/inputs/final-formal/lakefile.toml
[R5]: materials/reviewed-source/review-workspaces/candidate-record-006/review-build/lakefile.toml
[F5]: materials/reviewed-source/review-workspaces/candidate-record-006/inputs/final-formal/lean-toolchain
[R6]: materials/reviewed-source/review-workspaces/candidate-record-006/review-build/lean-toolchain
[R1]: materials/reviewed-source/review-workspaces/candidate-record-006/review-build/AuditScope.lean
[S1]: materials/showcase/proof.md
[S2]: materials/showcase/verification.json
[S3]: materials/showcase/review.md
[S4]: materials/showcase/review.cn.md
[S5]: materials/showcase/README.md
[S6]: materials/showcase/README.cn.md
[S7]: materials/showcase/formal/README.md
[S8]: materials/showcase/formal/README.cn.md
[S9]: materials/showcase/formal/Conjecture5.lean
[S10]: materials/showcase/formal/MedialAlgebra.lean
[S11]: materials/showcase/formal/MedialGeometry.lean
[S12]: materials/showcase/formal/lake-manifest.json
[S13]: materials/showcase/formal/lakefile.toml
[S14]: materials/showcase/formal/lean-toolchain
[B1]: https://ijopcm.zuj.edu.jo/index.php/IJOPCM/article/view/56
[B1PDF]: https://ijopcm.zuj.edu.jo/index.php/IJOPCM/article/download/56/43
[B2]: https://www.fx361.com/page/2019/0709/17500318.shtml
[B3]: https://shuxuetongxun.com/journal/teacher/2025/4
[B4]: https://journals.uol.edu.pk/JNHM/article/view/5387
[B4PDF]: https://journals.uol.edu.pk/JNHM/article/download/5387/2470/26948
[B5]: https://leanprover-community.github.io/mathlib4_docs/Mathlib/Analysis/Normed/Module/Convex.html
[B6]: https://leanprover-community.github.io/mathlib4_docs/Mathlib/Analysis/Convex/Mul.html
