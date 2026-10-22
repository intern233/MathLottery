# 安装与使用

[English](usage.md) | 简体中文

[项目介绍](../README.cn.md) · [结果样本](../showcase/README.cn.md)

所有命令都在 MathLottery 项目根目录执行。三个研究功能与 agent 后端相互独立：

| 功能 | 命令 | 结果 |
| --- | --- | --- |
| 找题 | `find` | 排序后的题目、来源、未解状态证据和推荐理由 |
| 求解 | `solve` | 持续探索记录、部分成果和候选证明 |
| 验真 | `verify` | 独立审查结论、问题清单、证据和新颖性判断 |
| 完整流程 | `run` | 找题 → 求解 → 审查，有问题时返回原研究会话 |

新任务自动读取项目根目录的 config.yaml，使用其中的后端、模型、思考设置和预算。运行命令只需指定任务和问题。

## 环境准备

~~~bash
conda env create -f environment.yml
conda activate mathlottery
cp config.example.yaml config.yaml
mathlottery doctor
~~~

已有环境可运行 `python -m pip install -e '.[dev,research]'`。研究依赖包含 NumPy、SciPy、Matplotlib、pypdf、SymPy/mpmath；Lean 是需要另外安装的可选工具。`mathlottery init` 也可初始化本地配置与存储。

## 本地浏览器工作台

完成环境准备后，启动本地界面：

~~~bash
conda activate mathlottery
mathlottery serve
~~~

终端会打印工作区、实际端口与浏览器地址，优先使用 `8765`。再次启动时，若同一工作区和配置已有兼容的 MathLottery 服务，会直接显示它的地址；若端口被其他服务占用，则自动尝试下一个端口，最多尝试绑定 20 次。在 WSL 中，Windows 网络工具可用时，启动过程还会读取并跳过 Windows 保留的 TCP 端口范围。使用 `mathlottery serve --open` 可自动打开页面，`--port 9001` 可指定其他优先端口。

以 editable 方式安装时，即使从其他项目目录运行，`serve` 也会定位 MathLottery 源码项目。显式使用 `mathlottery --root ./research-workspace serve` 可选择其他数据工作区，其他 CLI 命令原有的根目录行为保持一致。无需 Node.js 构建或单独安装前端。界面支持中英文，首次使用时跟随浏览器语言。

默认监听 `127.0.0.1`，WSL 中也一样。Windows 浏览器打开终端打印的 **Windows** `http://localhost:<端口>` 地址，由 WSL 的 localhost 转发连接到 Linux。请使用实际打印的端口，因为 Linux 能绑定的端口仍可能被 Windows 保留。出现访问故障时，分别检查 Linux 和 Windows 两侧。[微软 WSL 网络说明](https://learn.microsoft.com/en-us/windows/wsl/networking)

在 NAT 模式 WSL 中，也可显式运行 `mathlottery serve --wsl-direct`，启用并打印通过 WSL 地址直连的入口。该选项扩大监听范围，并将请求来源限制为本地回环、WSL 自身和 Windows 网关；不会自动启用。`--loopback-only` 继续兼容，用于明确选择默认回环行为，不能与 `--wsl-direct` 同时使用。启动过程不修改 WSL 配置、代理、端口转发规则或防火墙。

1. **找题**：填写选题条件、可选的来源网址与候选题数。结果出现后，查看陈述、来源与状态证据，点击「求解这道题」。
2. **求解**：选择已有题目或输入问题陈述。结果区域展示候选证明；「验真最新候选」会准备一项独立审查任务。
3. **验真**：选择已有任务的最新候选，或提供题目与证明。审查结论、问题、证据和新颖性与候选的证明等级分别展示。

可在选填的「任务说明」中要求 Lean 形式化、编译检查或指定研究方向，从第一轮就交给 agent，同时保留所选题目的原始陈述。

新任务读取当前 `config.yaml`。展开「模型与预算」可临时指定本次任务的后端、模型、思考设置和预算，不会修改配置文件。Codex 使用当前 MathLottery 工作区独立的登录与工具配置，Chat 使用 API 凭据及其额度。点击开始后会真实调用选定的后端。

使用 Codex 时，「开始」与「继续研究」需要先在 MathLottery 账号面板完成 ChatGPT 登录。服务器会在保存新任务或启动续接进程前再次检查：新任务使用本次选择的后端，续接使用任务原先保存的后端。CLI 不可用、登录待完成或 Codex 仅有 API Key 认证时，会显示具体处理提示，不启动后台进程。这些检查不修改本地 Codex 凭据，也不阻止 Chat API 任务。登录就绪不代表服务商一定接受后续模型请求；真实执行错误仍会显示在任务中。

页面可见时，历史和详情每两秒刷新，展示检查点、已保存的可见输出、token 用量、候选证明与报告。原生 agent 的长回合可能暂时没有新输出。可以下载报告，也可用「停止任务」请求取消并保留已有进度；停止不保证 agent 能完成正在撰写的正式提交。用户主动停止和活动时间预算耗尽会显示不同原因，服务商执行失败仍按错误展示。「继续 / 补充方向」续接原有会话；预算字段替换总上限，并沿用任务原先保存的模型设置。已经完成的任务需要补充新方向才能继续。

研究或审查工作区产生 Lean 文件后，「结果」中还会列出可下载的 `.lean`、`lean-toolchain` 和 `lakefile.toml` 文本文件。单个下载限制为 1 MB，不提供链接文件、隐藏目录、依赖缓存或构建产物；文件列表有数量限制，未完整列出时会提示。下载只包含所选文本，不是完整 Lean 项目压缩包，现代浏览器会保留源文件名；本地重建项目时应按页面显示的相对路径保存。文件存在不代表 Lean 已通过检查，也不代表形式陈述与公开问题等价或成果具有新颖性。展示和下载这些文件都不会改变候选的证明等级。

验真已有候选时，可以主动勾选其研究工作区中的证明源码，默认不选任何文件。表单保留页面显示的候选 ID 和校验值；提交前候选发生变化时，需要刷新来源再提交。源任务必须已停止运行。提交时会冻结所选文件的内容，并记录路径、大小和 SHA256；此后源文件发生变化，也不会改变这次审查的输入。验真结果中会单独展示这份清单。

最多选择 20 个文件，单文件不超过 1 MB；原生 Codex 的总上限为 2 MB。原生 Chat 会把实际源码文本放入提示，总上限为 128 KB。Codex 会在独立审查工作区的 `submitted-evidence/` 下收到源码。日志、旧审查、依赖缓存和登录数据不会一起交接。请包含证明需要的小型本地 Lean 依赖；此功能不打包或安装 mathlib。源码只作为不可信证据供审查者检查和复算，不会自动提高证明等级。

结果摘要分别展示证明等级、最近一次 agent 审查、登记的问题状态和新颖性。任务已完成或 agent 未发现问题，都不代表完整形式验证通过，也不代表确认首次解决了开放问题。

关闭浏览器或界面服务后，研究进程仍会运行。需要停止研究时，使用「停止任务」或 `mathlottery stop <run-id>`。重新启动界面会读取同一份本地状态，不会自动重启任务。界面与 CLI 共用 `problems/`、`runs/` 和 `.mathlottery/`，每项任务的后台进程记录位于 `runs/<run-id>/web/`。完整 `run` 流程与旧版手动交接继续使用 CLI。

浏览器写操作需要同源请求令牌，只提供打包的静态资源与选定的任务数据，agent 输出按文本展示。这仍是本地工作台；连接 Codex 账号不等于为网页提供多用户访问控制。

### 使用 ChatGPT 账号登录

「MathLottery 账号」面板管理当前工作区独立的登录状态。在这里登录、切换或退出，都不改变平时使用的本地 Codex CLI / IDE 登录。MathLottery 浏览器界面、MathLottery CLI 命令和后台研究进程共用当前工作区的独立登录。

即使本地 Codex 已登录，也需要在 MathLottery 中登录一次。点击「使用 ChatGPT 账号登录」，打开官方链接并输入一次性验证码，在 OpenAI 页面完成认证。可以选择同一个 ChatGPT 账号，也可以使用不同账号。登录状态隔离不会增加额度：使用同一账号的会话仍共用该账号的订阅额度。设备码登录可能需要先在 ChatGPT 安全设置中开启，或由工作区管理员允许。[官方认证说明](https://learn.chatgpt.com/docs/auth)

登录后，面板会在信息可用时展示脱敏邮箱与订阅类型。「切换账号」先退出当前 MathLottery 工作区的登录，再发起新的设备码登录；取消或未完成新授权后，MathLottery 保持退出状态，需要重新登录才能恢复使用。「退出登录」只退出当前工作区。两个操作都会要求确认，当前工作区有 Codex 任务运行时会被阻止。读取状态和普通登录不会自动替换已有的 MathLottery 登录。ChatGPT 网页的浏览器会话独立管理。

MathLottery 只为自己的 Codex 子进程设置 `CODEX_HOME`，固定指向 `.mathlottery/codex-home`，并强制使用 `cli_auth_credentials_store="file"`。官方 Codex 将凭据保存在此目录；目录由 Git 忽略，在 POSIX 系统上仅当前用户可访问。父进程环境、本地 Codex 目录与系统凭据存储不被修改。MathLottery 不复制也不回退使用本地 Codex 的凭据、配置或会话。需要 MCP、插件或 Codex 默认设置时，请在这个独立目录配置；搜索、Shell 和文件工具仍由官方 Codex 执行。[Codex 环境变量说明](https://learn.chatgpt.com/docs/config-file/environment-variables)

此次改动保留已有 MathLottery 题目、报告和检查点。之前保存在个人 Codex 目录中的原生对话不会复制过来，因此旧任务缺少原会话时，可能需要新建任务。新创建的会话会保存在独立目录中，供后续续接。

密码和令牌不经过 MathLottery 前端。应用只在内存中保留脱敏账号信息和待完成的设备码状态，不写入配置、报告或浏览器 localStorage。登录检查不会启动研究任务，接入使用官方 [Codex app-server 认证协议](https://learn.chatgpt.com/docs/app-server)。请将 `.mathlottery/` 连同其中的凭据和会话保持私有，不加入 Git。

此登录用于 **codex** 后端。MathLottery 当前的 **chat** 后端仍需要 API Key 并使用 API 计费，尚未接入另一套 Sign in with ChatGPT API 集成。

## 在 config.yaml 中选择模型

配置文件顶部集中放置常用选择，示例使用 Codex、GPT-6 Astra 和 Max：

~~~yaml
backend:
  mode: codex
  model: gpt-6-astra
  reasoning_effort: max
  chat:
    reasoning_mode: pro

budget:
  max_wall_time_minutes: 180
  max_iterations: 50
~~~

使用 Chat Pro 时，把 `backend.mode` 改为 `chat`，并按下文设置 API Key 即可。`backend.chat.reasoning_mode` 只在 chat 后端生效，可以选 pro 或 standard；Codex 使用 model 和 reasoning_effort。更换模型时直接修改 model。

保存配置后，运行短命令：

~~~bash
mathlottery find
mathlottery solve --prompt '请你解决黎曼猜想'
mathlottery verify --from-run <solve-run-id>
mathlottery run
~~~

以上分别启动找题、求解、验真和完整流程，按需要选择一条执行。模型与预算无需重复写在命令中。

| 配置字段 | 作用 | 示例 |
| --- | --- | --- |
| `backend.mode` | 选择 agent 后端 | `codex` / `chat` |
| `backend.model` | 模型 ID | `gpt-6-astra` |
| `backend.reasoning_effort` | 思考强度 | `max` |
| `backend.chat.reasoning_mode` | Chat API 思考模式 | `pro` / `standard` |
| `budget.max_wall_time_minutes` | 总活跃时间上限，分钟 | `180` |

GPT-6 Astra 支持 low、medium、high、xhigh、max。GPT-5.6 和 GPT-6 系列在 Responses API 中支持独立的 `reasoning.mode: pro`，不需要给模型 ID 添加 `-pro`，也不应将 pro 填入 reasoning_effort。Pro 会增加模型工作量、延迟和 token 用量。[模型说明](https://developers.openai.com/api/docs/models/gpt-6-astra)、[Reasoning mode](https://developers.openai.com/api/docs/guides/reasoning#reasoning-mode)

这里配置的是 API 的 Pro 执行模式；ChatGPT 网页的工具、系统提示和产品编排仍可能不同，不保证两者行为完全一致。模型、强度和工具的实际可用性由账户及后端决定，不支持时保留错误，不自动降级。报告会区分请求的设置与后端实际返回的设置；后端未报告的字段保持未知。

`--backend`、`--model`、`--reasoning-effort`、`--reasoning-mode` 仍可用于临时覆盖配置，不修改配置文件。新任务读取当前配置；`resume` 恢复创建任务时保存的配置，之后编辑 config.yaml 不会改变已有任务。续接时需要更换模型或模式，可显式传入对应覆盖参数；已在后台执行的请求先恢复处理，新设置用于下一次创建请求。

## 选择 agent 后端

### codex：持续的原生 agent 会话

安装官方 Codex CLI，通过浏览器工作台的「MathLottery 账号」面板完成登录。直接运行 `codex login` 登录的是独立的本地 Codex，不会登录 MathLottery。MathLottery 使用官方 `codex exec`，后续在自己的独立目录中精确续接同一个会话；搜索、Shell 和文件操作由 Codex 提供，MCP/插件等可选工具在 MathLottery 独立目录配置。实际可用工具取决于本机和账户。

~~~bash
mathlottery solve --prompt '请你解决哥德巴赫猜想'
~~~

将 config.yaml 的 backend.mode 设为 codex。model 和 reasoning_effort 为 null 时使用 MathLottery 独立目录中的 Codex 默认配置；需要指定时直接在文件中填写。界面中单独选择的对话模型不一定是 CLI 默认值。研究文件写入当前研究工作区，继续使用 workspace-write 沙箱和配置的网络权限。

原生调用不使用逐动作 JSON 协议，不经过旧版 15 秒、512 MB 的工具包装，也不使用固定长度摘要代替原生历史。Codex 自身仍有上下文窗口和压缩机制。[官方非交互调用说明](https://learn.chatgpt.com/docs/non-interactive-mode)

### chat：自动调用 Responses API

chat 直接调用模型 API，自动等待结果、保存上下文并继续下一轮。默认启用服务端 web_search 和 Code Interpreter。它需要 API 账户凭据和明确的模型设置；这里的 chat 指 API 后端，不是对 ChatGPT 网页 Pro 模式的自动操控。

将 config.yaml 的 backend.mode 设为 chat，model 填为账户可用的模型。将 API Key 放入 OPENAI_API_KEY 环境变量，不要写入配置文件。可以用以下 Bash 命令隐藏输入，避免把密钥直接写进命令历史：

~~~bash
read -rs -p 'OpenAI API key: ' OPENAI_API_KEY
export OPENAI_API_KEY
mathlottery doctor
mathlottery find --query '适合有限预算探索的组合数学问题'
~~~

backend.model 未设置时，也可以通过 OPENAI_MODEL 环境变量提供模型。`doctor` 只检查 Chat 配置是否齐全，不发送收费模型请求。API 缺少凭据、模型或工具不受支持时明确报错，不切换到手动模式或其他后端。

Chat 使用 previous_response_id 续接研究上下文，审查从新的上下文开始。长调用在服务端后台运行，程序轮询状态；Ctrl+C 和 stop 会请求服务端取消。连接中断后已有 response ID 的调用会被重新查询，不会重复创建。若创建请求断线且没有收到 ID，程序会保留不确定状态，需先核对 API 控制台再决定是否新建研究。

API 返回的完整回答、工具结果和引用元数据保存到本地；Code Interpreter 的计算发生在托管容器中，不能直接读取本机文件。容器和服务端响应有各自的保留期限，本地报告不能重建失效的服务端上下文。

依据：[会话状态](https://developers.openai.com/api/docs/guides/conversation-state)、[后台调用与取消](https://developers.openai.com/api/docs/guides/background)、[联网搜索](https://developers.openai.com/api/docs/guides/tools-web-search)、[Code Interpreter](https://developers.openai.com/api/docs/guides/tools-code-interpreter)。

## 找题

~~~bash
mathlottery find --query '优先找有明确表述、近期仍未解、适合程序实验的问题'
mathlottery find --source https://www.erdosproblems.com/ --count 3
mathlottery problems
~~~

agent 自行检索、比较问题、核查已有进展。找题结束后保存题库与本次排序，不自动开始求解。终端会列出问题 ID；详细结果位于 runs/<run-id>/literature/selection.json 和 report.md。

每个题目保留准确表述、来源、难度估计、验证可行性和选择理由。未解状态是有证据支持的 agent 判断，排序不是解出概率。只有运行记录支持的来源才能计入状态核查；证据不足时保持 UNKNOWN，原始 agent 判断仍保留在选题记录中。

## 求解

使用找题输出的问题 ID，或直接给出研究目标：

~~~bash
mathlottery solve --problem <problem-id>
mathlottery solve --prompt '研究这个数学问题……'
~~~

也可以导入自己的题目：

~~~bash
mathlottery add --file examples/odd_sum.problem.json
mathlottery solve --problem odd-sum --budget-time 10m
~~~

同一个研究 agent 自己决定推导、实验和工具顺序。部分候选可以保存后继续探索；最终候选提交后，独立 solve 任务结束，证明仍标为 CANDIDATE，等待 verify。没有找到证明也是有效的研究结果。

## 验真

审查一个已有求解任务的最新候选，或直接提供候选 JSON / 证明文件：

~~~bash
mathlottery verify --from-run <solve-run-id>
mathlottery verify --candidate runs/<run-id>/candidates/<candidate-id>.json
mathlottery verify --problem odd-sum --proof examples/odd_sum.proof.md
~~~

候选 JSON 会保留其 claim、proof、assumptions 和 references；已有审查结论不会带入新审查。没有指定 --problem 时，JSON 候选的 claim 就是本次要检查的命题。纯证明文本必须同时指定 --problem。

审查使用独立会话和工作区，初始上下文包含问题、候选、引用，以及在浏览器中明确选择的证明源码，不包含求解会话历史和旧审查结论。NO_ISSUES_FOUND、ISSUES_FOUND、INCONCLUSIVE 都会结束独立 verify 任务，不自动转去求解。模型审查无问题最多标为 SELF_CHECKED；有限测试或 agent 自报 Lean 通过都不会自动升级为正式证明。

Codex 的 workspace-write 不是完整的文件读取隔离，因此这里是上下文独立，不是经过认证的严格盲审。

## 串起完整流程

~~~bash
mathlottery run
mathlottery run --problem <problem-id>
mathlottery run --prompt '请你解决黎曼猜想'
~~~

未提供问题时先找题；指定问题后直接求解。候选交给独立审查，有问题或不确定时返回原研究会话。部分成果通过后继续研究；研究者明确将候选作为最终交付且审查无问题时，完整流程结束。

## 暂停、续接与报告

~~~bash
mathlottery status <run-id>
mathlottery stop <run-id>
mathlottery resume <run-id>
mathlottery resume <run-id> --message '优先检查边界情况并寻找反例'
mathlottery resume <run-id> --budget-time 6h --max-iterations 100
mathlottery report <run-id> --show
mathlottery export <run-id> --format json --output checkpoint.json
~~~

预算覆盖值是新的总上限，不会清零已消耗时间。暂停时间不计活跃时间；max_iterations 统计研究交接轮数，不限制一轮内的原生工具调用次数。token 使用后端实际返回值，在调用之间检查；未返回用量时保持未知。

报告包含阶段指标表和 `metrics.json`：完成的返回次数、缺失/无效阶段成果、实测调用耗时、候选数量与审查结论。可用它们定位找题、求解和审查各自的耗时，以及重复出现的交接失败。旧记录缺少耗时时显示 `unknown`，不按零处理。这些指标不认证数学成功；模块边界见[代码流与恢复](architecture.cn.md)。

已结束的 native 任务可通过 resume --message 补充方向，继续其原来的功能。需要切换 agent 时显式使用 --backend；存在未处理调用时先恢复该调用。每种后端的上下文 ID 分开保存，切换时导入已记录的研究回答。

不要在另一个 Codex 客户端同时操作本项目正在运行的同一个会话。

## 配置与用量

完整模板见 [config.example.yaml](../config.example.yaml)。常用配置：

~~~yaml
backend:
  mode: codex
  execution: native
  model: gpt-6-astra
  reasoning_effort: max
  native_turn_timeout_seconds: null
  native_web_search: live
  native_network_access: true
  chat:
    api_key_env: OPENAI_API_KEY
    base_url: https://api.openai.com/v1
    reasoning_mode: pro
    poll_interval_seconds: 1
    request_timeout_seconds: 30
    tools:
      - type: web_search
      - type: code_interpreter
        container:
          type: auto
budget:
  max_wall_time_minutes: 180
  max_iterations: 50
  max_external_cost_usd: null
~~~

native_turn_timeout_seconds 为 null 时，一次 agent 调用可以使用剩余总时间。chat.request_timeout_seconds 只限制单次 HTTP 请求，不是整个模型思考时长。chat.reasoning_mode 为 null 时不发送该字段，使用 API 默认模式；standard 和 pro 可显式选择。可按账户和模型支持情况配置 Chat 服务端工具；需要客户端执行的自定义工具尚未接入。

Chat 使用 API 计费；Codex 使用官方 CLI 的 ChatGPT 登录。程序不自动切换认证或计费方式。实际金额、订阅余额和第三方工具费用不在本项目中估算，API 花费上限应在服务商账户设置。保留的旧配置 max_external_cost_usd: 0 会阻止 Chat API；null 表示采用账户侧消费控制，不表示免费。

codex_command 默认是命令名 codex，运行时从 PATH 查找，不把探测到的绝对路径写回配置。config.yaml、.env、IDE 配置、数据库、运行记录和测试日志均属于被忽略的本机文件。

## 查看结果样本

[showcase 展示目录](../showcase/README.cn.md)包含三个精简案例，附证明、审查摘要和验证记录：

- [对合排列上的网格模式](../showcase/mesh-involutions/README.cn.md)：完整普通证明稿，Lean 仅部分验证。
- [中位三角形不等式](../showcase/medial-triangle-inequality/README.cn.md)：完整普通证明及实际通过检查的 Lean 形式化。
- [阶梯不规则图](../showcase/stepwise-irregular-graphs/README.cn.md)：完整反例及可执行的有限证书。

各案例提供复现说明并标明新颖性限制，相关判断的证据见各案例的审查摘要与验证记录。这些是研究产出，形式验证范围与新颖性状态需要分别理解。

## 本地产物

~~~text
.mathlottery/state.sqlite3          # 权威状态、后端上下文 ID、事件
problems/<problem-id>/problem.json # 可再次用于求解的题目
runs/<run-id>/
  literature/selection.json        # 找题排序、状态证据、原始判断
  workspace/                       # 研究工作区及完整研究回答
  review-workspaces/<candidate-id>/ # 独立审查工作区
  tasks/<task-id>/<attempt>/        # Prompt、回答、调用回执
    request.json / response.json   # Chat API 请求体与响应，不含认证头
    codex.events.jsonl             # Codex 原生事件
  candidates/                      # 不覆写的候选证明版本
  verification/                    # 独立审查结果
  checkpoints/ / usage.json         # 恢复状态与实际用量
  report.md                        # 当前功能的结果与证据
  metrics.json                     # 各阶段结果及调用耗时
~~~

模型与工具信息来自实际响应或会话元数据，没有报告的字段保持未知。外部工具副作用不保证 exactly-once；恢复时应结合日志和研究文件核对。

## 旧版兼容与开发

原来的手动交接改名为 manual，work 保留为 codex 的兼容名称，--mode 保留为 --backend 的兼容选项。旧的 chat 检查点恢复时仍是 manual，不会因升级而自动发送收费请求。

~~~bash
mathlottery run --backend manual --prompt '研究这个数学问题……'
mathlottery submit --run <run-id> --file response.md
mathlottery run --backend manual --execution structured --problem odd-sum
mathlottery demo
mathlottery demo --case incorrect
pytest -q
ruff check .
~~~

manual 才需要人工传递回答；chat 和 codex 都会自动调用 agent。structured 是旧版兼容协议，新版三项独立功能使用 native。

更多细节见 [架构与恢复](architecture.cn.md)、[验证方法与范围](local-validation.cn.md) 和 [旧版协议](protocol.cn.md)。离线 Demo 与模拟后端测试不代表模型数学能力。项目不会自动提交或推送到 GitHub。
