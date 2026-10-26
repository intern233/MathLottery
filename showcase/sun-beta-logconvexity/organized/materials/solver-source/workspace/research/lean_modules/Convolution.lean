import Basic
import CertificateData

set_option maxRecDepth 4096
set_option maxHeartbeats 2000000

namespace SunBeta
open scoped BigOperators
open Cert

-- The flux vanishes at both ends of each finite antidiagonal.
def flux (u : ℕ → ℚ) (c0 c1 : ℚ) (k l : ℕ) : ℚ :=
  u k*u l*(k:ℚ)^3*(l:ℚ)^3*((k:ℚ)-l)*
    (c0+c1*((k:ℚ)-1)*((l:ℚ)-1))

theorem flux_sum (u : ℕ → ℚ) (c0 c1 : ℚ) (d : ℕ) :
    (∑ p ∈ Finset.antidiagonal d,
      (flux u c0 c1 (p.1+1) p.2 - flux u c0 c1 p.1 (p.2+1))) = 0 := by
  have h0 := Finset.Nat.sum_antidiagonal_succ
    (n:=d) (f:=fun p => flux u c0 c1 p.1 p.2)
  have h1 := Finset.Nat.sum_antidiagonal_succ'
    (n:=d) (f:=fun p => flux u c0 c1 p.1 p.2)
  have e0 : flux u c0 c1 0 (d+1) = 0 := by simp [flux]
  have e1 : flux u c0 c1 (d+1) 0 = 0 := by simp [flux]
  simp only [e0, e1, zero_add] at h0 h1
  rw [Finset.sum_sub_distrib]
  exact sub_eq_zero.mpr (h0.symm.trans h1)

theorem weighted_flux (n k l : ℕ) (hn : 1≤n) (c0 c1 : ℚ) :
    w n k*w n l*(c0*T0 n k l+c1*T1 n k l) =
      flux (w n) c0 c1 (k+1) l - flux (w n) c0 c1 k (l+1) := by
  calc
    w n k*w n l*(c0*T0 n k l+c1*T1 n k l) =
      (w n k*((n:ℚ)+k)*((n:ℚ)-k+1)^2)*w n l*(l:ℚ)^3*
        ((k:ℚ)-l+1)*(c0+c1*(k:ℚ)*((l:ℚ)-1)) -
      w n k*(k:ℚ)^3*(w n l*((n:ℚ)+l)*((n:ℚ)-l+1)^2)*
        ((k:ℚ)-l-1)*(c0+c1*((k:ℚ)-1)*(l:ℚ)) := by
          unfold T0 T1 A
          ring
    _ = _ := by
      rw [← w_recur n k hn, ← w_recur n l hn]
      unfold flux
      push_cast
      ring

theorem weighted_telescopes (n d : ℕ) (hn : 1≤n) (c0 c1 : ℚ) :
    (∑ p ∈ Finset.antidiagonal d,
      w n p.1*w n p.2*(c0*T0 n p.1 p.2+c1*T1 n p.1 p.2)) = 0 := by
  simp_rw [weighted_flux n _ _ hn]
  exact flux_sum (w n) c0 c1 d

theorem paired_term (s k l : ℕ) :
    ((s:ℚ)+1)*(a s k*a (s+2) l+a (s+2) k*a s l-
      2*a (s+1) k*a (s+1) l) =
    w (s+1) k*w (s+1) l*P ((s:ℚ)+1) k l := by
  have hk0 := w_below s k
  have hl0 := w_below s l
  have hk1 := w_center (s+1) k (by omega)
  have hl1 := w_center (s+1) l (by omega)
  have hk2 := w_above (s+1) k (by omega)
  have hl2 := w_above (s+1) l (by omega)
  simp only [Nat.cast_add, Nat.cast_one] at hk1 hl1 hk2 hl2
  have es : s+1+1=s+2 := by omega
  rw [es] at hk2 hl2
  calc
    ((s:ℚ)+1)*(a s k*a (s+2) l+a (s+2) k*a s l-
      2*a (s+1) k*a (s+1) l) =
      (((s:ℚ)+1)*a s k)*a (s+2) l +
      a (s+2) k*(((s:ℚ)+1)*a s l) -
      2*((s:ℚ)+1)*a (s+1) k*a (s+1) l := by ring
    _ = _ := by rw [hk0,hl0,hk1,hl1,hk2,hl2]; unfold P; ring

def delta (s d : ℕ) : ℚ :=
  ∑ p ∈ Finset.antidiagonal d,
    (a s p.1*a (s+2) p.2-a (s+1) p.1*a (s+1) p.2)

theorem delta_sum (s d : ℕ) :
    2*((s:ℚ)+1)*delta s d =
      ∑ p ∈ Finset.antidiagonal d, w (s+1) p.1*w (s+1) p.2*P ((s:ℚ)+1) p.1 p.2 := by
  have hswap : (∑ p ∈ Finset.antidiagonal d, a (s+2) p.1*a s p.2) =
      ∑ p ∈ Finset.antidiagonal d, a s p.1*a (s+2) p.2 := by
    simpa only [Prod.swap, mul_comm] using
      (Finset.Nat.sum_antidiagonal_swap (n:=d) (f:=fun p => a s p.1*a (s+2) p.2))
  rw [show (∑ p ∈ Finset.antidiagonal d, w (s+1) p.1*w (s+1) p.2*P ((s:ℚ)+1) p.1 p.2) =
      ∑ p ∈ Finset.antidiagonal d, ((s:ℚ)+1)*(a s p.1*a (s+2) p.2+
        a (s+2) p.1*a s p.2-2*a (s+1) p.1*a (s+1) p.2) from
          Finset.sum_congr rfl (fun p hp => (paired_term s p.1 p.2).symm)]
  unfold delta
  simp only [Finset.sum_add_distrib, Finset.sum_sub_distrib, ← Finset.mul_sum,
    mul_assoc, ← Finset.sum_mul]
  rw [hswap]
  ring

theorem beta_coeff (n k : ℕ) :
    (beta n).coeff k = (n.choose k : ℤ)^2*((n+k).choose k : ℤ) := by
  unfold beta
  rw [Polynomial.finsetSum_coeff]
  simp only [Polynomial.coeff_monomial]
  by_cases hk : k<n+1
  · rw [Finset.sum_eq_single k]
    · simp
    · intro b hb hbk; simp [hbk]
    · simp [Finset.mem_range, hk]
  · have hz : n<k := by omega
    have hn : (n.choose k : ℤ)=0 := by simp [Nat.choose_eq_zero_of_lt hz]
    rw [hn]
    simp only [zero_pow (by decide : 2≠0), zero_mul]
    apply Finset.sum_eq_zero
    intro b hb
    have hbk : b≠k := by have := Finset.mem_range.mp hb; omega
    simp [hbk]

theorem delta_coeff (s d : ℕ) :
    (((beta s*beta (s+2)-beta (s+1)^2).coeff d : ℤ) : ℚ) = delta s d := by
  rw [Polynomial.coeff_sub, pow_two, Polynomial.coeff_mul, Polynomial.coeff_mul]
  simp_rw [beta_coeff]
  unfold delta a
  push_cast
  rw [Finset.sum_sub_distrib]

end SunBeta
