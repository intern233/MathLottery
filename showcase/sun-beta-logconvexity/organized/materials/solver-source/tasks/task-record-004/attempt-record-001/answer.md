已提交 **COMPLETE 候选证明**，覆盖原题全部 \(n\ge1\)、\(d\ge0\)：
\[
[q^d]\bigl(\beta_{n-1}(q)\beta_{n+1}(q)-\beta_n(q)^2\bigr)\ge0.
\]

证明将系数写成正权重卷积，再加入两项求和为零的差分。内部情形归结为两个具有 **334、415 个正系数单项式**的多项式证书；所有边界情形也已处理。这是一般恒等式证明，不依赖有限验算。

- [完整自然语言证明及全部证书表](../../../workspace/proof/Proof.md)
- [完整 Lean 源码](../../../workspace/proof/SunBeta.lean)
- [编译说明](../../../workspace/proof/README.md)
- [已保存的最终提交](../../../../omitted-sources.md#unavailable-attachments)

主定理全限定名：`SunBeta.beta_coeffwise_logconvex`。单一源码已用 **Lean 4.35.0** 本地编译通过，没有 `sorry`、`admit` 或新增公理。复现命令：

```sh
conda run -n mathlottery python proof/check.py
```

最终提交已设置 `conclude: true`、`remaining_obligations: []`。**独立 Verify 尚未运行**；未自行标记为已验证，也未认证文献新颖性。