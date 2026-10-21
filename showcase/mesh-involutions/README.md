# Equidistribution of four mesh patterns on involutions

English | [简体中文](README.cn.md)

[All result samples](../README.md) · [Project overview](../../README.md)

This case presents a complete written candidate proof of Fang–Fu–Kitaev–Li–Su–Sun's corrected Conjecture 1. The separate AI review returned **NO_ISSUES_FOUND**, and the novelty assessment is **POTENTIALLY_NEW**. Lean formalization is currently partial.

The problem appears on printed page 17 of the 2026-10-11 revision of *On mesh patterns of short length: Equidistribution and enumeration*. [Original paper](https://arxiv.org/abs/2606.14367v2)

An involution is a permutation satisfying π² = id. Let R = {(0,0),(1,1),(1,2),(2,1)} and R′ = {(2,2),(1,1),(1,0),(0,1)}. In their printed order, the four patterns are (12,R), (12,R′), (21,R′), and (21,R), with occurrences defined using strict empty rectangles. The proof covers every n,k ≥ 0: the number of involutions of size n with exactly k occurrences is the same for all four patterns.

The proof rotates star components in marked-occurrence graphs into path components, establishes compatibility with permutation inversion, and preserves transposition edge by edge. It assigns separate weights to orbits of sizes 1 and 2 in transposition-invariant marked objects, then recovers every occurrence count through generating polynomials. The star/path method has prior literature precedent, acknowledged in the proof. The new argument focuses on the involution restriction and orbit weights.

- [Complete written proof](proof.md)
- [Separate review summary and literature limits](review.md)
- [Lean sources, coverage, and reproduction instructions](formal/README.md)
- [Verification summary and file hashes](verification.json)

Recorded checks include compilation of 107 Lean theorems, axiom dependency inspection, and fresh kernel replay; all passed. A global equivariant bijection for arbitrary marked subsets has not been constructed in Lean, so **there is no unconditional Lean theorem for the complete original conjecture**. The separate review of the written proof did not cover later Lean additions.

Native discovery and separate verification of the written proof completed. Native solving stopped during formalization because of a usage limit, without submitting a final candidate. The controller submitted a snapshot of the written proof for separate verification and later continued partial formalization locally. The stored candidate level remains `SELF_CHECKED`, without promotion to full formal certification.
