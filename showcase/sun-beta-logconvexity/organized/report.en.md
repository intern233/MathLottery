> **Publication copy.** Local identifiers are replaced by stable aliases; personal data is screened. The frozen evidence inventory is [source-manifest.json](source-manifest.json); the actual public files and transformations are in [manifest.json](manifest.json). Downloaded article full texts are [omitted](materials/omitted-sources.md). Historical verification statements below are unchanged in scope; this export adds no proof review or novelty certification.

[mathlottery-expert-brief-v2]: #

# MathLottery expert reading report

> Frozen evidence only: this does not upgrade proof status or novelty, and adds no verification.

## Expert quick review

This is a navigation summary, not a complete proof. Ellipses mark display excerpts; frozen materials and the listed JSON paths contain full text, history and evidence. Source text is not translated; later success does not erase historical failures.

Source task: reviewed-source · Frozen revision: 26 · 2026-10-25T12:11:08.547899+00:00

Snapshot SHA-256: `5794400e6e7df74d99b84c863dd5c5fa03e68180addbef0f3acd706c465e8cdf`

Problem SHA-256: `3d0e93e3a159b0da83e8bee6bce4416f9a6e2aa84a953c5abea9bc3fda99c1b4`

[Evidence manifest](source-manifest.json) · [Frozen dossier (all records)][frozen-dossier]

[Read the full report](#full-editorial-report) · [Evidence index](#evidence-index)

### 1. Original problem and candidate claims

**Sun 的 beta 多项式逐系数对数凸猜想（Conjecture 4.7 第一项）**

对每个整数 n&gt;=0，令 beta\_n(q)=sum\_{k=0}^n binom(n,k)^2 binom(n+k,k) q^k ∈ Z&#91;q&#93;。证明：对所有整数 n&gt;=1 和 d&gt;=0，&#91;q^d&#93;(beta\_{n-1}(q) beta\_{n+1}(q)-beta\_n(q)^2)&gt;=0。等价地，(beta\_n(q))\_{n&gt;=0} 是 q-log-convex。q 是形式变量；不能将目标弱化为仅对每个实数 q&gt;=0 的点值不等式。

[/problem/statement][frozen-dossier]

Open status: `OPEN` · Checked: 2026-10-23T05:28:55.828585+00:00

[Original source](https://arxiv.org/html/1104.3856v8)

**candidate-record-002** · `PARTIALLY_VERIFIED` · scope `COMPLETE`

SHA-256: `87fe6633c0cb96ba88f5883d98ecef69a16abec88035d296e2f4f9f25b15fbf9` · With review snapshot: `3817f4ccbfd325651ea585817387490cc68b3ca85b32b59e8a436cea6347bc5b`

对每个整数 n≥0，令 beta\_n(q)=Σ\_{k=0}^n binom(n,k)^2 binom(n+k,k)q^k∈Z&#91;q&#93;。对所有整数 n≥1 和 d≥0，都有 &#91;q^d&#93;(beta\_{n-1}(q)beta\_{n+1}(q)-beta\_n(q)^2)≥0。完整 Lean 主定理为 SunBeta.beta\_coeffwise\_logconvex，单一源文件 proof/SunBeta.lean。本主张是覆盖原题全部量词的候选证明，不是独立 Verify 的结论。

[/candidates/0][frozen-dossier]

Assumptions: 仅原题条件：n、d 为整数，n≥1、d≥0；beta\_n 对全部 n≥0 按原二项式有限和定义。; q 是形式变量，系数在 Z 中比较；不增加点值、有限范围或额外参数假设。

**Latest status**: `NO_ISSUES_FOUND` · Coverage=`FULL` · Lean=`KERNEL_REPLAYED` · Novelty=`UNKNOWN`

### 2. Verification, key steps and historical failures

**candidate-record-002**

| Review | Verdict | Coverage | Novelty |
| --- | --- | --- | --- |
| 1 | `INCONCLUSIVE` | `UNKNOWN` | `KNOWN` |
| 2 | `INCONCLUSIVE` | `PARTIAL` | `UNKNOWN` |
| 3 | `NO_ISSUES_FOUND` | `FULL` | `UNKNOWN` |

10 historical issues or unresolved checks are retained in the evidence index; later success has not removed them.

Latest proof assessment: 提交证明作为整体完整有效。核对内容包括正权重及全部支撑边界、相邻行列递推、配对卷积的2n因子、零和式端点、d&gt;2n系数为零、奇偶重参数化、m=0/m=1/r=0边界、H非零和D正、与求和指标无关的Cramer系数、334和415项正系数证书、最终除以2nD。SymPy重建和只用整数稀疏多项式运算的第二套核查都精确验证全部恒等式，非有限取值检验。本轮直接检查控 …

Statement coverage: 独立比较实际源码及控制器实际声明：SunBeta.beta : ℕ → Polynomial ℤ，定义为∑k∈range(n+1), monomial k ((n.choose k:ℤ)^2\*((n+k).choose k:ℤ))，恰等于原题从k=0到n的二项式有限和。主定理只有n:ℕ、hn:1≤n、d:ℕ三个参数，结 …

Novelty explanation: 数学正确性与新颖性分别判断。Sun2014原猜想及其2014追述继续标为ORIGINAL\_STATEMENT，2026-02-10明确开放声明标为EXPLICIT\_OPEN；EQUIVALENT仅指同一目标，不表示已有证明。已成立的Narayana、S\_n、D\_n、Zhu–Sun …

Coverage policy: `UNASSESSED` · proof_complete=False · statement_aligned=False

Key-step coverage is unassessed; a verdict label does not imply completeness.

No structured proof roadmap recorded; reconstruct it from the full dossier.

[/candidates/0/reviews/2][frozen-dossier]

Lean: `KERNEL_REPLAYED` · —

Declarations: SunBeta.beta\_coeffwise\_logconvex

Check scope: Requested theorem declarations only; imported libraries and the Lean kernel are trusted. No independent kernel implement … · Statement alignment: `NOT_CERTIFIED`

[Frozen execution receipt](materials/reviewed-source/verification/formal/42f471b6b8f76c0b78c3f1414a7e39c02a3375dcc3718892aa820903d4199f4a/receipt.json)

Formal checks cover receipt declarations only; natural-language/formal-statement equivalence has no external certification.

### 3. Literature obstacles and novelty

Grouped by stable ID, kind and source; different sources stay separate. Historical states remain visible, without implying every old issue is still unresolved. Links identify frozen JSON paths.

Evidence policy: evidence-v2

No listed obstacle establishes exhaustive search or novelty.

The evidence index retains all 0 obstacle entries, 0 prior-result comparisons and 17 other gaps/scope limits; sources and comparisons for unresolved entries still need individual review.

### 4. Expert priorities and evidence navigation

1. Read the full proof and check key lemmas, quantifiers and boundaries; excerpts do not replace stepwise review.
2. Address unresolved obstacles individually and compare the closest prior theorems.
3. LLM approval and finite tests do not prove a general theorem.

## Evidence index

The index locates original records without repeating full proofs or quotations; the frozen dossier contains complete text. [Skip to the full report](#full-editorial-report).

### Historical issues and failed checks

**candidate-record-002**

- evidence gate · review 1: A blocking formal check has no independently successful execution receipt · [/candidates/0/reviews/0/validation\_notes/0][frozen-dossier]

- evidence gate · review 1: Full coverage requires a supported comparison to the original statement · [/candidates/0/reviews/0/validation\_notes/1][frozen-dossier]

- Lean ERROR · review 1: compile-0 did not complete successfully · [/candidates/0/reviews/0/formal\_receipt][frozen-dossier]

- issue · review 2: 验证未完成：控制器首轮编译返回1，在两个关键恒等式处报告(kernel) excessive memory consumption detected；本轮资源提高后的结果尚未产生。 · [/candidates/0/reviews/1/issues/0][frozen-dossier]

- issue · review 2: 首次审阅三条来源角色标错，把原猜想/开放声明写成PRIOR\_RESULT。此错误发生在审阅证据分类，不是候选证明；本次纠正并保留旧记录。 · [/candidates/0/reviews/1/issues/1][frozen-dossier]

- issue · review 2: EMIS载体已用公开原期刊PDF替代；MathOverflow原回答仍无可独立核验的替代载体，其具体来源缺口保持可见。 · [/candidates/0/reviews/1/issues/2][frozen-dossier]

- evidence gate · review 2: Full coverage conflicts with the candidate scope or remaining obligations · [/candidates/0/reviews/1/validation\_notes/0][frozen-dossier]

- check-15 · UNRESOLVED · blocking=True · review 2: 控制器能够在本次重新配置的资源限制下编译、重放冻结主定理并核对公理依赖。 — 实际读取并原样保存首轮receipt.json：status=ERROR、compile-0返回码1、elapsed\_seconds=207.363、memory\_mb=8192、address\_space\_mb=1638 … · [/candidates/0/reviews/1/checks/14][frozen-dossier]

- check-17 · UNRESOLVED · blocking=False · review 2: MathOverflow反例条目的完整内容、作者归属及发布日期具有独立下载器可复核的原始公开载体。 — 已进行针对作者、题名、−499140和反例的查询，没有找到另一份原始作者版本。未绕过MathOverflow的访问策略；第一次本地取得的文本保留，不能替代控制器独立下载器的策略核验。可校验的Sun … · [/candidates/0/reviews/1/checks/16][frozen-dossier]

- check-17 · UNRESOLVED · blocking=False · review 3: MathOverflow反例条目的完整内容、作者归属及发布日期具有独立下载器可复核的原始公开载体。 — 控制器2026-10-23T07:58:05.384018+00:00的来源评估仍报告该URLUnable to verify robots policy for https://mathover … · [/candidates/0/reviews/2/checks/16][frozen-dossier]

### Literature obstacle history (all IDs)

**Other search gaps and scope limits (deduplicated, all retained)**

| Excerpt | Full record |
| --- | --- |
| 检索截至2026-10-23；主要覆盖英文索引、arXiv、作者公开网页和所列原论文，不保证覆盖全部数据库、语言、未索引或未公开作品。 | [/problem/evidence\_assessment/limitations/0][frozen-dossier] |
| 最新明确开放声明的来源日期是2026-02-10；10月下载日期不会更新该声明，后续未索引解答仍可能存在。 | [/problem/evidence\_assessment/limitations/1][frozen-dossier] |
| 旧作者个人主页无法取得完整书目，只限制作者后续作品的覆盖；未识别到其中某一篇可能解决本题而尚未读取的具体论文。 | [/problem/evidence\_assessment/limitations/2][frozen-dossier] |
| 原始2014v8及2017v9已核对，2011v1/v7未含该项；未主张2014是全球首次提出日期，也未穷尽2011至2014所有公开载体。 | [/problem/evidence\_assessment/limitations/3][frozen-dossier] |
| 没有宣称排除文献中所有非显然推导。已具体核对的Narayanа、Sn、Domb、Zhu–Sun权重/条件不同；剩余泛指“可能存在未知等价证明”属于检索覆盖边界。 | [/problem/evidence\_assessment/limitations/4][frozen-dossier] |
| https://emis.de/ft/31765: Unable to verify robots policy for https://emis.de | [/candidates/0/reviews/0/evidence\_assessment/reasons/0][frozen-dossier] |
| https://mathoverflow.net/questions/479301/on-the-polynomials-sum-k-0n-binomnkkm-qk: Unable to verify robots policy for https://mat … | [/candidates/0/reviews/2/evidence\_assessment/reasons/0][frozen-dossier] |
| 检索截至2026-10-23，主要覆盖公开网络索引、arXiv、期刊/作者公开稿及检索命中的一手来源；英文为主，辅以一条中文检索，不穷尽全部语言或数据库。 | [/candidates/0/reviews/0/evidence\_assessment/limitations/0][frozen-dossier] |
| 最新直接称精确beta问题开放的已核对来源日期为2026-02-10；检索和下载日期不能将该状态声明更新为2026-10-23。2026年8月至9月的新论文已比较，但未索引、未公开或未命中的解答仍可能存在。 | [/candidates/0/reviews/0/evidence\_assessment/limitations/1][frozen-dossier] |
| 已逐一检查列出定理的对象、量词和可见参数特例，不宣称排除全体文献中的非显然推论或重构证明。没有已识别但未读的潜在精确beta解答；若后来发现这类来源，需要重新评价新颖性。 | [/candidates/0/reviews/0/evidence\_assessment/limitations/2][frozen-dossier] |
| LLM文献审阅和本地计算不是外部专家对原创性或自然语言/形式化语义对应的认证。 | [/candidates/0/reviews/0/evidence\_assessment/limitations/3][frozen-dossier] |
| https://mathoverflow.net/questions/479301/on-the-polynomials-sum-k-0n-binomnkkm-qk：控制器第一轮独立下载器无法核实robots policy；本次针对性查询未找到作者版或正式发表 … | [/candidates/0/reviews/1/evidence\_assessment/reasons/1][frozen-dossier] |
| 检索截至2026-10-23，以公开网络索引、arXiv、期刊/作者公开稿为主，主要英文并含中文查询；不穷尽全部数据库或语言。 | [/candidates/0/reviews/2/evidence\_assessment/limitations/0][frozen-dossier] |
| 直接称精确beta猜想开放的最新已核对文字日期是2026-02-10；后续下载时间不更新该状态。未索引或未公开解答仍可能存在。 | [/candidates/0/reviews/2/evidence\_assessment/limitations/1][frozen-dossier] |
| 对列出结果核对了定义、量词和可见参数特例，不宣称排除全体文献中的非显然推论。LLM检索不能认证全球首次性。 | [/candidates/0/reviews/2/evidence\_assessment/limitations/2][frozen-dossier] |
| 本独立会话的源码语义比较及本地计算不是外部专家对自然语言/形式化对应或原创性的认证。 | [/candidates/0/reviews/2/evidence\_assessment/limitations/3][frozen-dossier] |
| https://mathoverflow.net/questions/479301/on-the-polynomials-sum-k-0n-binomnkkm-qk：控制器最新来源评估仍报告Unable to verify robots policy for … | [/candidates/0/reviews/2/evidence\_assessment/reasons/1][frozen-dossier] |

### Material navigation and scope limits

**Proof and reviews** (17): [dossier.json](materials/reviewed-source/dossier.json) · [answer.md](materials/reviewed-source/tasks/task-record-002/attempt-record-003/answer.md) · [answer.md](materials/reviewed-source/tasks/task-record-001/attempt-record-002/answer.md)

**Formal** (14): [receipt.json](materials/reviewed-source/verification/formal/e11be54ba8bbfef1085efff0262fe51fa8ed6bf150af193adf433a74e64febe1/receipt.json) · [receipt.json](materials/reviewed-source/verification/formal/42f471b6b8f76c0b78c3f1414a7e39c02a3375dcc3718892aa820903d4199f4a/receipt.json) · [SunBeta.lean](materials/reviewed-source/submitted-evidence/workspace/proof/SunBeta.lean)

**Literature** (39): [0a8dfd10fa2a0ef9a1bc489b0466ef96bd4d3239410acb652287bb93add8b2b2.json](materials/reviewed-source/literature/receipts/0a8dfd10fa2a0ef9a1bc489b0466ef96bd4d3239410acb652287bb93add8b2b2.json) · [23c57e5cd3f86f980bf15a2b3f09b6a10c853ca9f4675f854fc494b36a02311a.json](materials/reviewed-source/literature/receipts/23c57e5cd3f86f980bf15a2b3f09b6a10c853ca9f4675f854fc494b36a02311a.json) · [27d96150139d45ac0d761880d03af7dcdde21e736dea6016fa7af52f73c43f54.json](materials/reviewed-source/literature/receipts/27d96150139d45ac0d761880d03af7dcdde21e736dea6016fa7af52f73c43f54.json)

The manifest lists every captured path, hash and omitted item.

- This is an editorial reconstruction of visible saved evidence, not hidden reasoning, an independent mathematical verification, or a certification of novelty.

- reviewed-source: only saved answers, named notes, proof/formal files and source receipts are included; arbitrary workspace files, binaries and caches are excluded.

- solver-source: only saved answers, named notes, proof/formal files and source receipts are included; arbitrary workspace files, binaries and caches are excluded.

- The linked solver is frozen at the revision shown in this manifest, which may include work saved after the review. The original reviewed candidate is matched exactly; later work is not retroactively verified.

[frozen-dossier]: materials/reviewed-source/dossier.json

[mathlottery-expert-brief-v2-end]: #

---

## Full editorial report

**Sun’s beta polynomials: coefficientwise log-convexity — an exposition of the frozen candidate and reviews**

**Expert entry.** The exact problem is to prove, for the formal variable \(q\),
\[
\beta_n(q)=\sum_{k=0}^{n}\binom nk^2\binom{n+k}{k}q^k\in\mathbb Z[q],
\qquad
C(n,d):=[q^d]\bigl(\beta_{n-1}(q)\beta_{n+1}(q)-\beta_n(q)^2\bigr)\ge0
\tag{T}
\]
for **every integer \(n\ge1\) and every integer \(d\ge0\)**, with \(\beta_0=1\). The candidate claims the entire statement, including \(n=1\), degrees \(0,1,2n-1,2n\), and the zero coefficients beyond \(2n\). It is not restricted to a branch, a finite range, or values of a real parameter.

| Question | Exact conclusion supported by the frozen record |
|---|---|
| What was formally established? | The declaration `SunBeta.beta_coeffwise_logconvex`, with the displayed universal quantifiers and integer polynomial coefficients, has a matching controller receipt with status `KERNEL_REPLAYED`. |
| What does the mathematical review say? | The final saved review is `NO_ISSUES_FOUND`, with original-problem coverage `FULL` and no remaining mathematical obligations. These are the saved LLM review’s judgments. |
| What remains uncertified? | The receipt says `statement_alignment=NOT_CERTIFIED`; novelty remains `UNKNOWN`; there is no external expert endorsement or certification of priority. The candidate’s stored level remains `PARTIALLY_VERIFIED`. |
| What historical uncertainty must remain visible? | The Problem record has `scope_relation=UNKNOWN`. Earlier saved review coverage is `UNKNOWN`, then `PARTIAL`; both earlier verdicts are `INCONCLUSIVE`. Later evidence does not rewrite those records. |
| What is the weakest link for an expert audit? | The substantial algebra is the two complete positive-coefficient identities in Lemma 7. Their Lean versions are included in the successful module replay. The less fully certified link is the correspondence between the written Cramer formulas, expanded Lean constants, and original natural-language statement: the review supports it, but no external equivalence certificate is present, and its detailed algebra scripts/logs are absent from this bundle. |

The decisive starting materials are the [submitted proof and full tables](materials/reviewed-source/submitted-evidence/workspace/proof/Proof.md), [exact Lean source](materials/reviewed-source/submitted-evidence/workspace/proof/SunBeta.lean), [successful formal receipt F1](materials/reviewed-source/verification/formal/42f471b6b8f76c0b78c3f1414a7e39c02a3375dcc3718892aa820903d4199f4a/receipt.json), and [review dossier](materials/reviewed-source/dossier.json). Known neighboring results concern the type-B Narayana, \(S_n\), Domb, Zhu–Sun, Hoggatt, and Baxter polynomials; the saved comparisons do not identify any as a proof of this exact beta statement. Sun’s dated 2026-02-10 text still calls it open. Correctness evidence and novelty evidence must therefore be read separately.

**1. Abstract, provenance, and editorial scope.**

The submitted argument converts each coefficient into a symmetric weighted convolution. Two corrections have exactly zero sum along a finite antidiagonal. Suitable coefficients for these corrections annihilate the two central positions; the remaining interior terms factor into nonnegative factors and two polynomials with respectively 334 and 415 positive integer coefficients. Separate certificates cover all boundary cases. The proof thus addresses unbounded indices by polynomial identities, not by extrapolating finite tests.

This report faithfully reorganizes the saved proof, adds explicit explanations of transitions already present in the proof/review, and reproduces the complete certificate data. Lemma numbers and positional check labels below are editorial. No new mathematical repair, new verification, new literature search, or reconstruction of hidden reasoning is being submitted. Where only a review’s account survives, that evidence level is stated. Both language editions use the same frozen source snapshot.

The selected reviewed dossier is frozen at revision 26, captured on 2026-10-25. Its `review_source` explicitly links the solver dossier at revision 9; the candidate hash and proof text agree. Thus the [linked solver dossier](materials/solver-source/dossier.json) is admissible provenance, not a history inferred from a matching title or hash. Both dossiers have empty `visible_research_notes` arrays. The manifest warns that a linked solver snapshot can contain later saved work; only the exact submitted candidate and its matching receipts carry the recorded review. The six submitted proof attachments also agree with the linked copies. File agreement identifies bytes, not truth.

The specified original source is Sun, *Some new series for \(1/\pi\) and related congruences*, Conjecture 4.7, first polynomial, in the 2014-12-24 version [B1](https://arxiv.org/html/1104.3856v8). Its preceding definition requires every coefficient of the adjacent product difference to be nonnegative. A separate 2014-12-29 text records the author’s retrospective attribution to 2011-05-07 [B3](https://arxiv.org/html/1102.5649v47). We retain the specified 2014 provenance without claiming that 2014 was the first proposal date or independently authenticating the 2011 event. The 2026-02-10 version of *A family of polynomials and related congruences and series* repeats the exact beta definition and says it “remains open” [B2](https://arxiv.org/html/2505.02767v4). A download in October does not extend that dated statement to October.

**2. Notation, assumptions, and proof dependencies.**

Throughout, \(n,k,l,d,m,r,j\) denote integers in the ranges explicitly specified. Binomial coefficients with \(k>n\) are zero. Put \(a_{n,k}=\binom nk^2\binom{n+k}{k}\) for \(n,k\ge0\), including that zero convention. The original coefficients are integers; the auxiliary weights and polynomial computations are in \(\mathbb Q\). Thus expressions such as \(n-k\) or \(l-1\) use ordinary subtraction, not truncated natural-number subtraction. In particular, \(q\) is never evaluated at a number.

The notation \(\sum_{k+l=d}\) always sums over all **ordered** pairs \((k,l)\in\mathbb N^2\). Sorting a pair is used only to prove a symmetric summand nonnegative; it does not change the convolution’s multiplicities. The auxiliary \(c_0,c_1,D\) may depend on \(n,d\), but must be constant across that antidiagonal.

The dependency structure is:
\[
\begin{gathered}
\text{Lemma 1}\longrightarrow\text{Lemmas 2 and 3},\\
\text{Lemma 4}+\text{Lemma 5}+\text{Lemma 6}+\text{Lemma 7}
\longrightarrow\text{a nonnegative corrected summand},\\
\text{Lemmas 2 and 3}+\text{that certificate}
\longrightarrow\text{Lemma 8}\longrightarrow\text{Theorem 1}.
\end{gathered}
\]
No neighboring literature theorem is a premise of this proof. The material in Sections 3–4 is an exposition of the submitted proof and its recorded review, not an additional verification verdict.

**3. Detailed exposition of the submitted proof.**

**Lemma 1 (weights and recurrences).** Fix \(n\ge1\), and define for every \(k\ge0\)
\[
b_k=\frac{a_{n+1,k}}{(n+1)(n+k)(n+k+1)}\ge0.
\]
The denominator is strictly positive. The support is \(0\le k\le n+1\), and
\[
\begin{aligned}
a_{n+1,k}&=(n+1)(n+k)(n+k+1)b_k,\\
a_{n,k}&=(n+k)(n-k+1)^2b_k,\\
n a_{n-1,k}&=(n-k)^2(n-k+1)^2b_k,\\
(k+1)^3b_{k+1}&=(n+k)(n-k+1)^2b_k.
\end{aligned}\tag{1}
\]
For the supported indices, the factorial representations used in the review are
\[
a_{n,k}=\frac{n!(n+k)!}{k!^3(n-k)!^2}\quad(k\le n),
\qquad
b_k=\frac{n!(n+k-1)!}{k!^3(n+1-k)!^2}\quad(k\le n+1).
\]
Cancellation gives (1) in the interior. These factorial expressions are not used with negative factorial arguments. At \(k=n\), the factor \((n-k)^2\) handles the lower row; at \(k=n+1\), \((n-k+1)^2=0\) handles the middle/lower rows and the column recurrence. For \(k>n+1\), all relevant weights vanish. This explains why no division by \(n-k\) is permissible or necessary. The Lean proof instead uses binomial identities with explicit zero cases (`choose_row`, `choose_col`, `choose_rising`, `a_row`, `a_col`, and `w_*`). The written \(b_k\) is `w n k`. Recorded check: R3.C02.

**Lemma 2 (symmetric coefficient identity).** Define
\[
\begin{aligned}
A(n,k,l)&=(n+k)l^3(n-k+1)^2,\\
P(n,k,l)&=(n+1)\bigl((n+l)(n+l+1)(n-k+1)^2(n-k)^2\\
&\qquad +(n+k)(n+k+1)(n-l+1)^2(n-l)^2\bigr)\\
&\qquad-2n(n+k)(n+l)(n-k+1)^2(n-l+1)^2,\\
T_0(n,k,l)&=(k-l+1)A(n,k,l)-(k-l-1)A(n,l,k),\\
T_1(n,k,l)&=(k-l+1)A(n,k,l)k(l-1)\\
&\qquad-(k-l-1)A(n,l,k)(k-1)l.
\end{aligned}\tag{2}
\]
The polynomials \(P,T_0,T_1\) are symmetric in \(k,l\). Substituting (1) gives the termwise equality
\[
b_kb_lP(n,k,l)
=n\bigl(a_{n-1,k}a_{n+1,l}+a_{n+1,k}a_{n-1,l}-2a_{n,k}a_{n,l}\bigr).
\]
The two mixed sums are equal by the bijection \((k,l)\mapsto(l,k)\). The polynomial multiplication formula then gives
\[
2nC(n,d)=\sum_{k+l=d}b_kb_lP(n,k,l).\tag{3}
\]
The diagonal \(k=l\) requires no exceptional half-weight: the symmetrization was performed on the full ordered sum. This accounts for the factor \(2n\), a necessary normalization in the final step. Recorded check: R3.C03; Lean `paired_term`, `delta_sum`, `beta_coeff`, `delta_coeff`.

**Lemma 3 (zero-sum corrections).** For arbitrary fixed \(c_0,c_1\in\mathbb Q\), let
\[
G(i,j)=b_i b_j i^3j^3(i-j)\bigl(c_0+c_1(i-1)(j-1)\bigr).
\]
The last recurrence in (1), once at \(k\) and once at \(l\), yields
\[
b_kb_l\bigl(c_0T_0(n,k,l)+c_1T_1(n,k,l)\bigr)
=G(k+1,l)-G(k,l+1).
\]
Both sums on the right range over \(i+j=d+1\); the first omits \(i=0\), and the second omits \(j=0\). Their difference is therefore \(G(d+1,0)-G(0,d+1)=0\), since \(G\) contains \(i^3j^3\). This also covers \(d=0\). Hence
\[
\sum_{k+l=d}b_kb_l(c_0T_0+c_1T_1)=0.\tag{4}
\]
The correction coefficients need not be nonnegative. What matters is that they are independent of \(k,l\). Consequently, it suffices to find \(D>0,c_0,c_1\) such that
\[
Q(n,k,l):=DP(n,k,l)+c_0T_0(n,k,l)+c_1T_1(n,k,l)\ge0\tag{5}
\]
on the support of \(b_kb_l\). Recorded check: R3.C04; Lean `flux_sum`, `weighted_flux`, `weighted_telescopes`.

**Lemma 4 (exhaustive parameterization).** If \(d>2n\), both products in (T) have zero coefficient at degree \(d\), since \(\deg\beta_s\le s\). For \(0\le d\le2n\), write uniquely
\[
d=2m+\varepsilon,\qquad n=m+r+\varepsilon,
\qquad \varepsilon\in\{0,1\},\quad m,r\ge0.
\]
For odd \(d\), the inequality \(2m+1\le2n\) gives \(m\le n-1\), so \(r\ge0\) in that case as well. By symmetry it suffices to inspect supported pairs with \(k\le l\). Such pairs have
\[
k=m-j,\qquad l=m+j+\varepsilon,
\qquad 0\le j\le m,\quad j\le r+1.\tag{6}
\]
Indeed, take \(j=m-k\); ordering gives \(k\le m\), and \(l\le n+1\) gives the last bound. The use of support \(n+1\), rather than \(n\), is essential because the weights come from \(a_{n+1,k}\). Put \(U_j=P(n,k,l)\), \(V_j=T_0(n,k,l)\), and \(W_j=T_1(n,k,l)\) after this substitution. Recorded check: R3.C05; Lean `sorted_suffices`, `exists_certificate`, and the high-degree branch of `delta_nonneg`.

**Lemma 5 (all small and top-degree boundaries).** If \(m=0\), take \(D=1,c_0=c_1=0\). For \(\varepsilon=0\), the only pair is \((0,0)\), and \(P(n,0,0)=0\). For \(\varepsilon=1\), the ordered representative is \((0,1)\), and
\[
P(n,0,1)=2n^2(n+1)^2(3n+1)>0.
\]
Now let \(m\ge1\), and suppose \(m=1\) or \(r=0\). Bounds (6) force \(j\in\{0,1\}\). Take \(c_1=0\) and
\[
\begin{array}{c|c|l}
\varepsilon&D&c_0\\\hline
0&m^2&4mr+2m+3r^2+3r\\
1&m^3&4m^2r+4m^2+3mr^2+4mr-2m-3r^2-10r-8.
\end{array}\tag{7}
\]
Here \(D>0\). Direct polynomial identities give \(DU_0+c_0V_0=0\), and
\[
\begin{array}{c|c|l}
\varepsilon&\text{condition}&DU_1+c_0V_1\\\hline
0&m=1&2(r+1)(r+2)^2(3r^2-3r+4)\\
0&r=0&8m(m+1)^2\\
1&m=1&36(r+2)(r+3)^2(2r^2+9r+14)\\
1&r=0&144m(m+2)^2(3m+4).
\end{array}\tag{8}
\]
All are nonnegative. For the sole factor with a negative coefficient, use
\[
4(3r^2-3r+4)=3(2r-1)^2+13>0.
\]
This handles \(d=0,1\), the small half-degrees \(m=1\), and \(d=2n,2n-1\) through \(r=0\); overlaps cause no additional case. Recorded check: R3.C06; Lean `edgeExprEven_*`, `edgeExprOdd_*`, `even_edge`, `odd_edge`, and the \(m=0\) branches of `certificate_even`/`certificate_odd`.

**Lemma 6 (interior constants).** It remains to treat \(m\ge2,r\ge1\). Set
\[
D_0=3m^2r^2(m-1)^3(2m+r+1),\qquad
D_1=3m^3r^2(m-1)^3(2m+r+3).\tag{9}
\]
Every factor is positive in this domain. With \(H=V_0W_1-V_1W_0\), the submitted identities are
\[
\begin{aligned}
H\bigm|_{\varepsilon=0}&=-12m^3r^2(m-1)^3(2m+r)(r+1)^2(2m+r+1),\\
H\bigm|_{\varepsilon=1}&=-24m^3r^2(m-1)^3(r+1)^2(2m+r+2)(2m+r+3).
\end{aligned}\tag{10}
\]
Thus \(H<0\), so the two linear equations
\(DU_0+c_0V_0+c_1W_0=0\) and \(DU_1+c_0V_1+c_1W_1=0\) have the solution
\[
c_0=D_\varepsilon\frac{U_1W_0-U_0W_1}{H},\qquad
c_1=D_\varepsilon\frac{V_1U_0-V_0U_1}{H}.\tag{11}
\]
This construction explains why the central positions \(j=0,1\) vanish and why the constants do not depend on the summation index. The submitted proof states that after simplification both constants are in \(\mathbb Z[m,r]\). Their expanded expressions are saved as `alpha` and `beta` in [certificates.json](materials/reviewed-source/submitted-evidence/workspace/proof/certificates.json) and as `alphaEven`, `betaEven`, `alphaOdd`, `betaOdd` in Lean. These auxiliary names `betaEven`/`betaOdd` do not denote the original polynomial sequence.

R3.C07 reports exact checks of (10), of the Cramer solution, and of its agreement with the expanded data, including checks of the identities after multiplication by \(H\). The formal source uses those expanded constants directly: it does not introduce a named theorem asserting (10) or the Cramer-to-expanded-expression correspondence. Its separate `exprEven_0`, `exprEven_1`, `exprOdd_0`, `exprOdd_1` prove the two vanishing conditions by `ring`. This is a real distinction between the written derivation and the formal implementation, not a missing hypothesis silently supplied by this report.

**Lemma 7 (the complete interior certificate).** For the constants of Lemma 6, the submitted identities are
\[
\begin{aligned}
D_0U_j+c_0V_j+c_1W_j
&=2j^2(j^2-1)E_0(m-j,r+1-j,j-2),\\
D_1U_j+c_0V_j+c_1W_j
&=2j(j-1)(j+1)(j+2)E_1(m-j,r+1-j,j-2).
\end{aligned}\tag{12}
\]
The first line uses the even constants and the second the odd constants. Appendix D gives **all** coefficients of \(E_0,E_1\in\mathbb Z[u,v,t]\): each row \((a,b;c_0,\ldots,c_s)\) means \(u^av^b\sum_{h=0}^s c_ht^h\), with unlisted terms zero. Here the table’s \(c_h\) are local coefficient labels, unrelated to the correction constants. The polynomials have respectively 334 and 415 nonzero terms; the review records total degrees 11 and 12 and minimum nonzero coefficient 36 for each. All listed coefficients are positive integers.

These are finite polynomial identities, not a finite collection of sampled values. An audit can substitute (2), (9), (11), clear the already nonzero \(H\), and compare coefficients with the complete tables. R3.C08 reports two such exact algorithms: SymPy reconstruction and an independent sparse polynomial implementation using integer addition and multiplication. Both reported zero remainders and agreement among the submitted proof, table, JSON, and Lean definitions. Their scripts/results are not frozen here; their reported outcomes are retained as review evidence. F1 separately records successful compilation and kernel replay of the module containing `identityEven` and `identityOdd`.

In Lean these identities are expressed after the inverse substitution
\[
m=u+t+2,\qquad r=v+t+1,\qquad j=t+2.
\]
The certificate polynomials are `posEven` and `posOdd`; `positivity` proves their nonnegative values on nonnegative arguments, while `ring` proves the identities. For \(j\ge2\), (6) gives
\[
u=m-j\ge0,\qquad v=r+1-j\ge0,\qquad t=j-2\ge0.
\]
The factors in (12) are then nonnegative. For \(j=0,1\), use Lemma 6 instead; the argument does **not** claim \(j-2\ge0\) there. Hence (5) holds in every interior case. Together with Lemma 5, this supplies \(D>0\) and a certificate for every \(d\le2n\). Recorded checks: R3.C07–C09; formal declarations include `exprEven_nonneg`, `exprOdd_nonneg`, `even_internal`, `odd_internal`, `certificate_even`, `certificate_odd`, and `exists_certificate`.

**Lemma 8 (return to the integer coefficient).** Multiply (5) by \(b_kb_l\ge0\) and sum over the full antidiagonal. Unsupported pairs contribute zero. Since the same constants are used throughout the sum, (4) removes the corrections and (3) gives
\[
0\le\sum_{k+l=d}b_kb_lQ(n,k,l)
=D\sum_{k+l=d}b_kb_lP(n,k,l)
=2nD\,C(n,d).\tag{13}
\]
For \(n\ge1\) and \(D>0\), \(2nD>0\), so \(C(n,d)\ge0\). The case \(d>2n\) was already handled by Lemma 4. Although (13) is an inequality in \(\mathbb Q\), its \(C(n,d)\) is the image of an integer coefficient; the order-preserving embedding \(\mathbb Z\hookrightarrow\mathbb Q\) gives exactly the required integer inequality. Recorded check: R3.C09. In Lean, `sumP_nonneg` combines the certificate and telescoping, `delta_nonneg` treats both degree regimes, `delta_coeff` identifies the coefficient, and `logconvex_step` returns to \(\mathbb Z\).

**Theorem 1 (the submitted conclusion, with recorded formal support).** Statement (T) holds under its stated assumptions according to the submitted proof, the final mathematical review, and the successful formal receipt for its formal declaration. The formal proof first uses a nonnegative lower index \(s\) and adjacent rows \(s,s+1,s+2\). Setting \(s=n-1\), the hypothesis \(1\le n\) justifies \(n-1+1=n\) and \(n-1+2=n+1\). The saved main declaration is

```lean
theorem SunBeta.beta_coeffwise_logconvex (n : ℕ) (hn : 1 ≤ n) (d : ℕ) :
  0 ≤ (SunBeta.beta (n-1) * SunBeta.beta (n+1) - SunBeta.beta n ^ 2).coeff d
```

Its definition is

```lean
noncomputable def SunBeta.beta (n : ℕ) : Polynomial ℤ :=
  ∑ k ∈ Finset.range (n+1),
    Polynomial.monomial k ((n.choose k : ℤ)^2 * ((n+k).choose k : ℤ))
```

This presentation does not promote the stored candidate level or certify the natural-language interpretation of the declaration.

**4. Original-problem coverage and additional claims.**

| Facet | Comparison in the frozen evidence | Limitation |
|---|---|---|
| Definition | The finite sum has exactly \(\binom nk^2\binom{n+k}{k}\), with \(k=0,\ldots,n\). | It is not the Narayana, \(S_n\), Domb, or rising-binomial weight. |
| Quantifiers and domain | `n : ℕ`, `hn : 1 ≤ n`, arbitrary `d : ℕ`; coefficients in `ℤ`. | No upper bound on either index, and no numerical substitution for \(q\). |
| Subtraction | Polynomial subtraction is in `Polynomial ℤ`; coefficient comparison is in `ℤ`. | Only the row index \(n-1\) uses natural subtraction, protected by `hn`. |
| Lowest cases | \(n=1\), \(\beta_0\), \(d=0,1\) occur in the same proof. | The theorem does not request a center \(n=0\). |
| Top and excess degrees | \(r=0\) covers \(2n,2n-1\); support handles \(d>2n\). | Ordinary coefficientwise log-convexity is the stated conclusion. |
| Semantic correspondence | R3.C01 and the saved statement probe support the comparison; latest review coverage is `FULL`. | The formal receipt remains `NOT_CERTIFIED` for statement alignment; no external expert equivalence evidence is supplied. |

R3.C10 records the following further boundary calculations:
\[
\begin{aligned}
C(n,0)&=0, & C(n,1)&=6n+2,\\
C(n,2n)&=\frac{\binom{2n}{n}^{\!2}}{(2n-1)(n+1)}>0,\\
\beta_0\beta_2-\beta_1^2&=8q+2q^2,\\
\beta_1\beta_3-\beta_2^2&=14q+6q^2+56q^3+4q^4.
\end{aligned}\tag{14}
\]
The review obtains \(C(n,1)\) from the second difference of \(a_{n,1}=n^2(n+1)\), and the top coefficient from the neighboring central binomial coefficients. These equalities and strict inequalities are saved derivation claims, **not separately requested or inspected Lean theorems** in F1. The main formal theorem asserts nonnegativity only. The proof also explains the zero coefficients for \(d>2n\), but no separately named universal equality-classification theorem is certified. No complete characterization of equality, strong \(q\)-log-convexity, parameter generalization, or optimality result is submitted or inferred here.

**5. Recorded checks and historical verdicts.**

All review `checks[].id` strings are empty, and `proof_steps` and `statement_alignment` arrays are empty. Thus **R3.C01–R3.C17 are editorial positional locators**, not original system check IDs: R3 means the third saved review, and C01 means its first `checks` element, i.e. `candidates[0].reviews[2].checks[0]` in the [dossier](materials/reviewed-source/dossier.json). R1 and R2 similarly denote the earlier reviews.

| Locator | Claim or proof dependency | Saved method/result |
|---|---|---|
| R3.C01 | Definition, quantifiers, integer coefficients; Theorem 1 and Section 4 | `DERIVATION / SUPPORTED` |
| R3.C02 | Weight recurrences and support; Lemma 1 | `DERIVATION / SUPPORTED` |
| R3.C03 | Symmetrized convolution and factor \(2n\); Lemma 2 | `DERIVATION / SUPPORTED` |
| R3.C04 | Zero-sum endpoints and fixed constants; Lemma 3 | `DERIVATION / SUPPORTED` |
| R3.C05 | Degree split and all parameter ranges; Lemma 4 | `DERIVATION / SUPPORTED` |
| R3.C06 | All boundary certificates; Lemma 5 | `DERIVATION / SUPPORTED` |
| R3.C07 | \(H\ne0\), \(D>0\), Cramer constants and expanded expressions; Lemma 6 | `DERIVATION / SUPPORTED` |
| R3.C08 | Both complete polynomial identities and 749 coefficients; Lemma 7 | `DERIVATION / SUPPORTED` |
| R3.C09 | Nonnegative sum and division by \(2nD\); Lemma 8 | `DERIVATION / SUPPORTED` |
| R3.C10 | Extra boundary equalities (14) | `DERIVATION / SUPPORTED` |
| R3.C11 | Finite exact convolution and recurrence tests | `FINITE_TEST / SUPPORTED` |
| R3.C12 | Original sources and neighboring theorem comparisons | `REFERENCE / SUPPORTED` |
| R3.C13 | The rising-binomial counterexample concerns a different family | `COUNTEREXAMPLE / SUPPORTED` |
| R3.C14 | Reviewer-local compilation, statement probe, and replay history | `FORMAL / SUPPORTED`, recorded narrative; detailed logs absent |
| R3.C15 | Matching successful controller receipt F1 | `FORMAL / SUPPORTED`, receipt present |
| R3.C16 | Corrected source roles and publisher replacement for EMIS | `REFERENCE / SUPPORTED` |
| R3.C17 | Independent source verification of the MathOverflow answer | `REFERENCE / UNRESOLVED`, nonblocking for the mathematical proof |

The first nine checks and R3.C14–C15 are marked blocking in the saved review; the other checks are nonblocking. In R2, C15 was still `UNRESOLVED`; R3 records its resolution using F1. C17 remains unresolved. The `SUPPORTED` labels above quote the record; they are not new results of this editorial session.

| Saved state | Verdict: reported → stored | Novelty: reported → stored | Stored original-problem coverage |
|---|---|---|---|
| Solver candidate | No independent review yet; `scope=COMPLETE`, level `CANDIDATE` | No certification | Candidate claims full scope |
| R1 | `NO_ISSUES_FOUND → INCONCLUSIVE` | `POTENTIALLY_NEW → KNOWN` | `UNKNOWN` |
| R2 | `INCONCLUSIVE → INCONCLUSIVE` | `UNKNOWN → UNKNOWN` | `PARTIAL` |
| R3 | `NO_ISSUES_FOUND → NO_ISSUES_FOUND` | `UNKNOWN → UNKNOWN` | `FULL` |
| Selected candidate at freeze | Level `PARTIALLY_VERIFIED`, `scope=COMPLETE` | Latest review `UNKNOWN` | Historical states retained |

R1’s stored `KNOWN` is not evidence of a previous solution: the subsequent review explicitly corrected three citations that had wrongly classified original conjectures/open-status statements as `PRIOR_RESULT`. An `EQUIVALENT` statement can be the same conjecture without being an established theorem. R1 validation notes also state that the blocking formal check lacked a successful independent execution receipt and that full coverage required supported comparison to the original statement.

R2 retained favorable mathematical reasoning but had no successful retry receipt when its text was written. Its stored `PARTIAL` and validation note (“Full coverage conflicts with the candidate scope or remaining obligations”) must not be overwritten by its prose’s semantic `FULL` claim. Its two listed obligations concerned the controller retry and the MathOverflow source. The successful receipt was subsequently attached to R2, so the frozen object contains both the earlier inconclusive narrative and the later success; R3 explicitly reconciles them. R3 has no remaining mathematical obligations, while the specific literature gap stays in `literature_search.unresolved`.

All three legacy `proof_coverage` objects still contain `proof_complete=false`, `statement_aligned=false`, `formal_alignment_certified=false`, zero step counts, and no assessed timestamp. They are not newly populated proof-coverage certificates. The Problem’s original `scope_relation=UNKNOWN` is also unchanged. These fields coexist with the latest review’s `FULL`; this report preserves the distinction instead of synthesizing an upgraded status.

**6. What Lean actually checked, and what the receipts do not establish.**

F0 denotes the [first controller receipt](materials/reviewed-source/verification/formal/e11be54ba8bbfef1085efff0262fe51fa8ed6bf150af193adf433a74e64febe1/receipt.json); F1 denotes the [successful retry](materials/reviewed-source/verification/formal/42f471b6b8f76c0b78c3f1414a7e39c02a3375dcc3718892aa820903d4199f4a/receipt.json). Both requested exactly one file, `workspace/proof/SunBeta.lean`, with `module_root=proof`, and exactly one declaration, `SunBeta.beta_coeffwise_logconvex`.

| Record | Actual saved outcome | Evidential use |
|---|---|---|
| Solver’s local manifest | `COMPILED`, exit 0; `independent_verify=NOT_RUN` | A solver-local claim, not the independent controller receipt. |
| Reviewer’s first local compile | 900-second external timeout | A failed attempt; never counted as success. |
| Reviewer’s second local compile | Reported exit 0 in 426.962 s | Review narrative; the raw compile log is absent here. |
| Reviewer’s separate statement probe | Reported exit 0 in 19.833 s | Its source survives, but its raw execution log and a separate controller receipt do not. |
| Reviewer’s local `leanchecker` | Reported exit 0 in 93.236 s | Review narrative of a replay, not a substitute for F1. |
| F0, 2026-10-23 07:22:31 UTC | `ERROR`; compilation exit 1 in 207.363 s; no inspected declarations | Lean threshold 8192 MiB. The review attributes the failure to kernel memory errors in `identityEven`/`identityOdd`; F0 itself gives the generic compilation-failure reason. |
| F1, 2026-10-23 07:46:45 UTC | `KERNEL_REPLAYED`; compile 534.384 s, replay 100.352 s, inspection 41.802 s; all exit 0 | Matching source/candidate receipt, with Lean threshold 16384 MiB, address-space limit 24576 MiB, 1800-second configured limit, and one thread. These limits are not measured peak RSS. |

F1 records Lean 4.35.0, commit `eb6cafb7290e8bd5f2937522d8d804f58f02bafc`, and an object of 570766176 bytes. Its inspected declaration has only the axioms `propext`, `Classical.choice`, and `Quot.sound`; no `sorryAx` appears in that list. This is a recorded compiler/kernel result, not an instruction that has merely been proposed. It trusts the installed Lean kernel and imported libraries, not an independently implemented kernel. It does not certify originality, semantic equivalence to prose, or every extra equality in Section 4.

The relevant identifiers are kept separate:

| Hash domain | SHA-256 / fingerprint |
|---|---|
| Candidate, as bound by both formal receipts and the dossier | `87fe6633c0cb96ba88f5883d98ecef69a16abec88035d296e2f4f9f25b15fbf9` |
| Submitted Lean source bytes | `5664f90350aa84b61f78d8bcc10741591852bc1572f5dbc3f1fb9c0675170aa3` |
| UTF-8 `Problem.statement`, used by formal receipts | `50b6ca7a1c36b480c5c7b20b8b07d789a08b70d6b29b119b1c25bdbc2bde01b6` |
| Full canonical Problem record, used by the organization manifest | `3d0e93e3a159b0da83e8bee6bce4416f9a6e2aa84a953c5abea9bc3fda99c1b4` |

The last two values hash different inputs; their difference is not a mismatch. The candidate/source values in F1 match this frozen candidate/source. No absent or mismatched receipt is used to support another version. The independent editorial inventory found all 70 manifest-listed files consistent with their listed sizes and hashes; that is only a file-integrity observation. F1’s compile, replay, and inspection log hashes are present in the receipt, but the log bodies are not in this bundle. R3 says it compared those logs at the time; this session cannot redo that comparison from absent bodies.

Appendix C enumerates the 52 named theorem declarations present in the compiled/replayed source. Only the main theorem was specifically requested and individually reported by the inspector. The other entries are module dependencies, not 51 additional separately issued theorem receipts. The saved [StatementProbe.lean](materials/reviewed-source/review-workspaces/candidate-record-002/formal-probes/StatementProbe.lean) contains an anonymous `example` writing out the three original finite sums; its reported success supports a Lean-level restatement, not external natural-language certification.

**7. Experiments, exact algebra checks, and missing evidence.**

| Material or activity | Saved result | What it supports / what is missing |
|---|---|---|
| Earlier feasibility metadata in the Problem | All coefficients for \(n=1,\ldots,80\) reportedly nonnegative; `FindProbes.BetaConjecture` reportedly elaborated | Background only. The named Find experiment/source and its execution receipt are not frozen here; elaborating a statement is not proving it. No independent Find history is imported. |
| R3.C11 direct integer convolution | \(n=1,\ldots,120\), \(d=0,\ldots,2n+2\): 14880 coefficients, zero negatives | Finite-range evidence only. `math.comb` and arbitrary-precision integer arithmetic are described in the review; the test script/results are absent. |
| R3.C11 rational recurrence tests | 4440 exact `Fraction` comparisons, including out-of-support cases | Finite instances of Lemma 1, not its universal proof. |
| R3.C07–C08 exact symbolic checks | Cramer identities, both full polynomial identities, and all 749 coefficients reportedly agree under two algorithms | Unlike finite tests, exact coefficient identities can support universal algebra. Here their outcomes are recorded in the review; the independent scripts/results themselves are absent. |
| Submitted proof, coefficient tables, JSON, and Lean | All are present; main source has matching F1 | The exact mathematical objects needed for a fresh audit survive. |

The missing items include `ReviewNotes.md`, `check_algebra.py`, `check_sparse.py`, their algebra/sparse JSON results, the reviewer’s `run_lean.py`, first/second compilation logs/results, probe/replay logs, correction notes, controller log copies, and the separate source-comparison/search files cited by the reviews. The proof README also refers to local development logs that are absent. The initial Problem’s `research/solver_handoff.md`, `research/experiments.py`, and Find probe are not supplied. Neither dossier supplies visible research notes. Therefore a discovery sequence, failed mathematical approaches before the saved candidate, or contents of those missing files cannot be reconstructed responsibly.

All project-specific source needed by the submitted **single-file** proof is present: it imports only Mathlib/Lean modules, not the development modules. The eight linked development files are preserved for provenance, but do not have separate formal receipts. The installed Lean/mathlib libraries, their compiled dependencies, the generated `.olean`, and `MathLotteryInspector.lean` are not in the frozen export. No complete mathlib dependency lock/revision is supplied. These are limitations of offline reproduction, not evidence of a mathematical defect in the checked declaration.

**8. Prior results, novelty, and the unresolved source obstacle.**

The following comparisons reproduce R3.C12 and R3.C16. All sums in the table run over \(k=0,\ldots,n\). “Different” concerns the visible definitions and theorem parameters; it does not rule out every non-obvious consequence in the literature.

| Established neighboring result | Polynomial or distinguishing feature | Why it is not a direct solution of (T) |
|---|---|---|
| Chen–Tang–Wang–Yang, type-B Narayana, Theorem 1.1 [B4](https://arxiv.org/html/0810.2247v1) | \(W_n(q)=\sum_k\binom nk^2q^k\), coefficientwise log-convex | Missing \(\binom{n+k}{k}\); \(W_1=1+q\), whereas \(\beta_1=1+2q\). |
| Dou–Ren, \(S_n\), Theorem 3.1 [B5](https://arxiv.org/html/1308.2736v2) | \(S_n(q)=\sum_k\binom nk\binom{2k}{k}\binom{2n-2k}{n-k}q^k\), coefficientwise log-convex | The second family in the parallel conjecture; its constant coefficient is \(\binom{2n}{n}\), not 1. |
| Dou–Ren, Domb, Theorem 3.1 [B6](https://arxiv.org/html/1308.2961v1) | \(D_n(q)=\sum_k\binom nk^2\binom{2k}{k}\binom{2n-2k}{n-k}q^k\), coefficientwise log-convex | The third family; both the extra weight and constant coefficient differ. |
| Zhu–Sun, Corollary 2.9 [B7](https://www.combinatorics.org/ojs/index.php/eljc/article/download/v22i3p26/pdf/) | \(P_n(q)=\sum_k\binom nk^2\binom{2k}{k}q^k\), strongly coefficientwise log-convex | \(P_2=1+8q+6q^2\), while \(\beta_2=1+12q+6q^2\). |
| Chern–Shi, Hoggatt, Theorem 1.2 [B8](https://arxiv.org/html/2609.33732v1) | Strong coefficientwise log-convexity for each fixed integer Hoggatt parameter \(h\ge1\); every row has constant and leading coefficient 1 | For \(n\ge1\), beta’s leading coefficient is \(\binom{2n}{n}\). Renaming the paper’s parameter as \(h\) avoids confusion with the target’s degree \(d\). |
| Liu–Mao, Baxter, Theorem 5.1 [B9](https://arxiv.org/html/2608.22258v1) | Coefficients \(B(n,k)=\binom nk\binom{n+1}{k}\binom{n+2}{k}/[\binom{k+1}{k}\binom{k+2}{k}]\); leading coefficient 1 | A different family, also appearing as the Hoggatt parameter-3 case; not beta. |

The Zhu–Sun route has a specific assumption obstacle: Proposition 2.8 requires a fixed input sequence \(f_k(q)\), independent of the outer row \(n\). Taking \(f_k(q)=\binom{n+k}{k}q^k\) violates that requirement. Theorem 2.1 also assumes in condition C1 that the row-generating polynomials already are strongly \(q\)-log-convex; choosing the beta array does not establish C1. The other parallel conjectures, pointwise inequalities for \(q\ge0\), and finite experiments likewise do not establish (T). These are saved methodological obstacles; the successful certificate argument does not use those shortcuts.

One concrete literature-source obstacle remains open. The reviews cite a [MathOverflow answer](https://mathoverflow.net/questions/479301/on-the-polynomials-sum-k-0n-binomnkkm-qk), attributed there to Qiping Zhou on 2026-07-24. Its complete content, authorship, and date were **not independently source-verified by the controller**: the saved status is `UNAVAILABLE`, with `verified_excerpt=false`, because the robots policy could not be verified. That attribution/date are reported metadata, not established here. A local text mentioned by the first review is absent from this export, and no independently verifiable author/publisher replacement was found in the recorded search.

The mathematics of the cited counterexample was separately distinguished in R3.C13. Sun’s 2026 Conjecture 1.1(i), second sentence, concerns
\[
R_n^{(p)}(q)=\sum_{k=0}^{n}\binom{n+k}{k}^{p}q^k,\qquad p\ge2.
\]
The review records, at \(p=5,n=7\),
\[
[q^2]\bigl(R_6^{(5)}R_8^{(5)}-(R_7^{(5)})^2\bigr)
=28^5+7^5\,9^5+45^5-2\,36^5-8^{10}=-499140,
\]
whereas the beta coefficient at \((n,d)=(7,2)\) is recorded as 1316. Thus that calculation does not refute (T). Its object can be identified from the frozen Sun source without authenticating the MathOverflow attribution. The specific source gap nevertheless remains in `literature_search.unresolved` and must not be hidden under generic search limitations. [Sun’s separate conjecture B2](https://arxiv.org/html/2505.02767v4#S1.Thmconjecture1) and the [review dossier](materials/reviewed-source/dossier.json) are the available evidence.

The EMIS access failure is also preserved, but its Zhu–Sun source was subsequently replaced by the original journal PDF, whose excerpt the controller accepted. In the latest assessment, ten of eleven citation entries have verified excerpts; the MathOverflow entry does not. `evidence_assessment.supported` remains false. The empty structured `obstacles` list does not negate the explicit unresolved source string.

The recorded search ends on 2026-10-23, primarily covers public web indexes, arXiv, author/journal sources, and English with some Chinese queries, and does not exhaust databases, languages, unpublished or unindexed work, or non-obvious derivations. Earlier Problem metadata also records incomplete access to the author’s old homepage bibliography and incomplete coverage of possible pre-2014 carriers. No exact beta solution was identified in the saved comparisons, but this is not a proof of first discovery. **Novelty stays `UNKNOWN`; the dated `OPEN` Problem record is not silently changed to `SOLVED` by this editorial report.**

**9. Reproduction instructions and remaining obligations.**

The following are **untested reproduction instructions in this editorial session**, not new execution receipts. Work on a copy of the six submitted proof attachments, placing them in `proof/` in a scratch workspace, and create a `research/` directory for the script’s logs. The saved solver command is

```sh
mkdir -p research
conda run -n mathlottery python proof/check.py
```

The [saved script](materials/reviewed-source/submitted-evidence/workspace/proof/check.py) searches the workspace and its ancestors for existing `.mathlottery/toolchains/mathlib4-v4.35.0` and the associated Lean 4.35.0 installation. It sets `LEAN_PATH` from existing mathlib/package caches, performs no download or build, and exits if the cache is absent. It runs single-threaded compilation with a 900-second external timeout. This reproduces the solver’s compilation procedure, **not automatically the controller’s resource settings or its inspector**.

For an environment already supplying the recorded Lean version and matching imported libraries, with `proof/` and the precompiled dependency directories configured in `LEAN_PATH`, the controller’s compilation/replay shape is

```sh
lean -j 1 -s 65536 -M 16384 -o proof/SunBeta.olean proof/SunBeta.lean
leanchecker SunBeta
```

These commands use executables available on `PATH`; environment preparation and resource availability remain prerequisites. The source already ends with `#print axioms SunBeta.beta_coeffwise_logconvex`. The separately supplied statement probe can be copied into the scratch workspace and run with `lean StatementProbe.lean` after the module is built. Reproducing the exact controller inspection would additionally require its missing `MathLotteryInspector.lean` and environment. A newly reproduced success would be new evidence, not a retroactive alteration of F0 or F1.

For algebra, the audit specification is fully given by (2), (9)–(12), and Appendix D: reconstruct \(U_j,V_j,W_j\), form \(H,c_0,c_1\), clear nonzero denominators, compare both complete polynomials, and check all boundary identities (8). No command is supplied for the absent `check_algebra.py` or `check_sparse.py`, and their runs are not claimed to have been reproduced here.

The latest review records no unresolved **mathematical** proof obligations. Still outstanding are the MathOverflow source verification, external expert assessment of the mathematical exposition and formal/prose correspondence, priority assessment, and the missing artifacts/environment needed for a fully independent reproduction. Any proposed simplification, strengthened theorem, equality classification, or repair would require a new Solve/Verify; none is supplied here.

**10. Bibliography and frozen source carriers.**

The links below identify the versions discussed in the saved evidence; they do not represent new browsing. For the nine available literature texts, this export contains extracted text, not the original HTML/PDF bytes named in source receipts. The hash in a snapshot filename identifies the original carrier; the extracted file has its own manifest hash. These domains must not be compared as if they were the same file. Source receipts certify text matching only, not interpretation or completeness of the search.

- **B1.** Zhi-Wei Sun, *Some new series for \(1/\pi\) and related congruences*, 2014-12-24 version, Conjecture 4.7 and its preceding definition. [Source](https://arxiv.org/html/1104.3856v8); [frozen extracted text](materials/omitted-sources.md#source-1). Role: `ORIGINAL_STATEMENT`; the first family is the exact target.
- **B2.** Zhi-Wei Sun, *A family of polynomials and related congruences and series*, v4, 2026-02-10, *Frontiers in Combinatorics and Number Theory* 2 (2026), 1–22. §1, `#S1.p5.2` supplies the dated beta open-status statement; Conjecture 1.1(i), second sentence, supplies the different rising-binomial family. [Source](https://arxiv.org/html/2505.02767v4); [frozen extracted text](materials/omitted-sources.md#source-9). Roles: `EXPLICIT_OPEN` for beta, `ORIGINAL_STATEMENT` for the different conjecture.
- **B3.** Zhi-Wei Sun, *List of conjectural series for powers of \(\pi\) and other constants*, v47, 2014-12-29, end of §2 before §3, the paragraph beginning with the retrospective 2011 date. [Source](https://arxiv.org/html/1102.5649v47); [frozen extracted text](materials/omitted-sources.md#source-8). Role: `ORIGINAL_STATEMENT`, not a prior proof.
- **B4.** William Y. C. Chen, Robert L. Tang, Larry X. W. Wang, Arthur L. B. Yang, *The q-Log-convexity of the Generating Functions of the Squares of Binomial Coefficients*, preprint v1, 2008-10-13, Theorem 1.1; the Problem also cites the 2010 journal version under the title *The q-Log-convexity of the Narayana Polynomials of Type B*. [Preprint source](https://arxiv.org/html/0810.2247v1); [frozen extracted text](materials/omitted-sources.md#source-5). Role: `PRIOR_RESULT`, `DIFFERENT`. The separately cited author-hosted PDF is not in this export.
- **B5.** Donna Q. J. Dou and Anne X. Y. Ren, *On the q-log-convexity conjecture of Sun*, v2, 2013-08-15, definition (1.1) and Theorem 3.1. [Source](https://arxiv.org/html/1308.2736v2); [frozen extracted text](materials/omitted-sources.md#source-7). Role: `SOLUTION` of the different \(S_n\) conjecture. The earlier PDF connection failure is noted in the Problem metadata; the same-version HTML was its replacement.
- **B6.** Donna Q. J. Dou and Anne X. Y. Ren, *The q-log-convexity of Domb’s polynomials*, v1, 2013-08-13, definition (1.1) and Theorem 3.1. [Source](https://arxiv.org/html/1308.2961v1); [frozen extracted text](materials/omitted-sources.md#source-3). Role: `SOLUTION` of the different Domb conjecture; the earlier separately cited PDF is absent.
- **B7.** Bao-Xuan Zhu and Hua Sun, *Linear transformations preserving the strong q-log-convexity of polynomials*, *Electronic Journal of Combinatorics* 22(3), P3.26, published 2015-08-28, Theorem 2.1, Proposition 2.8, Corollary 2.9. [Journal source](https://www.combinatorics.org/ojs/index.php/eljc/article/download/v22i3p26/pdf/); [frozen extracted text](materials/omitted-sources.md#source-2); [accepted publisher receipt](materials/reviewed-source/literature/receipts/82d6bbfd69a27cd285085018298c3679b5d035b1c2a84765cda3b1a4f0605e9b.json). The [failed EMIS receipt](materials/reviewed-source/literature/receipts/d0c1d40267c5f84382f037c76a3c553343e3380b41dded7bce0848aeef9b4e37.json) remains part of the history. Role: `PRIOR_RESULT`, `DIFFERENT`.
- **B8.** Shane Chern and Wenle Shi, *Strong q-log-convexity of the d-Hoggatt polynomials*, v1, 2026-09-27, Theorem 1.2. [Source](https://arxiv.org/html/2609.33732v1); [frozen extracted text](materials/omitted-sources.md#source-4). Role: `PRIOR_RESULT`, `DIFFERENT`.
- **B9.** Yanxin Liu and Jianxi Mao, *Pfaffian–Toeplitz identities, Schur positivity, and the q-log-convexity of Baxter polynomials*, v1, 2026-08-23, §4 definition and Theorem 5.1. [Source](https://arxiv.org/html/2608.22258v1); [frozen extracted text](materials/omitted-sources.md#source-6). Role: `PRIOR_RESULT`, `DIFFERENT`.
- **B10.** MathOverflow, *On the polynomials \(\sum_{k=0}^n\binom{n+k}{k}^m q^k\)*, answer attributed in the reviews to Qiping Zhou, 2026-07-24. [Reported source](https://mathoverflow.net/questions/479301/on-the-polynomials-sum-k-0n-binomnkkm-qk); [unavailable-source receipt](materials/reviewed-source/literature/receipts/27d96150139d45ac0d761880d03af7dcdde21e736dea6016fa7af52f73c43f54.json). Role: reported `CORRECTION` for a `DIFFERENT` family. No verified complete carrier is frozen; authorship/date/content remain subject to the specific source gap.

**Appendix A. Concise chronology of saved attempts.**

Times are UTC on 2026-10-23. Dossier chronology times are saved task observations, not guaranteed exact start or finish times. These are all the visible saved research/review attempts; hidden intermediate experiments are not reconstructed.

| Saved time or interval | Attempt and result | Surviving evidence |
|---|---|---|
| 05:30 observation; solver dossier updated 06:46 | One saved Solve attempt submits the complete candidate, the zero-sum certificate argument, full tables, and a locally compiled main theorem. No independent Verify yet. | [Solver answer](materials/solver-source/tasks/task-record-004/attempt-record-001/answer.md), [local manifest](materials/solver-source/workspace/proof/manifest.json). |
| 06:50 observation | First review: algebra/support audit, two exact certificate algorithms, finite tests; first local compile times out, second succeeds; probe/replay reportedly succeed. Reviewer reports favorable mathematics and potential novelty. | [R1 answer](materials/reviewed-source/tasks/task-record-002/attempt-record-003/answer.md); R1 in dossier. |
| 07:22 formal receipt; 07:25 source assessment | F0 fails; EMIS and MathOverflow source verification fails. Stored R1 becomes `INCONCLUSIVE`, coverage `UNKNOWN`; mistaken citation roles produce the historical stored `KNOWN`. | F0 and source receipts; R1 validation notes. |
| 07:34 observation | Second review preserves the formal failure, corrects citation roles, substitutes the Zhu–Sun journal source, leaves MathOverflow unresolved, and requests a resource-adjusted retry. | [R2 answer](materials/reviewed-source/tasks/task-record-001/attempt-record-002/answer.md); stored verdict `INCONCLUSIVE`, coverage `PARTIAL`, novelty `UNKNOWN`. |
| 07:46 formal receipt; 07:58 source assessment | Same source succeeds under F1; journal excerpt accepted; MathOverflow remains unverified. | F1 and the second source assessment, attached to the dossier. |
| 07:59 observation; final assessment 08:07 | Third review reads the actual successful receipt/logs without recompiling, confirms matching bytes, and records `NO_ISSUES_FOUND / FULL / UNKNOWN`. Earlier failures remain saved. | [R3 answer](materials/reviewed-source/tasks/task-record-003/attempt-record-004/answer.md); final dossier. |

The earlier Find metadata mentions citation-transcription problems and a PDF connection failure later addressed by original HTML/text carriers. That information is preserved as metadata only; no unlinked Find session, abandoned proof, or unsaved calculation is added to this chronology. The editorial freeze was captured on 2026-10-25; this session performed no new mathematical experiment or Lean compilation.

**Appendix B. Mathematical material index.**

This is a reading guide, not a duplicate of the controller’s deterministic file/handoff index.

| Material | What to inspect |
|---|---|
| [Reviewed dossier](materials/reviewed-source/dossier.json) | Exact candidate, all three reviews, empty check IDs, historical status projections, source assessments and unresolved gap. |
| [Linked solver dossier](materials/solver-source/dossier.json) | Explicitly associated candidate and the single visible Solve attempt; no visible notes. |
| [Proof.md](materials/reviewed-source/submitted-evidence/workspace/proof/Proof.md) | Submitted proof and full coefficient appendix; source of Lemmas 1–8. |
| [CertificateTable.md](materials/reviewed-source/submitted-evidence/workspace/proof/CertificateTable.md), [certificates.json](materials/reviewed-source/submitted-evidence/workspace/proof/certificates.json) | Complete \(E_0,E_1\) coefficients; JSON also supplies expanded correction constants. |
| [SunBeta.lean](materials/reviewed-source/submitted-evidence/workspace/proof/SunBeta.lean) | Exact single-file formal proof; theorem list in Appendix C. |
| [README.md](materials/reviewed-source/submitted-evidence/workspace/proof/README.md), [check.py](materials/reviewed-source/submitted-evidence/workspace/proof/check.py) | Solver-era instructions and compilation procedure; “Verify not run” is historical. |
| [F0](materials/reviewed-source/verification/formal/e11be54ba8bbfef1085efff0262fe51fa8ed6bf150af193adf433a74e64febe1/receipt.json), [F1](materials/reviewed-source/verification/formal/42f471b6b8f76c0b78c3f1414a7e39c02a3375dcc3718892aa820903d4199f4a/receipt.json) | Failed and successful controller checks of the same bytes; log bodies absent. |
| [StatementProbe.lean](materials/reviewed-source/review-workspaces/candidate-record-002/formal-probes/StatementProbe.lean), [reviewer’s source copy](materials/reviewed-source/review-workspaces/candidate-record-002/formal-probes/SunBeta.lean) | Anonymous finite-sum restatement and exact copied source; execution is described in reviews. |
| [Basic](materials/solver-source/workspace/research/lean_modules/Basic.lean), [Convolution](materials/solver-source/workspace/research/lean_modules/Convolution.lean), [Sign](materials/solver-source/workspace/research/lean_modules/Sign.lean), [Beta](materials/solver-source/workspace/research/lean_modules/Beta.lean) | Linked development modules for recurrences, sums, signs, and final theorem; not extra dependencies of the submitted file. |
| [CertificateData](materials/solver-source/workspace/research/lean_modules/CertificateData.lean), [CertificateEven](materials/solver-source/workspace/research/lean_modules/CertificateEven.lean), [CertificateOdd](materials/solver-source/workspace/research/lean_modules/CertificateOdd.lean), [Certificates](materials/solver-source/workspace/research/lean_modules/Certificates.lean) | Development certificate definitions and parity proofs; not separate successful formal receipts. |
| Bibliography B1–B10 | Nine frozen extracted texts and relevant source receipts, including failed retrievals and corrected provenance. |

**Appendix C. Named theorems in the checked module.**

The rows below enumerate source declarations, not independently issued receipts. Every row belongs to the exact `SunBeta.lean` source named in F1. **M** means “inside the compiled/replayed module, not separately requested or individually listed by the inspector”; **T** means “the requested main declaration, individually listed with its type and axioms in F1.” F0 supports none as successfully inspected declarations. Source line numbers are navigation aids; some line references in the historical review prose differ slightly, so declaration names are preferable.

| No. | Fully qualified theorem | Source line | Exposition lemma | Receipt and scope |
|---:|---|---:|---|---|
| 1 | `SunBeta.Cert.P_symm` | 36 | 2 | F1 / M |
| 2 | `SunBeta.Cert.T0_symm` | 38 | 2 | F1 / M |
| 3 | `SunBeta.Cert.T1_symm` | 40 | 2 | F1 / M |
| 4 | `SunBeta.Cert.posEven_nonneg` | 97 | 7 | F1 / M |
| 5 | `SunBeta.Cert.identityEven` | 102 | 7 | F1 / M |
| 6 | `SunBeta.Cert.exprEven_0` | 108 | 6 | F1 / M |
| 7 | `SunBeta.Cert.exprEven_1` | 112 | 6 | F1 / M |
| 8 | `SunBeta.Cert.exprEven_nonneg` | 116 | 7 | F1 / M |
| 9 | `SunBeta.Cert.edgeExprEven_0` | 128 | 5 | F1 / M |
| 10 | `SunBeta.Cert.edgeExprEven_small` | 132 | 5 | F1 / M |
| 11 | `SunBeta.Cert.edgeExprEven_top` | 136 | 5 | F1 / M |
| 12 | `SunBeta.Cert.posOdd_nonneg` | 147 | 7 | F1 / M |
| 13 | `SunBeta.Cert.identityOdd` | 152 | 7 | F1 / M |
| 14 | `SunBeta.Cert.exprOdd_0` | 158 | 6 | F1 / M |
| 15 | `SunBeta.Cert.exprOdd_1` | 162 | 6 | F1 / M |
| 16 | `SunBeta.Cert.exprOdd_nonneg` | 166 | 7 | F1 / M |
| 17 | `SunBeta.Cert.edgeExprOdd_0` | 181 | 5 | F1 / M |
| 18 | `SunBeta.Cert.edgeExprOdd_small` | 185 | 5 | F1 / M |
| 19 | `SunBeta.Cert.edgeExprOdd_top` | 189 | 5 | F1 / M |
| 20 | `SunBeta.a_nonneg` | 208 | 1 | F1 / M |
| 21 | `SunBeta.a_zero` | 210 | 1 | F1 / M |
| 22 | `SunBeta.choose_row` | 213 | 1 | F1 / M |
| 23 | `SunBeta.choose_col` | 223 | 1 | F1 / M |
| 24 | `SunBeta.choose_rising` | 233 | 1 | F1 / M |
| 25 | `SunBeta.a_row` | 240 | 1 | F1 / M |
| 26 | `SunBeta.a_col` | 255 | 1 | F1 / M |
| 27 | `SunBeta.w_nonneg` | 275 | 1 | F1 / M |
| 28 | `SunBeta.w_zero` | 279 | 1 | F1 / M |
| 29 | `SunBeta.w_above` | 282 | 1 | F1 / M |
| 30 | `SunBeta.w_center` | 289 | 1 | F1 / M |
| 31 | `SunBeta.w_below` | 297 | 1 | F1 / M |
| 32 | `SunBeta.w_recur` | 308 | 1 | F1 / M |
| 33 | `SunBeta.Cert.Q_symm` | 328 | 4 | F1 / M |
| 34 | `SunBeta.Cert.sorted_suffices` | 332 | 4 | F1 / M |
| 35 | `SunBeta.Cert.even_internal` | 341 | 7 | F1 / M |
| 36 | `SunBeta.Cert.odd_internal` | 352 | 7 | F1 / M |
| 37 | `SunBeta.Cert.even_edge` | 363 | 5 | F1 / M |
| 38 | `SunBeta.Cert.odd_edge` | 378 | 5 | F1 / M |
| 39 | `SunBeta.Cert.certificate_even` | 392 | 4–7 | F1 / M |
| 40 | `SunBeta.Cert.certificate_odd` | 448 | 4–7 | F1 / M |
| 41 | `SunBeta.Cert.exists_certificate` | 507 | 4–7 | F1 / M |
| 42 | `SunBeta.flux_sum` | 534 | 3 | F1 / M |
| 43 | `SunBeta.weighted_flux` | 547 | 3 | F1 / M |
| 44 | `SunBeta.weighted_telescopes` | 564 | 3 | F1 / M |
| 45 | `SunBeta.paired_term` | 570 | 2 | F1 / M |
| 46 | `SunBeta.delta_sum` | 595 | 2 | F1 / M |
| 47 | `SunBeta.beta_coeff` | 612 | 2 | F1 / M |
| 48 | `SunBeta.delta_coeff` | 631 | 2, 8 | F1 / M |
| 49 | `SunBeta.sumP_nonneg` | 649 | 8 | F1 / M |
| 50 | `SunBeta.delta_nonneg` | 678 | 4, 8 | F1 / M |
| 51 | `SunBeta.logconvex_step` | 703 | 8 | F1 / M |
| 52 | `SunBeta.beta_coeffwise_logconvex` | 712 | T1 | F1 / T |

**Appendix D. Complete positive-coefficient certificates.**

The following is the full mathematical certificate table copied from the frozen submitted attachment. Define
\[
E_\varepsilon(u,v,t)=\sum_{(a,b)\text{ listed}}u^av^b\sum_{h=0}^{s(a,b)}c_{a,b,h}t^h.
\]
Each row lists \(c_{a,b,0},\ldots,c_{a,b,s(a,b)}\); every unlisted coefficient is zero. This is exact integer data for Lemma 7, not an experiment or a raw execution log. Its presence makes the written certificate fully specified without referring to another language edition.

**D.1. E₀: 334 nonzero terms.**

| a | b | (c₀, c₁, …, cₛ) |
|---:|---:|:---|
| 0 | 0 | 677376, 4817664, 15752448, 31053184, 40811488, 37423472, 24381408, 11271744, 3621472, 769904, 97472, 5568 |
| 0 | 1 | 2232000, 14598720, 42968032, 74727488, 84881196, 65721420, 35105636, 12770068, 3027248, 422336, 26336 |
| 0 | 2 | 3135840, 18365648, 47598504, 71570876, 68762040, 43759856, 18444256, 4964956, 774616, 53376 |
| 0 | 3 | 2384972, 12329032, 27714147, 35372215, 28033769, 14127417, 4421244, 785724, 60720 |
| 0 | 4 | 1077986, 4853531, 9299395, 9830169, 6192505, 2325128, 481906, 42540 |
| 0 | 5 | 299184, 1153868, 1839630, 1552380, 731467, 182517, 18846 |
| 0 | 6 | 50180, 162046, 207456, 131635, 41405, 5166 |
| 0 | 7 | 4676, 12236, 11883, 5071, 802 |
| 0 | 8 | 186, 375, 249, 54 |
| 1 | 0 | 2050560, 13398912, 39701632, 69831616, 80413856, 63179256, 34244968, 12633960, 3035096, 428704, 27040 |
| 1 | 1 | 6564720, 38703992, 101167452, 153559634, 148972494, 95720366, 40720822, 11058616, 1739728, 120816 |
| 1 | 2 | 8759356, 45342960, 102181615, 130845045, 104092143, 52671823, 16554738, 2954992, 229376 |
| 1 | 3 | 6195772, 27758884, 53010607, 55925524, 35199519, 13217300, 2741746, 242396 |
| 1 | 4 | 2568207, 9800024, 15495315, 12994632, 6096129, 1516943, 156434 |
| 1 | 5 | 646816, 2054942, 2596364, 1630806, 509243, 63248 |
| 1 | 6 | 97438, 249158, 237354, 99827, 15640 |
| 1 | 7 | 8052, 15710, 10127, 2156 |
| 1 | 8 | 279, 378, 126 |
| 2 | 0 | 2575584, 15328080, 40717800, 63025020, 62424144, 40944120, 17764056, 4913532, 786144, 55440 |
| 2 | 1 | 7947792, 41792808, 95707836, 124501854, 100546000, 51599678, 16431204, 2968484, 232984 |
| 2 | 2 | 9966972, 45015546, 86675772, 92195227, 58496188, 22136979, 4626572, 411980 |
| 2 | 3 | 6473730, 24741894, 39212730, 32982215, 15526402, 3878407, 401618 |
| 2 | 4 | 2431020, 7698904, 9709790, 6095113, 1904130, 236816 |
| 2 | 5 | 549313, 1393828, 1320141, 553049, 86456 |
| 2 | 6 | 73367, 141064, 89869, 18968 |
| 2 | 7 | 5269, 6928, 2254 |
| 2 | 8 | 153, 108 |
| 3 | 0 | 1740528, 9341640, 21963324, 29395494, 24421370, 12875210, 4203506, 776856, 62232 |
| 3 | 1 | 5138856, 23796936, 46921758, 51026186, 33039992, 12737090, 2707018, 244724 |
| 3 | 2 | 5999028, 23242170, 37322515, 31787971, 15142831, 3825131, 400282 |
| 3 | 3 | 3536754, 11274760, 14319181, 9053704, 2849257, 356984 |
| 3 | 4 | 1193973, 3035574, 2883588, 1212541, 190376 |
| 3 | 5 | 240774, 460902, 292841, 61732 |
| 3 | 6 | 28131, 36268, 11618 |
| 3 | 7 | 1680, 1104 |
| 3 | 8 | 36 |
| 4 | 0 | 684288, 3274632, 6705660, 7578432, 5091022, 2030318, 444900, 41328 |
| 4 | 1 | 1919592, 7704432, 12775416, 11200018, 5475082, 1415234, 151156 |
| 4 | 2 | 2064984, 6706668, 8670731, 5575868, 1782995, 226762 |
| 4 | 3 | 1090428, 2807684, 2701848, 1150936, 183026 |
| 4 | 4 | 328611, 635328, 407872, 86890 |
| 4 | 5 | 58044, 75066, 24142 |
| 4 | 6 | 5469, 3548 |
| 4 | 7 | 204 |
| 5 | 0 | 156816, 659952, 1152300, 1062540, 544248, 146676, 16248 |
| 5 | 1 | 415152, 1414008, 1905876, 1271112, 419620, 54872 |
| 5 | 2 | 406788, 1071528, 1055004, 459640, 74700 |
| 5 | 3 | 189240, 374736, 246480, 53776 |
| 5 | 4 | 50592, 67132, 22124 |
| 5 | 5 | 7348, 4848 |
| 5 | 6 | 424 |
| 6 | 0 | 19440, 70704, 102156, 72776, 25480, 3504 |
| 6 | 1 | 48240, 135384, 140600, 64104, 10832 |
| 6 | 2 | 42456, 86200, 58484, 13200 |
| 6 | 3 | 17032, 23888, 8304 |
| 6 | 4 | 4028, 2816 |
| 6 | 5 | 384 |
| 7 | 0 | 1008, 3096, 3536, 1760, 320 |
| 7 | 1 | 2328, 5152, 3744, 896 |
| 7 | 2 | 1808, 2592, 960 |
| 7 | 3 | 608, 512 |
| 7 | 4 | 128 |

**D.2. E₁: 415 nonzero terms.**

| a | b | (c₀, c₁, …, cₛ) |
|---:|---:|:---|
| 0 | 0 | 124720000, 566442000, 1184507700, 1519482970, 1344493322, 873451324, 430902194, 163317598, 47100188, 10006064, 1471616, 133216, 5568 |
| 0 | 1 | 226374000, 958879800, 1869094845, 2231041691, 1827174184, 1085373695, 478683985, 156499484, 36959980, 5957576, 585088, 26336 |
| 0 | 2 | 185042700, 726708435, 1308538027, 1432788254, 1062594894, 559323407, 211426699, 56423154, 10107748, 1089896, 53376 |
| 0 | 3 | 87977490, 316943866, 519559343, 511393623, 334054493, 150133282, 46263156, 9373066, 1125836, 60720 |
| 0 | 4 | 26371830, 85896207, 125804110, 108571233, 60404999, 22123780, 5183139, 705908, 42540 |
| 0 | 5 | 5071020, 14663488, 18748857, 13754255, 6237910, 1740417, 274901, 18846 |
| 0 | 6 | 608240, 1526061, 1654141, 989564, 342765, 64717, 5166 |
| 0 | 7 | 41490, 87646, 77395, 35475, 8359, 802 |
| 0 | 8 | 1230, 2097, 1422, 447, 54 |
| 1 | 0 | 278068000, 1155184600, 2210478490, 2597901992, 2106199322, 1247628114, 552967756, 182821870, 43820640, 7175568, 715200, 32608 |
| 1 | 1 | 478917400, 1867794570, 3351998779, 3674784609, 2741843906, 1457882405, 558033069, 150882526, 27358768, 2980456, 147152 |
| 1 | 2 | 375564390, 1362721166, 2257227514, 2250381025, 1490433269, 678745147, 211531575, 43231650, 5223936, 282752 |
| 1 | 3 | 171449261, 569545994, 851017099, 748033640, 422453295, 156381543, 36865665, 5032816, 303116 |
| 1 | 4 | 49076547, 146266946, 191903040, 143516558, 65866057, 18468753, 2915465, 198974 |
| 1 | 5 | 8931698, 23316748, 26007210, 15817513, 5509405, 1037208, 82094 |
| 1 | 6 | 1002956, 2226580, 2023333, 936515, 219712, 20806 |
| 1 | 7 | 63241, 114768, 79716, 24964, 2958 |
| 1 | 8 | 1707, 2388, 1131, 180 |
| 2 | 0 | 269030800, 1020522540, 1785793048, 1920498954, 1418712328, 754795952, 291768420, 80154362, 14805316, 1642840, 82480 |
| 2 | 1 | 446604420, 1602679743, 2639095100, 2631731974, 1753781529, 807241015, 254903117, 52812138, 6463820, 353800 |
| 2 | 2 | 342308589, 1140406472, 1714117855, 1519147549, 866084762, 323670599, 76970860, 10585986, 641356 |
| 2 | 3 | 152033348, 457761225, 606433061, 457347244, 211285939, 59521511, 9423173, 644014 |
| 2 | 4 | 41815548, 110472533, 124239321, 75910679, 26479750, 4980727, 393250 |
| 2 | 5 | 7204226, 16145753, 14723456, 6807196, 1590276, 149704 |
| 2 | 6 | 753419, 1371374, 948850, 294826, 34608 |
| 2 | 7 | 43406, 60139, 28091, 4410 |
| 2 | 8 | 1044, 981, 234 |
| 3 | 0 | 148375200, 512703610, 818468842, 800686292, 531077238, 246564004, 79263404, 16794650, 2103768, 117672 |
| 3 | 1 | 241438780, 793316297, 1185654254, 1053674616, 606590451, 229949345, 55577513, 7768348, 477708 |
| 3 | 2 | 183062761, 551051079, 732768576, 556437746, 259330962, 73752879, 11784931, 812262 |
| 3 | 3 | 78889281, 209075018, 236033598, 144813744, 50720940, 9576338, 758602 |
| 3 | 4 | 20543696, 46108852, 42069888, 19448208, 4541103, 427192 |
| 3 | 5 | 3269533, 5938599, 4094949, 1267372, 148188 |
| 3 | 6 | 307074, 422971, 196205, 30586 |
| 3 | 7 | 15274, 14246, 3358 |
| 3 | 8 | 297, 144 |
| 4 | 0 | 51241800, 160577390, 232369998, 203981602, 118246844, 45766116, 11374258, 1637592, 103560 |
| 4 | 1 | 82926920, 246556553, 327668999, 251215579, 119032577, 34535888, 5633384, 395880 |
| 4 | 2 | 62239999, 164904983, 187082599, 115775379, 40988246, 7827904, 627044 |
| 4 | 3 | 25554896, 57366102, 52461048, 24344353, 5711193, 540010 |
| 4 | 4 | 6131768, 11113480, 7655497, 2369345, 277266 |
| 4 | 5 | 871180, 1194837, 552319, 85874 |
| 4 | 6 | 69977, 64815, 15166 |
| 4 | 7 | 2760, 1308 |
| 4 | 8 | 36 |
| 5 | 0 | 11370600, 32057230, 41535296, 31942440, 15506824, 4661258, 790056, 57576 |
| 5 | 1 | 18466840, 48695601, 55791331, 35226199, 12791049, 2508436, 206028 |
| 5 | 2 | 13566833, 30528519, 28149846, 13220385, 3144335, 301462 |
| 5 | 3 | 5155368, 9343667, 6457301, 2009624, 236802 |
| 5 | 4 | 1103934, 1511439, 699220, 109014 |
| 5 | 5 | 134196, 123992, 28990 |
| 5 | 6 | 8441, 3972 |
| 5 | 7 | 204 |
| 6 | 0 | 1583000, 3963350, 4505990, 2923082, 1111034, 229232, 19752 |
| 6 | 1 | 2585900, 5873620, 5552524, 2694908, 663532, 65704 |
| 6 | 2 | 1822400, 3320710, 2322062, 733812, 87900 |
| 6 | 3 | 618016, 847152, 394352, 62080 |
| 6 | 4 | 114304, 105916, 24940 |
| 6 | 5 | 11076, 5232 |
| 6 | 6 | 424 |
| 7 | 0 | 126200, 275160, 266252, 137132, 36192, 3824 |
| 7 | 1 | 206580, 387952, 283488, 93864, 11728 |
| 7 | 2 | 136056, 187260, 88332, 14160 |
| 7 | 3 | 39368, 36768, 8816 |
| 7 | 4 | 6108, 2944 |
| 7 | 5 | 384 |
| 8 | 0 | 4400, 8120, 6384, 2336, 320 |
| 8 | 1 | 7160, 10464, 5280, 896 |
| 8 | 2 | 4272, 3936, 960 |
| 8 | 3 | 992, 512 |
| 8 | 4 | 128 |
