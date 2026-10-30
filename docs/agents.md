# Configure Solve agents

English | [简体中文](agents.cn.md)

[Usage](usage.md) · [Research groups](solve-teams.md) · [Model configuration](configuration.md)

Open **Agent configuration** from the local workspace, or append `/agents` to the address printed by `mathlottery serve`. Set the number of slots, then configure each slot separately. For example:

| Slot | Agent execution | Authentication / billing |
| --- | --- | --- |
| 1 | Codex agent | ChatGPT login / subscription allowance |
| 2 | Codex agent | `RESEARCH_API_KEY_A` / OpenAI API billing |
| 3 | API agent (Responses) | `RESEARCH_API_KEY_B` / API billing |
| 4 | Codex agent | Separate ChatGPT login / subscription allowance |

Each slot has its own model and reasoning settings. Use a model and effort supported by that account or API endpoint. A configured name alone does not establish availability.

## Set up and use the slots

1. Choose the number of agents and the execution engine for each card.
2. For **Codex agent**, choose **ChatGPT login** or **API Key**. Subscription login: save, then sign in from that slot's card and authorize on the official page. API Key: supply the **environment variable name**, not its value; no device sign-in is needed. Both run the same Codex native tools and persistent sessions. Changing authentication requires a new task and does not erase the other login.
3. For **API agent (Responses)**, enter the endpoint, model and **environment variable name**, not the key itself. For either API-key option, set the variable in the terminal used to launch MathLottery and restart the server after changing its environment. The page reports whether a variable is present; this is not a successful API connection test.
4. Save, return to **Solve**, and enable **Use configured agent slots**. The saved number of slots supplies the parallelism cap. Set the group cap and research budget, then start solving.

For example, to enter a key without echoing it or putting it in shell command history:

```bash
read -rsp 'API key: ' RESEARCH_API_KEY_A
export RESEARCH_API_KEY_A
mathlottery serve
```

Codex API authentication uses the official OpenAI endpoint and preserves the Codex harness. The independent API agent remains available for vendor extensions. Its endpoint must implement the Responses features MathLottery uses, including background responses, retrieval, cancellation and the configured tools. An API key or OpenAI-compatible Chat Completions endpoint alone is not enough; a future DeepSeek or other protocol integration needs the corresponding adapter. See [provider compatibility](configuration.md#providers).

The supervisor uses slot 1 before the research round; wrap-up also uses slot 1 after the researchers stop. These calls count toward the task budget. They do not create a fifth simultaneous caller when four slots are configured. The supervisor may leave slots idle or change groups, but each researcher keeps its own connection and conversation. Nested Codex agent spawning is disabled when the harness enforces an explicit parallelism cap.

## Saved tasks and privacy

- The local roster is saved in ignored `.mathlottery/agents.json`. It contains connection settings and environment variable names, never API key values.
- Codex slot credentials and sessions stay in ignored `.mathlottery/codex-accounts/<slot-id>/`. The ordinary MathLottery account remains in `.mathlottery/codex-home`; personal CLI/IDE login is separate. Nothing is copied between these identities.
- Codex API sessions use `.mathlottery/codex-api-accounts/<slot-id>/`, or `.mathlottery/codex-api-home` outside the roster. Keys are supplied from the environment at execution time, not stored in these homes. The selected key variable is part of the saved route, and missing keys produce an error without falling back to a subscription login.
- Starting Solve freezes its slot configuration. Later roster edits apply to new tasks. Resume uses the saved routes; changing groups or budget does not move a conversation to another account. To change the roster or its size, start a new Solve task.
- Removing a slot from the roster does not erase its Codex login or research files. Sign out before removing it if you no longer want that login available; reusing the same slot ID reuses its local identity.
- Signing a slot into a different account can invalidate that slot's old conversations. Stop affected work before changing login, and keep its account if you intend to resume it. A missing session or rejected credential produces an error, not a fallback to another identity.
- Separate login directories do not create separate quota for the same actual account. MathLottery cannot guarantee that a usage pattern will avoid service restrictions. Authentication and quota failures pause work; the system does not rotate accounts to retry them.

Parallelism is a per-task cap. The workspace defaults to one active run; increasing `resources.max_concurrent_runs` can let separate tasks use the same slot at once. Slot configuration does not add an account-wide concurrency lock. Slot status queries release idle Codex helper processes; only pending device sign-ins retain a connection.

This follows Codex's documented [file credential storage](https://learn.chatgpt.com/docs/auth) and the API's guidance to keep [keys on the server](https://developers.openai.com/api/reference/overview).

## Terminal configuration

The browser uses the saved Agents-page roster only when explicitly selected for a new Solve; it does not silently activate YAML slots behind the task form. For terminal Solve, put equivalent slots in your ignored `config.yaml`:

```yaml
solve:
  parallel_agents: 3
  max_groups: 2
  agent_slots:
    - id: agent-1
      label: Researcher A
      backend:
        mode: codex
        execution: native
        model: null
    - id: agent-2
      label: Researcher B
      backend:
        mode: codex
        execution: native
        codex_auth: api_key
        codex_api_key_env: RESEARCH_API_KEY_A
        model: your-supported-openai-model
    - id: agent-3
      label: Researcher C
      backend:
        mode: chat
        execution: native
        model: your-supported-model
        chat:
          api_key_env: RESEARCH_API_KEY_B
          base_url: https://api.openai.com/v1
```

Use the same slot IDs as the browser to reuse their isolated logins. `parallel_agents` must equal the number of slots. Find, Verify, Organize and the composed `run` retain their normal backend configuration; slot routing applies to standalone native Solve.
