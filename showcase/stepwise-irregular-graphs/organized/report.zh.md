> 公开展示版本：仅进行私人运行信息脱敏和相对路径整理；原有结论及证据等级不变。正文、附录及历史材料中的哈希和字节数指向原始冻结输入；脱敏、链接整理及来源说明会改变公开副本的字节。核对本目录中的文件时，请使用[出版清单](manifest.json)中 `files[].sha256` 与 `files[].bytes`，不要用正文或附录的原始哈希判断公开副本是否损坏。清单分别保留原始与公开文件的哈希、字节数。

# MathLottery 专家阅读报告

> 本文是对已有研究材料的整理，未经新增独立验证。排版和说明不提升证明等级，也不认证问题的开放状态或新颖性。

来源任务：`reviewed-source`；冻结版本：9；冻结时间：2026-10-24T04:21:35.242517+00:00。

## 原始验证记录

- `candidate-record-005` · `SELF_CHECKED` · scope `UNKNOWN`; verdict `NO_ISSUES_FOUND`, coverage `UNKNOWN`, novelty `UNKNOWN`

[Evidence manifest](manifest.json)

### 材料范围与限制

- This is an editorial reconstruction of visible saved evidence, not hidden reasoning, an independent mathematical verification, or a certification of novelty.
- reviewed-source: only saved answers, named notes, proof/formal files and source receipts are included; arbitrary workspace files, binaries and caches are excluded.
- This historical Verify has no saved solver linkage. The original Solve history is unavailable; matching titles or proofs were not used to guess it.

---

# 阶梯不规则图度数序列猜想的反例

**中文专家报告 · 文献证据冻结至 2026-10-21 · 编辑快照采集于 2026-10-24**

## 摘要与准确结论

保存的求解稿给出了 Bera–Paul–Subramanian 的论文 *Some properties of stepwise irregular graphs*（EJGTA 14(1)，2026）印刷页第 223 页猜想 1 的反例。度数序列

\[
d=(6^4,5^6,4^1,3^1,2^3,1^1)
\]

满足该充分条件猜想的每一项前提，并且有一个 16 顶点、34 边的普通简单连通二部图实现。然而，它没有阶梯不规则（stepwise irregular，简称 SI）图实现，即使取消连通性要求也不可能。在任何假设存在的 SI 实现中，三个度为 2 的顶点都只能邻接度为 1 或 3 的顶点，因而需要六个关联端点，而这两个邻层的总度数只有四。这个矛盾针对所有可能实现，不来自有界搜索。显式普通图则独立承担通常意义下的可图性证明。

候选的保存等级仍为 **`SELF_CHECKED`**。历史独立 AI 审查返回 **`NO_ISSUES_FOUND`**，新颖性为 **`UNKNOWN`**。旧版候选的 `scope` 与审查的 `original_problem_coverage` 均保持 **`UNKNOWN`**。普通证明所声称的是对完整全称猜想的否定；这一数学范围说明不是新获得的数据库 `FULL` 认证。本例**没有 Lean 形式化**，没有外部专家审稿，也没有外部原题陈述等价性认证。计数方法已有记录在案的 2022 年先例。[冻结 dossier，M1](materials/reviewed-source/dossier.json)；[历史审查保存答复，M2](materials/reviewed-source/tasks/task-record-003/attempt-record-004/answer.md)；[显式提供的展示版验证摘要，S7](materials/showcase/verification.json)。

## 1. 来源、溯源与编辑性质

原生冻结材料包含一份 dossier，其中嵌入原候选证明和一条结构化审查，以及一份审查最终答复。没有可见研究笔记或证据回执。清单明确记载：这次历史 Verify 没有保存 solver linkage，原 Solve 历史不可获得。本报告没有根据相似题名或证明文本猜造会话关联。Showcase 补充是明确另行提供的既有证据展示稿，不是原生 Verify 新增附件，也不是把后来取得的结果追记到较早审查中。

本报告忠实重组已经保存的数学论证。定理与引理编号、证明义务的拆分、已记录层间递推的展开解释，以及双语表达均属编辑工作，不构成新的 Solve、独立 Verify、形式化证明或证明修补。原候选与审查保持不变。原生证明与保存答复为中文；本报告的英文论述属于编辑翻译，不宣称存在历史英文求解／审查检查点。展示版证明将原来的代码附录移至独立检查器文件，并加入相对链接；补充材料明确说明数学正文和邻接表未改。翻译不等于再次审稿。[M1](materials/reviewed-source/dossier.json)；[展示版证明，S4](materials/showcase/proof.md)；[展示版审查摘要，S6](materials/showcase/review.md)。

下文关于历史下载、计算和文献检索的陈述均归属于冻结记录。本次 Organize 没有新做文献检索、执行 Lean/Lake、运行有限证书检查器或进行数学实验。文件身份与双语一致性的编辑检查不会提高证据等级。文献截止日为 **2026-10-21**，不能延伸到较晚的编辑快照日期。

## 2. 原猜想、记号与全部参数域

原始来源为 Somnath Bera、Prithwineel Paul、K. G. Subramanian 的 *Some properties of stepwise irregular graphs*，第 4 节猜想 1，印刷页第 223 页，即 PDF 第 9 页。定义和通常采用简单连通图的约定见第 216 页。冻结记录给出卷期 14(1)、页码 215–230、DOI 10.5614/ejgta.2026.14.1.14，以及发布日期 2026-04-22。期刊元数据日期优先于机构发表清单中的笼统一月日期。以下是依据保存的陈述与原文核对记录作出的数学转述，并非本次重新检视出版者 PDF。[原论文，B1](https://www.ejgta.org/index.php/ejgta/article/download/1077/pdf_357)；[期刊元数据，B7](https://www.ejgta.org/index.php/ejgta/article/view/1077)；[M1](materials/reviewed-source/dossier.json)。

这里的图是有限无向简单图，即无环且无重边。对图 \(G=(V,E)\)，\(\deg_G(v)\) 表示顶点 \(v\) 的邻点数。SI 图要求

\[
|\deg_G(u)-\deg_G(v)|=1\qquad\text{对每条 }uv\in E.
\]

论文通常还要求图连通。设整数 \(m,M\) 分别为最小、最大度数条目，且 \(m<M\)。周围的非平凡连通图语境使用 \(1\le m<M\)。冻结陈述提示可能的零度解释歧义，但不利用它；本反例取 \(m=1\)。对每个整数 \(m\le i\le M\)，取 \(n_i\in\mathbb Z_{>0}\)，因此两个端点之间的每个度数类均出现。\(i^{n_i}\) 表示度数 \(i\) 重复 \(n_i\) 次，不是数值乘方。记

\[
d=(M^{n_M},(M-1)^{n_{M-1}},\ldots,m^{n_m}),
\qquad N=\sum_{i=m}^{M}n_i.
\]

**猜想 1（冻结记录所保存的陈述）。** 如果

\[
n_{M-1}\ge\max\{M,n_M\},
\qquad
\sum_{\substack{m\le i\le M\\i\equiv M\pmod 2}}i n_i
=
\sum_{\substack{m\le i\le M\\i\not\equiv M\pmod 2}}i n_i,
\tag{1}
\]

那么 \(d\) 是某个 SI 图的度数序列；依据论文的一般约定，该实现还须连通。通常意义的可图性与 \(n_1\le n_2\) 都不是这条猜想的显式前提，本报告没有暗中加入它们。

为明确两种端点情形，式 (1) 的奇偶平衡可展开为下式。这只是同一个条件的编辑性展开：

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

每条 SI 边均连接偶度顶点与奇度顶点。在两侧分别计数，每条边各贡献一次，从而解释了两个度数和为何必须相等。但全局平衡不能保证相邻度数层之间处处具有足够容量；反例正利用了这一区别。

对于一个假设的实现，定义 \(V_i=\{v\in V:\deg_G(v)=i\}\)，于是 \(|V_i|=n_i\)。涉及相邻层的公式中，规定区间以外令 \(n_i=0\)。这表示空层，并非额外加入孤立顶点。对互不相交的顶点集 \(A,B\)，以 \(e(A,B)\) 表示一端在 \(A\)、另一端在 \(B\) 的边数。

## 3. 定理与证明策略

**定理 1——提交稿的反例。** 对于

\[
m=1,\quad M=6,\quad(n_1,n_2,n_3,n_4,n_5,n_6)=(1,3,1,1,6,4),
\tag{3}
\]

序列 \(d\) 满足式 (1)，有简单连通二部图实现，但没有 SI 实现，无论是否要求连通。因此它否定印刷版的全称充分条件猜想。普通图实现满足 \(N=16\)、\(|E|=34\)。

证明包含三个彼此不同的义务：引理 1 核对前提；引理 2–3 给出普遍不可实现性；引理 4 构造普通连通图，排除输入不可图的异议。引理 5 展开历史审查者已经记录的另一种表述，它是辅助说明，不是主证明的必需环节。依赖关系为

\[
\text{引理 2}\Longrightarrow\text{引理 3},\qquad
\text{引理 1、3、4}\Longrightarrow\text{定理 1}.
\]

引理 1–4 的来源是 [M1](materials/reviewed-source/dossier.json) 内嵌的候选证明，也见 [S4](materials/showcase/proof.md)。引理 5 及度 5 层的附加矛盾见 [M1](materials/reviewed-source/dossier.json) 的结构化历史审查。本证明不调用原论文前面的构造定理。

## 4. 逐步完整证明

### 引理 1——序列满足猜想的全部前提

度数数据及保存稿中的附加邻点数检查如下：

| \(i\) | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---:|---:|---:|---:|---:|---:|
| \(n_i\) | 1 | 3 | 1 | 1 | 6 | 4 |
| \(i n_i\) | 1 | 6 | 3 | 4 | 30 | 24 |
| \(n_{i-1}+n_{i+1}\)，其中 \(n_0=n_7=0\) | 3 | 2 | 4 | 7 | 5 | 6 |

**证明。** 六个重数都是正整数。最高两层的条件成立，并且恰好取到原条件允许的等号：

\[
n_{M-1}=n_5=6=\max\{6,4\}=\max\{M,n_M\}.
\tag{4}
\]

这里 \(M-m=5\) 为奇数。两个度数和为

\[
6n_6+4n_4+2n_2=24+4+6=34,
\qquad
5n_5+3n_3+n_1=30+3+1=34.
\tag{5}
\]

所以式 (1) 成立。另外，\(N=4+6+1+1+3+1=16\)，总度数为 \(68\)。

原证明还核对了三个更强的条件，但它们不是原猜想额外的前提：

\[
n_1=1\le3=n_2,\qquad
6n_6=24<30=5n_5,\qquad
i\le n_{i-1}+n_{i+1}\quad(1\le i\le6).
\tag{6}
\]

最后一组不等式可逐项比较表格的首行与末行。在简单 SI 图中，一个度为 \(i\) 的顶点只能选取相邻度数类中的不同顶点作为邻点。本例通过这一逐顶点检查，但该检查没有判断同一度数类的所有顶点能否同时占用邻层有限的关联端点容量。后者正是引理 2 的约束。\(\square\)

### 引理 2——局部关联容量的必要条件

对每个有限简单 SI 图和每个正度数下标 \(i\)，将不存在的度数层重数置零后，必有

\[
i n_i\le(i-1)n_{i-1}+(i+1)n_{i+1}.
\tag{7}
\]

**证明。** \(V_i\) 中两个顶点的度数差为零，所以它们不能相邻。SI 边两端度数差恰好为一，因此 \(V_i\) 的每个邻点均位于 \(V_{i-1}\cup V_{i+1}\)。于是 \(V_i\) 的度数和恰好将每条与该层关联的边计数一次，故

\[
e(V_i,V_{i-1}\cup V_{i+1})
=\sum_{v\in V_i}\deg_G(v)=i n_i.
\]

每条这样的边都占用 \(V_{i-1}\cup V_{i+1}\) 中一个顶点的一次关联。不同边使用不同的关联端点，即使它们可能共享同一个顶点。这两层能够提供的关联端点总数为

\[
\sum_{v\in V_{i-1}\cup V_{i+1}}\deg_G(v)
=(i-1)n_{i-1}+(i+1)n_{i+1}.
\]

其中一部分关联端点可能被通往其他度数层的边占用，所以上式只能作为容量上界，不能直接断言与需求相等。合并两次计数即得式 (7)。证明没有使用连通性。\(\square\)

这里完整给出这一初等论证，便于人工审查。历史审查已在 Adiyanyam–Azjargal–Buyantogtokh（2022）印刷页第 8687 页式 (2.4) 找到相同必要不等式，因此不宣称方法原创。[B2](https://www.aimspress.com/aimspress-data/math/2022/5/PDF/math-07-05-485.pdf)；[M1](materials/reviewed-source/dossier.json)。

### 引理 3——任何 SI 图都不能实现该序列

**证明。** 假设式 (3) 有一个 SI 实现。三个度为 2 的顶点总度数为

\[
2n_2=2\cdot3=6.
\]

它们的邻点只能具有度数 1 或 3，而这两个度数类的总度数为

\[
n_1+3n_3=1+3\cdot1=4.
\]

引理 2 因此要求 \(6\le4\)，矛盾。这排除了该序列的每一个 SI 实现，而不只是说下文展示的普通图不是 SI 图；它也不依赖对可能图的搜索。证明从未使用连通性。\(\square\)

历史审查还记录了式 (7) 在度 5 层的另一处违反：

\[
5n_5=30>4n_4+6n_6=4+24=28.
\tag{8}
\]

这是已保存障碍的另一种表现，不是本次编辑新增的搜索结果。任一违反均足够；主证明采用度 2 层的论证。

### 引理 4——普通简单连通二部图实现

取互不相交的顶点集

\[
L=\{a_1,a_2,a_3,a_4,b,c_1,c_2,c_3\},\qquad
R=\{u_1,u_2,u_3,u_4,u_5,u_6,v,w\}.
\]

只加入下表列出的跨部边，每条恰加入一次，不加入其他边：

| 左侧顶点 | 它在 \(R\) 中的全部邻点 |
|---|---|
| \(a_1,a_2,a_3\) 中的每一个 | \(u_1,u_2,u_3,u_4,u_5,u_6\) |
| \(a_4\) | \(u_1,u_2,u_3,u_4,u_5,v\) |
| \(b\) | \(u_1,u_2,u_6,v\) |
| \(c_1\) | \(u_3,u_4\) |
| \(c_2\) | \(u_5,u_6\) |
| \(c_3\) | \(v,w\) |

**证明。** 两部不相交，每一行的邻点没有重复，因此不存在环或重边，且每条边均跨越两部。逐行计数得到左部度数

\[
(6,6,6,6,4,2,2,2).
\]

右部度数也可直接人工核对，无须信任程序：

| 右侧顶点 | 它在 \(L\) 中的全部邻点 | 度数 |
|---|---|---:|
| \(u_1,u_2\) 中的每一个 | \(a_1,a_2,a_3,a_4,b\) | 5 |
| \(u_3,u_4\) 中的每一个 | \(a_1,a_2,a_3,a_4,c_1\) | 5 |
| \(u_5\) | \(a_1,a_2,a_3,a_4,c_2\) | 5 |
| \(u_6\) | \(a_1,a_2,a_3,b,c_2\) | 5 |
| \(v\) | \(a_4,b,c_3\) | 3 |
| \(w\) | \(c_3\) | 1 |

所以右部度数为 \((5,5,5,5,5,5,3,1)\)，两部度数合在一起恰好得到 \(d\)。顶点数为 \(8+8=16\)，边数为

\[
|E|=3\cdot6+6+4+2+2+2=34=68/2
\tag{9}
\]

条。

顶点 \(a_1,a_2,a_3,u_1,\ldots,u_6\) 诱导一个连通的 \(K_{3,6}\)。\(a_4,b,c_1,c_2\) 各自在这个子图中有邻点。顶点 \(v\) 经 \(a_4\) 接入，\(c_3\) 经 \(v\) 接入，\(w\) 再经 \(c_3\) 接入。因此所有顶点都处于同一个连通分量，所声称的普通图实现成立。这里不宣称该实现是 SI 图；引理 3 已排除了所有 SI 实现。\(\square\)

### 引理 5——历史审查的层间边数递推

以下展开的是结构化审查中已经保存的论证，不是本次重新执行的独立检查。对一个假设的 SI 实现，令 \(e_i\) 为 \(V_i\) 与 \(V_{i+1}\) 之间的边数，其中 \(1\le i\le5\)，并置 \(e_0=e_6=0\)。每个 \(e_i\) 都必须是非负整数。只有相邻度数层之间可能连边，因此

\[
e_{i-1}+e_i=i n_i\qquad(1\le i\le6).
\tag{10}
\]

从最低层的边界出发，依次强制得到

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

仅 \(e_3=-2\) 就不可能是边数。后续各项只是强制代数递推的继续，不代表存在某个图具有这些边数。完整向量为 \((0,1,5,-2,6,24,0)\)，与历史记录一致。两个外边界均为零，与全局奇偶平衡相容，但这无法消除内部负数项。这就是审查所给的等价矛盾。\(\square\)

**定理 1 的证明。** 引理 1 核对了原猜想的全部前提。引理 3 否定其 SI 实现结论，而且即使不要求连通也成立。一个满足前提而违反结论的实例足以否定全称猜想。引理 4 另外给出普通简单连通二部图实现，因此本例没有利用输入不可图或只能有非连通实现的情况。引理 5 是障碍的可选第二种表达。\(\square\)

## 5. 边界、等号与原题覆盖

| 需要区分的问题 | 保存论证的准确范围 |
|---|---|
| 度数端点 | 本例满足 \(1=m<M=6\)，不使用零度解释、孤立顶点或正则情形 \(m=M\)。六个度数类的重数均为正。 |
| 最高层条件的等号 | 达到原条件允许的边界 \(n_5=\max\{6,4\}=6\)。本报告不声称反驳另一个要求最高层严格不等式的猜想。 |
| 两种奇偶情形 | 本例属于奇数间隔 \(M-m=5\)。一个这样的实例已经否定全称陈述；无须反驳每个参数子类，也没有给出偶数间隔情形的分类。 |
| 区间外的空层 | 此处 \(n_0=n_7=0\) 表示空类；递推满足 \(e_0=e_6=0\)，不存在通向度数范围以外的边。 |
| 附加不等式 | 叶子数界、最高层严格关联容量和逐顶点邻点数界全部成立，却无法阻止整层容量亏缺 \(6>4\)。 |
| 容量不等式中的等号 | 等号只会消除该处的严格亏缺障碍。原证明和本报告都不声称所有此类不等式足以保证 SI 可实现性。 |
| 连通性 | 普通图见证连通；不可实现性同时排除连通与非连通 SI 图。 |
| 最小性与其他模型 | 没有建立最小阶反例、全部反例枚举、SI 序列刻画，或其他图模型下的结论。 |

保存的普通稿明确声称完整否定印刷版全称猜想，历史审查也赞同这一数学范围解释。但旧版结构化字段仍为 `scope=UNKNOWN` 和 `original_problem_coverage=UNKNOWN`，`coverage_explanation` 为空，不能改写成 `FULL`。不存在外部认证来保证形式化或自然语言陈述与原题精确等价。[M1](materials/reviewed-source/dossier.json)。

## 6. 已记录结果与证据等级

| 记录或问题 | 保留的结果 | 能够说明与不能说明的内容 |
|---|---|---|
| 候选 | `SELF_CHECKED` | 提交的普通证明与有限见证；Organize 不提高该等级。 |
| 历史独立 AI 审查 | `NO_ISSUES_FOUND`；`issues=[]` | 审查者报告未见证明缺口或循环，认可完整反例主张；这是 LLM 审查，不是外部专家或形式化认证。 |
| 旧版覆盖字段 | 候选 `scope=UNKNOWN`；审查 `original_problem_coverage=UNKNOWN` | 旧记录缺乏显式覆盖评估；解释普通稿的范围不等于替换这些字段。 |
| 记录的数学义务 | 候选与审查的 `remaining_obligations=[]` | 未列出剩余数学义务；旧版空数组不能补足缺失的外部证据。 |
| 新颖性 | `UNKNOWN` | 不能认证该特定反驳的优先权；局部计数方法本身已有先例。 |
| 发现阶段的问题状态 | `UNKNOWN`，检查日期 2026-10-21 | 找到公开提出的猜想，但未认证其当时仍开放；也没有声称今天仍然开放。 |
| 结构化证据字段 | `checks=[]`、`citations=[]`、结构化文献检索数组为空；`evidence_assessment.supported=false` | 叙述性审查证据存在，但旧字段没有填入结构化验证或受支持评估；保留其空缺。 |
| 形式化证据 | `formal_target=null`、`formal_check=null`、`formal_receipt=null`；补充记为 `NOT_FORMALIZED` | 没有 Lean 源文件、成功 Lean 运行、内核回执或完整形式化定理验证。 |
| 外部审稿与对齐 | 展示摘要中两者均不存在 | 未取得外部专家审稿或外部原题陈述等价性认证。 |

原候选假设中“尚未进行独立 Verify”的表述描述的是提交时点。后来的保存审查属于另一个历史事件，不能暗中修改先前文字。同样，Verify 工作流完成不等于形式化验证完成。[M1](materials/reviewed-source/dossier.json)；[S7](materials/showcase/verification.json)。

## 7. 有限证书、计算与形式化文件的实际范围

原证明附录包含求解者的 Python 标准库检查器。公开 [checker，S8](materials/showcase/verify_certificate.py) 属于这一求解材料，并按原样保存；[证书，S3](materials/showcase/certificate.json) 描述同一个有限图。检查器核对重数为正且度数连续、猜想中的整数关系、附加强健性条件、互不相交的顶点标号、不重复的跨部边、度数多重集、边数、通过图遍历检验连通性，以及两部顶点度数的奇偶性，最后计算指定度数类的数值亏缺。

这些计算支撑引理 1、4 的有限数据以及引理 3 使用的数值。程序不对所有图作量化，也不证明引理 2。普遍不可实现性来自正文的计数证明。检查器自身的输出明确说明它没有进行独立审查，也不会设置 MathLottery 审查状态。

历史独立审查者报告另写了检查器，独立转录 8×8 邻接矩阵，得到 34 个值为 1 的元素、引理 4 中的两部度数列表，以及全部 16 个顶点的可达性。审查者明确表示**没有执行候选提供的程序**。保存的最终答复还报告独立检查器的 pytest 与 ruff 检查通过。这些是历史记录中的报告结果；该检查器、测试输出、算术输出文件与完整审计日志均不在原生清单收集的两个文件之内。因此，不能只靠当前包重放那次独立检查，也不能将公开求解者 checker 改称为独立审查者的检查器。[M1](materials/reviewed-source/dossier.json)；[M2](materials/reviewed-source/tasks/task-record-003/attempt-record-004/answer.md)；[S6](materials/showcase/review.md)。

不可实现性证明不需要、也没有把 SAT 或穷举搜索结果作为证明提交。冻结记录不能确定求解者如何发现这个例子。本例没有 Lean 开发，展示摘要还明确说明导出时没有执行新的 Lean 构建。本报告不把任何后来的形式化工作归到较早的普通证明审查。

## 8. 文献、已知方法与新颖性不确定性

原猜想是作者在 2026 年论文中公开提出的主张，不是本次编辑重新寻找或确认仍开放的结果。保存的原题记录将其列为低成本初筛的 Rank 1，但解决难度与 Lean 可行性仍未知。这是可行性估计，不是成功概率或已确定的难度分类。它提到原论文定理 4.1–4.2 的必要条件与引理 4.1–4.2 的特殊充分情形；发现阶段没有独立审查这些构造，它们也不是本反例证明的依赖。[M1](materials/reviewed-source/dossier.json)；[B1](https://www.ejgta.org/index.php/ejgta/article/download/1077/pdf_357)。

历史审查在 2022 年论文 *Bond incident degree indices of stepwise irregular graphs* 第 8687 页式 (2.4) 找到局部不等式 (7)，因此存在有记录支持的方法先例。这本身不等于已经发现对 2026 年印刷版特定猜想的既有反驳。具体重数向量及其优先权仍为 `UNKNOWN`。[B2](https://www.aimspress.com/aimspress-data/math/2022/5/PDF/math-07-05-485.pdf)；[S6](materials/showcase/review.md)。

叙述性记录说明检索涉及题名、DOI、作者、猜想编号、反例／更正词、具体重数、arXiv、GitHub 和数学论坛。截至 2026-10-21，在检查过的材料中没有找到直接的既有解决声明。2018 年前身论文的作者名单不同，其第 4 节讨论图运算，检查文本中未见目标度数序列猜想。已读的后续极值稿讨论度数、边数、直径或度数相关指标，而非明确解决这一准则。这些是有边界的历史检索结果，不是对整个文献的穷尽排除。[M1](materials/reviewed-source/dossier.json)；[B3](https://arxiv.org/pdf/1809.03297)；[B4](https://arxiv.org/pdf/2411.15765v1)；[B5](https://users.fmf.uni-lj.si/klavzar/preprints/k-si%20final%20version.pdf)。

特别是，2026 年的 *On k-stepwise irregular graphs*，DOI 10.1016/j.dam.2026.06.027，只有元数据、公开摘要及片段可用。记录显示直接全文访问因 HTTP 403 失败；候选还记录了出版者／SSRN 全文不可访问。元数据记录建立于 2026-07-07，印刷卷期标为 2026 年 11 月。没有排除该全文可能含有相关结果，也没有作者确认、穷尽引文审计或外部优先权评估。因此新颖性保持 `UNKNOWN`；历史审查没有把这一限制报告为计数证明的数学缺陷。[B6](https://doi.org/10.1016/j.dam.2026.06.027)；[记录的元数据来源](https://api.crossref.org/works/10.1016/j.dam.2026.06.027)；[M1](materials/reviewed-source/dossier.json)。

## 9. 未解决缺口与重构边界

历史审查报告提交的反例证明没有数学缺口，本报告也不提出修补。尚未解决的限制集中在证据、溯源和优先权：

- 原 Solve 关联、求解时间线、中间尝试和命名研究笔记缺失。可见一个导入候选和一个审查任务；未保存失败尝试不意味着不存在失败尝试。
- 审查提到独立检查器、完整审计报告、来源记录、算术输出与检索日志，但这些文件不是原生收集材料。保存答复和结构化审查中的描述不能代替缺失文件。
- 原论文和相关论文的二进制文件作为历史参考工件出现，部分附有哈希，但未收集入本包。来源 URL 与历史核对说明不构成本次对 PDF 的重新检视。
- 部分近期全文不可访问，特定优先权与当前文献状态仍不确定；没有外部专家评估或原题陈述等价性证书。
- 没有形式化源文件或回执。普遍不可实现性是普通数学证明，有限算术与图检查各自只承担较窄的职责。

清单的 `omitted=[]` 仅表示其收集流程没有列出遗漏条目，不表示所有历史文件均已收集。清单限制明确排除了任意工作区文件、二进制、缓存与隐藏推理。Showcase 补充也说明不打包原始日志。补充摘要中 Find、Solve、Verify 均已完成的概述，不能补上缺失的原生 solver linkage。本报告不声称任何替代猜想或数学修补成立；评估这类提案须另开 Solve/Verify。

## 10. 可复现命令与预期范围

待显式提供的 showcase 文件附入约定的相对位置后，读者可使用 Python 3.11 或更高版本，从报告所在目录运行：

```sh
cd materials/showcase
python verify_certificate.py certificate.json
```

保存来源说明的预期输出包括：16 个顶点、34 条边、偶度和与奇度和各为 34、重数 \((1,3,1,1,6,4)\)、普通简单连通二部图标志，以及 SI 关联需求 6 和可用邻层总度数 4。独立审查字段会说明该检查器未进行独立审查。这些预期来自保存源文件，本报告不宣称重新执行过程序。

读者也可以核对文件字节身份：

```sh
sha256sum certificate.json verify_certificate.py proof.md verification.json
```

将输出与附录 B 比较。哈希相同只识别字节，不能认证数学正确性、独立审查或陈述等价性。[M1](materials/reviewed-source/dossier.json) 的候选 `proof` 字段还保留完整标准库检查器，因此即使没有单独的补充文件，也能阅读有限算法。这里没有提供能够复现缺失独立审查日志或不存在的 Lean 证明的命令。本次 Organize 仅进行了源材料阅读、编辑性字节核对与报告一致性检查。

## 11. 参考文献及历史来源状态

以下访问与范围说明全部继承自冻结证据，截止日为 2026-10-21；链接用于引用，不表示本次重新取得材料。

1. **B1.** Somnath Bera, Prithwineel Paul, K. G. Subramanian. *Some properties of stepwise irregular graphs*. EJGTA 14(1) (2026), 215–230. DOI 10.5614/ejgta.2026.14.1.14。定义与约定见第 216 页；猜想 1 见第 223 页，即 PDF 第 9 页。记录的发布日期为 2026-04-22。[出版者 PDF](https://www.ejgta.org/index.php/ejgta/article/download/1077/pdf_357)。
2. **B2.** Damchaa Adiyanyam, Enkhbayar Azjargal, Lkhagva Buyantogtokh. *Bond incident degree indices of stepwise irregular graphs*. AIMS Mathematics 7(5) (2022)；记录的发布日期为 2022-03-02。局部容量不等式见第 8687 页式 (2.4)。[出版者 PDF](https://www.aimspress.com/aimspress-data/math/2022/5/PDF/math-07-05-485.pdf)。保存审查将它作为已知方法来源，而非 B1 猜想已被解决的证据。
3. **B3.** Somnath Bera, Prithwineel Paul. *Properties of stepwise irregular graphs*. arXiv:1809.03297v1，2018-09-10。相关前身；检查文本中未见目标度数序列猜想。[预印本](https://arxiv.org/pdf/1809.03297)。
4. **B4.** Yaser Alizadeh, Sandi Klavžar, Javaher Langari. *Extremal results on k-stepwise irregular graphs*. arXiv:2411.15765v1，2024-11-24；记录的期刊引用为 Applied Mathematics and Computation 514 (2026), 129818。[预印本](https://arxiv.org/pdf/2411.15765v1)。历史检查未见目标准则的明确解决声明。
5. **B5.** Yaser Alizadeh, Sandi Klavžar, Javaher Langari. *On size of k-stepwise irregular graphs and their degree based indices*。[作者托管稿](https://users.fmf.uni-lj.si/klavzar/preprints/k-si%20final%20version.pdf)。准确发表日期未确定；检查稿讨论边数与指标。
6. **B6.** Damchaa Adiyanyam, Enkhbayar Azjargal, Lkhagva Buyantogtokh, Shiikhar Dorjsembe, Batmend Horoldagva. *On k-stepwise irregular graphs*. DOI [10.1016/j.dam.2026.06.027](https://doi.org/10.1016/j.dam.2026.06.027)。[Crossref 记录](https://api.crossref.org/works/10.1016/j.dam.2026.06.027)。只有元数据与公开片段可用，全文访问受阻。2026 年 11 月的卷期日期属于记录元数据，不能证明已穷尽审查。
7. **B7.** [B1 的出版者文章元数据](https://www.ejgta.org/index.php/ejgta/article/view/1077)。保存的发现记录优先采用期刊的 2026-04-22 日期，而非机构清单的笼统日期。
8. **B8.** [机构 2026 年发表清单](https://iem.edu.in/publications-2026/)。出现在保存的发现阶段状态证据中，不是开放状态的权威证明，也不是新颖性证书。

## 附录 A. 保存工作的简明时间线

有时间的条目均采用 UTC。这些时间定位证据事件，不重构隐藏推理。

| 日期或记录区间 | 可见事件 | 限定说明 |
|---|---|---|
| 2026-10-21 04:01:26 | 保存的问题状态核对为 `UNKNOWN`，附初筛与来源选择理由 | 未认证开放状态；该发现阶段尚未声称已有见证。 |
| 2026-10-21，候选参考文献约在 04:05:09 取得 | 导入求解稿包含重数向量、容量证明、普通图邻接构造与求解者 checker | 参考文献取得时间不是 Solve 起止时间；原 Solve 关联与尝试时间线缺失。 |
| 2026-10-21 04:10:34–04:17:16 | 历史独立 Verify 工作流，记录为 `COMPLETED` | 可见一个完成的审查任务；任务自己的来源观察时间戳缺失。 |
| 审查期间：04:11:47 与 04:12:37 | 目标／相关来源以及 2022 年方法来源具有记录的取得时间 | 审查者报告独立核对来源、转录矩阵、有限检查与递推矛盾；原文件和命令日志未收集。 |
| 保存的审查结论时点 | `NO_ISSUES_FOUND`、新颖性 `UNKNOWN`；报告独立检查器 pytest 与 ruff 通过 | 普通 AI 审查；原覆盖字段仍为 `UNKNOWN`；没有 Lean 结果。 |
| Showcase 补充：证据日期 2026-10-21，导出时间未提供 | 证明代码附录移出，补充相对链接与双语展示文档 | 整理既有证据；数学证明与邻接表不变；没有新 Lean 构建或新审查。 |
| 2026-10-24 04:21:35 | 采集原生 Organize 快照 | 编辑资料边界，不是新的文献截止日。 |
| 本次 Organize | 依据同一冻结证据形成完整中英文报告 | 不修改候选、审查、原题或选择；没有新 Solve/Verify。 |

从可见时间线无法恢复其他失败或成功的求解尝试。这是在说明记录缺失，不是证明研究过程没有失败的中间工作。

## 附录 B. 材料索引与哈希域

### B.1 原生清单材料

只有下列两个文件属于原生收集条目。正文使用角色称呼；相对链接保留清单定位。

| 编号 | 相对材料链接 | 内容与限制 | 字节数 |
|---|---|---|---:|
| M1 | [冻结 Verify dossier](materials/reviewed-source/dossier.json) | 完整保存原题；原候选主张、假设、证明及 checker 附录；一条结构化审查及其参考文献；稀疏时间线。不含独立 checker 文件或原始审计日志。 | 33506 |
| M2 | [历史审查保存答复](materials/reviewed-source/tasks/task-record-003/attempt-record-004/answer.md) | 审查结论与报告的检查结果。它提到一份未收集的完整审计；这份简短答复不等于那份完整报告。 | 2171 |

原生文件的 SHA-256：

```text
M1  ba5203cf7d005c261fc9a12acf7c16293050b135c61019db05769c0e25a814e8
M2  4e2a22ed40f03bd535fff91ae2e025ddce09209b3424813a053d5e43471a9376
```

历史答复含有原始本地定位，本报告不复制这些定位；它们不能让所指文件自动成为冻结材料。

### B.2 显式提供的 showcase 补充

以下均为**显式 showcase 补充**，不是 Organize 清单 `files` 数组的原生条目。提供的导出说明给出了未来的 `materials/showcase/` 位置和完整文件哈希。S2、S4、S6 的全文内联提供；S7 的内联版本省略了冗余哈希索引。S1、S5 只有元数据／哈希条目，没有内联全文。S3 的图数据和 S8 的算法可在原证明与提供的附录差异中看到，但它们的独立文件字节不是原生收集文件。发布步骤负责附入精确冻结的补充文件；本次编辑没有根据节略文本重建缺失文件。

| 编号 | 链接 | 角色 | 字节数 |
|---|---|---|---:|
| S1 | [中文展示概览](materials/showcase/README.cn.md) | 展示文档 | 1775 |
| S2 | [英文展示概览](materials/showcase/README.md) | 展示文档 | 2221 |
| S3 | [有限证书](materials/showcase/certificate.json) | 求解者的显式图数据 | 892 |
| S4 | [展示版证明](materials/showcase/proof.md) | 移出代码附录后的原中文数学论证 | 5624 |
| S5 | [中文审查摘要](materials/showcase/review.cn.md) | 历史审查的展示文档 | 1659 |
| S6 | [英文审查摘要](materials/showcase/review.md) | 历史审查的展示文档 | 2038 |
| S7 | [验证摘要](materials/showcase/verification.json) | 整理的历史结果与身份信息，不是新验证运行 | 3666 |
| S8 | [有限证书检查器](materials/showcase/verify_certificate.py) | 求解者代码，不是独立审查者的 checker | 4538 |

提供的完整文件 SHA-256：

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

特别是，节略的 S7 内联文本不等于 3666 字节的完整文件，不能期待二者哈希相同。S4 所列是展示文件哈希，它与下表原证明文本哈希不同，原因是移出了代码附录并加入链接，而非提供了数学修补。

### B.3 历史证据身份：各自在本身的哈希域内比较

| 编号与对象／哈希域 | 限定说明 |
|---|---|
| H1——候选内容身份 | 清单与补充记录的候选身份，不是展示版证明文件的哈希。 |
| H2——原证明文本 | 候选 `proof` 字段的 UTF-8 文本，包含原来的内联 checker。 |
| H3——历史完整审查报告 | 只提供历史身份信息；完整文件未收集，也不是 M2。 |
| H4——原论文 PDF | 候选与审查者报告相同下载身份；本包未收集 PDF 字节。 |
| H5——2022 年已知方法 PDF | 历史审查参考记录；本包未收集 PDF 字节。 |
| H6——冻结 Problem.statement 文本 | UTF-8 陈述文本的 SHA-256，不表示存在形式化回执。 |
| H7——冻结完整 Problem 记录指纹 | 清单对完整规范化 Problem 记录的身份标记，含元数据和旧字段归一化。 |

记录的 SHA-256：

```text
H1  877630f102a9d01b633af85df6a45d1fea337d0c47477e89d8f331a6c574075e
H2  0010699c220ed13c8301bd0fa2f8656493b214abbad599e0a73254bd7f8c3536
H3  95419e9f737c7e45d6c4b3b0752ce2fe71fd6b9a271eff226161dd0ee68be6d2
H4  2a2475b57fd15d103e558a3ef88854a3b646987ee7007ecafb46b2ef9f1ecfbd
H5  65535b948ca828835fbd22bba82b5c6707f8688e358ef6dae07180c0905eabd2
H6  a243d69e034967dbd2fd848d6c6d87a705a90c3f1c2faf5eaf5c6ff0deb75103
H7  21c10fc11e5d48c5f529a426227577834477047a906e3d563346d521c198775e
```

最后两个哈希输入不同，不应期待相等；各自只能在相同的哈希域中比较。任何这些哈希都不能认证定理真假、新颖性，或自然语言与形式化陈述的等价性。

## 附录 C. 双语一致性记录

中英文报告使用相同的猜想 1、定理 1、引理 1–5、式 (1)–(11)、重数表、邻接表、端点约定、依赖结构、参考文献、相对材料链接与哈希身份。两版均保留完整普通图构造、普遍的 \(6>4\) 矛盾、记录的 \(30>28\) 检查与负层间边数，保留 `SELF_CHECKED`、`NO_ISSUES_FOUND`、所有 `UNKNOWN` 字段、形式化与外部证据缺失、Solve 关联缺失、不可访问文献，以及原生材料与 showcase 补充的区别。一致性检查属于编辑工作，不赋予新的数学或证据认证。
