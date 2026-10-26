# Sun 的 beta 多项式：逐系数对数凸性

[English](README.md) | 简体中文

[投稿候选成果](../README.cn.md) · [项目介绍](../../README.cn.md)

**优先准备的论文主结果。** 这项候选完整覆盖一个明确的多项式不等式猜想，包含显式证书论证和历史 Lean 内核重放记录，适合作为“加权卷积的正性证书”方向的起点。新颖性仍为 **UNKNOWN**；入选展示不等于已达到录用标准。

## 精确命题

令 $q$ 为形式变量，定义

$$
\beta_n(q)=\sum_{k=0}^{n}\binom nk^2\binom{n+k}{k}q^k\in\mathbb Z[q].
$$

候选声称

$$
[q^d]\bigl(\beta_{n-1}(q)\beta_{n+1}(q)-\beta_n(q)^2\bigr)\ge0
\qquad(n\ge1,\ d\ge0).
$$

这是对无界整数指标的逐系数非负性，包含全部边界情形。只证明某些实数 $q$ 下的点值不等式是不够的。

存档原始来源为 [arXiv:1104.3856v8](https://arxiv.org/abs/1104.3856v8) 的 Conjecture 4.7 第一项。已保存的文献审查还指出，日期为 2026-02-10 的 [arXiv:2505.02767v4](https://arxiv.org/abs/2505.02767v4) 有明确开放状态声明。存档检索日期为 2026-10-23；本次整理不更新检索，也不认证首次性。

## 阅读顺序

1. [完整提交证明](proof.md)，含全部证书表。保留提交时原文，其当时的状态描述与后来的审查结论分开读取。
2. 专家报告：[中文 Markdown](organized/report.zh.md) · [中文 PDF](organized/report.zh.pdf) · [English Markdown](organized/report.en.md) · [English PDF](organized/report.en.pdf)。
3. [审查摘要](review.cn.md)与[全部历史审查](organized/handoff/candidate-1.review.json)。
4. [Lean 源码与复现限制](formal/README.cn.md)、[正系数表](certificates/CertificateTable.md)和[证书数据](certificates/certificates.json)。
5. [专家交接入口](organized/handoff/START_HERE.zh.md)、[证据索引](organized/handoff/index.json)与[验证摘要](verification.json)。

## 值得发展成论文的部分

证明将目标系数化为对称加权卷积，用两个加权和为零的修正项消去中心贡献，再按奇偶情形建立产生非负项的多项式恒等式。两个主要证书分别含 334 和 415 个正系数；边界和支撑外的系数单独处理。

可能的贡献在于：针对精确 beta 权重构造并证明这些证书，以及在确实成立的前提下提炼可读、可复用的方法。系数表的规模、模型消耗和 Lean 编译本身不代表数学贡献大小。[Franel 案例](../franel-logconvexity/README.cn.md) 的路线相关，可考虑作为同篇论文的另一个应用；本目录**尚未证明**统一覆盖二者的一般定理。

## 证据与待完成事项

| 项目 | 已保存证据 |
| --- | --- |
| Solve 声称范围 | `COMPLETE` |
| 最新独立 AI 审查 | `NO_ISSUES_FOUND`；原题覆盖 `FULL` |
| 候选保存等级 | `PARTIALLY_VERIFIED` |
| 形式声明 | `SunBeta.beta_coeffwise_logconvex`；`KERNEL_REPLAYED` |
| 公开 Lean 源码 | 与成功回执所列源码逐字节一致 |
| 外部题意等价认证 | `NOT_CERTIFIED` |
| 结构化关键步骤覆盖 | 旧记录未评估，未保存结构化证明路线图 |
| 新颖性 | `UNKNOWN`；没有外部专家审查 |

投稿前需要：

- 请专家检查系数归约、两个零和式、证书恒等式及边界，并对照原猜想与 Lean 声明。
- 补回实际使用的依赖锁文件。冻结报告没有 `lean-toolchain` 和 `lake-manifest.json`；仅记录 Lean 版本不能固定导入的 mathlib 版本。
- 处理审查保留的具体来源访问缺口，更新与相近多项式对数凸结果的比较。某日仍被列为猜想，不等于已经确认当前首次性。
- 在论文中解释证书如何构造、方法能覆盖什么；先评估与 Franel 合写，再决定是否拆分。

第一次形式检查曾因内存消耗失败，后续成功重放不能抹去这段历史。本次导出没有重新编译 Lean、重新审查证明或检索文献。编译前请阅读[资源需求](../../docs/resources.cn.md)。

## 公开副本

[公开清单](organized/manifest.json)区分原始来源哈希与导出文件哈希。本地任务标识改为固定别名，PDF 从公开 Markdown 重新生成；不附下载的论文全文、原始 PDF、认证信息、会话及缓存。原始实验档案保持不变。运行 `python organized/handoff/check_files.py` 只核对清单中文件的完整性，不验证数学结论。
