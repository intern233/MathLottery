本文给出 Zeng–Fei–Yang《Tracing the Origins and Generalizations of a Class of Moving Point Inequalities》中 Conjecture 5 的完整证明，并推广到中位三角形的边界。原题见 2026 年第 19 卷第 1 期第 51 页；指数为任意正整数，权重为任意正实数。[出版记录](https://ijopcm.zuj.edu.jo/index.php/IJOPCM/article/view/56) · [原文 PDF](https://ijopcm.zuj.edu.jo/index.php/IJOPCM/article/download/56/43)

本证明对应的 Lean 源码位于 [formal/](formal/README.md)。本文的证明正确性、形式陈述与原题的对应关系、文献新颖性是三个分别核查的问题；新颖性仍为 UNKNOWN，没有声称首次解答。独立复核及实际构建结果见 [实验报告](README.md)。

**证明的精确命题。** 在任意实内积空间中取三点 $A,B,C$，令
\[
a=|BC|,\qquad b=|CA|,\qquad c=|AB|,
\qquad a\ge b\ge c>0,\qquad s=\frac{b+c}{2}.
\]
令 $A'=(B+C)/2, B'=(A+C)/2, C'=(A+B)/2$。对任意
\[
P\in\operatorname{conv}\{A',B',C'\},\quad x,y,z>0,\quad n\in\mathbb N,\ n\ge1,
\]
都有
\[
x|PA|^n+y|PB|^n+z|PC|^n
<\max\{x,y\}\,s^n+\max\{y,z\}\,a^n. \tag{1}
\]
这里有限点集的凸包包括边界；它是闭集。原题的非退化平面三角形及中位三角形严格内部的点满足这些条件。

**第一步：由几何证明距离界。** 记三条中线长为
\[
u=|AA'|,\qquad v=|BB'|,\qquad w=|CC'|.
\]
由内积的展开（Apollonius 恒等式），
\[
4u^2=2b^2+2c^2-a^2,\quad
4v^2=2a^2+2c^2-b^2,\quad
4w^2=2a^2+2b^2-c^2. \tag{2}
\]
例如，将 $B-A$ 和 $C-A$ 记作 $X,Y$，则
\(4u^2=\|X+Y\|^2=2\|X\|^2+2\|Y\|^2-\|X-Y\|^2\)，故第一式成立；其余两式同理。

边序给出 $0<s\le a$，并且
\[
4(s^2-u^2)=a^2-(b-c)^2=(a-b+c)(a+b-c)>0,
\]
因为两个因子分别至少为 $c$ 和 $a$。所以 $u<s\le a$。另外，
\[
\begin{aligned}
4(a^2-v^2)&=2a^2+b^2-2c^2\ge 2a^2-b^2\ge a^2>0,\\
4(a^2-w^2)&=2a^2-2b^2+c^2\ge c^2>0,
\end{aligned}
\]
故 $v<a, w<a$。

为控制距离之和，令 $R_b=a+(c-b)/2$、$R_c=a+(b-c)/2$。两者均为正数，而直接使用 (2) 得
\[
\begin{aligned}
4(R_b^2-v^2)&=2(a-b)^2+c(4a-2b-c)>0,\\
4(R_c^2-w^2)&=2(a-c)^2+b(4a-2c-b)>0.
\end{aligned}
\]
这里 $4a-2b-c\ge a>0$、$4a-2c-b\ge a>0$。因此
\[
u+a<a+s,\qquad v+b<a+s,\qquad w+c<a+s. \tag{3}
\]

三个中点处的距离分别为

| 点 | 到 $A$ | 到 $B$ | 到 $C$ | 距离总和 |
|---|---:|---:|---:|---:|
| $A'$ | $u$ | $a/2$ | $a/2$ | $u+a<a+s$ |
| $B'$ | $b/2$ | $v$ | $b/2$ | $v+b<a+s$ |
| $C'$ | $c/2$ | $c/2$ | $w$ | $w+c<a+s$ |

到一个定点的距离是凸函数：若 \(\lambda_i\ge0\)、\(\sum_i\lambda_i=1\)，则
\[
\left|\sum_i\lambda_i Q_i-X\right|
\le\sum_i\lambda_i|Q_i-X|.
\]
距离的和也是凸函数。表中每一项到 $A$ 的距离不超过 $s$，所有距离不超过 $a$，且三处总和都严格小于 $a+s$。任何凸组合的总和仍严格小于 $a+s$：有限个严格小于同一数的值的凸组合也严格小于该数。因此，令 $p=|PA|,q=|PB|,r=|PC|$，得到
\[
0\le p,q,r\le a,\qquad p\le s,\qquad p+q+r<a+s. \tag{4}
\]
此处没有要求 $P$ 的凸组合系数全部为正，故边界也包括在内。

**第二步：对每个正整数证明严格幂和界。** 我们证明如下一般引理：若 $0<s\le a$，$p,q,r\in[0,a]$，且 $p+q+r<a+s$，则对每个整数 $n\ge1$，
\[
p^n+q^n+r^n<a^n+s^n. \tag{5}
\]
若三数均不超过 $s$，则
\[
\begin{aligned}
p^n+q^n+r^n
&\le(p+q+r)s^{n-1}\\
&<(a+s)s^{n-1}\\
&\le a^n+s^n.
\end{aligned}
\]
中间严格性来自 $s^{n-1}>0$，最后一步来自 $s\le a$。这个论证也包括 $n=1$。

否则，选一个大于 $s$ 的数记为 $t$，其余记为 $d,e$。于是 $s<t\le a$，且
\(0\le d+e<a+s-t\)。二项式展开给出
\(d^n+e^n\le(d+e)^n\)，而正整数幂在非负实数上严格递增，因此
\[
t^n+d^n+e^n<t^n+(a+s-t)^n.
\]
函数 $f(t)=t^n+(a+s-t)^n$ 在 $[s,a]$ 上凸，因为两项的底数非负，且非负实数的 $n$ 次幂凸：$n=1$ 时为线性函数，$n\ge2$ 时二阶导数 $n(n-1)t^{n-2}$ 非负。它的两个端点值都为 $a^n+s^n$，所以全区间上 $f(t)\le a^n+s^n$。这就证明了 (5)。

**第三步：引入全部正权重。** 设 $U=\max\{x,y\}>0$、$V=\max\{y,z\}>0$。由 (4)、(5)，
\[
p^n\le s^n,\qquad r^n\le a^n,\qquad
T:=p^n+q^n+r^n<a^n+s^n.
\]
如果 $V\le U$，则 $x\le U,y\le V,z\le V$，从而
\[
\begin{aligned}
xp^n+yq^n+zr^n
&\le VT+(U-V)p^n\\
&<V(a^n+s^n)+(U-V)s^n\\
&=Us^n+Va^n.
\end{aligned}
\]
如果 $U\le V$，则 $x\le U,y\le U,z\le V$，从而
\[
\begin{aligned}
xp^n+yq^n+zr^n
&\le UT+(V-U)r^n\\
&<U(a^n+s^n)+(V-U)a^n\\
&=Us^n+Va^n.
\end{aligned}
\]
严格性分别由 $V>0$ 和 $U>0$ 保证，两种次序穷尽所有权重。故 (1) 成立，原猜想全部得证。整个证明没有借助有限数值检验。

**形式陈述与原题的对应。** `formal/Conjecture5.lean` 中的 `ZengFeiYang.conjecture5_original` 使用：

| 原题对象或条件 | Lean 表达 |
|---|---|
| 欧氏平面 | `EuclideanSpace ℝ (Fin 2)`，其标准欧氏距离 |
| 非退化三角形 | `AffineIndependent ℝ ![A, B, C]` |
| $a,b,c$ | `dist B C`、`dist C A`、`dist A B` |
| $a\ge b\ge c$ | 两个距离的 `≤` 假设 |
| $A',B',C'$ | `midpoint ℝ B C`、`midpoint ℝ A C`、`midpoint ℝ A B` |
| 中位三角形严格内部 | `interior (convexHull ℝ {三中点})` 的成员关系 |
| 所有正权重 | `x y z : ℝ` 及 `0 < x`、`0 < y`、`0 < z` |
| 所有正整数幂 | `n : ℕ` 及 `1 ≤ n` |
| 严格上界 | 结论使用 `<`，并保留两项原定的 `max` |

`conjecture5_closed` 的实际前提只有实内积空间、`A ≠ B`、两个边序关系、三中点凸包的成员关系、正权重及 `n ≥ 1`。原题推论在 Lean 内由仿射无关的单射性证明 `A ≠ B`，由 `interior_subset` 证明凸包成员关系。`medial_distance_bounds` 从 Apollonius 和真实中点距离出发证明 (4)，而非假定 (4)。`medialTriangle_isClosed` 由有限点凸包紧性证明该凸包闭合。因此没有遗漏从几何到代数的桥梁，也没有借用未证明的正重心坐标等价性。自然语言与形式陈述的这份对应说明仍应由独立审查者核对。

证明使用了主控助手给研究会话的未验证路线提示；提示中的几何界、幂和界和权重处理在 Lean 内均逐项证明。该提示并非用户撰写，也不是证明假设或独立审查结论。此文件从求解会话的证明报告提取，仅修正三处数学排版，并补充出处、贡献说明和结果链接；原始候选与三份 Lean 源码未被改写。
