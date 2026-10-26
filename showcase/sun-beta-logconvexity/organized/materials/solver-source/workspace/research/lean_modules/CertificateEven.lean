import CertificateData
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace SunBeta.Cert

theorem posEven_nonneg (u v t : ℚ) (hu : 0 ≤ u) (hv : 0 ≤ v) (ht : 0 ≤ t) :
    0 ≤ posEven u v t := by
  unfold posEven
  positivity

theorem identityEven (u v t : ℚ) :
    exprEven (t+2+u) (t+1+v) (t+2) =
    2*((t+2)^2*((t+2)^2-1))*posEven u v t := by
  unfold exprEven denEven alphaEven betaEven P T0 T1 A posEven
  ring

theorem exprEven_0 (m r : ℚ) : exprEven m r 0 = 0 := by
  unfold exprEven denEven alphaEven betaEven P T0 T1 A
  ring

theorem exprEven_1 (m r : ℚ) : exprEven m r 1 = 0 := by
  unfold exprEven denEven alphaEven betaEven P T0 T1 A
  ring

theorem exprEven_nonneg (m r j : ℚ) (hj : 2 ≤ j)
    (hm : j ≤ m) (hr : j ≤ r+1) : 0 ≤ exprEven m r j := by
  have he := identityEven (m-j) (r+1-j) (j-2)
  have hp := posEven_nonneg (m-j) (r+1-j) (j-2) (by linarith) (by linarith) (by linarith)
  have hf : 0 ≤ (j-2+2)^2*((j-2+2)^2-1) := by
    apply mul_nonneg (sq_nonneg _)
    nlinarith [sq_nonneg (j-1)]
  have hnon : 0 ≤ exprEven (j-2+2+(m-j)) (j-2+1+(r+1-j)) (j-2+2) := by
    rw [he]
    exact mul_nonneg (mul_nonneg (by norm_num) hf) hp
  convert hnon using 1 <;> congr 1 <;> ring

theorem edgeExprEven_0 (m r : ℚ) : edgeExprEven m r 0 = 0 := by
  unfold edgeExprEven edgeDenEven edgeAlphaEven P T0 A
  ring

theorem edgeExprEven_small (r : ℚ) : edgeExprEven 1 r 1 = (2 * ((2 + r) ^ 2) * (1 + r) * (4 + (-3 * r) + (3 * (r ^ 2)))) := by
  unfold edgeExprEven edgeDenEven edgeAlphaEven P T0 A
  ring

theorem edgeExprEven_top (m : ℚ) : edgeExprEven m 0 1 = (8 * m * ((1 + m) ^ 2)) := by
  unfold edgeExprEven edgeDenEven edgeAlphaEven P T0 A
  ring

end SunBeta.Cert
