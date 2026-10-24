> Public showcase edition: private runtime details were redacted and paths made portable; the original conclusions and evidence levels are unchanged. Hashes and byte sizes in the report body, appendices and historical materials identify the original frozen inputs. Redaction, link edits and provenance notices change the public copies. To check files in this directory, use `files[].sha256` and `files[].bytes` in the [publication manifest](manifest.json), rather than treating differences from the original appendix hashes as corruption. The manifest distinguishes original and public hashes and byte sizes.

# MathLottery expert reading report

> This is an editorial reconstruction of saved research, not a new independent verification. Formatting does not upgrade proof status or certify open status or novelty.

Source task: `reviewed-source`; frozen revision: 9; captured: 2026-10-24T04:21:35.242517+00:00.

## Recorded verification outcomes

- `candidate-record-005` · `SELF_CHECKED` · scope `UNKNOWN`; verdict `NO_ISSUES_FOUND`, coverage `UNKNOWN`, novelty `UNKNOWN`

[Evidence manifest](manifest.json)

### Evidence scope and limitations

- This is an editorial reconstruction of visible saved evidence, not hidden reasoning, an independent mathematical verification, or a certification of novelty.
- reviewed-source: only saved answers, named notes, proof/formal files and source receipts are included; arbitrary workspace files, binaries and caches are excluded.
- This historical Verify has no saved solver linkage. The original Solve history is unavailable; matching titles or proofs were not used to guess it.

---

# A counterexample to the stepwise irregular degree-sequence conjecture

**English expert report · frozen literature evidence through 2026-10-21 · editorial snapshot captured on 2026-10-24**

## Abstract and exact conclusion

The saved solution gives a counterexample to Conjecture 1 in Bera–Paul–Subramanian, *Some properties of stepwise irregular graphs*, EJGTA 14(1) (2026), printed p. 223. The degree sequence

\[
d=(6^4,5^6,4^1,3^1,2^3,1^1)
\]

satisfies every premise of the printed sufficiency conjecture and admits an ordinary simple connected bipartite realization with 16 vertices and 34 edges. Nevertheless, it has no stepwise irregular (SI) realization, even if connectivity is dropped. In any SI realization, the three degree-2 vertices would require six incident edges to the degree-1 and degree-3 classes, whose combined degree is only four. The contradiction is universal; it does not come from a bounded search. The explicit ordinary graph establishes graphicality separately from this non-realizability proof.

The stored candidate level remains **`SELF_CHECKED`**. The historical independent AI review returned **`NO_ISSUES_FOUND`**, with novelty **`UNKNOWN`**. The legacy candidate `scope` and review `original_problem_coverage` remain **`UNKNOWN`**. The written argument purports to refute the full universal conjecture; that mathematical scope is not a newly awarded `FULL` database certification. There is **no Lean formalization**, external expert review, or external statement-equivalence certification. The counting method has a recorded 2022 precedent. [Frozen dossier, M1](materials/reviewed-source/dossier.json); [saved historical review answer, M2](materials/reviewed-source/tasks/task-record-003/attempt-record-004/answer.md); [explicit showcase verification summary, S7](materials/showcase/verification.json).

## 1. Sources, provenance, and editorial status

The native frozen bundle contains one dossier, with the original candidate proof and one structured review, and one saved review answer. It contains no visible research notes or evidence receipts. Its manifest explicitly records that this historical Verify has no saved solver linkage: the original Solve history is unavailable. Similar titles or proof text have not been used to invent a session association. The showcase supplement is a separately and explicitly supplied presentation of existing evidence; it is not an additional native Verify attachment or a later result retroactively credited to that review.

This report faithfully reorganizes the saved mathematical argument. Theorem and lemma numbers, the separation of proof obligations, the expanded explanation of the recorded layer recurrence, and the bilingual exposition are editorial. They are not a new Solve, independent Verify, formal proof, or proof repair. The original candidate and review are unchanged. The native proof and saved answer are in Chinese; the English exposition here is editorial translation, not an asserted historical English solver/reviewer checkpoint. The showcase proof moves the original code appendix into a separate checker file and adds relative links; its mathematical text and adjacency table are recorded as unchanged. Translation is not a further proof review. [M1](materials/reviewed-source/dossier.json); [showcase proof, S4](materials/showcase/proof.md); [showcase review, S6](materials/showcase/review.md).

All statements about past downloads, computations, and literature searches below are attributed to the frozen records. No new literature search, Lean/Lake execution, certificate execution, or mathematical experiment was performed for this organization. Editorial checks of file identities and bilingual consistency do not change evidence levels. The literature cutoff is **2026-10-21**, not the later editorial snapshot date.

## 2. Original conjecture, notation, and parameter domains

The source is Somnath Bera, Prithwineel Paul, and K. G. Subramanian, *Some properties of stepwise irregular graphs*, Section 4, Conjecture 1, printed p. 223 (PDF p. 9). Definitions and the standing simple-connected-graph convention are on p. 216. The frozen source records journal issue 14(1), pp. 215–230, DOI 10.5614/ejgta.2026.14.1.14, and publication on 2026-04-22. The journal metadata date takes precedence over a generic January date in an institutional publication list. This is a mathematical transcription of the saved statement and source review, not a new inspection of the publisher PDF. [Original article, B1](https://www.ejgta.org/index.php/ejgta/article/download/1077/pdf_357); [journal metadata, B7](https://www.ejgta.org/index.php/ejgta/article/view/1077); [M1](materials/reviewed-source/dossier.json).

Graphs here are finite, undirected, and simple: no loops and no multiple edges. For a graph \(G=(V,E)\), \(\deg_G(v)\) is the number of neighbors of \(v\). An SI graph satisfies

\[
|\deg_G(u)-\deg_G(v)|=1\qquad\text{for every }uv\in E.
\]

The paper normally also requires connectedness. Let \(m,M\) be integer minimum and maximum degree entries with \(m<M\). The surrounding nontrivial connected-graph context uses \(1\le m<M\). The frozen statement flags rather than exploits any possible zero-degree ambiguity; the counterexample has \(m=1\). For every integer \(m\le i\le M\), let \(n_i\in\mathbb Z_{>0}\). Thus every degree class between the two endpoints is present. The notation \(i^{n_i}\) means the degree \(i\) repeated \(n_i\) times, not exponentiation. Write

\[
d=(M^{n_M},(M-1)^{n_{M-1}},\ldots,m^{n_m}),
\qquad N=\sum_{i=m}^{M}n_i.
\]

**Conjecture 1, as preserved in the frozen record.** If

\[
n_{M-1}\ge\max\{M,n_M\},
\qquad
\sum_{\substack{m\le i\le M\\i\equiv M\pmod 2}}i n_i
=
\sum_{\substack{m\le i\le M\\i\not\equiv M\pmod 2}}i n_i,
\tag{1}
\]

then \(d\) is the degree sequence of an SI graph, connected under the paper's standing convention. Ordinary graphicality and \(n_1\le n_2\) are not explicit premises of this conjecture; neither has been silently inserted.

For clarity about both endpoint cases, the parity equality in (1) can be written as follows. These are editorial expansions of the same condition:

\[
\begin{array}{ll}
M-m=2r,\ r\ge1:
&\displaystyle\sum_{j=0}^{r}(M-2j)n_{M-2j}
=\sum_{j=0}^{r-1}(M-2j-1)n_{M-2j-1},\\[4pt]
M-m=2r+1,\ r\ge0:
&\displaystyle\sum_{j=0}^{r}(M-2j)n_{M-2j}
=\sum_{j=0}^{r}(M-2j-1)n_{M-2j-1}.
\end{array}
\tag{2}
\]

Every SI edge joins an even-degree vertex to an odd-degree vertex. Counting each edge once at each side explains why the two degree sums must agree. This global balance does not guarantee adequate capacity in each neighboring pair of degree layers; that distinction drives the counterexample.

For a hypothetical realization, define \(V_i=\{v\in V:\deg_G(v)=i\}\), so \(|V_i|=n_i\). In formulas involving neighboring layers, set \(n_i=0\) outside the specified degree interval. This is a convention for empty layers, not an addition of isolated vertices. For disjoint vertex sets \(A,B\), let \(e(A,B)\) count the edges with one endpoint in \(A\) and the other in \(B\).

## 3. Theorem and proof strategy

**Theorem 1 — submitted counterexample.** For

\[
m=1,\quad M=6,\quad(n_1,n_2,n_3,n_4,n_5,n_6)=(1,3,1,1,6,4),
\tag{3}
\]

the sequence \(d\) satisfies (1), has a simple connected bipartite realization, and has no SI realization, whether connected or disconnected. It therefore refutes the printed universal sufficiency conjecture. The ordinary realization has \(N=16\) and \(|E|=34\).

There are three distinct obligations. Lemma 1 checks the hypotheses. Lemmas 2–3 give the universal obstruction. Lemma 4 constructs an ordinary connected graph, ruling out an objection based on nongraphicality. Lemma 5 expands a second formulation already recorded by the historical reviewer; it is corroborating exposition and is not needed for the main proof. The dependency is

\[
\text{Lemma 2}\Longrightarrow\text{Lemma 3},\qquad
\text{Lemmas 1, 3, 4}\Longrightarrow\text{Theorem 1}.
\]

The source for Lemmas 1–4 is the candidate proof embedded in [M1](materials/reviewed-source/dossier.json), also presented in [S4](materials/showcase/proof.md). Lemma 5 and the additional degree-5 obstruction are in the structured historical review in [M1](materials/reviewed-source/dossier.json). No preceding construction theorem from the source paper is used.

## 4. Detailed proof

### Lemma 1 — the sequence satisfies every conjectural premise

The degree data and the saved additional neighbor-count check are

| \(i\) | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---:|---:|---:|---:|---:|---:|
| \(n_i\) | 1 | 3 | 1 | 1 | 6 | 4 |
| \(i n_i\) | 1 | 6 | 3 | 4 | 30 | 24 |
| \(n_{i-1}+n_{i+1}\), with \(n_0=n_7=0\) | 3 | 2 | 4 | 7 | 5 | 6 |

**Proof.** All six multiplicities are positive integers. The top-layer hypothesis holds, including its allowed equality case:

\[
n_{M-1}=n_5=6=\max\{6,4\}=\max\{M,n_M\}.
\tag{4}
\]

Here \(M-m=5\) is odd. The degree sums are

\[
6n_6+4n_4+2n_2=24+4+6=34,
\qquad
5n_5+3n_3+n_1=30+3+1=34.
\tag{5}
\]

Thus (1) holds. Also \(N=4+6+1+1+3+1=16\), and the total degree is \(68\).

The saved proof includes three stronger checks, which are not additional premises of the original conjecture:

\[
n_1=1\le3=n_2,\qquad
6n_6=24<30=5n_5,\qquad
i\le n_{i-1}+n_{i+1}\quad(1\le i\le6).
\tag{6}
\]

For the last inequality, compare the first and last rows of the table. In a simple SI graph, a degree-\(i\) vertex can only use distinct vertices from the neighboring degree classes. This individual-vertex check passes, but it does not check whether all vertices in a degree class can simultaneously fit into the total incidence capacity of those classes. That stronger constraint is Lemma 2. \(\square\)

### Lemma 2 — necessary local incidence capacity

For every finite simple SI graph and every positive degree index \(i\), with absent layers assigned multiplicity zero,

\[
i n_i\le(i-1)n_{i-1}+(i+1)n_{i+1}.
\tag{7}
\]

**Proof.** No two vertices in \(V_i\) can be adjacent, because their degrees differ by zero. Every neighbor of \(V_i\) lies in \(V_{i-1}\cup V_{i+1}\), because an SI edge has degree difference exactly one. Consequently each edge incident to \(V_i\) is counted exactly once in its degree sum, and

\[
e(V_i,V_{i-1}\cup V_{i+1})
=\sum_{v\in V_i}\deg_G(v)=i n_i.
\]

Each such edge uses one incidence at a vertex of \(V_{i-1}\cup V_{i+1}\). Distinct edges use distinct incidences, although they may share a vertex. The total number of available incidences there is

\[
\sum_{v\in V_{i-1}\cup V_{i+1}}\deg_G(v)
=(i-1)n_{i-1}+(i+1)n_{i+1}.
\]

Some of these incidences may be used by edges to other degree layers, so this is an upper bound, not an asserted equality. Combining the two counts proves (7). Connectivity is not used. \(\square\)

This elementary argument is included in full for auditability. The historical review located the same necessary inequality in Adiyanyam–Azjargal–Buyantogtokh (2022), printed p. 8687, equation (2.4); no originality of the method is claimed. [B2](https://www.aimspress.com/aimspress-data/math/2022/5/PDF/math-07-05-485.pdf); [M1](materials/reviewed-source/dossier.json).

### Lemma 3 — no SI graph can realize the sequence

**Proof.** Assume an SI realization of (3) exists. Its three degree-2 vertices have total degree

\[
2n_2=2\cdot3=6.
\]

All of their neighbors must have degree 1 or 3. Those two classes have total degree

\[
n_1+3n_3=1+3\cdot1=4.
\]

Lemma 2 would therefore require \(6\le4\), a contradiction. This excludes every SI realization of this degree sequence. It is not a claim that only the displayed ordinary graph fails to be SI, and it does not rely on searching through possible graphs. Connectivity was never used. \(\square\)

The historical review also recorded a second violation of (7), at degree 5:

\[
5n_5=30>4n_4+6n_6=4+24=28.
\tag{8}
\]

This is another manifestation of the saved obstruction, not a new editorial search result. Either violation suffices; the degree-2 argument is the main proof.

### Lemma 4 — an ordinary simple connected bipartite realization

Let the disjoint vertex sets be

\[
L=\{a_1,a_2,a_3,a_4,b,c_1,c_2,c_3\},\qquad
R=\{u_1,u_2,u_3,u_4,u_5,u_6,v,w\}.
\]

Add exactly the following cross-part edges, once each, and no other edges:

| Left vertex | Its complete set of neighbors in \(R\) |
|---|---|
| Each of \(a_1,a_2,a_3\) | \(u_1,u_2,u_3,u_4,u_5,u_6\) |
| \(a_4\) | \(u_1,u_2,u_3,u_4,u_5,v\) |
| \(b\) | \(u_1,u_2,u_6,v\) |
| \(c_1\) | \(u_3,u_4\) |
| \(c_2\) | \(u_5,u_6\) |
| \(c_3\) | \(v,w\) |

**Proof.** The parts are disjoint, and each neighbor occurs at most once in any row. Thus no loop or repeated edge is created, and every edge crosses the bipartition. Reading row sizes gives the left degrees

\[
(6,6,6,6,4,2,2,2).
\]

The right degrees can be checked without trusting a program:

| Right vertex | Its complete set of neighbors in \(L\) | Degree |
|---|---|---:|
| Each of \(u_1,u_2\) | \(a_1,a_2,a_3,a_4,b\) | 5 |
| Each of \(u_3,u_4\) | \(a_1,a_2,a_3,a_4,c_1\) | 5 |
| \(u_5\) | \(a_1,a_2,a_3,a_4,c_2\) | 5 |
| \(u_6\) | \(a_1,a_2,a_3,b,c_2\) | 5 |
| \(v\) | \(a_4,b,c_3\) | 3 |
| \(w\) | \(c_3\) | 1 |

Thus the right degrees are \((5,5,5,5,5,5,3,1)\), and the union of the two degree lists is exactly \(d\). There are \(8+8=16\) vertices and

\[
|E|=3\cdot6+6+4+2+2+2=34=68/2
\tag{9}
\]

edges.

The vertices \(a_1,a_2,a_3,u_1,\ldots,u_6\) induce a connected \(K_{3,6}\). Each of \(a_4,b,c_1,c_2\) has a neighbor in this subgraph. The vertex \(v\) is attached through \(a_4\), then \(c_3\) through \(v\), and \(w\) through \(c_3\). All vertices therefore lie in one connected component. This proves the claimed ordinary realization. It is not asserted to be an SI realization; Lemma 3 excludes all such realizations. \(\square\)

### Lemma 5 — the historical review's layer recurrence

This is an expanded derivation of an argument already saved in the structured review, not a newly executed independent check. For a hypothetical SI realization, let \(e_i\) count edges between \(V_i\) and \(V_{i+1}\) for \(1\le i\le5\), and set \(e_0=e_6=0\). Each \(e_i\) must be a nonnegative integer. Since only consecutive layers can be adjacent,

\[
e_{i-1}+e_i=i n_i\qquad(1\le i\le6).
\tag{10}
\]

Starting at the lower boundary forces

\[
\begin{aligned}
e_0&=0,\\
e_1&=1-0=1,\\
e_2&=6-1=5,\\
e_3&=3-5=-2,\\
e_4&=4-(-2)=6,\\
e_5&=30-6=24,\\
e_6&=24-24=0.
\end{aligned}
\tag{11}
\]

Already \(e_3=-2\) is impossible for an edge count. The later entries are merely the continuation of the forced algebra, not edge counts of an existing graph. The complete vector is \((0,1,5,-2,6,24,0)\), exactly as recorded. Satisfying both outer zero boundaries, consistent with global parity balance, cannot cure the negative internal entry. This provides the review's equivalent contradiction. \(\square\)

**Proof of Theorem 1.** Lemma 1 supplies every original premise. Lemma 3 contradicts the asserted SI realization, even without connectedness. A single valid instance violating the conclusion refutes the universal conjecture. Lemma 4 supplies the additional ordinary connected bipartite realization, so the example does not exploit an input that was nongraphical or realizable only by disconnected graphs. Lemma 5 is an optional second account of the obstruction. \(\square\)

## 5. Boundary cases, equality, and original-problem coverage

| Point requiring care | Exact scope of the saved argument |
|---|---|
| Degree endpoints | The example has \(1=m<M=6\); no zero-degree interpretation, isolated vertex, or regular case \(m=M\) is used. All six degree multiplicities are positive. |
| Top-layer equality | The allowed boundary \(n_5=\max\{6,4\}=6\) is attained. No counterexample to a different conjecture requiring a strict top-layer inequality is claimed. |
| Two parity cases | The example lies in the odd-gap case \(M-m=5\). One such example refutes the universal statement; there is no need to refute every parameter slice, and no classification of the even-gap case is claimed. |
| Empty neighboring layers | Here \(n_0=n_7=0\); these are empty classes. The recurrence has \(e_0=e_6=0\), with no edges outside the degree range. |
| Additional inequalities | The leaf bound, strict top incidence capacity, and individual neighbor-count bounds all hold. They do not prevent the class-level deficit \(6>4\). |
| Equality in a capacity inequality | Equality would only remove that particular strict-deficit obstruction. Neither the proof nor this report claims that all such inequalities suffice for SI realizability. |
| Connectivity | The ordinary witness is connected. The non-realizability argument excludes connected and disconnected SI graphs alike. |
| Minimality and other models | No smallest-order counterexample, enumeration of all counterexamples, characterization of SI sequences, or assertion about other graph models is established. |

The saved prose explicitly claims a complete negation of the printed universal conjecture, and the historical reviewer endorsed that mathematical reading. The older structured fields nevertheless remain `scope=UNKNOWN` and `original_problem_coverage=UNKNOWN`; `coverage_explanation` is empty. They are not rewritten as `FULL`. External certification that a formal or natural-language statement exactly matches the original problem is absent. [M1](materials/reviewed-source/dossier.json).

## 6. Recorded outcomes and evidence levels

| Record or question | Preserved outcome | What it does and does not establish |
|---|---|---|
| Candidate | `SELF_CHECKED` | The submitted ordinary proof and finite witness; organization does not raise this level. |
| Historical independent AI review | `NO_ISSUES_FOUND`; `issues=[]` | The reviewer reported no proof gap or circularity and endorsed the full counterexample claim. This is an LLM review, not external expert or formal certification. |
| Legacy coverage fields | Candidate `scope=UNKNOWN`; review `original_problem_coverage=UNKNOWN` | Older records lack an explicit coverage assessment. The prose scope is explained without replacing these fields. |
| Mathematical obligations recorded | Candidate and review `remaining_obligations=[]` | No mathematical obligation is listed; empty legacy arrays do not supply missing external evidence. |
| Novelty | `UNKNOWN` | Priority for this particular refutation is not certified; the local method is already known. |
| Discovery-time problem status | `UNKNOWN`, checked on 2026-10-21 | A public conjecture was identified, but its then-current open status was not certified. It is not a claim that the problem is still open today. |
| Structured evidence fields | `checks=[]`, `citations=[]`, empty structured literature-search arrays; `evidence_assessment.supported=false` | Narrative review evidence exists, but these older fields do not contain a populated structured validation or supported assessment. Their emptiness is preserved. |
| Formal evidence | `formal_target=null`, `formal_check=null`, `formal_receipt=null`; `NOT_FORMALIZED` in the supplement | No Lean source, successful Lean run, kernel receipt, or verified full formal theorem is supplied. |
| External review and alignment | Both absent in the showcase summary | Neither an external expert review nor external statement-equivalence certification has been obtained. |

The candidate's original assumption that independent Verify had not yet occurred describes its submission stage. The later saved review is a separate historical event; the earlier text is not silently revised. Similarly, completion of the Verify workflow is not synonymous with formal verification. [M1](materials/reviewed-source/dossier.json); [S7](materials/showcase/verification.json).

## 7. Finite certificates, computations, and formal-file limits

The solver's Python standard-library checker is present in the original proof appendix. The public [checker, S8](materials/showcase/verify_certificate.py) is that solver material, preserved unchanged, and the [certificate, S3](materials/showcase/certificate.json) describes the same finite graph. It checks positive and consecutive multiplicities, the conjectural arithmetic, the extra robustness conditions, disjoint vertex labels, nonrepeated cross-part edges, the degree multiset, edge count, graph traversal for connectedness, and the parity of each part's degrees. Finally it computes the numerical deficit for the designated degree class.

These computations support the finite data in Lemmas 1 and 4 and the numbers used in Lemma 3. They do not quantify over all graphs or prove Lemma 2. The universal conclusion comes from the written counting argument. The checker itself reports that independent review is not performed by that checker, and it does not set MathLottery review statuses.

The historical independent reviewer reported writing a different checker, independently transcribing the 8-by-8 adjacency matrix, obtaining 34 entries equal to one, the two degree lists in Lemma 4, and reachability of all 16 vertices. The reviewer explicitly said the candidate's program was **not executed**. The saved final answer also reports that the independent checker's pytest and ruff checks passed. Those are historical reported outcomes; the checker, test output, arithmetic output file, and full audit logs are not among the native manifest's two collected files. They cannot be replayed from this bundle alone, and the public solver checker must not be relabeled as the reviewer's checker. [M1](materials/reviewed-source/dossier.json); [M2](materials/reviewed-source/tasks/task-record-003/attempt-record-004/answer.md); [S6](materials/showcase/review.md).

No SAT or exhaustive-search result is needed or supplied as the proof of non-realizability. The frozen record does not establish how the solver discovered the example. There is no Lean development for this case, and the showcase summary says no new Lean build occurred during export. No later formal work is attributed to the earlier ordinary-proof review.

## 8. Literature, known method, and novelty uncertainty

The original conjecture is an author-published claim in the 2026 article, not an assertion newly found or newly confirmed open by this editorial session. The saved problem record labels it Rank 1 for a low-cost initial screen, while leaving resolution difficulty and Lean feasibility unknown. This is a feasibility estimate, not a probability of success or an established difficulty classification. It mentions necessary conditions in Theorems 4.1–4.2 and special sufficient cases in Lemmas 4.1–4.2 of that article; those constructions were not independently audited in discovery and are not dependencies of this proof. [M1](materials/reviewed-source/dossier.json); [B1](https://www.ejgta.org/index.php/ejgta/article/download/1077/pdf_357).

The historical review located the local inequality (7) in the 2022 paper *Bond incident degree indices of stepwise irregular graphs*, p. 8687, equation (2.4). This establishes a recorded precedent for the method. It is not, by itself, a prior refutation of the precise conjecture printed in 2026. The specific tuple and its priority remain `UNKNOWN`. [B2](https://www.aimspress.com/aimspress-data/math/2022/5/PDF/math-07-05-485.pdf); [S6](materials/showcase/review.md).

The narrative records searches involving the title, DOI, authors, conjecture number, counterexample/correction terms, the multiplicities, arXiv, GitHub, and mathematical forums. Through 2026-10-21 they found no direct prior resolution in the material inspected. The 2018 predecessor has a different author list and its Section 4 concerns graph operations; the target degree-sequence conjecture was not found there. The inspected later extremal manuscripts concern degree, size, diameter, or degree-based indices rather than an explicit resolution of this criterion. These are bounded historical search findings, not exhaustive exclusions of the literature. [M1](materials/reviewed-source/dossier.json); [B3](https://arxiv.org/pdf/1809.03297); [B4](https://arxiv.org/pdf/2411.15765v1); [B5](https://users.fmf.uni-lj.si/klavzar/preprints/k-si%20final%20version.pdf).

In particular, the 2026 paper *On k-stepwise irregular graphs*, DOI 10.1016/j.dam.2026.06.027, was represented by metadata and public abstract/fragments. The recorded direct full-text access failed with HTTP 403; the candidate also records inaccessible publisher/SSRN access. The metadata record was created on 2026-07-07 and its print issue was dated November 2026. The full text was not ruled out as a possible source of relevant results. No author confirmation, exhaustive citation audit, or external priority assessment is supplied. Novelty therefore remains `UNKNOWN`; this limitation was not reported as a defect in the counting proof. [B6](https://doi.org/10.1016/j.dam.2026.06.027); [recorded metadata source](https://api.crossref.org/works/10.1016/j.dam.2026.06.027); [M1](materials/reviewed-source/dossier.json).

## 9. Unresolved gaps and limits of reconstruction

The historical review reports no mathematical gap in the submitted counterexample. This report does not introduce a repair. The unresolved limitations concern evidence, provenance, and priority:

- The original Solve linkage, solver chronology, intermediate attempts, and named research notes are absent. One imported candidate and one review task are visible; absence of failed attempts in that record does not show that none occurred.
- The review names an independent checker, a full audit report, provenance records, arithmetic output, and search logs, but these files are not native collected materials. The saved answer and structured review describe them; their descriptions are not the missing files.
- The original-paper and related-paper binaries appear as historical reference artifacts, with some recorded hashes, but are not collected in this bundle. Source URLs and reported checks do not constitute a new examination of those PDFs.
- Some recent full texts were inaccessible. Specific-priority and current literature-status questions remain unresolved. No external expert assessment or statement-equivalence certificate exists.
- No formal source or receipt exists. The general non-realizability proof is ordinary mathematics; finite arithmetic and graph checks have their narrower role.

The manifest's `omitted=[]` means that it lists no omission entry under its collection procedure; it does not mean every historical file was collected. Its limitations explicitly exclude arbitrary workspace files, binaries, caches, and hidden reasoning. The showcase supplement also states that raw logs are not bundled. Its summary that Find, Solve, and Verify were completed does not supply the missing native solver linkage. No replacement conjecture or proposed mathematical repair is asserted here; evaluating any such proposal would require a new Solve/Verify.

## 10. Reproducibility instructions and expected scope

With Python 3.11 or later, after the explicitly supplied showcase files have been attached at the advertised relative locations, a reader can run from the report directory:

```sh
cd materials/showcase
python verify_certificate.py certificate.json
```

The documented expected output has 16 vertices, 34 edges, even- and odd-degree sums of 34 each, multiplicities \((1,3,1,1,6,4)\), an ordinary simple connected bipartite graph flag, and SI incidence demand 6 versus available neighbor degree 4. The independent-review field says that this checker did not perform such a review. These expectations come from the saved source; this report does not claim a new execution.

For byte identity, a reader may also use:

```sh
sha256sum certificate.json verify_certificate.py proof.md verification.json
```

Compare those values with Appendix B. Hash matching identifies bytes, not mathematical correctness, independent review, or statement equivalence. The original proof also contains the full standard-library checker inline, in the candidate `proof` field of [M1](materials/reviewed-source/dossier.json), so the finite algorithm can be inspected even without a standalone supplemental file. No command is offered as a way to reproduce absent independent-review logs or a nonexistent Lean proof. The current organization performed only source reading, editorial byte checks, and report-consistency checks.

## 11. Bibliography and historical source status

All access and scope statements here are inherited from the frozen evidence, with cutoff 2026-10-21; links are citations, not claims of fresh retrieval.

1. **B1.** Somnath Bera, Prithwineel Paul, K. G. Subramanian. *Some properties of stepwise irregular graphs*. EJGTA 14(1) (2026), 215–230. DOI 10.5614/ejgta.2026.14.1.14. Definitions and conventions p. 216; Conjecture 1 p. 223, PDF p. 9. Recorded publication date 2026-04-22. [Publisher PDF](https://www.ejgta.org/index.php/ejgta/article/download/1077/pdf_357).
2. **B2.** Damchaa Adiyanyam, Enkhbayar Azjargal, Lkhagva Buyantogtokh. *Bond incident degree indices of stepwise irregular graphs*. AIMS Mathematics 7(5) (2022); recorded publication date 2022-03-02. Local capacity inequality on p. 8687, equation (2.4). [Publisher PDF](https://www.aimspress.com/aimspress-data/math/2022/5/PDF/math-07-05-485.pdf). The saved review treats it as a known-method source, not a prior resolution of B1.
3. **B3.** Somnath Bera, Prithwineel Paul. *Properties of stepwise irregular graphs*. arXiv:1809.03297v1, 2018-09-10. Related predecessor; the inspected text did not contain the target degree-sequence conjecture. [Preprint](https://arxiv.org/pdf/1809.03297).
4. **B4.** Yaser Alizadeh, Sandi Klavžar, Javaher Langari. *Extremal results on k-stepwise irregular graphs*. arXiv:2411.15765v1, 2024-11-24; recorded journal reference Applied Mathematics and Computation 514 (2026), 129818. [Preprint](https://arxiv.org/pdf/2411.15765v1). The historical inspection found no explicit resolution of the selected criterion.
5. **B5.** Yaser Alizadeh, Sandi Klavžar, Javaher Langari. *On size of k-stepwise irregular graphs and their degree based indices*. [Author-hosted manuscript](https://users.fmf.uni-lj.si/klavzar/preprints/k-si%20final%20version.pdf). Exact publication date was not established; the inspected manuscript concerns size and indices.
6. **B6.** Damchaa Adiyanyam, Enkhbayar Azjargal, Lkhagva Buyantogtokh, Shiikhar Dorjsembe, Batmend Horoldagva. *On k-stepwise irregular graphs*. DOI [10.1016/j.dam.2026.06.027](https://doi.org/10.1016/j.dam.2026.06.027). [Crossref record](https://api.crossref.org/works/10.1016/j.dam.2026.06.027). Only metadata and public fragments were available; full-text access was blocked. The November 2026 issue date is recorded metadata, not proof of an exhaustive review.
7. **B7.** [Publisher article metadata for B1](https://www.ejgta.org/index.php/ejgta/article/view/1077). The saved discovery record uses the journal's 2026-04-22 issue date in preference to an institutional list's generic date.
8. **B8.** [Institutional publications list for 2026](https://iem.edu.in/publications-2026/). Present in the saved discovery status evidence; it is neither an authoritative proof of openness nor a novelty certificate.

## Appendix A. Concise chronology of saved work

Times below are UTC where available. They identify evidence events, not reconstructed hidden reasoning.

| Date or recorded interval | Visible event | Qualification |
|---|---|---|
| 2026-10-21 04:01:26 | Saved problem status check: `UNKNOWN`; initial screening and source-selection rationale | No certified open status and no witness claimed at that discovery stage. |
| 2026-10-21, candidate references around 04:05:09 | Imported solution text contains the tuple, capacity proof, ordinary adjacency construction, and solver checker | Reference retrieval timestamps are not a Solve start or completion time. Original Solve linkage and attempt chronology are unavailable. |
| 2026-10-21 04:10:34–04:17:16 | Historical independent Verify workflow, recorded as `COMPLETED` | One completed review task is visible. The task's own source-observed timestamp is absent. |
| Within that review: 04:11:47 and 04:12:37 | Target/related sources and the 2022 method source have recorded retrieval timestamps | The reviewer reports independent source inspection, matrix transcription, finite checks, and the recurrence contradiction. Raw files and command logs are not collected. |
| At the saved review outcome | `NO_ISSUES_FOUND`, novelty `UNKNOWN`; independent-checker pytest and ruff reported passing | Ordinary AI review only; original coverage field remains `UNKNOWN`; no Lean result. |
| Showcase supplement, evidence date 2026-10-21; export time unspecified | Proof appendix moved to a separate file, relative links and bilingual presentation documentation added | Existing evidence curated; mathematical proof and adjacency table unchanged; no new Lean build and no new review. |
| 2026-10-24 04:21:35 | Native organization snapshot captured | Editorial source boundary, not a new literature cutoff. |
| This organization | Complete English and Chinese reports assembled from the same frozen evidence | No candidate, review, problem, or selection change; no new Solve/Verify. |

No other failed or successful solver attempt is recoverable from the visible chronology. This is a statement about missing records, not evidence that the research had no unsuccessful intermediate work.

## Appendix B. Material index and hash domains

### B.1 Native manifest materials

Only the following two files are native collected entries. Role labels are used in the prose; their relative links preserve the manifest locators.

| Code | Relative material link | Contents and limits | Bytes |
|---|---|---|---:|
| M1 | [Frozen Verify dossier](materials/reviewed-source/dossier.json) | Full saved problem; original candidate claim, assumptions, proof and checker appendix; one structured review and its references; sparse chronology. Contains no independent checker file or raw audit logs. | 33506 |
| M2 | [Saved historical review answer](materials/reviewed-source/tasks/task-record-003/attempt-record-004/answer.md) | Review conclusion and reported checks. It mentions a fuller audit that is not collected; this short answer is not that full report. | 2171 |

Native file SHA-256 values:

```text
M1  ba5203cf7d005c261fc9a12acf7c16293050b135c61019db05769c0e25a814e8
M2  4e2a22ed40f03bd535fff91ae2e025ddce09209b3424813a053d5e43471a9376
```

The historical answer contains original local locators; this exposition does not reproduce them. They do not make their targets part of the frozen bundle.

### B.2 Explicitly supplied showcase supplement

These are **explicit showcase supplements**, not native entries in the organization manifest's `files` array. The supplied export instructions provide their future `materials/showcase/` locations and exact-file hashes. Full text of S2, S4, and S6 was supplied inline; S7's inline rendition omits a redundant hash index. S1 and S5 have metadata/hash entries rather than inline full text. S3's graph data and S8's algorithm are visible in the original proof and supplied appendix diff, but their standalone bytes are not native collected files. The publication step is responsible for attaching the exact frozen supplement files; this editorial session has not recreated missing files from abbreviated text.

| Code | Link | Role | Bytes |
|---|---|---|---:|
| S1 | [Chinese showcase overview](materials/showcase/README.cn.md) | Presentation documentation | 1775 |
| S2 | [English showcase overview](materials/showcase/README.md) | Presentation documentation | 2221 |
| S3 | [Finite certificate](materials/showcase/certificate.json) | Solver's explicit graph data | 892 |
| S4 | [Showcase proof](materials/showcase/proof.md) | Original Chinese mathematical exposition with code appendix moved out | 5624 |
| S5 | [Chinese review summary](materials/showcase/review.cn.md) | Historical review presentation | 1659 |
| S6 | [English review summary](materials/showcase/review.md) | Historical review presentation | 2038 |
| S7 | [Verification summary](materials/showcase/verification.json) | Curated historical outcomes and identities; not a new verification run | 3666 |
| S8 | [Finite certificate checker](materials/showcase/verify_certificate.py) | Solver code; not the independent reviewer's checker | 4538 |

Supplied exact-file SHA-256 values:

```text
S1  9ed43ab441110c8e722db8ebed625b73e2eceb9d42309a3a9b1e1f03922f87b6
S2  db4acc25b699575b7d00e3ecb33c0b1becd22b5a0a5e6937dfb288c9e377ab35
S3  cd64ba28fc8006740fa0c1540aa15eada026b2c137341fc80ec00b162d1f59a0
S4  dafe5ab70e8e70544dc7878fab40de7f88af84b1ee2e31dcc5e1bb84b39e4b8d
S5  5760f27f0d7f50ce4c63b55340da792505fe023f89233085439a830ebc4e51f9
S6  3233e7d39536d56e9c365a7f165a772d96947acf907a5104408244bff4076615
S7  13f4102dc71d2fda9de972d11ea18a428b4df1afda4caa3ee652c0dfa0b1660e
S8  c8317682a5b9828b957c1ab46cf078d447ce3f2d34265f8eb79e7bc8288a8534
```

In particular, the abbreviated inline S7 text is not the 3666-byte exact file and must not be expected to have its hash. The displayed S4 hash is a presentation-file hash; it differs from the original proof-text hash below because the code appendix was moved out and links were added, not because a mathematical repair was supplied.

### B.3 Historical evidence identities, kept in their own domains

| Code and object/domain | Qualification |
|---|---|
| H1 — Candidate content identity | Candidate identity recorded in the manifest and supplement; not a hash of the showcase proof file. |
| H2 — Original proof text | UTF-8 candidate `proof` field, including its original inline checker. |
| H3 — Full historical review report | Supplied historical identity only; the full file is not collected and is not M2. |
| H4 — Original article PDF | Matching download identity reported by the candidate and reviewer; PDF bytes are not collected here. |
| H5 — 2022 known-method PDF | Historical reviewer reference; PDF bytes are not collected here. |
| H6 — Frozen Problem.statement text | SHA-256 of the UTF-8 statement text. No formal receipt is implied. |
| H7 — Frozen full Problem record fingerprint | Manifest identity over the canonical full Problem record, including metadata and legacy normalization. |

Recorded SHA-256 values:

```text
H1  877630f102a9d01b633af85df6a45d1fea337d0c47477e89d8f331a6c574075e
H2  0010699c220ed13c8301bd0fa2f8656493b214abbad599e0a73254bd7f8c3536
H3  95419e9f737c7e45d6c4b3b0752ce2fe71fd6b9a271eff226161dd0ee68be6d2
H4  2a2475b57fd15d103e558a3ef88854a3b646987ee7007ecafb46b2ef9f1ecfbd
H5  65535b948ca828835fbd22bba82b5c6707f8688e358ef6dae07180c0905eabd2
H6  a243d69e034967dbd2fd848d6c6d87a705a90c3f1c2faf5eaf5c6ff0deb75103
H7  21c10fc11e5d48c5f529a426227577834477047a906e3d563346d521c198775e
```

The last two hashes have different inputs and are not expected to coincide. Each must be compared only within its own domain. None of these hashes certifies theorem truth, originality, or equivalence of natural-language and formal statements.

## Appendix C. Bilingual consistency record

The Chinese and English reports use the same Conjecture 1, Theorem 1, Lemmas 1–5, equations (1)–(11), degree table, adjacency lists, endpoint conventions, dependency structure, bibliography, relative material links, and hash identities. Both preserve the full ordinary construction, the universal \(6>4\) contradiction, the recorded \(30>28\) check and negative layer count, `SELF_CHECKED`, `NO_ISSUES_FOUND`, all `UNKNOWN` fields, absent formal/external evidence, missing solver linkage, inaccessible literature, and the distinction between native and showcase materials. Their consistency check is editorial; it confers no new mathematical or evidential certification.
