# 投稿候选成果

[English](README.md) | 简体中文

[项目介绍](../README.cn.md) · [使用说明](../docs/usage.cn.md) · [证据政策](../docs/evidence.cn.md)

`ai4math` 分支精选三项结果，作为后续论文准备的起点。筛选侧重论证内容、精确的无界命题和支撑证据，不代表已确认新颖性、获得专家认可或达到期刊录用标准。原先的通用展示案例仍保存在 `main` 和 Git 历史中。

这些是历史 Solve/Verify/Organize 记录，没有作为新的[监督式 Solve](../docs/solve-teams.cn.md)
效果评测重新运行。新流程的监督意见与证明留言板审核，不会追溯性地提高下列历史证据的等级。

| 结果 | 可能的数学贡献 | 已保存验证 | 论文中的定位 |
| --- | --- | --- | --- |
| [Sun beta 多项式](sun-beta-logconvexity/README.cn.md) | 全部行指标的逐系数对数凸性；加权卷积的显式正性证书 | 完整候选；最终 AI 审查 `NO_ISSUES_FOUND`、覆盖 `FULL`；Lean 主声明已重放；新颖性 `UNKNOWN` | 第一优先级，证书方法论文的主结果 |
| [三次 Franel 尾序列](franel-logconvexity/README.cn.md) | 从 $F_8$ 开始逐系数对数凸，中心指标 $n\ge9$ 的内部系数严格正 | 完整候选；AI 审查 `NO_ISSUES_FOUND`、覆盖 `FULL`；无完整 Lean 证明；新颖性 `UNKNOWN` | 考虑与 beta 合写，作为另一个应用 |
| [对合排列上的 mesh 模式](mesh-involutions/README.cn.md) | 与取逆相容的标记出现传输及轨道权重，覆盖全部 $n,k$ 的四模式等分布 | 完整书面候选；AI 审查 `NO_ISSUES_FOUND`；仅部分 Lean；新颖性 `POTENTIALLY_NEW` | 单独的组合数学论文候选 |

**初步按两篇潜在稿件准备，不把三个案例算作三篇已成立的论文。** Beta 与 Franel 的证明策略相关，但统一覆盖二者的一般定理仍待建立；若只是表面相似，就需要重新评估合写结构。Mesh 的组合论证与文献背景相对独立。

## 从报告开始

| 案例 | 中文 | English | 证明与审查 |
| --- | --- | --- | --- |
| Beta | [Markdown](sun-beta-logconvexity/organized/report.zh.md) · [PDF](sun-beta-logconvexity/organized/report.zh.pdf) | [Markdown](sun-beta-logconvexity/organized/report.en.md) · [PDF](sun-beta-logconvexity/organized/report.en.pdf) | [证明](sun-beta-logconvexity/proof.md) · [审查](sun-beta-logconvexity/review.cn.md) · [Lean 范围](sun-beta-logconvexity/formal/README.cn.md) |
| Franel | [Markdown](franel-logconvexity/organized/report.zh.md) · [PDF](franel-logconvexity/organized/report.zh.pdf) | [Markdown](franel-logconvexity/organized/report.en.md) · [PDF](franel-logconvexity/organized/report.en.pdf) | [证明](franel-logconvexity/proof.md) · [审查](franel-logconvexity/review.cn.md) |
| Mesh | [Markdown](mesh-involutions/organized/report.zh.md) · [PDF](mesh-involutions/organized/report.zh.pdf) | [Markdown](mesh-involutions/organized/report.en.md) · [PDF](mesh-involutions/organized/report.en.pdf) | [证明](mesh-involutions/proof.md) · [审查](mesh-involutions/review.cn.md) · [Lean 范围](mesh-involutions/formal/README.cn.md) |

各案例 README 说明精确命题、可能贡献、证据边界及投稿前工作。Organize 报告解释已保存的论证，不新增证明审查。证明文件保留提交时的原话，与后来审查的结论并列呈现。

## 距离正式论文还缺什么

- **Beta：**专家独立检查证明和形式声明，补回依赖锁定，更新与已有结果的比较。虽然主定理有历史重放成功记录，题意等价认证仍为 `NOT_CERTIFIED`。
- **Franel：**补回或重建缺失的证书检查器并保存新检查，核对全部系数表和边界论证。目前没有完整形式化证明。
- **Mesh：**明确对合限制带来的新贡献与已知全排列方法的区别，处理尚未读到全文的相关文献，并取得专家审查。已检查的 107 条 Lean 定理没有补上缺失的全局双射。

Beta 和 Franel 的旧记录虽有积极的书面 AI 审查，却没有已评估的结构化关键步骤路线图。运行完成、AI 审查、有限计算、形式化编译回答的是不同问题，任何一个都不能单独认证原创数学贡献。

文献判断是历史记录：beta/Franel 为 2026-10-23，mesh 为 2026-10-21。本次 2026-10-26 的编辑筛选没有重新 Solve、Verify 或检索优先权。形成论文仍需要人类作者负责，并准确说明 AI 的参与。

## 文件与来源

本目录收录完整中英文 Markdown/PDF 报告、完整提交证明、审查摘要、精简证据、证书数据及已有 Lean 源码。Beta、Franel 的公开清单区分原始来源哈希与导出文件哈希，记录固定标识别名和未附送的下载论文全文；PDF 从公开 Markdown 重新生成。Mesh 保留此前已整理的证据与部分形式化工程。

认证信息、订阅信息、个人路径、运行会话、数据库、下载论文和编译缓存不放入本目录。原始本地实验不改动；完整性检查只核对所列文件字节，不认证数学或新颖性。复现 Lean 前请阅读[资源需求](../docs/resources.cn.md)，源码体积不代表编译内存占用。
