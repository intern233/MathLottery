# Formal source and reproduction limits

English | [简体中文](README.cn.md) · [Case overview](../README.md)

[`SunBeta.lean`](SunBeta.lean) is the exact source named by the historical successful receipt:

```text
SHA-256: 5664f90350aa84b61f78d8bcc10741591852bc1572f5dbc3f1fb9c0675170aa3
Lean: 4.35.0
Declaration: SunBeta.beta_coeffwise_logconvex
Status: KERNEL_REPLAYED
Axioms: propext, Classical.choice, Quot.sound
```

The full declaration type, source-hash matching, failed first attempt and later successful receipt are in the [evidence index](../organized/handoff/index.json). The declaration concerns all natural $n\ge1$ and $d\ge0$ and the coefficients of the polynomial defined in this file; external equivalence certification with the natural-language conjecture remains `NOT_CERTIFIED`.

**This is not a pinned standalone Lake project.** The frozen material includes no `lean-toolchain` or `lake-manifest.json`. In particular, a neighboring showcase's mathlib pin must not be silently presented as the dependency used for this check. Recover the actual environment or document a newly chosen environment and a new replay separately.

Reproduction order:

1. Check the file hash and inspect the definition and target theorem.
2. Recover the recorded mathlib dependency revision and prepare Lean 4.35.0 in a separate workspace; inspect dependency files before executing Lake hooks.
3. Compile this unchanged source and inspect the target theorem's type and axioms. Then perform kernel replay, recording commands, versions, logs and source hashes as new evidence.
4. Independently check statement alignment and the mathematical argument; compilation does not determine novelty.

The historical `check.py` included among the report materials is a cache-dependent compilation helper, not a portable certificate checker. It is retained as provenance and is not run by this export. The [resource guide](../../../docs/resources.md) explains memory and disk planning. The first historical attempt exceeded its resource allowance; no new compilation was performed while preparing this showcase.
