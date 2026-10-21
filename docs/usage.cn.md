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

安装官方 Codex CLI，执行 `codex login` 完成 ChatGPT 登录。MathLottery 使用官方 `codex exec`，后续精确续接同一个会话；搜索、Shell、文件操作以及已有 MCP/插件配置由 Codex 提供。实际可用工具取决于本机和账户。

~~~bash
mathlottery solve --prompt '请你解决哥德巴赫猜想'
~~~

将 config.yaml 的 backend.mode 设为 codex。model 和 reasoning_effort 为 null 时继承 Codex 用户配置；需要指定时直接在文件中填写。界面中单独选择的对话模型不一定是 CLI 默认值。研究文件写入当前研究工作区，继续使用 workspace-write 沙箱和配置的网络权限。

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

审查使用独立会话和工作区，初始上下文只包含问题、候选和引用。NO_ISSUES_FOUND、ISSUES_FOUND、INCONCLUSIVE 都会结束独立 verify 任务，不自动转去求解。模型审查无问题最多标为 SELF_CHECKED；有限测试或 agent 自报 Lean 通过都不会自动升级为正式证明。

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

各案例提供复现说明并标明新颖性限制，相关判断的证据见[来源与正确性复核](../showcase/audit-2026-10-21.cn.md)。这些是研究产出，形式验证范围与新颖性状态需要分别理解。

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
