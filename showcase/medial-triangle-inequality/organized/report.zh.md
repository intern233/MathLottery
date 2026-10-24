> 公开展示版本：仅进行私人运行信息脱敏和相对路径整理；原有结论及证据等级不变。正文、附录及历史材料中的哈希和字节数指向原始冻结输入；脱敏、链接整理及来源说明会改变公开副本的字节。核对本目录中的文件时，请使用[出版清单](manifest.json)中 `files[].sha256` 与 `files[].bytes`，不要用正文或附录的原始哈希判断公开副本是否损坏。清单分别保留原始与公开文件的哈希、字节数。

# MathLottery 专家阅读报告

> 本文是对已有研究材料的整理，未经新增独立验证。排版和说明不提升证明等级，也不认证问题的开放状态或新颖性。

来源任务：`reviewed-source`；冻结版本：16；冻结时间：2026-10-24T04:21:32.659285+00:00。

## 原始验证记录

- `candidate-record-006` · `SELF_CHECKED` · scope `UNKNOWN`; verdict `NO_ISSUES_FOUND`, coverage `UNKNOWN`, novelty `UNKNOWN`

[Evidence manifest](manifest.json)

### 材料范围与限制

- This is an editorial reconstruction of visible saved evidence, not hidden reasoning, an independent mathematical verification, or a certification of novelty.
- reviewed-source: only saved answers, named notes, proof/formal files and source receipts are included; arbitrary workspace files, binaries and caches are excluded.
- This historical Verify has no saved solver linkage. The original Solve history is unavailable; matching titles or proofs were not used to guess it.

---

# 中位三角形内加权距离幂和：Zeng–Fei–Yang 猜想 5 专家报告

**摘要与精确结论。** 保存的求解稿给出原猜想的肯定证明：对所有满足边序的非退化欧氏平面三角形、所有中位三角形严格内部点、所有正实数权重及全部正整数指数，所述严格上界成立。同一稿件证明了更强的闭凸包版本，允许中位三角形的边界，并适用于任意实内积空间中满足条件的三点。下文完整展开这份既有证明，而非只列研究日志。历史独立 AI 审查结论为 `NO_ISSUES_FOUND`；三份 Lean 源码的独立重编译、几何到代数的完整桥梁、内核重放及另一次可移植构建均有历史成功记录。这些事实与旧数据库中的 `SELF_CHECKED`、`scope=UNKNOWN` 和 `original_problem_coverage=UNKNOWN` 并存，本文不升级这些字段。新颖性及经确认的当前开放性均保持 `UNKNOWN`，没有外部专家认证。[D1] [H2] [S2]

**材料与编辑范围。** 本报告以 2026-10-24 冻结的 Verify dossier、其清单所列文件，以及用户明确提供、证据日期为 2026-10-21 的 showcase 补充为唯一依据。后者是既有展示稿和历史审计摘要，不是原生清单收集到的新审查记录。文献状态只截至 2026-10-21；本次没有联网查证、数值实验、Lean/Lake 执行或新的独立审稿。编号、解释性过渡和英译属于编辑重述，不是对候选的修补。凡下文提到“审查”“编译”“检索”，均指明其历史来源。原始候选、审查和形式源码保持不变。

**1. 原题、来源与证据状态。** Shanpeng Zeng、Hongliang Fei、Xuezhi Yang 的 *Tracing the Origins and Generalizations of a Class of Moving Point Inequalities*，19(1)，42–52，2026 年 3 月卷期，出版记录标注在线发表日期为 2025-11-30。目标在 §4 “Open Problem”，印刷页 51、PDF 第 10 页，编号为 Conjecture 5，前面的引导文字另称 Conjecture 5.5。历史稿记录了第 43 页的正整数指数约定及第 45 页只涉及一次幂的 Inequality J。作者当时公开提出猜想，不等于已确认它在本次整理日期仍开放。[出版记录][B1] [原文 PDF][B1PDF] [D1]

以下是冻结题目的忠实数学转写，不冒充本轮重新读取 PDF 后的逐字引文。

**定理 1（原猜想的已提交结论）。** 设 \(A,B,C\) 为非退化欧氏平面三角形的顶点，欧氏距离记作 \(|UV|\)，令

\[
a=|BC|,\qquad b=|CA|,\qquad c=|AB|,\qquad a\ge b\ge c>0,
\qquad s=\frac{b+c}{2}.
\]
\[
A'=\frac{B+C}{2},\qquad B'=\frac{A+C}{2},\qquad C'=\frac{A+B}{2},
\qquad M=\operatorname{conv}\{A',B',C'\}.
\]

对每个 \(P\in\operatorname{int}_{\mathbb R^2}M\)、每组 \(x,y,z\in\mathbb R_{>0}\) 和每个 \(n\in\mathbb Z_{\ge1}\)，有

\[
x|PA|^n+y|PB|^n+z|PC|^n
<\max\{x,y\}\left(\frac{b+c}{2}\right)^n+\max\{y,z\}a^n.
\tag{1}
\]

权重与顶点的配对固定为 \((x,A),(y,B),(z,C)\)；第一个最大值确为 \(\max\{x,y\}\)，第二个为 \(\max\{y,z\}\)。交换加法中的 \(b+c\) 与 \(c+b\) 不改变原式；换成 \(\max\{x,z\}\) 则改变命题。这里没有限制为某个幂次或等腰三角形，也没有声称任意实数指数。

**状态台账。** 数学陈述的范围、旧系统字段、实际历史形式化证据及新颖性须分别阅读。

| 项目 | 冻结记录及其解释 |
|---|---|
| 问题发现状态 | `UNKNOWN`；状态检查记录日期为 2026-10-21。不能改写成已认证 `OPEN`。 |
| 候选等级与范围字段 | `level=SELF_CHECKED`，`scope=UNKNOWN`；候选文字明确主张整个原题及闭凸包加强版。 |
| 历史独立审查 | `verdict=NO_ISSUES_FOUND`，`issues=[]`；这是 LLM 审查结论。 |
| 原题覆盖字段 | `original_problem_coverage=UNKNOWN`，`coverage_explanation` 为空；旧版缺少明确覆盖记录，不能补写成新获得的 `FULL` 认证。 |
| 未决数学义务字段 | 候选与审查的 `remaining_obligations=[]`；审查文字未指出实质数学缺口。空数组并不补足缺失的历史资料或专家认证。 |
| 形式化记录 | 有成功历史编译与重放叙述；旧结构中的 `formal_check=null`、`formal_receipt=null`、`checks=[]`，dossier 的 `evidence_receipts=[]`。不能虚构系统签发的形式收据，也不能因此抹去历史 Lean 证据。 |
| 证据评估旧字段 | `evidence_assessment.supported=false`，策略及检查信息为空；这不是一次失败的 Lean 执行结论。 |
| 新颖性与专家认证 | `novelty=UNKNOWN`；没有外部数学专家审稿或外部自然语言—形式陈述等价认证。 |

以上均来自冻结候选、审查及补充摘要。[D1] [S2] 原候选开头“独立 Verify 尚未进行”描述的是提交时阶段；后来的审查已完成。这两个有时间顺序的记录都保留，不回写旧稿。

**2. 记号、加强命题与证明依赖。** 对加强版，环境为任意实内积空间 \(E\)，\(|UV|=\|U-V\|\)。三条边长必须是真实三点距离，而不是任意三个互不相容的正数。假设 \(A\ne B\) 以及上述边序；这正好给出 \(a\ge b\ge c>0\)。中点以向量运算定义。有限凸包表示为

\[
M=\left\{\lambda_1A'+\lambda_2B'+\lambda_3C':
\lambda_i\ge0,\quad\lambda_1+\lambda_2+\lambda_3=1\right\}.
\tag{2}
\]

允许系数为零，因此包含边和顶点；有限点集的凸包是紧集，因而闭合，形式文件还单独证明了这一点。[F3] 这里不要求 \(E\) 完备或有限维；这个有限凸包位于有限维仿射子空间。

**定理 2（已提交的闭凸包加强版）。** 在上述实内积空间、真实距离和 \(a\ge b\ge c>0\) 的假设下，每个 \(P\in M\)、所有 \(x,y,z>0\) 和全部整数 \(n\ge1\) 均满足式 (1)。加强版不要求三点非共线。定理 1 由非退化性推出 \(A\ne B\)，再由严格内部包含于凸包而得到。

为展开证明，记

\[
u=|AA'|,\quad v=|BB'|,\quad w=|CC'|,
\qquad p=|PA|,\quad q=|PB|,\quad r=|PC|.
\]

证明依赖为：引理 1 的中线估计，经引理 2 的凸性得到几何距离界；引理 3 的二项幂和界用于引理 4 的严格三项幂和界；引理 5 按两个最大权重的次序组合这些结果，给出定理 2，继而给出定理 1。此路线使用 Apollonius 恒等式、范数凸性、整数幂凸性及初等权重分解。它最初由主控助手以未验证路线提示提供；求解稿明确归属该帮助，并自行证明每一步。路线提示不是公理，主控也不是独立审查者。[D1] [S1]

**3. 完整普通证明。** 下列引理将原求解稿的三个步骤重新编号，并展开已有推导所需的过渡；不是新增 Solve，也没有替换失败步骤或补入未保存的证明。

**引理 1（中线及中点距离和的严格估计）。** 定理 2 的条件推出 \(0<s\le a\)，并且

\[
u<s,\qquad v<a,\qquad w<a,
\qquad u+a<a+s,\quad v+b<a+s,\quad w+c<a+s.
\tag{3}
\]

证明。由内积展开得到 Apollonius 恒等式：

\[
4u^2=2b^2+2c^2-a^2,\qquad
4v^2=2a^2+2c^2-b^2,\qquad
4w^2=2a^2+2b^2-c^2.
\tag{4}
\]

例如设 \(X=B-A\)、\(Y=C-A\)，则 \(2(A'-A)=X+Y\)，且 \(X-Y=B-C\)，所以

\[
4u^2=\|X+Y\|^2
=2\|X\|^2+2\|Y\|^2-\|X-Y\|^2
=2c^2+2b^2-a^2.
\]

在另外两个顶点作同样展开得到其余两式。边序给出 \(0<s\le a\)，而

\[
4(s^2-u^2)=a^2-(b-c)^2
=(a-b+c)(a+b-c)>0.
\tag{5}
\]

两个因子分别至少为 \(c>0\) 和 \(a>0\)。由于 \(u\ge0\)、\(s>0\)，平方比较给出 \(u<s\)。同理，

\[
\begin{aligned}
4(a^2-v^2)&=2a^2+b^2-2c^2
\ge2a^2-b^2\ge a^2>0,\\
4(a^2-w^2)&=2a^2-2b^2+c^2\ge c^2>0.
\end{aligned}
\tag{6}
\]

所以 \(v<a\)、\(w<a\)。为控制距离和，令

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

式 (7) 是将式 (4) 代入后展开所得；严格性来自 \(4a-2b-c\ge a>0\)、\(4a-2c-b\ge a>0\) 以及 \(b,c>0\)。因此 \(v<R_b\)、\(w<R_c\)，即 \(v+b<a+s\)、\(w+c<a+s\)。最后 \(u<s\) 给出 \(u+a<a+s\)。整个过程没有使用严格三角不等式，因而适用于加强版允许的共线情形。证毕。[D1] [S1] [F2]

**引理 2（闭凸包上的真实几何距离界）。** 对每个 \(P\in M\)，有

\[
0\le p,q,r\le a,\qquad p\le s,\qquad p+q+r<a+s.
\tag{8}
\]

证明。三个真实中点的距离表为：

| 点 | 到 \(A\) 的距离 | 到 \(B\) 的距离 | 到 \(C\) 的距离 | 距离和 |
|---|---:|---:|---:|---:|
| \(A'\) | \(u\) | \(a/2\) | \(a/2\) | \(u+a<a+s\) |
| \(B'\) | \(b/2\) | \(v\) | \(b/2\) | \(v+b<a+s\) |
| \(C'\) | \(c/2\) | \(c/2\) | \(w\) | \(w+c<a+s\) |

表中到 \(A\) 的三项不超过 \(s\)，因为 \(u<s\)、\(b/2\le s\)、\(c/2\le s\)。全部距离不超过 \(a\)，由引理 1 及边序立即得到。

对任意固定点 \(X\)，范数三角不等式和非负齐次性给出

\[
\left|\sum_{i=1}^3\lambda_iQ_i-X\right|
=\left\|\sum_{i=1}^3\lambda_i(Q_i-X)\right\|
\le\sum_{i=1}^3\lambda_i|Q_i-X|,
\qquad \lambda_i\ge0,\quad\sum_{i=1}^3\lambda_i=1.
\tag{9}
\]

取 \((Q_1,Q_2,Q_3)=(A',B',C')\)，即可把逐项上界传到整个 \(M\)。距离和同样是凸函数。为显式保留严格性，令

\[
D=\max\{u+a,v+b,w+c\}<a+s.
\]
\[
p+q+r\le\lambda_1(u+a)+\lambda_2(v+b)+\lambda_3(w+c)
\le D<a+s.
\tag{10}
\]

这一步只需系数非负，并不需要全为正，故边和顶点也满足严格界。距离非负，式 (8) 得证。这里的 \(D\) 只是将原稿“有限个严格上界的凸组合仍严格有界”展开为便于审计的一行，不增加假设。[D1] [S1] [F2]

**引理 3（二项幂和的端点界）。** 设 \(0<s\le a\)、\(t\in[s,a]\)，且 \(n\ge1\) 为整数，则

\[
t^n+(a+s-t)^n\le a^n+s^n.
\tag{11}
\]

证明。函数 \(f(t)=t^n+(a+s-t)^n\) 在 \([s,a]\) 上凸，因为两个底数非负，而非负实数的正整数次幂为凸函数。\(n=1\) 时幂函数为线性；\(n\ge2\) 时这是二阶导数非负的多项式凸性。若 \(s=a\)，区间只有一点，结论是等式。若 \(s<a\)，令 \(\theta=(t-s)/(a-s)\in[0,1]\)，则

\[
t=(1-\theta)s+\theta a,\qquad
f(t)\le(1-\theta)f(s)+\theta f(a)=a^n+s^n.
\]

最后一式使用两个端点函数值相等，证明了式 (11)。这个分支说明只是展开原稿的凸性论证；Lean 中对应 `two_power_le`。[D1] [S1] [F1]

**引理 4（全部正整数指数的严格三项幂和界）。** 若 \(0<s\le a\)、\(p,q,r\in[0,a]\) 且 \(p+q+r<a+s\)，则每个整数 \(n\ge1\) 都满足

\[
p^n+q^n+r^n<a^n+s^n.
\tag{12}
\]

证明分两种情况。如果三个数都不超过 \(s\)，则 \(p^n\le p s^{n-1}\)，另外两项同理。因此

\[
\begin{aligned}
p^n+q^n+r^n
&\le(p+q+r)s^{n-1}\\
&<(a+s)s^{n-1}\\
&=a s^{n-1}+s^n\le a^n+s^n.
\end{aligned}
\tag{13}
\]

严格不等号使用 \(s^{n-1}>0\)；最后使用 \(s\le a\)。当 \(n=1\) 时 \(s^{n-1}=1\)，仍然严格成立。

否则，把一个大于 \(s\) 的数记作 \(t\)，其余记作 \(d,e\)。不需要假设 \(d,e\le s\)。此时

\[
s<t\le a,\qquad 0\le d+e<a+s-t,\qquad a+s-t\ge s>0.
\]
\[
(d+e)^n-d^n-e^n
=\sum_{k=1}^{n-1}\binom{n}{k}d^k e^{n-k}\ge0.
\tag{14}
\]

\(n=1\) 时式 (14) 的和为空，两边均为零。正整数次幂在非负实数上严格递增，结合引理 3 可得

\[
t^n+d^n+e^n
\le t^n+(d+e)^n
<t^n+(a+s-t)^n
\le a^n+s^n.
\tag{15}
\]

这证明了引理，包括 \(t=a\) 的端点；严格性来自总和的严格界，而非要求引理 3 严格。注意引理 4 本身不使用 \(p\le s\)，该单项界留给下一步权重处理。[D1] [S1] [F1]

**引理 5（两个最大权重的组合）。** 在引理 2、4 的条件下，任意 \(x,y,z>0\) 给出式 (1)。证明：令

\[
U=\max\{x,y\}>0,\qquad V=\max\{y,z\}>0,
\qquad T=p^n+q^n+r^n<a^n+s^n.
\]
\[
p^n\le s^n,\qquad r^n\le a^n.
\tag{16}
\]

若 \(V\le U\)，有 \(x\le U\)、\(y,z\le V\)，且 \(U-V\ge0\)。因此

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

严格性由 \(V>0\) 和 \(T<a^n+s^n\) 保证，而单项估计乘以非负的 \(U-V\) 保持方向。

若 \(U\le V\)，则 \(x,y\le U\)、\(z\le V\)，且 \(V-U\ge0\)，从而

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

这次严格性来自 \(U>0\)。两个次序穷尽所有正权重，包括 \(U=V\)；因此得到式 (1)。[D1] [S1] [F1]

**定理 2 与定理 1 的证明完成。** 对真实几何距离应用引理 1、2，再用引理 3、4 得到式 (12)，最后引理 5 给出定理 2。对于定理 1，非退化平面三角形保证 \(A\ne B\)，边序保证 \(c>0\)，严格内部点属于 \(M\)，因此满足定理 2 的每个假设。证明没有借助有限数值检验，也没有把几何距离界作为额外前提。对应形式化正是 `conjecture5_closed` 及其推论 `conjecture5_original`。[F3]

**4. 边界、等号及参数端点。**

| 情形 | 已提交证明如何处理 |
|---|---|
| \(n=1\) | 式 (13) 中零次幂为 1，式 (14) 为空和，严格性仍来自式 (8)。 |
| \(s=a\)，特别是等边三角形 | 引理 3 的区间成为单点；边序下 \(s=a\) 意味着 \(a=b=c\)。引理 4 的“某项大于 \(s\)”分支不会发生。 |
| \(a=b\) 或 \(b=c\) | 引理 1 的正项仍由 \(a,c>0\) 保证；不需要边长互异。 |
| 权重并列，尤其 \(U=V\) | 式 (17)、(18) 中修正项可以为零，但乘在严格总和界上的权重仍为正。 |
| \(P\) 在中位三角形边或顶点 | 式 (2)、(9)、(10) 允许零系数；式 (1) 仍严格。 |
| 共线三点或退化情形 | 原题排除；加强版包含实际距离仍满足 \(a\ge b\ge c>0\) 的共线三点。无须严格三角不等式。历史审查还检查了退化极限，但这不扩展到 \(c=0\)。 |
| 等号 | 在定理 1、2 的允许参数域中，式 (1) 没有等号情形；边界点也不能取等号。没有声称跨越被排除退化情形时存在统一正间隙或最优常数。 |
| 未声称的域 | \(n=0\)、非整数实指数、非正权重、\(c=0\) 及凸包外的点均不属于本报告的结论范围。 |

这些端点说明是对已保存论证和审查范围的解释，不是新的推广。[D1] [H2] [S1]

**5. 形式文件、原题覆盖与数学主张的对应。** 三份冻结 Lean 源码可直接读取；审查构建目录中的对应源码与输入副本的清单哈希相同。补充清单也给出相同的三份源码哈希。版本固定为 Lean 4.35.0、mathlib 提交 `56a005855ea17e0b0958f73ec801ae140b0a1679`；旧求解稿另记录 Lean 提交 `eb6cafb7290e8bd5f2937522d8d804f58f02bafc`。[F1] [F2] [F3] [F4] [F5] [S2]

| 数学内容 | 对应形式声明及实际范围 |
|---|---|
| 引理 1，式 (4)–(7) | `MedialGeometry.lean` 的 `median_estimates` 从中线恒等式及边序推出所需估计；上层 `medial_distance_bounds` 从真实点与 mathlib 的 Apollonius 定理证明这些恒等式。 |
| 引理 2，式 (8) | `convex_le_on_hull`、`convex_lt_on_hull` 和 `medial_distance_bounds`；真实中点距离、逐项上界和严格总和界均在 Lean 内推导。 |
| 引理 3、4 | `MedialAlgebra.lean` 的 `two_power_le`、`three_power_lt_of_large`、`three_power_lt`；最终严格结论要求 `n : ℕ`、`1 ≤ n`，没有实指数定理。 |
| 引理 5 | `weighted_lt` 对已经取幂的非负量作权重组合；最终定理将几何距离的 \(n\) 次幂代入，不是省略取幂步骤。 |
| 定理 2 | `ZengFeiYang.conjecture5_closed`：任意实内积空间、`A ≠ B`、两个边序关系、真实三中点凸包成员关系、三个正实数权重、正整数指数。 |
| 闭性 | `medialTriangle_isClosed` 用有限点凸包紧性证明闭性；“闭凸包”没有隐藏遗漏边界。 |
| 定理 1 | `ZengFeiYang.conjecture5_original` 从上述闭凸包定理推出原题；没有额外假定式 (8)。 |

普通稿用有限凸组合说明引理 2；形式源码则用凸函数的严格/非严格次水平集为凸集及 `convexHull_min` 传递上界。这是同一证明过渡的两种表达。原题主定理直接使用三中点凸包的 `interior`，无需额外假定“严格内部等价于所有重心坐标为正”。早期问题元数据将该等价性列作可行性障碍，最终实现绕开了这项额外表示义务，没有把障碍当作已获证明的新引理。[D1] [F2] [F3]

| 原题条件 | 冻结 Lean 主定理中的表达 | 覆盖说明 |
|---|---|---|
| 欧氏平面及欧氏距离 | `EuclideanSpace ℝ (Fin 2)`、`dist` | 独立范围文件核对二范数及距离平方的坐标公式。 |
| 非退化三角形 | `AffineIndependent ℝ ![A, B, C]` | 独立范围文件核对与三点不共线等价；主证明由其单射性推出 `A ≠ B`。 |
| \(a\ge b\ge c\) | `dist A B ≤ dist C A`，`dist C A ≤ dist B C` | 顶点与边的对应保持不变。 |
| 三个边中点 | `midpoint ℝ B C`、`midpoint ℝ A C`、`midpoint ℝ A B` | 独立范围文件核对中点的向量公式。 |
| 严格内部 | `P ∈ interior (convexHull ℝ {...})` | `interior_subset` 给出闭凸包定理需要的成员关系。 |
| 全部正实权重 | `x y z : ℝ`，`0 < x`、`0 < y`、`0 < z` | 没有归一化或权重互异的附加限制。 |
| 全部正整数 | `n : ℕ`，`1 ≤ n` | 不是有限指数列表。 |
| 严格上界与两个最大值 | `<`，`max x y`，`max y z` | 原题中 \((c+b)/2\) 与闭凸包版中 \((b+c)/2\) 仅用加法交换律连接。 |

独立审查保存的 `AuditScope.lean` 还用不共线假设单独写出预期的原题类型，再调用已提交主定理；它属于审查辅助材料，不属于不可变候选的三个证明模块。[R1] 上表解释文字陈述的完整范围，但数据库中的历史 coverage 仍是 `UNKNOWN`。历史 AI 的语义对应检查和 Lean 内的坐标例子支持这种对应解读，不能替代外部专家对自然语言陈述等价性的认证。

**6. 已记录的验证结果与工具信任边界。** 求解稿报告三模块编译、模块重放及包含依赖的 fresh 重放成功；历史独立审查随后在自己的构建目录从相同源码重新编译，没有复用求解者生成的三个模块对象。以下整理的是保存的执行结果，不是本轮新执行的输出。[D1] [H2] [S2]

| 阶段或检查 | 历史结果 | 证据界限 |
|---|---|---|
| 求解稿三模块编译与两种重放 | 记载退出码均为 0；打印两条主定理类型及公理 | 属于求解稿自述；完整原始日志未随本 bundle 提供。 |
| 历史独立审查的三次源码重编译 | 三次退出码均为 0 | 精确 review 字段及补充摘要均记载；源码在冻结清单内。 |
| 历史独立审查的模块重放 | `leanchecker --verbose MedialAlgebra MedialGeometry Conjecture5`，退出 0 | 使用 Lean 自身的内核。 |
| 历史独立范围检查 | `AuditScope.lean` 编译退出 0 | 源文件保留，日志仅有摘要及哈希。 |
| 首次独立 fresh 重放 | 中断，`exit_code=null` | 不计为通过；中断日志据审查记录另存，但本 bundle 未包含该原始日志。 |
| 恢复后的独立 fresh 重放 | `leanchecker --fresh --verbose Conjecture5`，退出 0 | 包含导入依赖；不能将成功倒填到首次中断尝试。 |
| 原独立审查中的 Lake 范围 | 固定版本配置静态核验；没有另做空缓存联网 Lake 构建 | 原审查的限制保留。 |
| 后续主控的可移植构建 | 先失败，恢复依赖缓存后成功 | 来自显式 showcase 补充；不归到原独立审查。 |

后续可移植构建的具体次序为：`lake update` 退出 0；普通 `lake exe cache get` 退出 0；`lake build` 退出 **1**。补充摘要将原因记为此前中断后留下空的依赖 `Name.ir.sig` 及部分 `.trace` 文件，导致无效头部错误。随后强制重新取得所需官方依赖闭包，退出 0；重试 `lake build` 退出 0；`lake env lean Conjecture5.lean` 退出 0。恢复过程没有修改证明源码。失败构建与首次重放中断是不同事件，都必须保留。[S2] [S3]

历史输出给出的两个主定理传递公理仅为 `propext`、`Classical.choice`、`Quot.sound`。历史源码检查记录未发现 `sorry`、`admit`、`sorryAx`、新增 `axiom`、`unsafe`、`native_decide` 或 `Lean.ofReduceBool`；三个模块都关闭自动隐式变量。源码中的普通 `decide` 仅处理 `Fin 3` 的两个不同下标。[D1] [F3] 这些记录支持“完整所陈述的形式定理通过 Lean 检查”，不是“自然语言陈述等价性或新颖性已被内核证明”。`leanchecker` 仍依赖 Lean 的内核及其实现，不是另一个证明助手；依赖缓存、工具链和公理是形式化证据的信任边界。

**有限计算的角色。** 冻结问题的选择理由记载 12,000 个固定种子浮点实例未见违反，用于可行性筛查。独立审查记载五个符号恒等式的展开差为零，并检查 5,040 个 120 位精度边缘实例，未见违反。这些都不是普遍命题的有限证书；数值结果不涵盖无限多的三角形、权重和指数，也不能保证严格不等式的所有极限情形。普遍证明依赖上面的推导及对应 Lean 证明。实验脚本、具体种子、全部取样域和原始结果文件没有随原生清单提供，因此不能从现有材料复现这些精确样本；本报告不补造命令或输出。[D1]

**7. 既有方法、文献关系与新颖性限制。** 数学方法由经典中线恒等式、凸性和权重比较组成；本报告没有为这些基础方法声称新颖性。原文的 Inequality J 只给出一次幂的中位三角形版本；原猜想的目标是所有正整数指数。2019 年作者文本中的全三角形上界与这里的上界分别为

\[
B_{2019}=\max\{y,z\}a^n+\max\{x,z\}b^n,
\qquad
B_{\mathrm{medial}}=\max\{x,y\}s^n+\max\{y,z\}a^n.
\tag{19}
\]

虽然 \(s\le b\)，两个式子的另一权重因子不同，不能对所有正权重断言 \(B_{\mathrm{medial}}\le B_{2019}\)。早期选择理由用了“较弱”、求解稿用了“较小”的表述；历史独立审查明确澄清二者**没有统一大小关系**。本文保留这项审查意见，不把早期措辞提升为已证明的比较，也不修改原始候选。2019 年结果不能直接当作这里的完整现成证明，范围及权重对应仍须比较。[D1] [H2] [2019 年作者文本转载][B2]

历史检索截至 2026-10-21 未识别出匹配整个原命题的先前公开完整解答。这只说明所记录检索的结果：标题、作者中英文姓名、公式关键词、勘误、arXiv、GitHub 和公共讨论的检索不能排除未检索、未收录或未读到的结果。两项具体的未解决文献证据尤其重要：

- 2025 年费红亮《Guggenheimer 不等式的局部加强形式》只取得官方录用目录和原论文引述，没有全文。原论文参考文献 [8] 被历史审查记录为 2025(08)，43–44，但这是所引书目信息；2025 年 4 月是录用目录日期，不能当作本轮核实的正式发表日期。目录及一次幂引用都不足以排除全文包含进一步结果。[B3] [D1]
- 2026-09-15 的 *A Generalization of an Inequality for Moving Points in a Triangle*，DOI `10.51846/jnhm.v2i2.5387`，历史材料读到了官方摘要；摘要涉及 Erdős 1935 Problem 3746 的幂次与多动点推广。正式 PDF 及其他全文端点直接访问出现 HTTP 403，网页工具获取全文也失败。没有读到全文，不能声称已经排除与本题重合。[官方记录][B4] [当时访问失败的正式 PDF 端点][B4PDF] [D1]

2019 年材料的可见作者转载经网页工具/缓存读取，直接 HTTP 下载也曾 403；没有声称取得该期刊原版全文。原题论文的独立下载则记录 HTTP 200、11 页、222,898 字节，并目视核对印刷页 45、51。原始 PDF 字节未进入本次原生清单，这里依据保存的审查记录报告这些事实。[D1]

因此 `novelty=UNKNOWN` 和发现状态 `UNKNOWN` 均保持不变。完整普通证明、形式化通过、文献优先权和“截至今天仍开放”的认证是不同问题。原作者的公开猜想、历史检索日期和本报告日期不能混同。[S2] [S3]

**8. 缺失材料、未决事项与编辑改动。** 保存的审查未指出定理 1、2 的实质数学缺口，候选和审查的未决数学义务数组均为空。本报告忠实展示这一结果，不新增通过判定。尚未解决的是具体全文缺失与优先权问题、外部专家及外部陈述等价认证缺失，以及历史资料可复核性的限制；这些不能因排版变得更完整而消失。

原生 dossier 的 `visible_research_notes=[]`、`review_source=null`，清单只收录一份 Verify dossier、两个保存回答及形式源文件/配置。清单还明确写明没有保存 solver linkage，因此原 Solve 的完整历史不可用；不能按题名、相同证明或哈希相近猜造会话关联。可利用的是嵌入候选中的求解稿及明确提供的补充，而非一条补造的 Solve 会话时间线。[D1]

原稿提到的完整审查报告、原始 PDF 和图像、来源审计、实验目录、编译与重放日志、封存清单、求解包装脚本及源码归档，大部分不在本 bundle 中。具体包括 `review/report.md`、`review/evidence.json`、`review/edge-checks.json`、`review/sources/`、`review/logs/`，以及求解稿中的 `inputs/run_lean.py`、`notes/formal-source.tar`、`notes/literature/`、`experiments/`、`logs/validation.json`、`logs/artifact-manifest.json` 和 `logs/SHA256SUMS`。这些是历史文件名说明，**不是已附材料链接**。不能用旧回答中的本机路径代替材料，也不能从空白回答恢复中断前的推理。清单的 `omitted=[]` 不表示全部历史文件都存在。

showcase 的 `proof.md` 与原始候选证明不是相同字节：已有展示整理更换了导语及引用，将验证/文献附录内容移到配套说明，并修正了三处数学排版，将误放在显示公式内的美元符号改为相应括号。数学路线和三份 Lean 模块未改变。补充说明称当前证明又从此前可移植展示稿逐字复制；这是展示版本之间的关系，不能据此声称它与原始候选全文同哈希。原候选内容哈希、原始审查报告哈希和展示证明哈希在附录中分开列出。英文中文文档的整理及本报告的双语展开均不构成新的证明审查。[S1] [S2]

本报告没有提出或实施证明修补。若以后发现实质漏洞，任何可能修补都应另列为待新 Solve/Verify 的提案，不能悄悄放入本次组织报告。

**附录 A：保存尝试的简明时间线。** 时间均为 UTC；没有保存的时刻明确留空，不据叙述猜测。

| 时间或顺序 | 保存内容及结论 |
|---|---|
| 2026-10-21 04:50:45，问题状态记录 | 发现状态为 `UNKNOWN`；可行性排名与 12,000 个浮点样本仅作探索依据。早期 `lean_feasibility=unknown` 和“尚未编译”的文字保留为当时记录，不否定后来的形式化证据。 |
| 求解稿阶段，独立时间戳及会话关联缺失 | 提交完整肯定证明和闭凸包加强版，记载编译及两种重放成功；独立 Verify 当时尚待进行，候选为 `SELF_CHECKED`。提及早期失败探索保存在实验和编号日志中，但这些未附，不能列出未知的失败次数、具体步骤或退出码。 |
| 2026-10-21 05:04:24 至 10:09:59，Verify 容器创建/最后更新 | 这是已保存审查流程的外层时间范围，不是每项命令的执行时刻。 |
| 历史独立审查，第一次保存尝试 | 状态 `INTERRUPTED`，保存回答为 0 字节；无最终结论可从此回答提取。首次 fresh 重放中断另见审查文字，退出码为空，不计成功。[H1] |
| 历史独立审查，恢复后的保存尝试 | 状态 `COMPLETED`；回答及 review 字段记录 `NO_ISSUES_FOUND`、新颖性 `UNKNOWN`，独立源码编译、模块重放、范围检查和恢复后的 fresh 重放成功。精确单项时刻未给出。[H2] [D1] |
| 后续可移植构建，单项时间未提供 | 主控在另一源码目录构建；缓存损坏造成一次退出 1，强制恢复后退出 0。仅见于显式补充，不能倒归于原独立审查。[S2] |
| 已有展示整理，补充证据日期 2026-10-21 | 三处排版及文档/附录整理；三份 Lean 模块不变。showcase 导出没有新 Lean 构建。[S2] |
| 2026-10-24 04:21:32，材料冻结 | 原生清单的截取时间；显式补充随用户说明提供。它不是一次新的验证或文献状态检查。 |
| 本次 Organize | 阅读冻结材料，重述数学，核对双语公式、范围、引文及证据状态；没有执行 Solve、Verify 或新的 Lean/Lake 检查。 |

**附录 B：可复现步骤与参考文献。** 下列命令供读者在取得所附源码和官方工具链后另行复现；本次 Organize 没有执行它们。先核对附录 C 的源码哈希及版本固定文件。以下主流程来自已提供的形式化说明；在报告发布包根目录执行第一行，之后均在该形式项目目录中运行。[S7] [S8]

```sh
cd materials/showcase/formal
lake update
lake exe cache get
lake build
lake env lean Conjecture5.lean
```

版本固定文件要求 `leanprover/lean4:v4.35.0` 及上述 mathlib 提交。网络用于取得工具链和依赖；源码包不含大体积构建产品。最后一条命令打印主定理类型及传递公理，历史结果只列出 `propext`、`Classical.choice`、`Quot.sound`。成功构建后，可按已提供说明运行：

```sh
lake env leanchecker --verbose MedialAlgebra MedialGeometry Conjecture5
lake env leanchecker --fresh --verbose Conjecture5
```

该版本的工具须明确给出模块名，补充说明指出它没有 `--help` 选项。`--fresh` 还重放导入依赖，可能需要数分钟；它仍使用 Lean 内核。历史独立审查在已配置依赖搜索路径的环境中记录了以下原命令：

```sh
lean -R . -o MedialAlgebra.olean MedialAlgebra.lean
lean -R . -o MedialGeometry.olean MedialGeometry.lean
lean -R . -o Conjecture5.olean Conjecture5.lean
lean -R . AuditScope.lean
```

`AuditScope.lean` 需从独立审查辅助材料 [R1] 取得，不在 showcase 的三个候选证明模块内。旧求解包装脚本及完整环境没有随包提供；上面的 Lake 流程是已提供的可移植入口，不伪装成旧环境的逐字重建。

为保留失败后的真实恢复过程，补充摘要记录的强制取缓存命令如下；这是一条历史恢复记录，不是成功构建必须额外通过的新检查。[S2]

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

既有普通证明可直接按引理 1–5 审读，毋须数值实验；精确重现 12,000 或 5,040 个样本所需脚本未附，因此不提供虚构的实验复现命令。新执行的结果应单独记录，不回填历史时间线。

**参考文献与来源状态（截至 2026-10-21）。**

| 引用 | 书目信息及本报告中的用途 |
|---|---|
| [B1]、[B1PDF] | Shanpeng Zeng, Hongliang Fei, Xuezhi Yang, *Tracing the Origins and Generalizations of a Class of Moving Point Inequalities*, 19(1), 42–52，2026 年 3 月卷期；在线日期 2025-11-30。原题 §4、p.51，定义 pp.43–45。原论文是猜想与一次幂先前结果的来源；历史记录称已读全文，本轮未重新下载。 |
| [B2] | 费红亮、曾善鹏、杨学枝，《Guggenheimer 不等式的高次加权推广》，《数学通报》58(5)，58–59，2019；转载日期 2019-07-09。历史可见作者文本给出不同权重的全三角形上界，不是本题完整解答的认证。 |
| [B3] | 《数学通讯》下半月刊 2025 年 4 月录用目录，列费红亮《Guggenheimer 不等式的局部加强形式》。只读目录，全文缺失；2025(08)，43–44 为原论文参考文献所引信息。 |
| [B4]、[B4PDF] | Shanpeng Zeng, Jing Liu, Xuezhi Yang, *A Generalization of an Inequality for Moving Points in a Triangle*, 2026-09-15，DOI `10.51846/jnhm.v2i2.5387`。历史只读取正式摘要；全文获取失败，内容重合未排除。 |
| [B5] | mathlib 文档 `Mathlib.Analysis.Normed.Module.Convex`：距离函数凸性等基础工具的文档来源，不是猜想 5 的先前证明。 |
| [B6] | mathlib 文档 `Mathlib.Analysis.Convex.Mul`：非负凸函数自然数次幂的工具。文档 URL 是历史引用，复现版本以源码固定提交为准。 |

**附录 C：材料索引、哈希域与缺失项。** 下列原生材料均用冻结清单的实际相对路径链接。正文标签按证据角色命名；链接目标仅用于定位原始材料。相同内容的输入副本与审查构建副本分列链接，并未当作两次新的数学发现。

| 引用 | 原生冻结材料 | 字节数 |
|---|---|---:|
| [D1] | 冻结 dossier：原题、精确候选证明、审查字段及两次保存尝试 | 32022 |
| [H1] | 历史中断审查回答；空文件 | 0 |
| [H2] | 历史完成审查回答；其中旧的本机路径不作为本报告的材料链接 | 2150 |
| [F1] | 候选输入：幂和及权重证明 | 4564 |
| [R2] | 审查构建副本：幂和及权重证明 | 4564 |
| [F2] | 候选输入：真实几何距离界 | 6895 |
| [R3] | 审查构建副本：真实几何距离界 | 6895 |
| [F3] | 候选输入：闭凸包主定理及原题推论 | 3376 |
| [R4] | 审查构建副本：闭凸包主定理及原题推论 | 3376 |
| [F4] | 候选输入：项目与 mathlib 固定提交 | 320 |
| [R5] | 审查构建副本：项目与 mathlib 固定提交 | 320 |
| [F5] | 候选输入：Lean 版本固定 | 25 |
| [R6] | 审查构建副本：Lean 版本固定 | 25 |
| [R1] | 独立范围核查辅助源码；不是候选模块 | 2040 |

**显式提供的 showcase 补充。** 以下 14 个文件来自用户冻结的补充清单，**不是**原生 `organization-context/manifest.json` 的收集条目。发布步骤将同一份展示源文件附入 `materials/showcase/`，链接按该约定书写。本轮直接得到的内联文本有总览英文版、审查摘要英文版、形式化说明英文版、普通证明及 `verification.json` 的节略版；其他补充项按所提供的文件清单标识，未冒称逐份读到未内联的完整内容。三份 Lean 模块及两个版本配置另有上述原生副本可读。

`verification.json` 内联版明确省去冗余文件哈希索引；其内联文本与清单所指 8,058 字节完整文件不是相同哈希输入，不能误判为证据矛盾，也不能把内联节略版冒充完整附件。

| 引用 | 补充文件及角色 | 声明字节数 |
|---|---|---:|
| [S1] | `proof.md`：既有普通证明展示稿；中文原文 | 6573 |
| [S2] | `verification.json`：历史验证摘要；完整文件的冗余哈希索引未在内联版重复 | 8058 |
| [S3] | `review.md`：独立审查及后续构建摘要，英文 | 2460 |
| [S4] | `review.cn.md`：审查摘要，中文 | 1910 |
| [S5] | `README.md`：案例总览，英文 | 2253 |
| [S6] | `README.cn.md`：案例总览，中文 | 1910 |
| [S7] | `formal/README.md`：形式化说明及复现命令，英文 | 2679 |
| [S8] | `formal/README.cn.md`：形式化说明及复现命令，中文 | 2253 |
| [S9] | `formal/Conjecture5.lean`：原样保留的主定理源码 | 3376 |
| [S10] | `formal/MedialAlgebra.lean`：原样保留的代数源码 | 4564 |
| [S11] | `formal/MedialGeometry.lean`：原样保留的几何源码 | 6895 |
| [S12] | `formal/lake-manifest.json`：可移植项目的依赖清单 | 3176 |
| [S13] | `formal/lakefile.toml`：项目配置及 mathlib 固定提交 | 320 |
| [S14] | `formal/lean-toolchain`：Lean 版本固定文件 | 25 |

**哈希的对象必须区分。** 下表保留源记录中的 SHA-256。原始证据哈希用于定位原对象；后来展示稿的哈希仅定位展示字节。形式收据若含 `problem_sha256`，其域是 UTF-8 的 `Problem.statement`；组织清单的同名字段则是包含元数据和旧字段归一化的完整规范 Problem 记录的 `discovery.problem_fingerprint`。二者输入不同，不能跨域比较。本例旧审查实际没有 `formal_receipt`，这里列出陈述文本哈希也不补造收据。哈希相符只识别字节或规范记录，不认证数学正确性或自然语言对应。

| 对象与域 | SHA-256 |
|---|---|
| 原始 Problem.statement 文本域 | `d5fb1e963dbeea8fba358cc4876e8f6714073af0f24b2c8df76e0ee941d9d59b` |
| 组织清单的完整 Problem 记录指纹域 | `9bafa78c693f12e1337d3be7b391320fccfb9770326966c177a7415750549ddd` |
| 原始候选内容哈希；不是展示 proof.md 的字节哈希 | `8a1a465483ee0d4b4417caa826e81a510a3060418209cb7305f31bdced5d1267` |
| 原始完整审查报告哈希；全文未附，不是保存回答的哈希 | `6c1ad072da86a2538c8cd008400030150ac4c92d9bdbd3aede021e3b1fcbca9b` |
| 冻结 dossier 文件字节 [D1] | `24a3b3d93149c23f32a7c30ce945f0a14f130e6cad2d2aa51667acb69cd0edbf` |
| 原始下载 PDF 哈希；PDF 未附 | `0d96143c1a8b348cbebcdc760f1547e7eaf85ab04448796bcb9324dfe531fd3b` |
| 后来的展示普通证明 [S1] | `fdd130c5ce90d2497196c9c03e1c42841b4422594e8852820fad25092b671833` |
| 后来的完整展示验证摘要 [S2]；不是内联节略版 | `20285e38b8c9f430ecdf0f96f8de3bb4cc527a68299280b24f0f10aaa2662ee5` |

三份证明模块的原始输入、副本及展示源码具有共同的已记录哈希：

| 文件 | 材料 | SHA-256 |
|---|---|---|
| `MedialAlgebra.lean` | [F1], [R2], [S10] | `676684cccd71e6c2a6294bc9f702137426e02fd68f6a8020d632a4dba9f013b1` |
| `MedialGeometry.lean` | [F2], [R3], [S11] | `e6879f933d7753421312220f7ad821e968d4a333aadf2139db0344460628bc94` |
| `Conjecture5.lean` | [F3], [R4], [S9] | `a3bfe87f49abf11394fc1b76c51c54b705c5c4f380273d0018955bbe20d6d5d9` |

历史独立检查日志的已记录哈希如下。原始日志未附；哈希是可供以后匹配原日志的标识，不是本轮执行收据。

| 历史检查（均记录退出 0） | 日志 SHA-256 |
|---|---|
| 代数模块编译 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| 几何模块编译 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| 主模块编译 | `8180a32f21764c0f771085a34f9d6baf4311b9fac2bf42b2cc7f84ec33f8ef74` |
| 三模块重放 | `8b8ae13cfba362649c71276db63bb616b5e1b939480b3066bda681cafca679e8` |
| 独立范围检查 | `44c78b9a16092e0d5bacf72aa66c9fa857fcd9f315a63df23c6c6e275b930f11` |
| 恢复后的 fresh 重放 | `77ff926b9f6cb12cf5f78e7cf26af53b2a11495e6a1d789e0a8646386a72d311` |

前两项空日志的共同哈希对应空字节串；历史记录把它们与退出 0 配对，不能只凭“没有日志文字”判断成功。首次中断重放及失败 Lake 构建不在上表的成功项内；其失败/中断状态已在第 6 节和附录 A 保留。全部补充文件的声明大小与哈希来自用户提供的冻结清单，完整展示摘要另含文件索引；本文没有为未取得的原始日志补造附件。

**双语一致性说明。** 本报告的中文与英文分别包含完整原题、定理 1–2、引理 1–5、式 (1)–(19)、证明、边界说明、状态台账、失败与缺失项、文献限制、时间线、复现命令及材料索引。两版按同一冻结来源生成；编号、全部数学公式、参数域、材料及来源链接、关键哈希、命令与证据状态已作编辑一致性核对。这种核对不新增数学审查、形式运行、原题覆盖认证或新颖性结论。

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
