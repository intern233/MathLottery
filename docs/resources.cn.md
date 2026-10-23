# 资源需求与 Lean 环境配置

[English](resources.md) | 简体中文

[安装与使用](usage.cn.md) · [结果样本](../showcase/README.cn.md)

MathLottery 调用远程模型，当前后端不需要在本地下载模型权重，也不要求 GPU 或 CUDA。但浏览器工作台、agent 客户端、文件和本地启动的工具仍消耗本机资源。其中，Lean/mathlib 检查和符号、数值实验可能占用最多的内存与磁盘。Chat 的托管 Code Interpreter 使用独立的远程环境，在本地安装 Lean 不会把它安装到远程容器中。

当前实现请使用 Linux 或 WSL 2。环境文件安装 Python 3.12 及项目依赖，软件包要求 Python 3.11 或更新版本。Codex 后端需要官方 CLI；Lean 和 [PDF 报告渲染器](#reports)均为需要另外安装的可选工具。前端不需要单独进行 Node.js 构建。

认证、模型调用与研究搜索需要出站网络连接。首次配置 Python/Lean/mathlib 时，还需要访问软件包、代码仓库和缓存服务；下载量可能较大，解压后的磁盘占用也会高于传输大小。准备完成、依赖齐全的本地 Lean 检查可以离线运行，模型驱动的研究仍需要后端连接与账号额度。

## 内存、CPU 与磁盘规划

以下是**用于起步的规划建议**，不是实测最低配置，也不能保证任意证明都能运行。表中内存指其他应用占用后，能够留给该工作负载的可用容量。在 WSL 中，需要同时检查 Windows 与 Linux；主机安装了多少内存，不等于 WSL 内有多少可用内存。磁盘建议包括新环境、依赖和部分工作空间，不包含操作系统与 WSL swap。

| 使用场景 | 建议留出的可用内存 | 起步 CPU / 并发策略 | 建议预留磁盘 |
| --- | --- | --- | --- |
| 浏览器/CLI 和一个远程研究会话，不运行大型本地实验 | 2–4 GiB | 2 个逻辑 CPU；一次一个研究任务 | 3–5 GiB |
| 复用已编译依赖，检查一个 Lean/mathlib 证明 | 6–8 GiB | 2–4 个逻辑 CPU；一次一个 Lean 检查，从 `-j 1` 开始 | SSD 上 20–30 GiB |
| 重建较大依赖、大型符号证明或多个本地任务 | 16–24 GiB 或更多 | 先测单任务，确认内存余量后再增加并发 | SSD 上 40–60 GiB 或更多 |

如果还要同时运行 IDE 和浏览器，偶尔使用缓存检查 Lean 时，可以从 16 GiB 主机内存规划；较重的任务建议 32 GiB 或更多。8 GiB 机器可以先尝试远程工作流与小规模检查，但不宜一开始就从源码完整构建 mathlib。这些是本项目的使用建议，不是 Lean 官方硬件要求。

CPU 核心多不代表构建一定跑得动。多个编译进程、编辑器的 Lean 工作进程和数值库线程会争用内存。即使只有一个线程，大型 tactic 搜索或多项式展开也可能超过预算。耗时还受证明写法、导入范围、文件缓存和磁盘速度影响；依赖下载与准备时间也要单独考虑，不能只计算模型思考时间。

### 一个实测参考

在 Linux x86-64 / WSL 2 环境中，使用 Lean 4.35.0 和样本固定的 mathlib 版本，单独检查 showcase 中的 [MedialAlgebra.lean](../showcase/medial-triangle-inequality/formal/MedialAlgebra.lean)，得到：

| 测量项目 | 观测值 |
| --- | --- |
| 编译参数 | `-j 1 -M 2048 -o MedialAlgebra.olean MedialAlgebra.lean` |
| 依赖状态 | 已有编译好的 mathlib 导入文件，没有构建或下载依赖 |
| GNU `time -v` 记录的最大常驻内存 | 2,081,860 KiB，约 **1.99 GiB** |
| 实际耗时 / 退出码 | 约 34 秒 / `0` |
| Lean 工具链磁盘占用 | 约 3.0 GiB |
| mathlib 工作副本、依赖及已有构建/缓存文件 | 约 7.2 GiB |

这里的内存只统计**一个模块的编译进程**，不包括界面、agent、IDE 和其他任务，不代表整个样本、从零构建 mathlib 或 WSL 的峰值。磁盘数字对应一个已安装版本及当时的缓存状态，不是压缩包下载大小，也不是固定需求。其他实验中，大型多项式归一化曾触发 Lean 的 `-M 2048` 上限；这说明触及了内部限制，不能据此声称实测常驻内存恰好为 2 GiB。配置上限和实际用量需要分别记录。

<a id="reports"></a>

## 可选：配置专家报告 PDF 导出

Organize 使用配置的远程模型撰写专家报告。保存 Markdown 不需要 PDF 渲染器；导出 PDF 会在本地运行 Chromium。激活 MathLottery 环境，在项目目录执行：

```bash
python -m pip install -e '.[reports]'
python -m playwright install chromium
```

Linux 提示缺少浏览器动态库时，可运行 `python -m playwright install-deps chromium`，可能需要管理员权限。中文报告还需要系统 CJK 字体；Debian/Ubuntu/WSL Ubuntu 可使用 `sudo apt-get install fonts-noto-cjk` 安装。浏览器依赖和字体属于本机环境配置，不调用模型。

Chromium 的下载与缓存因平台而异，通常占用数百 MB，需要在基础 Python 环境之外预留磁盘。每次导出都会启动本地浏览器进程组；先一次导出一份，长报告应实测 RAM，没有适用于所有报告的实测最低内存或整个进程组的内存上限。Organize 的模型任务沿用普通研究预算；PDF 导出和本地重试只使用 CPU、内存与磁盘，不再次调用模型，也不编译 Lean。

渲染支持标题、表格、代码、页码，以及 `$…$`、`$$…$$`、`\(…\)`、`\[…\]` 内的常用 TeX 数学公式。数学排版资源随项目提供，不从 CDN 获取脚本或字体。不支持的 TeX 会保留原文并提示警告。图片替换为描述文字，需要另行查看已捕获的原始材料；不执行原始 HTML，也不读取嵌入的远程或本地资源。

缺少依赖、Chromium 或渲染失败时，已保存的 Markdown 仍可用。修复环境后点击**重新导出 PDF**，或运行 `mathlottery export <organize-run-id> --format pdf`。分享前请查看导出警告并检查第一份 PDF，特别是数学符号、长公式和中文字体。PDF 生成成功仅表示排版完成，不代表证明通过验证。[整理操作与保存路径](usage.cn.md#organize)

## 准备 Lean，避免不必要的完整重建

按照 [Lean 官方安装说明](https://lean-lang.org/install/)安装工具链。项目的 `lean-toolchain` 与固定的 mathlib 版本应配套使用。[样本中的形式化工程](../showcase/medial-triangle-inequality/formal/README.cn.md)提供了完整示例。MathLottery 的环境安装和 `doctor` 不会安装 mathlib，也不会测试其内存需求。

在已经声明 mathlib 依赖的 Lean 项目中，先获取兼容的编译缓存，再检查证明：

```bash
lake exe cache get
```

导入范围较小时，也可以指定模块，例如 `lake exe cache get Mathlib.Algebra.Group.Basic`，只获取该模块及其依赖；这不等于自动获取任意证明的全部导入文件。下载和解压缓存仍会消耗磁盘、网络流量以及一定的 CPU/内存。保留版本固定信息；若没有匹配缓存，先查明原因，再决定是否从源码大量重建。[mathlib 缓存说明](https://github.com/leanprover-community/mathlib4/blob/master/Cache/README.md)

优先导入证明需要的模块，不默认导入整个 `Mathlib`。复杂 tactic 可考虑拆成小引理、给出明确的中间恒等式。对于导入依赖已经编译好的 `Proof.lean`，可从其 **Lean 项目根目录**采用以下起步命令：

```bash
env LEAN_NUM_THREADS=1 lake env lean -j 1 -M 2048 Proof.lean
```

`-j 1` 设置 Lean 的处理线程数，`-M 2048` 设置 Lean 内部的 MB 单位内存阈值。它不是操作系统对整棵进程树的限制，不是精确 RSS 上限，也不保证证明能在此限制下完成；具体选项以已安装版本的 `lean --help` 为准。遇到上限时，先检查证明、导入范围和可用内存，再决定是否提高。`lake env lean` 使用项目环境检查文件，不会替你编译缺失的导入模块。[Lake 命令说明](https://lean-lang.org/doc/reference/latest/Build-Tools-and-Distribution/Lake/)

确实需要构建时，可从 `env LEAN_NUM_THREADS=1 lake build <target>` 和明确的目标开始。`LEAN_NUM_THREADS` 控制 Lean 运行时并发，不是全局内存配额，也不能代替对子进程的观察。不要假设 `lake -j 1 build` 可用，Lake 与 Lean 的命令参数不同。[Lake 维护者的并发说明](https://leanprover-community.github.io/archive/stream/270676-lean4/topic/Lake.20parallel.20builds.html)

内核重放是另一种工作负载。对已经构建好的样本工程，可先使用 `env LEAN_NUM_THREADS=1 lake env leanchecker --verbose Conjecture5`。`--fresh` 还会重查导入依赖，可能消耗明显更多的资源。并行模块检查会同时加载多个导入环境，增加线程前应先测量。[官方 lean-action 说明](https://github.com/leanprover/lean-action#run-leanchecker-on-a-project-with-a-mathlib-dependency)

让 agent 操作时，可以在「任务补充说明」里写清楚工具链、缓存位置与并发要求，例如：“复用固定版本的 Lean/mathlib 环境；一次只启动一个编译器，使用 `-j 1 -M 2048`；尝试更大构建前记录峰值 RSS、退出码和上限失败情况。”这属于研究指令，不会自动给原生 agent 命令施加操作系统资源限制；独立附件检查器使用下文介绍的单独限额。

## 配置究竟限制了什么

| 配置或控制方式 | 生效范围与限制 |
| --- | --- |
| `tools.memory_mb: 512` | 旧版 structured Python 工作进程的地址空间限制。**不限制**原生 Codex 命令、Lean/Lake、Web 服务或 WSL；旧版 Lean 检查器也没有使用此内存设置。 |
| `tools.timeout_seconds: 15` | 旧版本地工具的超时，包括旧版 Lean 检查器；不会给原生 shell 命令统一加上 15 秒上限。 |
| `verification.formal_memory_mb: 2048` | 独立附件检查器的 Lean `-M` 阈值；另有 `formal_address_space_mb: 8192` 限制每进程虚拟地址空间（`RLIMIT_AS`，包括预留栈和映射库，不是实测 RAM）。一个 Lean 工作线程、64 MiB 线程栈，总检查默认限时 120 秒；不是整个进程树或 WSL 的 RSS 限制。 |
| `verification.formal_max_object_mb: 16` / `formal_max_total_object_mb: 960` | 独立检查器生成对象的单文件大小限制与监测总量，单位 MiB。证明对象可能远大于源码；检查后删除临时编译对象，回执保留限额、大小与哈希。不限制原生研究产物或整个磁盘。 |
| `verification.max_sources`、`source_timeout_seconds` | 独立引用抓取：每次阶段成果默认最多 12 个网址、60 秒收集预算；正在等待的请求使用 `tools.web_timeout_seconds`。PDF 解析沙箱限额 512 MB，详见[证据配置](evidence.cn.md)。 |
| `budget.max_wall_time_minutes` / `backend.native_turn_timeout_seconds` | 研究的活跃时间 / 单次原生调用时长，不是内存、CPU 线程数或磁盘上限。 |
| `budget.max_iterations` | 研究交接次数，不是一轮内的工具调用数或子进程数量。 |
| `backend.native_max_log_bytes` | 对单次原生 Codex 调用的事件/stdout 与 stderr 日志检查大小；不限制下载、产物、全部运行记录或 Chat 响应的总大小。 |
| Lean `-M`、`-j` 与 `LEAN_NUM_THREADS` | 对所调用 Lean 运行时的控制，不是所有任务合计的硬上限。 |

MathLottery 会阻止两个工作进程同时执行**同一条 run**，但目前没有跨不同任务的全局资源调度器，也没有按可用内存排队的机制。在测得足够余量前，一次只运行一个本地计算较重的任务。关闭浏览器或 Web 服务不会停止后台研究，需要使用「停止任务」或 `mathlottery stop <run-id>`。

如果需要对整组进程施加硬上限，应使用覆盖其子进程的操作系统或容器资源限制。MathLottery 不会自动配置这些限制，Codex 的工作区沙箱也不是内存配额。同样，时间/token 预算不等于预留了服务商额度；凭据、订阅/API 额度、网络与本机硬件是不同的运行条件，见[接入配置与预算](configuration.cn.md)。

## WSL 2 的内存与 swap

构建前同时查看 Linux 的 `free -h` 与 Windows 任务管理器，给 Windows、浏览器、IDE 和其他 WSL 工作负载留出容量。WSL 的 `memory` 限制作用于各 WSL 2 发行版共用的虚拟机，不只限制 MathLottery。swap 使用磁盘，可缓解短时内存压力，但持续换页会让编译明显变慢。

例如，**16 GiB 主机**可以从以下虚拟机配置尝试：

```ini
# Windows: %UserProfile%\.wslconfig
[wsl2]
memory=8GB
processors=4
swap=4GB
```

根据实际余量调整，并与已有配置合并；此示例不是必需配置，也不保证大型构建能完成。生效可能需要在 PowerShell 执行 `wsl --shutdown`，它会停止**所有正在运行的 WSL 发行版及其中的任务**。先保存工作并停止任务，再重启 WSL，用 `free -h` 确认。MathLottery 不会修改这些设置。[微软 WSL 配置说明](https://learn.microsoft.com/en-us/windows/wsl/wsl-config)

## 测量用量与排查失败

在 Linux/WSL 中查看余量和常驻内存较高的进程，以下命令不会打印进程的命令行参数：

```bash
free -h
df -h .
ps -eo pid,ppid,rss,comm --sort=-rss | head -n 15
du -sh .mathlottery runs audits
```

最后一条在 MathLottery 根目录、这些目录已存在后运行。如果 Conda/Elan 位于其他磁盘，也要检查相应文件系统。`free` 中的 **available** 比单看 **free** 更有参考意义，因为文件缓存可能被回收。`ps` 的 RSS 是当前快照，不是峰值；多个进程也可能重复计入共享页面。Windows 显示的 WSL 占用包含 Lean 以外的内存。

测量单文件时，若没有 `/usr/bin/time`，先安装 GNU `time`；进入已有依赖缓存的 Lean 项目，将 `Proof.lean` 换成目标文件：

```bash
env LEAN_NUM_THREADS=1 /usr/bin/time -v lake env lean -j 1 -M 2048 Proof.lean
```

查看 `Maximum resident set size (kbytes)`、耗时和退出码。在 Linux 上，该 RSS 数值除以 1,048,576 可换算为 GiB。对 Lake 构建计时得到的最大值，不等于所有并发子进程占用的总和；要和虚拟机限制比较，还需监测整体工作负载。原始日志和机器诊断应保存到新的、被忽略的 `audits/codex_audits/<timestamp>/` 目录，遵循[本地审计约定](local-validation.cn.md#本地实验审计)。

| 现象 | 下一步检查 |
| --- | --- |
| `lean::memory_exception` / `excessive memory consumption` | Lean 内部阈值，以及 tactic/导入开销；减少工作量，或在可用内存范围内调整阈值。 |
| `Killed`、信号 9 或退出码 137 | 查看权限允许访问的内核、容器或 WSL 日志，确认是否发生 OOM；仅凭退出码不能确定原因。 |
| swap 活动很高且进度极慢 | 减少同时运行的研究、编译或编辑器工作进程，检查可用内存。 |
| `No space left on device` | 检查项目磁盘、工具链磁盘、下载缓存、临时目录与 WSL 的宿主磁盘。 |
| 缺少 `.olean` 或工具链不兼容 | 先恢复固定版本对应的依赖，再决定是否重建。 |

资源不足意味着检查没有完成。保留退出码与日志，既不能记为 Lean 验证通过，也不能据此认定数学命题为假。

## 磁盘增长与清理

工具链、mathlib 的 `.lake/`、压缩缓存、源码编译产物和重复的依赖版本都可能占用很多 GiB。研究历史、下载论文、事件日志与数值输出还会随使用增长；当前没有自动的总磁盘配额或保留期限。除了下载包，也要给解压后的文件留空间；额外环境或独立工作副本可能重复保存依赖。

先测量再清理。确认缓存没有被正在运行的任务使用后，只删除已识别、可重新生成的缓存/构建目录或不再使用的工具链版本；保留复现结果所需的固定源码与证据。**不要为了清缓存而删除整个 `.mathlottery/`**，其中还包含状态数据库、独立账号凭据与原生会话。需要保留研究历史时，也要保留 `problems/` 和 `runs/`。加入 Git ignore 不会自动删除本地文件或减少磁盘占用。

[showcase 展示目录](../showcase/README.cn.md)只包含精简源码与证据样本。复现 Lean 案例时会另行下载大型依赖，这些依赖没有打包进样本。
