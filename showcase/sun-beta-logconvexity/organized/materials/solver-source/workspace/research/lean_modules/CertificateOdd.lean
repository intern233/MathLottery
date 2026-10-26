import CertificateData
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace SunBeta.Cert

theorem posOdd_nonneg (u v t : ℚ) (hu : 0 ≤ u) (hv : 0 ≤ v) (ht : 0 ≤ t) :
    0 ≤ posOdd u v t := by
  unfold posOdd
  positivity

theorem identityOdd (u v t : ℚ) :
    exprOdd (t+2+u) (t+1+v) (t+2) =
    2*((t+2)*(t+1)*(t+3)*(t+4))*posOdd u v t := by
  unfold exprOdd denOdd alphaOdd betaOdd P T0 T1 A posOdd
  ring

theorem exprOdd_0 (m r : ℚ) : exprOdd m r 0 = 0 := by
  unfold exprOdd denOdd alphaOdd betaOdd P T0 T1 A
  ring

theorem exprOdd_1 (m r : ℚ) : exprOdd m r 1 = 0 := by
  unfold exprOdd denOdd alphaOdd betaOdd P T0 T1 A
  ring

theorem exprOdd_nonneg (m r j : ℚ) (hj : 2 ≤ j)
    (hm : j ≤ m) (hr : j ≤ r+1) : 0 ≤ exprOdd m r j := by
  have he := identityOdd (m-j) (r+1-j) (j-2)
  have hp := posOdd_nonneg (m-j) (r+1-j) (j-2) (by linarith) (by linarith) (by linarith)
  have hf : 0 ≤ (j-2+2)*(j-2+1)*(j-2+3)*(j-2+4) := by
    apply mul_nonneg
    · apply mul_nonneg
      · apply mul_nonneg <;> linarith
      · linarith
    · linarith
  have hnon : 0 ≤ exprOdd (j-2+2+(m-j)) (j-2+1+(r+1-j)) (j-2+2) := by
    rw [he]
    exact mul_nonneg (mul_nonneg (by norm_num) hf) hp
  convert hnon using 1 <;> congr 1 <;> ring

theorem edgeExprOdd_0 (m r : ℚ) : edgeExprOdd m r 0 = 0 := by
  unfold edgeExprOdd edgeDenOdd edgeAlphaOdd P T0 A
  ring

theorem edgeExprOdd_small (r : ℚ) : edgeExprOdd 1 r 1 = (36 * ((3 + r) ^ 2) * (2 + r) * (14 + (2 * (r ^ 2)) + (9 * r))) := by
  unfold edgeExprOdd edgeDenOdd edgeAlphaOdd P T0 A
  ring

theorem edgeExprOdd_top (m : ℚ) : edgeExprOdd m 0 1 = (144 * m * ((2 + m) ^ 2) * (4 + (3 * m))) := by
  unfold edgeExprOdd edgeDenOdd edgeAlphaOdd P T0 A
  ring

end SunBeta.Cert
