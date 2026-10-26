import Mathlib.Algebra.Polynomial.Coeff
import Mathlib.Algebra.BigOperators.NatAntidiagonal
import Mathlib.Data.Nat.Choose.Basic
import Mathlib.Data.Rat.Cast.Order
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.NormNum
import Lean.Elab.Tactic.Omega

set_option maxRecDepth 4096
set_option maxHeartbeats 1000000

namespace SunBeta
open scoped BigOperators

noncomputable def beta (n : ℕ) : Polynomial ℤ :=
  ∑ k ∈ Finset.range (n+1),
    Polynomial.monomial k ((n.choose k : ℤ)^2 * ((n+k).choose k : ℤ))

def a (n k : ℕ) : ℚ := (n.choose k : ℚ)^2 * ((n+k).choose k : ℚ)

theorem a_nonneg (n k : ℕ) : 0 ≤ a n k := by unfold a; positivity

theorem a_zero {n k : ℕ} (h : n < k) : a n k = 0 := by
  simp [a, Nat.choose_eq_zero_of_lt h]

theorem choose_row (n k : ℕ) :
    ((n+1).choose k : ℚ) * ((n:ℚ)+1-k) = (n.choose k : ℚ)*((n:ℚ)+1) := by
  by_cases hk : k ≤ n+1
  · have h := congrArg (fun z : ℕ => (z : ℚ)) (Nat.choose_mul_succ_eq n k)
    push_cast [Nat.cast_sub hk] at h
    exact h.symm
  · have h1 : n+1 < k := by omega
    have h0 : n < k := by omega
    simp [Nat.choose_eq_zero_of_lt h1, Nat.choose_eq_zero_of_lt h0]

theorem choose_col (n k : ℕ) :
    (n.choose (k+1) : ℚ)*((k:ℚ)+1) = (n.choose k : ℚ)*((n:ℚ)-k) := by
  by_cases hk : k ≤ n
  · have h := congrArg (fun z : ℕ => (z : ℚ)) (Nat.choose_succ_right_eq n k)
    push_cast [Nat.cast_sub hk] at h
    exact h
  · have h0 : n < k := by omega
    have h1 : n < k+1 := by omega
    simp [Nat.choose_eq_zero_of_lt h0, Nat.choose_eq_zero_of_lt h1]

theorem choose_rising (n k : ℕ) :
    ((n+k+1).choose k : ℚ)*((n:ℚ)+1) =
    ((n+k).choose k : ℚ)*((n:ℚ)+k+1) := by
  have h := choose_row (n+k) k
  push_cast at h
  convert h using 1 <;> ring

theorem a_row (n k : ℕ) :
    a (n+1) k * ((n:ℚ)+1-k)^2 =
    ((n:ℚ)+1)*((n:ℚ)+k+1)*a n k := by
  have h1 := choose_row n k
  have h2 := choose_rising n k
  have he : n+1+k = n+k+1 := by omega
  unfold a
  rw [he]
  calc
    ((n+1).choose k : ℚ)^2 * ((n+k+1).choose k : ℚ) * ((n:ℚ)+1-k)^2 =
        (((n+1).choose k : ℚ)*((n:ℚ)+1-k))^2 * ((n+k+1).choose k : ℚ) := by ring
    _ = ((n.choose k : ℚ)*((n:ℚ)+1))^2 * ((n+k+1).choose k : ℚ) := by rw [h1]
    _ = (n.choose k : ℚ)^2*((n:ℚ)+1)*(((n+k+1).choose k : ℚ)*((n:ℚ)+1)) := by ring
    _ = _ := by rw [h2]; ring

theorem a_col (n k : ℕ) :
    a n (k+1) * ((k:ℚ)+1)^3 =
    a n k*((n:ℚ)-k)^2*((n:ℚ)+k+1) := by
  have h1 := choose_col n k
  have h2 := congrArg (fun z : ℕ => (z : ℚ)) (Nat.add_one_mul_choose_eq (n+k) k)
  push_cast at h2
  have he : n+(k+1) = n+k+1 := by omega
  unfold a
  rw [he]
  calc
    (n.choose (k+1) : ℚ)^2 * ((n+k+1).choose (k+1) : ℚ) * ((k:ℚ)+1)^3 =
      ((n.choose (k+1) : ℚ)*((k:ℚ)+1))^2 *
        (((n+k+1).choose (k+1) : ℚ)*((k:ℚ)+1)) := by ring
    _ = ((n.choose k : ℚ)*((n:ℚ)-k))^2 *
        (((n:ℚ)+k+1)*((n+k).choose k : ℚ)) := by rw [h1, ← h2]
    _ = _ := by ring

def w (n k : ℕ) : ℚ :=
  a (n+1) k / (((n:ℚ)+1)*((n:ℚ)+k)*((n:ℚ)+k+1))

theorem w_nonneg (n k : ℕ) : 0 ≤ w n k := by
  unfold w
  exact div_nonneg (a_nonneg _ _) (by positivity)

theorem w_zero {n k : ℕ} (h : n+1 < k) : w n k = 0 := by
  simp [w, a_zero h]

theorem w_above (n k : ℕ) (hn : 1 ≤ n) :
    a (n+1) k = w n k*((n:ℚ)+1)*((n:ℚ)+k)*((n:ℚ)+k+1) := by
  have hn' : (0:ℚ) < n := by exact_mod_cast (show 0 < n by omega)
  unfold w
  field_simp
  <;> ring

theorem w_center (n k : ℕ) (hn : 1 ≤ n) :
    a n k = w n k*((n:ℚ)+k)*((n:ℚ)-k+1)^2 := by
  have hn' : (0:ℚ) < n := by exact_mod_cast (show 0 < n by omega)
  have h := a_row n k
  unfold w
  field_simp
  nlinarith [h]

theorem w_below (s k : ℕ) :
    ((s:ℚ)+1)*a s k =
    w (s+1) k*((s:ℚ)+1-k+1)^2*((s:ℚ)+1-k)^2 := by
  have hc := w_center (s+1) k (by omega)
  have h := a_row s k
  push_cast at hc
  rw [hc] at h
  have hn : (0:ℚ) < (s:ℚ)+k+1 := by positivity
  apply (mul_right_cancel₀ (ne_of_gt hn))
  nlinarith [h]

theorem w_recur (n k : ℕ) (hn : 1 ≤ n) :
    w n (k+1)*((k:ℚ)+1)^3 = w n k*((n:ℚ)+k)*((n:ℚ)-k+1)^2 := by
  have hn' : (0:ℚ) < n := by exact_mod_cast (show 0 < n by omega)
  have h := a_col (n+1) k
  push_cast at h
  unfold w
  push_cast
  field_simp
  nlinarith [h]

end SunBeta
