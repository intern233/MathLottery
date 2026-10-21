# 验证方法与范围

[English](local-validation.md) | 简体中文

[项目介绍](../README.cn.md) · [安装与使用](usage.cn.md) · [结果样本](../showcase/README.cn.md)

本文提供可复用的检查步骤。具体机器路径、账户信息、真实会话标识和原始运行日志保留在被忽略的本地运行目录，不写入仓库文档。

## 自动化检查

在已安装开发依赖的 MathLottery 项目根目录运行：

```bash
conda activate mathlottery
pytest -q
ruff check .
python -m compileall -q src
python -m pip check
```

测试覆盖 native 与 structured 两种流程，包括：

- 精确会话续接、普通 Markdown 交接及跨模式反馈。
- find、solve、verify 的独立终止行为，以及 run 串联的完整流程。
- Chat Responses API 的请求体、服务端工具、连续上下文与独立审查上下文。
- 模型与 Max 参数的 Codex 会话续接、Chat Pro/standard 模式的独立传参，以及所有研究命令的命令行覆盖。
- Chat 后台响应的轮询、断线恢复、远端取消、真实用量字段及凭据不落盘。
- 独立审查、不确定结论的后续研究，以及部分成果通过后继续探索。
- 中断、限流、预算、回执恢复和孤儿子进程识别。
- 候选证明完整性、路径隔离及运行元数据。
- 离线数学实验、文献来源适配和可选形式验证工具的缺失处理。

自动化后端测试使用明确标注的假 CLI 和 httpx.MockTransport，不消耗真实模型额度；隔离执行测试会运行真实子进程。手动交接测试仅覆盖 manual 兼容后端，不代表 chat 的调用方式。测试数量与耗时以本次命令输出为准。需要保存原始测试输出时，放入 .mathlottery/ 等被忽略的目录。

## 离线流程

```bash
mathlottery demo
mathlottery demo --case incorrect
mathlottery demo --case hidden-assumption
mathlottery demo --case finite-only
```

这些案例覆盖正确证明、除零、遗漏假设和用有限测试代替一般证明。Demo 的审查内容是固定测试素材，不代表模型自动识别任意数学错误的能力。

## 真实 Codex 集成检查

先用 mathlottery doctor 检查可执行文件、ChatGPT 登录及本地工具。诊断输出供本机排查使用，不应复制进公开文档。

导入教育示例，并在明确预算下执行：

```bash
mathlottery add --file examples/odd_sum.problem.json
mathlottery solve --backend codex --problem odd-sum --budget-time 3m --max-iterations 5
```

使用命令输出的运行 ID 查看报告：

```bash
mathlottery status <run-id>
mathlottery report <run-id> --show
```

检查候选证明是否保存，以及模型、工具调用和 token 用量是否来自实际运行记录。solve 本身不启动审查。使用该任务的候选单独验证：

```bash
mathlottery verify --backend codex --from-run <solve-run-id> --budget-time 3m
```

检查审查是否使用独立会话，且没有继承原求解轨迹。LLM 审查通过最多为 SELF_CHECKED，不能据此宣称形式证明。

进一步检查同一研究会话的续接：

```bash
mathlottery resume <run-id> --message '检查 n=0 的边界情况，并保留已有研究结果' --budget-time 6m --max-iterations 10
```

预算参数是新的总上限。比较续接前后的研究会话 ID，确认文件仍可读取。原生 Shell、网页搜索和工作区写入边界可以在受控集成任务中单独检查；不要绕过沙箱来使检查通过。

报告和原始事件位于 runs/<run-id>/，数据库位于 .mathlottery/，都属于本机产物，不纳入仓库。真实调用会使用账户的订阅额度，结果和用量不要求逐字复现。

## 验证边界

真实 Chat API 检查需要先配置 API Key 和模型，方法见 [安装与使用](usage.cn.md)。可将上述命令的后端改为 chat；再用 find 检查选题结果和状态证据。自动化 HTTP 合约测试不等同于真实账户已具备模型、搜索或代码执行权限。

历史集成检查已覆盖原生 Shell、文件保留、精确会话续接、网页搜索以及候选提交与独立审查。它们证明执行链路可用，不构成与 ChatGPT Pro 或原生 Codex 的数学能力对照评测，也不代表解决了开放猜想。

Lean 等可选工具需要另外安装。缺少工具或外部证据时应如实记录不可用或未验证，不能将其计为通过。

## 展示样本的证据

[结果样本](../showcase/README.cn.md)提供各案例的普通证明、审查摘要、验证元数据和复现说明。[2026-10-21 复核报告](../showcase/audit-2026-10-21.cn.md)分别说明公开来源、开放状态、数学正确性和新颖性。

网格模式案例只有部分 Lean 验证，中位三角形案例已有完整形式陈述通过检查，图论案例则以可执行有限证书辅助其书面反例证明。理解检查通过的含义时，应先阅读各案例注明的范围。
