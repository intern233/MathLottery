> **Publication copy.** Local identifiers are replaced by stable aliases; personal data is screened. The frozen evidence inventory is [source-manifest.json](source-manifest.json); the actual public files and transformations are in [manifest.json](manifest.json). Downloaded article full texts are [omitted](materials/omitted-sources.md). Historical verification statements below are unchanged in scope; this export adds no proof review or novelty certification.

[mathlottery-expert-brief-v2]: #

# MathLottery expert reading report

> Frozen evidence only: this does not upgrade proof status or novelty, and adds no verification.

## Expert quick review

This is a navigation summary, not a complete proof. Ellipses mark display excerpts; frozen materials and the listed JSON paths contain full text, history and evidence. Source text is not translated; later success does not erase historical failures.

Source task: reviewed-source · Frozen revision: 9 · 2026-10-25T12:36:24.743503+00:00

Snapshot SHA-256: `df5a6ff472287d257aeb2d20f29b0e46aecbad19206a7c9a78d1d2c58bca4d78`

Problem SHA-256: `9b3d92fc177c85627a748a19f196d19acfcc809a7c617d4a53e2d82cd7e5e3b6`

[Evidence manifest](source-manifest.json) · [Frozen dossier (all records)][frozen-dossier]

[Read the full report](#full-editorial-report) · [Evidence index](#evidence-index)

### 1. Original problem and candidate claims

**三次 Franel 多项式从 F\_8 起的逐系数对数凸性**

对整数 n&gt;=0 定义 F\_n(q)=sum\_{k=0}^n binom(n,k)^3 q^k ∈ Z&#91;q&#93;。原问题要求尾序列 (F\_n(q))\_{n&gt;=8} 是 q-log-convex；展开即：对所有整数 n&gt;=9、d&gt;=0，&#91;q^d&#93;(F\_{n-1}(q)F\_{n+1}(q)-F\_n(q)^2)&gt;=0。中心下标是 n&gt;=9，不是 n&gt;=8；q为形式变量。

[/problem/statement][frozen-dossier]

Open status: `UNKNOWN` · Checked: 2026-10-23T05:28:55.885172+00:00

[Original source](https://arxiv.org/html/2505.02767v4)

**candidate-record-002** · `SELF_CHECKED` · scope `COMPLETE`

SHA-256: `693a09a4ede1e970f3060e6491480231492b2b0e62ea7e8d8d3a49e3341c88be` · With review snapshot: `2f22f64a69440461e3e0fc45f96eeed38ebcee5616ed2b4c872d6a066711f91a`

令 F\_n(q)=sum\_{k=0}^n binom(n,k)^3 q^k。对所有整数 n&gt;=9、d&gt;=0，有 &#91;q^d&#93;(F\_{n-1}(q)F\_{n+1}(q)-F\_n(q)^2)&gt;=0；更强地，当 1&lt;=d&lt;=2n-1 时该系数严格为正，在 d=0、d=2n 或 d&gt;2n 时为零。因此原题从 F\_8 开始的尾序列逐系数 q-log-convex。

[/candidates/0][frozen-dossier]

Assumptions: n、d 为整数，n&gt;=9、d&gt;=0；q 为形式变量。; F\_n(q)=sum\_{k=0}^n binom(n,k)^3 q^k；二项式系数越界取零。; 没有附加猜想、渐近假设或依赖有限 n 实验外推的条件。

**Latest status**: `NO_ISSUES_FOUND` · Coverage=`FULL` · Lean=`UNASSESSED` · Novelty=`UNKNOWN`

### 2. Verification, key steps and historical failures

**candidate-record-002**

| Review | Verdict | Coverage | Novelty |
| --- | --- | --- | --- |
| 1 | `NO_ISSUES_FOUND` | `FULL` | `UNKNOWN` |

1 historical issues or unresolved checks are retained in the evidence index; later success has not removed them.

Latest proof assessment: 所提交文字证明是自包含的完整代数证明。已独立推导换下标消去、卷积归一化、正性与范围衔接，并直接从提交正文提取四张大次数表和十五张低次数表，以两种精确多项式实现核对全部恒等式；没有读取求解历史，也没有依赖候选自报的检查程序。全部数学关键步骤通过，奇数d的半整数参数和d=n的边界均包含。所附Lean仅定义猜想和做有限求值；本地重编译因缺Mathlib失败，故没有 …

Statement coverage: 原题精确要求F\_n(q)=Σ C(n,k)^3q^k的尾序列n≥8为q-log-convex，等价于中心n≥9、每个整数d≥0的c\_{n,d}≥0。候选使用完全相同的对象和量词，并证明更强的内部严格正性及全部零系数位置。独立审查确认回文约化后的1≤d≤n被d≤15和d≥16两段完全覆盖；不存在仅处理固定d、有限n或q= …

Novelty explanation: 原非负性主命题已由Sun在2024年公开提出，并在2026-02-10的论文v4中明确列为猜想；这些出处不构成已知证明。此次20项实际检索及原始文献比较未发现覆盖该完整立方尾序列结论的已证定理。最接近的平方Narayana、加权超几何多项式、q=1数值Franel以及rising …

Coverage policy: `UNASSESSED` · proof_complete=False · statement_aligned=False

Key-step coverage is unassessed; a verdict label does not imply completeness.

No structured proof roadmap recorded; reconstruct it from the full dossier.

[/candidates/0/reviews/0][frozen-dossier]

No independent Lean execution receipt recorded.

Formal checks cover receipt declarations only; natural-language/formal-statement equivalence has no external certification.

### 3. Literature obstacles and novelty

Grouped by stable ID, kind and source; different sources stay separate. Historical states remain visible, without implying every old issue is still unresolved. Links identify frozen JSON paths.

Evidence policy: evidence-v2

No listed obstacle establishes exhaustive search or novelty.

The evidence index retains all 0 obstacle entries, 0 prior-result comparisons and 13 other gaps/scope limits; sources and comparisons for unresolved entries still need individual review.

### 4. Expert priorities and evidence navigation

1. Read the full proof and check key lemmas, quantifiers and boundaries; excerpts do not replace stepwise review.
2. Address unresolved obstacles individually and compare the closest prior theorems.
3. LLM approval and finite tests do not prove a general theorem.

## Evidence index

The index locates original records without repeating full proofs or quotations; the frozen dossier contains complete text. [Skip to the full report](#full-editorial-report).

### Historical issues and failed checks

**candidate-record-002**

- check-15 · UNRESOLVED · blocking=False · review 1: 本地重新编译所附 Lean 源码。 — 实际使用Lean 4.35.0尝试编译所附原始字节，报unknown module prefix 'Mathlib'，本地模块搜索路径缺依赖。因此不能声称重新编译成功，也没有形式检查回执。源码本来就没有待审定理的证明，故不请求把其Prop定义当作theorem … · [/candidates/0/reviews/0/checks/14][frozen-dossier]

### Literature obstacle history (all IDs)

**Other search gaps and scope limits (deduplicated, all retained)**

| Excerpt | Full record |
| --- | --- |
| 独立检查未能取得MathOverflow网页（robots获取失败）。官方API虽向研究端返回200及完整原始评论/反例正文，但其robots端点返回HTTP400 no\_method；按当前WebTools.download策略亦无法取得。评论1247286 … | [/problem/evidence\_assessment/reasons/2][frozen-dossier] |
| https://api.stackexchange.com/2.3/comments/1247286?site=mathoverflow&amp;filter=withbody: Unable to verify robots policy for https://a … | [/problem/evidence\_assessment/reasons/0][frozen-dossier] |
| https://api.stackexchange.com/2.3/questions/479301/answers?site=mathoverflow&amp;filter=withbody: Unable to verify robots policy for h … | [/problem/evidence\_assessment/reasons/1][frozen-dossier] |
| 实际检索词沿用同一Find会话；主要英文索引、arXiv、作者公开问题页和所列原始论文，未穷尽所有语言、数据库或未索引工作。 | [/problem/evidence\_assessment/limitations/0][frozen-dossier] |
| 最新作者论文猜想表述为2026-02-10。没有更晚针对Franel尾序列的专门状态重申；检索截至2026-10-23不使旧声明自动更新。 | [/problem/evidence\_assessment/limitations/1][frozen-dossier] |
| 作者旧个人主页不可取得完整书目，限制作者后续作品覆盖；未识别到某篇具体未读的Franel尾序列解答。 | [/problem/evidence\_assessment/limitations/2][frozen-dossier] |
| Franel名称可能指不同多项式。已经具体比较的二次Narayana、完整立方序列及rising-binomial族均不等价；不声称穷尽所有变量变换或未知等价表述。 | [/problem/evidence\_assessment/limitations/3][frozen-dossier] |
| https://mathoverflow.net/questions/479301/on-the-polynomials-sum-k-0n-binomnkkm-qk: Unable to verify robots policy for https://mat … | [/candidates/0/reviews/0/evidence\_assessment/reasons/2][frozen-dossier] |
| https://emis.de/ft/31765: Unable to verify robots policy for https://emis.de | [/candidates/0/reviews/0/evidence\_assessment/reasons/1][frozen-dossier] |
| 20个实际查询主要覆盖英文网页索引、少量中文关键词、arXiv、原作者公开问题页及所列论文；未穷尽所有语言、数据库、引用网络或未索引成果。 | [/candidates/0/reviews/0/evidence\_assessment/limitations/0][frozen-dossier] |
| 明确将Franel尾序列列为猜想的最新所读原作者论文版本为2026-02-10；没有取得更晚的专门开放状态重申，不能自动把该历史状态更新为当前全球状态。 | [/candidates/0/reviews/0/evidence\_assessment/limitations/1][frozen-dossier] |
| POTENTIALLY\_NEW不是首证或优先权认证。没有检索命中不证明新颖性；未知等价表述、未公开成果或未索引证明仍可能存在。 | [/candidates/0/reviews/0/evidence\_assessment/limitations/2][frozen-dossier] |
| 此次审查没有外部专家评价，也没有一般定理的Lean证明。附带源码的本地编译依赖缺失属于形式化工具限制，已单列非阻塞FORMAL检查，未伪装成文献结论或形式回执。 | [/candidates/0/reviews/0/evidence\_assessment/limitations/3][frozen-dossier] |

### Material navigation and scope limits

**Proof and reviews** (4): [dossier.json](materials/reviewed-source/dossier.json) · [answer.md](materials/reviewed-source/tasks/task-record-002/attempt-record-002/answer.md) · [dossier.json](materials/solver-source/dossier.json)

**Formal** (0): —

**Literature** (7): [420c3f8ccfa26cb393d1f401c628667d042902b02bae0c10648a5cfe65eed0cf.json](materials/reviewed-source/literature/receipts/420c3f8ccfa26cb393d1f401c628667d042902b02bae0c10648a5cfe65eed0cf.json) · [6cf136a4f1583b1200993b61ec664cb96012453cdc3ac08e14792f56e15a08ff.json](materials/reviewed-source/literature/receipts/6cf136a4f1583b1200993b61ec664cb96012453cdc3ac08e14792f56e15a08ff.json) · [86e133a57f3135e3a9f0152f1439a721a5ceec4a1e29b8f1fcefcba104b6c8f7.json](materials/reviewed-source/literature/receipts/86e133a57f3135e3a9f0152f1439a721a5ceec4a1e29b8f1fcefcba104b6c8f7.json)

The manifest lists every captured path, hash and omitted item.

- This is an editorial reconstruction of visible saved evidence, not hidden reasoning, an independent mathematical verification, or a certification of novelty.

- reviewed-source: only saved answers, named notes, proof/formal files and source receipts are included; arbitrary workspace files, binaries and caches are excluded.

- solver-source: only saved answers, named notes, proof/formal files and source receipts are included; arbitrary workspace files, binaries and caches are excluded.

- The linked solver is frozen at the revision shown in this manifest, which may include work saved after the review. The original reviewed candidate is matched exactly; later work is not retroactively verified.

Omitted material: 2 entries; see omitted in the manifest.

[frozen-dossier]: materials/reviewed-source/dossier.json

[mathlottery-expert-brief-v2-end]: #

---

## Full editorial report

# Coefficientwise log-convexity of the cubic Franel tail: an expert report on the frozen proof and review evidence

## Expert entry and abstract

**Exact original problem.** For integers \(n\ge0\), let \(F_n(q)=\sum_{k=0}^n\binom nk^3q^k\in\mathbb Z[q]\), with \(q\) a formal variable. The tail \((F_n)_{n\ge8}\) is required to be coefficientwise log-convex: every pair of integers \(n\ge9,d\ge0\) must satisfy \(c_{n,d}=[q^d](F_{n-1}F_{n+1}-F_n^2)\ge0\). The central index starts at **9**, not 8. The report concerns the first clause of Sun's Conjecture 1.1(i), not its other polynomial families.[L1] [M5]

**Saved proof claim and evidence level.** The complete written candidate additionally claims strict positivity for \(1\le d\le2n-1\), and zero for \(d=0,2n\) and \(d>2n\). The saved LLM review says `NO_ISSUES_FOUND`, assesses original-problem coverage as `FULL`, and leaves the candidate at `SELF_CHECKED`. Thus a complete candidate and a supporting review record exist; there is no external expert certification, Lean proof of the candidate's universal theorem, or successful kernel receipt. The historical problem fields `status=UNKNOWN`, `scope_relation=UNKNOWN`, and the final `novelty=UNKNOWN` are preserved. Mathematical correctness, original-problem coverage, and novelty are separate assessments.[M1]

**Prior results and the weakest audit link.** The saved comparisons concern squared binomial weights, numerical Franel sequences at \(q=1\), and a different rising-binomial family; none is recorded as an established result covering this candidate. The parts most in need of expert audit are the large-degree table identity (4) and the fifteen small-degree identities (6). Their complete data survive, but the original checking code and logs are absent from the frozen bundle. The review reports full coefficient comparisons; that report must not be presented as execution in this editorial session or as a Lean check. Independent source-retrieval receipts also leave unresolved literature gaps.[M1] [M10] [M11]

**Where to inspect the decisive evidence.** Consult `candidates[0].proof` in [M1], whose complete coefficient tables are reproduced in Appendices A and B, and `reviews[0].checks[6]` and `checks[8]`. The formal limitation is in `checks[14]`; novelty limitations are in `evidence_assessment` and [M10], [M11]. The exposition below expands the submitted finite-sum argument into numbered lemmas, retaining original equations (1)–(7). It is an editorial reconstruction of visible evidence. It performs no new Solve, Verify, search, or compilation, and invents no missing steps, repairs, or hidden research history.

## 1. Frozen provenance, status, and reading conventions

The manifest was captured at 2026-10-25 12:36:24 UTC and lists 11 files. It explicitly links the selected reviewed result to one Solve dossier. The two dossiers agree on the candidate's claim, proof, assumptions, references, scope, and remaining obligations; both record candidate SHA-256 `693a09a4ede1e970f3060e6491480231492b2b0e62ea7e8d8d3a49e3341c88be`. The selected candidate's separate snapshot hash is `2f22f64a69440461e3e0fc45f96eeed38ebcee5616ed2b4c872d6a066711f91a`. Only that explicit lineage is used; no other session is inferred from a matching name or hash.[M1] [M2]

| Saved field | Value and interpretation |
|---|---|
| Problem `status`, `scope_relation` | Both `UNKNOWN`; `source_statement` and `scope_description` are empty, and `formal_target=null`. Historical certification cannot be supplied retrospectively. |
| Solve candidate | `scope=COMPLETE`, `level=CANDIDATE`, `remaining_obligations=[]`, with no reviews. |
| Reviewed candidate | `scope=COMPLETE`, `level=SELF_CHECKED`. |
| Review conclusion | `verdict=reported_verdict=NO_ISSUES_FOUND`; `issues=[]`; `original_problem_coverage=FULL`; `remaining_obligations=[]`. These are saved LLM assessments. |
| Novelty | `novelty=UNKNOWN`, while `reported_novelty=POTENTIALLY_NEW`; the favorable prose did not change the final field. |
| Structured proof coverage | `proof_steps=[]`, `statement_alignment=[]`; `proof_coverage` has no assessment time or policy version, has 0 total steps, and records `proof_complete=false`, `statement_aligned=false`, `formal_alignment_certified=false`. This records the absence of structured certification, not a mathematical counterexample. |
| Formal and external evidence | `formal_check=null`, `formal_receipt=null`; no external expert-review evidence is supplied. |

The problem's historical scope relation `UNKNOWN` and the review's written coverage assessment `FULL` belong to different fields and must coexist. The former cannot be converted into certification, and the latter must not be suppressed. The theorem and lemma labels below organize the submitted argument; they do not constitute new verification.

All 16 original check `id` fields are **empty strings**. **R01–R16 are editorial locators**, corresponding in order to `candidates[0].reviews[0].checks[0]` through `checks[15]` in [M1]. They are not invented historical check IDs.

## 2. Original statement, notation, and strategy

Sun's version dated 2026-02-10 states this tail-sequence conjecture in the first clause of Conjecture 1.1(i), preceded by the definition of coefficientwise log-convexity. The saved provenance also attributes the earliest actually read public question to Sun's MathOverflow comment 1247286, dated 2024-09-21 06:18:37 UTC, but controller retrieval of that page still failed. The immediately preceding phrase “remains open” in Sun's paper concerns a different sequence \(\beta_n\); it must not be reused as a newer status statement for the Franel problem.[L1] [L2] [M5] [M10]

**Theorem 1 (submitted claim supported by the LLM review; level remains SELF_CHECKED).** Define

\[
F_n(q)=\sum_{k=0}^{n}\binom nk^3q^k,
\qquad \Delta_n(q)=F_{n-1}(q)F_{n+1}(q)-F_n(q)^2,
\qquad c_{n,d}=[q^d]\Delta_n(q).
\]

The candidate claims that, for all integers \(n\ge9,d\ge0\),

\[
c_{n,d}
\begin{cases}
>0,&1\le d\le2n-1,\\
=0,&d=0,\ d=2n,\ \text{or }d>2n.
\end{cases}
\]

The convention is \(\binom ak=0\) for \(k<0\) or \(k>a\), with nonnegative integer upper index \(a\); an empty product equals 1. All sums are finite, so convergence is irrelevant. The parameters \(h,x_k\) may be half-integers; this neither changes the integrality of \(n,d,k\) nor replaces the formal variable \(q\) by a numerical value.

The dependency chain is as follows. Lemma 1 reduces the problem to \(1\le d\le n\). Lemmas 2–6 treat \(n\ge d\ge16\). Lemma 7 treats \(1\le d\le15\) and \(n\ge\max(9,d)\). Lemma 8 assembles all quantifiers. In the large-degree range, two identities with zero weighted sum transform a convolution whose sign is not immediate into an explicit positive sum. In the small-degree range, a finite list of **polynomial identities** covers unbounded \(n\). Neither literature comparisons nor finite experiments are premises of this mathematical chain.

## 3. Faithful expansion of the proof

The following argument comes from the candidate text and the saved explanations in R01–R12. Intermediate reindexing and normalization equations are expanded editorially for readability. No certificate is replaced, and no new lemma is supplied to repair the submission. Execution outcomes for the large tables are reported only as historical records.

### Lemma 1: convolution, palindromicity, and all boundaries (R01–R03)

Put \(P_j=F_{j+8}\). The definition for the tail requires coefficientwise nonnegativity of \(P_{j-1}P_{j+1}-P_j^2\) for every \(j\ge1\), so its central index is exactly \(n=j+8\ge9\). Polynomial multiplication gives

\[
c_{n,d}=\sum_{k=0}^{d}
\left(\binom{n-1}{k}^{3}\binom{n+1}{d-k}^{3}
-\binom nk^{3}\binom n{d-k}^{3}\right).
\]

The zero convention includes the endpoints. Binomial symmetry also gives

\[
q^nF_n(q^{-1})=F_n(q),\qquad
c_{n,d}=c_{n,2n-d}\quad(0\le d\le2n).
\]

Here \(q^{-1}\) merely expresses palindromicity in Laurent polynomials. Both products have palindromic length \(2n\); this does not assert that their difference has a nonzero coefficient of \(q^{2n}\). Their constant and leading coefficients are all 1, so \(c_{n,0}=c_{n,2n}=0\). Their degree bound gives zero for \(d>2n\). Only strict positivity for \(1\le d\le n\) remains.

### Lemma 2: parameters and positive weights for large degrees (R04)

For \(n\ge d\ge16\), set

\[
N=n+1,\quad h=d/2,\quad z=N-d,\quad m=h+z=N-h,
\quad H=h-8,\quad Z=z-1,
\]

\[
x_k=k-h,\qquad W_k=\binom Nk^3\binom N{d-k}^3
\quad(0\le k\le d).
\]

Then \(N=2h+z=h+m\), \(h\ge8\), \(z\ge1\), and \(H,Z\ge0\). Since \(d\le N-1\), every such \(W_k\) is strictly positive, so adjacent-weight ratios do not divide by zero. The boundary \(d=n\) gives the allowed values \(z=1,Z=0\). Odd \(d\) merely makes \(h,x_k\) half-integral.

### Lemma 3: two finite-sum identities without boundary remainders (R05)

Define polynomials in an independent variable \(x\) by

\[
\begin{aligned}
A(x)&=(m-x)^3(h-x)^3,\\
B(x)&=(m+x)^3(h+x)^3,\\
S_0(x)&=A(x)(2x+1)-B(x)(2x-1),\\
S_1(x)&=A(x)(2x+1)^3-B(x)(2x-1)^3.
\end{aligned}
\]

At the summation points, \(A(x_k)=(N-k)^3(d-k)^3\) and \(B(x_k)=(N-d+k)^3k^3\), while

\[
\frac{W_{k+1}}{W_k}
=\left(\frac{(N-k)(d-k)}{(k+1)(N-d+k+1)}\right)^3,
\qquad W_kA(x_k)=W_{k+1}B(x_{k+1})\quad(0\le k<d).
\]

The endpoint factors satisfy \(A(x_d)=B(x_0)=0\). For \(r=1,3\), the reindexing is

\[
\begin{aligned}
\sum_{k=0}^d W_k B(x_k)(2x_k-1)^r
&=\sum_{k=1}^d W_k B(x_k)(2x_k-1)^r\\
&=\sum_{j=0}^{d-1}W_j A(x_j)(2x_j+1)^r\\
&=\sum_{j=0}^{d}W_j A(x_j)(2x_j+1)^r.
\end{aligned}
\]

The middle equality uses \(2x_{j+1}-1=2x_j+1\); the first and last use the zero endpoints. Hence

\[
\sum_{k=0}^{d}W_kS_0(x_k)=
\sum_{k=0}^{d}W_kS_1(x_k)=0.\tag{1}
\]

This follows solely from adjacent binomial relations, without assuming the positivity being proved.

### Lemma 4: exact normalization of the convolution (R06)

Set

\[
\begin{aligned}
P(x)={}&N^3\big((m-x)^3(m-x-1)^3
                    +(m+x)^3(m+x-1)^3\big)\\
&-2(N-1)^3(m^2-x^2)^3,\\
\ell={}&[N(m-1)]^2+N(m-1)(N-1)m+[(N-1)m]^2.
\end{aligned}
\]

The identities

\[
\binom{N-2}{k}=\binom Nk\frac{(N-k)(N-k-1)}{N(N-1)},
\qquad
\binom{N-1}{k}=\binom Nk\frac{N-k}{N}
\]

rewrite the two products in the convolution as

\[
\binom{N-2}{k}^{3}\binom N{d-k}^{3}
=\frac{W_k(m-x_k)^3(m-x_k-1)^3}{N^3n^3},
\]

\[
\binom{N-1}{k}^{3}\binom{N-1}{d-k}^{3}
=\frac{W_k(m^2-x_k^2)^3}{N^6}.
\]

Using \(W_{d-k}=W_k\) and \(x_{d-k}=-x_k\), average the first expression with its reindexed copy, then take a common denominator. This gives

\[
c_{n,d}=\frac{1}{2n^3N^6}\sum_{k=0}^{d}W_kP(x_k).\tag{2}
\]

At \(n=d,k=d\), the factor \(m-x_k-1=0\) exactly represents \(\binom{n-1}{d}=0\); this boundary is retained. Both denominator factors \(n,N\) are strictly positive.

### Lemma 5: the large-degree algebraic certificate (R07)

Let \(U,V,C,D\in\mathbb Z[H,Z]\) be defined completely by the four tables in Appendix A. Every listed coefficient and every constant term is strictly positive, so

\[
U>0,\qquad V>0,\qquad C>0,\qquad D>0
\quad(H,Z\ge0).\tag{3}
\]

The central identity of the submitted certificate is

\[
\begin{aligned}
4h^2UP(x)+4\ell U S_0(x)-NV\big(S_1(x)-S_0(x)\big)
=24N\big(hm^3Cx^2+Dx^6+(2N-1)Vx^8\big).
\end{aligned}\tag{4}
\]

After substituting \(N=2h+z,m=h+z,H=h-8,Z=z-1\), this is a polynomial identity, equivalent to agreement of every monomial coefficient, not a fit at finitely many parameter values. R07 reports that the reviewer extracted the tables from the candidate text and expanded the identity using both standard-library sparse rational polynomial arithmetic and SymPy 1.14.0 over \(\mathbb Z[H,Z,x]\). Every difference coefficient was zero; after simplification each side contained 210 nonzero monomials. The original programs and output are not frozen, and this report does not rerun that calculation.

R07 also records the cancellation structure. With \(T=hm\),

\[
A(x)=(T+x^2-Nx)^3,\qquad B(x)=(T+x^2+Nx)^3,
\]

\[
U=-\frac{[x^4](S_1-S_0)}8
=N^3+3(2N-3)T^2-3N(3N-2)T,
\qquad h^2[x^4]P+\ell[x^4]S_0=-2NV.
\]

Consequently the coefficient of \(x^4\) on the left of (4) cancels; symmetry removes the odd powers. R07 also records cancellation of the constant term, agreement of the \(x^8\) term, and expanded checks of the remaining \(x^2,x^6\) identities. This explains why only even powers suitable for a sign argument survive, but does not replace an audit of the complete certificate.

### Lemma 6: an explicit positive sum for large degrees (R08)

Multiply (4) by \(W_k\), substitute \(x=x_k\), and sum. Equation (1) removes both correction terms, yielding

\[
4h^2U\sum_{k=0}^dW_kP(x_k)
=24N\sum_{k=0}^dW_k\big(hm^3Cx_k^2+Dx_k^6+(2N-1)Vx_k^8\big).
\]

Substitution into (2) gives the candidate's positive-sum formula

\[
\boxed{
c_{n,d}=\frac{3}{n^3N^5h^2U}
\sum_{k=0}^dW_k\big(hm^3Cx_k^2+Dx_k^6+(2N-1)Vx_k^8\big).
}\tag{5}
\]

The prefactor is \(24N/(4h^2U\cdot2n^3N^6)\), with no extra factor of 2 or \(N\). Every scalar coefficient is positive and every even power is nonnegative. For \(k=0\), \(x_0=-h\ne0\) and \(W_0=\binom Nd^3>0\). Retaining only its quadratic contribution gives the lower bound recorded in R08:

\[
c_{n,d}\ge\frac{3\binom Nd^3 h m^3C}{n^3N^5U}>0.
\]

This covers every \(n\ge d\ge16\), including \(H=0\), \(Z=0\), and odd \(d\). An even \(d\) can give one term with \(x_k=0\), but that does not remove the strictly positive term just exhibited.

### Lemma 7: fifteen small-degree identities and their positivity (R09–R10)

For \(1\le d\le15\), put \(s_d=\max(9,d)\) and define

\[
\begin{aligned}
B_{2r+1}(n)&=n\prod_{j=1}^r(n-j)^3\quad(r\ge0),\\
B_{2r}(n)&=n(n-r)\prod_{j=1}^{r-1}(n-j)^3\quad(r\ge1).
\end{aligned}
\]

Appendix B supplies \(a_d>0\) and polynomials \(R_d\) with positive integer coefficients such that

\[
c_{n,d}=a_dB_d(n)R_d(n-s_d),\qquad 1\le d\le15.\tag{6}
\]

To see why this is an argument for unbounded \(n\), write \((t)_{\underline k}=\prod_{j=0}^{k-1}(t-j)\). Replace each binomial in Lemma 1 by its falling-factorial formula and use \(d!/(k!(d-k)!)=\binom dk\). Then

\[
\begin{aligned}
(d!)^3c_{s_d+y,d}=\sum_{k=0}^d\binom dk^3
\big[&((s_d+y-1)_{\underline k}
       (s_d+y+1)_{\underline{d-k}})^3\\
&-((s_d+y)_{\underline k}
       (s_d+y)_{\underline{d-k}})^3\big].
\end{aligned}\tag{7}
\]

It therefore suffices to multiply the right side of (6) by \((d!)^3\) and compare every coefficient in \(y\) with (7). R09 records zero residuals for all fifteen tables under two exact implementations, with left-side degrees \(3d-2=1,4,\ldots,43\). This is not a check of fifteen values of \(n\): the list of \(d\) is finite, but \(y\) is unbounded in each identity. The missing original output has the same evidential limitation as in Lemma 5.

For the required integers \(n\ge s_d\), one has \(y\ge0\), every \(R_d(y)>0\), and every factor of \(B_d(n)\) is positive. Thus (6) is strictly positive. For \(d=1\), the empty product gives \(B_1=n,R_1=1,a_1=6\), so \(c_{n,1}=6n\). At \(n=d\), an out-of-range falling factorial in (7) contains a zero factor, remaining consistent with the convolution.

### Lemma 8: assembly of the quantifiers and Theorem 1 (R11)

For any \(n\ge9\) and internal degree \(1\le d\le2n-1\), set

\[
e=\min(d,2n-d),\qquad 1\le e\le n.
\]

If \(e\le15\), then \(n\ge\max(9,e)\), so Lemma 7 applies. If \(e\ge16\), apply Lemma 6. Lemma 1 then gives \(c_{n,d}=c_{n,e}>0\). All remaining degrees were handled in Lemma 1. In particular, the whole reduced range for \(n=9\) is covered by the small-degree tables; there is no gap between \(d=15\) and \(d=16\); and \(d=n\) is not excluded. This completes the submitted argument for its full conclusion, rather than a fixed-degree, finite-\(n\), even-degree-only, or \(q=1\) branch.

**Proposition 2: the starting-index threshold (R12; written-derivation level).** For integers \(n\ge2\),

\[
\begin{aligned}
c_{n,2}
&=\binom{n-1}{2}^3+\binom{n+1}{2}^3
+(n-1)^3(n+1)^3-2\binom n2^3-n^6\\
&=\frac34n(n-1)(n^2-9n+6).
\end{aligned}\tag{8}
\]

Substitution gives \(c_{8,2}=-84\) and \(c_{9,2}=324\). The tail starting at \(F_7\) contains the failing center \(n=8\), so Theorem 1 cannot be extended to central index 8. Together with Theorem 1, this explains sharpness of the starting index among these integer-indexed tails; no separate Lean optimality theorem exists. Internal strictness, equality locations, and this threshold are supported only by the written argument and the recorded algebraic/experimental review. The frozen candidate proves no extension to other powers, other polynomial families, or strong \(q\)-log-convexity.

## 4. Claims mapped to the recorded checks

Every `SUPPORTED` or `UNRESOLVED` below is a historical outcome, not a new check. R01–R11 were recorded as essential; R12–R16 have `blocking=false`. All original check IDs are empty.[M1]

| Editorial locator | Subject and method | Saved result and location here |
|---|---|---|
| R01 | Tail reindexing, objects, quantifiers; DERIVATION | SUPPORTED; Lemma 1 and Theorem 1. |
| R02 | Finite coefficient convolution; DERIVATION | SUPPORTED; Lemma 1. |
| R03 | Palindromicity, zero endpoints, outside support; DERIVATION | SUPPORTED; Lemma 1. |
| R04 | Parameter domain, weights, half-integers; DERIVATION | SUPPORTED; Lemma 2. |
| R05 | Finite-sum reindexing; DERIVATION | SUPPORTED; Lemma 3, equation (1). |
| R06 | Symmetric averaging and normalization; DERIVATION | SUPPORTED; Lemma 4, equation (2). |
| R07 | Full polynomial comparison with two implementations; DERIVATION | SUPPORTED; Lemma 5, equation (4), Appendix A; code and logs not frozen. |
| R08 | Positive sum and a strictly positive term; DERIVATION | SUPPORTED; Lemma 6, equation (5). |
| R09 | Fifteen full polynomial comparisons; DERIVATION | SUPPORTED; Lemma 7, equations (6)–(7), Appendix B; code and logs not frozen. |
| R10 | Positivity of the small-degree factors; DERIVATION | SUPPORTED; Lemma 7. |
| R11 | Assembly of ranges and all quantifiers; DERIVATION | SUPPORTED; Lemma 8. |
| R12 | Quadratic coefficient and starting-index counterexample; DERIVATION | SUPPORTED; Proposition 2. |
| R13 | Exact integer convolution and five connection experiments; FINITE_TEST | SUPPORTED; auxiliary tests only, not a universal proof. |
| R14 | Scope of the attached Lean source; DERIVATION | SUPPORTED; definitions and evaluations only, no universal theorem proof. |
| R15 | Local recompilation with Lean 4.35.0; FORMAL | UNRESOLVED; Mathlib missing, no successful compilation or formal receipt. |
| R16 | Prior-result comparisons and counterexample for a different family; REFERENCE | SUPPORTED as the reviewer's assessment; controller source retrieval still has failures. |

R13 reports checks of all \(d=0,\ldots,2n\) for \(n=9,\ldots,100\): 10120 coefficients within support, plus \(d=2n+1\) for each \(n\). Internal positivity, zero endpoints, zero outside support, and palindromicity agreed with the candidate. Five additional parameter sets tested adjacent relations and equations (1), (2), (5), including odd \(d\) and \(d=n\); their exact values are not listed in the visible record and cannot be invented.[M1]

The Solve answer reports three passing integer-algebra tests, while its proof describes four exact rational substitutions checking normalization and half-integral parameters. These must remain distinct from Verify's five connection experiments; they cannot be combined into additional independent verifications. The inherited Find information separately mentions experiments for \(n=1,\ldots,100\) and probe evaluations of \(-84,324\). These survive as saved descriptions, without their executable programs or complete output in this bundle.[M2] [M4]

## 5. What Lean, receipts, and hashes establish

**The list of candidate theorems with successful Lean theorem-checking receipts is empty.** Every one of the 16 checks has an empty `formal_declarations` list. No request or receipt identifies a kernel-proved main theorem. Literature download receipts are not formal-proof receipts.[M1]

| Object | What the frozen record actually says | What does not follow |
|---|---|---|
| `FindProbes.FranelConjecture` | R14 describes a Prop definition `CoeffwiseLogConvexFrom franel 8`, with condition `8<n`. The inherited Find description reports earlier successful elaboration. | Defining a proposition does not prove it; there is no successful receipt bound to this candidate. |
| `deltaCoeff` | An executable finite sum; inherited records mention evaluations of \(-84\) and \(324\). | No equivalence theorem with `Polynomial.coeff`, and no universal positivity theorem. |
| `StatementProbes.lean` | R14 records source hash `8a00d28b653669be3158f996cbd0164614491887a7a101851af0a67b21f10a4a`; the manifest explicitly excludes the source. | Its original bytes cannot now be inspected; the hash alone proves neither declaration semantics nor successful compilation. |
| Local compilation attempt | R15 records Lean 4.35.0 reporting `unknown module prefix 'Mathlib'`; outcome UNRESOLVED. | Compilation cannot be called successful; this is also not a refutation of the written identities. |
| Theorem 1, strictness, equalities, threshold | Supported by the written candidate and review. | No corresponding Lean theorem declarations, dependency closure, or kernel receipts. |

The two problem-hash domains must remain separate. The UTF-8 SHA-256 of `Problem.statement` is `2275c68fbb750017200eb777926cbcdcc2a9b40ec6f59017e67ad69057bbd192`. The organization manifest's fingerprint of the full canonicalized Problem record is `9b3d92fc177c85627a748a19f196d19acfcc809a7c617d4a53e2d82cd7e5e3b6`. Their inputs differ, so unequal values do not constitute a mismatch. Original webpage/PDF hashes and manifest hashes of extracted text likewise identify different byte objects. This bundle contains no formal receipt to match against the candidate: no successful match can be claimed, and no actual formal-receipt hash conflict should be invented. Missing or mismatched receipts cannot support the candidate; matching hashes alone cannot certify correspondence between natural-language and formal statements.

## 6. Original-problem coverage, prior work, and novelty obstacles

At the level of the submitted mathematical argument, the definition, integer domains, \(n\ge9\), all \(d\ge0\), formal variable, zero boundary coefficients, and strict internal positivity are addressed. These support R01–R11 and the saved `FULL` assessment. The original problem asks only for nonnegativity; strict positivity strengthens it rather than restricting its domain. Nevertheless, the structured alignment list is empty, the historical problem has `scope_relation=UNKNOWN`, and no external natural-language/formal-statement equivalence certification exists. These three levels cannot be merged into a new coverage certificate.

| Source and saved locator | Recorded result or proposition | Relation to this problem and evidence limits |
|---|---|---|
| Sun, 2026, first clause of Conjecture 1.1(i) [L1] | The same \(F_n\), with nonnegativity conjectured for the tail starting at 8. | Equivalent to the original nonnegativity claim; the full candidate adds strictness. The review citation's `DIFFERENT` compares the full strengthened claim, not a changed problem. Text and a successful text receipt survive.[M5] [M7] |
| Sun, 2024, comment 1247286 [L2] | The saved record attributes the earliest actually read public question for this conjecture to that comment. | The reviewer says the full text was obtained, but the controller receipt is UNAVAILABLE; independent source verification cannot be declared complete.[M10] |
| Chen–Tang–Wang–Yang, 2010, equation (1.1), Theorem 1.1, and following discussion [L3] | The full sequence \(W_n(q)=\sum_k\binom nk^2q^k\) is coefficientwise log-convex; full power sequences with exponent at least 3 are not. | Squared and cubed weights differ; failure of the full sequence does not refute a tail. R16 gives \(c_{2,2}=-12\), outside this problem's domain. A successful excerpt receipt survives, but the PDF and extracted text do not.[M8] |
| Zhu–Sun, 2015, Theorem 2.1 and Corollary 2.9 [L4] | Strong coefficientwise log-convexity of \(P_n(q)=\sum_k\binom nk^2\binom{2k}kq^k\), and preservation conditions. | \(P_2=1+8q+6q^2\ne F_2=1+8q+q^2\). A fixed input weight in the preservation theorem cannot simply be replaced by \(\binom nk\), which depends on \(n\). The original text is absent; the EMIS receipt is UNAVAILABLE.[M11] |
| Došlić, §4, Corollary 3 [L5] | Numerical sequences \(F_n^{(r)}=\sum_k\binom nk^r\) are log-balanced for \(r=3,4\). | By the §2 definition, this includes log-convexity and log-concavity after division by \(n!\). It supplies numerical information at \(q=1\), not signs of individual coefficients. Text and a successful receipt survive.[M6] [M9] |
| Zhou, 2026-07-24, answer 513542 [L2] | A counterexample for \(\sum_k\binom{n+k}k^m q^k\), with \(m=5\), center \(n=7\), and quadratic coefficient \(-499140\). | Both weights and quantifiers differ. R16 reports recomputation of that value, but independent webpage retrieval still failed. It is neither a counterexample nor a solution to this problem.[M10] |

These papers are not external premises of the candidate's algebraic proof. The saved comparisons do not classify the candidate as a `SPECIAL_CASE` of any of these theorems, nor do they exhaust unknown transformations or every definition attached to the Franel name.

**An evidential discrepancy that must be preserved.** The review's `literature_search.conclusion` and `novelty_notes` say the relevant originals were obtained and specific obstacles were resolved, with `unresolved` left empty. The controller nevertheless records `evidence_assessment.supported=false`, explicitly citing failures to verify the robots policies for MathOverflow and EMIS, and sets the corresponding `verified_excerpt=false`. Actual failure receipts [M10] [M11] support the latter record, so the former prose cannot be copied as an established resolution. The inherited Find record also retains `HTTP400 no_method` at the Stack Exchange API robots endpoint and incomplete access to the author's old homepage bibliography. A researcher-side GET200 is not a substitute for an independent controller receipt. These failures remain visible historical evidence.[M1] [L6] [L7]

The review saves 20 queries covering mainly English indexes, a few Chinese terms, arXiv, the author's public question page, and the listed papers, with the search dated 2026-10-23. It does not cover all languages, databases, citation networks, unindexed work, or unpublished results. The latest actually read author version explicitly stating the conjecture is still dated 2026-02-10; no later dedicated reaffirmation of its open status was obtained. Accordingly, “no prior proof found” and `POTENTIALLY_NEW` certify neither a first solution, priority, nor the current worldwide open status. The final `UNKNOWN` remains unchanged.

## 7. Missing materials and limits of reproduction

The saved review identifies no blocking mathematical gap, and both candidate and review have `remaining_obligations=[]`. That does not remove evidence limitations: there is no external expert assessment or formal universal theorem, and the original table-checking code, logs, and dependency environment cannot be replayed from this bundle. Any future defect found in a certificate would require a new Solve/Verify, rather than a silent editorial repair. No new proof repair is proposed here.

Both dossiers have `visible_research_notes=[]`. The candidate's named `proof.zh.md`, `certificate.json`, `check_certificate.py`, and `test_certificate.py` are not listed in the manifest; fortunately, the complete proof and coefficient tables survive in the JSON `proof` field. The review's named `review.md`, `check_algebra.py`, `algebra_results.json`, `test_connections.py`, algebra/pytest/ruff/Lean logs, and search/download logs are also absent. Repeated evidence entries pointing to a raw event file do not represent multiple independent checks, and that event file itself is not supplied. Execution details or failed attempts cannot be inferred from filenames.

The manifest also explicitly excludes the Lean source and omits the extracted Chen et al. file with reason “binary content”; the original PDF is not in the file list either. The MathOverflow, EMIS, and API originals are absent. Readable extracted texts for Sun and Došlić are supplied but are not the original webpage bytes. These exclusions and omissions do not describe downloads performed by this report.

**Portable inspection commands.** Run the following from an exported report's root to read the saved proof and checks. It is an inspection template, not a mathematical verification receipt. This command in the exported layout was not executed in this session.

```bash
python - <<'PY'
import json
from pathlib import Path
d = json.loads(Path('materials/reviewed-source/dossier.json').read_text(encoding='utf-8'))
c = d['candidates'][0]
print(c['proof'])
r = c['reviews'][0]
for i, check in enumerate(r['checks'], 1):
    print(f'R{i:02d}', check['method'], check['result'], check['claim'])
print(r['proof_coverage'])
print(r['evidence_assessment'])
PY
```

**Conditional templates for the original mathematical checks, not executed.** If the original sources are separately recovered and identified, the following entry points can be attempted from the original certificate directory. They are reproduction suggestions based on filenames, not frozen original command lines or success records:

```bash
conda run -n mathlottery python check_certificate.py
conda run -n mathlottery pytest -q test_certificate.py
```

The candidate describes its checker as standard-library-only Python; the review additionally used SymPy 1.14.0. No environment lockfile survives. Full reproduction should compare all coefficients in (4) and all instances of (6), and separately audit (1), (2), positivity, and range assembly. Numerical sampling alone cannot replace these steps. Lean reproduction first requires the original source, Mathlib, toolchain, and module paths. This bundle contains neither a successful command to quote nor a universal theorem to replay. Installing new dependencies or recompiling for presentation would not supply such a proof. This session checks only the frozen files and report transcription, adding no mathematical tests or formal receipts.

## 8. Bibliography: sources in the frozen record only

1. **[L1]** Zhi-Wei Sun, *A family of polynomials and related congruences and series*, arXiv:2505.02767v4, 2026-02-10; *Frontiers in Combinatorics and Number Theory* 2 (2026), 1–22, DOI 10.3934/fcnt.2026009. Locator: §1, first clause of Conjecture 1.1(i), identified as PDF p. 3 in the dossier. Readable text [M5], successful receipt [M7]. The separately referenced arXiv PDF is not in the bundle.[L1PDF]
2. **[L2]** MathOverflow, *On the polynomials sum binom(n+k,k)^m q^k*, question 479301. Sun's comment 1247286 (2024-09-21) and Qiping Zhou's answer 513542 (2026-07-24). Successful full-text access is asserted in reviewer prose; the controller receipt failed [M10].
3. **[L3]** William Y. C. Chen, Robert L. Tang, Larry X. W. Wang, Arthur L. B. Yang, *The q-Log-convexity of the Narayana Polynomials of Type B*, *Advances in Applied Mathematics* 44(2) (2010), 85–110. Locators: equation (1.1), Theorem 1.1, and the subsequent statement about full power sequences. Successful receipt [M8]; original text absent.
4. **[L4]** Bao-Xuan Zhu, Hua Sun, *Linear transformations preserving the strong q-log-convexity of polynomials*, *Electronic Journal of Combinatorics* 22(3) (2015), P3.26; saved date 2015-08-28. Locators: Theorem 2.1 and Corollary 2.9, the latter on PDF p. 9. Text absent; failed receipt [M11].
5. **[L5]** Tomislav Došlić, *Log-balanced combinatorial sequences*, arXiv:math/0603403v1, publicly submitted 2006-03-16. Locators: §2 definition and §4 Corollary 3. The dossier separately records journal year 2005; the extracted page's autogenerated date is not a priority date. Readable text [M6], successful receipt [M9].
6. **[L6]** Official Stack Exchange API: comment 1247286. An inherited Find source for attribution, timestamp, and body linkage; no independent successful retrieval receipt or original JSON is supplied here.
7. **[L7]** Official Stack Exchange API: answers to question 479301. An inherited Find source used to distinguish the rising-binomial counterexample; the robots-policy failure remains, and this is not treated as a newly verified source.

## Appendix A. Complete large-degree certificate data

These are item-for-item transcriptions of the selected candidate, not newly fitted tables. Each name denotes \(T(H,Z)=\sum_j Z^j\sum_i a_{j,i}H^i\). Labels \(j\) run consecutively from 0 and specify the power of \(Z\); entries within each array are in increasing powers starting with \(H^0\); unlisted terms are zero. Array line breaks are for layout only. Here \(T\) is a generic table name, distinct from the temporary notation \(T=hm\) in Lemma 5. Set \(H=h-8,Z=z-1\). The four tables are used in equations (3)–(5).[M1]

**\(U\)**

```text
j = 0: [307097, 205923, 54558, 7154, 465, 12]
j = 1: [97515, 52413, 10452, 918, 30]
j = 2: [9867, 4017, 540, 24]
j = 3: [313, 87, 6]
```

**\(V\)**

```text
j = 0: [64781696, 46643040, 13986038, 2235552, 200900, 9624, 192]
j = 1: [32616248, 19609687, 4713694, 566258, 33996, 816]
j = 2: [6496373, 3132431, 566144, 45456, 1368]
j = 3: [645189, 234105, 28302, 1140]
j = 4: [32913, 8001, 486]
j = 5: [783, 96]
j = 6: [6]
```

**\(C\)**

```text
j = 0: [99860992, 211925120, 138536712, 45315104, 8632824, 1007294, 71282, 2820, 48]
j = 1: [160387152, 192549258, 90555744, 22440166, 3221715, 270695, 12402, 240]
j = 2: [61746819, 56108328, 20416035, 3853735, 400892, 21894, 492]
j = 3: [10463364, 7493063, 2099159, 289088, 19641, 528]
j = 4: [890650, 497001, 102473, 9279, 312]
j = 5: [37156, 15467, 2121, 96]
j = 6: [603, 171, 12]
```

**\(D\)**

```text
j = 0: [427997128832, 465018127136, 224478819170, 63191271556, 11431762918, 1378283176,
        110747342, 5718788, 172208, 2304]
j = 1: [292371224424, 282851567901, 119678048430, 28925900205, 4368118770, 422024571, 25475190,
        878448, 13248]
j = 2: [85543112127, 72559909640, 26368087506, 5321522637, 644159179, 46768272, 1885764, 32576]
j = 3: [13985927051, 10192998147, 3094132746, 500741365, 45567009, 2210688, 44672]
j = 4: [1397506290, 851226645, 207310326, 25234383, 1535190, 37344]
j = 5: [87623274, 42850554, 7854708, 639630, 19524]
j = 6: [3399643, 1252567, 153754, 6288]
j = 7: [77103, 19050, 1176]
j = 8: [900, 112]
j = 9: [4]
```

## Appendix B. Complete small-degree certificate data

Each entry supplies \(d,s_d,a_d\) and the coefficients of \(R_d(y)\) in increasing order from the constant term. See Lemma 7 for \(B_d\). All data are transcribed from the same candidate. Together with Appendix A there are 319 positive integer coefficients, excluding the denominators of \(a_d\) from that count. These tables are proof data, not execution logs.[M1]

**\(d=1,\quad s_d=9,\quad a_d=6\)**

```text
[1]
```

**\(d=2,\quad s_d=9,\quad a_d=3/4\)**

```text
[6, 9, 1]
```

**\(d=3,\quad s_d=9,\quad a_d=1/6\)**

```text
[1695, 524, 55, 2]
```

**\(d=4,\quad s_d=9,\quad a_d=1/1152\)**

```text
[906660, 606852, 157791, 20053, 1253, 31]
```

**\(d=5,\quad s_d=9,\quad a_d=1/28800\)**

```text
[14758200, 10140660, 2948694, 464343, 41685, 2017, 41]
```

**\(d=6,\quad s_d=9,\quad a_d=1/5184000\)**

```text
[3018249000, 3185348400, 1452628500, 374981609, 60091171, 6136187, 390703, 14204, 226]
```

**\(d=7,\quad s_d=9,\quad a_d=1/381024000\)**

```text
[36121734000, 40554558900, 20447564775, 6065933134, 1164396822, 149693346, 12868953, 712680,
 23058, 332]
```

**\(d=8,\quad s_d=9,\quad a_d=1/2731180032000\)**

```text
[109463378745600, 167663382874560, 115622446795440, 47498771324916, 12941751343608,
 2459666153285, 333156580308, 32187939717, 2175149424, 97950615, 2646036, 32491]
```

**\(d=9,\quad s_d=9,\quad a_d=1/442451165184000\)**

```text
[1117584848033280, 1810387011828096, 1355680881251424, 619238575993608, 191756723674876,
 42335098555334, 6823863235291, 808443530058, 69833875347, 4288297434, 177678041, 4459918,
 51293]
```

**\(d=10,\quad s_d=10,\quad a_d=1/159282419466240000\)**

```text
[451699433896550400, 819623216041781760, 686594884593149568, 352399534959570848,
 123936504121490456, 31620126296254340, 6038668533719606, 877281142708217, 97449034444475,
 8237696335453, 521702074411, 24004320235, 758581609, 14738587, 132835]
```

**\(d=11,\quad s_d=11,\quad a_d=1/48182931888537600000\)**

```text
[27823034669008550400, 47927580137127365760, 38595678978280963104, 19258255067061183512,
 6654374275166294860, 1685775512377439410, 323350422843351867, 47808444075416264,
 5492848968686090, 490368676596710, 33737000323304, 1756612187426, 67005350250, 1767716320,
 28841725, 219398]
```

**\(d=12,\quad s_d=12,\quad a_d=1/76321764111443558400000\)**

```text
[46519378688524620902400, 85706776005984113794560, 74130623502307582074624,
 39992373456765757934112, 15076105170871611013632, 4215263861158366300176,
 905299887281794026952, 152558810613926738894, 20423631322112138626, 2184580493187401297,
 186702995238633034, 12676932684154676, 675478150170242, 27652862969278, 839953922990,
 17838465118, 236503100, 1473889]
```

**\(d=13,\quad s_d=13,\quad a_d=1/38695134404501884108800000\)**

```text
[3459404445967724713804800, 6166611738311666090181120, 5188748093707721377088448,
 2737631294540610387993504, 1014747192888161349073248, 280576066602611317688208,
 59968597099836256096436, 10130044396754966563278, 1370968140329631635454,
 149761262206625991615, 13235927593076431017, 944193454824845142, 53961631162779938,
 2437253521952256, 85085283144996, 2215356191676, 40511595360, 464318001, 2510303]
```

**\(d=14,\quad s_d=14,\quad a_d=1/98595202462670800709222400000\)**

```text
[8387445380396926317255936000, 15696327584556243881557056000, 13931598464618789109492489600,
 7798511554758385143960362976, 3087934141191123116332604736, 919415661239910468650450688,
 213591710748227926762482616, 39645420868474072867286038, 5971395441429940601134984,
 737051312244865319614545, 74959962714772609127826, 6292644920148239781264,
 435261761599544454355, 24672594864088979776, 1134923923912841710, 41713436706372804,
 1196316564824904, 25801937274591, 393709471048, 3789762118, 17307421]
```

**\(d=15,\quad s_d=15,\quad a_d=1/388218609696766277792563200000000\)**

```text
[3731056290570604632494598720000, 6800347106090882213945814144000,
 5896435691026993413000134786400, 3234669205564115860177828121760,
 1259445399562339782835721329728, 370092431675858555048223067488, 85199413658273487767561109918,
 15742995092350096358030697370, 2372899427067482172004667669, 294868695982007263192857097,
 30405513078566738387603916, 2609689786505267187523725, 186440030871015805157295,
 11052644427076578292876, 540199525826052878114, 21537110568764640400, 689204649363387591,
 17278451349543405, 326916811439652, 4389985050745, 37293959717, 150701134]
```

## Appendix C. Visible chronology and failure records

| Time (UTC) | Saved event and its limits |
|---|---|
| Around 2026-10-23 05:28 | The inherited problem dossier retains Find statement checks, finite probes, and UNKNOWN status. At center \(n=8,d=2\), \(-84\) refutes the incorrectly enlarged domain; \(n=9,d=2\) gives 324. MathOverflow/API robots failures and the old-homepage bibliography gap persist. No separate Find-session history is imported. |
| 2026-10-23 13:51:39–14:23:43 | Explicitly linked Solve: one saved candidate, COMPLETE/CANDIDATE. Its answer reports three passing tests and explicitly says independent verification has not yet occurred.[M2] [M4] |
| 2026-10-23 14:36:40–15:02:00 | Verify: 16 checks, 15 SUPPORTED and one FORMAL/UNRESOLVED due to missing Mathlib. LLM assessment NO_ISSUES_FOUND/FULL, prose assessment POTENTIALLY_NEW; final novelty UNKNOWN and candidate SELF_CHECKED. Independent MathOverflow and EMIS retrieval failed.[M1] [M3] |
| 2026-10-25 12:36:24 | The organization manifest freezes the selected review and explicitly linked Solve. It warns that a source revision may include work saved after review, which cannot be retroactively approved; this report uses only the matching original candidate and explicit review. |
| This Organize session | Reading frozen materials, arranging the proof, and comparing bilingual transcription only; no certificate rerun, Lean recompilation, new literature search, or evidence-level change. |

No other candidate versions, abandoned routes, failed solution drafts, or hidden reasoning are visible, so none are invented. Recorded mathematical negative examples, the formal failure, and source-retrieval failures remain visible. “No issues found” and empty obligation lists are not recast as proof of a worldwide first solution.

## Appendix D. Concise material index

This index supports reading the mathematics; the controller separately generates the full file-checking and handoff index. All links are relative to the exported report's `materials/` directory and target files actually supplied in the manifest.

| Material | Purpose |
|---|---|
| [M1] Reviewed dossier | Exact candidate text, 16 checks, status fields, literature excerpts, and evidence assessment; the primary source for this report. |
| [M2] Explicitly linked Solve dossier | The same candidate, assumptions, and original self-reported scope; no reviews or visible research notes. |
| [M3] Saved Verify answer | Concise review conclusion; its favorable novelty wording must be read with the final UNKNOWN in [M1]. |
| [M4] Saved Solve answer | Self-report of candidate completion and three tests; the programs it links are absent. |
| [M5] Extracted Sun text | Definition, Conjecture 1.1(i), neighboring distinct propositions, and references. |
| [M6] Extracted Došlić text | Definition of log-balancedness and Corollary 3 for numerical Franel sequences. |
| [M7] Sun source receipt | OK; text matching only, not certification of interpretation or search completeness. |
| [M8] Chen et al. source receipt | OK; original PDF/extracted text absent; a receipt is not the complete paper. |
| [M9] Došlić source receipt | OK; text matching only. |
| [M10] MathOverflow source receipt | UNAVAILABLE; robots policy could not be verified. |
| [M11] EMIS source receipt | UNAVAILABLE; robots policy could not be verified. |

[M1]: materials/reviewed-source/dossier.json
[M2]: materials/solver-source/dossier.json
[M3]: materials/reviewed-source/tasks/task-record-002/attempt-record-002/answer.md
[M4]: materials/solver-source/tasks/task-record-001/attempt-record-001/answer.md
[M5]: materials/omitted-sources.md#source-1
[M6]: materials/omitted-sources.md#source-2
[M7]: materials/reviewed-source/literature/receipts/86e133a57f3135e3a9f0152f1439a721a5ceec4a1e29b8f1fcefcba104b6c8f7.json
[M8]: materials/reviewed-source/literature/receipts/420c3f8ccfa26cb393d1f401c628667d042902b02bae0c10648a5cfe65eed0cf.json
[M9]: materials/reviewed-source/literature/receipts/d53a616b09dd7a95c2e236d1b432113039a01800184ed4861153576e789437a0.json
[M10]: materials/reviewed-source/literature/receipts/6cf136a4f1583b1200993b61ec664cb96012453cdc3ac08e14792f56e15a08ff.json
[M11]: materials/reviewed-source/literature/receipts/c3279ec33e5b91c0c9b8e05350cdd883dc77e86abf5ddd57c1c9ce03e9458a22.json
[L1]: https://arxiv.org/html/2505.02767v4#S1.Thmconjecture1
[L1PDF]: https://arxiv.org/pdf/2505.02767v4
[L2]: https://mathoverflow.net/questions/479301/on-the-polynomials-sum-k-0n-binomnkkm-qk
[L3]: https://cfc.nankai.edu.cn/_upload/article/files/d2/e7/02ad99784f4bbe19008160bb92ce/session-record-001.pdf
[L4]: https://emis.de/ft/31765
[L5]: https://arxiv.org/html/math/0603403v1
[L6]: https://api.stackexchange.com/2.3/comments/1247286?site=mathoverflow&filter=withbody
[L7]: https://api.stackexchange.com/2.3/questions/479301/answers?site=mathoverflow&filter=withbody
