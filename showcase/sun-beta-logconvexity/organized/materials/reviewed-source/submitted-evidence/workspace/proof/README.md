# Sun beta 系数对数凸候选证明

提交范围：COMPLETE。原题所有整数中心下标 n≥1、次数 d≥0 都包含在主定理中。独立 Verify 尚未运行；这里不提供独立验证或新颖性评级。

前端选择并冻结 **SunBeta.lean** 即可。全部证明已合并到此文件，其他本项目 Lean 文件不是编译依赖。

- 完整自然语言证明：Proof.md。
- 完整正系数证书表：CertificateTable.md；机器可读表：certificates.json。
- 完整源码：SunBeta.lean（只导入 Lean / Mathlib 模块）。
- 主定理全限定名：`SunBeta.beta_coeffwise_logconvex`。
- 定义：`SunBeta.beta : ℕ → Polynomial ℤ`。

主定理：

```lean
theorem SunBeta.beta_coeffwise_logconvex (n : ℕ) (hn : 1 ≤ n) (d : ℕ) :
  0 ≤ (SunBeta.beta (n-1) * SunBeta.beta (n+1) - SunBeta.beta n ^ 2).coeff d
```

在提供的研究工作区中，用已经安装的工具链编译：

```sh
conda run -n mathlottery python proof/check.py
```

脚本运行时发现已有的 `.mathlottery/toolchains/lean-4.35.0-linux` 与 `mathlib4-v4.35.0`，设置 `LEAN_PATH` 为现有 mathlib 和依赖包的预编译库目录，执行 `lean -j1 -o proof/SunBeta.olean proof/SunBeta.lean`。不使用 Lake 构建，也不下载另一套库。单次时限 900 秒；大多项式恒等式需要数分钟。原始本地输出保留在研究日志目录。

证明只使用标准 Lean/mathlib 公理 `propext`、`Classical.choice`、`Quot.sound`；不使用 `sorry`、`admit`、新公理或 `native_decide`，也不把目标结论作为假设。源码末尾的 `#print axioms` 可用于复核依赖。有限实验只用于发现证书，不是主定理的假设。

独立 Verify 应核查原题与主定理定义的对应、自然语言证书与源码的对应、编译结果及来源/新颖性。数学候选的 COMPLETE 范围不等于 VERIFIED 状态。
