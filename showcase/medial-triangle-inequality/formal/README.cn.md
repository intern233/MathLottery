# Lean 形式化

[English](README.md) | 简体中文

[案例介绍](../README.cn.md) · [全部结果样本](../../README.cn.md)

本项目形式化 Zeng–Fei–Yang Conjecture 5（原文印刷页 51），覆盖全部正实权重和全部正整数指数。完整数学证明见 [proof.md](../proof.md)，实测记录和文献限制见 [实验报告](../README.cn.md)。

主定理 `ZengFeiYang.conjecture5_original` 使用欧氏平面 `EuclideanSpace ℝ (Fin 2)`、非退化条件 `AffineIndependent ℝ ![A,B,C]` 及真实三边中点的凸包内部。`conjecture5_closed` 还证明边界情形，并适用于任意实内积空间；没有把中间所需距离界当作假设。

- `MedialGeometry.lean`：中线恒等式和凸性导出的几何距离界。
- `MedialAlgebra.lean`：所有指数的严格幂和界和最大权重的组合。
- `Conjecture5.lean`：完整命题、原题推论、类型与公理输出。

版本固定为 Lean 4.35.0 和 mathlib 提交 `56a005855ea17e0b0958f73ec801ae140b0a1679`。安装官方 Elan 后，从本目录运行：

```sh
lake update
lake exe cache get
lake build
lake env lean Conjecture5.lean
```

`lake update` 获取固定提交及其依赖；所需网络访问只用于下载工具链和依赖，不上传证明。最后一个命令打印主定理类型及传递公理，预期仅有 `propext`、`Classical.choice`、`Quot.sound`。

已经完成构建时，可额外运行 Lean 自带的内核重放工具：

```sh
lake env leanchecker --verbose MedialAlgebra MedialGeometry Conjecture5
lake env leanchecker --fresh --verbose Conjecture5
```

明确给出模块名；该版本 `leanchecker` 没有 `--help` 参数。`--fresh` 还重放导入依赖，可能需要数分钟。它仍使用 Lean 的内核，不是另一种证明助手。

研究环境和初步路线由主控助手准备，求解会话完成形式化，独立审查会话重新编译。三份 Lean 源码与被冻结的候选完全一致；本说明是整理后的可移植文档，不含本机路径、账号、会话编号或编译产物。

本展示目录只包含源码和固定版本信息。运行复现命令会另行下载较大的依赖；本次整理核对源码与既有验证版本一致，没有重新构建工具链。
