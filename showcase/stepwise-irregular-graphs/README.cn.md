# 阶梯不规则图度数序列猜想的反例

[English](README.md) | 简体中文

[全部结果样本](../README.cn.md) · [项目介绍](../../README.cn.md)

**专家报告：** [中文 Markdown](organized/report.zh.md) · [中文 PDF](organized/report.zh.pdf) · [English Markdown](organized/report.en.md) · [English PDF](organized/report.en.pdf)。两版均完整整理已有证明与证据，不提升验证或新颖性等级。[公开材料清单](organized/manifest.json)。

本例给出 Bera–Paul–Subramanian《Some properties of stepwise irregular graphs》中 **Conjecture 1 的完整反例**。独立 AI 审查结论为 **NO_ISSUES_FOUND**；新颖性为 **UNKNOWN**，没有 Lean 形式化。

原题刊于 EJGTA 14(1) (2026)，猜想在印刷页 223，简单连通图的约定和 SI 定义在页 216。[原论文](https://www.ejgta.org/index.php/ejgta/article/download/1077/pdf_357)

SI 图要求每条边两端的度数恰好相差 1。反例度数序列为：

```text
(6,6,6,6, 5,5,5,5,5,5, 4, 3, 2,2,2, 1)
```

它满足原猜想全部前提，也有普通简单连通二部图实现，但不可能有 SI 实现：三个度为 2 的顶点需要向度为 1 或 3 的顶点连出 6 条边；后两类顶点的总度数只有 4，矛盾。这排除所有 SI 实现，不依赖有限搜索，也不需要连通性。

- [完整反例证明与邻接表](proof.md)
- [机器可读的 16 顶点证书](certificate.json)
- [标准库证书检查器](verify_certificate.py)
- [独立审查摘要](review.cn.md)
- [验证摘要及文件哈希](verification.json)

用 Python 3.11+ 在本目录核对有限证书：

```sh
python verify_certificate.py certificate.json
```

预期得到 16 个顶点、34 条边、奇偶度数和各为 34，以及 SI 关联边需求 6 大于可用邻点总度数 4。程序检查整数和显式图数据，普遍不可实现性由书面证明承担。

独立审查发现所用局部容量不等式已有 2022 年文献先例；部分近期相关全文不可访问，无法确证对该猜想的首次反驳。系统候选等级保留 SELF_CHECKED。
