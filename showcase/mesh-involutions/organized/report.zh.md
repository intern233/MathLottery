> 公开展示版本：仅进行私人运行信息脱敏和相对路径整理；原有结论及证据等级不变。正文、附录及历史材料中的哈希和字节数指向原始冻结输入；脱敏、链接整理及来源说明会改变公开副本的字节。核对本目录中的文件时，请使用[出版清单](manifest.json)中 `files[].sha256` 与 `files[].bytes`，不要用正文或附录的原始哈希判断公开副本是否损坏。清单分别保留原始与公开文件的哈希、字节数。

# MathLottery 专家阅读报告

> 本文是对已有研究材料的整理，未经新增独立验证。排版和说明不提升证明等级，也不认证问题的开放状态或新颖性。

来源任务：`reviewed-source`；冻结版本：9；冻结时间：2026-10-24T04:21:29.528744+00:00。

## 原始验证记录

- `candidate-record-005` · `SELF_CHECKED` · scope `UNKNOWN`; verdict `NO_ISSUES_FOUND`, coverage `UNKNOWN`, novelty `POTENTIALLY_NEW`

[Evidence manifest](manifest.json)

### 材料范围与限制

- This is an editorial reconstruction of visible saved evidence, not hidden reasoning, an independent mathematical verification, or a certification of novelty.
- reviewed-source: only saved answers, named notes, proof/formal files and source receipts are included; arbitrary workspace files, binaries and caches are excluded.
- This historical Verify has no saved solver linkage. The original Solve history is unavailable; matching titles or proofs were not used to guess it.

---

# 对合上四个二阶网格模式的等分布：保存候选证明及其证据的专家报告

## 1. 摘要与准确的证据结论

保存的普通证明声称解决 Fang–Fu–Kitaev–Li–Su–Sun 的修正版猜想 1：对每一对非负整数 \(n,k\)，大小为 \(n\)、恰有 \(k\) 次指定模式出现的对合数，对四个给定网格模式均相等。论证首先在排列及其**任意出现标记子集**上构造双射，证明星形与路径分量的同时旋转在对象和逐条边两个层面都与取逆相容，再给转置作用的单边轨道与双边轨道赋予两个独立权重，从而恢复每一个出现次数的计数。反向补给出其余模式对的等分布。下文完整展开这份普通论证，包括空情形及构造的两个方向。

保存的候选等级为 **`SELF_CHECKED`**。历史独立 AI 审查结论为 **`NO_ISSUES_FOUND`**，截至 **2026-10-21** 的新颖性评估为 **`POTENTIALLY_NEW`**。旧记录的候选 `scope` 与审查 `original_problem_coverage` 均为 **`UNKNOWN`**；旧版没有提供明确的覆盖评估。解释证明正文声称、审查正文认可的完整数学范围，**不等于**把这些字段改为 `FULL`。问题的保存状态也仍为 `UNKNOWN`。没有外部数学专家审稿，也没有自然语言陈述与形式陈述等价性的外部认证。[冻结 dossier](materials/reviewed-source/dossier.json)；[保存的审查答复](materials/reviewed-source/tasks/task-record-003/attempt-record-004/answer.md)。

单独提供的 showcase 摘要记录了后续 **107 条定理**的 Lean 编译、公理依赖检查及 fresh 内核重放。这些只是**部分**形式化结果：对每个 \(n\) 构造全局 \(\mathrm{MarkedTransport}\ n\) 的工作尚缺。普通稿的历史审查者没有审查这些后续形式化工作。原生 Solve 因 usage limit 停止，未提交最终候选；主控提交了普通稿快照，后来继续部分 Lean 工作。因此不能将其写成原生 Solve 端到端正常完成。[显式提供的验证摘要](materials/showcase/verification.json)；[形式化范围说明](materials/showcase/formal/README.md)。

本报告是对可见冻结证据的**编辑性重构**，不是新的 Solve 或 Verify。数学阐释忠实遵循 dossier 内嵌候选证明；编号、过渡说明及翻译属于编辑工作。报告不补入未记录的修复、隐藏推理、新的文献检索、有限实验或 Lean 执行。文献状态截至历史检索日，而非报告制作日。显式提供的 showcase 文档是另一类来源，不是原生 Verify 清单后来新增收集的文件；其局限与缺失材料均在下文标明。

## 2. 原题、记号与全部参数域

目标是 *On mesh patterns of short length: Equidistribution and enumeration* **2026-10-11 的 v2** 第 4 节、印刷页码第 17 页的 **corrected Conjecture 1（修正版猜想 1）**。原断言是所展示的四个模式在对合上等分布。Remark 4.1 讨论的较早错误版本不是本题；已经解决的全体排列版本也不是本题。保存的审查记录称，审查者独立取得了 v2 PDF、TeX 与版本元数据，并核对图形及坐标；本次编辑没有重新取得这些外部材料。[固定版本原文](https://arxiv.org/abs/2606.14367v2)；[PDF](https://arxiv.org/pdf/2606.14367v2)；[TeX 源码](https://arxiv.org/src/2606.14367v2)；[冻结审查记录](materials/reviewed-source/dossier.json)。

令 \([n]=\{1,\ldots,n\}\)，其中 \([0]=\varnothing\)。令 \(S_n\) 为 \([n]\) 上的排列集合，定义

\[
I_n=\{\pi\in S_n:\pi\circ\pi=\mathrm{id}_{[n]}\}.
\tag{1}
\]

\(S_0=I_0\) 含唯一的空排列。设

\[
R=\{(0,0),(1,1),(1,2),(2,1)\},\qquad
R'=\{(2,2),(1,1),(1,0),(0,1)\}.
\tag{2}
\]

按照原文图示顺序，四个模式为

\[
p_1=(12,R),\quad p_2=(12,R'),\quad
p_3=(21,R'),\quad p_4=(21,R).
\tag{3}
\]

这里 \(12\)、\(21\) 分别是 \(S_2\) 中的递增、递减排列。阴影格 \((a,b)\) 的左下角坐标是该点，其中 \(a,b\in\{0,1,2\}\)。给定 \(\pi\in S_n\) 和 \(1\le i<j\le n\)，置

\[
x=(0,i,j,n+1),\qquad
y=(0,\min(\pi(i),\pi(j)),\max(\pi(i),\pi(j)),n+1).
\tag{4}
\]

对于 \(\tau\in S_2\) 以及 \(S=R\) 或 \(R'\)，这对下标是模式 \((\tau,S)\) 的一次出现，当且仅当对应值的相对次序为 \(\tau\)，且

\[
\forall(a,b)\in S,\quad
\nexists\,t\in[n]\quad
x_a<t<x_{a+1}\ \text{ and }\ y_b<\pi(t)<y_{b+1}.
\tag{5}
\]

矩形中的不等号全部是**严格不等号**。以 \(\operatorname{Occ}_p(\pi)\) 表示这样的有序下标对集合，令 \(\operatorname{occ}_p(\pi)=|\operatorname{Occ}_p(\pi)|\)。

**定理 1（保存的普通候选稿所声称的完整结论）。** 对每个 \(n,k\in\mathbb Z_{\ge0}\) 及每个 \(s,t\in\{1,2,3,4\}\)，均有

\[
\#\{\pi\in I_n:\operatorname{occ}_{p_s}(\pi)=k\}
=\#\{\pi\in I_n:\operatorname{occ}_{p_t}(\pi)=k\}.
\tag{6}
\]

候选稿没有增加其他数学假设。这是四个**边缘分布**在所有出现次数上的相等，包括回避情形 \(k=0\)；不是联合分布恒等式，也不是说同一个对合上的四个统计量逐一相等。下文的有限图术语用于排列的出现标记图，并非另一个图论猜想。

## 3. 证明策略与引理依赖

设 \(A=p_1\)、\(B=p_4\)。标记对象是 \((\pi,M)\)，其中 \(\pi\in S_n\)，而 \(M\subseteq\operatorname{Occ}_A(\pi)\) 或 \(M\subseteq\operatorname{Occ}_B(\pi)\)。**允许所有子集**，不要求极大性或饱和性。

保存证明的逻辑依赖如下：

| 步骤 | 数学任务 | 后续用途 |
|---|---|---|
| 引理 1 | 将阴影矩形条件改写为三个不等式条件 | 引理 2–4 |
| 引理 2–3 | 确定星形、路径结构并证明单间隙嵌套 | 引理 5 |
| 引理 4 | 给出适用于两种结构的共同外部充要条件 | 引理 5 |
| 引理 5 | 同时旋转所有分量，检查嵌套的两个方向并构造逆映射 | 引理 6 |
| 引理 6 | 证明对象及逐条边的取逆等变性 | 引理 7 |
| 引理 7 | 使用两种轨道权重，再以代换恢复所有系数 | 定理 1 的 \(A,B\) 情形 |
| 引理 8 | 应用反向补并处理边界情形 | 定理 1 的四模式情形 |

一个看似自然的捷径是错误的。历史审查者记录了对合 \(\pi=213\)，取唯一的 \(A\)-标记 \(M=\{(1,3)\}\)，旋转这颗星会得到不是对合的 \(312\)。实际上转置把 \((1,3)\) 送到 \((2,3)\)，后者没有被选入 \(M\)。因此，不能把全体排列上的标记双射直接限制到“对合的任意标记”。证明改为限制到**转置不动的标记对象**，然后用轨道权重恢复未标记的出现次数分布。这是保存记录中对错误捷径的反例，不是定理 1 的反例。[审查证据](materials/reviewed-source/dossier.json)。

以下引理 1–8 忠实展开[历史内嵌证明](materials/reviewed-source/dossier.json)第 1–7 节的论证，其数学内容与[显式提供的 showcase 证明稿](materials/showcase/proof.md)相同。后者是展示版本，记录的修改包括一个区间排版修正、两处将括号中的 `1` 改为数学 \(1\)，以及引用和审查指向的更新。这些修改不构成新验证过的证明。

## 4. 完整普通证明

### 引理 1. 严格矩形条件的等价改写

对 \(i<j\)，设 \(l=\min(\pi(i),\pi(j))\)、\(h=\max(\pi(i),\pi(j))\)。\(R\) 对应的四个阴影矩形为空，当且仅当

\[
\begin{array}{ll}
\mathrm L:&t<i\ \Longrightarrow\ \pi(t)>l,\\
\mathrm M:&i<t<j\ \Longrightarrow\ \pi(t)<l,\\
\mathrm Q:&t>j\ \Longrightarrow\ \pi(t)\notin(l,h).
\end{array}
\tag{7}
\]

\(A\)-出现还要求 \(\pi(i)<\pi(j)\)，\(B\)-出现还要求 \(\pi(i)>\pi(j)\)。

**证明。** 阴影格 \((0,0)\) 排除了较早位置上小于 \(l\) 的值。由单射性，非端点处不可能等于 \(l\)，故恰为 L。阴影格 \((1,1)\) 与 \((1,2)\) 联合排除内部位置上大于 \(l\) 的值：两格并集遗漏的边界值 \(h\) 已出现在某个端点，不可能再出现在内部；值 \(l\) 同理也不可能出现。这给出 M。阴影格 \((2,1)\) 直接给出 Q。所有位置和值均在 \([n]\) 内，所以外边界 \(0,n+1\) 不产生例外。这些论证可以双向使用。∎

### 引理 2. 标记分量分别是星形或下降路径

每条标记边从较小下标指向较大下标，并去掉孤立顶点。\(A\) 一侧的每个非平凡连通分量都是星形；\(B\) 一侧的每个非平凡连通分量都是下降路径。

更准确地，对某个 \(m\ge1\)，可将该分量的位置和互异值记为

\[
x_0<x_1<\cdots<x_m,\qquad v_0>v_1>\cdots>v_m,
\tag{8}
\]

使两种排列方式分别为

\[
\begin{array}{lll}
A:&(\pi(x_0),\ldots,\pi(x_m))=(v_1,\ldots,v_m,v_0),
&M_C=\{(x_{h-1},x_m):1\le h\le m\},\\
B:&(\pi(x_0),\ldots,\pi(x_m))=(v_0,v_1,\ldots,v_m),
&M_C=\{(x_{h-1},x_h):1\le h\le m\}.
\end{array}
\tag{9}
\]

**证明。** 在 \(A\) 一侧，若存在两条出边 \((i,j),(i,k)\)，其中 \(j<k\)，则第二条边的 M 给出 \(\pi(j)<\pi(i)\)，与第一条边递增矛盾。由 L，每个起点都是从左到右的新最小值。递增边的终点已有一个较早且更小的值，所以不能再是某条边的起点。因此每个非根顶点只有一条出边；终点根之间也不能通过这些度为一的叶子连在一起。每个连通分量遂为只有一个终点根的星。相继叶子的 L 使叶值严格递减；各条递增边使根值大于所有叶值。这就是式 (9) 第一行。

在 \(B\) 一侧，若有 \((i,j),(k,j)\) 且 \(i<k<j\)，第一条边的 M 给出 \(\pi(k)<\pi(j)\)，与第二条边递减矛盾，故入度至多一。若有 \((i,j),(i,k)\) 且 \(j<k\)，由第二条边的 M 及递减性，有 \(\pi(j)<\pi(k)<\pi(i)\)；位于 \(k\) 的点于是违反第一条边的 Q，故出度也至多一。每条边沿下标递增方向前进，不可能形成有向圈。在有限分量中不断寻找前驱必到达初始顶点，从该点沿后继行走便覆盖整个分量，否则额外接入的边会违反入度或出度界。故分量为路径，且沿每条边值严格下降，得到式 (9) 第二行。整个论证均不需要标记的极大性。∎

### 引理 3. 不同分量不相交，或嵌套在单个间隙内

不同分量的边不能交叉。任意两个不同分量的闭位置区间要么不相交，要么其中一个分量的整个区间包含在另一个分量的相邻两个顶点之间的单个开间隙内。

**证明。** 假设两条边 \((i,j),(k,l)\) 满足 \(i<k<j<l\)。对于 \(A\)，第一条边的 M 及递增性给出 \(\pi(k)<\pi(i)<\pi(j)\)，而第二条边的 M 给出 \(\pi(j)<\pi(k)\)，矛盾。对于 \(B\)，第一条边的 M 给出 \(\pi(k)<\pi(j)\)，第二条边递减给出 \(\pi(l)<\pi(k)\)，而第二条边的 M 又给出 \(\pi(j)<\pi(l)\)，同样矛盾。交换两条边的名称即可处理另一种交叉顺序。

为证明更强的单间隙断言，设分量顶点依次为 \(c_0<\cdots<c_m\)、\(d_0<\cdots<d_r\)。不同分量不共用顶点。交换名称后，非不交情形只需考虑 \(c_0<d_0<c_m\)。对于星形，边 \((c_0,c_m),(d_0,d_r)\) 迫使 \(d_r<c_m\)，否则二者交叉。若某个 \(c_t\) 位于 \((d_0,d_r)\)，它必为叶子，其边 \((c_t,c_m)\) 将与 \((d_0,d_r)\) 交叉。因此 \([d_0,d_r]\) 不含任何 \(c\)-顶点，必处于单个开间隙内。

对于路径，取 \(t\) 使 \(c_t<d_0<c_{t+1}\)。若 \(d_r>c_{t+1}\)，则某两个相邻 \(d\)-顶点必跨过 \(c_{t+1}\)，即 \(d_a<c_{t+1}<d_{a+1}\)。于是 \(c_t<d_a<c_{t+1}<d_{a+1}\) 给出交叉路径边，矛盾。所以 \(d_r<c_{t+1}\)，路径情形的单间隙断言也成立。∎

### 引理 4. 两种结构共有的外部充要条件

固定式 (8) 的位置与值，并按式 (9) 任一行排列。所有指定边都是相应模式的出现，当且仅当位置不在 \(\{x_0,\ldots,x_m\}\) 中的每个点都满足

\[
\begin{array}{ll}
\mathrm O_0:&t<x_0\ \Longrightarrow\ \pi(t)>v_1,\\
\mathrm O_k:&x_{k-1}<t<x_k\ \Longrightarrow\ v_{k+1}<\pi(t)<v_k
\quad(1\le k<m),\\
\mathrm O_m:&x_{m-1}<t<x_m\ \Longrightarrow\ \pi(t)<v_m,\\
\mathrm O_{m+1}:&t>x_m\ \Longrightarrow\ \pi(t)\notin(v_m,v_0).
\end{array}
\tag{10}
\]

**星形的必要性。** 第一条叶根边的 L 给出 \(\mathrm O_0\)。在间隙 \(k<m\) 中，以 \(x_{k-1}\) 为起点的边之 M 给出上界 \(v_k\)，以 \(x_k\) 为起点的边之 L 给出下界 \(v_{k+1}\)。最后一个叶子的 M 给出 \(\mathrm O_m\)，同一条叶根边的 Q 给出 \(\mathrm O_{m+1}\)。

**路径的必要性。** 第一条边的 L 给出 \(\mathrm O_0\)。在间隙 \(k<m\) 中，第 \(k\) 条边的 M 给出上界，第 \(k+1\) 条边的 L 给出下界。最后一条边的 M 给出 \(\mathrm O_m\)。在 \(x_m\) 之后，各条路径边的 Q 联合排除 \((v_h,v_{h-1})\)、\(1\le h\le m\) 的并集。该并集是从 \((v_m,v_0)\) 中去掉中间值 \(v_1,\ldots,v_{m-1}\) 后的集合。那些中间值已出现在指定顶点，单射性排除了它们在外部点再次出现。因此得到 \(\mathrm O_{m+1}\)。

**星形的充分性。** 考察边 \((x_{h-1},x_m)\)，其低、高值分别为 \(v_h,v_0\)。起点之前，\(x_0\) 之前的点值 \(>v_1\ge v_h\)，较早叶子的值 \(>v_h\)，较早间隙 \(k<h\) 中的值 \(>v_{k+1}\ge v_h\)，所以 L 成立。两个端点之间，后面的叶值 \(<v_h\)，而间隙 \(k\ge h\) 的值 \(<v_k\le v_h\)，最后一个间隙也包括在内，所以 M 成立。根之后，由式 (10) 排除 \((v_m,v_0)\)，也就排除其中的 \((v_h,v_0)\)，故 Q 成立。

**路径的充分性。** 考察边 \((x_{h-1},x_h)\)，其低、高值为 \(v_h,v_{h-1}\)。由同样的较早顶点及间隙界，起点之前所有值都大于 \(v_h\)。内部恰为第 \(h\) 个间隙，值均 \(<v_h\)。在右侧，后续指定顶点及后续间隙的值均 \(<v_h\)，而 \(x_m\) 之后的点值避开

\[
(v_m,v_0)\supseteq(v_h,v_{h-1}).
\tag{11}
\]

故 L、M、Q 都成立。若 \(m=1\)，中间条件族 \(1\le k<m\) 为空，证明仍然适用。∎

式 (11) 清楚写出了历史快照中排版不完整的区间包含关系。历史审查者明确判断该错误仅属排版，所提供的展示修改记录也已修正它。本报告显式采用这项已有记录的排版修正，并未静默改变数学断言。

### 引理 5. 同时旋转在任意标记子集上给出双射

对每个 \(A\)-星形施行

\[
(v_1,\ldots,v_m,v_0)\longmapsto(v_0,v_1,\ldots,v_m),\qquad
e_h=(x_{h-1},x_m)\longmapsto f_h=(x_{h-1},x_h).
\tag{12}
\]

在所有分量上同时这样做，得到标记 \(A\)-对象到标记 \(B\)-对象的双射 \(\Phi\)，并附有边双射 \(\theta_{\pi,M}:M\to N\)。其逆映射 \(\Psi\) 将每条标记下降路径的值旋转回原状，并把相邻边换成对应的星形边。

**操作的定义。** 不同分量的顶点集不交，每次旋转仅置换自身顶点上的值。因此所有替换同时施行后仍得到一个排列 \(\sigma\)。新边互异，式 (12) 给出双射 \(M\to N\)。反向替换也同样定义了排列及标记集合。但还必须证明每一条新标记都是模式出现；仅仅顶点集不交，并不能证明这一点。

**所有分量的有效性。** 固定分量 \(C\)，使用式 (8) 的记号。自身旋转保持位置与值的递减列表，所以保持式 (10) 中的所有界。现在检查任意其他分量 \(D\) 的旋转是否保持 \(C\) 的条件；当 \(C\) 包围 \(D\) 时，还须检查反过来是否保持 \(D\) 的条件。

若位置区间不交，则 \(D\) 的所有顶点都位于 \(C\) 的同一个外侧。它们的值原本都满足式 (10) 在该侧的条件；置换这些值之后，每个点仍满足该条件。即使右侧允许值分成两个互不相接的区间，这一点也成立。

若 \(D\) 位于 \(C\) 的中间间隙 \(k<m\)，则 \(D\) 的所有值都在 \((v_{k+1},v_k)\) 内，旋转保持这一点。若位于最后一个间隙，则所有值 \(<v_m\)，同样保持。这检查了**内层**旋转对**外层**分量的影响。

反过来，假设 \(D\) 位于 \(C\) 的第 \(k\) 个间隙，记

\[
a=\min\{\pi(d):d\in D\},\qquad b=\max\{\pi(d):d\in D\}.
\tag{13}
\]

\(D\) 旋转时这两个界不变。如果 \(k<m\)，则

\[
v_{k+1}<a\le b<v_k.
\tag{14}
\]

\(C\) 的顶点 \(x_t\) 在星形、路径两种排列中的可能值依次为

\[
\begin{cases}
(v_{t+1},v_t),&0\le t<m,\\
(v_0,v_m),&t=m.
\end{cases}
\tag{15}
\]

当 \(t\le k-1\) 时，该顶点在 \(D\) 之前，两种可能值均至少为 \(v_k>b\)。顶点 \(x_k\) 在 \(D\) 之后，其两种可能值分别为 \(v_{k+1}<a\)、\(v_k>b\)。满足 \(k<t<m\) 的顶点也在 \(D\) 之后，两种可能值均不超过 \(v_{k+1}<a\)。最后一个顶点 \(x_m\) 在 \(D\) 之后，其可能值为 \(v_0>b\)、\(v_m<a\)。因此，在 \(D\) 之前的每个 \(C\)-值都大于所有 \(D\)-值，而在 \(D\) 之后的每个 \(C\)-值都在 \([a,b]\) 之外。这比式 (10) 对 \(D\) 的两个外侧要求更强。\(C\) 没有顶点位于 \(D\) 区间内部，所以 \(D\) 的内部条件不受影响。

对于最后一个间隙 \(k=m\)，所有 \(D\)-值均 \(<v_m\)。每个 \(t<m\) 的 \(x_t\) 都在 \(D\) 之前，两种可能值都满足 \(\ge v_m>b\)。在 \(D\) 之后唯一的 \(C\)-顶点是 \(x_m\)，其两种可能值 \(v_0,v_m\) 都大于 \(b\)。因此该情形的外侧条件同样成立。我们已在两种排列方式下检查了**外层**旋转对**内层**分量的影响。

由引理 3，以上情形穷尽全部可能。检查只依赖固定的位置集、值集以及每个分量顶点的两种可能值，没有使用某种特定旋转顺序。未被操作的点保留原先允许的值；每个发生变化的点，相对于任意其他分量均满足上述相应情形。因此对 \(\Phi\)、\(\Psi\)，所有分量的条件 (10) 都能**同时**保持。由引理 4，所有新标记都是相应模式的出现。

**两侧逆映射。** 每颗星都被换成相同顶点集上的连通路径，没有添加不同分量之间的标记边，所以新标记图的分量顶点集与原来完全相同。反向操作能准确找回这些分量，把各个值列表旋转回去，并恢复每条原边。以路径为起点同理可得

\[
\Psi\Phi=\mathrm{id},\qquad \Phi\Psi=\mathrm{id}.
\tag{16}
\]

标记集合为空时，两个映射都保持排列不变。输出中即使出现了新的未标记模式出现，也不改变这些标记分量，无须排除。因此双射确实适用于任意标记子集。∎

### 引理 6. 对象及每条边的取逆等变性

对边 \(e=(i,j)\)，定义

\[
T_\pi(e)=\bigl(\min(\pi(i),\pi(j)),\max(\pi(i),\pi(j))\bigr),
\qquad
(\pi,M)^T=(\pi^{-1},T_\pi M).
\tag{17}
\]

转置将 \(\pi\) 的 \(A\)-出现双射到 \(\pi^{-1}\) 的 \(A\)-出现，对 \(B\) 也如此。若 \(\Phi(\pi,M)=(\sigma,N)\)，则

\[
\Phi((\pi,M)^T)=\Phi(\pi,M)^T,
\qquad
\theta_{\pi^{-1},T_\pi M}(T_\pi e)
=T_\sigma\bigl(\theta_{\pi,M}(e)\bigr)
\quad(e\in M).
\tag{18}
\]

**证明。** 转置排列图会交换排好序的位置边界列表和值边界列表。底层排列 \(12,21\) 均为自逆，而 \(R\) 在 \((a,b)\mapsto(b,a)\) 下不变。一个严格矩形中的禁止点与转置矩形中的禁止点双向对应。因此得到出现集合的双射，其逆为 \(T_{\pi^{-1}}\)。

将式 (9) 的一个 \(A\)-星形转置，递增位置及对应值变为下列三行；其中第一行是位置，第二、三行分别为旋转前、后的值：

\[
\begin{array}{ll}
\text{positions}:&(v_m,v_{m-1},\ldots,v_0),\\
\text{values before rotation}:&(x_{m-1},\ldots,x_0,x_m),\\
\text{values after rotation}:&(x_m,x_{m-1},\ldots,x_0).
\end{array}
\tag{19}
\]

原来的每条边变为 \((v_h,v_0)\)，故这恰为转置后的星形。原旋转满足 \(\sigma(x_t)=v_t\)，所以最后一行正是其逆排列。不同原分量的顶点集在转置下成为互不相交的值集，并准确给出全部转置分量。所有分量之外的点在两边均保持不变。这就证明了对象层面的恒等式，其底层排列是 \(\sigma^{-1}\)。

对单条边 \(e_h=(x_{h-1},x_m)\)，转置得到 \((v_h,v_0)\)；在按位置递增排列的转置星形中，它的边序号为 \(m-h+1\)。旋转该星形后，它变为 \((v_h,v_{h-1})\)。另一方面，先旋转原边得到 \(f_h=(x_{h-1},x_h)\)，其在 \(\sigma\) 中的值为 \((v_{h-1},v_h)\)，再转置同样得到 \((v_h,v_{h-1})\)。因此式 (18) 的逐边恒等式对每条标记边成立，包括自身转置不变的分量中的边，不需要对中间边或方向另设例外。

由于 \(\Psi=\Phi^{-1}\)，对两种逆像施行 \(\Phi\) 并利用单射性，可得 \(\Psi\) 的对象等变性；将边双射取逆，则得到逆向的逐边等变性。因此转置不动的对象双射对应，而这类对象恰为

\[
\pi\in I_n,\qquad T_\pi(M)=M.
\tag{20}
\]

在这样的对象上，转置是标记边集合上的对合。式 (18) 把不动边送到不动边，把两边轨道送到两边轨道。反过来，若某条边的像是转置不动的，由式 (18) 与 \(\theta\) 的单射性可知原边也不动。因此单边轨道数与双边轨道数都被**分别**保持。∎

### 引理 7. 两种轨道权重恢复每个出现次数

对 \(\pi\in I_n\)，令 \(f_A(\pi)\)、\(d_A(\pi)\) 分别为 \(T_\pi\) 在**整个** \(\operatorname{Occ}_A(\pi)\) 上的单元素轨道数与双元素轨道数；同样定义 \(f_B,d_B\)。则

\[
\operatorname{occ}_A(\pi)=f_A(\pi)+2d_A(\pi),\qquad
\operatorname{occ}_B(\pi)=f_B(\pi)+2d_B(\pi).
\tag{21}
\]

并且对每个 \(n\)，\(A,B\) 的出现次数生成多项式相等。

**证明。** 有限集合上一个对合的每个轨道都是 \(\{e,T_\pi(e)\}\)，大小为一或二，两个这样的集合要么相同，要么不交，从而得到式 (21)。转置不变的标记子集恰是这些轨道的并。

在 \(\mathbb Z[u,v]\) 中，给被选中的单边轨道权重 \(u\)，被选中的双边轨道权重 \(v\)，未被选中的轨道权重 \(1\)。以 \(s(M),q(M)\) 分别表示被选中的单边、双边轨道数。对固定 \(\pi\)，各轨道可独立选入，因此

\[
\sum_{\substack{M\subseteq\operatorname{Occ}_A(\pi)\\T_\pi M=M}}
u^{s(M)}v^{q(M)}
=(1+u)^{f_A(\pi)}(1+v)^{d_A(\pi)}.
\tag{22}
\]

这只是有限乘积的分配律展开，也包括空乘积；\(B\) 一侧有相同公式。引理 6 给出了所有不动标记对象之间的双射，且保持两个指数，故

\[
\sum_{\pi\in I_n}(1+u)^{f_A(\pi)}(1+v)^{d_A(\pi)}
=\sum_{\pi\in I_n}(1+u)^{f_B(\pi)}(1+v)^{d_B(\pi)}.
\tag{23}
\]

施行多项式环同态

\[
\mathbb Z[u,v]\longrightarrow\mathbb Z[y],\qquad
u\longmapsto y-1,\quad v\longmapsto y^2-1.
\tag{24}
\]

每一项变为 \(y^{f+2d}\)，因而

\[
\sum_{\pi\in I_n}y^{\operatorname{occ}_A(\pi)}
=\sum_{\pi\in I_n}y^{\operatorname{occ}_B(\pi)}.
\tag{25}
\]

所有和与积都有限，不涉及收敛或除法。\(y^k\) 的系数恰为出现 \(k\) 次的对合数，所以对每个 \(k\ge0\)，得到式 (6) 的 \(A,B\) 情形。

两个独立权重对于此论证至关重要。如果仅按标记边总数加权，得到的是 \((1+t)^f(1+t^2)^d\)；此时不能把式 (24) 当成合法的单变量代换。正是两个轨道计数的分别保持，才使这里的系数恢复成立。∎

### 引理 8. 反向补与全部边界情形

在 \([n]\) 上令 \(r(i)=n+1-i\)，定义 \(\operatorname{rc}(\pi)=r\pi r\)。这个排列集合上的对合保持 \(I_n\)，并把 \(p_1\)-出现双射到 \(p_2\)-出现，把 \(p_4\)-出现双射到 \(p_3\)-出现。

**证明。** 由于 \(r^2=\mathrm{id}\)，反向补是自身的逆，且

\[
(r\pi r)^2=r\pi^2r.
\tag{26}
\]

所以它将对合双射到对合。位置对 \((i,j)\) 变为 \((r(j),r(i))\)。位置次序与值次序同时颠倒，所以递增仍为递增，递减仍为递减。格子变换为

\[
(a,b)\longmapsto(2-a,2-b),\qquad R\longmapsto R'.
\tag{27}
\]

为了同时检查严格边界，将 \(s\mapsto n+1-s\) 延伸到边界值 \(0,n+1\)。它颠倒式 (4) 中四个排好序的边界，把秩为 \(a\) 的开区间变为秩为 \(2-a\) 的开区间；值方向也相同。因此空阴影矩形双向对应，各指定模式对的出现次数得到保持。

当 \(n=0\) 时，有唯一的空对合，出现集合与标记集合均为空，分量操作都是空操作，生成多项式为 \(1\)。当 \(n=1\) 时同样没有下标对，生成多项式仍为 \(1\)。在这两种情形下，式 (6) 的计数在 \(k=0\) 时为 \(1\)，在 \(k>0\) 时为 \(0\)。任意 \(n\) 的空标记已由引理 5 覆盖，单边分量 \(m=1\) 已由引理 4 覆盖。对任意 \(n\)，无法实现的次数在两侧系数均为零，特别包括 \(k>\binom n2\)。结论本身对全部允许的 \(n,k\) 都是恒等式，因此没有额外的“等号成立条件”。∎

**定理 1 的保存普通论证完成。** 引理 7 给出 \(p_1,p_4\) 的等分布，引理 8 给出 \(p_1,p_2\) 及 \(p_4,p_3\) 的等分布，三者合并即得到任意两个模式之间的式 (6)。至此，提交普通稿的论证已完整展开；其证据等级仍保持第 1 节所述状态。

## 5. 保存的验证结果及各类证据的实际范围

### 5.1 历史普通稿审查

唯一保存的审查记录给出 **`NO_ISSUES_FOUND`**，问题列表为空。它说明精确的 v2 图示、严格矩形条件及对合上所有 \(n,k\) 的陈述，与独立取得的原始来源一致。其数学评估明确涵盖 L/M/Q 等价性、度数约束、单间隙嵌套、外部条件的双向刻画、内外层同时旋转、两个逆恒等式、包含自转置分量的对象与逐边等变性、单/双轨道权重、代换、系数、反向补和端点。审查报告称未发现额外假设、实质缺口或循环论证，并明确把区间错误认定为纯排版问题。这些是**历史 AI 审查的结论**，并非本次重新进行的独立审查结论。[保存的精确审查](materials/reviewed-source/dossier.json)；[审查者最终答复](materials/reviewed-source/tasks/task-record-003/attempt-record-004/answer.md)。

审查文字提到其他详细文件中记录了 18 项证明检查和 19 条文献查询。但这些文件并未收入本次原生冻结包。规范化保存的审查中，`checks` 及结构化文献查询数组仍为空；正文里的历史引用不能事后填充这些数组。材料缺失限制了读者对历史检查过程的追溯，但不改变原有 verdict。

### 5.2 有限挑战

历史审查者报告独立编写并穷尽执行了以下检查，显式提供的 showcase 摘要也重复记录了这些结果：

| 范围 | 记录规模 | 记录结果及其与证明的关系 |
|---|---:|---|
| 大小从 \(0\) 到 \(8\) 的所有排列，以及两侧每个适用标记子集 | 46,234 个排列；130,354 个标记 \(A\)-对象及 130,354 个标记 \(B\)-对象 | 逆映射、对象等变性和逐边等变性全部通过；对引理 5–6 的有限挑战 |
| \(n\le7\) 的全部合格星形/路径分量配置 | 199,630 个配置 | 外部条件等价性的两个方向均通过；对引理 4 的有限挑战 |
| \(n\le11\) 的所有对合 | 48,928 个对合 | 四种模式的出现次数直方图相同；对定理 1 的有限挑战 |

此外，还记录了第 3 节中的朴素限制反例 \(213\mapsto312\)。它否定的是提交论证所避开的捷径。记录没有报告实际候选证明的反例。[冻结审查证据](materials/reviewed-source/dossier.json)；[显式提供的审查摘要](materials/showcase/review.md)。

上述数量是历史记录中的结果，不是 Organize 期间重复计算所得。被称为 `review/check_candidate.py` 的脚本及其结果 JSON 文件，既不在原生清单中，也不在 showcase 补充文件表中。因此本包没有提供可执行的有限检查证书，也不能给出这些历史挑战的完整复现命令。有限检查寻找有界范围内的反例或实现错误；任何有限上界都不能证明一般定理。上面的普通证明没有把这些实验当作前提。

### 5.3 后续部分 Lean 工作

下表转述显式[形式化补充说明](materials/showcase/formal/README.md)所记范围，而不是对 Lean 文件的重新检查或执行。材料包括 12 个证明模块，以及用于检查的 `MeshPartial` 入口。

| 模块 | 记录中的内容 | 与本报告的对应关系 |
|---|---|---|
| `MeshDefinitions`、`MeshStructure` | 实际有限排列、严格空矩形、L/M/Q 等价性、局部图结构 | 定义及引理 1–2 的局部部分 |
| `MeshSymmetry` | 取逆与反向补；底层排列相同的模式之间的完整分布等式 | 引理 6、8 的对称性；它们本身不连接 \(12\) 与 \(21\) 两组 |
| `MeshComponents`、`MeshRotation` | 单个分量的外部充要条件、旋转及其逆 | 引理 4，以及引理 5 的单分量部分 |
| `MeshEquivariance`、`MeshNesting`、`MeshCompatibility` | 单分量取逆相容性、逐边公式、嵌套与关键相容条件 | 引理 3、5、6 的局部构件 |
| `MeshOrbitCounting`、`MeshPolynomial`、`MeshTransport` | 有限轨道权重、实际出现集合的多项式系数、等变边映射的保权性质 | 引理 7 的计数工具及传递后果 |
| `MeshReduction` | 在显式全局标记传递前提下推出完整四模式陈述 | 到定理 1 的条件性归约 |
| `MeshPartial` | 导入模块、展示关键类型及 107 条定理的公理依赖 | 检查入口，不是缺失前提的证明 |

记录的条件定理准确类型为：

```lean
Mesh.correctedConjecture_of_markedTransport :
  (∀ (n : ℕ), Nonempty (Mesh.MarkedTransport n)) → Mesh.correctedConjecture
```

其中 `Mesh.correctedConjecture` 据记录定义了原题四模式对所有 \(n,k\) 的计数相等。**上述前提尚未证明，也没有被声明为公理。** 缺失工作包括任意出现标记子集的规范分量分解与重构；全局同时旋转的组装及双向有效性；对象与逐边的全局等变性，从而为每个 \(n\) 实际构造 `MarkedTransport n`。已有局部分量定理不能自动实例化这一全局前提。因此，所给证据中**没有完整原猜想的无条件 Lean 定理**。

摘要记录 Lean 版本为 **4.35.0**，mathlib 提交固定为 **`56a005855ea17e0b0958f73ec801ae140b0a1679`**，并记录主控曾执行以下检查：

| 历史检查 | 命令 | 记录退出码 |
|---|---|---:|
| 编译 | `lake build` | 0 |
| 类型与传递公理依赖 | `lake env lean MeshPartial.lean` | 0 |
| 经过 Lean 内核的 fresh 重放 | `lake env leanchecker --fresh --verbose MeshPartial` | 0 |

摘要称这 107 条受审计定理的传递公理至多为 `propext`、`Classical.choice`、`Quot.sound`，没有证明占位符或绕过内核的 native 计算，并称发布 Lean 源码哈希与已编译、重放的版本一致。这是**记录中的主控审计**，日志摘要哈希保存在 [verification.json](materials/showcase/verification.json)；原始日志未打包，也没有另外的 AI 形式化审查。内核重放仍信任 Lean 自身内核，验证的是已有形式陈述及其显式假设，不能认证自然语言对应关系或补齐全局构造。

补充说明将前八个证明模块归于原生求解，记录主控后来修复了 `MeshOrbitCounting` 与 `MeshPolynomial` 的编译错误，并添加 `MeshTransport`、`MeshReduction`、`MeshPartial`。因此，早先的编译错误也是历史的一部分；具体诊断在本包中不可得。后来的成功检查不能归到较早的普通稿审查者名下。showcase 导出本身没有重新构建 Lean，本次 Organize 也没有执行 Lean 或 Lake。

## 6. 原题覆盖与未解决的限制

| 要求 | 保存普通论证的陈述 | 保留的证据边界 |
|---|---|---|
| 精确 v2 模式及严格矩形 | 式 (2)–(5)、引理 1 和引理 8 使用给定阴影集合 | 历史来源比对有记录；PDF/TeX 未收入本原生包 |
| 全体对合 | 引理 6 限制到转置不动对象，引理 7 恢复未标记计数 | 没有声称可直接限制任意标记 |
| 任意标记子集 | 引理 2–5 不要求极大性，覆盖空标记及嵌套标记 | 对应的 Lean 全局组装缺失 |
| 所有 \(n,k\ge0\) | 引理 7 的有限多项式恒等式及取系数，引理 8 的端点 | 有限测试本身仅覆盖有限范围 |
| 四个边缘分布 | 引理 7 连接 \(p_1,p_4\)，引理 8 连接 \(p_1,p_2\) 及 \(p_4,p_3\) | 不主张联合分布结论 |
| 保存的 coverage 字段 | 候选 `scope=UNKNOWN`；审查 `original_problem_coverage=UNKNOWN` | 本报告不把任何一个字段升级为 `FULL` |

**保存的普通稿审查**没有指出未解决的数学缺口。保存的两个 `remaining_obligations` 数组均为空。但这是历史字段，不是新的完成认证，也不消除明确存在的形式化缺口。规范化审查记录还保留 `formal_check=null`、`formal_receipt=null`、`evidence_assessment.supported=false`，且没有填写评估策略或理由。这样的旧版空结构不能解释成成功的现代形式化凭据，也不能解释成已独立支持的覆盖评估。

仍然存在的限制包括：全局 Lean 传递构造缺失；没有后续独立形式化审查；没有外部专家审稿或陈述等价性认证；下节所列不可访问文献；详细审查及检查器材料缺失；以及显式 solver linkage 缺失。将来完成全局构造，或提出任何普通证明修复，都需要新的 Solve/Verify。本报告没有提出数学修复，也不修改候选或审查。

## 7. 来源、已知方法、新颖性与参考文献

以标记出现将星形、路径互换的方法，在 Zhang–Zhao 的工作中已有先例。候选稿明确承认这一来源，也承认主控路线稿和结构草稿属于**未验证的协助，而非证明前提**。这里额外声称的范围，是利用对象及逐边取逆等变性限制到对合，再以两种轨道权重恢复分布。原作者在 2026-10-11 修订版中继续列出该猜想，是该日作者提出未决问题的证据，不是对报告制作时仍然开放的独立确认。

历史审查者报告截至 **2026-10-21** 共进行了 19 条定向查询及原始来源追查，没有找到更早的完整公开解答。v2 在承认 7 月全排列结果的同时仍保留修正版对合猜想。有关分层排列的后续论文适用域不同。还找到了一个交替排列相关预印本，但经尝试的 HAL/SSRN 路径无法取得全文，因此不能排除该文含有其他相关结果。索引滞后、不可访问、未索引或未发表工作仍是限制。因此 **`POTENTIALLY_NEW` 是保存的有界检索评估，不是确认首解或全球优先权**。本次 Organize 没有更新文献状态。[历史新颖性记录](materials/reviewed-source/dossier.json)；[显式提供的审查摘要](materials/showcase/review.md)。

1. **Qi Fang、Shishuo Fu、Sergey Kitaev、Haijun Li、Xinyu Su、Ziyao Sun**，*On mesh patterns of short length: Equidistribution and enumeration*，arXiv:2606.14367v2，修订日期 2026-10-11。Definition 2.1 见印刷第 5–6 页；等分布量词见第 2 页；corrected Conjecture 1、Remark 4.1 及脚注 3 见第 17 页。保存审查记录的版本时间为 2026-10-11 12:48:29 UTC，取得材料的日期为 2026-10-21；TeX 定位为 `mesh_pattern_arXiv_version_1011.tex` 的第 1007–1012 行。[版本页](https://arxiv.org/abs/2606.14367v2)、[PDF](https://arxiv.org/pdf/2606.14367v2)、[TeX](https://arxiv.org/src/2606.14367v2)。
2. **Zuo-Ru Zhang、Hongkuan Zhao**，*The last distribution-equivalence class of mesh patterns of length 2*，arXiv:2607.04111，2026-07-05。Theorem 1.1 及第 1–2 节，包括第 3–4 页的标记出现构造，提供了已知全 \(S_n\) 结果及方法。历史审查者称阅读了完整五页正文，并将其与修正后的全 \(I_n\) 目标区分。[摘要](https://arxiv.org/abs/2607.04111)、[PDF](https://arxiv.org/pdf/2607.04111)。
3. **Jiahao Zhang、Sergey Kitaev、Artem Pyatkin、Xinyu Su**，*Equidistribution of mesh patterns of short length on layered permutations*。保存审查记录其在线出版日期为 2026-10-15、期刊卷年份为 2027，检查日期为 2026-10-21。其定义域是分层排列，而非全部对合。[机构库条目](https://strathprints.strath.ac.uk/97484/)、[记录的 PDF](https://strathprints.strath.ac.uk/97484/7/Zhang-etal-DM-2026-Equidistribution-of-mesh-patterns-of-short-length-on-layered-permutations.pdf)。
4. **交替排列相关预印本**，[记录的 SSRN 定位](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7425138)。本次使用的冻结摘录没有提供完整题名与作者表，历史审查者未能获取全文。此项标记一个未完成的文献比较，不能作为已读且排除了先前结果的来源。
5. **Xinyu Su 的公开 arXiv 索引**，[元数据页面](https://arxiv.symmetricfunctions.com/author/xinyu-su)。继承的问题参考文献将其列为修订版本元数据的辅助来源；它不是开放状态的独立证明。

继承的问题难度及可行性文字属于求解前评估：排名 1、相当实质的有限双射项目、Lean 可行性未知，以及主控报告的 \(n\le7\) 可行性测试。这些是估计和历史背景，不是成功概率、证明或后来的验证结果。补充摘要记录 Find 已完成，但本包没有提供完整 Find 或 Solve 历史。

## 8. 可复现步骤与来源身份

本次编辑读取了原生清单列出的两个文件，以及显式提供的 showcase 内联正文与修改记录，仅进行了轻量的字节身份和报告一致性检查。原生文件大小与 SHA-256 均匹配清单；内嵌证明与候选内容的摘要也匹配保存值。这些检查均不是数学验证。

形式化补充稿给出以下**供今后复现的指令**：安装官方 Elan 后，在附入的 `materials/showcase/formal/` 目录中执行：

```sh
lake update
lake exe cache get
lake build
lake env lean MeshPartial.lean
lake env leanchecker --fresh --verbose MeshPartial
```

这些命令只是转录来源说明，**本次没有执行**。固定版本的 `lean-toolchain`、`lakefile.toml`、`lake-manifest.json` 列在补充文件表中；工具链和大型依赖须另行下载。复现应保持并核对声明的 Lean、mathlib 版本，只能确认已有部分陈述及其前提。材料没有提供构建完整猜想无条件定理的命令。

例如，可用下列命令核对展示证明稿的字节身份：

```sh
sha256sum materials/showcase/proof.md
```

预期的**展示文件**摘要为 `0788dc26255153faaab5e5458b373d279767b950bd702204534ce6d7cba26e47`。它与下表的历史受审证明摘要有意区分。对未提供的有限检查脚本及原始审查材料，本报告既不声称已复现成功，也不编造可执行复现命令。

| 哈希输入域 | SHA-256 | 含义 |
|---|---|---|
| 历史候选内容 | `74183c541d86feb6ecc57151b1cfc661663afb1d50b985c806defec3bf0c4e6f` | `claim + newline + proof` 的 UTF-8；已从冻结 dossier 重现 |
| 历史普通证明 | `8c6844e8b904f446524ec16aea6baf94343d317ba3b6b089fca5305b66e1a01b` | 内嵌证明的 UTF-8，即受审的不可变正文 |
| 原始详细审查报告 | `08956a0884958da8013ac18e1d264a804e72df0fdec1f5e15e2fed64669c68e9` | showcase 摘要提供的哈希；详细报告本体未在此附入 |
| 后来的 showcase 证明 | `0788dc26255153faaab5e5458b373d279767b950bd702204534ce6d7cba26e47` | 带有已说明排版及引用修改的展示版本 |
| 问题陈述文本 | `bbb48b9352ff8f3728416867a6ced5b0387b93bdfb4c7e73cd079a1eac2f0521` | UTF-8 `Problem.statement` 的 SHA-256；亦为形式化凭据的陈述文本输入域，但此处没有保存此类凭据 |
| 完整规范问题记录 | `e7805279c77205034b016c7e85cfefbbbec3ae5f85cb44f0003fb5232601d4f2` | 清单的 `discovery.problem_fingerprint`，包括元数据与旧字段规范化；作为另一输入域提供 |

最后两个哈希的输入不同，不能将它们当作同一种校验值相互比较。哈希仅标识指定输入域的字节，不认证数学真理或自然语言与形式陈述的对应。后来的展示稿摘要不能取代历史受审证明的身份。

## 附录 A. 保存工作与尝试的简明时间线

| 时间或先后关系 | 保存事件 | 可以与不可以推断的内容 |
|---|---|---|
| 2026-07-05 | Zhang–Zhao 的已知全排列结果 | 方法先例，不是所选对合题的解答 |
| 2026-10-11 | 原作者 v2 保留修正版猜想 1，并区分较早错误版本 | 历史作者猜想，不是今日开放状态认证 |
| 历史普通稿审查之前；缺少准确会话关联 | showcase 补充摘要称原生 Find 完成；主控路线及结构草稿协助原生求解；完整普通稿已经写出；原生 Solve 在形式化期间因 usage limit 停止，未提交最终候选 | 随后由主控提交普通快照。Verify dossier 没有保存显式 solver linkage，不据此编造会话关联或不可见的尝试序列 |
| 2026-10-21，10:39:24–10:50:50 UTC | 可见 Verify 记录创建并完成，保存一个候选及一个完成的审查 | 这是 dossier 时间戳，不是完整事件轨迹。结论 `NO_ISSUES_FOUND`，新颖性 `POTENTIALLY_NEW`，历史 coverage 仍为 `UNKNOWN` |
| 该历史审查期间 | 报告来源比较、有限挑战、朴素限制反例及有界文献工作 | 审查者称未查阅求解者/主控历史；详细支持脚本和报告仅有引用，未收入当前原生包 |
| 后续主控工作，摘要证据日期为 2026-10-21 | 修复编译、添加归约/传递/检查模块、检查 107 条定理、公理依赖检查及 fresh 内核重放 | 与较早普通稿审查分离；完整形式化全局构造仍缺；逐命令准确时间和原始日志未提供 |
| 后来的 showcase 展示整理 | 三项排版编辑、公开/本地引用更新，以及双语文档 | 数学论证据记录未改；没有新独立审查，导出时也没有重新构建 Lean |
| 2026-10-24 冻结与本次 Organize | 原生来源修订 9 被冻结；依据该快照及显式补充整理两份自足报告 | 仅编辑阐释和一致性核对，没有新的文献状态或证明认证 |

原生 dossier 只展示一个普通候选和一个完成的历史审查。`visible_research_notes` 与 `evidence_receipts` 为空，`review_source` 为 null。清单明确记载 solver linkage 缺失，不能通过题名匹配恢复废弃尝试、隐藏求解笔记或精确 Solve 时间线。上表将额外历史归属于 showcase 补充摘要，没有编造数据库关联。

## 附录 B. 材料索引、可得性与信任边界

### B.1 原生冻结材料

| 材料 | 可得性及用途 | SHA-256 |
|---|---|---|
| [冻结 dossier](materials/reviewed-source/dossier.json) | 42,515 字节；含问题、完整普通候选、精确保存审查、参考文献及一条可见时间线记录 | `00939d2d0d9d27a5dace6a3af7e9f79f4367f8939d5ed9c9aeffef53f7d1d581` |
| [保存的历史审查答复](materials/reviewed-source/tasks/task-record-003/attempt-record-004/answer.md) | 1,657 字节；含结论与限制的最终审查文字 | `e8f3b667a21802cc3c6d30e52f4bf6af1424bc20c0b3e0f7c8cfd6ce6a4f2033` |

原生清单只列这两个文件，遗漏列表为空。这个空列表不表示 dossier 内提到的所有材料都已附入。候选完整证明是从内嵌 `proof` 字段读取的。详细独立审查报告、18 项检查证据文件、快照身份文件、取得材料及模式比对记录、网络调用日志、有限检查脚本/结果、本地 PDF/TeX、主控草稿和状态检查文件，虽在历史文字中被引用，却**不是原生附件**。原始传输事件的引用也没有对应附件，不能用来证明未见行动。这里没有提供或重构隐藏推理。

### B.2 显式提供的 showcase 补充

下列文件是**显式 showcase 补充**，不是原生清单收集条目。用户提供了四份内联正文（`README.md`、`review.md`、`formal/README.md`，以及省略冗余文件哈希索引的 `verification.json` 版本）、一份展示证明差异记录和这份 24 文件大小/哈希目录。本次编辑没有作为原生文件独立取得完整 `.lean` 正文或单独的 showcase 证明文件；但普通证明本身已完整内嵌在 dossier 中。发布步骤将把相同的冻结 showcase 文件附入以下链接。仅凭文件名或哈希不能视为已经阅读其数学内容；第 5 节的源码内容描述明确归于所提供的摘要。

下表短摘要是所给 SHA-256 的**前 12 个十六进制字符**，仅供识别。完整提供值保存在 showcase 验证记录及冻结补充目录中。本报告不声称重新比较了本次未提供实体的 showcase 文件字节。

| 补充材料 | 字节 | 所给 SHA-256 前缀 | 用途与来源地位 |
|---|---:|---|---|
| [README.cn.md](materials/showcase/README.cn.md) | 2,099 | `0b78e1af82f0` | 中文案例总览；索引及状态 |
| [README.md](materials/showcase/README.md) | 2,564 | `ddd34f98b817` | 英文案例总览；已提供完整内联正文 |
| [formal/MeshCompatibility.lean](materials/showcase/formal/MeshCompatibility.lean) | 6,674 | `ff83da03043b` | 局部及嵌套相容条件 |
| [formal/MeshComponents.lean](materials/showcase/formal/MeshComponents.lean) | 10,675 | `3882654f5bf9` | 单分量外部条件 |
| [formal/MeshDefinitions.lean](materials/showcase/formal/MeshDefinitions.lean) | 5,780 | `9bac2a293d76` | 排列、矩形及目标定义 |
| [formal/MeshEquivariance.lean](materials/showcase/formal/MeshEquivariance.lean) | 4,463 | `997a9f7d8de6` | 单分量及逐边等变性 |
| [formal/MeshNesting.lean](materials/showcase/formal/MeshNesting.lean) | 2,752 | `81055e6a56cc` | 嵌套条件 |
| [formal/MeshOrbitCounting.lean](materials/showcase/formal/MeshOrbitCounting.lean) | 6,033 | `24c82721a9c6` | 有限轨道权重 |
| [formal/MeshPartial.lean](materials/showcase/formal/MeshPartial.lean) | 4,677 | `d91e8f23ff1c` | 导入、类型及公理检查入口 |
| [formal/MeshPolynomial.lean](materials/showcase/formal/MeshPolynomial.lean) | 4,138 | `33f6ed655e24` | 出现计数的多项式系数 |
| [formal/MeshReduction.lean](materials/showcase/formal/MeshReduction.lean) | 3,516 | `57a2b6b1a435` | 带全局前提的原题归约 |
| [formal/MeshRotation.lean](materials/showcase/formal/MeshRotation.lean) | 6,677 | `8222189953c3` | 单分量旋转及逆 |
| [formal/MeshStructure.lean](materials/showcase/formal/MeshStructure.lean) | 2,076 | `3e2f503183dd` | 局部标记图结构 |
| [formal/MeshSymmetry.lean](materials/showcase/formal/MeshSymmetry.lean) | 6,750 | `8143c05a87b7` | 取逆、反向补及同底层模式等分布 |
| [formal/MeshTransport.lean](materials/showcase/formal/MeshTransport.lean) | 2,051 | `b5e2d2b6ed53` | 等变边映射的保权传递 |
| [formal/README.cn.md](materials/showcase/formal/README.cn.md) | 2,564 | `a80a05b73c5c` | 中文形式化范围与复现说明 |
| [formal/README.md](materials/showcase/formal/README.md) | 3,106 | `6b87f8ab73b0` | 英文形式化说明；已提供完整内联正文 |
| [formal/lake-manifest.json](materials/showcase/formal/lake-manifest.json) | 3,557 | `35d978fa9cd2` | 依赖锁定清单 |
| [formal/lakefile.toml](materials/showcase/formal/lakefile.toml) | 498 | `87aac4742e53` | Lake 项目配置 |
| [formal/lean-toolchain](materials/showcase/formal/lean-toolchain) | 25 | `ca5f1f601d34` | Lean 版本固定 |
| [proof.md](materials/showcase/proof.md) | 22,270 | `0788dc262551` | 普通证明展示版；已提供历史稿及展示差异 |
| [review.cn.md](materials/showcase/review.cn.md) | 2,374 | `c94f9195beaf` | 中文历史审查摘要；不是新审查 |
| [review.md](materials/showcase/review.md) | 3,096 | `93f8010f5572` | 英文历史审查摘要；已提供完整内联正文 |
| [verification.json](materials/showcase/verification.json) | 7,782 | `f1579a2ca1d6` | 既有证据摘要、完整哈希及日志摘要哈希 |

### B.3 未附原始来源与最终信任边界

历史审查记录还保留了原始论文文件的以下摘要。它们是已保存的身份信息，不是本次重新下载或比较的结果，也不使缺失的源文件自动成为附件。

| 未附文件 | 保存的 SHA-256 |
|---|---|
| Fang 等 v2 PDF | `d019d71fbb265fc0fc4619d9849855c644811498dd0812c34a2c0e741a04c57a` |
| Fang 等 v2 提取的 TeX | `a104f63c5186abffcf8efde9329e119135d49540afedeb1c0e15d0613e1759f4` |
| Zhang–Zhao PDF | `380cc56b2d9b6b8ab65abc2f5bf2fd4acfe88058ac1212e7a5d80378bd931fc1` |
| 分层排列论文 PDF | `22d4d19be4e7dc4fc5e4bb0abe8c7f6fb9c8a8307d2e9baff7b8045788140460` |

可审读的完整普通论证、保存的 AI 审查结论、有限挑战摘要和后续部分 Lean 记录，是四种不同的证据。前者供专家逐步审读；AI 审查不是外部专家认证；有限挑战不覆盖无限参数域；Lean 的成功记录仅涉及已构造的形式结果及显式前提。展示排版、翻译、文件哈希或本次两种语言的一致性核对，都不能提高证明等级、coverage 或新颖性等级。

本报告对两版的定理及引理编号、全部 27 个编号公式、参数域、边界情形、来源链接、命令、哈希域及关键证据限制进行了编辑一致性核对。两版均完整保留 `SELF_CHECKED`、`NO_ISSUES_FOUND`、历史 `UNKNOWN` 与截至 2026-10-21 的 `POTENTIALLY_NEW`，并保留 usage limit、材料缺失、全局形式化缺口及外部认证缺失。这项双语检查不是新的数学审查。
