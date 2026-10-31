# 旧版 structured 协议 1.0

[English](protocol.md) | 简体中文

[项目介绍](../README.cn.md) · [安装与使用](usage.cn.md) · [结果样本](../showcase/README.cn.md)

> 本文描述 legacy structured 协议，仅适用于 `--execution structured`、旧检查点和离线 Demo。默认 native 模式使用普通 Markdown 与阶段成果登记，见[安装与使用](usage.cn.md)。

新的[监督式 Solve](solve-teams.cn.md)使用原生研究会话、研究者阶段成果、
`solve-supervision` 决策检查点，以及独立的证明留言板 schema，不使用下文逐动作的
兼容协议。它要求独立原生 Solve 和明确的并行数；structured/manual 保留原行为。

此兼容协议用于明确命名的 manual 后端，或使用 `--execution structured` 的 Codex，不是 Chat API 的协议。每个任务在 `tasks/<task-id>/response.schema.json` 中提供完整 JSON Schema。两个旧版后端由同一 Pydantic 协议校验；Codex 还会把该 Schema 传给官方 CLI 的结构化输出选项。

最小手动响应如下：

```json
{
  "protocol_version": "1.0",
  "run_id": "run-0123456789ab",
  "task_id": "task-0123456789ab",
  "phase": "SOLVE",
  "action": "REASON",
  "summary": "Visible mathematical progress, not hidden chain of thought."
}
```

将 ID 和 phase 替换为当前提示中的值，只提交 JSON。额外字段、无效动作、格式错误的 `arguments_json`、错误阶段和过期任务 ID 都会被拒绝。手动输入中省略的可选字段使用默认值；Work Schema 要求所有字段齐全，适当填写 null 或空值。

| 动作 | 附加内容或效果 |
| --- | --- |
| `SELECT_PROBLEM` | 仅 FIND；必须提供 `problem`，可选有序 `shortlist` |
| `SUBMIT_CANDIDATE` | 仅 SOLVE；必须提供 `candidate.claim`、`candidate.proof` |
| `REVIEW` | 仅 VERIFY；必须提供结构化 `review` |
| `STOP` | 即使未找到证明也成功结束并生成报告；不调用工具 |
| 其他研究动作 | REASON、SEARCH、DECOMPOSE、PROPOSE_LEMMA、PROVE_LEMMA、TEST_CASES、FIND_COUNTEREXAMPLE、RUN_CODE、FORMALIZE、REVISE、CHANGE_STRATEGY |

`tools` 最多包含六项。参数编码为 JSON 字符串，以保持外部输出 Schema 封闭且稳定：

```json
{
  "name": "python_exec",
  "arguments_json": "{\"code\":\"print(sum(range(11)))\"}"
}
```

支持的名称和参数：

| 工具 | 参数 |
| --- | --- |
| `web_search` | `query`，可选 `limit`（1–10）；搜索 arXiv 元数据关键词 |
| `web_fetch` | `url`；公开 HTTP(S) HTML 或文本，不使用凭据，不访问私有地址 |
| `python_exec` | `code`；隔离 Python，可使用 SymPy |
| `sympy_compute` | `expression`，`operation` = simplify / expand / factor / diff |
| `lean_check` | `proof`；用户固定的 `formal_target` 对应的证明正文 |
| `read_artifact` | `path`；相对于本次运行的 `artifacts/` |
| `write_artifact` | `path`、`content`；同一受限目录 |
| `search_memory` | `query`；数量受限的匹配条目 |

独立审查者不能读取产物和记忆。工具失败会作为下一条提示中的数据返回，不会模拟成功。工具请求的结果在后续任务中交付，因此不能声称已经看到了尚未返回的结果。

记忆条目包含 `kind`、`content`、`status`、`source_iteration`、`dependencies` 和 `evidence`。模型写入的条目标为 `unverified`，验证状态由运行框架控制。没有显式更新记忆时，会保留求解者摘要。

审查分别记录证明正确性、`original_problem_coverage`、剩余证明义务与新颖性。新的肯定审查需要具体 `checks`；空泛通过、只有有限实验或关键步骤仍未解决时，结论改为 `INCONCLUSIVE`。`NO_ISSUES_FOUND` 始终是 LLM 判断；拒绝需要具体矛盾检查或带证据的问题。新颖性与开放状态需要独立核对的 `citations` 和 `literature_search` 覆盖，不再仅凭网址列表。详见同样适用于原生阶段成果的[证据规则](evidence.cn.md)。旧记录继续可读，缺失字段默认为未评估。

新版审查还提交 `proof_steps`（编号、依赖和检查编号）及六类 `statement_alignment`。`proof_coverage` 由控制器重算，不采信模型填写的评估结果。文献 `obstacles` 有固定编号，需要证据才能消除；`comparisons` 明确已有定理与候选的假设及结论。继承的 `review_literature` 将待核查事项带入新 Verify，不包含旧结论。缺失字段保证旧记录可读，但不能支持新提交的肯定审查。详见[逐项覆盖与文献障碍](evidence.cn.md#逐项覆盖与可跟进的文献障碍)。

`examples/chat_response.template.json` 是可编辑的 SOLVE 阶段示例。完整 Schema 及全部嵌套字段应以任务生成的文件为准，无需手工重写协议。
