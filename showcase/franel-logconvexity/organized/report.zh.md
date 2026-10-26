> **公开展示副本。** 本地标识已替换为固定别名，并筛查个人信息。冻结证据原清单见 [source-manifest.json](source-manifest.json)，实际公开文件与编辑记录见 [manifest.json](manifest.json)。下载的论文全文[未随包附送](materials/omitted-sources.md)。下文历史验证结论的范围不变；本次导出不新增证明审查或新颖性认证。

[mathlottery-expert-brief-v2]: #

# MathLottery 专家阅读报告

> 仅整理冻结证据，不新增验证或提升证明、新颖性等级。

## 专家速览

下文为导航摘要，不是完整证明。省略号表示显示截短；完整原文、历史记录和逐项证据见链接的冻结材料及标注的 JSON 路径。原文不自动翻译；历史失败不会因后续通过而消失。

来源任务: reviewed-source · 冻结版本: 9 · 2026-10-25T12:36:24.743503+00:00

快照 SHA-256: `df5a6ff472287d257aeb2d20f29b0e46aecbad19206a7c9a78d1d2c58bca4d78`

原题 SHA-256: `9b3d92fc177c85627a748a19f196d19acfcc809a7c617d4a53e2d82cd7e5e3b6`

[Evidence manifest](source-manifest.json) · [冻结审查材料（全部记录）][frozen-dossier]

[直接阅读完整报告](#完整整理报告) · [查看证据索引](#证据索引)

### 1. 原题与候选结论

**三次 Franel 多项式从 F\_8 起的逐系数对数凸性**

对整数 n&gt;=0 定义 F\_n(q)=sum\_{k=0}^n binom(n,k)^3 q^k ∈ Z&#91;q&#93;。原问题要求尾序列 (F\_n(q))\_{n&gt;=8} 是 q-log-convex；展开即：对所有整数 n&gt;=9、d&gt;=0，&#91;q^d&#93;(F\_{n-1}(q)F\_{n+1}(q)-F\_n(q)^2)&gt;=0。中心下标是 n&gt;=9，不是 n&gt;=8；q为形式变量。

[/problem/statement][frozen-dossier]

开放状态: `UNKNOWN` · 核查日期: 2026-10-23T05:28:55.885172+00:00

[原始出处](https://arxiv.org/html/2505.02767v4)

**candidate-record-002** · `SELF_CHECKED` · scope `COMPLETE`

SHA-256: `693a09a4ede1e970f3060e6491480231492b2b0e62ea7e8d8d3a49e3341c88be` · 含审查快照: `2f22f64a69440461e3e0fc45f96eeed38ebcee5616ed2b4c872d6a066711f91a`

令 F\_n(q)=sum\_{k=0}^n binom(n,k)^3 q^k。对所有整数 n&gt;=9、d&gt;=0，有 &#91;q^d&#93;(F\_{n-1}(q)F\_{n+1}(q)-F\_n(q)^2)&gt;=0；更强地，当 1&lt;=d&lt;=2n-1 时该系数严格为正，在 d=0、d=2n 或 d&gt;2n 时为零。因此原题从 F\_8 开始的尾序列逐系数 q-log-convex。

[/candidates/0][frozen-dossier]

假设: n、d 为整数，n&gt;=9、d&gt;=0；q 为形式变量。; F\_n(q)=sum\_{k=0}^n binom(n,k)^3 q^k；二项式系数越界取零。; 没有附加猜想、渐近假设或依赖有限 n 实验外推的条件。

**最新状态**: `NO_ISSUES_FOUND` · 原题覆盖=`FULL` · Lean=`UNASSESSED` · 新颖性=`UNKNOWN`

### 2. 验证状态、关键步骤与历史失败

**candidate-record-002**

| 审查 | 判断 | 原题覆盖 | 新颖性 |
| --- | --- | --- | --- |
| 1 | `NO_ISSUES_FOUND` | `FULL` | `UNKNOWN` |

保留 1 项历史失败/未决检查，详见证据索引；后续通过未删除历史记录。

最新论证审查: 所提交文字证明是自包含的完整代数证明。已独立推导换下标消去、卷积归一化、正性与范围衔接，并直接从提交正文提取四张大次数表和十五张低次数表，以两种精确多项式实现核对全部恒等式；没有读取求解历史，也没有依赖候选自报的检查程序。全部数学关键步骤通过，奇数d的半整数参数和d=n的边界均包含。所附Lean仅定义猜想和做有限求值；本地重编译因缺Mathlib失败，故没有 …

原题对应: 原题精确要求F\_n(q)=Σ C(n,k)^3q^k的尾序列n≥8为q-log-convex，等价于中心n≥9、每个整数d≥0的c\_{n,d}≥0。候选使用完全相同的对象和量词，并证明更强的内部严格正性及全部零系数位置。独立审查确认回文约化后的1≤d≤n被d≤15和d≥16两段完全覆盖；不存在仅处理固定d、有限n或q= …

新颖性说明: 原非负性主命题已由Sun在2024年公开提出，并在2026-02-10的论文v4中明确列为猜想；这些出处不构成已知证明。此次20项实际检索及原始文献比较未发现覆盖该完整立方尾序列结论的已证定理。最接近的平方Narayana、加权超几何多项式、q=1数值Franel以及rising …

覆盖策略: `UNASSESSED` · proof_complete=False · statement_aligned=False

关键步骤覆盖尚未评估，不能从通过标签推断完整性。

未记录结构化证明路线，需从完整材料重建。

[/candidates/0/reviews/0][frozen-dossier]

未记录独立 Lean 执行回执。

形式检查仅覆盖回执声明；自然语言原题与形式命题等价性未经外部认证。

### 3. 文献障碍与新颖性

按稳定 ID、类型、来源归并；不同来源保留独立条目。历史状态保留，不代表所有旧问题仍未解决。每项链接标注冻结 JSON 路径。

证据策略: evidence-v2

没有列出的具体障碍不代表检索穷尽或新颖性已确认。

证据索引保留全部 0 个障碍条目、0 项已有结果对照及 13 项其它缺口/范围限制；未解除项的来源与比较仍需逐项检查。

### 4. 专家优先检查与材料入口

1. 阅读完整证明并复核关键引理、量词和边界；以上摘录不替代逐步检查。
2. 逐项处理未解决障碍，比较最接近的已有定理。
3. LLM 审查和有限测试不构成普遍定理的证明。

## 证据索引

以下是原始记录的位置索引，不重复完整证明或文献引用；完整内容见冻结 dossier。可[跳至完整整理报告](#完整整理报告)。

### 历史问题与失败检查

**candidate-record-002**

- check-15 · UNRESOLVED · blocking=False · 审查 1: 本地重新编译所附 Lean 源码。 — 实际使用Lean 4.35.0尝试编译所附原始字节，报unknown module prefix 'Mathlib'，本地模块搜索路径缺依赖。因此不能声称重新编译成功，也没有形式检查回执。源码本来就没有待审定理的证明，故不请求把其Prop定义当作theorem … · [/candidates/0/reviews/0/checks/14][frozen-dossier]

### 文献障碍历史（全部 ID）

**其它检索缺口与范围限制（去重，全部保留）**

| 摘要 | 完整记录 |
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

### 材料入口与范围限制

**证明与审查** (4): [dossier.json](materials/reviewed-source/dossier.json) · [answer.md](materials/reviewed-source/tasks/task-record-002/attempt-record-002/answer.md) · [dossier.json](materials/solver-source/dossier.json)

**形式化** (0): —

**文献** (7): [420c3f8ccfa26cb393d1f401c628667d042902b02bae0c10648a5cfe65eed0cf.json](materials/reviewed-source/literature/receipts/420c3f8ccfa26cb393d1f401c628667d042902b02bae0c10648a5cfe65eed0cf.json) · [6cf136a4f1583b1200993b61ec664cb96012453cdc3ac08e14792f56e15a08ff.json](materials/reviewed-source/literature/receipts/6cf136a4f1583b1200993b61ec664cb96012453cdc3ac08e14792f56e15a08ff.json) · [86e133a57f3135e3a9f0152f1439a721a5ceec4a1e29b8f1fcefcba104b6c8f7.json](materials/reviewed-source/literature/receipts/86e133a57f3135e3a9f0152f1439a721a5ceec4a1e29b8f1fcefcba104b6c8f7.json)

全部材料路径、哈希及遗漏项见证据清单。

- This is an editorial reconstruction of visible saved evidence, not hidden reasoning, an independent mathematical verification, or a certification of novelty.

- reviewed-source: only saved answers, named notes, proof/formal files and source receipts are included; arbitrary workspace files, binaries and caches are excluded.

- solver-source: only saved answers, named notes, proof/formal files and source receipts are included; arbitrary workspace files, binaries and caches are excluded.

- The linked solver is frozen at the revision shown in this manifest, which may include work saved after the review. The original reviewed candidate is matched exactly; later work is not retroactively verified.

未纳入材料：2 项，详见清单 omitted。

[frozen-dossier]: materials/reviewed-source/dossier.json

[mathlottery-expert-brief-v2-end]: #

---

## 完整整理报告

# 三次 Franel 尾序列的逐系数对数凸性：冻结证明与审查证据的专家报告

## 专家速览与摘要

**精确原题。** 对整数 \(n\ge0\)，令 \(F_n(q)=\sum_{k=0}^n\binom nk^3q^k\in\mathbb Z[q]\)，其中 \(q\) 是形式变量。要求尾序列 \((F_n)_{n\ge8}\) 逐系数对数凸，即所有整数 \(n\ge9,d\ge0\) 满足 \(c_{n,d}=[q^d](F_{n-1}F_{n+1}-F_n^2)\ge0\)。中心下标是 **9**，不是 8。本报告覆盖 Sun 猜想 1.1(i) 的第一分句，不覆盖同条中的其他多项式。[L1] [M5]

**已保存的证明主张及证据等级。** 完整书面候选还主张：\(1\le d\le2n-1\) 时严格为正；\(d=0,2n\) 及 \(d>2n\) 时为零。保存的 LLM 审查为 `NO_ISSUES_FOUND`，原题覆盖评价为 `FULL`，候选等级为 `SELF_CHECKED`。这表示有完整候选及支持它的审查记录；没有外部专家认证、候选全定理的 Lean 证明或成功内核回执。原题历史 `status=UNKNOWN`、`scope_relation=UNKNOWN` 及最终 `novelty=UNKNOWN` 均保留。数学正确性、原题覆盖和新颖性是不同判断。[M1]

**已有结果与最弱核验环节。** 已保存文献比较涉及平方二项式多项式、\(q=1\) 的数值 Franel 序列及另一 rising-binomial 族，均未被记录为覆盖本候选的已证结果。证明最需要专家审计的是大次数的表格恒等式 (4) 和十五个低次数恒等式 (6)：完整数据仍在，但原复算源码和日志未进入冻结包。审查文字报告过完整系数比较，不能将这种报告冒充本次重新执行或 Lean 检查。文献获取还存在未解除的控制器回执缺口。[M1] [M10] [M11]

**先看哪些证据。** 决定性数学内容在 [M1] 的 `candidates[0].proof`（本报告附录 A、B完整转录其系数）及 `reviews[0].checks[6]`、`checks[8]`；形式化限制在 `checks[14]`；新颖性限制在 `evidence_assessment` 和 [M10]、[M11]。以下正文把原候选的有限和推导展开为可逐步阅读的引理，并保留原式 (1)–(7)。这是基于可见材料的编辑性重构，没有重新 Solve、Verify、检索或编译，没有补造缺失步骤、修复方案或隐藏研究历史。

## 1. 冻结来源、状态与阅读约定

冻结清单捕获于 2026-10-25 12:36:24 UTC，列出 11 个文件。清单明确将已审查结果关联到一份 Solve 来源；两份档案的候选主张、证明、假设、引用、范围和待证义务相同，记录的候选 SHA-256 均为 `693a09a4ede1e970f3060e6491480231492b2b0e62ea7e8d8d3a49e3341c88be`。所选候选的快照哈希另为 `2f22f64a69440461e3e0fc45f96eeed38ebcee5616ed2b4c872d6a066711f91a`。本报告只采用该明确关联，不由同名或同哈希推测其他会话。[M1] [M2]

| 保存字段 | 原值及解释 |
|---|---|
| 原题 `status`、`scope_relation` | 均为 `UNKNOWN`；`source_statement`、`scope_description` 为空，`formal_target=null`。不能追填历史认证。 |
| Solve 候选 | `scope=COMPLETE`、`level=CANDIDATE`、`remaining_obligations=[]`，没有审查。 |
| 已审查候选 | `scope=COMPLETE`、`level=SELF_CHECKED`。 |
| 审查结论 | `verdict=reported_verdict=NO_ISSUES_FOUND`；`issues=[]`；`original_problem_coverage=FULL`；`remaining_obligations=[]`。这些是保存的 LLM 评价。 |
| 新颖性 | `novelty=UNKNOWN`，而 `reported_novelty=POTENTIALLY_NEW`；积极的文字评价没有改变最终字段。 |
| 结构化证明覆盖 | `proof_steps=[]`、`statement_alignment=[]`；`proof_coverage` 没有评估时间或策略版本，总步骤数为 0，`proof_complete=false`、`statement_aligned=false`、`formal_alignment_certified=false`。这是未建立结构化认证的记录，不是一个数学反例。 |
| 形式化与外部证据 | `formal_check=null`、`formal_receipt=null`；没有外部专家审查证据。 |

原题的历史范围关系 `UNKNOWN` 与审查的文字覆盖评价 `FULL` 分属不同字段，应并存。不能把前者改成已获认证，也不能把后者隐去。本报告的定理和引理名称用于组织已经提交的论证，不构成新的验证结论。

原始 16 项检查的 `id` **全部为空字符串**。下文 **R01–R16 是编辑定位号**，依次对应 [M1] 中 `candidates[0].reviews[0].checks[0]` 至 `checks[15]`，并非补造的原始检查 ID。

## 2. 原题、记号与证明路线

Sun 的 2026-02-10 版本在猜想 1.1(i) 第一分句明确提出该尾序列问题；正文前面的定义给出逐系数对数凸的含义。保存的历史归属还指向 Sun 于 2024-09-21 06:18:37 UTC 发布的 MathOverflow 评论 1247286，但该网页的控制器获取仍失败。Sun 正文紧前的 “remains open” 指的是另一 \(\beta_n\) 序列，不能移用为本题的新近状态证明。[L1] [L2] [M5] [M10]

**定理 1（所提交且获 LLM 审查支持的主张；等级仍为 SELF_CHECKED）。** 定义

\[
F_n(q)=\sum_{k=0}^{n}\binom nk^3q^k,
\qquad \Delta_n(q)=F_{n-1}(q)F_{n+1}(q)-F_n(q)^2,
\qquad c_{n,d}=[q^d]\Delta_n(q).
\]

则候选主张，对所有整数 \(n\ge9,d\ge0\)，

\[
c_{n,d}
\begin{cases}
>0,&1\le d\le2n-1,\\
=0,&d=0,\ d=2n,\ \text{or }d>2n.
\end{cases}
\]

这里 \(\binom ak=0\) 当 \(k<0\) 或 \(k>a\)，其中上标 \(a\) 为非负整数；空积为 1。所有求和均有限，不涉及收敛性。参数 \(h,x_k\) 可为半整数；这不改变 \(n,d,k\) 的整数要求，也不把 \(q\) 改为数值变量。

证明依赖关系是：引理 1 把原题化为 \(1\le d\le n\)；引理 2–6处理 \(n\ge d\ge16\)；引理 7处理 \(1\le d\le15\)、\(n\ge\max(9,d)\)；引理 8拼接全部量词。大次数部分通过两个加权和为零的恒等式，将不易直接判号的卷积变为显式正项和。小次数部分使用有限张**多项式恒等式**，每张覆盖无界的 \(n\)。文献比较与有限实验均不是这条数学依赖链的前提。

## 3. 逐步证明的忠实展开

以下推导来自候选正文及 R01–R12 的保存说明。为便于审计，换下标和归一化的中间等式作了编辑展开；没有替换原证书或增补新引理来修补它。大表恒等式的执行结果只按历史记录陈述。

### 引理 1：卷积、回文性与全部边界（R01–R03）

令 \(P_j=F_{j+8}\)。尾序列的定义要求每个 \(j\ge1\) 的 \(P_{j-1}P_{j+1}-P_j^2\) 逐系数非负，因此中心恰为 \(n=j+8\ge9\)。多项式乘法给出

\[
c_{n,d}=\sum_{k=0}^{d}
\left(\binom{n-1}{k}^{3}\binom{n+1}{d-k}^{3}
-\binom nk^{3}\binom n{d-k}^{3}\right).
\]

越界取零保证该式也包含端点。又因为二项式系数对称，

\[
q^nF_n(q^{-1})=F_n(q),\qquad
c_{n,d}=c_{n,2n-d}\quad(0\le d\le2n).
\]

这里的 \(q^{-1}\) 只是在 Laurent 多项式中表达回文关系。两个乘积都以 \(2n\) 为回文长度；不是说差多项式的 \(q^{2n}\) 系数非零。它们的常数项和最高次项均为 1，故 \(c_{n,0}=c_{n,2n}=0\)；次数上界又给出 \(d>2n\) 时为零。因此只剩 \(1\le d\le n\) 的严格正性。

### 引理 2：大次数参数与正权重（R04）

在 \(n\ge d\ge16\) 中设

\[
N=n+1,\quad h=d/2,\quad z=N-d,\quad m=h+z=N-h,
\quad H=h-8,\quad Z=z-1,
\]

\[
x_k=k-h,\qquad W_k=\binom Nk^3\binom N{d-k}^3
\quad(0\le k\le d).
\]

有 \(N=2h+z=h+m\)、\(h\ge8\)、\(z\ge1\)、\(H,Z\ge0\)。因为 \(d\le N-1\)，所有这些 \(W_k\) 严格为正，相邻权重比值不对零作除法。\(d=n\) 对应允许的 \(z=1,Z=0\)；奇数 \(d\) 只使 \(h,x_k\) 为半整数。

### 引理 3：两个无余项的有限和恒等式（R05）

定义独立变量 \(x\) 的多项式

\[
\begin{aligned}
A(x)&=(m-x)^3(h-x)^3,\\
B(x)&=(m+x)^3(h+x)^3,\\
S_0(x)&=A(x)(2x+1)-B(x)(2x-1),\\
S_1(x)&=A(x)(2x+1)^3-B(x)(2x-1)^3.
\end{aligned}
\]

在求和点，\(A(x_k)=(N-k)^3(d-k)^3\)、\(B(x_k)=(N-d+k)^3k^3\)，而

\[
\frac{W_{k+1}}{W_k}
=\left(\frac{(N-k)(d-k)}{(k+1)(N-d+k+1)}\right)^3,
\qquad W_kA(x_k)=W_{k+1}B(x_{k+1})\quad(0\le k<d).
\]

端点满足 \(A(x_d)=B(x_0)=0\)。对 \(r=1,3\)，换下标的过程为

\[
\begin{aligned}
\sum_{k=0}^d W_k B(x_k)(2x_k-1)^r
&=\sum_{k=1}^d W_k B(x_k)(2x_k-1)^r\\
&=\sum_{j=0}^{d-1}W_j A(x_j)(2x_j+1)^r\\
&=\sum_{j=0}^{d}W_j A(x_j)(2x_j+1)^r.
\end{aligned}
\]

第二步使用 \(2x_{j+1}-1=2x_j+1\)，首尾两步使用上述零端点。因此

\[
\sum_{k=0}^{d}W_kS_0(x_k)=
\sum_{k=0}^{d}W_kS_1(x_k)=0.\tag{1}
\]

这只依赖二项式相邻关系，并未使用待证正性。

### 引理 4：卷积的精确归一化（R06）

设

\[
\begin{aligned}
P(x)={}&N^3\big((m-x)^3(m-x-1)^3
                    +(m+x)^3(m+x-1)^3\big)\\
&-2(N-1)^3(m^2-x^2)^3,\\
\ell={}&[N(m-1)]^2+N(m-1)(N-1)m+[(N-1)m]^2.
\end{aligned}
\]

由于

\[
\binom{N-2}{k}=\binom Nk\frac{(N-k)(N-k-1)}{N(N-1)},
\qquad
\binom{N-1}{k}=\binom Nk\frac{N-k}{N}
\]

卷积的两种乘积可分别写成

\[
\binom{N-2}{k}^{3}\binom N{d-k}^{3}
=\frac{W_k(m-x_k)^3(m-x_k-1)^3}{N^3n^3},
\]

\[
\binom{N-1}{k}^{3}\binom{N-1}{d-k}^{3}
=\frac{W_k(m^2-x_k^2)^3}{N^6}.
\]

利用 \(W_{d-k}=W_k\)、\(x_{d-k}=-x_k\)，把第一项与换下标后的自身平均，再统一分母，得到

\[
c_{n,d}=\frac{1}{2n^3N^6}\sum_{k=0}^{d}W_kP(x_k).\tag{2}
\]

\(n=d,k=d\) 时因子 \(m-x_k-1=0\)，恰好对应 \(\binom{n-1}{d}=0\)；没有丢掉这一边界。分母中的 \(n,N\) 都严格为正。

### 引理 5：大次数的代数证书（R07）

令 \(U,V,C,D\in\mathbb Z[H,Z]\) 由附录 A 的四张表完整定义。每个列出的系数及每个常数项均严格为正，所以

\[
U>0,\qquad V>0,\qquad C>0,\qquad D>0
\quad(H,Z\ge0).\tag{3}
\]

提交证书的核心恒等式是

\[
\begin{aligned}
4h^2UP(x)+4\ell U S_0(x)-NV\big(S_1(x)-S_0(x)\big)
=24N\big(hm^3Cx^2+Dx^6+(2N-1)Vx^8\big).
\end{aligned}\tag{4}
\]

代入 \(N=2h+z,m=h+z,H=h-8,Z=z-1\) 后，这是多项式恒等式，等价于全部单项式系数相等；不是有限参数点上的拟合。R07 记载审查者从候选正文取表，分别用标准库稀疏有理多项式运算及 SymPy 1.14.0 在 \(\mathbb Z[H,Z,x]\) 中展开，全部差系数为零；约简后的左右两侧各有 210 个非零单项式。原程序和输出未冻结，本报告没有重跑此计算。

保存的 R07 还说明了证书的消项结构。令 \(T=hm\)，则

\[
A(x)=(T+x^2-Nx)^3,\qquad B(x)=(T+x^2+Nx)^3,
\]

\[
U=-\frac{[x^4](S_1-S_0)}8
=N^3+3(2N-3)T^2-3N(3N-2)T,
\qquad h^2[x^4]P+\ell[x^4]S_0=-2NV.
\]

因此 (4) 左端的 \(x^4\) 系数相消；奇次项由对称性消失。常数项相消、\(x^8\) 项吻合及 \(x^2,x^6\) 的剩余恒等式也被 R07 记为已展开核对。这解释了为何右端只留适合判号的偶次幂，但不能替代对整张证书的审计。

### 引理 6：大次数的显式正项和（R08）

把 (4) 乘以 \(W_k\)，取 \(x=x_k\) 后求和。由 (1)，两个修正项消失，故

\[
4h^2U\sum_{k=0}^dW_kP(x_k)
=24N\sum_{k=0}^dW_k\big(hm^3Cx_k^2+Dx_k^6+(2N-1)Vx_k^8\big).
\]

再代入 (2)，得到候选的正项和公式

\[
\boxed{
c_{n,d}=\frac{3}{n^3N^5h^2U}
\sum_{k=0}^dW_k\big(hm^3Cx_k^2+Dx_k^6+(2N-1)Vx_k^8\big).
}\tag{5}
\]

前因子来自 \(24N/(4h^2U\cdot2n^3N^6)\)，不存在额外的 2 或 \(N\)。所有标量系数正，偶次幂非负。取 \(k=0\)，有 \(x_0=-h\ne0\)、\(W_0=\binom Nd^3>0\)。仅保留其二次项便得到 R08 保存的下界

\[
c_{n,d}\ge\frac{3\binom Nd^3 h m^3C}{n^3N^5U}>0.
\]

这覆盖每个 \(n\ge d\ge16\)，包括 \(H=0\)、\(Z=0\) 及奇数 \(d\)。偶数 \(d\) 可能有一个 \(x_k=0\) 项，但不影响上述严格正项。

### 引理 7：十五个低次数恒等式及其正性（R09–R10）

对 \(1\le d\le15\)，令 \(s_d=\max(9,d)\)，并定义

\[
\begin{aligned}
B_{2r+1}(n)&=n\prod_{j=1}^r(n-j)^3\quad(r\ge0),\\
B_{2r}(n)&=n(n-r)\prod_{j=1}^{r-1}(n-j)^3\quad(r\ge1).
\end{aligned}
\]

附录 B 给出 \(a_d>0\) 和正整数系数多项式 \(R_d\)，使

\[
c_{n,d}=a_dB_d(n)R_d(n-s_d),\qquad 1\le d\le15.\tag{6}
\]

为什么这是无界 \(n\) 的论证：设 \((t)_{\underline k}=\prod_{j=0}^{k-1}(t-j)\)。把引理 1的每个二项式写成下阶乘除以阶乘，再用 \(d!/(k!(d-k)!)=\binom dk\)，得到

\[
\begin{aligned}
(d!)^3c_{s_d+y,d}=\sum_{k=0}^d\binom dk^3
\big[&((s_d+y-1)_{\underline k}
       (s_d+y+1)_{\underline{d-k}})^3\\
&-((s_d+y)_{\underline k}
       (s_d+y)_{\underline{d-k}})^3\big].
\end{aligned}\tag{7}
\]

因此只需把 (6) 的右端乘以 \((d!)^3\)，与 (7) 比较 \(y\) 的所有系数。R09 记录两种精确实现对全部十五张表均得零剩余，左侧次数依次为 \(3d-2=1,4,\ldots,43\)。这与抽查十五个 \(n\) 完全不同；有限的是 \(d\) 的列表，恒等式中的 \(y\) 没有上界。原始输出缺失的限制同引理 5。

对所需整数 \(n\ge s_d\)，有 \(y\ge0\)，每个 \(R_d(y)>0\)，且 \(B_d(n)\) 中每个因子正；于是 (6) 严格为正。\(d=1\) 用空积给出 \(B_1=n,R_1=1,a_1=6\)，即 \(c_{n,1}=6n\)。当 \(n=d\) 时，(7) 中应越界的下阶乘含零因子，仍与卷积一致。

### 引理 8：量词拼接及定理 1的结论（R11）

对任意 \(n\ge9\) 和内部次数 \(1\le d\le2n-1\)，置

\[
e=\min(d,2n-d),\qquad 1\le e\le n.
\]

若 \(e\le15\)，则 \(n\ge\max(9,e)\)，适用引理 7；若 \(e\ge16\)，则适用引理 6。再由引理 1得 \(c_{n,d}=c_{n,e}>0\)。其余次数已在引理 1中处理。特别地，\(n=9\) 的半区全由低次数表覆盖，\(d=15\) 与 \(d=16\) 之间没有缺口，\(d=n\) 没有被排除。这样给出所提交论证的完整结论，而非固定次数、有限 \(n\)、仅偶数次数或仅 \(q=1\) 的分支结论。

**命题 2：起点的阈值核对（R12；书面推导层级）。** 对整数 \(n\ge2\)，

\[
\begin{aligned}
c_{n,2}
&=\binom{n-1}{2}^3+\binom{n+1}{2}^3
+(n-1)^3(n+1)^3-2\binom n2^3-n^6\\
&=\frac34n(n-1)(n^2-9n+6).
\end{aligned}\tag{8}
\]

代入得到 \(c_{8,2}=-84\)、\(c_{9,2}=324\)。从 \(F_7\) 开始的尾序列包含失败中心 \(n=8\)，所以不能把定理 1的中心放宽到 8。结合定理 1，这给出这些整数起点尾序列的起点锐性解释；它没有单独的 Lean 最优性定理。内部严格正性、等号位置及这一阈值均只有上述书面证明和所记录的代数/实验审查支持。冻结候选没有证明其他幂次、其他多项式或强 \(q\)-对数凸性的推广。

## 4. 每项主张与记录检查的对应

下表中的 `SUPPORTED`、`UNRESOLVED` 都是历史记录，本次未重做。R01–R11 被记录为必要检查；R12–R16 的 `blocking=false`。全部原始检查 ID 为空。[M1]

| 编辑定位号 | 内容及方法 | 保存结果与本报告位置 |
|---|---|---|
| R01 | 原题重编号、对象和量词；DERIVATION | SUPPORTED；引理 1、定理 1。 |
| R02 | 系数有限卷积；DERIVATION | SUPPORTED；引理 1。 |
| R03 | 回文与零端点、支撑外；DERIVATION | SUPPORTED；引理 1。 |
| R04 | 参数域、权重、半整数；DERIVATION | SUPPORTED；引理 2。 |
| R05 | 有限和换下标；DERIVATION | SUPPORTED；引理 3、式 (1)。 |
| R06 | 对称平均与归一化；DERIVATION | SUPPORTED；引理 4、式 (2)。 |
| R07 | 两种实现的完整多项式比较；DERIVATION | SUPPORTED；引理 5、式 (4)、附录 A；脚本与日志未冻结。 |
| R08 | 正项和与严格正项；DERIVATION | SUPPORTED；引理 6、式 (5)。 |
| R09 | 十五个完整多项式比较；DERIVATION | SUPPORTED；引理 7、式 (6)–(7)、附录 B；脚本与日志未冻结。 |
| R10 | 低次数各因子正性；DERIVATION | SUPPORTED；引理 7。 |
| R11 | 两段拼接、全部量词；DERIVATION | SUPPORTED；引理 8。 |
| R12 | 二次系数和起点反例；DERIVATION | SUPPORTED；命题 2。 |
| R13 | 精确整数卷积及五组连接实验；FINITE_TEST | SUPPORTED；仅辅助测试，不证明一般定理。 |
| R14 | 附带 Lean 文件的证据范围；DERIVATION | SUPPORTED；仅定义与求值，没有全称定理证明。 |
| R15 | Lean 4.35.0 本地重编译；FORMAL | UNRESOLVED；缺 Mathlib，未成功编译，无形式回执。 |
| R16 | 先前结果及不同族反例的比较；REFERENCE | SUPPORTED 为审查者评价；控制器仍有文献获取失败。 |

R13 记录对 \(n=9,\ldots,100\) 的全部 \(d=0,\ldots,2n\) 检查了 10120 个支撑内系数，并对每个 \(n\) 另验 \(d=2n+1\)。内部全正、端点和支撑外为零、回文性均与候选相符；另有五组参数检查相邻关系、式 (1)、(2)、(5)，含奇数 \(d\) 和 \(d=n\)，但具体五组参数未在可见记录中列出。不能虚构其取值。[M1]

Solve 答复自报三项纯整数代数测试通过，正文还说明四组精确有理数代入用于检查归一化和半整数参数；与 Verify 的五组实验应区别记录，不能拼成更多独立验证。Find 继承信息中另有 \(n=1,\ldots,100\) 的实验及 \(-84,324\) 的探针求值。这些只有相应保存文字，没有本包中的可执行程序或完整运行输出。[M2] [M4]

## 5. Lean、回执与哈希能支持什么

**真正有成功 Lean 定理检查回执的本候选定理清单：空。** 16 项检查的 `formal_declarations` 都为空；没有请求或回执列出一个被内核证明的主定理。不能把文献下载回执当作形式证明回执。[M1]

| 对象 | 冻结记录实际说明 | 不能推出的结论 |
|---|---|---|
| `FindProbes.FranelConjecture` | R14称其为 `CoeffwiseLogConvexFrom franel 8` 的 Prop 定义，条件为 `8<n`。继承的 Find 描述曾称 elaboration 通过。 | 定义一个命题不等于证明该命题；没有本候选绑定的成功回执。 |
| `deltaCoeff` | 可执行有限和；继承记录提及 \(-84\)、\(324\) 的求值。 | 没有与 `Polynomial.coeff` 的等价定理，也没有全称正性定理。 |
| `StatementProbes.lean` | R14记载源码哈希 `8a00d28b653669be3158f996cbd0164614491887a7a101851af0a67b21f10a4a`；源码被清单明确排除。 | 当前不能检查其原始字节；该哈希本身不证明声明语义或编译成功。 |
| 本地编译尝试 | R15记录 Lean 4.35.0 报 `unknown module prefix 'Mathlib'`；结果 UNRESOLVED。 | 不能写成编译通过；这也不是对书面恒等式的反驳。 |
| 定理 1、严格正性、等号和阈值 | 书面候选和审查支持。 | 没有对应的 Lean 定理声明、依赖闭包或内核回执。 |

两种题目哈希必须分域理解：题面 `Problem.statement` 的 UTF-8 SHA-256 是 `2275c68fbb750017200eb777926cbcdcc2a9b40ec6f59017e67ad69057bbd192`；组织清单对完整规范化 Problem 记录的指纹是 `9b3d92fc177c85627a748a19f196d19acfcc809a7c617d4a53e2d82cd7e5e3b6`。两者输入不同，数值不同不是错配。原网页/PDF 的哈希与其导出文本的清单哈希也属不同字节对象。本包没有形式回执可用于候选匹配，因此不存在可宣称的匹配成功；也不能凭空报告一个实际发生的形式回执哈希冲突。缺失或错配的回执均不能支持候选，哈希一致本身也不能认证自然语言与形式陈述的对应。

## 6. 原问题覆盖、已有文献与新颖性障碍

在所提交的数学论证层面，定义、整数域、\(n\ge9\)、全部 \(d\ge0\)、形式变量、边界零系数和严格内部正性均明确处理；这是 R01–R11 及保存 `FULL` 评价的依据。原题只要求非负性，严格正性是加强，不是缩小原题。但结构化陈述对齐列表为空，原题历史 `scope_relation=UNKNOWN`，没有外部自然语言/形式陈述等价认证。这三层信息不能合并成一次新的范围认证。

| 来源及保存定位 | 记录中的结果或命题 | 与本题的关系及证据限制 |
|---|---|---|
| Sun，2026，猜想 1.1(i) 第一分句 [L1] | 同一 \(F_n\)、尾序列从 8 起的非负性猜想。 | 原题非负性部分等价；完整候选因严格性而更强。审查引用的 `DIFFERENT` 是比较完整加强主张，并非题目变了。正文与成功文本回执均保存。[M5] [M7] |
| Sun，2024，评论 1247286 [L2] | 保存记录将同一猜想最早实读公开提问归于该评论。 | 审查者称取得全文，但控制器回执 UNAVAILABLE，不能写成独立来源核验完成。[M10] |
| Chen–Tang–Wang–Yang，2010，式 (1.1)、定理 1.1及后文 [L3] | \(W_n(q)=\sum_k\binom nk^2q^k\) 的完整序列逐系数对数凸；完整幂次序列在幂至少 3时不具此性质。 | 平方与立方不同；完整序列失败不否定尾序列。R16举 \(c_{2,2}=-12\)，在本题域外。成功摘录回执保存，但 PDF 与提取正文未随包提供。[M8] |
| Zhu–Sun，2015，定理 2.1、推论 2.9 [L4] | \(P_n(q)=\sum_k\binom nk^2\binom{2k}kq^k\) 的强逐系数对数凸性及保持性条件。 | \(P_2=1+8q+6q^2\ne F_2=1+8q+q^2\)。保持性定理的固定输入权重不能随意换成依赖 \(n\) 的 \(\binom nk\)。原文未冻结，EMIS 回执 UNAVAILABLE。[M11] |
| Došlić，§4推论 3 [L5] | 数值 \(F_n^{(r)}=\sum_k\binom nk^r\)，\(r=3,4\) 为 log-balanced。 | 按 §2定义，这包含序列对数凸及除以 \(n!\) 后对数凹；只给 \(q=1\) 数值信息，不能推出每个系数的符号。正文与成功回执均保存。[M6] [M9] |
| Zhou，2026-07-24，回答 513542 [L2] | \(\sum_k\binom{n+k}k^m q^k\) 在 \(m=5\)、中心 \(n=7\) 的反例，二次系数 \(-499140\)。 | 权重及量词均不同。R16记录重新计算该值，但网页独立回执仍失败；不构成本题的反例或解答。[M10] |

这些文献不是候选代数证明的外部前提。已记录的比较不把候选判为任何上述定理的 `SPECIAL_CASE`，也不声称穷尽未知变量变换或同名多项式的所有定义。

**必须保留的证据差异。** 审查 `literature_search.conclusion` 和 `novelty_notes` 称相关原文已取得、具体障碍已解决，并将 `unresolved` 留空；但是控制器的 `evidence_assessment.supported=false`，明确列出 MathOverflow、EMIS 的 robots 策略获取失败，且对应摘录 `verified_excerpt=false`。后者有实际失败回执 [M10] [M11]，所以不能照抄前者而宣称障碍解除。继承的 Find 记录还保存 Stack Exchange API 的 robots 端点 `HTTP400 no_method` 及原作者旧主页书目获取不足；研究端 GET200 不能替代控制器独立回执。这些失败仍作为历史证据保留。[M1] [L6] [L7]

审查保存 20 项查询，覆盖主要英文索引、少量中文词、arXiv、作者公开问题页及所列论文，检索时点为 2026-10-23。没有覆盖所有语言、数据库、引用网络、未索引或未公开工作。最新实读的作者明确猜想版本仍为 2026-02-10，没有更晚的专门开放状态重申。因而“未发现已有证明”和 `POTENTIALLY_NEW` 都不是首解、优先权或当前全球开放状态认证，最终 `UNKNOWN` 保持不变。

## 7. 尚缺材料与复现边界

保存的审查未指出阻塞性数学缺口，候选和审查的 `remaining_obligations` 均为空。这并不消除证据缺失：没有外部专家意见或形式化全定理；大表复算原代码、日志和依赖环境不能从本包重放；若将来对证书发现问题，应另开 Solve/Verify，不能由本次编辑悄悄修补。这里不提出新的证明修复。

两个档案的 `visible_research_notes=[]`。候选提到的 `proof.zh.md`、`certificate.json`、`check_certificate.py`、`test_certificate.py` 未列入清单；完整证明和系数表幸而仍在 JSON 的 `proof` 字段。审查提到的 `review.md`、`check_algebra.py`、`algebra_results.json`、`test_connections.py`、代数/pytest/ruff/Lean 日志、检索和下载日志也未冻结。重复指向原始事件文件的 evidence 条目不等于多个独立检查，事件文件本身未提供。不能从这些文件名推测执行细节或失败尝试。

另外，清单明确排除 Lean 源码，并将 Chen 等论文的提取文件以 binary content 原因省略；原 PDF 也不在文件列表。MathOverflow、EMIS 与 API 原始正文未提供。Sun 和 Došlić 可读的导出文本在包内，但不能把它们当作原始网页字节。清单中的排除和缺失均不是本报告补做下载的授权或完成记录。

**可移植的阅读命令。** 以下从导出报告根目录运行，仅提取已经保存的证明与检查；是阅读模板，不是数学验证回执。导出布局中的这段命令未在本次执行。

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

**原数学复算的条件性模板，未执行。** 如果另行取得并核对原始源码，可在原证书目录尝试下列入口；这是依据文件名写的复现建议，不是冻结的原始命令行，也不是成功记录：

```bash
conda run -n mathlottery python check_certificate.py
conda run -n mathlottery pytest -q test_certificate.py
```

候选称其检查器只需 Python 标准库；审查另用 SymPy 1.14.0。具体环境锁定文件没有保存。完整重放应逐系数比较 (4) 和全部 (6)，并单独审计 (1)、(2)、正性与范围衔接；仅做数值抽样不能代替这些环节。Lean 重放须先恢复原源码、Mathlib、工具链和模块路径；本包没有成功命令可照录，也没有全称定理可供重放。为排版安装新依赖或重编译不会补出这种证明。本次只核对冻结文件与报告转录，不新增数学测试或形式回执。

## 8. 参考文献（仅冻结材料中的来源）

1. **[L1]** Zhi-Wei Sun, *A family of polynomials and related congruences and series*, arXiv:2505.02767v4，2026-02-10；*Frontiers in Combinatorics and Number Theory* 2 (2026), 1–22，DOI 10.3934/fcnt.2026009。定位：§1，猜想 1.1(i) 第一分句（档案注明 PDF 第3页）。可读文本 [M5]、成功回执 [M7]。另列的 arXiv PDF 未在包内。[L1PDF]
2. **[L2]** MathOverflow, *On the polynomials sum binom(n+k,k)^m q^k*，问题 479301。Sun 评论 1247286（2024-09-21）与 Qiping Zhou 回答 513542（2026-07-24）；正文获取成功为审查者文字主张，控制器回执失败 [M10]。
3. **[L3]** William Y. C. Chen, Robert L. Tang, Larry X. W. Wang, Arthur L. B. Yang, *The q-Log-convexity of the Narayana Polynomials of Type B*, *Advances in Applied Mathematics* 44(2) (2010), 85–110。定位：式 (1.1)、定理 1.1及其后完整幂次序列说明；成功回执 [M8]，原文缺失。
4. **[L4]** Bao-Xuan Zhu, Hua Sun, *Linear transformations preserving the strong q-log-convexity of polynomials*, *Electronic Journal of Combinatorics* 22(3) (2015), P3.26；保存日期 2015-08-28。定位：定理 2.1、推论 2.9，后者在 PDF 第9页；正文缺失，失败回执 [M11]。
5. **[L5]** Tomislav Došlić, *Log-balanced combinatorial sequences*, arXiv:math/0603403v1，公开提交日 2006-03-16。定位：§2定义及 §4推论 3。档案另记期刊年份为 2005；导出页面上的自动生成日期不能充当优先权日期。可读文本 [M6]、成功回执 [M9]。
6. **[L6]** 官方 Stack Exchange API：评论 1247286。继承 Find 记录的作者、时间与正文关联来源；本包无独立成功获取回执或原始 JSON。
7. **[L7]** 官方 Stack Exchange API：问题 479301 的回答。继承 Find 记录中用于区分 rising-binomial 反例的来源；同样保留 robots 获取失败，不当作已核验新来源。

## 附录 A. 大次数证书的完整数据

以下逐项转录所选候选，没有重新拟合。每个名字表示 \(T(H,Z)=\sum_j Z^j\sum_i a_{j,i}H^i\)；标签 \(j\) 从 0连续计数，指定对应的 \(Z\) 幂，每个数组内从 \(H^0\) 起升幂排列，未列出的项为零。数组换行仅为排版。这里 \(T\) 仅为表名的泛指，与引理 5临时记号 \(T=hm\) 区别。取 \(H=h-8,Z=z-1\)。四表用于式 (3)–(5)。[M1]

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

## 附录 B. 低次数证书的完整数据

每项列出 \(d,s_d,a_d\)，以及 \(R_d(y)\) 从常数项起升幂的系数。\(B_d\) 见引理 7。所有数据逐项转录同一候选；与附录 A 共 319 个正整数系数（不把 \(a_d\) 的分母计入系数表）。这些表是证明数据，不是运行日志。[M1]

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

## 附录 C. 可见研究进程与失败记录

| 时间（UTC） | 保存事件及其限度 |
|---|---|
| 2026-10-23 05:28前后 | 继承题目档案保留 Find 的题面核对、有限探针与 UNKNOWN 状态；中心 \(n=8,d=2\) 的 \(-84\) 否定错误放宽的范围，\(n=9,d=2\) 为 324。MathOverflow/API robots 失败及旧主页书目缺口仍在。没有另行导入 Find 会话历史。 |
| 2026-10-23 13:51:39–14:23:43 | 明确关联的 Solve：仅一个保存候选，COMPLETE/CANDIDATE；答复自报三项测试通过，并明确尚未独立验证。[M2] [M4] |
| 2026-10-23 14:36:40–15:02:00 | Verify：16项检查；15项 SUPPORTED，1项 FORMAL/UNRESOLVED（缺 Mathlib）。LLM评价 NO_ISSUES_FOUND/FULL，文字暂评 POTENTIALLY_NEW；最终新颖性 UNKNOWN，候选 SELF_CHECKED。MathOverflow、EMIS 独立获取失败。[M1] [M3] |
| 2026-10-25 12:36:24 | 组织清单冻结所选审查及明确关联的 Solve。清单警告来源修订可能含审查之后保存的工作，不能追认；本报告只采用匹配的原候选与显式审查。 |
| 本次 Organize | 只阅读冻结材料、组织证明并核对双语转录；没有重算证书、重编译 Lean、搜索新论文或变更证据等级。 |

没有可见的其他候选版本、放弃路线、失败求解草稿或隐藏推理记录，故不编造。已知的数学负例、形式化失败和来源获取失败均保留；没有把“未发现问题”或空的义务列表写成全球首解证明。

## 附录 D. 精简材料索引

这是供阅读数学论证的索引；完整文件核对和交接索引由控制器另行生成。所有链接都相对于导出报告的 `materials/`，只指向清单中实际提供的文件。

| 材料 | 用途 |
|---|---|
| [M1] 已审查档案 | 精确候选全文、16项检查、状态字段、文献摘录与证据评估；本报告的首要来源。 |
| [M2] 明确关联的 Solve 档案 | 同一证明候选、假设、原始自报范围；无审查、无可见研究笔记。 |
| [M3] Verify 保存答复 | 简洁审查结论；其中较积极的新颖性文字须与 [M1] 最终 UNKNOWN 一并读。 |
| [M4] Solve 保存答复 | 候选完成与三项测试的自报；其引用的程序文件未提供。 |
| [M5] Sun 导出文本 | 原题定义、猜想 1.1(i)、相邻不同命题和参考文献。 |
| [M6] Došlić 导出文本 | log-balanced 定义、数值 Franel 推论 3。 |
| [M7] Sun 来源回执 | OK；仅文本匹配，不认证解释或检索穷尽性。 |
| [M8] Chen 等来源回执 | OK；原 PDF/提取正文缺失，不能把回执当完整原文。 |
| [M9] Došlić 来源回执 | OK；仅文本匹配。 |
| [M10] MathOverflow 来源回执 | UNAVAILABLE；robots 策略未能核验。 |
| [M11] EMIS 来源回执 | UNAVAILABLE；robots 策略未能核验。 |

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
