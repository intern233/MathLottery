# Lean formalization

English | [简体中文](README.cn.md)

[Case overview](../README.md) · [All result samples](../../README.md)

This project formalizes Zeng–Fei–Yang's Conjecture 5, on printed page 51 of the original paper, for all positive real weights and all positive integer exponents. See the [complete written proof (Chinese original)](../proof.md) and the [case overview](../README.md) for experimental evidence and literature limits.

The main theorem `ZengFeiYang.conjecture5_original` uses the Euclidean plane `EuclideanSpace ℝ (Fin 2)`, the nondegeneracy condition `AffineIndependent ℝ ![A,B,C]`, and the interior of the convex hull of the actual side midpoints. `conjecture5_closed` also covers the boundary and applies to any real inner product space. Intermediate distance bounds are proved rather than assumed.

- `MedialGeometry.lean`: geometric distance bounds from median identities and convexity.
- `MedialAlgebra.lean`: strict power-sum bounds for all exponents and the combination of maximum weights.
- `Conjecture5.lean`: full statement, the original-problem corollary, and type and axiom output.

Versions are pinned to Lean 4.35.0 and mathlib commit `56a005855ea17e0b0958f73ec801ae140b0a1679`. After installing official Elan, run from this directory:

```sh
lake update
lake exe cache get
lake build
lake env lean Conjecture5.lean
```

`lake update` retrieves the pinned commit and its dependencies. Network access is used to download toolchains and dependencies, not to upload proofs. The last command prints the main theorem's type and transitive axioms, expected to be only `propext`, `Classical.choice`, and `Quot.sound`.

After a successful build, you can also run Lean's kernel replay tool:

```sh
lake env leanchecker --verbose MedialAlgebra MedialGeometry Conjecture5
lake env leanchecker --fresh --verbose Conjecture5
```

Provide module names explicitly; this version of `leanchecker` has no `--help` option. `--fresh` also replays imported dependencies and may take several minutes. It still uses Lean's kernel, not a different proof assistant.

The controller prepared the research environment and an initial approach. The solving session completed the formalization, and a separate review session recompiled it. The three Lean sources match the frozen candidate exactly. This is portable documentation without local machine paths, account details, session IDs, or build products.

This showcase directory contains only sources and version pins. Reproduction commands download large dependencies separately. Preparing the showcase checked source consistency with the previously verified version without rebuilding the toolchain.
