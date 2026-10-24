# Partial Lean formalization

English | [简体中文](README.cn.md)

[Case overview](../README.md) · [All result samples](../../../../../README.md)

These sources formalize parts of the [written proof](../proof.md); they are not a certificate for the entire conjecture. `Mesh.correctedConjecture` defines the original four-pattern counting equality for all n and k.

| Modules | Content that has compiled successfully |
| --- | --- |
| MeshDefinitions, MeshStructure | Actual finite permutations, strict empty rectangles, L/M/Q equivalences, and local graph structure |
| MeshSymmetry | Inversion and reverse complement; full distribution equalities for patterns with the same underlying permutation |
| MeshComponents, MeshRotation | Necessary and sufficient external conditions for a single component, rotation, and its inverse |
| MeshEquivariance, MeshNesting, MeshCompatibility | Single-component compatibility with inversion, edgewise formulas, nesting, and key compatibility conditions |
| MeshOrbitCounting, MeshPolynomial, MeshTransport | Finite orbit weights, polynomial coefficients of actual occurrence sets, and weight preservation by equivariant edge maps |
| MeshReduction | Derivation of the full original statement assuming a global marked bijection exists |
| MeshPartial | Imports the modules above and prints axioms for 107 theorems and key types |

Constructing `MarkedTransport n` still requires a unique component decomposition for arbitrary marked-occurrence subsets, assembly of all component rotations, and global equivariance for objects and edges. The current conditional theorem is:

```lean
Mesh.correctedConjecture_of_markedTransport :
  (∀ n : ℕ, Nonempty (Mesh.MarkedTransport n)) → Mesh.correctedConjecture
```

This premise has not been proved or declared as an axiom. The transitive axioms of the 107 theorems are at most `propext`, `Classical.choice`, and `Quot.sound`; there are no proof placeholders or native computations bypassing the kernel. The sources match the compiled and replayed versions byte for byte; see [verification.json](../verification.json) for hashes.

Lean is pinned to 4.35.0 and mathlib to commit `56a005855ea17e0b0958f73ec801ae140b0a1679`. After installing official Elan, run from this directory:

```sh
lake update
lake exe cache get
lake build
lake env lean MeshPartial.lean
lake env leanchecker --fresh --verbose MeshPartial
```

Reproduction downloads large toolchains and dependencies separately; this directory contains only sources and version pins. The build and replay above previously passed in a separate build directory. Preparing this showcase checked source consistency without downloading dependencies again. Replay still uses Lean's own kernel and verifies only the existing partial results and their explicit premises.

The first eight proof modules came from the native solving session. The controller fixed compilation errors in `MeshOrbitCounting` and `MeshPolynomial`, and added `MeshTransport`, `MeshReduction`, and `MeshPartial`. There has been no separate AI review of the formalization or external expert certification.
