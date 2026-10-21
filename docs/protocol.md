# Legacy structured protocol 1.0

English | [简体中文](protocol.cn.md)

[Project overview](../README.md) · [Usage](usage.md) · [Result showcase](../showcase/README.md)

> This document describes the legacy structured protocol for `--execution structured`, old checkpoints, and offline demos. The default native mode uses ordinary Markdown and milestone registration; see [installation and usage](usage.md).

This compatibility protocol uses the explicitly named manual backend or Codex with `--execution structured`. It is not the Chat API protocol. Every task includes a complete JSON Schema in `tasks/<task-id>/response.schema.json`. The same Pydantic protocol validates both legacy transports. Codex also passes that schema to the official CLI's structured-output option.

The minimum manual response is:

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

Replace the IDs and phase with the current prompt. Submit JSON only. Extra keys, invalid actions, malformed `arguments_json`, wrong phase, and stale task IDs are rejected. Omitted optional fields receive defaults for manual input; the Work schema requires all fields with null/empty values where appropriate.

| Action | Additional payload / effect |
| --- | --- |
| `SELECT_PROBLEM` | FIND only; requires `problem`; optional ordered `shortlist` |
| `SUBMIT_CANDIDATE` | SOLVE only; requires `candidate.claim`, `candidate.proof` |
| `REVIEW` | VERIFY only; requires structured `review` |
| `STOP` | Stops successfully with a report, even if no proof was found; no tool calls |
| Other research actions | REASON, SEARCH, DECOMPOSE, PROPOSE_LEMMA, PROVE_LEMMA, TEST_CASES, FIND_COUNTEREXAMPLE, RUN_CODE, FORMALIZE, REVISE, CHANGE_STRATEGY |

`tools` contains at most six entries. Arguments are encoded as a JSON string so the external output schema remains closed and stable:

```json
{
  "name": "python_exec",
  "arguments_json": "{\"code\":\"print(sum(range(11)))\"}"
}
```

Supported names and arguments:

| Tool | Arguments |
| --- | --- |
| `web_search` | `query`, optional `limit` (1–10); keyword search over arXiv metadata |
| `web_fetch` | `url`; public HTTP(S) HTML/text, no credentials or private destinations |
| `python_exec` | `code`; isolated Python, SymPy available |
| `sympy_compute` | `expression`, `operation` = simplify / expand / factor / diff |
| `lean_check` | `proof`; proof body for a user-pinned `formal_target` |
| `read_artifact` | `path`; relative to this run's `artifacts/` |
| `write_artifact` | `path`, `content`; same restricted directory |
| `search_memory` | `query`; bounded matching entries |

Artifacts and memory cannot be read by the independent reviewer. Tool failures are data in the next prompt; no tool returns a simulated success. A tool request's result is delivered in a later task, so do not claim to have already seen it.

Memory entries contain `kind`, `content`, `status`, `source_iteration`, `dependencies`, and `evidence`. Model-written entries are stored as `unverified`; the harness controls validation status. A solver summary is retained when no explicit memory update was supplied.

Reviews distinguish `truth_assessment`, `proof_assessment`, `issues`, `evidence`, `novelty`, `novelty_notes`, and `novelty_references`. `NO_ISSUES_FOUND` is an LLM review, not a mathematical proof. `ISSUES_FOUND` without concrete issue/evidence does not confer `REJECTED`; it still returns the agent to revision. Novelty without references to sources actually retrieved during review is reset to `UNKNOWN`.

`examples/chat_response.template.json` is an editable SOLVE-stage example. For a full schema and all nested fields, use the task-generated file rather than retyping the protocol by hand.
