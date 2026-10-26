> **公开展示副本。** 本地标识已替换为固定别名，并筛查个人信息。冻结证据原清单见 [source-manifest.json](source-manifest.json)，实际公开文件与编辑记录见 [manifest.json](manifest.json)。下载的论文全文[未随包附送](materials/omitted-sources.md)。下文历史验证结论的范围不变；本次导出不新增证明审查或新颖性认证。

[mathlottery-expert-brief-v2]: #

# MathLottery 专家阅读报告

> 仅整理冻结证据，不新增验证或提升证明、新颖性等级。

## 专家速览

下文为导航摘要，不是完整证明。省略号表示显示截短；完整原文、历史记录和逐项证据见链接的冻结材料及标注的 JSON 路径。原文不自动翻译；历史失败不会因后续通过而消失。

来源任务: reviewed-source · 冻结版本: 26 · 2026-10-25T12:11:08.547899+00:00

快照 SHA-256: `5794400e6e7df74d99b84c863dd5c5fa03e68180addbef0f3acd706c465e8cdf`

原题 SHA-256: `3d0e93e3a159b0da83e8bee6bce4416f9a6e2aa84a953c5abea9bc3fda99c1b4`

[Evidence manifest](source-manifest.json) · [冻结审查材料（全部记录）][frozen-dossier]

[直接阅读完整报告](#完整整理报告) · [查看证据索引](#证据索引)

### 1. 原题与候选结论

**Sun 的 beta 多项式逐系数对数凸猜想（Conjecture 4.7 第一项）**

对每个整数 n&gt;=0，令 beta\_n(q)=sum\_{k=0}^n binom(n,k)^2 binom(n+k,k) q^k ∈ Z&#91;q&#93;。证明：对所有整数 n&gt;=1 和 d&gt;=0，&#91;q^d&#93;(beta\_{n-1}(q) beta\_{n+1}(q)-beta\_n(q)^2)&gt;=0。等价地，(beta\_n(q))\_{n&gt;=0} 是 q-log-convex。q 是形式变量；不能将目标弱化为仅对每个实数 q&gt;=0 的点值不等式。

[/problem/statement][frozen-dossier]

开放状态: `OPEN` · 核查日期: 2026-10-23T05:28:55.828585+00:00

[原始出处](https://arxiv.org/html/1104.3856v8)

**candidate-record-002** · `PARTIALLY_VERIFIED` · scope `COMPLETE`

SHA-256: `87fe6633c0cb96ba88f5883d98ecef69a16abec88035d296e2f4f9f25b15fbf9` · 含审查快照: `3817f4ccbfd325651ea585817387490cc68b3ca85b32b59e8a436cea6347bc5b`

对每个整数 n≥0，令 beta\_n(q)=Σ\_{k=0}^n binom(n,k)^2 binom(n+k,k)q^k∈Z&#91;q&#93;。对所有整数 n≥1 和 d≥0，都有 &#91;q^d&#93;(beta\_{n-1}(q)beta\_{n+1}(q)-beta\_n(q)^2)≥0。完整 Lean 主定理为 SunBeta.beta\_coeffwise\_logconvex，单一源文件 proof/SunBeta.lean。本主张是覆盖原题全部量词的候选证明，不是独立 Verify 的结论。

[/candidates/0][frozen-dossier]

假设: 仅原题条件：n、d 为整数，n≥1、d≥0；beta\_n 对全部 n≥0 按原二项式有限和定义。; q 是形式变量，系数在 Z 中比较；不增加点值、有限范围或额外参数假设。

**最新状态**: `NO_ISSUES_FOUND` · 原题覆盖=`FULL` · Lean=`KERNEL_REPLAYED` · 新颖性=`UNKNOWN`

### 2. 验证状态、关键步骤与历史失败

**candidate-record-002**

| 审查 | 判断 | 原题覆盖 | 新颖性 |
| --- | --- | --- | --- |
| 1 | `INCONCLUSIVE` | `UNKNOWN` | `KNOWN` |
| 2 | `INCONCLUSIVE` | `PARTIAL` | `UNKNOWN` |
| 3 | `NO_ISSUES_FOUND` | `FULL` | `UNKNOWN` |

保留 10 项历史失败/未决检查，详见证据索引；后续通过未删除历史记录。

最新论证审查: 提交证明作为整体完整有效。核对内容包括正权重及全部支撑边界、相邻行列递推、配对卷积的2n因子、零和式端点、d&gt;2n系数为零、奇偶重参数化、m=0/m=1/r=0边界、H非零和D正、与求和指标无关的Cramer系数、334和415项正系数证书、最终除以2nD。SymPy重建和只用整数稀疏多项式运算的第二套核查都精确验证全部恒等式，非有限取值检验。本轮直接检查控 …

原题对应: 独立比较实际源码及控制器实际声明：SunBeta.beta : ℕ → Polynomial ℤ，定义为∑k∈range(n+1), monomial k ((n.choose k:ℤ)^2\*((n+k).choose k:ℤ))，恰等于原题从k=0到n的二项式有限和。主定理只有n:ℕ、hn:1≤n、d:ℕ三个参数，结 …

新颖性说明: 数学正确性与新颖性分别判断。Sun2014原猜想及其2014追述继续标为ORIGINAL\_STATEMENT，2026-02-10明确开放声明标为EXPLICIT\_OPEN；EQUIVALENT仅指同一目标，不表示已有证明。已成立的Narayana、S\_n、D\_n、Zhu–Sun …

覆盖策略: `UNASSESSED` · proof_complete=False · statement_aligned=False

关键步骤覆盖尚未评估，不能从通过标签推断完整性。

未记录结构化证明路线，需从完整材料重建。

[/candidates/0/reviews/2][frozen-dossier]

Lean: `KERNEL_REPLAYED` · —

声明: SunBeta.beta\_coeffwise\_logconvex

检查范围: Requested theorem declarations only; imported libraries and the Lean kernel are trusted. No independent kernel implement … · 命题对应: `NOT_CERTIFIED`

[冻结执行回执](materials/reviewed-source/verification/formal/42f471b6b8f76c0b78c3f1414a7e39c02a3375dcc3718892aa820903d4199f4a/receipt.json)

形式检查仅覆盖回执声明；自然语言原题与形式命题等价性未经外部认证。

### 3. 文献障碍与新颖性

按稳定 ID、类型、来源归并；不同来源保留独立条目。历史状态保留，不代表所有旧问题仍未解决。每项链接标注冻结 JSON 路径。

证据策略: evidence-v2

没有列出的具体障碍不代表检索穷尽或新颖性已确认。

证据索引保留全部 0 个障碍条目、0 项已有结果对照及 17 项其它缺口/范围限制；未解除项的来源与比较仍需逐项检查。

### 4. 专家优先检查与材料入口

1. 阅读完整证明并复核关键引理、量词和边界；以上摘录不替代逐步检查。
2. 逐项处理未解决障碍，比较最接近的已有定理。
3. LLM 审查和有限测试不构成普遍定理的证明。

## 证据索引

以下是原始记录的位置索引，不重复完整证明或文献引用；完整内容见冻结 dossier。可[跳至完整整理报告](#完整整理报告)。

### 历史问题与失败检查

**candidate-record-002**

- evidence gate · 审查 1: A blocking formal check has no independently successful execution receipt · [/candidates/0/reviews/0/validation\_notes/0][frozen-dossier]

- evidence gate · 审查 1: Full coverage requires a supported comparison to the original statement · [/candidates/0/reviews/0/validation\_notes/1][frozen-dossier]

- Lean ERROR · 审查 1: compile-0 did not complete successfully · [/candidates/0/reviews/0/formal\_receipt][frozen-dossier]

- issue · 审查 2: 验证未完成：控制器首轮编译返回1，在两个关键恒等式处报告(kernel) excessive memory consumption detected；本轮资源提高后的结果尚未产生。 · [/candidates/0/reviews/1/issues/0][frozen-dossier]

- issue · 审查 2: 首次审阅三条来源角色标错，把原猜想/开放声明写成PRIOR\_RESULT。此错误发生在审阅证据分类，不是候选证明；本次纠正并保留旧记录。 · [/candidates/0/reviews/1/issues/1][frozen-dossier]

- issue · 审查 2: EMIS载体已用公开原期刊PDF替代；MathOverflow原回答仍无可独立核验的替代载体，其具体来源缺口保持可见。 · [/candidates/0/reviews/1/issues/2][frozen-dossier]

- evidence gate · 审查 2: Full coverage conflicts with the candidate scope or remaining obligations · [/candidates/0/reviews/1/validation\_notes/0][frozen-dossier]

- check-15 · UNRESOLVED · blocking=True · 审查 2: 控制器能够在本次重新配置的资源限制下编译、重放冻结主定理并核对公理依赖。 — 实际读取并原样保存首轮receipt.json：status=ERROR、compile-0返回码1、elapsed\_seconds=207.363、memory\_mb=8192、address\_space\_mb=1638 … · [/candidates/0/reviews/1/checks/14][frozen-dossier]

- check-17 · UNRESOLVED · blocking=False · 审查 2: MathOverflow反例条目的完整内容、作者归属及发布日期具有独立下载器可复核的原始公开载体。 — 已进行针对作者、题名、−499140和反例的查询，没有找到另一份原始作者版本。未绕过MathOverflow的访问策略；第一次本地取得的文本保留，不能替代控制器独立下载器的策略核验。可校验的Sun … · [/candidates/0/reviews/1/checks/16][frozen-dossier]

- check-17 · UNRESOLVED · blocking=False · 审查 3: MathOverflow反例条目的完整内容、作者归属及发布日期具有独立下载器可复核的原始公开载体。 — 控制器2026-10-23T07:58:05.384018+00:00的来源评估仍报告该URLUnable to verify robots policy for https://mathover … · [/candidates/0/reviews/2/checks/16][frozen-dossier]

### 文献障碍历史（全部 ID）

**其它检索缺口与范围限制（去重，全部保留）**

| 摘要 | 完整记录 |
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

### 材料入口与范围限制

**证明与审查** (17): [dossier.json](materials/reviewed-source/dossier.json) · [answer.md](materials/reviewed-source/tasks/task-record-002/attempt-record-003/answer.md) · [answer.md](materials/reviewed-source/tasks/task-record-001/attempt-record-002/answer.md)

**形式化** (14): [receipt.json](materials/reviewed-source/verification/formal/e11be54ba8bbfef1085efff0262fe51fa8ed6bf150af193adf433a74e64febe1/receipt.json) · [receipt.json](materials/reviewed-source/verification/formal/42f471b6b8f76c0b78c3f1414a7e39c02a3375dcc3718892aa820903d4199f4a/receipt.json) · [SunBeta.lean](materials/reviewed-source/submitted-evidence/workspace/proof/SunBeta.lean)

**文献** (39): [0a8dfd10fa2a0ef9a1bc489b0466ef96bd4d3239410acb652287bb93add8b2b2.json](materials/reviewed-source/literature/receipts/0a8dfd10fa2a0ef9a1bc489b0466ef96bd4d3239410acb652287bb93add8b2b2.json) · [23c57e5cd3f86f980bf15a2b3f09b6a10c853ca9f4675f854fc494b36a02311a.json](materials/reviewed-source/literature/receipts/23c57e5cd3f86f980bf15a2b3f09b6a10c853ca9f4675f854fc494b36a02311a.json) · [27d96150139d45ac0d761880d03af7dcdde21e736dea6016fa7af52f73c43f54.json](materials/reviewed-source/literature/receipts/27d96150139d45ac0d761880d03af7dcdde21e736dea6016fa7af52f73c43f54.json)

全部材料路径、哈希及遗漏项见证据清单。

- This is an editorial reconstruction of visible saved evidence, not hidden reasoning, an independent mathematical verification, or a certification of novelty.

- reviewed-source: only saved answers, named notes, proof/formal files and source receipts are included; arbitrary workspace files, binaries and caches are excluded.

- solver-source: only saved answers, named notes, proof/formal files and source receipts are included; arbitrary workspace files, binaries and caches are excluded.

- The linked solver is frozen at the revision shown in this manifest, which may include work saved after the review. The original reviewed candidate is matched exactly; later work is not retroactively verified.

[frozen-dossier]: materials/reviewed-source/dossier.json

[mathlottery-expert-brief-v2-end]: #

---

## 完整整理报告

**Sun 的 beta 多项式逐系数对数凸性：冻结候选证明及审查记录的专家报告**

**专家速览。** 精确原题要求：以 \(q\) 为形式变量，定义
\[
\beta_n(q)=\sum_{k=0}^{n}\binom nk^2\binom{n+k}{k}q^k\in\mathbb Z[q],
\qquad
C(n,d):=[q^d]\bigl(\beta_{n-1}(q)\beta_{n+1}(q)-\beta_n(q)^2\bigr)\ge0
\tag{T}
\]
并对**每个整数 \(n\ge1\)、每个整数 \(d\ge0\)**证明上述不等式，其中 \(\beta_0=1\)。候选主张覆盖整个命题，包括 \(n=1\)、次数 \(0,1,2n-1,2n\) 以及超过 \(2n\) 的零系数；没有限制为某个分支、有限范围或实参数点值。

| 专家关注点 | 冻结记录实际支持的结论 |
|---|---|
| 形式系统实际证明了什么？ | `SunBeta.beta_coeffwise_logconvex` 具有上述全称量词及整数多项式系数结论，并有匹配本候选的控制器 `KERNEL_REPLAYED` 回执。 |
| 数学审查如何评价？ | 最后保存的审查为 `NO_ISSUES_FOUND`，原题覆盖 `FULL`，无剩余数学义务。这些是保存的 LLM 审查判断。 |
| 哪些事项仍未认证？ | 回执中 `statement_alignment=NOT_CERTIFIED`；新颖性仍为 `UNKNOWN`；没有外部专家认可或首解认证。候选保存级别仍是 `PARTIALLY_VERIFIED`。 |
| 哪些历史不确定性必须保留？ | Problem 记录的 `scope_relation=UNKNOWN`；较早两次审查的保存覆盖分别是 `UNKNOWN`、`PARTIAL`，判定均为 `INCONCLUSIVE`。后来的证据不能重写这些历史记录。 |
| 专家最应检查哪一环？ | 数学上最重的步骤是引理 7 的两条完整正系数恒等式，其 Lean 版本属于成功重放的模块。认证较弱的一环是书面 Cramer 公式、Lean 展开常数及自然语言原题之间的对应：审查支持该对应，但没有外部等价认证，而且详细代数审查脚本与日志未收入本包。 |

决定性材料入口为[提交证明及完整系数表](materials/reviewed-source/submitted-evidence/workspace/proof/Proof.md)、[精确 Lean 源码](materials/reviewed-source/submitted-evidence/workspace/proof/SunBeta.lean)、[成功形式回执 F1](materials/reviewed-source/verification/formal/42f471b6b8f76c0b78c3f1414a7e39c02a3375dcc3718892aa820903d4199f4a/receipt.json)和[审查 dossier](materials/reviewed-source/dossier.json)。已知邻近结果涉及 B 型 Narayana、\(S_n\)、Domb、Zhu–Sun、Hoggatt、Baxter 多项式；保存的比较没有将其中任何一个认定为精确 beta 命题的证明。Sun 在 2026-02-10 的文字仍称本题开放。因此必须分开阅读正确性证据与新颖性证据。

**1. 摘要、出处及本次整理的边界。**

提交论证将每个目标系数改写为对称的非负权重卷积，再加入两项在有限反对角线上求和为零的修正项。适当选取修正系数，使中央两个位置消失；其余内部位置分解为非负因子乘以分别含 334、415 个正整数系数单项式的多项式。所有边界另有证书。因此，无界指标的结论来自多项式恒等式，而不是从有限测试外推。

本报告忠实重排已保存证明，并把证明及审查中已有的过渡步骤展开说明，同时完整保留证书数据。下文的引理编号和按位置标记的检查编号属于编辑层。这里没有提交新的修补、新的验证、新的文献检索，也没有重建隐藏思考；只剩审查叙述的地方会明确标注其证据层级。中英文两版使用同一冻结快照。

所选审查 dossier 冻结于修订 26，截取日期为 2026-10-25。其 `review_source` 明确关联修订 9 的 Solve dossier，候选哈希及证明正文一致。因此，[关联的 Solve dossier](materials/solver-source/dossier.json) 是正式保存的来源，而不是仅凭同名或同哈希猜测的历史。两个 dossier 的 `visible_research_notes` 均为空。清单提醒关联的 Solve 快照可能含审查后保存的内容；只有精确提交候选及其匹配回执承载相应审查。六份提交证明附件也与关联副本一致。文件一致只识别字节，不证明数学真伪。

指定原始出处为 Sun 的 *Some new series for \(1/\pi\) and related congruences*，2014-12-24 版本 Conjecture 4.7 第一种多项式 [B1](https://arxiv.org/html/1104.3856v8)。紧前定义要求相邻乘积差的每个系数非负。另一份 2014-12-29 文本中，作者追述在 2011-05-07 提出了该猜想 [B3](https://arxiv.org/html/1102.5649v47)。这里保留题目指定的 2014 出处，但不称 2014 为首次提出年份，也不把作者追述变成对 2011 事件的独立认证。2026-02-10 版本 *A family of polynomials and related congruences and series* 重述精确 beta 定义并称其 “remains open” [B2](https://arxiv.org/html/2505.02767v4)。十月的下载日期不能把这一有日期的开放声明延伸到十月。

**2. 记号、假设及证明依赖。**

下文 \(n,k,l,d,m,r,j\) 均为明确给定范围内的整数。约定 \(k>n\) 时二项式系数为零，并对所有 \(n,k\ge0\) 记 \(a_{n,k}=\binom nk^2\binom{n+k}{k}\)。原始系数在整数中；辅助权重与多项式运算在 \(\mathbb Q\) 中。因此，\(n-k\)、\(l-1\) 等使用通常减法，不是自然数截断减法。整个证明不对 \(q\) 作数值代入。

\(\sum_{k+l=d}\) 始终表示遍历 \((k,l)\in\mathbb N^2\) 的全部**有序**对。排序只用于证明对称求和项非负，不改变卷积中的重数。辅助常数 \(c_0,c_1,D\) 可以依赖 \(n,d\)，但在同一反对角线上必须固定。

依赖关系为：
\[
\begin{gathered}
\text{引理 1}\longrightarrow\text{引理 2、3},\\
\text{引理 4}+\text{引理 5}+\text{引理 6}+\text{引理 7}
\longrightarrow\text{修正后的求和项非负},\\
\text{引理 2、3}+\text{上述证书}
\longrightarrow\text{引理 8}\longrightarrow\text{定理 1}.
\end{gathered}
\]
没有任何邻近文献定理被用作本证明的前提。第 3–4 节是对已提交证明及已有审查的阐释，不是本次追加的验证结论。

**3. 提交证明的完整数学阐释。**

**引理 1（权重及递推）。** 固定 \(n\ge1\)，对每个 \(k\ge0\) 定义
\[
b_k=\frac{a_{n+1,k}}{(n+1)(n+k)(n+k+1)}\ge0.
\]
分母严格为正，支撑为 \(0\le k\le n+1\)，并有
\[
\begin{aligned}
a_{n+1,k}&=(n+1)(n+k)(n+k+1)b_k,\\
a_{n,k}&=(n+k)(n-k+1)^2b_k,\\
n a_{n-1,k}&=(n-k)^2(n-k+1)^2b_k,\\
(k+1)^3b_{k+1}&=(n+k)(n-k+1)^2b_k.
\end{aligned}\tag{1}
\]
在相应支撑内，审查使用的阶乘表示为
\[
a_{n,k}=\frac{n!(n+k)!}{k!^3(n-k)!^2}\quad(k\le n),
\qquad
b_k=\frac{n!(n+k-1)!}{k!^3(n+1-k)!^2}\quad(k\le n+1).
\]
内部指标直接约分得到式 (1)。这些阶乘表示不用于负阶乘参数。\(k=n\) 时，\((n-k)^2\) 处理下方一行的零值；\(k=n+1\) 时，\((n-k+1)^2=0\) 处理中央行、下方行及列递推。\(k>n+1\) 时所有相关权重均为零。这也说明不允许、也不需要除以 \(n-k\)。Lean 使用带显式越界零值处理的二项式恒等式：`choose_row`、`choose_col`、`choose_rising`、`a_row`、`a_col` 和 `w_*`。正文的 \(b_k\) 对应 `w n k`。保存检查：R3.C02。

**引理 2（对称系数恒等式）。** 定义
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
\(P,T_0,T_1\) 均关于 \(k,l\) 对称。代入式 (1)，逐项得到
\[
b_kb_lP(n,k,l)
=n\bigl(a_{n-1,k}a_{n+1,l}+a_{n+1,k}a_{n-1,l}-2a_{n,k}a_{n,l}\bigr).
\]
映射 \((k,l)\mapsto(l,k)\) 是有序反对角线上的双射，因此两个混合和相等。结合多项式乘法的系数公式，得到
\[
2nC(n,d)=\sum_{k+l=d}b_kb_lP(n,k,l).\tag{3}
\]
当 \(k=l\) 时无需补半权重：对称化始终作用于完整有序和。这解释了最终必需的归一化因子 \(2n\)。保存检查：R3.C03；Lean 对应 `paired_term`、`delta_sum`、`beta_coeff`、`delta_coeff`。

**引理 3（求和为零的修正项）。** 任取固定 \(c_0,c_1\in\mathbb Q\)，令
\[
G(i,j)=b_i b_j i^3j^3(i-j)\bigl(c_0+c_1(i-1)(j-1)\bigr).
\]
对 \(k\) 和 \(l\) 各使用一次式 (1) 最后一条递推，可得
\[
b_kb_l\bigl(c_0T_0(n,k,l)+c_1T_1(n,k,l)\bigr)
=G(k+1,l)-G(k,l+1).
\]
右侧两个和都位于 \(i+j=d+1\) 上：第一个不含 \(i=0\)，第二个不含 \(j=0\)。相减只剩 \(G(d+1,0)-G(0,d+1)=0\)，因为 \(G\) 含有 \(i^3j^3\)。这也包含 \(d=0\)。所以
\[
\sum_{k+l=d}b_kb_l(c_0T_0+c_1T_1)=0.\tag{4}
\]
修正系数自身不必非负，关键是它们不依赖 \(k,l\)。因此，只需找出 \(D>0,c_0,c_1\)，使
\[
Q(n,k,l):=DP(n,k,l)+c_0T_0(n,k,l)+c_1T_1(n,k,l)\ge0\tag{5}
\]
在 \(b_kb_l\) 的支撑上成立。保存检查：R3.C04；Lean 对应 `flux_sum`、`weighted_flux`、`weighted_telescopes`。

**引理 4（穷尽全部情形的参数化）。** 若 \(d>2n\)，由于 \(\deg\beta_s\le s\)，式 (T) 中两个乘积在次数 \(d\) 的系数均为零。对 \(0\le d\le2n\)，唯一写成
\[
d=2m+\varepsilon,\qquad n=m+r+\varepsilon,
\qquad \varepsilon\in\{0,1\},\quad m,r\ge0.
\]
对奇数次数 \(d\)，由 \(2m+1\le2n\) 得 \(m\le n-1\)，故同样有 \(r\ge0\)。利用对称性，只需考察支撑内满足 \(k\le l\) 的对。它们必可写为
\[
k=m-j,\qquad l=m+j+\varepsilon,
\qquad 0\le j\le m,\quad j\le r+1.\tag{6}
\]
事实上令 \(j=m-k\)：排序给出 \(k\le m\)，而 \(l\le n+1\) 给出最后的上界。这里必须使用 \(n+1\) 而非 \(n\) 的支撑，因为权重来自 \(a_{n+1,k}\)。按此代换令 \(U_j=P(n,k,l)\)、\(V_j=T_0(n,k,l)\)、\(W_j=T_1(n,k,l)\)。保存检查：R3.C05；Lean 对应 `sorted_suffices`、`exists_certificate` 及 `delta_nonneg` 的高次数分支。

**引理 5（全部低指标及最高次数边界）。** 若 \(m=0\)，取 \(D=1,c_0=c_1=0\)。\(\varepsilon=0\) 时唯一一对是 \((0,0)\)，有 \(P(n,0,0)=0\)；\(\varepsilon=1\) 时排序代表为 \((0,1)\)，且
\[
P(n,0,1)=2n^2(n+1)^2(3n+1)>0.
\]
现设 \(m\ge1\)，且 \(m=1\) 或 \(r=0\)。式 (6) 强制 \(j\in\{0,1\}\)。令 \(c_1=0\)，并取
\[
\begin{array}{c|c|l}
\varepsilon&D&c_0\\\hline
0&m^2&4mr+2m+3r^2+3r\\
1&m^3&4m^2r+4m^2+3mr^2+4mr-2m-3r^2-10r-8.
\end{array}\tag{7}
\]
此时 \(D>0\)。直接多项式恒等式给出 \(DU_0+c_0V_0=0\)，以及
\[
\begin{array}{c|c|l}
\varepsilon&\text{条件}&DU_1+c_0V_1\\\hline
0&m=1&2(r+1)(r+2)^2(3r^2-3r+4)\\
0&r=0&8m(m+1)^2\\
1&m=1&36(r+2)(r+3)^2(2r^2+9r+14)\\
1&r=0&144m(m+2)^2(3m+4).
\end{array}\tag{8}
\]
这些表达式均非负；唯一含负系数的因子满足
\[
4(3r^2-3r+4)=3(2r-1)^2+13>0.
\]
因此已包含 \(d=0,1\)、\(m=1\) 的小半次数，以及由 \(r=0\) 给出的 \(d=2n,2n-1\)；重叠边界无需额外处理。保存检查：R3.C06；Lean 对应 `edgeExprEven_*`、`edgeExprOdd_*`、`even_edge`、`odd_edge` 及 `certificate_even`、`certificate_odd` 的 \(m=0\) 分支。

**引理 6（内部情形的常数）。** 余下 \(m\ge2,r\ge1\)。令
\[
D_0=3m^2r^2(m-1)^3(2m+r+1),\qquad
D_1=3m^3r^2(m-1)^3(2m+r+3).\tag{9}
\]
此定义域内每个因子为正。记 \(H=V_0W_1-V_1W_0\)，提交的恒等式为
\[
\begin{aligned}
H\bigm|_{\varepsilon=0}&=-12m^3r^2(m-1)^3(2m+r)(r+1)^2(2m+r+1),\\
H\bigm|_{\varepsilon=1}&=-24m^3r^2(m-1)^3(r+1)^2(2m+r+2)(2m+r+3).
\end{aligned}\tag{10}
\]
故 \(H<0\)。线性方程组 \(DU_0+c_0V_0+c_1W_0=0\)、\(DU_1+c_0V_1+c_1W_1=0\) 的解为
\[
c_0=D_\varepsilon\frac{U_1W_0-U_0W_1}{H},\qquad
c_1=D_\varepsilon\frac{V_1U_0-V_0U_1}{H}.\tag{11}
\]
此构造说明了为何中央位置 \(j=0,1\) 的修正表达式为零，也说明常数与求和指标无关。提交证明指出，化简后两常数都属于 \(\mathbb Z[m,r]\)。它们的展开式保存在 [certificates.json](materials/reviewed-source/submitted-evidence/workspace/proof/certificates.json) 的 `alpha`、`beta` 字段，以及 Lean 的 `alphaEven`、`betaEven`、`alphaOdd`、`betaOdd` 中。这里辅助名称 `betaEven`、`betaOdd` 不代表原多项式序列。

R3.C07 记录了对式 (10)、Cramer 解及其与展开数据对应关系的精确核查，包括乘以 \(H\) 后的恒等式检查。形式源码直接使用展开常数，没有单独命名的定理来陈述式 (10) 或 Cramer 式与展开式的对应。它通过 `ring` 分别证明 `exprEven_0`、`exprEven_1`、`exprOdd_0`、`exprOdd_1`，得到两个中央零值。这是书面推导与形式实现之间真实存在的区别，本报告没有悄悄补入额外假设。

**引理 7（完整内部证书）。** 对引理 6 的常数，提交恒等式为
\[
\begin{aligned}
D_0U_j+c_0V_j+c_1W_j
&=2j^2(j^2-1)E_0(m-j,r+1-j,j-2),\\
D_1U_j+c_0V_j+c_1W_j
&=2j(j-1)(j+1)(j+2)E_1(m-j,r+1-j,j-2).
\end{aligned}\tag{12}
\]
第一行使用偶数常数，第二行使用奇数常数。附录 D 给出 \(E_0,E_1\in\mathbb Z[u,v,t]\) 的**全部**系数：每行 \((a,b;c_0,\ldots,c_s)\) 表示 \(u^av^b\sum_{h=0}^s c_ht^h\)，未列项为零。系数表的 \(c_h\) 是局部标签，与修正常数无关。两多项式分别有 334、415 个非零项；审查记录总次数分别为 11、12，二者最小非零系数均为 36，所有列出系数均为正整数。

这些是有限表示的多项式恒等式，不是若干采样点上的等式。审计者可代入式 (2)、(9)、(11)，清除已知非零的 \(H\)，并与完整系数表逐系数比较。R3.C08 记录了两套这样的精确算法：SymPy 重建和仅用整数加乘的独立稀疏多项式实现。二者均报告零余数，并确认提交正文、表格、JSON 与 Lean 定义一致。本冻结包没有收入这些脚本及结果文件，故此处保留其审查证据层级；F1 另行记录了包含 `identityEven`、`identityOdd` 的模块成功编译及内核重放。

Lean 将恒等式写在逆代换
\[
m=u+t+2,\qquad r=v+t+1,\qquad j=t+2.
\]
之后。证书多项式为 `posEven`、`posOdd`；`positivity` 证明非负自变量上的非负取值，`ring` 证明恒等式。若 \(j\ge2\)，由式 (6) 得
\[
u=m-j\ge0,\qquad v=r+1-j\ge0,\qquad t=j-2\ge0.
\]
于是式 (12) 的其余因子也非负。\(j=0,1\) 时使用引理 6，绝不在这两个位置声称 \(j-2\ge0\)。故式 (5) 对全部内部情形成立，结合引理 5，为每个 \(d\le2n\) 给出了 \(D>0\) 及相应证书。保存检查：R3.C07–C09；形式声明包括 `exprEven_nonneg`、`exprOdd_nonneg`、`even_internal`、`odd_internal`、`certificate_even`、`certificate_odd`、`exists_certificate`。

**引理 8（回到整数系数）。** 对式 (5) 乘以 \(b_kb_l\ge0\)，沿完整反对角线求和。支撑外的项为零；常数在整条反对角线上固定，所以式 (4) 消去修正项，式 (3) 给出
\[
0\le\sum_{k+l=d}b_kb_lQ(n,k,l)
=D\sum_{k+l=d}b_kb_lP(n,k,l)
=2nD\,C(n,d).\tag{13}
\]
因为 \(n\ge1\) 且 \(D>0\)，有 \(2nD>0\)，从而 \(C(n,d)\ge0\)。\(d>2n\) 已由引理 4 处理。尽管式 (13) 写在 \(\mathbb Q\) 中，\(C(n,d)\) 是整数系数的像，利用保序嵌入 \(\mathbb Z\hookrightarrow\mathbb Q\) 得到所需的整数不等式。保存检查：R3.C09。Lean 的 `sumP_nonneg` 合成证书与消项，`delta_nonneg` 覆盖两个次数区域，`delta_coeff` 识别系数，`logconvex_step` 返回 \(\mathbb Z\) 中的结论。

**定理 1（具有保存形式证据的提交结论）。** 按提交证明、最终数学审查及其形式声明的成功回执，式 (T) 在所列假设下成立。形式证明先使用非负下标 \(s\) 及三行 \(s,s+1,s+2\)，再取 \(s=n-1\)。条件 \(1\le n\) 保证 \(n-1+1=n\)、\(n-1+2=n+1\)。保存的主声明为

```lean
theorem SunBeta.beta_coeffwise_logconvex (n : ℕ) (hn : 1 ≤ n) (d : ℕ) :
  0 ≤ (SunBeta.beta (n-1) * SunBeta.beta (n+1) - SunBeta.beta n ^ 2).coeff d
```

相应定义为

```lean
noncomputable def SunBeta.beta (n : ℕ) : Polynomial ℤ :=
  ∑ k ∈ Finset.range (n+1),
    Polynomial.monomial k ((n.choose k : ℤ)^2 * ((n+k).choose k : ℤ))
```

这种表述不提升候选保存级别，也不认证该声明的自然语言解释。

**4. 原题覆盖及附加主张。**

| 方面 | 冻结证据中的对应 | 限定 |
|---|---|---|
| 定义 | 权重精确为 \(\binom nk^2\binom{n+k}{k}\)，求和 \(k=0,\ldots,n\)。 | 不是 Narayana、\(S_n\)、Domb 或 rising-binomial 权重。 |
| 量词与定义域 | `n : ℕ`、`hn : 1 ≤ n`、任意 `d : ℕ`，系数在 `ℤ` 中。 | 两指标均无上界，\(q\) 不作数值代入。 |
| 减法 | 多项式减法位于 `Polynomial ℤ`，系数比较位于 `ℤ`。 | 只有行下标 \(n-1\) 使用自然数减法，并受 `hn` 保护。 |
| 最小情形 | 同一证明包括 \(n=1\)、\(\beta_0\)、\(d=0,1\)。 | 原题不要求中心下标 \(n=0\)。 |
| 最高及超出次数 | \(r=0\) 覆盖 \(2n,2n-1\)，支撑处理 \(d>2n\)。 | 结论是通常的逐系数对数凸性。 |
| 语义对应 | R3.C01 及保存的声明探针支持对应，最新审查覆盖为 `FULL`。 | 回执仍为 `NOT_CERTIFIED`；没有外部专家等价认证。 |

R3.C10 还记录了以下边界计算：
\[
\begin{aligned}
C(n,0)&=0, & C(n,1)&=6n+2,\\
C(n,2n)&=\frac{\binom{2n}{n}^{\!2}}{(2n-1)(n+1)}>0,\\
\beta_0\beta_2-\beta_1^2&=8q+2q^2,\\
\beta_1\beta_3-\beta_2^2&=14q+6q^2+56q^3+4q^4.
\end{aligned}\tag{14}
\]
审查由 \(a_{n,1}=n^2(n+1)\) 的二阶差得到 \(C(n,1)\)，由相邻中央二项式系数得到最高项。这些等式及严格不等式是保存的推导主张，**不是 F1 中单独请求或检查的 Lean 定理**。形式主定理只陈述非负性。证明也说明 \(d>2n\) 的系数为零，但并没有被单独认证的全局等号分类定理。这里不提交或推断完整等号刻画、强 \(q\)-对数凸性、参数推广或最优性结论。

**5. 保存的检查与历史判定。**

各审查的 `checks[].id` 字符串全部为空，`proof_steps`、`statement_alignment` 数组也为空。因此，**R3.C01–R3.C17 是编辑添加的按位置定位符，不是原始系统检查 ID**：R3 表示第三份保存审查，C01 表示其中第一个 `checks` 元素，即 [dossier](materials/reviewed-source/dossier.json) 中的 `candidates[0].reviews[2].checks[0]`。R1、R2 同理表示前两次审查。

| 定位符 | 主张或证明依赖 | 保存的方法／结果 |
|---|---|---|
| R3.C01 | 定义、量词、整数系数；定理 1 及第 4 节 | `DERIVATION / SUPPORTED` |
| R3.C02 | 权重递推与支撑；引理 1 | `DERIVATION / SUPPORTED` |
| R3.C03 | 对称卷积及 \(2n\) 因子；引理 2 | `DERIVATION / SUPPORTED` |
| R3.C04 | 零和式端点与固定常数；引理 3 | `DERIVATION / SUPPORTED` |
| R3.C05 | 次数划分及全部参数范围；引理 4 | `DERIVATION / SUPPORTED` |
| R3.C06 | 全部边界证书；引理 5 | `DERIVATION / SUPPORTED` |
| R3.C07 | \(H\ne0\)、\(D>0\)、Cramer 常数及展开式；引理 6 | `DERIVATION / SUPPORTED` |
| R3.C08 | 两条完整多项式恒等式及 749 个系数；引理 7 | `DERIVATION / SUPPORTED` |
| R3.C09 | 非负求和及除以 \(2nD\)；引理 8 | `DERIVATION / SUPPORTED` |
| R3.C10 | 附加边界等式 (14) | `DERIVATION / SUPPORTED` |
| R3.C11 | 有限精确卷积与递推测试 | `FINITE_TEST / SUPPORTED` |
| R3.C12 | 原始来源与邻近定理比较 | `REFERENCE / SUPPORTED` |
| R3.C13 | rising-binomial 反例针对另一多项式族 | `COUNTEREXAMPLE / SUPPORTED` |
| R3.C14 | 审查者本地编译、声明探针及重放历史 | `FORMAL / SUPPORTED`，保存的是叙述，详细日志缺失 |
| R3.C15 | 匹配的控制器成功回执 F1 | `FORMAL / SUPPORTED`，回执存在 |
| R3.C16 | 更正来源角色，以期刊载体替代 EMIS | `REFERENCE / SUPPORTED` |
| R3.C17 | MathOverflow 回答的独立来源核验 | `REFERENCE / UNRESOLVED`，不阻断数学证明 |

保存审查中，前九项及 R3.C14–C15 标记为阻断检查，其他项为非阻断检查。R2 的 C15 仍为 `UNRESOLVED`，R3 使用 F1 记录其解除；C17 仍未解决。表中的 `SUPPORTED` 是原记录标签，不是本次编辑新产生的结果。

| 保存状态 | 判定：报告值 → 保存值 | 新颖性：报告值 → 保存值 | 保存的原题覆盖 |
|---|---|---|---|
| Solve 候选 | 尚无独立审查；`scope=COMPLETE`，级别 `CANDIDATE` | 未认证 | 候选主张完整覆盖 |
| R1 | `NO_ISSUES_FOUND → INCONCLUSIVE` | `POTENTIALLY_NEW → KNOWN` | `UNKNOWN` |
| R2 | `INCONCLUSIVE → INCONCLUSIVE` | `UNKNOWN → UNKNOWN` | `PARTIAL` |
| R3 | `NO_ISSUES_FOUND → NO_ISSUES_FOUND` | `UNKNOWN → UNKNOWN` | `FULL` |
| 冻结时的所选候选 | 级别 `PARTIALLY_VERIFIED`，`scope=COMPLETE` | 最新审查为 `UNKNOWN` | 保留历史状态 |

R1 保存的 `KNOWN` 不是已有解答的证据：后续审查明确纠正了三条把原猜想／开放声明误标为 `PRIOR_RESULT` 的引用。`EQUIVALENT` 可能只表示同一个猜想，不表示已有定理。R1 的校验说明还指出，阻断形式检查没有独立成功执行回执，完整覆盖需要有证据支持的原题比较。

R2 继续支持数学推理，但其正文写成时尚无成功重试回执。不能用其正文中语义对应的 `FULL` 判断，覆盖保存的 `PARTIAL` 或校验说明 “Full coverage conflicts with the candidate scope or remaining obligations”。它列出的两项义务分别是控制器重试与 MathOverflow 来源核验。成功回执随后附加到 R2，因此冻结对象同时含有较早的未定论叙述和较后的成功证据；R3 才明确综合二者。R3 没有剩余数学义务，而具体文献缺口仍列在 `literature_search.unresolved`。

三份历史 `proof_coverage` 对象均仍为 `proof_complete=false`、`statement_aligned=false`、`formal_alignment_certified=false`，步骤计数为零，没有评估时间戳；它们不是新生成的证明覆盖认证。Problem 的 `scope_relation=UNKNOWN` 也未变。这些字段与最新审查的 `FULL` 并存，本报告保留其差别，不合成一个升级状态。

**6. Lean 实际检查范围与回执限制。**

F0 指[首次控制器回执](materials/reviewed-source/verification/formal/e11be54ba8bbfef1085efff0262fe51fa8ed6bf150af193adf433a74e64febe1/receipt.json)，F1 指[成功重试回执](materials/reviewed-source/verification/formal/42f471b6b8f76c0b78c3f1414a7e39c02a3375dcc3718892aa820903d4199f4a/receipt.json)。二者均只请求文件 `workspace/proof/SunBeta.lean`，`module_root=proof`，且只请求声明 `SunBeta.beta_coeffwise_logconvex`。

| 记录 | 实际保存结果 | 证据用途 |
|---|---|---|
| Solve 本地清单 | `COMPILED`，退出码 0；`independent_verify=NOT_RUN` | Solve 本地记录，不是独立控制器回执。 |
| 审查者第一次本地编译 | 900 秒外部超时 | 失败尝试，从未算作通过。 |
| 审查者第二次本地编译 | 记录为 426.962 秒、退出码 0 | 审查叙述；本包缺原始编译日志。 |
| 审查者独立声明探针 | 记录为 19.833 秒、退出码 0 | 源码存在，但原始执行日志和单独控制器回执缺失。 |
| 审查者本地 `leanchecker` | 记录为 93.236 秒、退出码 0 | 重放的审查叙述，不替代 F1。 |
| F0，2026-10-23 07:22:31 UTC | `ERROR`；编译 207.363 秒、退出码 1；没有已检查声明 | Lean 阈值 8192 MiB。审查将失败归于 `identityEven`、`identityOdd` 的内核内存错误；F0 本身只写通用编译失败原因。 |
| F1，2026-10-23 07:46:45 UTC | `KERNEL_REPLAYED`；编译 534.384 秒、重放 100.352 秒、声明检查 41.802 秒，均退出 0 | 候选／源码匹配；Lean 阈值 16384 MiB、地址空间上限 24576 MiB、配置时限 1800 秒、单线程。这些限制不是实测内存峰值 RSS。 |

F1 记录 Lean 4.35.0、提交 `eb6cafb7290e8bd5f2937522d8d804f58f02bafc`，以及 570766176 字节的编译对象。其检查的声明只依赖 `propext`、`Classical.choice`、`Quot.sound`，清单中无 `sorryAx`。这是已经记录的编译器／内核结果，不是尚未执行的建议命令。其信任基础是安装的 Lean 内核和导入库，不是另一独立实现的内核；它不认证原创性、与自然语言的语义等价，也不认证第 4 节每条附加等式。

有关哈希须分域理解：

| 哈希对象 | SHA-256／指纹 |
|---|---|
| 两份形式回执及 dossier 绑定的候选 | `87fe6633c0cb96ba88f5883d98ecef69a16abec88035d296e2f4f9f25b15fbf9` |
| 提交的 Lean 源码字节 | `5664f90350aa84b61f78d8bcc10741591852bc1572f5dbc3f1fb9c0675170aa3` |
| 形式回执使用的 UTF-8 `Problem.statement` | `50b6ca7a1c36b480c5c7b20b8b07d789a08b70d6b29b119b1c25bdbc2bde01b6` |
| 整理清单使用的完整规范化 Problem 记录 | `3d0e93e3a159b0da83e8bee6bce4416f9a6e2aa84a953c5abea9bc3fda99c1b4` |

最后两值的输入不同，数值不同不是哈希不匹配。F1 的候选及源码值匹配本冻结候选／源码；没有借用缺失或不匹配的回执支持其他版本。本次独立编辑清点发现，清单列出的 70 份文件均符合记录大小与哈希，但这只是文件完整性观察。F1 保留编译、重放、声明检查日志的哈希，却未附日志正文。R3 记载当时曾核对这些日志，本会话不能从缺失正文重新完成该比较。

附录 C 逐项列出已编译／重放源码中的 52 条具名定理。只有主定理被单独请求，并由检查器逐项报告；其他条目是模块依赖，不能说成另有 51 份逐定理回执。保存的 [StatementProbe.lean](materials/reviewed-source/review-workspaces/candidate-record-002/formal-probes/StatementProbe.lean) 用匿名 `example` 写出了原题的三个有限和；其被记录的成功支持 Lean 层面的重述，不是外部自然语言认证。

**7. 实验、精确代数核查与缺失证据。**

| 材料或活动 | 保存结果 | 支持范围／缺失情况 |
|---|---|---|
| Problem 中较早的可行性元数据 | 记录 \(n=1,\ldots,80\) 的全部系数非负；`FindProbes.BetaConjecture` 声明曾成功 elaboration | 仅作背景。所指 Find 实验／源码及执行回执不在本包；声明 elaboration 不等于定理被证明。没有导入独立 Find 历史。 |
| R3.C11 直接整数卷积 | \(n=1,\ldots,120\)、\(d=0,\ldots,2n+2\)，共 14880 个系数，负值为零 | 只支持有限范围。审查描述使用 `math.comb` 和任意精度整数；脚本及结果文件缺失。 |
| R3.C11 有理递推测试 | 4440 次精确 `Fraction` 比较，含支撑外情形 | 引理 1 的有限实例，不是其全称证明。 |
| R3.C07–C08 精确符号核查 | 记录两套算法均确认 Cramer 恒等式、两条完整多项式恒等式及全部 749 个系数一致 | 精确系数恒等式不同于有限取值测试，可支持一般代数结论；本包保存的是审查结果叙述，独立脚本及结果文件缺失。 |
| 提交证明、系数表、JSON、Lean | 均存在，主源码有匹配 F1 | 重新审计所需的精确数学对象仍可读取。 |

缺失材料包括 `ReviewNotes.md`、`check_algebra.py`、`check_sparse.py`、代数／稀疏结果 JSON、审查者的 `run_lean.py`、首次和第二次编译日志／结果、探针及重放日志、更正笔记、控制器日志副本，以及审查引用的单独文献比较／检索文件。证明 README 提到的本地开发日志也未收入。原始 Problem 所指 `research/solver_handoff.md`、`research/experiments.py` 和 Find 探针未提供；两个 dossier 都没有可见研究笔记。因此不能负责任地补写证书发现过程、已保存候选之前的数学失败路线，或这些缺失文件的具体内容。

提交的**单文件**证明所需全部本项目源码已齐备：它仅导入 Mathlib／Lean 模块，不依赖开发分模块文件。八份关联开发文件只供追溯，没有单独形式回执。冻结导出不含安装的 Lean／mathlib 库、预编译依赖、生成的 `.olean` 和 `MathLotteryInspector.lean`，也未提供完整 mathlib 依赖锁定文件／修订。这限制离线复现，不构成已检查声明存在数学缺陷的证据。

**8. 已有结果、新颖性及未解除的来源障碍。**

下表重述 R3.C12、R3.C16 的比较，所有求和均为 \(k=0,\ldots,n\)。“不同”针对可见定义与定理参数，并不排除文献中的所有非显然推论。

| 已成立的邻近结果 | 多项式或区分特征 | 为何不直接解决式 (T) |
|---|---|---|
| Chen–Tang–Wang–Yang，B 型 Narayana，Theorem 1.1 [B4](https://arxiv.org/html/0810.2247v1) | \(W_n(q)=\sum_k\binom nk^2q^k\)，逐系数对数凸 | 缺少 \(\binom{n+k}{k}\)；\(W_1=1+q\)，而 \(\beta_1=1+2q\)。 |
| Dou–Ren，\(S_n\)，Theorem 3.1 [B5](https://arxiv.org/html/1308.2736v2) | \(S_n(q)=\sum_k\binom nk\binom{2k}{k}\binom{2n-2k}{n-k}q^k\)，逐系数对数凸 | 是并列猜想的第二族；常数项为 \(\binom{2n}{n}\)，不是 1。 |
| Dou–Ren，Domb，Theorem 3.1 [B6](https://arxiv.org/html/1308.2961v1) | \(D_n(q)=\sum_k\binom nk^2\binom{2k}{k}\binom{2n-2k}{n-k}q^k\)，逐系数对数凸 | 是第三族；额外权重及常数项均不同。 |
| Zhu–Sun，Corollary 2.9 [B7](https://www.combinatorics.org/ojs/index.php/eljc/article/download/v22i3p26/pdf/) | \(P_n(q)=\sum_k\binom nk^2\binom{2k}{k}q^k\)，强逐系数对数凸 | \(P_2=1+8q+6q^2\)，而 \(\beta_2=1+12q+6q^2\)。 |
| Chern–Shi，Hoggatt，Theorem 1.2 [B8](https://arxiv.org/html/2609.33732v1) | 对每个固定整数 Hoggatt 参数 \(h\ge1\) 强逐系数对数凸；每行常数项、最高项均为 1 | \(n\ge1\) 时 beta 最高项为 \(\binom{2n}{n}\)。这里把原文参数改记 \(h\)，避免与目标次数 \(d\) 混淆。 |
| Liu–Mao，Baxter，Theorem 5.1 [B9](https://arxiv.org/html/2608.22258v1) | 系数 \(B(n,k)=\binom nk\binom{n+1}{k}\binom{n+2}{k}/[\binom{k+1}{k}\binom{k+2}{k}]\)，最高项为 1 | 是另一族，也是 Hoggatt 参数 3 的情形；不是 beta。 |

Zhu–Sun 路线有明确的假设障碍：Proposition 2.8 要求固定输入序列 \(f_k(q)\)，不能依赖外层行号 \(n\)。取 \(f_k(q)=\binom{n+k}{k}q^k\) 不满足这一要求。Theorem 2.1 的 C1 又先要求行生成多项式已具有强 \(q\)-对数凸性；直接选 beta 数组并未证明 C1。同一并列猜想的其他已解项、所有 \(q\ge0\) 的点值不等式、有限实验，也不能建立式 (T)。这些是保存的方法障碍；本证书论证没有依赖这些捷径。

一项具体文献来源障碍仍未解除。审查引用 [MathOverflow 回答](https://mathoverflow.net/questions/479301/on-the-polynomials-sum-k-0n-binomnkkm-qk)，并将其归于 Qiping Zhou、日期 2026-07-24；但其完整内容、作者归属与日期**尚未通过控制器独立来源核验**。保存状态为 `UNAVAILABLE`、`verified_excerpt=false`，原因是无法核实 robots 策略。上述归属与日期是报告中的元数据，不是本报告确证的事实。首次审查提及的本地文本未收入导出，保存的检索也没有找到可独立核验的作者／期刊替代版本。

R3.C13 另行区分了该反例的数学对象。Sun 2026 Conjecture 1.1(i) 第二句讨论
\[
R_n^{(p)}(q)=\sum_{k=0}^{n}\binom{n+k}{k}^{p}q^k,\qquad p\ge2.
\]
审查记录在 \(p=5,n=7\) 时
\[
[q^2]\bigl(R_6^{(5)}R_8^{(5)}-(R_7^{(5)})^2\bigr)
=28^5+7^5\,9^5+45^5-2\,36^5-8^{10}=-499140,
\]
而 beta 在 \((n,d)=(7,2)\) 的系数被记录为 1316。因此，这个计算不反驳式 (T)。无需认证 MathOverflow 的作者归属，也可从冻结的 Sun 原文识别其数学对象；但具体来源缺口仍须留在 `literature_search.unresolved`，不能藏入一般检索局限。[Sun 的另一猜想 B2](https://arxiv.org/html/2505.02767v4#S1.Thmconjecture1)及[审查 dossier](materials/reviewed-source/dossier.json)是现有证据。

EMIS 访问失败同样保留；其 Zhu–Sun 来源后来被原期刊 PDF 替代，控制器接受了后者的摘录。最新评估中，十一条引用有十条摘录获核实，MathOverflow 一条未核实；`evidence_assessment.supported` 仍为 false。结构化 `obstacles` 列表为空，不消除明确记录的 unresolved 来源字符串。

保存的检索截至 2026-10-23，主要覆盖公开网络索引、arXiv、作者／期刊公开来源，以英文为主并含中文查询，不穷尽数据库、语言、未公开／未索引作品或非显然推导。较早 Problem 元数据还记录了作者旧主页书目访问不全，以及 2014 年以前可能公开载体覆盖不全。已保存比较中没有识别到精确 beta 的既有证明，但这不是首解证明。**新颖性保持 `UNKNOWN`；本次编辑不会把有日期的 `OPEN` Problem 记录悄悄改成 `SOLVED`。**

**9. 复现说明与尚待事项。**

下列是**本次编辑未执行的复现说明**，不是新的执行回执。请在副本上操作，将六份提交证明附件置于临时工作区的 `proof/`，并建立脚本存日志所需的 `research/`。保存的 Solve 命令为

```sh
mkdir -p research
conda run -n mathlottery python proof/check.py
```

[保存脚本](materials/reviewed-source/submitted-evidence/workspace/proof/check.py) 在工作区及祖先目录寻找已有 `.mathlottery/toolchains/mathlib4-v4.35.0` 与相应 Lean 4.35.0，使用已有 mathlib／依赖包缓存设置 `LEAN_PATH`，不下载、不构建；找不到缓存即退出。它单线程编译，外部时限 900 秒。该命令复现 Solve 的编译过程，**不会自动复现控制器资源设置或声明检查器**。

若环境已提供记录的 Lean 版本及匹配导入库，并在 `LEAN_PATH` 配好 `proof/` 及预编译依赖目录，控制器编译／重放的命令形式为

```sh
lean -j 1 -s 65536 -M 16384 -o proof/SunBeta.olean proof/SunBeta.lean
leanchecker SunBeta
```

命令从 `PATH` 使用可执行程序；环境配置与可用资源仍是前提。源码末尾已含 `#print axioms SunBeta.beta_coeffwise_logconvex`。模块生成后，可把单独提供的声明探针复制到临时工作区，运行 `lean StatementProbe.lean`。精确复现控制器声明检查还需要缺失的 `MathLotteryInspector.lean` 及环境。新复现的成功属于新证据，不追溯改写 F0、F1。

代数审计规范已由式 (2)、(9)–(12) 及附录 D 完整给出：重建 \(U_j,V_j,W_j\)，构造 \(H,c_0,c_1\)，清除非零分母，比较两条完整多项式，并核对全部边界恒等式 (8)。这里不提供运行缺失 `check_algebra.py`、`check_sparse.py` 的虚构命令，也不声称本次已重现它们的结果。

最终审查没有记载尚未解决的**数学证明**义务。仍待处理的是 MathOverflow 来源核验、外部专家对数学阐释及形式／自然语言对应的评价、优先权判断，以及完全独立复现所需的缺失材料／环境。任何简化、加强、等号分类或修补建议均应进入新的 Solve/Verify；本报告没有提供这类新主张。

**10. 参考文献及冻结载体。**

下列链接标识保存证据讨论的版本，不代表本次新浏览。九份现有文献文本在本导出中均为提取文本，不是来源回执指向的原始 HTML／PDF 字节。快照文件名中的哈希标识原始载体；提取文件另有自己的清单哈希，不能把两个哈希域当作同一文件比较。来源回执只认证文本匹配，不认证解读或检索完备性。

- **B1.** Zhi-Wei Sun，*Some new series for \(1/\pi\) and related congruences*，2014-12-24 版本，Conjecture 4.7 及紧前定义。[来源](https://arxiv.org/html/1104.3856v8)；[冻结提取文本](materials/omitted-sources.md#source-1)。角色为 `ORIGINAL_STATEMENT`，第一族即精确目标。
- **B2.** Zhi-Wei Sun，*A family of polynomials and related congruences and series*，v4，2026-02-10，*Frontiers in Combinatorics and Number Theory* 2 (2026)，1–22。§1 `#S1.p5.2` 给出有日期的 beta 开放声明；Conjecture 1.1(i) 第二句给出不同的 rising-binomial 族。[来源](https://arxiv.org/html/2505.02767v4)；[冻结提取文本](materials/omitted-sources.md#source-9)。beta 对应 `EXPLICIT_OPEN`，另一个猜想对应 `ORIGINAL_STATEMENT`。
- **B3.** Zhi-Wei Sun，*List of conjectural series for powers of \(\pi\) and other constants*，v47，2014-12-29，§2 末、§3 前追述 2011 日期的段落。[来源](https://arxiv.org/html/1102.5649v47)；[冻结提取文本](materials/omitted-sources.md#source-8)。角色为 `ORIGINAL_STATEMENT`，不是已有证明。
- **B4.** William Y. C. Chen、Robert L. Tang、Larry X. W. Wang、Arthur L. B. Yang，*The q-Log-convexity of the Generating Functions of the Squares of Binomial Coefficients*，预印本 v1，2008-10-13，Theorem 1.1；Problem 另以 *The q-Log-convexity of the Narayana Polynomials of Type B* 为题引用 2010 期刊版本。[预印本来源](https://arxiv.org/html/0810.2247v1)；[冻结提取文本](materials/omitted-sources.md#source-5)。角色为 `PRIOR_RESULT`、关系 `DIFFERENT`。另行引用的作者网站 PDF 不在导出中。
- **B5.** Donna Q. J. Dou、Anne X. Y. Ren，*On the q-log-convexity conjecture of Sun*，v2，2013-08-15，定义 (1.1)、Theorem 3.1。[来源](https://arxiv.org/html/1308.2736v2)；[冻结提取文本](materials/omitted-sources.md#source-7)。角色为不同 \(S_n\) 猜想的 `SOLUTION`。Problem 元数据保存了较早 PDF 连接失败，由同版本 HTML 替代的记录。
- **B6.** Donna Q. J. Dou、Anne X. Y. Ren，*The q-log-convexity of Domb’s polynomials*，v1，2013-08-13，定义 (1.1)、Theorem 3.1。[来源](https://arxiv.org/html/1308.2961v1)；[冻结提取文本](materials/omitted-sources.md#source-3)。角色为不同 Domb 猜想的 `SOLUTION`；早先另行引用的 PDF 缺失。
- **B7.** Bao-Xuan Zhu、Hua Sun，*Linear transformations preserving the strong q-log-convexity of polynomials*，*Electronic Journal of Combinatorics* 22(3)，P3.26，2015-08-28 发表，Theorem 2.1、Proposition 2.8、Corollary 2.9。[期刊来源](https://www.combinatorics.org/ojs/index.php/eljc/article/download/v22i3p26/pdf/)；[冻结提取文本](materials/omitted-sources.md#source-2)；[接受的期刊回执](materials/reviewed-source/literature/receipts/82d6bbfd69a27cd285085018298c3679b5d035b1c2a84765cda3b1a4f0605e9b.json)。[失败的 EMIS 回执](materials/reviewed-source/literature/receipts/d0c1d40267c5f84382f037c76a3c553343e3380b41dded7bce0848aeef9b4e37.json)仍保留为历史。角色为 `PRIOR_RESULT`、关系 `DIFFERENT`。
- **B8.** Shane Chern、Wenle Shi，*Strong q-log-convexity of the d-Hoggatt polynomials*，v1，2026-09-27，Theorem 1.2。[来源](https://arxiv.org/html/2609.33732v1)；[冻结提取文本](materials/omitted-sources.md#source-4)。角色为 `PRIOR_RESULT`、关系 `DIFFERENT`。
- **B9.** Yanxin Liu、Jianxi Mao，*Pfaffian–Toeplitz identities, Schur positivity, and the q-log-convexity of Baxter polynomials*，v1，2026-08-23，§4 定义及 Theorem 5.1。[来源](https://arxiv.org/html/2608.22258v1)；[冻结提取文本](materials/omitted-sources.md#source-6)。角色为 `PRIOR_RESULT`、关系 `DIFFERENT`。
- **B10.** MathOverflow，*On the polynomials \(\sum_{k=0}^n\binom{n+k}{k}^m q^k\)*，审查将回答归于 Qiping Zhou、2026-07-24。[报告的来源](https://mathoverflow.net/questions/479301/on-the-polynomials-sum-k-0n-binomnkkm-qk)；[来源不可用回执](materials/reviewed-source/literature/receipts/27d96150139d45ac0d761880d03af7dcdde21e736dea6016fa7af52f73c43f54.json)。记录角色为不同族的 `CORRECTION`，关系 `DIFFERENT`。本包没有已核验的完整载体，作者／日期／内容仍受具体来源缺口限制。

**附录 A：已保存尝试的简明时间线。**

时间均为 2026-10-23 的 UTC。dossier 时间线记录的是任务观察时间，不保证就是精确开始／结束时间。下表涵盖可见的全部保存研究／审查尝试，不重建隐藏的中间实验。

| 保存时间或区间 | 尝试及结果 | 现存证据 |
|---|---|---|
| 05:30 观察；Solve dossier 更新于 06:46 | 唯一保存的 Solve 尝试提交完整候选、零和修正证书、完整表格及本地编译主定理；当时尚无独立 Verify。 | [Solve 答复](materials/solver-source/tasks/task-record-004/attempt-record-001/answer.md)、[本地清单](materials/solver-source/workspace/proof/manifest.json)。 |
| 06:50 观察 | 首次审查检查代数与支撑、两套精确证书算法及有限实验；本地首次编译超时，第二次成功，探针／重放被记录为成功；报告数学支持及潜在新颖性。 | [R1 答复](materials/reviewed-source/tasks/task-record-002/attempt-record-003/answer.md)及 dossier 中 R1。 |
| 07:22 形式回执；07:25 来源评估 | F0 失败；EMIS、MathOverflow 来源核验失败；保存 R1 为 `INCONCLUSIVE`、覆盖 `UNKNOWN`，误分类引用造成历史保存值 `KNOWN`。 | F0、来源回执、R1 校验说明。 |
| 07:34 观察 | 第二次审查保留形式失败，纠正引用角色，用期刊来源替代 Zhu–Sun 的 EMIS 载体，保留 MathOverflow 缺口，并请求调整资源后的重试。 | [R2 答复](materials/reviewed-source/tasks/task-record-001/attempt-record-002/answer.md)；保存判定 `INCONCLUSIVE`、覆盖 `PARTIAL`、新颖性 `UNKNOWN`。 |
| 07:46 形式回执；07:58 来源评估 | 同一源码获得 F1 成功；期刊摘录被接受，MathOverflow 仍未核实。 | F1 及附于 dossier 的第二次来源评估。 |
| 07:59 观察；08:07 最终评估 | 第三次审查直接读取实际成功回执／日志，未重新编译，核对字节后记录 `NO_ISSUES_FOUND / FULL / UNKNOWN`，保留早先失败。 | [R3 答复](materials/reviewed-source/tasks/task-record-003/attempt-record-004/answer.md)及最终 dossier。 |

较早 Find 元数据还提及引用转写问题与一次 PDF 连接失败，之后改用原始 HTML／文本载体。这些只按元数据保留；不向时间线添加未关联的 Find 会话、放弃的证明或未保存计算。编辑快照截取于 2026-10-25；本会话没有新做数学实验或 Lean 编译。

**附录 B：数学材料索引。**

这是阅读指南，不重复控制器另行生成的确定性文件／交接索引。

| 材料 | 建议检查内容 |
|---|---|
| [审查 dossier](materials/reviewed-source/dossier.json) | 精确候选、三份审查、空检查 ID、历史状态投影、来源评估及未解决缺口。 |
| [关联 Solve dossier](materials/solver-source/dossier.json) | 明确关联的候选、唯一可见 Solve 尝试；没有可见笔记。 |
| [Proof.md](materials/reviewed-source/submitted-evidence/workspace/proof/Proof.md) | 提交证明及完整系数附录，引理 1–8 的来源。 |
| [CertificateTable.md](materials/reviewed-source/submitted-evidence/workspace/proof/CertificateTable.md)、[certificates.json](materials/reviewed-source/submitted-evidence/workspace/proof/certificates.json) | \(E_0,E_1\) 的全部系数；JSON 还给出展开修正常数。 |
| [SunBeta.lean](materials/reviewed-source/submitted-evidence/workspace/proof/SunBeta.lean) | 精确单文件形式证明；附录 C 逐项列定理。 |
| [README.md](materials/reviewed-source/submitted-evidence/workspace/proof/README.md)、[check.py](materials/reviewed-source/submitted-evidence/workspace/proof/check.py) | Solve 时的说明及编译程序；“尚未 Verify”是历史描述。 |
| [F0](materials/reviewed-source/verification/formal/e11be54ba8bbfef1085efff0262fe51fa8ed6bf150af193adf433a74e64febe1/receipt.json)、[F1](materials/reviewed-source/verification/formal/42f471b6b8f76c0b78c3f1414a7e39c02a3375dcc3718892aa820903d4199f4a/receipt.json) | 相同字节的失败／成功控制器检查；日志正文缺失。 |
| [StatementProbe.lean](materials/reviewed-source/review-workspaces/candidate-record-002/formal-probes/StatementProbe.lean)、[审查源码副本](materials/reviewed-source/review-workspaces/candidate-record-002/formal-probes/SunBeta.lean) | 匿名有限和重述及精确复制的源码；执行情况由审查叙述保存。 |
| [Basic](materials/solver-source/workspace/research/lean_modules/Basic.lean)、[Convolution](materials/solver-source/workspace/research/lean_modules/Convolution.lean)、[Sign](materials/solver-source/workspace/research/lean_modules/Sign.lean)、[Beta](materials/solver-source/workspace/research/lean_modules/Beta.lean) | 递推、求和、符号及主定理的关联开发模块；不是提交单文件的额外依赖。 |
| [CertificateData](materials/solver-source/workspace/research/lean_modules/CertificateData.lean)、[CertificateEven](materials/solver-source/workspace/research/lean_modules/CertificateEven.lean)、[CertificateOdd](materials/solver-source/workspace/research/lean_modules/CertificateOdd.lean)、[Certificates](materials/solver-source/workspace/research/lean_modules/Certificates.lean) | 开发阶段证书定义及奇偶证明；没有单独成功形式回执。 |
| 参考文献 B1–B10 | 九份冻结提取文本及相关来源回执，包括失败获取与更正后的出处。 |

**附录 C：已检查模块中的具名定理。**

下表列举源码声明，不是逐项单独出具的回执。全部条目属于 F1 指定的精确 `SunBeta.lean`。**M** 表示“处于已编译／重放模块内，未单独请求、也未由检查器逐条列出”；**T** 表示“请求的主声明，F1 单独列明其类型和公理”。F0 不支持任何成功检查的声明。源码行号只用于导航；历史审查文字的少数行号略有偏差，应优先按声明名定位。

| 序号 | 定理全限定名 | 源码行 | 阐释引理 | 回执及范围 |
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

**附录 D：完整正系数证书。**

下表完整复制冻结提交附件中的数学证书。定义
\[
E_\varepsilon(u,v,t)=\sum_{(a,b)\text{ 已列出}}u^av^b\sum_{h=0}^{s(a,b)}c_{a,b,h}t^h.
\]
每行列出 \(c_{a,b,0},\ldots,c_{a,b,s(a,b)}\)，所有未列系数为零。这是引理 7 的精确整数数据，不是实验或原始执行日志。完整列出后，书面证书无需依赖另一语言报告即可确定。

**D.1. E₀: 334 个非零项.**

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

**D.2. E₁: 415 个非零项.**

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
