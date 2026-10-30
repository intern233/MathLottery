# 接入与模型配置

[English](configuration.md) | 简体中文

[快速上手与命令](usage.cn.md) · [资源与 Lean](resources.cn.md) · [结果样本](../showcase/README.cn.md)

本文用于完成[浏览器快速上手](usage.cn.md#本地浏览器工作台)后的配置，或直接使用终端时查阅。两种入口共用所选工作区的 `config.yaml`；agent 接入方式与找题、求解、验真分别选择。`mathlottery init` 生成本地默认配置，[config.example.yaml](../config.example.yaml) 提供更完整的字段参考，其中的示例模型设置需要按账号调整。只修改需要的部分，本地设置保持私有。

[模型](#models) · [API 提供方](#providers) · [Codex 账号与工具](#account) · [网络](#network) · [预算](#budgets) · [证据](#evidence) · [恢复](#recovery) · [兼容模式](#legacy)

<a id="models"></a>
## 模型与配置优先级

Codex 的模型 ID 与思考强度分别设置：

```yaml
backend:
  mode: codex
  model: gpt-6-astra
  reasoning_effort: max
```

请使用账号实际支持的模型和强度；上面是配置示例，不保证模型权限。浏览器的「本次任务的模型」读取所选提供方的目录，也允许手填未列出的模型。Codex 订阅目录提供声明支持的思考档位；Responses 目录可能只有模型 ID。Codex API 鉴权使用配置或手填的模型 ID，不查询订阅目录。缺失的能力信息仍记为未知。点击「刷新模型列表」更新目录；列出模型不等于已测试推理、额度或工具可用性。

| 字段 | 含义与未设置时的行为 |
| --- | --- |
| `backend.mode` | `codex` 使用官方 Codex 会话；`chat` 调用 Responses。 |
| `backend.codex_auth` | Codex 的鉴权：`chatgpt`（默认，订阅登录）或 `api_key`（OpenAI API 计费），都使用原生 Codex agent。 |
| `backend.codex_api_key_env` | Codex API 使用的环境变量**名称**，默认 `OPENAI_API_KEY`；不要填写密钥本身。 |
| `backend.provider` | 可选配置 ID：`codex`、`chat` 或自定义名称，如 `research-api`。省略或设为 `null` 时使用该 mode 的内置接入。 |
| `backend.model` | 准确的模型 ID，不附加 ` max` 等强度。`null` 时 Codex 使用独立目录的默认值；内置 Chat 可读取 `OPENAI_MODEL`。自定义 API 配置必须明确指定模型。 |
| `backend.reasoning_effort` | 提供方支持的可选值，如 `max`；`null` 交给后端默认处理。 |
| `backend.chat.reasoning_mode` | 可选 Responses 字段：`pro`、`standard`，或 `null` 表示不发送。只在 `chat` 下使用，且需要提供方/模型支持。 |

不要把 `pro` 写入 `reasoning_effort`，也不要自行给模型名加 `-pro`。API 设置不保证与 ChatGPT 网页产品具有相同行为。不支持的组合会报错，系统不会静默换模型或降低强度。报告区分请求设置与后端实际返回的设置。

**新任务：**程序默认值 → `config.yaml`（或全局 `--config` 指定的文件）→ 显式 CLI/网页任务参数。例如 `mathlottery --config alternate.yaml find` 使用指定文件。`--backend`、`--model`、`--reasoning-effort`、`--reasoning-mode` 覆盖对应字段，不改写配置文件。手动换后端时，清除原先不兼容的模型/强度/模式；网页切换提供方会重置这些字段。

**已有任务：**`resume` 从保存的配置快照开始。后来修改 `config.yaml` 或提供方配置，不会把已保存会话转向其他接口。网页续接保留模型设置；CLI 续接支持显式覆盖模型/后端。必须先恢复待处理调用，详见[恢复](#recovery)。

<a id="providers"></a>
## API 凭据与其他提供方

执行方式与鉴权分别选择。**Codex agent** 可以使用 ChatGPT 订阅登录或 OpenAI API Key；**API agent** 保留独立的 Responses harness，供兼容提供方及未来的协议适配使用，配置中的历史名称仍是 `chat`。使用 API Key 不代表一定走独立 API harness。

### Codex agent 使用 OpenAI API Key

保留 `mode: codex`，即可继续使用 Codex 的原生终端、文件、工具与会话续接：

```yaml
backend:
  mode: codex
  execution: native
  codex_auth: api_key
  codex_api_key_env: OPENAI_API_KEY
  model: your-api-model-id
  reasoning_effort: null
```

在启动服务或 CLI 的终端设置对应环境变量，输入方法见下方。Agent 配置页选择 **Codex agent → API Key**。此模式走 OpenAI 官方 API 计费，不消耗 ChatGPT 订阅额度；不需要设备码登录，也不通过 `codex login` 保存密钥。MathLottery 只向 Codex 执行进程传入所选密钥，并清除其 shell 工具环境中的已知凭据值。部分依赖 ChatGPT 工作区的集成仍可能要求订阅登录，但原生终端与文件工具保留。见[官方认证说明](https://learn.chatgpt.com/docs/auth)。

API 模式的 Codex 状态保存在 `.mathlottery/codex-api-home`，各槽位使用 `.mathlottery/codex-api-accounts/<slot-id>`，与订阅登录及会话分开。续跑使用原任务的鉴权选择和环境变量名；需要更换接入时新建任务。检测到环境变量仅表示本地已配置，不代表账号权限或模型可用性已经验证。API 模型 ID 请手动填写，不复用订阅账号的模型目录。

### 独立 API agent（Responses）

内置 `chat` 接入使用 OpenAI Responses API，需要单独的 API Key 和 API 计费；MathLottery 的 Codex 登录不会提供这份凭据。

```yaml
backend:
  mode: chat
  provider: chat
  model: your-api-model-id
  reasoning_effort: null
  chat:
    api_key_env: OPENAI_API_KEY
    base_url: https://api.openai.com/v1
    reasoning_mode: null
    poll_interval_seconds: 1
    request_timeout_seconds: 30
    tools:
      - type: web_search
      - type: code_interpreter
        container: {type: auto}
```

替换 `your-api-model-id`，并使用该 API 模型支持的工具。在 Bash 中可用以下方式输入密钥，避免将其写入命令历史，再从该终端启动 MathLottery：

```bash
read -rs -p 'OpenAI API key: ' OPENAI_API_KEY
export OPENAI_API_KEY
mathlottery doctor
```

`doctor` 检查本地配置，不发起收费模型调用，也不能确认 API 权限。密钥只从环境变量读取，不保存进配置或报告。`.env` 虽被 Git 忽略，但**不会自动加载**，请通过 Shell 或可信的环境管理工具设置。只有内置 `chat` 会在 `backend.model` 未设置时读取 `OPENAI_MODEL`。

使用其他提供方时，在本地配置中替换以下占位内容：

```yaml
backend:
  mode: chat
  provider: research-api
  model: provider-model-id
  reasoning_effort: null
  chat:
    reasoning_mode: null

model_providers:
  research-api:
    label: Research API
    transport: responses
    chat:
      base_url: https://api.example.invalid/v1
      api_key_env: RESEARCH_API_KEY
      tools: []
    models:
      - id: provider-model-id
        label: Research model
        reasoning_efforts: null
    reasoning_modes: []
```

在启动终端中导出 `RESEARCH_API_KEY`。每个配置必须显式提供 `base_url`、`api_key_env`、`tools`，不继承 OpenAI 凭据或工具。**`tools: []` 不启用托管搜索或代码执行。** 依赖 Find/Verify 查询当前文献前，应配置提供方实际支持的工具。网页只选择已配置的 ID，不接收 API Key，也不要求输入接口地址。真实私有端点和凭据不要进入版本控制。

非空的可选 `models` 列表用于本地目录，代替请求 `/models`；省略后可在线获取目录。每个模型的 `reasoning_efforts` 省略或为 `null` 表示未知，`[]` 表示未声明支持任何强度。要声明支持，可以设置 `reasoning_efforts: [low, high]` 和 `default_reasoning_effort: high`。只有提供方支持独立的 Responses mode 字段时才声明 `reasoning_modes`。在网页中选择命名配置，或在文件中设置 `backend.provider`；CLI 没有 `--provider` 参数。

**兼容需要完整的 Responses 生命周期：**后台请求、保存响应、查询、取消、`previous_response_id` 续接，以及配置的工具。只有 `/chat/completions` 的接口不够。尚未实现 Anthropic/Gemini 原生协议，以及需要客户端执行的自定义函数工具。新协议需显式增加研究调用和模型目录适配器；失败不会触发提供方、认证或计费方式切换。托管 Code Interpreter 无法直接访问本地文件或本机安装的 Lean 环境。

<a id="account"></a>
## Codex 账号隔离与原生工具

并行 Solve 可以为每个研究者指定不同接入。[Agent 配置页](agents.cn.md)管理 Codex 鉴权与独立 API 设置。订阅槽位登录位于 `.mathlottery/codex-accounts/<slot-id>`，与下文所述的默认账号分开。本节登录步骤适用于 `codex_auth: chatgpt`。

请把官方 Codex CLI 安装在运行 MathLottery 的同一个 Linux/WSL 环境，并确认该环境中 `codex --version` 可用。安装方式见[官方 CLI 文档](https://learn.chatgpt.com/docs/cli)和 [Codex 仓库](https://github.com/openai/codex)。WSL 的 `PATH` 若继承了 Windows 启动器，可能选错程序；无法启动时检查 `command -v node`、`command -v npm`、`command -v codex`。

即使普通 Codex 已登录，也需要在浏览器「MathLottery 账号」面板登录一次。设备码授权可能需要先在 ChatGPT 安全设置中启用，或由管理员开启。授权在官方页面完成，不在 MathLottery 中输入密码。[官方认证说明](https://learn.chatgpt.com/docs/auth)

纯终端使用时，先激活 MathLottery 环境、安装好 `codex`，再**在目标项目/工作区根目录**执行：

```bash
python - <<'PY'
from pathlib import Path
import subprocess
from mathlottery.providers.identity import CodexIdentity

identity = CodexIdentity(Path.cwd())
subprocess.run(
    ["codex", *identity.overrides(), "login", "--device-auth"],
    env=identity.environment(),
    check=True,
)
PY
```

按打印的提示完成一次授权。此示例通过 MathLottery 的身份工具，只设置子进程环境；不要全局导出 `CODEX_HOME`。不经过此工具的普通 `codex login` 操作的是你平时使用的 Codex 登录。网页、MathLottery CLI 与后台任务共用工作区的隔离登录。

| 项目 | 作用范围 |
| --- | --- |
| 登录与会话 | `.mathlottery/codex-home`，强制文件凭据存储，POSIX 下目录仅当前用户可访问。不复制个人 Codex 凭据、配置或会话，也不以个人登录兜底。 |
| 切换账号 / 退出登录 | 只作用于当前 MathLottery 工作区。网页需要确认，本工作区有 Codex 任务运行时禁止变更。切换先退出，若取消或未完成新授权，此工作区保持退出状态。 |
| 订阅额度 | 使用同一个 ChatGPT 账号仍共享该账号额度，隔离登录不会增加额度。 |
| MCP、插件与 Codex 默认配置 | 配置在独立的 `.mathlottery/codex-home/config.toml` 及私有目录中，不会自动继承个人 CLI/IDE 设置。 |

前端只收到脱敏账号信息与待授权的设备码状态，不接收账号令牌。请保持 `.mathlottery/` 私有。独立目录机制使用 Codex 官方支持的 [`CODEX_HOME` 设置](https://learn.chatgpt.com/docs/config-file/environment-variables)。

可选原生设置：

```yaml
backend:
  mode: codex
  execution: native
  codex_command: codex
  native_web_search: live
  native_network_access: true
  native_multi_agent: null
  native_memories: null
```

`native_web_search` 支持 `live`、`cached`、`disabled`。多 agent 和记忆设置支持 `true`、`false`、`null`；`null` 继承独立 Codex/运行时默认值。连续的主研究者负责最终结果，辅助 agent 可能增加用量。独立审查者始终禁用记忆。这些开关不安装工具，也不保证账号支持。原生 Codex 保留自身上下文/压缩机制与 workspace-write 沙箱，不施加旧版逐动作 JSON 协议或 512 MB 工具限制。`codex_command` 在运行时通过 `PATH` 查找，不保存自动发现的机器路径。

<a id="network"></a>
## 网络与代理配置

MathLottery 及其 Codex 子进程使用启动终端的环境。IDE 插件能联网，不代表该终端具有相同代理设置。需要代理时，配置终端环境，或创建工作区中已被忽略的 `.mathlottery/network.json`：

```json
{
  "HTTP_PROXY": "http://proxy.example.invalid:8080",
  "HTTPS_PROXY": "http://proxy.example.invalid:8080",
  "NO_PROXY": "localhost,127.0.0.1,::1"
}
```

将占位地址改成你可访问的代理，运行 `chmod 600 .mathlottery/network.json` 限制权限。只接受 `HTTP_PROXY`、`HTTPS_PROXY`、`ALL_PROXY`、`NO_PROXY` 及其小写形式。已有环境变量优先于文件中对应的大/小写变量，包括显式空值。文件上限 16 KiB，必须是没有链接的普通文件；不要写入账号令牌或 `CODEX_HOME`。

CLI、服务与后台进程启动时加载默认值，只影响各自进程，不修改父终端、不把网络设置复制到报告，也不修改 Windows/WSL 网络。**改变服务环境或网络默认值后，要重启已有服务**；再次执行 `serve` 可能只是打印旧实例地址。已启动的研究进程保留自己的环境。状态请求超时不会清除登录，也不代表必须重新授权。

通过 `NO_PROXY` 让回环地址直连。**代理地址用于出站请求，不是浏览器工作台地址。** 界面请打开 `serve` 打印的网址：

- 默认监听 `127.0.0.1`，首选端口 `8765`。匹配的已有服务会复用；端口被占用时尝试后续端口，最多绑定 20 次。WSL 启动时若能查询到 Windows 保留端口，也会跳过它们。使用实际打印的端口，或通过 `mathlottery serve --port 9001` 选择首选端口；`--open` 请求打开浏览器。
- Windows 浏览器通常通过 WSL 转发访问打印的 `http://localhost:<port>`。排查时分别检查两侧：Linux 中用 `curl --noproxy '*' http://localhost:9001/`，Windows PowerShell 中用 `curl.exe --noproxy '*' http://localhost:9001/`；把 `9001` 换成实际端口。仅 Linux 内可访问，不能证明 Windows 浏览器可访问。
- `mathlottery serve --wsl-direct` 显式扩大监听范围并打印 WSL 直连地址，只允许回环、该 WSL 地址和 Windows 网关访问。它是可选项；`--loopback-only` 保留默认方式，不能与之同时使用。MathLottery 不会自动修改端口映射、防火墙、WSL 设置或代理配置。

其他启动错误见[排障清单](usage.cn.md#troubleshooting)。

<a id="budgets"></a>
## 预算与用量

```yaml
budget:
  max_wall_time_minutes: 180
  max_iterations: 50
  solve_until_budget_exhausted: false
  finalize_minutes: 5
  max_input_tokens: null
  max_output_tokens: null
  max_external_cost_usd: null
backend:
  native_turn_timeout_seconds: null
```

| 控制项 | 含义 |
| --- | --- |
| 活跃时间预算 | 包括研究及独立证据检查，不计暂停时间。续接时替换总上限，不是追加时间。 |
| `max_iterations` | 研究交接次数，不是每次原生工具调用，也不是完整解题尝试次数。 |
| `solve_until_budget_exhausted` | 只适用于原生独立 Solve。设为 `true` 后，每次保存候选并持续研究和自查至活动时间上限，声称完整解决后也继续。默认 `false`。 |
| `finalize_minutes` | 原生 Solve 到达时间上限后，在原研究会话执行一次收尾调用，最多额外使用这些分钟。默认 `5`，设为 `0` 关闭。原生 `run` 在 Solve 阶段到达时间上限时同样适用。 |
| 输入/输出 token 上限 | 依据后端真实返回，在调用之间检查。一次调用可能超过阈值，未报告用量保持未知。 |
| `native_turn_timeout_seconds: null` | 一次原生调用可以使用剩余总时间预算。 |
| `chat.request_timeout_seconds` | 单次 HTTP 请求超时，不是远端模型的总思考时限。 |
| `max_external_cost_usd` | 只接受 `null` 或旧版 `0`；`0` 阻止 API 计费调用，包括 Codex API 和付费 Solve 槽位；`null` 交给服务商账号控制支出，不代表免费。 |

原生 Solve 收到 `PARTIAL`、`UNKNOWN`，或仍有数学义务未完成的候选时，会保存检查点，在剩余预算内续接同一研究会话。默认只有候选同时声明 `conclude: true`、范围为 `COMPLETE` 或 `COUNTEREXAMPLE`，且 `remaining_obligations` 为空，才可提前结束独立 Solve。这只记录求解者的声称；正确性、原题覆盖和新颖性仍由 Verify 审查。`run` 可以独立审查部分候选，但即使审查通过，也不会把部分结果当作完整解答而结束研究。

在页面的预算设置或续接表单中勾选**用满求解时间预算**，独立 Solve 声称完整解决后也会继续研究和自查。它复用已保存的研究会话并保留不可变的候选历史，不会启动 Verify 或 Organize。下述其他限额和中断条件仍然有效。续接请求不指定此选项时保留原值；时间仍是累计总上限：填写 `360` 分钟表示包含此前活动耗时在内的六小时。

从 CLI 新建 Solve 任务时，可在 `config.yaml` 设置 `budget.solve_until_budget_exhausted: true`。CLI 续接沿用已保存的值；已有任务可通过页面续接表单修改此选项。

研究时间用尽后，页面显示**快速收尾中**。Agent 应停止探索，保存现有结果、支持材料、剩余义务，并明确注明部分完成、未解决等范围。收尾只有一次有时间上限的调用：例如研究预算 `360` 分钟、`finalize_minutes: 5`，表示最多额外使用五分钟收尾；收尾活动耗时和已报告用量仍会记录。提交收尾候选后结束执行，不自动启动 Verify 或 Organize，也不升级正确性或新颖性。**已收尾**只表示结果已保存，不表示原题已解决。

如果 agent 未能在收尾时限内提交结果，MathLottery 保存本地检查点摘要，明确注明“未获得 agent 收尾总结”。这个回退摘要不会补造最终证明或声称完整解决。用户主动停止、提供方错误及其他硬限制仍可中断收尾，不会为了收尾绕过这些限制。收尾时限在新建任务前通过 `config.yaml` 配置；已有任务沿用保存的配置。

常规求解过程中模型提交的 `stop` 阶段成果也只保存进展并继续；用户点击**停止任务**或使用 CLI 停止命令仍然有效。迭代或 token 限额，以及提供方额度、超时和错误，都可能在研究时间预算用尽前中断任务。增加时间不保证解决问题。这些续接与收尾规则适用于原生执行，旧版 structured 协议保留原有结束行为。

MathLottery 不估算美元成本、订阅余额或第三方工具费用，请在提供方账号中设置 API 支出限制。时间/token 预算不限制 RAM、磁盘或所有子进程。尤其 `tools.memory_mb: 512` 只用于旧版 Python 工具，不限制原生 Codex 或 Lean/Lake。增加并发或编译限额前，请看[资源控制与 Lean 用量实测](resources.cn.md)。

<a id="evidence"></a>
## 找题资料与证明证据

### 把 Find 资料带入 Solve

在网页中选择候选，或使用 `solve --from-find <find-run-id> --problem <problem-id>`，会为所选题目捕获冻结的 Find 资料，包括来源评估、研究笔记与允许的工作文件。单独 `solve --problem` 复用题目表述，不执行此资料交接。凭据存储、二进制缓存和可变会话不共享，被省略的材料会记录原因。

| `discovery` 设置 | 默认值 |
| --- | --- |
| `context_max_files` | 300 个文件 |
| `context_max_file_bytes` | 每文件 8,000,000 字节 |
| `context_max_total_bytes` | 总计 32,000,000 字节 |
| `chat_context_max_bytes` | Chat 提示内最多 256,000 字节文本 |

Codex 在 `discovery-context/` 收到冻结文件；Chat 直接收到限额内的文本，因为托管工具不能读取本机文件。Find 的判断和省略项会保留，不会因此变成证明或“问题确定未解决”的保证。

### 为独立 Verify 附加源码

**CLI 的 `verify --from-run` 复制候选，不复制求解工作区。** 浏览器中需在启动 Verify 前显式选择必要证明文件。源任务必须空闲，页面显示的候选 ID/校验值仍须匹配。文件字节被冻结并计算哈希，后续修改不影响本次审查输入。

| 证据 | 支持范围 |
| --- | --- |
| Lean/项目源码 | 求解者 `workspace/` 内的 `.lean`、`lean-toolchain`、`lakefile.toml`。 |
| 证明文本与证书 | `workspace/proof/` 或 `workspace/formal/` 下的 `.md`、`.txt`、`.json`、`.csv`、`.py`；脚本不会自动执行。 |
| 大小限制 | 最多 20 个文件，每文件 1,000,000 字节；Codex 总计 2,000,000 字节，Chat 提示内源码总计 128,000 字节。 |
| 排除内容 | 链接文件、隐藏/缓存/构建目录、凭据、求解历史和旧审查。 |

Codex 在独立审查工作区的 `submitted-evidence/` 下收到附件。结果面板还可以列出审查工作区允许下载的文件，但它们不会自动成为新审查可选的求解附件。下载的是单个文本文件，不是完整 Lean 环境压缩包。

使用独立 Lean 检查前，准备兼容的 Lean、`leanchecker`、bubblewrap、`prlimit` 和预编译库。审查者需要请求检查已附加的模块和明确命名的定理。用 `verification.lean_library_paths` 设置可信库路径；检查器不安装依赖，也不执行提交的 Lake 配置。

| `verification` 设置 | 默认限制 |
| --- | --- |
| `max_sources` / `source_timeout_seconds` | 每次阶段成果最多 12 个引用网址、60 秒收集预算；正在等待的请求使用 `tools.web_timeout_seconds`。 |
| `formal_timeout_seconds` | 总计 120 秒，可配置到 1,800 秒，仍受任务剩余时间限制。 |
| `formal_memory_mb` | 2,048 MB Lean 内部阈值；单工作线程、64 MiB 线程栈。 |
| `formal_address_space_mb` | 每进程 8,192 MB 虚拟地址空间上限，包括预留和映射内存；不是实测 RAM 或全局 RSS 上限。 |
| `formal_max_object_mb` / `formal_max_total_object_mb` | 每个编译文件 16 MiB、监测总量 960 MiB；检查后删除临时编译产物。 |

内核重放成功会记录检查过的声明与信任假设，可以支持 `PARTIALLY_VERIFIED`，不会自动认证完整的新解答。普通语言/形式陈述等价性和新颖性仍须单独判断。缺少工具、超时或资源失败表示检查未完成。完整配置、允许公理、模块布局和来源回执规则见[证据要求](evidence.cn.md)。

<a id="recovery"></a>
## 已保存会话与恢复

使用[停止、续接和报告命令](usage.cn.md#operations)继续已有工作。`.mathlottery/` 中的 SQLite 是权威状态，候选版本不可变。报告与 `metrics.json` 汇总检查点、阶段耗时、交接失败、用量和审查结论；缺失的历史测量保持未知。

- Codex 在独立目录精确续接会话。不要让其他 Codex 客户端同时驱动同一活跃会话。独立目录中不存在的会话，不能通过复制个人登录恢复。
- Chat 轮询后台响应，并通过 `previous_response_id` 续接。断线前若已保存响应 ID，恢复时取回该响应，不再创建第二次请求；创建失败且未获得 ID 时保持不确定状态，决定新建任务前先检查提供方记录。
- Stop/Ctrl+C 请求取消。已保存输出保留，但停止不保证形成完整候选或远端立即取消。切换后端前必须先恢复待处理请求。
- 关闭网页或 UI 服务后，浏览器启动的研究进程仍可继续。重启界面会重新连接保存的状态，不自动重启已退出进程。停止研究需要显式停止请求。
- 关闭或重启主机/WSL 会终止本地研究进程。重新运行 `mathlottery serve`，再续接原任务。原生 Codex 进程异常退出且存在对应资源快照时，耗时停在最后一次保存的采样，后续停机时间不计入预算；最后未采样的短暂区间保持未知。此修正不适用于可能仍在远端运行的 Chat 响应，也不补造旧任务缺失的测量。
- 托管响应/容器有保留期限，本地检查点不能重建已过期的远端上下文。外部工具副作用不保证恰好执行一次，恢复时应检查文件和回执。

`resume --message` 给原功能添加方向。CLI 切换后端时保留各后端独立的上下文 ID，并交接已记录的研究回答，不会创造完全相同的工具环境。独立审查使用新上下文，不包含求解者对话。实现细节见[架构与恢复](architecture.cn.md)。

<a id="legacy"></a>
## 兼容模式、离线演示与开发

普通研究使用 `execution: native`。`manual` 是明确命名的手动交接后端；`work` 是 `codex` 的别名，`--mode` 是 `--backend` 的别名。历史上的手动交接 `chat` 检查点恢复时仍按 manual 处理，不会静默转为收费 API 调用。

```bash
mathlottery run --backend manual --prompt 'Investigate this mathematical problem...'
mathlottery submit --run <run-id> --file response.md
```

使用旧版 JSON/工具协议时，先导入教学题目，再按生成任务的格式提交响应：

```bash
mathlottery add --file examples/odd_sum.problem.json
mathlottery run --backend manual --execution structured --problem odd-sum
mathlottery submit --run <run-id> --file response.json
```

结构见[协议说明](protocol.cn.md)。只有 `manual` 需要人工传递回答；`codex` 和 `chat` 都会自动调用 agent。

安装开发依赖后，可运行不消耗模型额度的离线检查：

```bash
mathlottery demo
mathlottery demo --case incorrect
pytest -q
ruff check .
```

演示使用固定审查素材，不测量模型数学能力。集成检查见[验证方法](local-validation.cn.md)；本地审计脚本和日志放在已忽略的 `audits/codex_audits/<timestamp>/` 目录。经过整理的小型示例放在[结果样本](../showcase/README.cn.md)。MathLottery 不会自动提交或上传研究文件。
