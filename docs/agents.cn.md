# 配置 Solve 的各个 agent

[English](agents.md) | 简体中文

[使用说明](usage.cn.md) · [研究组调度](solve-teams.cn.md) · [模型配置](configuration.cn.md)

在本地工作台打开 **Agent 配置**，也可以在 `mathlottery serve` 打印的地址后加 `/agents`。设置槽位数量，再分别配置每个 agent。例如：

| 槽位 | Agent 执行方式 | 鉴权与计费 |
| --- | --- | --- |
| 1 | Codex agent | ChatGPT 登录，使用订阅额度 |
| 2 | Codex agent | 环境变量 `RESEARCH_API_KEY_A`，OpenAI API 计费 |
| 3 | API agent（Responses） | 环境变量 `RESEARCH_API_KEY_B`，API 计费 |
| 4 | Codex agent | 独立 ChatGPT 登录，使用订阅额度 |

各槽位可以选不同模型和推理设置；填写的模型与强度需要该账号或 API 端点实际支持，配置了名称不代表一定可用。

## 配置与使用

1. 设置 agent 数量，在各卡片选择执行引擎。
2. **Codex agent**：选择 **ChatGPT 登录**或 **API Key**。订阅登录先保存配置，再在对应卡片登录，到官方页面完成授权；API Key 只填写**环境变量名**，不需要设备码登录。两种方式使用相同的 Codex 原生工具与持续会话。改变鉴权需要新建任务，不会清除另一种登录。
3. **API agent（Responses）**：填写端点、模型和 **API Key 的环境变量名**，不要填写密钥本身。两种 API Key 方式都需要在启动 MathLottery 的终端设置变量；修改环境后重启服务。页面显示变量是否存在，并不表示 API 连接已经验证成功。
4. 保存后返回 **Solve**，勾选**使用已配置的 agent 槽位**。并行数由已保存的槽位数量确定；再设置组数上限和预算，启动求解。

例如，可以通过以下方式输入密钥，不回显输入，也不把密钥写进 shell 命令历史：

```bash
read -rsp 'API key: ' RESEARCH_API_KEY_A
export RESEARCH_API_KEY_A
mathlottery serve
```

Codex API 鉴权连接 OpenAI 官方端点，保留原生 Codex harness。独立 API agent 继续用于厂商扩展：端点需要支持 MathLottery 使用的 Responses 功能，包括后台响应、查询、取消及配置的工具。监督式 Solve 还需要函数调用及 `function_call_output` 续接，供实时留言板使用。只有 API Key 或兼容 OpenAI 的 Chat Completions 接口还不够；未来接入 DeepSeek 等其他协议时需要相应适配器。见[提供方兼容要求](configuration.cn.md#providers)。

监督者与主研究者顺序复用槽位 1。新监督式任务会审核研究信号并定期请求复查留言板；复查等待槽位 1 空闲，其他研究者可以继续。时间到达后等待当前尝试返回，再监督整理。见[监督式 Solve](solve-teams.cn.md)。这些调用计入任务预算；配置 4 个槽位时，不会因为监督再增加第 5 个同时调用者。监督可以让槽位闲置或重新分组，但每个研究者保留自己的接入和会话。显式限制并行数时，禁用 Codex 内部再启动额外 agent，避免绕过上限。

## 已有任务与隐私

- 配置保存在被 Git 忽略的 `.mathlottery/agents.json`，只保存接入设置和环境变量名，不保存 API Key 的值。
- 各 Codex 槽位的认证与会话位于被忽略的 `.mathlottery/codex-accounts/<slot-id>/`；原来的 MathLottery 账号仍在 `.mathlottery/codex-home`。个人 CLI/IDE 登录也保持独立，不在这些目录之间复制认证。
- Codex API 槽位的会话使用 `.mathlottery/codex-api-accounts/<slot-id>/`，普通任务使用 `.mathlottery/codex-api-home`。运行时从环境变量获取密钥，不把密钥保存在这些目录。环境变量名属于任务接入快照，缺少密钥会报错，不会改用订阅登录。
- Solve 启动时保存槽位配置快照。之后修改配置页只影响新任务；续跑使用已保存的接入。调整分组或预算不会把会话转交另一个账号。要更换槽位配置或数量，请新建 Solve 任务。
- 从配置中移除槽位，不会删除该槽位的 Codex 登录或研究文件。不再需要该登录时，请先退出再移除；再次使用同一槽位 ID，会复用其本地身份。
- 把同一槽位切换到其他账号，可能使旧账号的会话无法继续。修改登录前停止相关工作；需要续跑时保留原账号。找不到会话或认证失败会报错，不会自动改用其他身份。
- 同一个实际账号登录到不同槽位，仍共享该账号的额度；登录隔离不能保证不触发服务方限制。认证或额度失败会暂停，不会通过轮换账号自动重试。

并行数是单个任务的上限。工作区默认只运行一个任务；调高 `resources.max_concurrent_runs` 后，不同任务可能同时使用同一槽位，目前没有跨任务的账号并发锁。槽位状态查询结束后会释放空闲的 Codex 辅助进程，只有等待设备码登录时保留连接。

认证实现参考 Codex 官方的[文件凭据存储](https://learn.chatgpt.com/docs/auth)及 API 的[服务端密钥管理说明](https://developers.openai.com/api/reference/overview)。

## 终端配置

新建网页 Solve 只有在显式勾选后，才使用 Agent 配置页保存的槽位，不会绕过任务表单自动启用 YAML 中的槽位。终端 Solve 可以在被忽略的 `config.yaml` 中填写等效配置：

```yaml
solve:
  coordination: supervised
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

使用与网页相同的槽位 ID，就会使用对应的隔离登录。`parallel_agents` 必须等于槽位数。Find、Verify、Organize 和组合命令 `run` 仍使用通常的后端配置；槽位路由只作用于独立的原生 Solve。
