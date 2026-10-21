# 部分 Lean 形式化

[English](README.md) | 简体中文

[案例介绍](../README.cn.md) · [全部结果样本](../../README.cn.md)

这些源码对应[普通证明（英文）](../proof.md)的部分步骤，不能作为整个猜想的证书。Mesh.correctedConjecture 定义了原题的四模式、所有 n、k 的计数等式。

| 模块 | 已编译通过的内容 |
|---|---|
| MeshDefinitions、MeshStructure | 真实有限排列、严格空矩形、L/M/Q 等价与局部图结构 |
| MeshSymmetry | 取逆和反向补足；同底层模式的全分布等式 |
| MeshComponents、MeshRotation | 单分量外部条件的双向刻画、旋转及逆变换 |
| MeshEquivariance、MeshNesting、MeshCompatibility | 单分量取逆相容性、逐边公式、嵌套与关键兼容条件 |
| MeshOrbitCounting、MeshPolynomial、MeshTransport | 有限轨道加权、真实出现集合的多项式系数、等变边映射保权 |
| MeshReduction | 假设存在全局标记双射时，推出完整原题 |
| MeshPartial | 导入上述模块并打印 107 条定理的公理及关键类型 |

仍需从任意标记出现子集构造唯一分量分解，组合所有分量旋转，并证明全局对象与边的等变性，才能实际构造 MarkedTransport n。当前条件定理的类型是：

```lean
Mesh.correctedConjecture_of_markedTransport :
  (∀ n : ℕ, Nonempty (Mesh.MarkedTransport n)) → Mesh.correctedConjecture
```

这个前提尚未被证明，也没有被声明为公理。107 条定理的传递公理至多为 propext、Classical.choice、Quot.sound；不使用证明占位符或原生计算绕过内核。源码与已经编译、重放的版本逐字一致，哈希见 [verification.json](../verification.json)。

Lean 固定为 4.35.0，mathlib 固定为 56a005855ea17e0b0958f73ec801ae140b0a1679。安装官方 Elan 后在本目录执行：

```sh
lake update
lake exe cache get
lake build
lake env lean MeshPartial.lean
lake env leanchecker --fresh --verbose MeshPartial
```

复现时需要另行下载较大的工具链和依赖，本目录只保存源码和固定版本信息。上述构建与重放曾在独立构建目录通过；本次展示整理只核对源码一致性，没有重新下载依赖。重放仍使用 Lean 自身内核，且只验证实际存在的部分结果和显式前提。

前八个证明模块由原生求解会话生成；MeshOrbitCounting、MeshPolynomial 的编译错误由主控修复，MeshTransport、MeshReduction、MeshPartial 由主控补充。尚无独立 AI 形式化审查或外部专家认证。
