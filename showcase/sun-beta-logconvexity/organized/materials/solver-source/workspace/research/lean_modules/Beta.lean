import Convolution
import Sign

set_option maxRecDepth 8192
set_option maxHeartbeats 2000000

namespace SunBeta
open scoped BigOperators
open Cert

theorem sumP_nonneg (n d : ℕ) (hn : 1≤n) (hd : d≤2*n) :
    0 ≤ ∑ p ∈ Finset.antidiagonal d, w n p.1*w n p.2*P n p.1 p.2 := by
  obtain ⟨D,c0,c1,hD,hcert⟩ := exists_certificate n d hd
  have ht := weighted_telescopes n d hn c0 c1
  have hpos : 0 ≤ ∑ p ∈ Finset.antidiagonal d, w n p.1*w n p.2*Q n p.1 p.2 D c0 c1 := by
    apply Finset.sum_nonneg
    intro p hp
    have hkl := Finset.mem_antidiagonal.mp hp
    by_cases hk : p.1≤n+1
    · by_cases hl : p.2≤n+1
      · exact mul_nonneg (mul_nonneg (w_nonneg _ _) (w_nonneg _ _)) (hcert _ _ hkl hk hl)
      · rw [w_zero (by omega : n+1<p.2)]
        simp
    · rw [w_zero (by omega : n+1<p.1)]
      simp
  have heq : (∑ p ∈ Finset.antidiagonal d, w n p.1*w n p.2*Q n p.1 p.2 D c0 c1) =
      D*(∑ p ∈ Finset.antidiagonal d, w n p.1*w n p.2*P n p.1 p.2) := by
    calc
      (∑ p ∈ Finset.antidiagonal d, w n p.1*w n p.2*Q n p.1 p.2 D c0 c1) =
        ∑ p ∈ Finset.antidiagonal d, (D*(w n p.1*w n p.2*P n p.1 p.2)+
          w n p.1*w n p.2*(c0*T0 n p.1 p.2+c1*T1 n p.1 p.2)) := by
            apply Finset.sum_congr rfl
            intro p hp
            unfold Q
            ring
      _ = _ := by rw [Finset.sum_add_distrib, ← Finset.mul_sum, ht, add_zero]
  rw [heq] at hpos
  exact nonneg_of_mul_nonneg_right hpos hD

theorem delta_nonneg (s d : ℕ) : 0≤delta s d := by
  by_cases hd : d≤2*(s+1)
  · have h := sumP_nonneg (s+1) d (by omega) hd
    have he := delta_sum s d
    simp only [Nat.cast_add, Nat.cast_one] at h
    rw [← he] at h
    have hpos : (0:ℚ)<2*((s:ℚ)+1) := by positivity
    exact nonneg_of_mul_nonneg_right h hpos
  · unfold delta
    apply Finset.sum_nonneg
    intro p hp
    have hkl := Finset.mem_antidiagonal.mp hp
    have hleft : a s p.1*a (s+2) p.2=0 := by
      by_cases hk : s<p.1
      · rw [a_zero hk]; ring
      · have hl : s+2<p.2 := by omega
        rw [a_zero hl]; ring
    have hright : a (s+1) p.1*a (s+1) p.2=0 := by
      by_cases hk : s+1<p.1
      · rw [a_zero hk]; ring
      · have hl : s+1<p.2 := by omega
        rw [a_zero hl]; ring
    rw [hleft,hright]
    norm_num

theorem logconvex_step (s d : ℕ) :
    0≤(beta s*beta (s+2)-beta (s+1)^2).coeff d := by
  have h : (0:ℚ)≤((beta s*beta (s+2)-beta (s+1)^2).coeff d : ℤ) := by
    rw [delta_coeff]
    exact delta_nonneg s d
  exact_mod_cast h

/-- Sun's original beta-polynomial coefficientwise log-convexity statement.
    Every center n ≥ 1 and every degree d ≥ 0 are included. -/
theorem beta_coeffwise_logconvex (n : ℕ) (hn : 1≤n) (d : ℕ) :
    0≤(beta (n-1)*beta (n+1)-beta n^2).coeff d := by
  have h := logconvex_step (n-1) d
  have h1 : n-1+1=n := by omega
  have h2 : n-1+2=n+1 := by omega
  simpa only [h1,h2] using h

#print axioms SunBeta.beta_coeffwise_logconvex

end SunBeta
