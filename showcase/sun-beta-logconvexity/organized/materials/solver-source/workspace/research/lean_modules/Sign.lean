import Certificates
import Lean.Elab.Tactic.Omega

set_option maxRecDepth 8192
set_option maxHeartbeats 2000000

namespace SunBeta.Cert

def Q (n k l D a b : ℚ) : ℚ := D*P n k l + a*T0 n k l + b*T1 n k l

theorem Q_symm (n k l D a b : ℚ) : Q n k l D a b = Q n l k D a b := by
  unfold Q
  rw [P_symm n k l, T0_symm n k l, T1_symm n k l]

theorem sorted_suffices (n d : ℕ) (D a b : ℚ)
    (h : ∀ k l : ℕ, k+l=d → k≤n+1 → l≤n+1 → k≤l → 0≤Q n k l D a b) :
    ∀ k l : ℕ, k+l=d → k≤n+1 → l≤n+1 → 0≤Q n k l D a b := by
  intro k l hkl hk hl
  rcases le_total k l with hs | hs
  · exact h k l hkl hk hl hs
  · rw [Q_symm]
    exact h l k (by omega) hl hk hs

theorem even_internal (m r j : ℕ) (hm : 2≤m) (hr : 1≤r)
    (hj : j≤m) (hj' : j≤r+1) : 0≤exprEven m r j := by
  by_cases h0 : j=0
  · subst j; rw [Nat.cast_zero, exprEven_0]
  by_cases h1 : j=1
  · subst j; rw [Nat.cast_one, exprEven_1]
  apply exprEven_nonneg
  · exact_mod_cast (show 2≤j by omega)
  · exact_mod_cast hj
  · exact_mod_cast hj'

theorem odd_internal (m r j : ℕ) (hm : 2≤m) (hr : 1≤r)
    (hj : j≤m) (hj' : j≤r+1) : 0≤exprOdd m r j := by
  by_cases h0 : j=0
  · subst j; rw [Nat.cast_zero, exprOdd_0]
  by_cases h1 : j=1
  · subst j; rw [Nat.cast_one, exprOdd_1]
  apply exprOdd_nonneg
  · exact_mod_cast (show 2≤j by omega)
  · exact_mod_cast hj
  · exact_mod_cast hj'

theorem even_edge (m r j : ℕ) (hm : 1≤m) (he : m=1 ∨ r=0)
    (hj : j≤m) (hj' : j≤r+1) : 0≤edgeExprEven m r j := by
  have jj : j=0 ∨ j=1 := by rcases he with h|h <;> omega
  rcases jj with h|h
  · subst j; rw [Nat.cast_zero, edgeExprEven_0]
  subst j
  rcases he with h|h
  · subst m
    rw [Nat.cast_one, edgeExprEven_small]
    have hpoly : (0:ℚ) ≤ 4+(-3*(r:ℚ))+(3*(r:ℚ)^2) := by nlinarith [sq_nonneg (2*(r:ℚ)-1)]
    positivity
  · subst r
    rw [Nat.cast_zero, Nat.cast_one, edgeExprEven_top]
    positivity

theorem odd_edge (m r j : ℕ) (hm : 1≤m) (he : m=1 ∨ r=0)
    (hj : j≤m) (hj' : j≤r+1) : 0≤edgeExprOdd m r j := by
  have jj : j=0 ∨ j=1 := by rcases he with h|h <;> omega
  rcases jj with h|h
  · subst j; rw [Nat.cast_zero, edgeExprOdd_0]
  subst j
  rcases he with h|h
  · subst m
    rw [Nat.cast_one, edgeExprOdd_small]
    positivity
  · subst r
    rw [Nat.cast_zero, Nat.cast_one, edgeExprOdd_top]
    positivity

theorem certificate_even (m r : ℕ) :
    ∃ D a b : ℚ, 0<D ∧ ∀ k l : ℕ,
      k+l=2*m → k≤m+r+1 → l≤m+r+1 → 0≤Q ((m+r:ℕ):ℚ) k l D a b := by
  by_cases h0 : m=0
  · subst m
    refine ⟨1,0,0,by norm_num,?_⟩
    intro k l hkl hk hl
    have hk0 : k=0 := by omega
    have hl0 : l=0 := by omega
    subst k; subst l
    have he : P (r:ℚ) 0 0 = 0 := by unfold P; ring
    simpa only [Q, Nat.cast_zero, zero_add, one_mul, zero_mul, add_zero, he] using (le_refl (0:ℚ))
  have hm : 1≤m := by omega
  by_cases he : m=1 ∨ r=0
  · refine ⟨edgeDenEven m, edgeAlphaEven m r, 0, ?_, ?_⟩
    · unfold edgeDenEven
      have : (0:ℚ)<m := by exact_mod_cast (show 0<m by omega)
      positivity
    apply sorted_suffices (m+r) (2*m)
    intro k l hkl hk hl hs
    let j := m-k
    have hm' : k≤m := by omega
    have hkj : k+j=m := by dsimp [j]; omega
    have hlj : l=m+j := by omega
    have hj : j≤m := by omega
    have hj' : j≤r+1 := by omega
    have hkq : (k:ℚ)=(m:ℚ)-j := by
      have h : (k:ℚ)+(j:ℚ)=m := by exact_mod_cast hkj
      linarith
    have hlq : (l:ℚ)=(m:ℚ)+j := by exact_mod_cast hlj
    have h := even_edge m r j hm he hj hj'
    simpa only [Q, edgeExprEven, Nat.cast_add, Nat.cast_one, hkq, hlq,
      add_zero, zero_mul] using h
  · have hm2 : 2≤m := by omega
    have hr : 1≤r := by omega
    refine ⟨denEven m r, alphaEven m r, betaEven m r, ?_, ?_⟩
    · unfold denEven
      have : (1:ℚ)<m := by exact_mod_cast (show 1<m by omega)
      have : (0:ℚ)<r := by exact_mod_cast (show 0<r by omega)
      have hdiff : (0:ℚ)< -1+(m:ℚ) := by linarith
      positivity
    apply sorted_suffices (m+r) (2*m)
    intro k l hkl hk hl hs
    let j := m-k
    have hm' : k≤m := by omega
    have hkj : k+j=m := by dsimp [j]; omega
    have hlj : l=m+j := by omega
    have hj : j≤m := by omega
    have hj' : j≤r+1 := by omega
    have hkq : (k:ℚ)=(m:ℚ)-j := by
      have h : (k:ℚ)+(j:ℚ)=m := by exact_mod_cast hkj
      linarith
    have hlq : (l:ℚ)=(m:ℚ)+j := by exact_mod_cast hlj
    have h := even_internal m r j hm2 hr hj hj'
    simpa only [Q, exprEven, Nat.cast_add, Nat.cast_one, hkq, hlq, add_zero] using h

theorem certificate_odd (m r : ℕ) :
    ∃ D a b : ℚ, 0<D ∧ ∀ k l : ℕ,
      k+l=2*m+1 → k≤m+r+1+1 → l≤m+r+1+1 → 0≤Q ((m+r+1:ℕ):ℚ) k l D a b := by
  by_cases h0 : m=0
  · subst m
    refine ⟨1,0,0,by norm_num,?_⟩
    apply sorted_suffices (0+r+1) (2*0+1)
    intro k l hkl hk hl hs
    have hk0 : k=0 := by omega
    have hl1 : l=1 := by omega
    subst k; subst l
    have he : P ((r:ℚ)+1) 0 1 = 2*((r:ℚ)+1)^2*((r:ℚ)+2)^2*(3*r+4) := by unfold P; ring
    simp only [Q, zero_add, Nat.cast_add, Nat.cast_one, Nat.cast_zero, one_mul, zero_mul, add_zero]
    rw [he]
    positivity
  have hm : 1≤m := by omega
  by_cases he : m=1 ∨ r=0
  · refine ⟨edgeDenOdd m, edgeAlphaOdd m r, 0, ?_, ?_⟩
    · unfold edgeDenOdd
      have : (0:ℚ)<m := by exact_mod_cast (show 0<m by omega)
      positivity
    apply sorted_suffices (m+r+1) (2*m+1)
    intro k l hkl hk hl hs
    let j := m-k
    have hm' : k≤m := by omega
    have hkj : k+j=m := by dsimp [j]; omega
    have hlj : l=m+j+1 := by omega
    have hj : j≤m := by omega
    have hj' : j≤r+1 := by omega
    have hkq : (k:ℚ)=(m:ℚ)-j := by
      have h : (k:ℚ)+(j:ℚ)=m := by exact_mod_cast hkj
      linarith
    have hlq : (l:ℚ)=(m:ℚ)+j+1 := by exact_mod_cast hlj
    have h := odd_edge m r j hm he hj hj'
    simpa only [Q, edgeExprOdd, Nat.cast_add, Nat.cast_one, hkq, hlq,
      add_zero, zero_mul] using h
  · have hm2 : 2≤m := by omega
    have hr : 1≤r := by omega
    refine ⟨denOdd m r, alphaOdd m r, betaOdd m r, ?_, ?_⟩
    · unfold denOdd
      have : (1:ℚ)<m := by exact_mod_cast (show 1<m by omega)
      have : (0:ℚ)<r := by exact_mod_cast (show 0<r by omega)
      have hdiff : (0:ℚ)< -1+(m:ℚ) := by linarith
      positivity
    apply sorted_suffices (m+r+1) (2*m+1)
    intro k l hkl hk hl hs
    let j := m-k
    have hm' : k≤m := by omega
    have hkj : k+j=m := by dsimp [j]; omega
    have hlj : l=m+j+1 := by omega
    have hj : j≤m := by omega
    have hj' : j≤r+1 := by omega
    have hkq : (k:ℚ)=(m:ℚ)-j := by
      have h : (k:ℚ)+(j:ℚ)=m := by exact_mod_cast hkj
      linarith
    have hlq : (l:ℚ)=(m:ℚ)+j+1 := by exact_mod_cast hlj
    have h := odd_internal m r j hm2 hr hj hj'
    simpa only [Q, exprOdd, Nat.cast_add, Nat.cast_one, hkq, hlq] using h

theorem exists_certificate (n d : ℕ) (hd : d≤2*n) :
    ∃ D a b : ℚ, 0<D ∧ ∀ k l : ℕ,
      k+l=d → k≤n+1 → l≤n+1 → 0≤Q n k l D a b := by
  have hpar : d=2*(d/2) ∨ d=2*(d/2)+1 := by omega
  rcases hpar with he|ho
  · have hn : n=d/2+(n-d/2) := by omega
    rw [he, hn]
    exact certificate_even (d/2) (n-d/2)
  · have hn : n=d/2+(n-d/2-1)+1 := by omega
    rw [ho, hn]
    exact certificate_odd (d/2) (n-d/2-1)

end SunBeta.Cert
