# 专家交接：从这里开始

本页为本地自动生成的阅读入口，不新增验证，也不提升证明或新颖性等级。完整细节在双语报告和冻结材料中。

[中文报告](../report.zh.md) · [English report](../report.en.md) · [Structured index](index.json) · [Evidence manifest](../source-manifest.json)

**交付范围：报告正文提及的补充材料或额外附件未必包含在本包中。请按 `source-manifest.json` 核对冻结材料、按 `handoff/files.json` 核对实际导出文件；完整性检查通过只表示索引所列文件的字节匹配，不保证所有被提及的附件齐全。缺失附件须另行提供并说明来源。这是交付边界，不是对数学结论的新否定。**

## 先核对命题与结论

三次 Franel 多项式从 F\_8 起的逐系数对数凸性

原题完整陈述、假设和来源见 `index.json → problem`；不以标题或摘要代替量词、定义域和边界。

### 1. candidate-record-002

令 F\_n(q)=sum\_{k=0}^n binom(n,k)^3 q^k。对所有整数 n&gt;=9、d&gt;=0，有 &#91;q^d&#93;(F\_{n-1}(q)F\_{n+1}(q)-F\_n(q)^2)&gt;=0；更强地，当 1&lt;=d&lt;=2n-1 时该系数严格为正，在 d=0、d=2n 或 d&gt;2n 时为零。因此原题从 F\_8 开始的尾序列逐系数 q-log-convex。

`SELF_CHECKED` · scope `COMPLETE` · review `NO_ISSUES_FOUND` · coverage `FULL` · novelty `UNKNOWN`

[Proof](candidate-1.proof.md) · [All reviews and steps](candidate-1.review.json)

已记录 0 个证明步骤；逐项对照依赖、检查 ID 和未覆盖项。

未完成义务：—

## 形式化覆盖与复现

只对下列回执明确列出的声明主张形式检查；等号情形、推广、最优性等附加结论若未列入，仍需书面复核。自然语言命题与 Lean 定理的对应性不是由编译成功自动确认的。

1. 解压完整材料包，在包根目录运行 `python handoff/check_files.py`，只核对文件完整性。
2. 在 `index.json` 查看 `formal_checks` 的完整定理类型、axioms、源码哈希和原始 argv；argv 中的隔离路径不能直接在本机执行。
3. 检查冻结的 Lean/Lake 依赖文件，在独立受限环境准备对应版本，核对依赖源码后再重放。缺少依赖锁定或源码时先补齐，不能声称可一键复现。
4. 逐项核对书面证明、Lean 声明与原题；没有自动执行任何材料中的脚本或 Lake 钩子。

### 尚缺的复现条件

- No formal execution receipt is recorded; this handoff does not establish Lean verification.

## 新颖性与专家检查顺序

先读证明，再核对命题范围和关键步骤，最后逐项比较最接近的已有结果。`candidate-*.review.json` 保留全部历史检查和文献障碍；旧失败不会因新审查而消失。请分别记录数学正确性、题意对应和新颖性判断。

公开分享请使用独立的脱敏文本包；原始材料包保留原始字节，可能包含本机路径。脱敏后的源码不能直接继承原始 Lean 回执。
