# 三次 Franel 多项式尾序列的逐系数对数凸性

[English](README.md) | 简体中文

[投稿候选成果](../README.cn.md) · [项目介绍](../../README.cn.md)

**同篇论文的另一项候选结果。** 这份完整书面候选与 [Sun beta 结果](../sun-beta-logconvexity/README.cn.md) 使用相关的正性证书策略。优先考虑在专家复核、并确实提炼共同框架后，作为方法论文的第二个应用；目前不把它当作可以直接投稿的定理，新颖性仍为 **UNKNOWN**。

## 精确命题

令 $q$ 为形式变量，定义

$$
F_n(q)=\sum_{k=0}^{n}\binom nk^3q^k,\qquad
c_{n,d}=[q^d]\bigl(F_{n-1}(q)F_{n+1}(q)-F_n(q)^2\bigr).
$$

候选声称，对全部整数 $n\ge9$、$d\ge0$，

$$
c_{n,d}>0\quad(1\le d\le2n-1),\qquad
c_{n,d}=0\quad(d=0,\ d=2n,\ \text{或 }d>2n).
$$

因此尾序列 $(F_n)_{n\ge8}$ 逐系数对数凸。**中心指标从 9 开始，不是 8。** 目标为 [Sun 的定日期论文 arXiv:2505.02767v4](https://arxiv.org/abs/2505.02767v4) 中 Conjecture 1.1(i) 的第一项，不覆盖该猜想的全部多项式族。

存档文献检查日期为 2026-10-23。原文紧邻之前的 “remains open” 指的是另一个 beta 序列，不能移用于 Franel。历史问题状态为 `UNKNOWN`，具体来源获取问题和检索范围限制仍保留。

## 阅读顺序

1. [完整提交证明](proof.md)，含大次数和小次数情形的全部证书表。
2. 专家报告：[中文 Markdown](organized/report.zh.md) · [中文 PDF](organized/report.zh.pdf) · [English Markdown](organized/report.en.md) · [English PDF](organized/report.en.pdf)。
3. [审查摘要](review.cn.md)与[完整历史审查](organized/handoff/candidate-1.review.json)。
4. [专家交接入口](organized/handoff/START_HERE.zh.md)、[证据索引](organized/handoff/index.json)和[验证摘要](verification.json)。

证明保留提交时原文，包括其中对补充检查脚本的引用。这些脚本**不在**冻结报告包中；完整系数表在包内，但这里不宣称可以一条命令重放证书检查。

## 为什么选择它

回文性先缩小需检查的系数范围。对全部 $n\ge d\ge16$，两个加权零和式和四个显式正系数多项式给出正项和公式；对 $1\le d\le15$，十五条多项式恒等式覆盖无界 $n$，不是只测试有限个 $n$。

它为加权卷积修正提供了另一个有内容的应用。论文需要解释修正项及证书的构造、与 beta 论证的关系，以及方法到底覆盖哪些对象。使用相近术语不等于已经证明一般定理，也不足以单独成为拆分论文的依据。

## 证据与待完成事项

| 项目 | 已保存证据 |
| --- | --- |
| Solve 声称范围 | 对此精确尾序列命题为 `COMPLETE` |
| 独立 AI 审查 | `NO_ISSUES_FOUND`；原题覆盖 `FULL` |
| 候选保存等级 | `SELF_CHECKED` |
| Lean | 没有完整形式证明，也没有成功形式执行回执 |
| 结构化关键步骤覆盖 | 旧记录未评估，未保存结构化证明路线图 |
| 新颖性 | 最终字段 `UNKNOWN`；模型报告的 `POTENTIALLY_NEW` 未被提升为最终结论 |
| 外部专家审查 | 无 |

投稿前应补回或独立重建缺失的证书检查器，记录新的检查结果；核对全部表格、归一化、端点及严格正性；比较相近多项式对数凸定理，并处理具体文献缺口。完成这些数学和复现检查后，再考虑 Lean 形式化。本次导出没有新增数学验证或新颖性检索。

[公开清单](organized/manifest.json)记录来源哈希、公开文件哈希、编辑及省略。本地任务标识替换为固定别名，PDF 从公开 Markdown 重新生成，不附下载的论文全文或原始运行文件。运行 `python organized/handoff/check_files.py` 仅检查公开文件完整性。
