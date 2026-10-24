# An equivariant marked-occurrence proof of corrected Conjecture 1

## Claim and provenance

For every integer $n\geq0$, let $I_n$ be the permutations of $[n]$ whose
square is the identity. Let

\[
R=\{(0,0),(1,1),(1,2),(2,1)\},\qquad
R'=\{(2,2),(1,1),(1,0),(0,1)\}.
\]

In the printed order of corrected Conjecture 1 of Fang–Fu–Kitaev–Li–Su–Sun,
arXiv:2606.14367v2 (11 October 2026), the four patterns are

\[
p_1=(12,R),\quad p_2=(12,R'),\quad
p_3=(21,R'),\quad p_4=(21,R).
\]

We prove, for every $n,k\geq0$ and every $s,t\in\{1,2,3,4\}$,

\[
\#\{\pi\in I_n:\operatorname{occ}_{p_s}(\pi)=k\}
=\#\{\pi\in I_n:\operatorname{occ}_{p_t}(\pi)=k\}.                 \tag{1}
\]

The occurrence convention is exactly the strict empty-rectangle convention in
the question. The proof below is an ordinary mathematical proof submitted as a
candidate. The independent AI review and its limits are summarized in
[review.md](review.md); this is not a complete Lean certificate.

The supplied controller drafts proposed the star/path rotation, its inversion
equivariance, and the two-variable refinement used here. They were unverified
assistance, not premises. All needed structural assertions and both directions
of the construction are proved below. The use of marked occurrences and a
path/star rotation is indebted to Zhang–Zhao, *The last distribution-equivalence
class of mesh patterns of length 2*, arXiv:2607.04111, Sections 1–2. Their
whole-permutation result is already known. The additional argument here concerns
inversion, individual edges, and the restriction to involutions. No finite probe
is used as a premise, and no claim of global priority is made.

## 1. The literal occurrence predicate

Write $A=p_1$ and $B=p_4$. For a permutation $\pi$ and indices $i<j$,
put $l=\min(\pi(i),\pi(j))$, $h=\max(\pi(i),\pi(j))$. The shading $R$
is equivalent to the following three conditions:

\[
\begin{array}{ll}
\mathrm L:& t<i\ \Longrightarrow\ \pi(t)>l,\\
\mathrm M:& i<t<j\ \Longrightarrow\ \pi(t)<l,\\
\mathrm Q:& t>j\ \Longrightarrow\ \pi(t)\notin(l,h).
\end{array}                                                        \tag{2}
\]

Indeed cell $(0,0)$ excludes precisely $t<i,\ \pi(t)<l$. Cells $(1,1)$
and $(1,2)$ together exclude precisely $i<t<j,\ \pi(t)>l$: their only
potential missing boundary is the value $h$, which is already used at an
endpoint. Cell $(2,1)$ excludes precisely $t>j,\ l<\pi(t)<h$.
Injectivity also excludes the value $l$ at every nonendpoint. The outer
boundaries $0,n+1$ add no exceptions, since all entries and indices lie in
$[n]$. Thus (2) is equivalent in both directions to all four strict empty
rectangles. An $A$-occurrence additionally has $\pi(i)<\pi(j)$, and a
$B$-occurrence has $\pi(i)>\pi(j)$.

We represent an occurrence by its ordered pair of indices, called an edge.
A marked object is a pair $(\pi,M)$, where $M$ is any subset of the
occurrence set of the specified pattern. No maximality condition is imposed.

## 2. Shapes of marked components and their nesting

Consider the directed graph with edge set $M$, oriented from the smaller
index to the larger index, discarding isolated vertices.

For $A$, a vertex has at most one outgoing edge. If both $(i,j)$ and
$(i,k)$ were edges with $j<k$, condition M for $(i,k)$ would give
$\pi(j)<\pi(i)$, contrary to the ascent at $(i,j)$. Every starting vertex
is a left-to-right minimum by L. A terminal vertex of an edge cannot be a
starting vertex: it has an earlier entry smaller than itself, whereas L for an
outgoing $A$-edge would require every earlier entry to be larger. Thus each
nontrivial connected component is a star with a single terminal root. To see
that there cannot be two roots in a connected component, each non-root has
only one edge, and roots connect only to such degree-one vertices. Write a
component as

\[
x_0<x_1<\cdots<x_m,\qquad m\geq1,
\]

with edges $(x_{h-1},x_m)$, $1\leq h\leq m$. Its values have the form

\[
\bigl(\pi(x_0),\ldots,\pi(x_m)\bigr)=(v_1,\ldots,v_m,v_0),
\qquad v_0>v_1>\cdots>v_m.                                    \tag{3}
\]

The decreasing order of the leaves follows from L at each later leaf, and
the root exceeds every leaf because each marked edge is an ascent.

For $B$, a vertex has at most one incoming edge. If $(i,j)$ and $(k,j)$
were edges with $i<k<j$, M for the first would give $\pi(k)<\pi(j)$,
contrary to the descent of the second. It also has at most one outgoing edge.
If $(i,j)$ and $(i,k)$ were edges with $j<k$, M for the second and its
descent would give $\pi(j)<\pi(k)<\pi(i)$, forbidden by Q for the first.
Since each edge increases the index, there are no directed cycles. In a finite
component, repeatedly following predecessors must terminate, and following
successors from that initial vertex then visits the whole component: any
extra attached edge would violate one of the degree bounds. Therefore every
component is a path

\[
x_0<x_1<\cdots<x_m,\qquad
M_C=\{(x_{h-1},x_h):1\leq h\leq m\},
\]

with values

\[
\bigl(\pi(x_0),\ldots,\pi(x_m)\bigr)=(v_0,v_1,\ldots,v_m),
\qquad v_0>v_1>\cdots>v_m.                                    \tag{4}
\]

In either graph, edges in different components cannot cross. Suppose edges
$(i,j),(k,l)$ had $i<k<j<l$. In the $A$ case, M for the first gives
$\pi(k)<\pi(i)<\pi(j)$, while M for the second gives
$\pi(j)<\pi(k)$, a contradiction. In the $B$ case, M for the first,
descent of the second, and M for the second give respectively
$\pi(k)<\pi(j)$, $\pi(l)<\pi(k)$, and $\pi(j)<\pi(l)$, again a
contradiction. Reversing the names covers the other crossing order.

Consequently, two distinct components have disjoint closed position intervals,
or one is contained in a single open gap between consecutive vertices of the
other. Here is a proof of this stronger consequence, which will be needed
below. Write their vertices as $c_0<\cdots<c_m$ and $d_0<\cdots<d_r$,
and assume $c_0<d_0<c_m$, the only case remaining after interchanging names
and excluding disjoint intervals. Endpoints of distinct components are never
equal.

For stars, the edges $(c_0,c_m)$, $(d_0,d_r)$ show that $d_r<c_m$,
since otherwise they cross. If a vertex $c_t$ lay in $(d_0,d_r)$, it
would be a leaf, and $(d_0,d_r)$, $(c_t,c_m)$ would cross. Thus no
$c_t$ lies in the closed interval $[d_0,d_r]$, so that interval is wholly
in one open gap of the $c$'s. For paths, choose $t$ with
$c_t<d_0<c_{t+1}$. If $d_r>c_{t+1}$, consecutive $d$-vertices must
straddle $c_{t+1}$; write $d_a<c_{t+1}<d_{a+1}$. Then
$c_t<d_a<c_{t+1}<d_{a+1}$ makes two path edges cross. Hence
$d_r<c_{t+1}$, proving the asserted gap containment for paths too.

## 3. A common characterization of a star and a path

Fix positions $x_0<\cdots<x_m$ and distinct values $v_0>\cdots>v_m$,
where $m\geq1$. Consider either the star arrangement (3) or the path
arrangement (4). The designated edges are all occurrences of the appropriate
pattern if and only if every entry at a position outside
$\{x_0,\ldots,x_m\}$ satisfies the following conditions:

\[
\begin{array}{ll}
\mathrm{O}_0:& t<x_0\ \Longrightarrow\ \pi(t)>v_1;\\
\mathrm{O}_k:& x_{k-1}<t<x_k\ \Longrightarrow\
                     v_{k+1}<\pi(t)<v_k\quad(1\leq k<m);\\
\mathrm{O}_m:& x_{m-1}<t<x_m\ \Longrightarrow\ \pi(t)<v_m;\\
\mathrm{O}_{m+1}:& t>x_m\ \Longrightarrow\ \pi(t)\notin(v_m,v_0).
\end{array}                                                        \tag{5}
\]

For necessity in the star arrangement, L for the first edge gives
$\mathrm O_0$. In gap $k<m$, M for leaf $x_{k-1}$ gives the upper
bound $v_k$, and L for leaf $x_k$ gives the lower bound $v_{k+1}$.
M for the last leaf gives $\mathrm O_m$; Q for that leaf gives
$\mathrm O_{m+1}$.

For necessity in the path arrangement, L for the first edge again gives
$\mathrm O_0$. In gap $k<m$, M for the $k$-th edge and L for the
$(k+1)$-st give its two bounds. M for the last edge gives
$\mathrm O_m$. After $x_m$, Q for every path edge forbids all intervals
$(v_h,v_{h-1})$, $1\leq h\leq m$. Their union is $(v_m,v_0)$
except for $v_1,\ldots,v_{m-1}$. Those values are already occupied at
designated vertices, and injectivity excludes them at the outside entry.
This proves $\mathrm O_{m+1}$.

For sufficiency in the star arrangement, consider the edge
$(x_{h-1},x_m)$, whose low and high values are $v_h,v_0$. Every entry
to its left is either before $x_0$, at an earlier designated leaf, or in
a gap $k<h$. The respective lower bounds are $>v_1\geq v_h$, a leaf
value strictly greater than $v_h$, and $>v_{k+1}\geq v_h$. Every
entry strictly between its endpoints is a later leaf with smaller value,
or is in a gap $k\geq h$, where its value is $<v_k\leq v_h$
(including the final gap). Entries after the root avoid $(v_m,v_0)$
and therefore avoid $(v_h,v_0)$. Thus L, M, Q all hold.

For sufficiency in the path arrangement, consider $(x_{h-1},x_h)$, whose
low and high values are $v_h,v_{h-1}$. Before its first endpoint,
$\mathrm O_0$, earlier vertex values, and earlier gap bounds give values
strictly greater than $v_h$, by the same inequalities just used. Its open
interior is gap $h$, whose values are $<v_h$. To its right, later
designated vertices have values $<v_h$, as do later gaps; entries after
$x_m$ avoid $(v_m,v_0)\supseteq(v_h,v_{h-1})$. Hence Q also holds.
This proves the characterization in both directions, including $m=1$,
when there are no gaps of the intermediate kind.

## 4. Simultaneous rotations and their inverse

For a marked $A$-object, replace the values on every star (3) by the path
arrangement (4), and replace its marks by consecutive path edges. Explicitly,

\[
(v_1,\ldots,v_m,v_0)\longmapsto(v_0,v_1,\ldots,v_m),\qquad
e_h=(x_{h-1},x_m)\longmapsto f_h=(x_{h-1},x_h).                 \tag{6}
\]

Distinct components have disjoint vertices, and each replacement only permutes
the values on its vertices, so this defines a permutation $\sigma$ and a
set $N$ of distinct marked edges. The correspondence $e_h\mapsto f_h$
is a bijection $M\longrightarrow N$.

Conversely, for a marked $B$-object, on each descending path replace
$(v_0,v_1,\ldots,v_m)$ by $(v_1,\ldots,v_m,v_0)$, and replace
$(x_{h-1},x_h)$ by $(x_{h-1},x_m)$. Denote the first operation by
$\Phi$ and the second by $\Psi$. We now prove that both are well-defined
on all marked objects, including arbitrary nested collections of components.

Fix any component $C$. Its own rotation preserves the ordered positions,
the decreasing list of its values, and hence the bounds in (5). It suffices
to show that every other component's rotation keeps each of its entries in
the allowed region of (5) relative to $C$. The position intervals have the
nesting property proved in Section 2.

If the intervals of $C,D$ are disjoint, all vertices of $D$ are on the
same exterior side of $C$. Beforehand all their values satisfy that side's
condition of (5); permuting those values leaves the condition true at each
vertex. This works even when the allowed values form two disjoint intervals.

If $D$ is in gap $k<m$ of $C$, all its values lie in
$(v_{k+1},v_k)$ by (5), so its rotation keeps them in that interval.
If it is in the final gap, all its values are $<v_m$, also preserved.
Thus inner rotations preserve all outside conditions of the outer component.

It remains to check the effect of an outer rotation on an inner component;
this cannot be inferred just from disjoint vertex sets. Suppose $D$ lies
in gap $k$ of $C$, and write $a=\min\{\pi(d):d\in D\}$,
$b=\max\{\pi(d):d\in D\}$. Rotations of $D$ do not change $a,b$.
For $k<m$, (5) gives

\[
v_{k+1}<a\leq b<v_k.                                         \tag{7}
\]

For each vertex $x_t$ of $C$, its two possible values, in the star and
path arrangements respectively, are

\[
\begin{cases}
(v_{t+1},v_t),&0\leq t<m,\\
(v_0,v_m),&t=m.
\end{cases}                                                   \tag{8}
\]

If $t\leq k-1$, both values in (8) are at least $v_k>b$; these vertices
are before $D$. The vertex $x_k$, after $D$, has possible values
$v_{k+1}<a$ and $v_k>b$. Vertices with $k<t<m$, also after $D$,
have both values at most $v_{k+1}<a$. The final vertex $x_m$, after
$D$, has possibilities $v_0>b$ and $v_m<a$. Thus, before $D$,
every $C$-value is greater than every $D$-value; after $D$, every
$C$-value is outside the whole interval $[a,b]$. Such values satisfy
the two exterior conditions for $D$ in either arrangement. No $C$-vertex
is inside $D$'s interval, so its interior conditions are untouched.

For the final gap $k=m$, every value of $D$ is $<v_m$. Each vertex
$x_t$ with $t<m$ is before $D$, and both values in (8) are
$\geq v_m>b$. The only $C$-vertex after $D$ is $x_m$, whose two
possible values $v_0,v_m$ are both $>b$. Again all exterior conditions
for $D$ hold in both arrangements.

These checks use only positions, value sets, and the two possible values of
each vertex. They are therefore valid simultaneously, not merely for a
chosen order of rotations. An untouched point keeps its original allowed
value, and a point in another component satisfies the appropriate case just
proved. Conditions (5) survive for every component. Section 3 now shows that
all new marks of $\Phi$ are $B$-occurrences and all new marks of $\Psi$
are $A$-occurrences. This proves well-definedness in both directions.

The marked graph produced by (6) has exactly the same component vertex sets:
each star was replaced by a connected path on those vertices, and no edge
between components was introduced. The analogous assertion holds backwards.
Applying $\Psi$ to $\Phi(\pi,M)$ therefore finds precisely those paths,
rotates each value list back, and restores precisely the original star marks.
Thus $\Psi\Phi=\mathrm{id}$. Starting with a $B$-object gives
$\Phi\Psi=\mathrm{id}$ by the same explicit componentwise computation.
For the empty marked set both maps leave the permutation unchanged. We have
proved a bijection of all marked objects, with its explicit edge bijection.

## 5. Inversion and individual edges

For a permutation $\pi$, transposition of its plot gives $\pi^{-1}$.
For an edge $e=(i,j)$, write

\[
T_\pi(e)=\bigl(\min(\pi(i),\pi(j)),\max(\pi(i),\pi(j))\bigr).
                                                                    \tag{9}
\]

Both underlying patterns $12,21$ are their own inverses, and $R$ is
invariant under $(a,b)\mapsto(b,a)$. A forbidden point in one rectangle
transposes to a forbidden point in the transposed rectangle, and conversely.
Hence (9) bijects the $A$-occurrences of $\pi$ with those of
$\pi^{-1}$, and likewise for $B$. Its inverse is $T_{\pi^{-1}}$.
This also follows directly by sorting the two endpoint positions and values:
transposition interchanges those sorted boundary lists, so each cell's two
strict interval inequalities are exchanged. Put
$(\pi,M)^T=(\pi^{-1},T_\pi(M))$.

We prove the stronger assertion that $\Phi$ commutes with transposition
including its edge correspondence. Take an $A$-star (3). Its transpose is
the $A$-star with increasing positions

\[
v_m<v_{m-1}<\cdots<v_1<v_0
\]

and values

\[
x_{m-1},x_{m-2},\ldots,x_0,x_m.
\]

Indeed each original leaf/root edge becomes $(v_h,v_0)$, and the original
root $x_m$ is the largest of these values. Rotating this transposed star
gives values

\[
x_m,x_{m-1},\ldots,x_0
\]

at positions $v_m,v_{m-1},\ldots,v_0$, respectively. The original
rotation has $\sigma(x_t)=v_t$ for every $0\leq t\leq m$, so this
is exactly the inverse of the rotated component. Under inversion the sets of
vertices of distinct components become disjoint sets of values; thus these
are precisely all transposed components. Any point outside their vertex sets
is unchanged in the original permutation and also unchanged after inversion.
We conclude at the permutation level that the output is $\sigma^{-1}$.

For individual edges, the original star edge
$e_h=(x_{h-1},x_m)$ transposes to $(v_h,v_0)$. Its index within the
increasingly ordered transposed star is $m-h+1$, so its image under the
transposed rotation is $(v_h,v_{h-1})$. On the other hand its original
image is $f_h=(x_{h-1},x_h)$, whose values in $\sigma$ are
$(v_{h-1},v_h)$. Hence its transpose is also $(v_h,v_{h-1})$.
Writing $\theta_{\pi,M}:M\longrightarrow N$ for (6), we have proved

\[
\Phi((\pi,M)^T)=\Phi(\pi,M)^T,\qquad
\theta_{\pi^{-1},T_\pi M}(T_\pi e)
       =T_\sigma(\theta_{\pi,M}(e)).                         \tag{10}
\]

This is an identity for every individual marked edge, including edges in
self-transposed components. No orientation or middle-edge exception is needed.
Since $\Psi=\Phi^{-1}$, the object-level identity also holds for $\Psi$:
apply $\Phi$ to the two possible inverse images and use its injectivity.
The inverse edge bijections intertwine transposition as well, by inverting
the second identity in (10).

In particular, fixed marked objects under $T$ are carried bijectively to
fixed marked objects. Such objects are exactly those with
$\pi\in I_n$ and $T_\pi(M)=M$. On any such $M$, transposition is an
involution on its edges. By (10), $\theta_{\pi,M}$ is an equivariant
bijection with the marked edges of the image. It carries every fixed edge to
a fixed edge and every two-element orbit to a two-element orbit. Conversely,
if an image edge is fixed, injectivity in (10) forces its preimage to be
fixed. Thus both orbit counts are preserved separately.

## 6. Recovering every occurrence count

For $\pi\in I_n$, let $f_A(\pi)$ be the number of fixed edges of
$T_\pi$ on its entire $A$-occurrence set, and $d_A(\pi)$ the number of
two-element orbits. Define $f_B,d_B$ likewise. An involution of a finite
set partitions it into singleton and two-element orbits: each element lies
in $\{e,T_\pi(e)\}$, and two such sets are equal or disjoint. Therefore

\[
\operatorname{occ}_A(\pi)=f_A(\pi)+2d_A(\pi),\qquad
\operatorname{occ}_B(\pi)=f_B(\pi)+2d_B(\pi).                 \tag{11}
\]

A transpose-invariant marked subset is exactly a union of these orbits.
In the polynomial ring $\mathbb Z[u,v]$, give a chosen singleton orbit
weight $u$, a chosen two-element orbit weight $v$, and an unchosen
orbit weight $1$. Each orbit is chosen independently, so the sum of weights
over all invariant marked subsets of a fixed permutation is

\[
(1+u)^{f_A(\pi)}(1+v)^{d_A(\pi)}
\]

on the $A$ side, and the analogous expression on the $B$ side. This is
just the distributive expansion of a finite product, including the empty
product. Section 5 supplies a weight-preserving bijection on all invariant
marked objects with underlying permutation in $I_n$. Consequently

\[
\sum_{\pi\in I_n}(1+u)^{f_A(\pi)}(1+v)^{d_A(\pi)}
=\sum_{\pi\in I_n}(1+u)^{f_B(\pi)}(1+v)^{d_B(\pi)}.           \tag{12}
\]

Apply the ring homomorphism $\mathbb Z[u,v]\longrightarrow\mathbb Z[y]$
which sends $u\mapsto y-1$ and $v\mapsto y^2-1$. By (11), (12) becomes

\[
\sum_{\pi\in I_n}y^{\operatorname{occ}_A(\pi)}
=\sum_{\pi\in I_n}y^{\operatorname{occ}_B(\pi)}.               \tag{13}
\]

All sums are finite, so this substitution is an ordinary polynomial
substitution, with no convergence or division issue. The coefficient of
$y^k$ on each side is exactly the number of permutations with that
occurrence count, proving the required all-$k$ equality between $p_1$
and $p_4$. Weighting invariant subsets only by total number of edges would
give $(1+t)^f(1+t^2)^d$ and would not justify this step; the separate
weights in (12) are essential to this argument.

## 7. The other two corrected patterns and boundary cases

Let $r(i)=n+1-i$ on $[n]$, and let $\operatorname{rc}(\pi)=r\pi r$.
Since $r^2=\mathrm{id}$, this operation is its own inverse and
$(r\pi r)^2=r\pi^2r$. It therefore bijects $I_n$ to itself. The
position pair $(i,j)$ corresponds to $(r(j),r(i))$. Both index order
and value order are reversed, so an ascent remains an ascent and a descent
remains a descent. The rank cell $(a,b)$ is sent to $(2-a,2-b)$.
For completeness, on the full boundary lists including $0,n+1$, the
map $s\mapsto n+1-s$ reverses the four boundaries; an open interval
with rank $a$ is the open interval of rank $2-a$ after reflection.
Thus an empty shaded rectangle corresponds to an empty shaded rectangle
in both directions. This sends $R$ to $R'$ and bijects occurrences
of $p_1$ with $p_2$, and occurrences of $p_4$ with $p_3$.
Together with (13) this proves (1) for every pair of the four patterns.

For $n=0$, the single empty permutation is an involution, all occurrence
sets and marked sets are empty, the maps are the unique empty maps, and the
generating polynomial is $1$. For $n=1$ there are likewise no pairs of
indices. All the constructions and formulas above include these cases
without a nonempty-component assumption. For every $n$, coefficients at
unattainable $k$ are zero on both sides. This completes the ordinary proof.

## Sources and review scope

1. Fang–Fu–Kitaev–Li–Su–Sun, *On mesh patterns of short length: Equidistribution
   and enumeration*, [arXiv:2606.14367v2](https://arxiv.org/abs/2606.14367v2),
   corrected Conjecture 1 and Remark 4.1, printed p.17; Definition 2.1, pp.5–6.
   The diagrams and coordinates were checked against both the PDF and TeX.
2. Zhang–Zhao, *The last distribution-equivalence class of mesh patterns of
   length 2*, [arXiv:2607.04111](https://arxiv.org/abs/2607.04111),
   5 July 2026, Theorem 1.1 and Sections 1–2. This is the known
   whole-permutation result and the precedent for the marked-occurrence method.
3. Controller assistance consisted of explicitly unverified route and structural
   drafts. This proof is self-contained; those drafts are not premises.

The v2 source acknowledges the July whole-permutation result while retaining
the corrected involution conjecture. Literature checks through 21 October 2026
support POTENTIALLY_NEW, not a global priority claim; see [review.md](review.md).
The [formalization notes](formal/README.md) state the remaining global construction.

This showcase adapts the local presentation by replacing archive-only references
and updating this review pointer. Its mathematical argument is unchanged. The
earlier presentation corrected three typesetting issues in the reviewed snapshot.
The original snapshot and review digests are retained in
[verification.json](verification.json); no new independent review is claimed.
