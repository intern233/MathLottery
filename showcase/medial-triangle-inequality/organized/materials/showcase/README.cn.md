# 中位三角形内动点的加权距离幂不等式

[English](README.md) | 简体中文

[全部结果样本](../../../../README.cn.md) · [项目介绍](../../../../../README.cn.md)

本例给出 Zeng–Fei–Yang **Conjecture 5 的完整证明与实际通过检查的 Lean 形式化**，并把结论扩展到中位三角形的边界。独立 AI 审查未发现问题；新颖性仍为 **UNKNOWN**，不能据此确认首次解决当前开放问题。

原题来自《Tracing the Origins and Generalizations of a Class of Moving Point Inequalities》，2026 年第 19 卷第 1 期，印刷页 51，在线发布日期 2025-11-30。[出版记录](https://ijopcm.zuj.edu.jo/index.php/IJOPCM/article/view/56) · [原文](https://ijopcm.zuj.edu.jo/index.php/IJOPCM/article/download/56/43)

对非退化三角形 ABC，令 a = BC ≥ b = CA ≥ c = AB；P 在三边中点组成的三角形内，x、y、z 为任意正实数，n 为任意正整数。结论为：

```text
x·PAⁿ + y·PBⁿ + z·PCⁿ < max(x,y)·((b+c)/2)ⁿ + max(y,z)·aⁿ
```

证明由几何距离界、任意正整数的严格幂和界、最大权重组合三步构成。Lean 主定理从真实欧氏距离、三边中点和凸包出发，没有将中间所需的距离不等式直接当作假设。

- [完整数学证明及原题对应表](proof.md)
- [独立审查摘要](review.cn.md)
- [Lean 项目与复现说明](formal/README.cn.md)
- [主定理源码](formal/Conjecture5.lean)
- [验证摘要及文件哈希](verification.json)

原生求解、独立重新编译、Lean 内核重放及单独 Lake 构建均有成功记录。原题和形式陈述的对应已由独立 AI 对照来源检查，但没有外部数学专家认证。2025 年前作和 2026 年 9 月后续论文的部分全文未取得，因此开放状态和优先权保留不确定性。系统候选等级仍为 SELF_CHECKED，与这里列出的实际 Lean 检查证据分别记录。
