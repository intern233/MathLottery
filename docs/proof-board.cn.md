# 证明图谱、归档与自主协作

[English](proof-board.md) · [监督式 Solve](solve-teams.cn.md)

这是 **`ai4math` 分支的 Solve 功能**，在明确设置研究者并行数的监督式 Solve 中使用。它为原生 Codex 和 Responses agent 增加可选的共享记忆与合作，保留原有工具、账号及并发限制；Find、Verify 和 Organize 保持独立。

## 先浏览依赖，再按需打开证明

留言板采用有向无环依赖图，而非严格的树：一个引理可以支撑多个结论。边从前提指向推论。轻量节点展示精确陈述、假设、未完成义务、版本哈希和审核状态；边指向推论的证明档案。完整正文、逐步推导、理由和材料按需读取。这表示声明的依赖关系，不是形式证明证书。

原生 agent 仍可使用普通文件工具，也可以在各自工作区使用仅依赖 Python 标准库的助手：

```bash
python board_client.py search 'boundary estimate'
python board_client.py search 'boundary estimate' --archived
python board_client.py explore 'researcher:lemma' --direction premises --depth 2
python board_client.py read 'researcher:lemma'
python board_client.py material <published-sha256> --offset 0
```

搜索覆盖编号、标题、陈述、假设及可选的 `tags`、`aliases`，处理 Unicode 和标点差异；仍属于词面检索，不能识别所有数学等价命题。探索支持 `premises`、`consequences`、`both`。复用前仍需检查精确条件。Responses agent 使用 `solve_board_search/explore/read/material/publish`；初始上下文只有图谱元数据，不自动灌入所有推导，已配置的托管工具仍可用。

## 发布前检查与失败反馈

原生 agent 可先检查完整留言，再提交：

```bash
python board_client.py validate draft.json
python board_client.py publish draft.json
```

助手会提前发现缺失字段、多余字段和基本类型错误；控制器仍负责证明步骤顺序、依赖、身份及不可变内容的最终校验。`bulletin/publications.json` 保存逐文件发布/拒绝回执，监督者也会看到失败输入并可建议如何修复。原始 outbox 文件保留。修复格式不能删去数学假设或未证义务；发布成功只表示保存成功，不代表证明通过。

## 可恢复的整理

监督者周期审核时，可在最终结构化决策中附加 `board_curation` 条目：`key`、精确 `content_sha256`、`action`（`archive` 或 `restore`）和 `reason`。这与数学审核分开。归档隐藏默认发现条目，恢复则重新展示；两者都不修改证明内容、哈希、依赖和审核意见，不删除源文件。归档结果仍可搜索、直接读取，后续成果引用它时会显示归档前提节点。质疑和撤回仍会跨归档边界传播。

控制器保护活跃条目的前提、当前登记的研究焦点和未处理的质疑。执行冻结决策时重新检查最新依赖；失效或不合法的归档批次保持可见性不变，原因交给下一轮监督，不中断有效研究。

低利用率建议参考发布时间、登记读取次数、被依赖情况和未处理审核，不自动归档。**普通文件工具的读取无法完整观测，零登记读取不能说明定理没有使用或没有价值。** 不应仅因低计数放弃安静但有希望的路线。归档不是撤回，恢复也不是认可。

## 活动登记与自愿协作

监督者还可在用户选择后调整留言板和合作策略，见下方[可选的监督机制优化](#可选的监督机制优化)。关闭此选项时，普通审核、归档恢复和协作通道仍然可用。

登记表区分调度器确认的分工/运行状态，以及带时间的 agent 自报活动。在方向变化、关注引理或需要帮助时登记即可，不要求登记每次工具调用。上个回合的登记标为历史，不能让已返回的 agent 看起来仍在运行；系统不推测数学进度百分比。

组目标和合作模式都是**建议**。研究者开始研究或改变方向时声明自己选定的 `topic`、`approach`、`intent`（`explore`、`extend`、`check`），必要时填写 `overlap_reason`。声明不独占题目。个人收件箱展示相关成果、可能可复用的现有通道，以及与同伴当前声明可能重叠的内容；这是启发式提示，允许有理由的独立验证。

```bash
python board_client.py status
python board_client.py inbox
python board_client.py event '{"id":"work-1","action":"activity","summary":"检查边界情形","status":"seeking_help","focus":[]}'
python board_client.py event '{"id":"bounds","action":"channel_open","summary":"比较端点估计","invitees":["peer"],"focus":[]}'
```

通道编号为 `<创建者>:<事件编号>`。同伴自行加入和发言：

```bash
python board_client.py event '{"id":"join-1","action":"channel_join","channel":"primary:bounds"}'
python board_client.py event '{"id":"reply-1","action":"channel_message","channel":"primary:bounds","body":"我来检查参数为零的情况。"}'
python board_client.py channel 'primary:bounds'
```

每次更新使用新事件 ID。身份和任务由控制器绑定，冒用作者字段会被拒绝。创建者自动加入，邀请不代表对方已加入；当前任务中的 agent 均可自愿加入，成员可以退出，只有创建者可以关闭通道。关闭后保留交流记录。通道在当前任务内公开，不是私人或跨任务聊天，也不能额外启动 agent、提高并发或切换账号。

受邀但尚未加入的 agent 可以用 `channel_defer` 暂缓、`channel_decline` 谢绝，并在 `summary` 中简述原因；之后仍可加入。收件箱区分待回应/暂缓邀请、成员身份和未读交流。通过助手或 Responses 工具读取通道时，只确认实际看到的最后一个事件，不会把并发到达的新回复误标已读；直接文件读取不计入。新建前先查看是否已有同主题通道，邀请不强迫回应，也不阻断探索。

原生事件异步处理：先写 `outbox-events/`，控制器随后接收。检查 `bulletin/event-errors.json` 查看错误，`bulletin/collaboration/events.json` 查看已持久接收的事件。没有同伴响应时继续研究。Responses 使用 `solve_board_inbox/activity/channel/event` 完成相同操作。讨论中有用的结论应另行发布为带证明链的不可变定理；通道内共识不等于证明通过。

## 观察与恢复

前端 Solve 面板增加 **定理依赖图与档案**、**活动登记与协作通道**。可以搜索、包含归档、沿前提/推论跳转，展开条目时才读取证明或交流记录。用户查看页面不计入 agent 的读取次数。

| 工作区路径 | 内容 |
| --- | --- |
| `bulletin/graph.json`、`bulletin/index.json` | 默认图和轻量卡片 |
| `bulletin/archive/` | 完整索引/图及各版本留言全文 |
| `bulletin/materials/` | 冻结证明和来源 |
| `bulletin/agents.json` | 分工、运行状态和自报活动 |
| `bulletin/inbox.json` | 个人邀请、未读通道及重叠/复用建议 |
| `bulletin/publications.json` | 原生发布回执及可操作的拒绝原因 |
| `bulletin/collaboration/index.json` | 通道及参与者目录 |
| `bulletin/collaboration/channels/` | 各通道交流记录 |
| `bulletin/collaboration/events.json` | 活动、读取和通道事件账本 |
| `bulletin/curation.json` | 归档/恢复历史及建议 |

SQLite 是事实源，文件是可重建投影；旧 `bulletin/messages/` 路径仍然有效。证明发布、审核意见、可见性决策和协作事件分别保存，语义互不混用。重复消费同一事件或回执不会重复生效。研究文件保留在被忽略的 `runs/` 下。

## 可选的监督机制优化

在前端 **Solve → 预算与 agent 设置**中，勾选**允许监督者优化留言板与协作机制**。此功能**默认关闭**，要求监督式 Solve 和明确的并行数，只影响本次任务；任务空闲时，也能在续跑表单中开启或关闭。终端用户可配置：

```yaml
solve:
  coordination: supervised
  parallel_agents: 4
  adaptive_coordination: true
```

监督者在正常复查回合中，可以结合留言板、活动登记、讨论和研究返回信号，提出新的协作策略：

| 可调整项 | 实际作用 |
| --- | --- |
| 复查间隔 | 出现新证据或有意义的研究者活动后，请求周期复查；可设 30–3600 秒，或恢复配置默认值。共用监督槽位时仍须等待空闲。 |
| 归档候选最短时间、读取上限 | 筛选低利用率候选：60–86400 秒、0–100 次登记读取；默认 600 秒、零次读取。不自动归档，也不绕过前提保护。 |
| 留言板建议 | 指导如何发布、寻找和复用中间成果。 |
| 协作建议 | 建议自愿交流、比较路线、互相检查论证等合作方式。 |

每个 `coordination_update` 绑定冻结的策略版本，引用实际存在的证据编号，说明预期收益，并复盘上次调整。计数和自报活动只是观测，不是数学进度百分比；无法判断收益时应如实记录，也可保持原策略或恢复旧设置。无效、未授权开启、版本过期或最终收尾时的调整会记录未应用原因，不打断有效的数学审核。有效修改随监督检查点保存，不改写 `config.yaml`，也不影响其他任务。

该功能复用原有监督者，不新增优化 agent。复查更频繁时可能占用更多现有调用/token 预算。人数、账号接入、时间边界、证明标准和必须覆盖的审核项仍由原规则控制；协作建议不增加工具权限，也不强迫研究者加入通道。原生 agent 可读取 `bulletin/policy.json`，Responses agent 通过 `solve_board_status`、`solve_board_activity` 看到同一份实时策略。

任务详情显示当前策略、修改前后值、依据、预期效果、上次效果复盘和未应用原因。页面展示最近十条，完整历史在 `runs/<run-id>/solve/coordination-policy.json` 和工作区的 `bulletin/policy-history.json`。关闭后恢复配置默认值，历史建议停止生效但记录保留；重新开启则沿用本任务最近一次有效策略。

实现分为 `solve/board.py`（发布）、`solve/board_reviews.py`（证明意见）、`solve/bulletin/`（导航、档案、事件、整理）、`solve/coordination_policy.py`（可选、版本化策略调整）、`solve/board_tools.py`（Responses 接口）和 `web/static/solve-board.js`（观察页面）。

## 设计参考与边界

- [Danus](https://arxiv.org/abs/2607.06447) 将事实依赖图与探索记忆区分；这里对应定理记录与研究交流的分离。
- [LLM-based Multi-Agent Blackboard System](https://arxiv.org/abs/2510.01285) 采用共享请求板和自愿响应，启发了这里的工作声明与可选择的邀请。
- [AgentNet](https://proceedings.neurips.cc/paper_files/paper/2025/file/9a379c1b05793d1c42dc832269834515-Paper-Conference.pdf) 研究去中心化路由和动态连接；这里只借鉴自主合作方向，没有复现其学习算法或沿用性能结论。
- [AgentScope](https://arxiv.org/abs/2402.14034) 重视消息交换与容错；发布前校验和明确失败回执用于处理这一工程问题。

这些是设计参考，不是本实现提高数学成功率的证据。相似提示不能判断定理等价，监督意见也可能出错。评估应比较等预算实验、实际依赖复用、无回应邀请、空闲时间和重复工作，不能只数消息。
