import Mathlib.Analysis.Convex.Mul
import Mathlib.Analysis.Convex.Jensen
import Mathlib.Basic.Real.Basic
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.Ring

/-!
Elementary real inequalities used in the proof of Conjecture 5.
The geometric hypotheses are established in MedialGeometry, not assumed
in the final theorem. The power-sum route was suggested in the supplied
controller feasibility note; every step below is proved independently.
-/

namespace ZengFeiYang
set_option autoImplicit false
open Set

/-- A convex power sum with fixed total is largest at the interval endpoints. -/
lemma two_power_le (a s t : ℝ) (hs : 0 ≤ s) (hsa : s ≤ a)
    (ht : t ∈ Icc s a) (n : ℕ) :
    t ^ n + (a + s - t) ^ n ≤ a ^ n + s ^ n := by
  have hi : ConvexOn ℝ (Icc s a) (fun u : ℝ => u) := convexOn_id (convex_Icc s a)
  have hj : ConvexOn ℝ (Icc s a) (fun u : ℝ => a + s - u) :=
    (convexOn_const (a + s) (convex_Icc s a)).sub (concaveOn_id (convex_Icc s a))
  have hp : ConvexOn ℝ (Icc s a) (fun u : ℝ => u ^ n + (a + s - u) ^ n) :=
    (hi.pow (fun u hu => hs.trans hu.1) n).add
      (hj.pow (fun u hu => by linarith [hu.2]) n)
  have h := hp.le_max_of_mem_Icc (show s ∈ Icc s a from ⟨le_rfl, hsa⟩)
    (show a ∈ Icc s a from ⟨hsa, le_rfl⟩) ht
  simpa [add_sub_cancel_left, add_sub_cancel_right, add_comm] using h

lemma three_power_lt_of_large (a s t u v : ℝ) (hs : 0 < s) (hsa : s ≤ a)
    (hu : 0 ≤ u) (hv : 0 ≤ v) (hst : s ≤ t) (hta : t ≤ a)
    (hsum : t + u + v < a + s) (n : ℕ) (hn : 1 ≤ n) :
    t ^ n + u ^ n + v ^ n < a ^ n + s ^ n := by
  have hn0 : n ≠ 0 := by omega
  have hsmall : u ^ n + v ^ n ≤ (u + v) ^ n := pow_add_pow_le hu hv hn0
  have hstrict : (u + v) ^ n < (a + s - t) ^ n :=
    pow_lt_pow_left₀ (by linarith) (add_nonneg hu hv) hn0
  have hpair := two_power_le a s t hs.le hsa ⟨hst, hta⟩ n
  linarith

/-- Strict weak-majorization bound for three nonnegative numbers. -/
lemma three_power_lt (a s p q r : ℝ) (hs : 0 < s) (hsa : s ≤ a)
    (hp : 0 ≤ p) (hq : 0 ≤ q) (hr : 0 ≤ r)
    (hpa : p ≤ a) (hqa : q ≤ a) (hra : r ≤ a)
    (hsum : p + q + r < a + s) (n : ℕ) (hn : 1 ≤ n) :
    p ^ n + q ^ n + r ^ n < a ^ n + s ^ n := by
  by_cases hps : p ≤ s
  · by_cases hqs : q ≤ s
    · by_cases hrs : r ≤ s
      · obtain ⟨k, rfl⟩ := Nat.exists_eq_succ_of_ne_zero (by omega : n ≠ 0)
        have hpk := mul_le_mul_of_nonneg_left (pow_le_pow_left₀ hp hps k) hp
        have hqk := mul_le_mul_of_nonneg_left (pow_le_pow_left₀ hq hqs k) hq
        have hrk := mul_le_mul_of_nonneg_left (pow_le_pow_left₀ hr hrs k) hr
        have hak := mul_le_mul_of_nonneg_left (pow_le_pow_left₀ hs.le hsa k)
          (hs.le.trans hsa)
        have hstrict := mul_lt_mul_of_pos_right hsum (pow_pos hs k)
        simp only [pow_succ] at *
        nlinarith
      · have h := three_power_lt_of_large a s r p q hs hsa hp hq
          (le_of_lt (lt_of_not_ge hrs)) hra (by linarith) n hn
        linarith
    · have h := three_power_lt_of_large a s q p r hs hsa hp hr
        (le_of_lt (lt_of_not_ge hqs)) hqa (by linarith) n hn
      linarith
  · exact three_power_lt_of_large a s p q r hs hsa hq hr
      (le_of_lt (lt_of_not_ge hps)) hpa hsum n hn

/-- Recover the two different maximum weights from the unweighted bound. -/
lemma weighted_lt (a s p q r x y z : ℝ) (hp : 0 ≤ p) (hq : 0 ≤ q) (hr : 0 ≤ r)
    (hps : p ≤ s) (hra : r ≤ a) (hsum : p + q + r < a + s)
    (hx : 0 < x) (_hy : 0 < y) (hz : 0 < z) :
    x * p + y * q + z * r < max x y * s + max y z * a := by
  let U := max x y
  let V := max y z
  have hxU : x ≤ U := le_max_left _ _
  have hyU : y ≤ U := le_max_right _ _
  have hyV : y ≤ V := le_max_left _ _
  have hzV : z ≤ V := le_max_right _ _
  have hU : 0 < U := lt_of_lt_of_le hx hxU
  have hV : 0 < V := lt_of_lt_of_le hz hzV
  change x * p + y * q + z * r < U * s + V * a
  rcases le_total V U with hVU | hUV
  · have h1 := mul_le_mul_of_nonneg_right hxU hp
    have h2 := mul_le_mul_of_nonneg_right hyV hq
    have h3 := mul_le_mul_of_nonneg_right hzV hr
    have h4 := mul_lt_mul_of_pos_left hsum hV
    have h5 := mul_le_mul_of_nonneg_left hps (sub_nonneg.mpr hVU)
    nlinarith
  · have h1 := mul_le_mul_of_nonneg_right hxU hp
    have h2 := mul_le_mul_of_nonneg_right hyU hq
    have h3 := mul_le_mul_of_nonneg_right hzV hr
    have h4 := mul_lt_mul_of_pos_left hsum hU
    have h5 := mul_le_mul_of_nonneg_left hra (sub_nonneg.mpr hUV)
    nlinarith

end ZengFeiYang
