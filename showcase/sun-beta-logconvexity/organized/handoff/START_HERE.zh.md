# 专家交接：从这里开始

本页为本地自动生成的阅读入口，不新增验证，也不提升证明或新颖性等级。完整细节在双语报告和冻结材料中。

[中文报告](../report.zh.md) · [English report](../report.en.md) · [Structured index](index.json) · [Evidence manifest](../source-manifest.json)

**交付范围：报告正文提及的补充材料或额外附件未必包含在本包中。请按 `source-manifest.json` 核对冻结材料、按 `handoff/files.json` 核对实际导出文件；完整性检查通过只表示索引所列文件的字节匹配，不保证所有被提及的附件齐全。缺失附件须另行提供并说明来源。这是交付边界，不是对数学结论的新否定。**

## 先核对命题与结论

Sun 的 beta 多项式逐系数对数凸猜想（Conjecture 4.7 第一项）

原题完整陈述、假设和来源见 `index.json → problem`；不以标题或摘要代替量词、定义域和边界。

### 1. candidate-record-002

对每个整数 n≥0，令 beta\_n(q)=Σ\_{k=0}^n binom(n,k)^2 binom(n+k,k)q^k∈Z&#91;q&#93;。对所有整数 n≥1 和 d≥0，都有 &#91;q^d&#93;(beta\_{n-1}(q)beta\_{n+1}(q)-beta\_n(q)^2)≥0。完整 Lean 主定理为 SunBeta.beta\_coeffwise\_logconvex，单一源文件 proof/SunBeta.lean。本主张是覆盖原题全部量词的候选证明，不是独立 Verify 的结论。

`PARTIALLY_VERIFIED` · scope `COMPLETE` · review `NO_ISSUES_FOUND` · coverage `FULL` · novelty `UNKNOWN`

[Proof](candidate-1.proof.md) · [All reviews and steps](candidate-1.review.json)

已记录 0 个证明步骤；逐项对照依赖、检查 ID 和未覆盖项。

未完成义务：—

## 形式化覆盖与复现

只对下列回执明确列出的声明主张形式检查；等号情形、推广、最优性等附加结论若未列入，仍需书面复核。自然语言命题与 Lean 定理的对应性不是由编译成功自动确认的。

- candidate-record-002 / review 1: `ERROR`; alignment `NOT_CERTIFIED`

  Lean: Lean (version 4.35.0, x86\_64-unknown-linux-gnu, commit eb6cafb7290e8bd5f2937522d8d804f58f02bafc, Release)

  - [reviewed-source/submitted-evidence/workspace/proof/SunBeta.lean](../materials/reviewed-source/submitted-evidence/workspace/proof/SunBeta.lean), [reviewed-source/review-workspaces/candidate-record-002/audits/codex\_audits/2026-10-23\_06-51-24/SunBeta.lean](../materials/reviewed-source/review-workspaces/candidate-record-002/formal-probes/SunBeta.lean), [solver-source/workspace/proof/SunBeta.lean](../materials/solver-source/workspace/proof/SunBeta.lean); SHA-256 `5664f90350aa84b61f78d8bcc10741591852bc1572f5dbc3f1fb9c0675170aa3`

- candidate-record-002 / review 2: `KERNEL_REPLAYED`; alignment `NOT_CERTIFIED`

  Lean: Lean (version 4.35.0, x86\_64-unknown-linux-gnu, commit eb6cafb7290e8bd5f2937522d8d804f58f02bafc, Release)

  - SunBeta.beta\_coeffwise\_logconvex

  - [reviewed-source/submitted-evidence/workspace/proof/SunBeta.lean](../materials/reviewed-source/submitted-evidence/workspace/proof/SunBeta.lean), [reviewed-source/review-workspaces/candidate-record-002/audits/codex\_audits/2026-10-23\_06-51-24/SunBeta.lean](../materials/reviewed-source/review-workspaces/candidate-record-002/formal-probes/SunBeta.lean), [solver-source/workspace/proof/SunBeta.lean](../materials/solver-source/workspace/proof/SunBeta.lean); SHA-256 `5664f90350aa84b61f78d8bcc10741591852bc1572f5dbc3f1fb9c0675170aa3`

- candidate-record-002 / review 3: `KERNEL_REPLAYED`; alignment `NOT_CERTIFIED`

  Lean: Lean (version 4.35.0, x86\_64-unknown-linux-gnu, commit eb6cafb7290e8bd5f2937522d8d804f58f02bafc, Release)

  - SunBeta.beta\_coeffwise\_logconvex

  - [reviewed-source/submitted-evidence/workspace/proof/SunBeta.lean](../materials/reviewed-source/submitted-evidence/workspace/proof/SunBeta.lean), [reviewed-source/review-workspaces/candidate-record-002/audits/codex\_audits/2026-10-23\_06-51-24/SunBeta.lean](../materials/reviewed-source/review-workspaces/candidate-record-002/formal-probes/SunBeta.lean), [solver-source/workspace/proof/SunBeta.lean](../materials/solver-source/workspace/proof/SunBeta.lean); SHA-256 `5664f90350aa84b61f78d8bcc10741591852bc1572f5dbc3f1fb9c0675170aa3`

1. 解压完整材料包，在包根目录运行 `python handoff/check_files.py`，只核对文件完整性。
2. 在 `index.json` 查看 `formal_checks` 的完整定理类型、axioms、源码哈希和原始 argv；argv 中的隔离路径不能直接在本机执行。
3. 检查冻结的 Lean/Lake 依赖文件，在独立受限环境准备对应版本，核对依赖源码后再重放。缺少依赖锁定或源码时先补齐，不能声称可一键复现。
4. 逐项核对书面证明、Lean 声明与原题；没有自动执行任何材料中的脚本或 Lake 钩子。

### 尚缺的复现条件

- No lean-toolchain file was captured; consult the receipt's recorded Lean version.

- No lake-manifest.json was captured; imported library revisions are not pinned by this handoff.

## 新颖性与专家检查顺序

先读证明，再核对命题范围和关键步骤，最后逐项比较最接近的已有结果。`candidate-*.review.json` 保留全部历史检查和文献障碍；旧失败不会因新审查而消失。请分别记录数学正确性、题意对应和新颖性判断。

公开分享请使用独立的脱敏文本包；原始材料包保留原始字节，可能包含本机路径。脱敏后的源码不能直接继承原始 Lean 回执。
