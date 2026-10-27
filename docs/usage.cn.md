# 安装与使用

[English](usage.md) | 简体中文

[浏览器快速上手](#本地浏览器工作台) · [终端运行](#cli) · [接入配置](#backends) · [常见问题](#troubleshooting)

MathLottery 提供两种运行入口，共用同一工作区的配置、账号和结果。

| 运行入口 | 适合做什么 |
| --- | --- |
| **浏览器：`mathlottery serve`** | 找题、选题求解、审查证明、整理报告。建议从这里开始。 |
| **终端：`find`、`solve`、`verify`、`organize`、`run`** | 单独执行各阶段，或自动串联研究流程。 |

运行入口与模型接入方式是两回事：**Codex** 使用官方 CLI 和 MathLottery 独立登录；**Chat** 使用 API Key 和 Responses API，也可以配置[兼容的提供方](configuration.cn.md#providers)。

## 本地浏览器工作台

<a id="install"></a>

### 1. 安装 MathLottery

使用 **Linux 或 WSL 2**，提前安装 Git 和 Conda。WSL 用户在 Linux 终端执行以下命令。已有仓库时，进入项目目录，跳过克隆步骤。

```bash
git clone https://github.com/intern233/MathLottery.git
cd MathLottery
conda env create -f environment.yml
conda activate mathlottery
mathlottery init
```

环境文件会安装 Python、项目依赖和研究工具。`init` 创建本地存储，并在 `config.yaml` 不存在时生成默认配置；已有配置不会被覆盖。初次诊断可能提示 Codex 未安装、未登录，或 Chat 没有 API Key；下一步配置你实际要使用的后端即可。

如果已有 `mathlottery` 环境，用 `python -m pip install -e '.[dev,research]'` 更新项目安装。

**第一次跑通不需要安装 Lean。** 单个远程研究流程可先预留 2–4 GiB 可用内存和 3–5 GiB 磁盘；Lean/mathlib 需要更多资源。这些是规划余量，不是实测最低要求。安装 Lean 或进行大型本地实验前，请看[资源需求](resources.cn.md)。

### 2. 准备 Codex

默认后端是 Codex。请在**运行 MathLottery 的同一个 Linux/WSL 环境**安装[官方 Codex CLI](https://learn.chatgpt.com/docs/cli)，再用 `codex --version` 检查。如果该环境已有 Node.js/npm，可以这样安装：

```bash
npm install --global --prefix "$CONDA_PREFIX" @openai/codex
hash -r
codex --version
```

执行前需激活 Conda 环境。`environment.yml` 不包含 Node.js/npm；官方 CLI 页面也提供不依赖 npm 的安装方式。[官方安装说明](https://github.com/openai/codex#installing-and-running-codex-cli)

已有可用的 CLI 就跳过安装。想用 API？跳过 Codex 设置，先完成 [Chat API 配置](#chat-api)，再启动页面。

### 3. 打开页面并登录

```bash
mathlottery serve
```

打开**终端实际打印的地址**。首选端口是 `8765`，被占用时可能使用其他端口。WSL 用户在 Windows 浏览器打开打印出的 `http://localhost:<port>`。保持服务终端运行；前端不需要单独安装或构建。

在 **MathLottery 账号**面板选择**使用 ChatGPT 账号登录**，去官方页面完成授权。它与普通 Codex CLI / IDE 的登录状态独立；可以使用同一个账号，但额度仍按账号共享。设备码登录可能需要先在 ChatGPT 安全设置中开启。[官方认证说明](https://learn.chatgpt.com/docs/auth)

在**本次任务的模型**中选择提供方、模型和推理强度。例如，`gpt-6-astra` 是模型 ID，`max` 是另一个推理强度选项，需要账号支持。开始任务会消耗所选后端的额度或产生 API 费用。第一次测试可在**预算与 agent 设置**中先缩短时间预算。

### 4. 跑通一次流程

| 阶段 | 你需要做什么 | 会得到什么 |
| --- | --- | --- |
| **找题 Find** | 输入倾向，例如：“找一个公开未解决的数学问题，陈述精确、范围较小，最好能用 Lean 验证；检查原始来源和后续进展。” | 候选列表、来源、开放状态证据，以及难度、验真和 Lean 可行性评价。 |
| **选题 → 求解 Solve** | 点击**选择这道题**，确认**你选择的题目**，再点击**开始求解**；可补充任务要求。 | 研究过程与候选证明，也可能只有部分结果或未成功的尝试。选题本身不会启动求解。 |
| **验真 Verify** | 点击**验真最新候选**，选择需要的证明源文件，确认审查设置后启动。 | 独立审查结果、发现的问题、证据缺口和实际检查范围。 |
| **整理 Organize · 可选** | 审查后点击**整理为专家阅读报告**，选择模型，再点击**生成专家阅读报告**。 | 中英文各一份 Markdown 和 PDF 报告，解释论证、支持材料与审查发现。[报告配置](#organize) |

也可以跳过 Find：在 **Solve** 中选择**输入一个新问题**并填写陈述。第一次可用“证明对每个非负整数 n，前 n 个正奇数之和等于 n²”测试流程。这是已知结论，用来检查系统是否跑通，不是开放问题发现。

任务历史按精确问题陈述归并 Solve、Verify 和 Organize 尝试。选题启动 Solve 并记录明确来源后，Find 会并入对应问题组，使用问题标题；尚未选题的 Find 仍用查询标题。同一次 Find 选出多个问题时，会作为各组的共享来源展示，但执行总数只计一次。

请分开看**运行状态**与**研究结果**。“运行完成”只表示执行结束。Solve 展示求解者声称完整解决、部分解决或尚未解决；Verify 另列审查结论、原题覆盖和新颖性。部分结果审查未发现问题，不代表完整原题已解决。Organize 沿用这些结论。旧候选若依据明确自述展示范围，会注明依据，原记录及哈希不变。参见[证据说明](evidence.cn.md)和[成果样本](../showcase/README.cn.md)。

原生 Solve 会保存部分结果或未解决的进展，在剩余累计预算内续接同一会话。默认情况下，求解者明确声称完整解决或给出反例，且没有剩余数学义务时，才可以提前结束，之后仍须 Verify。在**预算与 agent 设置**中勾选**用满求解时间预算**，声称完整解决后也会继续研究和自查；续接原生 Solve 任务时也可选择。其他限额、额度或错误可能提前中断，你也可以主动停止。[Solve 结束条件与预算规则](configuration.cn.md#budgets)

研究时间用尽时，原生 Solve 显示**快速收尾中**，在原会话执行一次收尾调用，默认最多**额外五分钟**保存现有结果和剩余问题。**已收尾**不等于已解决，请查看求解者声称的完成范围。若收尾调用失败，会保存并明确标注本地检查点摘要。可在新建任务前通过 `config.yaml` 的 `budget.finalize_minutes` 设置收尾时限（`0` 关闭）。

关闭页面或 UI 服务**不会停止**后台研究。请使用**停止任务**或 `mathlottery stop <run-id>`。重新启动服务会连接已有记录，不会自动重启已停止的任务。

**运行动态**中可查看最近的工具活动、最后活动时间和本任务进程树的内存采样。排队任务显示队列位置。新任务共享工作区资源配置，默认同时执行一个任务、一个独立形式化检查；任务开始前的排队等待不消耗研究时间。[资源控制说明](resources.cn.md)

查看审查结果时，展开**关键证明步骤**或**新颖性待核查事项**。空闲 Find/Verify 的**继续核查这一项**会填写针对性方向；检查预算并点击继续才执行。旧记录没有这些评估时会显示未评估。[证据要求](evidence.cn.md)

<a id="cli"></a>

## 在终端运行

激活环境后，在 **MathLottery 项目目录**执行。先完成一次[接入配置](#backends)；终端研究不需要浏览器服务一直运行。

| 命令 | 行为 |
| --- | --- |
| `mathlottery find` | 找题并保存候选列表，然后等待你选题。 |
| `mathlottery solve --problem <problem-id>` | 求解已保存的问题；新陈述用 `--prompt`。 |
| `mathlottery verify --from-run <solve-run-id>` | 独立审查某次 Solve 的最新候选证明。 |
| `mathlottery organize --from-run <verify-run-id> --language zh` | 生成中英文专家报告，默认导出中文版本。 |
| `mathlottery run` | 自动找题、求解、审查，不在选题处等待用户。 |

### 找题 → 选题 → 求解 → 验真

```bash
mathlottery find --query '找一个范围较小、陈述精确、适合 Lean 验证的公开未解决问题；检查原始来源和后续工作' --count 3
mathlottery problems
mathlottery solve --from-find <find-run-id> --problem <problem-id>
mathlottery verify --from-run <solve-run-id>
```

请**逐条执行**，将 `<find-run-id>`、`<problem-id>`、`<solve-run-id>` 替换为前面命令打印的实际 ID，不要原样粘贴尖括号占位符。选题前先看 Find 报告。`--from-find` 会把所选问题的研究资料快照交给新的 Solve 会话，原 Find 记录保持不变。

`verify --from-run` 会带入候选证明、问题陈述和引用，但不会自动复制工作区的证明文件。需要把 Lean 等源文件作为固定附件提交时，请使用浏览器 Verify 表单。[证据输入与限制](configuration.cn.md#evidence)

### 直接提供自己的问题

```bash
mathlottery solve --prompt '证明对每个非负整数 n，前 n 个正奇数之和等于 n 的平方' --budget-time 10m
```

也可以导入仓库自带示例，然后使用其问题 ID：

```bash
mathlottery add --file examples/odd_sum.problem.json
mathlottery solve --problem odd-sum --budget-time 10m
mathlottery verify --problem odd-sum --proof examples/odd_sum.proof.md
```

最后一条审查的是给定的示例证明。要审查刚才求解产生的候选，请用 `verify --from-run <solve-run-id>`。自行输入问题不代表它已被确认为开放问题或新成果。

<a id="organize"></a>

### 验真后：整理专家阅读报告

在浏览器中选择 **Organize 整理**，或运行：

```bash
mathlottery organize --from-run <verify-run-id> --language zh
mathlottery export <organize-run-id> --format markdown --language zh --output report.zh.md
mathlottery export <organize-run-id> --format pdf --language en
mathlottery export <organize-run-id> --format bundle --output expert-reports.zip
mathlottery export <organize-run-id> --format public_bundle --output public-text-reports.zip
```

将任务 ID 占位符换成实际值。Organize 始终根据同一份证据生成**中英文两版**。它的 `--language zh|en` 只设置默认导出语言，不限制生成版本；`export --language` 则选择要导出的已保存版本。`--instructions` 可以指定读者背景或重点。Organize 使用同一套模型配置，也支持 `--backend`、`--model`、`--reasoning-effort`、`--reasoning-mode`、`--budget-time` 和 `--max-iterations` 覆盖参数。启动整理会创建独立模型任务并消耗额度，选择来源本身不会调用模型。

来源任务必须处于空闲状态，且包含审查记录；未能确认或发现问题的审查也可以整理。报告说明原题、假设、证明思路、引理与推导，并保留审查问题、形式检查范围和新颖性不确定性。它根据已保存的可见材料重构说明，不是隐藏思维过程，也不构成新的验证。

新报告开头会增加根据冻结证据确定性生成的**专家速览**，中英文各一份，概括原题、候选、证明路线、Lean 证据和待核查事项，随后附证据索引。长记录会明确标注摘录；完整陈述和检查原文保留在报告正文及链接的冻结材料中。重复障碍归并展示，历史失败和未解决编号仍可查。导航链接可直接跳到完整论述，PDF 同样支持。重新导出旧报告会保留原文及速览版本；需要修订时，可续接原 Organize 任务，这会再次调用模型。

需要 PDF 时，先安装一次[可选报告依赖](resources.cn.md#reports)。两种入口都在 `runs/<organize-run-id>/organized/` 保存：

| 语言 | Markdown | PDF（导出成功时） |
| --- | --- | --- |
| 中文 | `report.zh.md` | `report.zh.pdf` |
| English | `report.en.md` | `report.en.pdf` |

`report.md` 和 `report.pdf` 保留为默认导出语言的兼容副本。同目录的 `manifest.json` 记录来源、哈希和遗漏，`materials/` 保存捕获的小型源文件。二进制依赖、缓存，以及没有明确来源关联的历史 Solve 记录可能未被收集；分享前请检查清单。

专家交接时，下载**原始报告与材料 ZIP**，先读 `handoff/START_HERE.zh.md` 或 `handoff/START_HERE.en.md`。包内提供简短阅读顺序、独立证明和审查文件、结构化覆盖与复现索引，以及文件完整性检查器。索引列明真正检查过的定理声明、源码哈希、已记录命令和捕获的 Lean/Lake 依赖；缺少依赖锁定或源码时会明确说明。原始隔离环境中的命令是执行证据，不能直接作为本机脚本运行。解压后在包根目录运行 `python handoff/check_files.py`，仅核对文件哈希，不能据此判断数学正确性。单独下载 Markdown 或 PDF 不附带引用材料。

公开分享请另选**脱敏文本 ZIP**（`--format public_bundle`）。它处理已支持的凭据、账号、邮箱、本机路径和私有 IP 模式，并排除原始 PDF 和二进制文件。`public-export.json` 对照原始与导出哈希，列出删改和遗漏。发布前仍需检查这个副本：模式匹配无法识别所有私人事实，修改后的 Lean 源码也不能直接继承原内核回执。原始材料包保持不变，可能包含本机路径。

交接文件在导出时由本地生成，无需调用模型。历史已完成报告通过下载 ZIP 或重新导出 PDF 即可获得新版交接材料，原 Markdown 和哈希保持不变；需要改写报告正文时，才显式续接 Organize。

某一版 PDF 导出失败不会丢失两版 Markdown，也不妨碍另一版 PDF 导出。修复渲染环境后，点击**重新导出 PDF**或执行上述 PDF 导出命令，根据已保存版本重新生成，**无需再次调用模型**。Markdown 导出得到专家报告；`mathlottery report <organize-run-id>` 仍然生成任务摘要。

历史单语言报告仍可读取，页面会注明缺失版本。重新导出 PDF 不会翻译；需要双语时，从已审查来源重新启动 Organize。

### 自动串联各阶段

```bash
mathlottery run
```

不指定问题时，`run` 自动找题后继续执行；用 `run --problem <problem-id>` 或 `run --prompt '你的问题陈述'` 则直接从求解开始。需要继续研究时，审查意见会返回原研究会话。原生 `run` 可以先审查部分候选，再在剩余预算内继续求解。如果时间在 Solve 阶段用尽，也会执行上述有时限的收尾，然后结束执行，不自动审查最终收尾候选。其他限额或错误可能中断尝试，增加预算不保证解决问题。

`run` 不会自动启动 Organize；查看结果后再明确选择整理。

<a id="backends"></a>

## 配置模型接入方式

两种入口启动**新任务**时都读取工作区的 **`config.yaml`**。修改已有的 `backend` 段即可，不要在 YAML 末尾重复添加同名键。浏览器可以覆盖本次新任务的设置，不会改写配置文件。

| 接入方式 | 需要什么 | 在哪里配置 |
| --- | --- | --- |
| **Codex**（默认） | 官方 CLI、MathLottery 的 ChatGPT 登录 | `backend.mode: codex`；在 MathLottery 登录一次 |
| **Chat / OpenAI API** | API Key 和可用模型 | `backend.mode: chat`；密钥放环境变量 |
| **其他 Responses 提供方** | 兼容的 API 地址、密钥和模型 | 命名的 `model_providers` 配置与 `backend.provider` |

### Codex：浏览器和终端共用工作区登录

`init` 生成的配置默认使用 Codex 及其默认模型设置。最小后端配置如下：

```yaml
backend:
  mode: codex
  execution: native
  model: null
  reasoning_effort: null
```

`null` 使用 **MathLottery 独立 Codex 目录**中的默认设置，不继承个人 CLI / IDE 的配置。需要指定时，修改 `model` 和 `reasoning_effort`，例如账号支持的 `gpt-6-astra` 和 `max`；每次执行命令就不必带长串模型参数。

先通过 `mathlottery serve` 登录一次，之后在同一工作区直接执行终端命令即可。不使用 MathLottery 页面时，参见[独立终端登录步骤](configuration.cn.md#account)。普通 `codex login` 登录的是个人 Codex，不是 MathLottery。

<a id="chat-api"></a>

### Chat：配置 API Key

将后端段改为下例，并把 `your-model-id` 换成实际可用的模型 ID。默认托管工具是网页搜索和 Code Interpreter，模型和账号需要支持它们。

```yaml
backend:
  mode: chat
  execution: native
  model: your-model-id
  reasoning_effort: null
  chat:
    reasoning_mode: null
    api_key_env: OPENAI_API_KEY
```

在即将启动 MathLottery 的终端输入密钥，避免明文显示或写入命令历史：

```bash
read -rs -p 'OpenAI API key: ' OPENAI_API_KEY
export OPENAI_API_KEY
mathlottery doctor
```

然后执行 `mathlottery serve` 或终端研究命令。已有服务需要重启才能读取新的环境变量。程序**不会自动加载 `.env`**。密钥放在环境变量中，不写进 YAML 或证明文件。

`chat` 是自动调用 Responses API 的后端，不是 ChatGPT 网页里的 Pro 模式。MathLottery 的 Codex 登录不能代替 Chat API 认证。`backend.chat.reasoning_mode: pro` 是可选请求参数，仅在所选 API 模型支持时配置。[模型、工具与提供方设置](configuration.cn.md#models)

### 其他提供方

配置命名的 Responses 提供方后，可以从浏览器选择，或在 YAML 的 `backend.provider` 中指定。参见[完整配置示例与兼容要求](configuration.cn.md#providers)。终端 `--backend` 选择的是接入方式（`codex` 或 `chat`），不是厂商名称；没有 `--provider` 参数。其他厂商的原生协议需要额外适配器。

<a id="operations"></a>

## 查看、停止和继续任务

将 `<run-id>` 替换为实际任务 ID。

| 操作 | 命令 |
| --- | --- |
| 查看已保存的状态 | `mathlottery status <run-id>` |
| 停止任务 | `mathlottery stop <run-id>` |
| 继续中断的任务 | `mathlottery resume <run-id>` |
| 补充方向，也可用于已完成任务 | `mathlottery resume <run-id> --message '检查边界情况和缺失的假设'` |
| 提高总预算 | `mathlottery resume <run-id> --budget-time 6h --max-iterations 100` |
| 查看报告 | `mathlottery report <run-id> --show` |
| 导出已保存的状态 | `mathlottery export <run-id> --format json --output checkpoint.json` |

继续任务使用它**已保存的配置**。修改 `config.yaml` 或页面上的模型选择不会改变已有任务。预算覆盖设置的是**新总上限**，不是追加时长；暂停时间不计入。已完成任务需要用 `--message` 给出新方向才能继续。[预算与恢复说明](configuration.cn.md#budgets)

终端研究在前台运行，浏览器任务由后台 worker 执行。不要同时用多个客户端操作同一个运行中的任务。

<a id="files"></a>

## 结果保存在哪里

| 路径 | 内容 |
| --- | --- |
| `problems/<problem-id>/` | 可复用的问题陈述 |
| `runs/<run-id>/report.md` | 结果与证据摘要 |
| `runs/<run-id>/candidates/` / `verification/` | 候选版本和审查记录 |
| `runs/<run-id>/workspace/` | 研究文件和可见回答 |
| `runs/<organize-run-id>/organized/` | 中英文专家报告、各版本 PDF 导出状态、来源清单和已收集材料 |
| `.mathlottery/` | 本地状态、会话和独立 Codex 登录 |

这些工作目录和 `config.yaml` 都已被 Git 忽略。浏览器可下载报告和小型证明源文件；有源文件不代表已通过形式化验证。整理后的小型案例放在纳入版本管理的 [showcase](../showcase/README.cn.md)。

<a id="troubleshooting"></a>

## 常见问题

| 现象 | 下一步 |
| --- | --- |
| Codex 不可用 / WSL 缺少 Linux 依赖 | 在启动服务的终端检查 `codex --version`，在 Linux 环境安装 CLI。[安装与账号说明](configuration.cn.md#account) |
| 登录请求超时 | 检查该终端的网络或代理，再重启服务。超时不等于已保存的登录过期。[网络设置](configuration.cn.md#network) |
| 浏览器拒绝连接 / 端口占用 | 使用实际打印的地址；可尝试 `mathlottery serve --port 9001`。[WSL 与端口说明](configuration.cn.md#network) |
| Chat 缺少密钥或模型 | 在启动终端导出 API Key、配置模型，并重启服务。[Chat 配置](#chat-api) |
| 模型或推理设置被拒绝 | 选择账号与提供方支持的选项；MathLottery 不会静默替换模型。[模型设置](configuration.cn.md#models) |
| Lean 失败或内存过高 | 检查固定的工具链版本、依赖库、可用内存与并发数。[资源指南](resources.cn.md) |
| Markdown 已生成，PDF 不可用 | 安装报告依赖、Chromium 和所需字体，再重试 PDF 导出。[PDF 配置](resources.cn.md#reports) |

`mathlottery doctor` 同时检查两个内置后端的基础配置，不运行模型推理。未使用后端的缺项不影响你选择的另一个后端。Chat 诊断只检查配置，不验证连通性、额度、模型权限或工具支持。

终端命令通常使用当前目录。显式指定工作区或配置时，将全局参数放在**子命令前面**：`mathlottery --root ./research-workspace --config ./my-config.yaml find`。`--config` 的相对路径按启动终端的当前目录解析，不相对于 `--root`；省略时才默认读取 `<root>/config.yaml`。`serve` 可以自动定位 editable 安装的项目，其他命令不会。更多选项可用 `mathlottery --help` 或 `mathlottery solve --help` 查看。

<a id="next"></a>

## 继续阅读

- [配置参考](configuration.cn.md)：提供方、账号、网络、预算、附件和兼容模式。
- [资源需求](resources.cn.md)：Lean 安装、内存/磁盘规划和 WSL。
- [证据政策](evidence.cn.md)与[成果样本](../showcase/README.cn.md)：结果究竟支持什么结论。
- [架构](architecture.cn.md)与[本地验证](local-validation.cn.md)：实现、检查和恢复机制。
