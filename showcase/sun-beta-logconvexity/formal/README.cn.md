# 形式化源码与复现限制

[English](README.md) | 简体中文 · [案例介绍](../README.cn.md)

[`SunBeta.lean`](SunBeta.lean) 与历史成功回执中的源码逐字节相同：

```text
SHA-256: 5664f90350aa84b61f78d8bcc10741591852bc1572f5dbc3f1fb9c0675170aa3
Lean: 4.35.0
Declaration: SunBeta.beta_coeffwise_logconvex
Status: KERNEL_REPLAYED
Axioms: propext, Classical.choice, Quot.sound
```

[证据索引](../organized/handoff/index.json)保留完整声明类型、源码哈希对应关系、首轮失败及后来的成功回执。声明涉及所有自然数 $n\ge1$、$d\ge0$ 和本文件定义的多项式系数；与原自然语言猜想的外部等价认证仍为 `NOT_CERTIFIED`。

**这里不是一个锁定依赖、可以独立直接构建的 Lake 工程。** 冻结材料没有 `lean-toolchain` 和 `lake-manifest.json`，不能把其他 showcase 的 mathlib 版本直接当成本次历史检查使用的依赖。应补回原环境，或明确记录新选环境并单独生成新的重放证据。

复现顺序：

1. 核对源码哈希，阅读定义及目标定理。
2. 补回实际 mathlib 版本，在独立工作区准备 Lean 4.35.0；执行 Lake 钩子前检查依赖文件。
3. 编译未修改的源码，查看定理类型及公理依赖，再做内核重放，将命令、版本、日志和源码哈希保存为新证据。
4. 独立检查题意对应关系与数学论证；编译不判断新颖性。

报告材料中的历史 `check.py` 是依赖特定缓存布局的编译辅助脚本，不是可移植的证书检查器。本次仅保留其来源记录，没有执行。内存与磁盘规划见[资源说明](../../../docs/resources.cn.md)。历史首轮检查曾超过资源限额；此次整理没有重新编译。
