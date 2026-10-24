> Public showcase edition: private runtime details were redacted and paths made portable; the original conclusions and evidence levels are unchanged. Hashes and byte sizes in the report body, appendices and historical materials identify the original frozen inputs. Redaction, link edits and provenance notices change the public copies. To check files in this directory, use `files[].sha256` and `files[].bytes` in the [publication manifest](manifest.json), rather than treating differences from the original appendix hashes as corruption. The manifest distinguishes original and public hashes and byte sizes.

# MathLottery expert reading report

> This is an editorial reconstruction of saved research, not a new independent verification. Formatting does not upgrade proof status or certify open status or novelty.

Source task: `reviewed-source`; frozen revision: 9; captured: 2026-10-24T04:21:29.528744+00:00.

## Recorded verification outcomes

- `candidate-record-005` · `SELF_CHECKED` · scope `UNKNOWN`; verdict `NO_ISSUES_FOUND`, coverage `UNKNOWN`, novelty `POTENTIALLY_NEW`

[Evidence manifest](manifest.json)

### Evidence scope and limitations

- This is an editorial reconstruction of visible saved evidence, not hidden reasoning, an independent mathematical verification, or a certification of novelty.
- reviewed-source: only saved answers, named notes, proof/formal files and source receipts are included; arbitrary workspace files, binaries and caches are excluded.
- This historical Verify has no saved solver linkage. The original Solve history is unavailable; matching titles or proofs were not used to guess it.

---

# Four length-two mesh patterns on involutions: an expert exposition of the saved candidate and its evidence

## 1. Abstract and exact evidential conclusion

The saved ordinary proof claims the complete corrected Conjecture 1 of Fang–Fu–Kitaev–Li–Su–Sun: for every pair of nonnegative integers \(n,k\), the four specified mesh patterns have the same number of involutions of size \(n\) with exactly \(k\) occurrences. The argument constructs a bijection on permutations with **arbitrary subsets of marked occurrences**, proves that simultaneous star/path rotations commute with inversion on both objects and individual edges, and uses independent weights for singleton and two-edge transposition orbits to recover every occurrence count. Reverse complement supplies the remaining pattern pairs. The full ordinary argument is expounded below, including empty cases and both directions of the construction.

The saved candidate level is **`SELF_CHECKED`**. Its historical separate AI review returned **`NO_ISSUES_FOUND`**, with novelty **`POTENTIALLY_NEW`** as of **2026-10-21**. The legacy candidate `scope` and review `original_problem_coverage` are both **`UNKNOWN`**; the older record did not supply an explicit coverage assessment. Explaining the full scope claimed and assessed in the prose does **not** turn those fields into `FULL`. The stored problem status is also `UNKNOWN`. There is no external mathematics expert review or external certification of equivalence between the natural-language statement and the formal statement. [Frozen dossier](materials/reviewed-source/dossier.json); [saved review answer](materials/reviewed-source/tasks/task-record-003/attempt-record-004/answer.md).

The separately supplied showcase summary records later compilation, axiom inspection, and fresh Lean kernel replay of **107 theorems**. Those are **partial** formal results: the global construction of \(\mathrm{MarkedTransport}\ n\) for every \(n\) is missing. The ordinary-proof reviewer did not assess this later formalization. Native Solve stopped at a usage limit without a final candidate submission; the controller submitted the ordinary snapshot and later continued partial Lean work. This was not a normally completed end-to-end native Solve. [Supplied verification summary](materials/showcase/verification.json); [formalization scope](materials/showcase/formal/README.md).

This report is an **editorial reconstruction of visible, frozen evidence**, not another Solve or Verify. Its mathematical exposition follows the embedded candidate proof; numbering, transitions, and translations are editorial. It does not supply an unrecorded repair, hidden reasoning, a new literature search, a new finite experiment, or a new Lean run. Literature claims stop at the historical cutoff, not the date of this report. The explicitly supplied showcase documents are a separate source class, not additional files collected by the native Verify manifest. Their limitations and the missing materials are indexed below.

## 2. Original statement, notation, and parameter domains

The target is **corrected Conjecture 1**, Section 4, printed page 17 of the **2026-10-11 v2** of *On mesh patterns of short length: Equidistribution and enumeration*. Its assertion is that the four displayed patterns are equidistributed on involutions. The earlier false version discussed in Remark 4.1 is not the target. Nor is the already known assertion on all permutations. The saved review reports independently retrieving the v2 PDF, TeX, and version metadata and matching its diagrams and coordinates; this editorial session did not retrieve them again. [Versioned primary source](https://arxiv.org/abs/2606.14367v2); [PDF](https://arxiv.org/pdf/2606.14367v2); [TeX source](https://arxiv.org/src/2606.14367v2); [frozen review record](materials/reviewed-source/dossier.json).

Let \([n]=\{1,\ldots,n\}\), with \([0]=\varnothing\). Let \(S_n\) be the permutations of \([n]\), and put

\[
I_n=\{\pi\in S_n:\pi\circ\pi=\mathrm{id}_{[n]}\}.
\tag{1}
\]

There is one empty permutation in \(S_0=I_0\). Define

\[
R=\{(0,0),(1,1),(1,2),(2,1)\},\qquad
R'=\{(2,2),(1,1),(1,0),(0,1)\}.
\tag{2}
\]

In the original printed order,

\[
p_1=(12,R),\quad p_2=(12,R'),\quad
p_3=(21,R'),\quad p_4=(21,R).
\tag{3}
\]

Here \(12\) and \(21\) are the increasing and decreasing permutations in \(S_2\). A shaded cell \((a,b)\), where \(a,b\in\{0,1,2\}\), means the unit cell with that bottom-left coordinate. For \(\pi\in S_n\) and \(1\le i<j\le n\), set

\[
x=(0,i,j,n+1),\qquad
y=(0,\min(\pi(i),\pi(j)),\max(\pi(i),\pi(j)),n+1).
\tag{4}
\]

The pair is an occurrence of \((\tau,S)\), with \(\tau\in S_2\) and \(S=R\) or \(R'\), exactly when its values have relative order \(\tau\) and

\[
\forall(a,b)\in S,\quad
\nexists\,t\in[n]\quad
x_a<t<x_{a+1}\ \text{ and }\ y_b<\pi(t)<y_{b+1}.
\tag{5}
\]

All rectangle inequalities are **strict**. Write \(\operatorname{Occ}_p(\pi)\) for this set of ordered index pairs and \(\operatorname{occ}_p(\pi)=|\operatorname{Occ}_p(\pi)|\).

**Theorem 1 (the complete conclusion claimed by the saved ordinary candidate).** For every \(n,k\in\mathbb Z_{\ge0}\) and every \(s,t\in\{1,2,3,4\}\),

\[
\#\{\pi\in I_n:\operatorname{occ}_{p_s}(\pi)=k\}
=\#\{\pi\in I_n:\operatorname{occ}_{p_t}(\pi)=k\}.
\tag{6}
\]

There are no extra mathematical assumptions in the candidate. This is equality of four **marginal distributions**, for every occurrence count, including avoidance \(k=0\); it is not a joint-distribution identity, nor equality of the four statistics on each individual involution. The finite graph terminology below concerns marked occurrence graphs in permutations, not a separate graph-theory conjecture.

## 3. Proof strategy and dependencies

Put \(A=p_1\) and \(B=p_4\). A marked object is \((\pi,M)\), where \(\pi\in S_n\) and \(M\subseteq\operatorname{Occ}_A(\pi)\) or \(M\subseteq\operatorname{Occ}_B(\pi)\). **Every subset is allowed**; no maximality or saturation is assumed.

The logical dependencies of the saved proof are:

| Step | Mathematical task | Used by |
|---|---|---|
| Lemma 1 | Replace the shaded rectangles by three inequalities | Lemmas 2–4 |
| Lemmas 2–3 | Identify stars and paths and prove single-gap nesting | Lemma 5 |
| Lemma 4 | Obtain one necessary-and-sufficient external condition for both shapes | Lemma 5 |
| Lemma 5 | Rotate all components, prove validity in both nesting directions, and construct the inverse | Lemma 6 |
| Lemma 6 | Prove object and individual-edge inversion equivariance | Lemma 7 |
| Lemma 7 | Use two orbit weights and substitute to recover every coefficient | Theorem 1 for \(A,B\) |
| Lemma 8 | Apply reverse complement and handle endpoints | Theorem 1 for all four patterns |

A tempting shortcut is false. The historical reviewer recorded the involution \(\pi=213\) with the single \(A\)-mark \(M=\{(1,3)\}\); rotating that star gives \(312\), which is not an involution. Indeed transposition sends \((1,3)\) to \((2,3)\), which is absent from \(M\). Thus a marked bijection on all permutations cannot simply be restricted to all markings of involutions. The proof instead restricts to **transpose-fixed marked objects**, and then uses orbit weights to recover the unmarked occurrence distribution. This example is a saved counterexample to the shortcut, not a counterexample to Theorem 1. [Review evidence](materials/reviewed-source/dossier.json).

Lemmas 1–8 below are a faithful exposition of Sections 1–7 of the [embedded historical proof](materials/reviewed-source/dossier.json), with the same mathematics as the [explicitly supplied showcase proof](materials/showcase/proof.md). The latter is a presentation edition. Its recorded changes include an interval-typesetting correction and two conversions of parenthesized `1` to mathematical \(1\), plus citation and review-pointer updates. These edits do not constitute a newly verified proof.

## 4. Detailed ordinary proof

### Lemma 1. The literal rectangle predicate

For \(i<j\), set \(l=\min(\pi(i),\pi(j))\) and \(h=\max(\pi(i),\pi(j))\). The four shaded rectangles for \(R\) are empty if and only if

\[
\begin{array}{ll}
\mathrm L:&t<i\ \Longrightarrow\ \pi(t)>l,\\
\mathrm M:&i<t<j\ \Longrightarrow\ \pi(t)<l,\\
\mathrm Q:&t>j\ \Longrightarrow\ \pi(t)\notin(l,h).
\end{array}
\tag{7}
\]

An \(A\)-occurrence additionally requires \(\pi(i)<\pi(j)\), and a \(B\)-occurrence requires \(\pi(i)>\pi(j)\).

**Proof.** Cell \((0,0)\) forbids an earlier value below \(l\). A nonendpoint cannot equal \(l\), by injectivity, so this is exactly L. Cells \((1,1)\) and \((1,2)\) together forbid an interior value above \(l\): the boundary value \(h\), which their union omits, already occurs at an endpoint and cannot occur inside. The value \(l\) is excluded there for the same reason. This gives M. Cell \((2,1)\) gives Q directly. All indices and values lie in \([n]\), so the outer boundaries \(0,n+1\) introduce no extra cases. These observations work in both directions. ∎

### Lemma 2. The marked components are stars or descending paths

Orient each mark from its smaller to its larger index and discard isolated vertices. Every nontrivial connected component on the \(A\) side is a star, and every such component on the \(B\) side is a descending path.

More precisely, with \(m\ge1\), its vertices and distinct values can be labelled

\[
x_0<x_1<\cdots<x_m,\qquad v_0>v_1>\cdots>v_m,
\tag{8}
\]

so that the two arrangements are

\[
\begin{array}{lll}
A:&(\pi(x_0),\ldots,\pi(x_m))=(v_1,\ldots,v_m,v_0),
&M_C=\{(x_{h-1},x_m):1\le h\le m\},\\
B:&(\pi(x_0),\ldots,\pi(x_m))=(v_0,v_1,\ldots,v_m),
&M_C=\{(x_{h-1},x_h):1\le h\le m\}.
\end{array}
\tag{9}
\]

**Proof.** On the \(A\) side, two outgoing edges \((i,j),(i,k)\), with \(j<k\), would give \(\pi(j)<\pi(i)\) by M for the second, contrary to the ascent of the first. A starting vertex is a left-to-right minimum by L. A terminal vertex of an ascent has an earlier smaller value, so cannot be a starting vertex. Hence each non-root vertex has only its one outgoing edge; terminal roots cannot be joined to one another through such degree-one leaves. Each connected component is therefore a star with a single terminal root. L at successive leaves makes their values strictly decreasing, and the ascent edges put the root above every leaf. This is the first line of (9).

On the \(B\) side, if \((i,j),(k,j)\) were edges with \(i<k<j\), M for the first would imply \(\pi(k)<\pi(j)\), contradicting the descent of the second. Thus indegree is at most one. If \((i,j),(i,k)\) were edges with \(j<k\), M for the second and its descent imply \(\pi(j)<\pi(k)<\pi(i)\); the point at \(k\) then violates Q for the first. Outdegree is also at most one. Indices increase along every edge, so directed cycles are impossible. Following predecessors in a finite component reaches an initial vertex; following successors from it covers the whole component, since an extra attached edge would violate a degree bound. The component is a path, and every edge decreases the value. This is the second line of (9). None of the reasoning requires marks to be maximal. ∎

### Lemma 3. Different components are disjoint or nested in a single gap

Edges belonging to distinct components cannot cross. The closed position intervals of any two distinct components are either disjoint, or the whole interval of one lies in a single open gap between consecutive vertices of the other.

**Proof.** Suppose edges \((i,j),(k,l)\) have \(i<k<j<l\). For \(A\), M for the first and its ascent give \(\pi(k)<\pi(i)<\pi(j)\), whereas M for the second gives \(\pi(j)<\pi(k)\), a contradiction. For \(B\), M for the first gives \(\pi(k)<\pi(j)\), the second descent gives \(\pi(l)<\pi(k)\), and M for the second gives \(\pi(j)<\pi(l)\), again a contradiction. Interchanging the edges treats the other crossing order.

For the stronger assertion, write component vertices as \(c_0<\cdots<c_m\) and \(d_0<\cdots<d_r\). Vertices of distinct components are different. After interchanging their names, the only nondisjoint case to consider is \(c_0<d_0<c_m\). For stars, the edges \((c_0,c_m),(d_0,d_r)\) force \(d_r<c_m\), since otherwise they cross. If some \(c_t\) lay in \((d_0,d_r)\), it would be a leaf and its edge \((c_t,c_m)\) would cross \((d_0,d_r)\). Thus \([d_0,d_r]\) contains no \(c\)-vertex and lies in one open gap.

For paths, choose \(t\) with \(c_t<d_0<c_{t+1}\). If \(d_r>c_{t+1}\), some consecutive \(d\)-vertices straddle \(c_{t+1}\): \(d_a<c_{t+1}<d_{a+1}\). Then \(c_t<d_a<c_{t+1}<d_{a+1}\) gives crossing path edges, a contradiction. Hence \(d_r<c_{t+1}\). This proves the single-gap assertion in both cases. ∎

### Lemma 4. A common necessary-and-sufficient external condition

Fix positions and values as in (8), and arrange them in either line of (9). All designated edges are occurrences of the corresponding pattern if and only if entries at all positions outside \(\{x_0,\ldots,x_m\}\) satisfy

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

**Proof of necessity for a star.** L for the first leaf/root edge gives \(\mathrm O_0\). In gap \(k<m\), M for the edge starting at \(x_{k-1}\) gives the upper bound \(v_k\), and L for the edge starting at \(x_k\) gives the lower bound \(v_{k+1}\). M for the last leaf gives \(\mathrm O_m\), and Q for that same leaf/root edge gives \(\mathrm O_{m+1}\).

**Proof of necessity for a path.** L for the first edge gives \(\mathrm O_0\). In gap \(k<m\), M for edge \(k\) gives the upper bound and L for edge \(k+1\) gives the lower bound. M for the last edge gives \(\mathrm O_m\). After \(x_m\), Q for all path edges forbids the union of the intervals \((v_h,v_{h-1})\), \(1\le h\le m\). This union is \((v_m,v_0)\) with intermediate values \(v_1,\ldots,v_{m-1}\) removed. Those values are already used at designated vertices; injectivity excludes them at any outside entry. Thus \(\mathrm O_{m+1}\) follows.

**Proof of sufficiency for a star.** Consider edge \((x_{h-1},x_m)\), whose low/high values are \(v_h,v_0\). Before its first endpoint, entries before \(x_0\) are \(>v_1\ge v_h\), earlier leaves have values \(>v_h\), and earlier gaps \(k<h\) have values \(>v_{k+1}\ge v_h\). This proves L. Between its endpoints, later leaves have values \(<v_h\), and gaps \(k\ge h\) have values \(<v_k\le v_h\), including the final gap. This proves M. After the root, (10) excludes \((v_m,v_0)\), which contains \((v_h,v_0)\), proving Q.

**Proof of sufficiency for a path.** Consider edge \((x_{h-1},x_h)\), whose low/high values are \(v_h,v_{h-1}\). Entries before its first endpoint exceed \(v_h\) by the same earlier-vertex and earlier-gap bounds. Its interior is gap \(h\), where values are \(<v_h\). To its right, later designated vertices and later gaps have values \(<v_h\); entries after \(x_m\) avoid

\[
(v_m,v_0)\supseteq(v_h,v_{h-1}).
\tag{11}
\]

Thus L, M, and Q hold. For \(m=1\), the intermediate family \(1\le k<m\) is empty, and the same proof applies. ∎

Equation (11) displays the intended interval inclusion that was malformed typographically in the historical snapshot. The historical reviewer explicitly judged that typo harmless, and the supplied presentation-change record fixes it. This report makes that already documented presentation correction explicit; it does not silently change a mathematical claim.

### Lemma 5. Simultaneous rotation is a bijection for arbitrary marked subsets

On every \(A\)-star apply

\[
(v_1,\ldots,v_m,v_0)\longmapsto(v_0,v_1,\ldots,v_m),\qquad
e_h=(x_{h-1},x_m)\longmapsto f_h=(x_{h-1},x_h).
\tag{12}
\]

Doing this on all components defines a bijection \(\Phi\) from marked \(A\)-objects to marked \(B\)-objects, with an edge bijection \(\theta_{\pi,M}:M\to N\). Its inverse \(\Psi\) rotates every marked descending path back and replaces its consecutive edges by the corresponding star edges.

**Proof: defining the operations.** Distinct components have disjoint vertex sets, and a rotation only permutes the values on its own vertices. Thus the simultaneous replacements define a permutation \(\sigma\). The resulting edges are distinct, and (12) gives a bijection \(M\to N\). The reverse replacement is equally well-defined as a permutation and a set of marks. What must still be proved is that every new mark is an occurrence. Disjoint vertex sets alone do not establish this.

**Validity for all components.** Fix a component \(C\), with notation (8). Its own rotation preserves its positions and decreasing list of values, hence all bounds in (10). We check that rotations on every other component \(D\) preserve the conditions for \(C\), and also the conditions for \(D\) when \(C\) surrounds it.

If their position intervals are disjoint, all vertices of \(D\) lie on the same exterior side of \(C\). All their values already satisfy that side's condition in (10), and permuting those values preserves it. This remains valid on the right even though the allowed values lie in two separated intervals.

If \(D\) lies in an intermediate gap \(k<m\) of \(C\), all its values lie in \((v_{k+1},v_k)\); its rotation preserves membership in that interval. In the final gap all its values are \(<v_m\), again preserved. This checks the effect of an **inner** rotation on the **outer** component.

For the other direction, suppose \(D\) lies in gap \(k\) of \(C\), and put

\[
a=\min\{\pi(d):d\in D\},\qquad b=\max\{\pi(d):d\in D\}.
\tag{13}
\]

These bounds do not change when \(D\) rotates. If \(k<m\), then

\[
v_{k+1}<a\le b<v_k.
\tag{14}
\]

The possible values of vertex \(x_t\) of \(C\) in its star and path arrangements are, respectively,

\[
\begin{cases}
(v_{t+1},v_t),&0\le t<m,\\
(v_0,v_m),&t=m.
\end{cases}
\tag{15}
\]

For \(t\le k-1\), the vertex is before \(D\) and both possible values are at least \(v_k>b\). The vertex \(x_k\) is after \(D\); its two possible values are \(v_{k+1}<a\) and \(v_k>b\). Vertices with \(k<t<m\) are also after \(D\), with both values at most \(v_{k+1}<a\). The last vertex \(x_m\) is after \(D\), with possibilities \(v_0>b\) and \(v_m<a\). Thus every \(C\)-value before \(D\) exceeds all \(D\)-values, and every \(C\)-value after \(D\) lies outside \([a,b]\). These are stronger than the two exterior requirements in (10) for \(D\). No vertex of \(C\) lies in the interior of \(D\)'s interval, so its interior requirements are unaffected.

For the final gap \(k=m\), all \(D\)-values are \(<v_m\). Every \(x_t\) with \(t<m\) precedes \(D\), and both of its values are \(\ge v_m>b\). The only \(C\)-vertex after \(D\) is \(x_m\), whose two values \(v_0,v_m\) both exceed \(b\). This proves the exterior requirements in this case too. We have now checked the effect of an **outer** rotation on an **inner** component, in both arrangements.

By Lemma 3 these cases exhaust the possibilities. They depend only on fixed position sets, value sets, and the two possible values at each component vertex; no particular order of rotations was used. An unmarked, untouched point retains its original allowed value. Every changed point satisfies the appropriate case above relative to each other component. Consequently all conditions (10) survive **simultaneously**, for \(\Phi\) and for \(\Psi\). Lemma 4 proves that every resulting mark is an occurrence of the required pattern.

**Two-sided inverse.** Each star is replaced by a connected path on exactly its vertex set, with no marked edge between different components. Therefore the new marked graph has exactly the same component vertex sets. The reverse operation finds those components, rotates each value list back, and restores every original edge. The same argument starting from paths gives

\[
\Psi\Phi=\mathrm{id},\qquad \Phi\Psi=\mathrm{id}.
\tag{16}
\]

For an empty marked set, both maps leave the permutation unchanged. Extra unmarked occurrences in the output do not alter these marked components and need not be forbidden. Thus the bijection applies to all marked subsets. ∎

### Lemma 6. Inversion equivariance holds for objects and individual edges

For an edge \(e=(i,j)\), define

\[
T_\pi(e)=\bigl(\min(\pi(i),\pi(j)),\max(\pi(i),\pi(j))\bigr),
\qquad
(\pi,M)^T=(\pi^{-1},T_\pi M).
\tag{17}
\]

Transposition bijects the occurrences of \(A\) in \(\pi\) with those in \(\pi^{-1}\), and likewise for \(B\). If \(\Phi(\pi,M)=(\sigma,N)\), then

\[
\Phi((\pi,M)^T)=\Phi(\pi,M)^T,
\qquad
\theta_{\pi^{-1},T_\pi M}(T_\pi e)
=T_\sigma\bigl(\theta_{\pi,M}(e)\bigr)
\quad(e\in M).
\tag{18}
\]

**Proof.** Transposing the permutation plot interchanges its sorted position and value boundary lists. The underlying permutations \(12,21\) are self-inverse, and \(R\) is invariant under \((a,b)\mapsto(b,a)\). A forbidden point in a strict rectangle corresponds in both directions to a forbidden point in its transposed rectangle. This proves the occurrence bijection, whose inverse is \(T_{\pi^{-1}}\).

Transpose an \(A\)-star from (9). Its increasing positions and corresponding values become

\[
\begin{array}{ll}
\text{positions}:&(v_m,v_{m-1},\ldots,v_0),\\
\text{values before rotation}:&(x_{m-1},\ldots,x_0,x_m),\\
\text{values after rotation}:&(x_m,x_{m-1},\ldots,x_0).
\end{array}
\tag{19}
\]

Each original edge becomes \((v_h,v_0)\), so this is exactly the transposed star. The original rotation has \(\sigma(x_t)=v_t\); therefore the last row is its inverse. Distinct original component vertex sets become disjoint value sets under transposition, and give exactly the transposed components. Points outside all components are unchanged on both sides. This establishes the object identity, including its underlying permutation \(\sigma^{-1}\).

For an individual edge \(e_h=(x_{h-1},x_m)\), its transpose is \((v_h,v_0)\), the edge with index \(m-h+1\) in the increasingly ordered transposed star. Rotating that star sends it to \((v_h,v_{h-1})\). Alternatively, first rotating sends \(e_h\) to \(f_h=(x_{h-1},x_h)\), whose values in \(\sigma\) are \((v_{h-1},v_h)\); transposing gives the same edge \((v_h,v_{h-1})\). This proves the second identity in (18) for every marked edge, including edges in self-transposed components. No middle-edge or orientation exception occurs.

Since \(\Psi=\Phi^{-1}\), object equivariance holds for \(\Psi\) by applying \(\Phi\) and using injectivity. Inverting the edge bijections gives inverse edge equivariance as well. Thus transpose-fixed objects correspond bijectively. They are precisely

\[
\pi\in I_n,\qquad T_\pi(M)=M.
\tag{20}
\]

On such an object, transposition is an involution on the marked edges. Equation (18) sends a fixed edge to a fixed edge and a two-edge orbit to a two-edge orbit. Conversely, if the image of an edge is fixed, injectivity of \(\theta\) in (18) forces the original edge to be fixed. The numbers of singleton and two-edge orbits are therefore preserved **separately**. ∎

### Lemma 7. Two orbit weights recover every occurrence count

For \(\pi\in I_n\), let \(f_A(\pi)\) and \(d_A(\pi)\) be the numbers of singleton and two-element orbits of \(T_\pi\) on the **entire** set \(\operatorname{Occ}_A(\pi)\), and define \(f_B,d_B\) in the same way. Then

\[
\operatorname{occ}_A(\pi)=f_A(\pi)+2d_A(\pi),\qquad
\operatorname{occ}_B(\pi)=f_B(\pi)+2d_B(\pi).
\tag{21}
\]

Moreover the occurrence generating polynomials for \(A,B\) agree for every \(n\).

**Proof.** Every orbit of an involution on a finite set is \(\{e,T_\pi(e)\}\), of size one or two; two such sets are equal or disjoint. This proves (21). An invariant marked subset is exactly a union of these orbits.

In \(\mathbb Z[u,v]\), give a chosen singleton orbit weight \(u\), a chosen two-edge orbit weight \(v\), and an unchosen orbit weight \(1\). Write \(s(M),q(M)\) for the numbers of chosen singleton and two-edge orbits. Independent selection of these orbits gives, for fixed \(\pi\),

\[
\sum_{\substack{M\subseteq\operatorname{Occ}_A(\pi)\\T_\pi M=M}}
u^{s(M)}v^{q(M)}
=(1+u)^{f_A(\pi)}(1+v)^{d_A(\pi)}.
\tag{22}
\]

This is the distributive expansion of a finite product, including the empty product; the same formula holds for \(B\). Lemma 6 supplies a bijection of all fixed marked objects preserving both exponents, so

\[
\sum_{\pi\in I_n}(1+u)^{f_A(\pi)}(1+v)^{d_A(\pi)}
=\sum_{\pi\in I_n}(1+u)^{f_B(\pi)}(1+v)^{d_B(\pi)}.
\tag{23}
\]

Apply the polynomial-ring homomorphism

\[
\mathbb Z[u,v]\longrightarrow\mathbb Z[y],\qquad
u\longmapsto y-1,\quad v\longmapsto y^2-1.
\tag{24}
\]

Each summand becomes \(y^{f+2d}\). Consequently

\[
\sum_{\pi\in I_n}y^{\operatorname{occ}_A(\pi)}
=\sum_{\pi\in I_n}y^{\operatorname{occ}_B(\pi)}.
\tag{25}
\]

All sums and products are finite; neither convergence nor division is involved. The coefficient of \(y^k\) is exactly the number of involutions with \(k\) occurrences, which gives (6) for \(A,B\), for every \(k\ge0\).

The separate weights are essential to this argument. Weighting an invariant subset only by its number of marked edges produces \((1+t)^f(1+t^2)^d\); the substitution in (24) is not a justified substitution in that single variable. Preservation of the two orbit counts is what permits the stated coefficient recovery. ∎

### Lemma 8. Reverse complement and all endpoint cases

Let \(r(i)=n+1-i\) on \([n]\) and define \(\operatorname{rc}(\pi)=r\pi r\). This involution on permutations preserves \(I_n\), and bijects occurrences of \(p_1\) with those of \(p_2\), and occurrences of \(p_4\) with those of \(p_3\).

**Proof.** Since \(r^2=\mathrm{id}\), reverse complement is its own inverse and

\[
(r\pi r)^2=r\pi^2r.
\tag{26}
\]

Thus it maps involutions bijectively to involutions. A position pair \((i,j)\) becomes \((r(j),r(i))\). Both position order and value order are reversed, so ascents remain ascents and descents remain descents. The cell map is

\[
(a,b)\longmapsto(2-a,2-b),\qquad R\longmapsto R'.
\tag{27}
\]

To check strict boundaries as well, extend \(s\mapsto n+1-s\) to the boundary values \(0,n+1\). It reverses the four sorted boundaries in (4), taking an open rank-\(a\) interval to an open rank-\(2-a\) interval, and similarly for values. Hence empty shaded rectangles correspond in both directions. Occurrence counts are preserved for each indicated pair of patterns.

For \(n=0\), there is a single empty involution, all occurrence and mark sets are empty, the component operations are the empty operations, and the generating polynomial is \(1\). For \(n=1\), there are likewise no index pairs and the generating polynomial is \(1\). In either case, the count in (6) is \(1\) for \(k=0\) and \(0\) for \(k>0\). Empty markings for any \(n\) were already included in Lemma 5, and one-edge components \(m=1\) in Lemma 4. For any \(n\), unattainable coefficients are zero on both sides; in particular this holds for \(k>\binom n2\). There is no additional equality-case restriction because the conclusion is an identity for every allowed \(n,k\). ∎

**Completion of the saved ordinary argument for Theorem 1.** Lemma 7 equates \(p_1\) and \(p_4\); Lemma 8 equates \(p_1,p_2\) and \(p_4,p_3\). Combining the three equalities proves (6) for any two of the four patterns. This completes the exposition of the submitted ordinary argument. Its evidence level remains the one stated in Section 1.

## 5. Recorded verification and the scope of each kind of evidence

### 5.1 Historical ordinary-proof review

The single saved review records **`NO_ISSUES_FOUND`** and an empty issue list. It states that the exact v2 diagrams, strict rectangles, and all-\(n\), all-\(k\) involution statement matched the independently retrieved sources. Its mathematical assessment explicitly covers the L/M/Q equivalence, degree bounds, single-gap nesting, both directions of the external characterization, simultaneous inner and outer rotations, both inverse identities, object and edge equivariance including self-transposed components, singleton/doubleton weights, substitution, coefficients, reverse complement, and endpoints. It reports no extra hypothesis, substantive gap, or circularity, and identifies the interval typo as typographical only. These are **the historical AI review's findings**, not findings of a new independent review here. [Exact saved review](materials/reviewed-source/dossier.json); [reviewer's final answer](materials/reviewed-source/tasks/task-record-003/attempt-record-004/answer.md).

The review narrative refers to 18 proof checks and 19 literature queries in separate detailed files. Those files were not collected in this frozen native bundle. In the normalized saved review, `checks` and the structured literature-query arrays are empty; the narrative references do not fill those arrays retroactively. The absence of those artifacts limits inspection of the historical checking procedure, without changing the saved verdict.

### 5.2 Finite challenges

The historical reviewer reports independently written exhaustive challenges with the following results, repeated in the supplied showcase summary:

| Scope | Recorded size | Recorded result and connection to the proof |
|---|---:|---|
| All permutations of sizes \(0\) through \(8\), and every applicable marked subset on each side | 46,234 permutations; 130,354 marked \(A\)-objects and 130,354 marked \(B\)-objects | All inverse, object-equivariance, and individual-edge-equivariance checks passed; finite challenges to Lemmas 5–6 |
| All eligible star/path component arrangements through \(n=7\) | 199,630 arrangements | Both directions of the external-condition equivalence passed; finite challenge to Lemma 4 |
| All involutions through \(n=11\) | 48,928 involutions | The four occurrence-count histograms agreed; finite challenge to Theorem 1 |

The naive involution-restriction counterexample \(213\mapsto312\) was also recorded, as explained in Section 3. It is a negative result for a proposed shortcut that the submitted argument avoids. No counterexample to the actual candidate is reported. [Frozen review evidence](materials/reviewed-source/dossier.json); [supplied review summary](materials/showcase/review.md).

These counts are recorded outcomes, not computations repeated during Organize. The script referred to as `review/check_candidate.py` and its result JSON files are absent from the native manifest and from the supplied showcase file list. Therefore this package does not provide an executable finite-check certificate or a complete reproduction command for those historical challenges. They search for bounded counterexamples and implementation errors; no finite bound proves the universal theorem. The ordinary proof above uses none of these experiments as a premise.

### 5.3 Later partial Lean work

The following table reports the scope stated in the explicit [formalization supplement](materials/showcase/formal/README.md), not a fresh inspection or execution of the Lean files. There are 12 proof modules and the `MeshPartial` inspection entry point.

| Modules | Recorded content | Relation to this exposition |
|---|---|---|
| `MeshDefinitions`, `MeshStructure` | Actual finite permutations, strict empty rectangles, L/M/Q equivalences, local graph structure | Definitions and local portions of Lemmas 1–2 |
| `MeshSymmetry` | Inversion and reverse complement; full distribution equalities for patterns having the same underlying permutation | Symmetries in Lemmas 6 and 8; these do not by themselves bridge \(12\) to \(21\) |
| `MeshComponents`, `MeshRotation` | Necessary-and-sufficient external conditions for a single component, its rotation and inverse | Lemma 4 and the single-component part of Lemma 5 |
| `MeshEquivariance`, `MeshNesting`, `MeshCompatibility` | Single-component inversion compatibility, edgewise formulas, nesting, and key compatibility conditions | Local ingredients of Lemmas 3, 5, and 6 |
| `MeshOrbitCounting`, `MeshPolynomial`, `MeshTransport` | Finite orbit weights, polynomial coefficients for actual occurrence sets, and weight preservation by equivariant edge maps | Counting machinery of Lemma 7 and transport consequences |
| `MeshReduction` | Derivation of the full four-pattern statement under an explicit global marked-transport premise | Conditional reduction to Theorem 1 |
| `MeshPartial` | Imports, key type displays, and axiom displays for 107 theorems | Inspection entry point, not a proof of the missing premise |

The exact conditional theorem reported is:

```lean
Mesh.correctedConjecture_of_markedTransport :
  (∀ (n : ℕ), Nonempty (Mesh.MarkedTransport n)) → Mesh.correctedConjecture
```

Here `Mesh.correctedConjecture` is reported to define the original four-pattern all-\(n\), all-\(k\) equality. **The premise has not been proved, and has not been declared as an axiom.** Missing work consists of canonical decomposition and reconstruction for arbitrary marked occurrence subsets; assembly and two-sided validity of the simultaneous global rotation; and global object and edge equivariance producing an actual `MarkedTransport n` for every \(n\). Local component theorems do not instantiate this global premise. Consequently there is **no unconditional Lean theorem for the entire original conjecture** in the supplied evidence.

The summary records Lean **4.35.0**, mathlib commit **`56a005855ea17e0b0958f73ec801ae140b0a1679`**, and these historical controller checks:

| Historical check | Command | Recorded exit code |
|---|---|---:|
| Compilation | `lake build` | 0 |
| Types and transitive axiom dependencies | `lake env lean MeshPartial.lean` | 0 |
| Fresh replay through Lean's kernel | `lake env leanchecker --fresh --verbose MeshPartial` | 0 |

The summary says all 107 audited theorems used at most `propext`, `Classical.choice`, and `Quot.sound`, with no proof placeholders or native computations bypassing the kernel, and that the published Lean source hashes match the compiled/replayed versions. This is a **recorded controller audit**, with log digests retained in [verification.json](materials/showcase/verification.json); raw logs are not bundled, and no separate AI formalization review is supplied. Kernel replay still trusts Lean's own kernel and proves the supplied formal statements with their explicit hypotheses; it does not establish natural-language correspondence or a missing global construction.

The supplement attributes the first eight proof modules to native solving. It reports later controller fixes to compilation errors in `MeshOrbitCounting` and `MeshPolynomial`, and controller additions of `MeshTransport`, `MeshReduction`, and `MeshPartial`. Earlier compilation errors therefore form part of the history; their individual diagnostics are not available here. Later successful checks must not be attributed to the earlier ordinary-proof reviewer. The showcase export itself did not rebuild Lean, and this Organize session did not run Lean or Lake.

## 6. Original-problem coverage and unresolved limitations

| Requirement | What the saved ordinary argument states | Evidential limit retained |
|---|---|---|
| Exact v2 patterns and strict rectangles | Equations (2)–(5), Lemma 1, and Lemma 8 use the specified shadings | Historical source comparison is recorded; PDFs/TeX are not in this native bundle |
| All involutions | Lemma 6 restricts to transpose-fixed objects; Lemma 7 recovers the unmarked counts | No direct restriction of arbitrary markings is claimed |
| Arbitrary marked subsets | Lemmas 2–5 impose no maximality and cover empty and nested markings | The corresponding global Lean assembly is missing |
| Every \(n,k\ge0\) | Finite-polynomial identity and coefficient extraction in Lemma 7; endpoints in Lemma 8 | Finite tests alone have bounded scope |
| All four marginal distributions | Lemma 7 bridges \(p_1,p_4\); Lemma 8 supplies \(p_1,p_2\) and \(p_4,p_3\) | No joint-distribution claim is made |
| Recorded coverage field | Candidate `scope=UNKNOWN`; review `original_problem_coverage=UNKNOWN` | Neither is upgraded to `FULL` by this report |

No unresolved mathematical gap was identified in the **saved ordinary-proof review**. Both saved `remaining_obligations` arrays are empty. Those are historical entries, not a new completion certificate, and they do not erase the explicit formalization gap. The normalized review also has `formal_check=null`, `formal_receipt=null`, and `evidence_assessment.supported=false`, without a populated assessment policy or reasons. Such empty legacy structures must not be interpreted as a successful modern formal receipt or an independently supported coverage assessment.

The outstanding limitations are substantive: no global Lean transport construction; no later independent formalization review; no external expert review or statement-equivalence certification; inaccessible literature described below; absent detailed review/checker artifacts; and missing explicit solver linkage. A future completion of the global construction or any proposed repair of the ordinary proof would need a new Solve/Verify. This report proposes no mathematical repair and changes neither candidate nor review.

## 7. Sources, known method, novelty, and bibliography

The star/path marked-occurrence method has a known predecessor in Zhang–Zhao. The candidate explicitly acknowledges it and also acknowledges controller route and structural drafts as **unverified assistance, not premises**. The additional scope claimed here is the involution restriction via object/edge inversion equivariance and the two-orbit-weight recovery. The original authors' revised conjecture is evidence of an author-stated open question on 2026-10-11, not independent confirmation that the problem remains open at the time of this report.

The historical reviewer reports 19 targeted queries and primary-source follow-up through **2026-10-21**, finding no earlier complete public solution. The v2 itself acknowledges the July all-permutation result while retaining the corrected involution conjecture. A layered-permutation follow-up had a different domain. A related alternating-permutation preprint was located, but its full text was inaccessible through the attempted HAL/SSRN routes; additional results in that text were not excluded. Indexing delay, inaccessible, unindexed, and unpublished work remain limitations. Accordingly **`POTENTIALLY_NEW` is the saved bounded-search assessment, not confirmation of a first solution or worldwide priority**. No literature status was refreshed during Organize. [Historical novelty record](materials/reviewed-source/dossier.json); [supplied review summary](materials/showcase/review.md).

1. **Qi Fang, Shishuo Fu, Sergey Kitaev, Haijun Li, Xinyu Su, and Ziyao Sun**, *On mesh patterns of short length: Equidistribution and enumeration*, arXiv:2606.14367v2, revision 2026-10-11. Definition 2.1, printed pp. 5–6; equidistribution quantifiers on p. 2; corrected Conjecture 1, Remark 4.1, and footnote 3 on p. 17. The saved review records v2 metadata time 2026-10-11 12:48:29 UTC and retrieval on 2026-10-21; the TeX locator is lines 1007–1012 of `mesh_pattern_arXiv_version_1011.tex`. [Version page](https://arxiv.org/abs/2606.14367v2), [PDF](https://arxiv.org/pdf/2606.14367v2), [TeX](https://arxiv.org/src/2606.14367v2).
2. **Zuo-Ru Zhang and Hongkuan Zhao**, *The last distribution-equivalence class of mesh patterns of length 2*, arXiv:2607.04111, 2026-07-05. Theorem 1.1 and Sections 1–2, including the marked-occurrence construction on pp. 3–4, supply the known all-\(S_n\) result and method. The historical reviewer reports reading the complete five-page text and distinguishing it from the corrected all-\(I_n\) target. [Abstract](https://arxiv.org/abs/2607.04111), [PDF](https://arxiv.org/pdf/2607.04111).
3. **Jiahao Zhang, Sergey Kitaev, Artem Pyatkin, and Xinyu Su**, *Equidistribution of mesh patterns of short length on layered permutations*. The saved review records online publication on 2026-10-15, with a journal volume dated 2027, and inspection on 2026-10-21. Its domain is layered permutations, not all involutions. [Repository entry](https://strathprints.strath.ac.uk/97484/), [recorded PDF](https://strathprints.strath.ac.uk/97484/7/Zhang-etal-DM-2026-Equidistribution-of-mesh-patterns-of-short-length-on-layered-permutations.pdf).
4. **Related alternating-permutation preprint**, [recorded SSRN locator](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7425138). A full title and author list are not supplied in the frozen excerpts used here, and the historical reviewer could not access the full text. This entry records an unresolved literature comparison, not an inspected source proving absence of prior work.
5. **Public Xinyu Su arXiv index**, [metadata page](https://arxiv.symmetricfunctions.com/author/xinyu-su). This appears among the inherited problem references as corroborating revision metadata only; it is not independent evidence of open status.

The inherited problem's difficulty and feasibility prose describes a pre-solution assessment: rank 1, a substantial finite-bijection project, unknown Lean feasibility, and controller-reported \(n\le7\) feasibility tests. These are estimates and historical context, not a success probability, a proof, or a later validation result. The supplied summary records Find as completed; it does not supply the complete Find or Solve history here.

## 8. Reproducibility and source identity

This editorial session read the two native manifest files and the supplied inline showcase texts/change record. It performed only lightweight byte-identity and report-consistency checks. The native file sizes and SHA-256 digests matched the manifest; the embedded proof and the candidate content digest matched the recorded values. None of these checks is a mathematical verification.

The formal supplement gives the following **future reproduction instructions**, to run from the attached `materials/showcase/formal/` directory after installing official Elan:

```sh
lake update
lake exe cache get
lake build
lake env lean MeshPartial.lean
lake env leanchecker --fresh --verbose MeshPartial
```

These commands are reproduced from the source notes, **not executed here**. The pinned `lean-toolchain`, `lakefile.toml`, and `lake-manifest.json` are part of the supplied file index. Toolchains and large dependencies must be downloaded separately. Reproduction should retain/check the declared Lean and mathlib pins, and can confirm only the existing partial statements and their premises. There is no supplied command that builds an unconditional full-conjecture theorem.

For example, byte identity of the presentation proof can be checked with:

```sh
sha256sum materials/showcase/proof.md
```

The expected **presentation-file** digest is `0788dc26255153faaab5e5458b373d279767b950bd702204534ce6d7cba26e47`. It is intentionally distinct from the reviewed historical proof digest below. For the unavailable finite-check script and raw review artifacts, no reproduction success or invented executable command is supplied.

| Hash domain | SHA-256 | Meaning |
|---|---|---|
| Historical candidate content | `74183c541d86feb6ecc57151b1cfc661663afb1d50b985c806defec3bf0c4e6f` | UTF-8 of `claim + newline + proof`; reproduced from the frozen dossier |
| Historical ordinary proof | `8c6844e8b904f446524ec16aea6baf94343d317ba3b6b089fca5305b66e1a01b` | UTF-8 embedded proof; the immutable text reviewed |
| Original detailed review report | `08956a0884958da8013ac18e1d264a804e72df0fdec1f5e15e2fed64669c68e9` | Digest supplied by the showcase summary; the detailed report itself is absent here |
| Later showcase proof | `0788dc26255153faaab5e5458b373d279767b950bd702204534ce6d7cba26e47` | Presentation edition, with the documented typographical/reference edits |
| Problem statement text | `bbb48b9352ff8f3728416867a6ced5b0387b93bdfb4c7e73cd079a1eac2f0521` | SHA-256 of UTF-8 `Problem.statement`; also the formal-receipt statement-text domain, although no such receipt is saved here |
| Full canonical problem record | `e7805279c77205034b016c7e85cfefbbbec3ae5f85cb44f0003fb5232601d4f2` | Manifest's `discovery.problem_fingerprint`, including metadata and legacy normalization; supplied as a different domain |

The last two hashes have different inputs and must not be compared as though they were the same kind of checksum. A hash identifies bytes in its specified domain; it certifies neither mathematical truth nor natural-language/formal-statement correspondence. The later presentation digest must not replace the identity of the historical reviewed proof.

## Appendix A. Concise chronology of the saved work

| Time or order | Saved event | What can and cannot be inferred |
|---|---|---|
| 2026-07-05 | Zhang–Zhao's known all-permutation result | Methodological precedent, not the selected involution solution |
| 2026-10-11 | Primary authors' v2 retains corrected Conjecture 1 and distinguishes the false earlier version | Historical author-stated conjecture; not today's open-status certification |
| Before the historical ordinary review; exact session linkage absent | Supplied showcase summary says native Find completed; controller route/structural drafts assisted native solving; a complete ordinary draft was written; native Solve stopped during formalization at a usage limit without final candidate submission | The controller subsequently submitted the ordinary snapshot. No explicit solver linkage is saved in the Verify dossier, so no session association or unseen attempt sequence is reconstructed |
| 2026-10-21, 10:39:24–10:50:50 UTC | The visible Verify record was created and completed; one candidate and one completed review are saved | These are dossier timestamps, not a full event trace. Review verdict `NO_ISSUES_FOUND`, novelty `POTENTIALLY_NEW`; historical coverage remains `UNKNOWN` |
| During that historical review | Source comparisons, finite challenges, the naive-restriction counterexample, and bounded literature work were reported | The reviewer states that solver/controller history was not consulted; detailed supporting scripts and reports are referenced but absent from the present native bundle |
| Later controller work, summarized with evidence date 2026-10-21 | Compilation fixes, added reduction/transport/inspection modules, 107 theorem checks, axiom inspection, and fresh kernel replay | Separate from the earlier ordinary review; full formal global construction still missing; exact per-command times and raw logs not supplied |
| Later showcase presentation | Three typographical edits, public/local citation updates, and bilingual documentation | Mathematical argument reported unchanged; no new independent review, and no new Lean build during export |
| 2026-10-24 frozen capture and this Organize | Native source revision 9 was frozen; two standalone reports were organized from that snapshot and the explicit supplement | Editorial exposition and consistency checking only; no new literature status or proof certification |

Only one ordinary candidate and one completed historical review are visible in the native dossier. `visible_research_notes` and `evidence_receipts` are empty, and `review_source` is null. The manifest explicitly records the absent solver linkage. No abandoned attempts, hidden solver notes, or exact Solve chronology can be recovered from matching titles. The concise chronology above attributes the additional history to the supplied showcase summary rather than inventing a database link.

## Appendix B. Materials, availability, and trust boundaries

### B.1 Native frozen materials

| Material | Availability and use | SHA-256 |
|---|---|---|
| [Frozen dossier](materials/reviewed-source/dossier.json) | 42,515 bytes; contains the problem, complete ordinary candidate, exact saved review, references, and one visible chronology entry | `00939d2d0d9d27a5dace6a3af7e9f79f4367f8939d5ed9c9aeffef53f7d1d581` |
| [Saved historical review answer](materials/reviewed-source/tasks/task-record-003/attempt-record-004/answer.md) | 1,657 bytes; final review prose, including verdict and limitations | `e8f3b667a21802cc3c6d30e52f4bf6af1424bc20c0b3e0f7c8cfd6ce6a4f2033` |

The native manifest lists only these two files and an empty omission list. That empty list does not imply that every artifact mentioned inside the dossier is attached. The full candidate proof was read from its embedded `proof` field. The detailed independent report, 18-check evidence file, snapshot-identity file, retrieval/source-pattern records, web-call log, finite-check script/results, local PDFs/TeX, controller drafts, and status-check file are mentioned in historical prose but are **not native attachments**. Raw transport-event references are also not attached and were not used as evidence of unseen actions. No hidden reasoning is supplied or reconstructed.

### B.2 Explicitly supplied showcase supplement

The following files are **explicit showcase supplements**, not native manifest collection entries. The user supplied four inline texts (`README.md`, `review.md`, `formal/README.md`, and a `verification.json` rendition omitting its redundant file-hash index), a presentation-proof diff, and this 24-file size/hash inventory. The full `.lean` contents and the standalone showcase proof file were not independently available as native files for this editorial session; the ordinary proof itself was available in full in the dossier. The publication step is to attach the same frozen showcase files at the following links. File names or hashes alone are not treated as inspected mathematical content. Source descriptions in Section 5 are attributed to the supplied summaries.

The short digests in the index below are the **first 12 hexadecimal characters** of supplied SHA-256 values, useful for identification only. Full supplied digests are retained in the showcase verification record and frozen supplemental inventory. No fresh byte comparison of absent showcase files is claimed.

| Supplemental material | Bytes | Supplied SHA-256 prefix | Use and source status |
|---|---:|---|---|
| [README.cn.md](materials/showcase/README.cn.md) | 2,099 | `0b78e1af82f0` | Chinese case overview; index and status |
| [README.md](materials/showcase/README.md) | 2,564 | `ddd34f98b817` | English overview; full text supplied inline |
| [formal/MeshCompatibility.lean](materials/showcase/formal/MeshCompatibility.lean) | 6,674 | `ff83da03043b` | Local and nesting compatibility conditions |
| [formal/MeshComponents.lean](materials/showcase/formal/MeshComponents.lean) | 10,675 | `3882654f5bf9` | Single-component external conditions |
| [formal/MeshDefinitions.lean](materials/showcase/formal/MeshDefinitions.lean) | 5,780 | `9bac2a293d76` | Permutations, rectangles, and target definitions |
| [formal/MeshEquivariance.lean](materials/showcase/formal/MeshEquivariance.lean) | 4,463 | `997a9f7d8de6` | Single-component and edge equivariance |
| [formal/MeshNesting.lean](materials/showcase/formal/MeshNesting.lean) | 2,752 | `81055e6a56cc` | Nesting conditions |
| [formal/MeshOrbitCounting.lean](materials/showcase/formal/MeshOrbitCounting.lean) | 6,033 | `24c82721a9c6` | Finite orbit weights |
| [formal/MeshPartial.lean](materials/showcase/formal/MeshPartial.lean) | 4,677 | `d91e8f23ff1c` | Imports and type/axiom inspection entry point |
| [formal/MeshPolynomial.lean](materials/showcase/formal/MeshPolynomial.lean) | 4,138 | `33f6ed655e24` | Polynomial coefficients for occurrence counts |
| [formal/MeshReduction.lean](materials/showcase/formal/MeshReduction.lean) | 3,516 | `57a2b6b1a435` | Original-statement reduction with a global premise |
| [formal/MeshRotation.lean](materials/showcase/formal/MeshRotation.lean) | 6,677 | `8222189953c3` | Single-component rotation and inverse |
| [formal/MeshStructure.lean](materials/showcase/formal/MeshStructure.lean) | 2,076 | `3e2f503183dd` | Local marked-graph structure |
| [formal/MeshSymmetry.lean](materials/showcase/formal/MeshSymmetry.lean) | 6,750 | `8143c05a87b7` | Inversion, reverse complement, and same-underlying-pattern distributions |
| [formal/MeshTransport.lean](materials/showcase/formal/MeshTransport.lean) | 2,051 | `b5e2d2b6ed53` | Weight transport through equivariant edge maps |
| [formal/README.cn.md](materials/showcase/formal/README.cn.md) | 2,564 | `a80a05b73c5c` | Chinese formal scope and reproduction notes |
| [formal/README.md](materials/showcase/formal/README.md) | 3,106 | `6b87f8ab73b0` | English formal notes; full text supplied inline |
| [formal/lake-manifest.json](materials/showcase/formal/lake-manifest.json) | 3,557 | `35d978fa9cd2` | Dependency lock manifest |
| [formal/lakefile.toml](materials/showcase/formal/lakefile.toml) | 498 | `87aac4742e53` | Lake project configuration |
| [formal/lean-toolchain](materials/showcase/formal/lean-toolchain) | 25 | `ca5f1f601d34` | Lean version pin |
| [proof.md](materials/showcase/proof.md) | 22,270 | `0788dc262551` | Ordinary proof presentation; historical text and presentation diff supplied |
| [review.cn.md](materials/showcase/review.cn.md) | 2,374 | `c94f9195beaf` | Chinese historical review summary; not a new review |
| [review.md](materials/showcase/review.md) | 3,096 | `93f8010f5572` | English historical review summary; full text supplied inline |
| [verification.json](materials/showcase/verification.json) | 7,782 | `f1579a2ca1d6` | Existing evidence summary, full hashes, and log digests |

### B.3 Unattached primary files and final trust boundaries

The historical review also retains the following primary-file digests. They are saved identity information, not results of fresh downloads or comparisons, and do not turn absent source files into attachments.

| Unattached file | Recorded SHA-256 |
|---|---|
| Fang et al. v2 PDF | `d019d71fbb265fc0fc4619d9849855c644811498dd0812c34a2c0e741a04c57a` |
| Extracted Fang et al. v2 TeX | `a104f63c5186abffcf8efde9329e119135d49540afedeb1c0e15d0613e1759f4` |
| Zhang–Zhao PDF | `380cc56b2d9b6b8ab65abc2f5bf2fd4acfe88058ac1212e7a5d80378bd931fc1` |
| Layered-permutation paper PDF | `22d4d19be4e7dc4fc5e4bb0abe8c7f6fb9c8a8307d2e9baff7b8045788140460` |

The complete readable ordinary argument, the saved AI review verdict, the finite-challenge summary, and the later partial Lean record are four different kinds of evidence. The first is available for step-by-step expert scrutiny; an AI review is not external expert certification; finite challenges do not cover unbounded parameters; and the reported Lean successes concern only constructed formal results and their explicit premises. Presentation, translation, hashes, or consistency between the two language editions cannot raise the proof level, coverage, or novelty assessment.

An editorial consistency check compared the theorem and lemma numbers, all 27 numbered formulas, parameter domains, endpoint cases, source links, commands, hash domains, and material evidential limitations across the two complete editions. Both retain `SELF_CHECKED`, `NO_ISSUES_FOUND`, historical `UNKNOWN`, and `POTENTIALLY_NEW` as of 2026-10-21, together with the usage limit, missing materials, global formalization gap, and absent external certification. This bilingual check is not a new mathematical review.
