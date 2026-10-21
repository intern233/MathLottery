# 旧版 structured 协议 1.0

[English](protocol.md) | 简体中文

[项目介绍](../README.cn.md) · [安装与使用](usage.cn.md) · [结果样本](../showcase/README.cn.md)

> 本文描述 legacy structured 协议，仅适用于 `--execution structured`、旧检查点和离线 Demo。默认 native 模式使用普通 Markdown 与阶段成果登记，见[安装与使用](usage.cn.md)。

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

审查区分 `truth_assessment`、`proof_assessment`、`issues`、`evidence`、`novelty`、`novelty_notes` 和 `novelty_references`。`NO_ISSUES_FOUND` 代表 LLM 审查意见，不代表数学证明。缺少具体问题或证据的 `ISSUES_FOUND` 不会使候选成为 `REJECTED`，但仍会让 agent 返回修改。新颖性判断若没有引用审查过程中实际获取的来源，会重置为 `UNKNOWN`。

`examples/chat_response.template.json` 是可编辑的 SOLVE 阶段示例。完整 Schema 及全部嵌套字段应以任务生成的文件为准，无需手工重写协议。
