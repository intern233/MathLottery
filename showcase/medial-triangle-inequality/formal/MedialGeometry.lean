import Mathlib.Analysis.Normed.Module.Convex
import Mathlib.Geometry.Euclidean.Triangle
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.Ring

namespace ZengFeiYang
set_option autoImplicit false
open Set

/-- The median estimates needed below follow from Apollonius and the side order.
No strict triangle inequality is needed. -/
lemma median_estimates (a b c u v w : ℝ) (hc : 0 < c) (hcb : c ≤ b) (hba : b ≤ a)
    (hu2 : 4 * u ^ 2 = 2 * b ^ 2 + 2 * c ^ 2 - a ^ 2)
    (hv2 : 4 * v ^ 2 = 2 * a ^ 2 + 2 * c ^ 2 - b ^ 2)
    (hw2 : 4 * w ^ 2 = 2 * a ^ 2 + 2 * b ^ 2 - c ^ 2) :
    u < (b + c) / 2 ∧ v < a ∧ w < a ∧
      v + b < a + (b + c) / 2 ∧ w + c < a + (b + c) / 2 := by
  have hb : 0 < b := hc.trans_le hcb
  have ha : 0 < a := hb.trans_le hba
  have hcb2 : c ^ 2 ≤ b ^ 2 := pow_le_pow_left₀ hc.le hcb 2
  have hba2 : b ^ 2 ≤ a ^ 2 := pow_le_pow_left₀ hb.le hba 2
  have hc2 : 0 < c ^ 2 := sq_pos_of_pos hc
  have ha2 : 0 < a ^ 2 := sq_pos_of_pos ha
  have hua : u < (b + c) / 2 := by
    have he : 0 < (a - b + c) * (a + b - c) :=
      mul_pos (by linarith) (by linarith)
    nlinarith [sq_nonneg (u - (b + c) / 2)]
  have hva : v < a := by nlinarith [sq_nonneg (v - a)]
  have hwa : w < a := by nlinarith [sq_nonneg (w - a)]
  have hvsum : v + b < a + (b + c) / 2 := by
    have he : 0 < c * (4 * a - 2 * b - c) := mul_pos hc (by linarith)
    nlinarith [sq_nonneg (a - b), sq_nonneg (v - (a + (c - b) / 2))]
  have hwsum : w + c < a + (b + c) / 2 := by
    have he : 0 < b * (4 * a - 2 * c - b) := mul_pos hb (by linarith)
    nlinarith [sq_nonneg (a - c), sq_nonneg (w - (a + (b - c) / 2))]
  exact ⟨hua, hva, hwa, hvsum, hwsum⟩

variable {E : Type*} [NormedAddCommGroup E] [InnerProductSpace ℝ E]

/-- The filled medial triangle, including its three edges. -/
def medialTriangle (A B C : E) : Set E :=
  convexHull ℝ {midpoint ℝ B C, midpoint ℝ A C, midpoint ℝ A B}

lemma convex_lt_on_hull {f : E → ℝ} (hf : ConvexOn ℝ univ f)
    {T : Set E} {M : ℝ} (hT : ∀ Q ∈ T, f Q < M) :
    ∀ P ∈ convexHull ℝ T, f P < M := by
  have hsub : T ⊆ {Q ∈ (univ : Set E) | f Q < M} := fun Q hQ => ⟨mem_univ Q, hT Q hQ⟩
  intro P hP
  exact (convexHull_min hsub (hf.convex_lt M) hP).2

lemma convex_le_on_hull {f : E → ℝ} (hf : ConvexOn ℝ univ f)
    {T : Set E} {M : ℝ} (hT : ∀ Q ∈ T, f Q ≤ M) :
    ∀ P ∈ convexHull ℝ T, f P ≤ M := by
  have hsub : T ⊆ {Q ∈ (univ : Set E) | f Q ≤ M} := fun Q hQ => ⟨mem_univ Q, hT Q hQ⟩
  intro P hP
  exact (convexHull_min hsub (hf.convex_le M) hP).2

/-- Actual Euclidean distances on the entire medial triangle satisfy all
the geometric bounds used by the power-sum argument. -/
theorem medial_distance_bounds (A B C P : E) (hAB : A ≠ B)
    (hcb : dist A B ≤ dist C A) (hba : dist C A ≤ dist B C)
    (hP : P ∈ medialTriangle A B C) :
    dist P A ≤ (dist C A + dist A B) / 2 ∧
    dist P A ≤ dist B C ∧ dist P B ≤ dist B C ∧ dist P C ≤ dist B C ∧
    dist P A + dist P B + dist P C < dist B C + (dist C A + dist A B) / 2 := by
  let a := dist B C
  let b := dist C A
  let c := dist A B
  let u := dist (midpoint ℝ B C) A
  let v := dist (midpoint ℝ A C) B
  let w := dist (midpoint ℝ A B) C
  have hc : 0 < c := dist_pos.mpr hAB
  have hb : 0 < b := hc.trans_le hcb
  have ha : 0 < a := hb.trans_le hba
  have hu2 : 4 * u ^ 2 = 2 * b ^ 2 + 2 * c ^ 2 - a ^ 2 := by
    have h := EuclideanGeometry.dist_sq_add_dist_sq_eq_two_mul_dist_midpoint_sq_add_half_dist_sq A B C
    dsimp [u, a, b, c]
    simp only [dist_comm A C, dist_comm A (midpoint ℝ B C)] at h
    nlinarith
  have hv2 : 4 * v ^ 2 = 2 * a ^ 2 + 2 * c ^ 2 - b ^ 2 := by
    have h := EuclideanGeometry.dist_sq_add_dist_sq_eq_two_mul_dist_midpoint_sq_add_half_dist_sq B A C
    dsimp [v, a, b, c]
    simp only [dist_comm B A, dist_comm A C, dist_comm B (midpoint ℝ A C)] at h
    nlinarith
  have hw2 : 4 * w ^ 2 = 2 * a ^ 2 + 2 * b ^ 2 - c ^ 2 := by
    have h := EuclideanGeometry.dist_sq_add_dist_sq_eq_two_mul_dist_midpoint_sq_add_half_dist_sq C A B
    dsimp [w, a, b, c]
    simp only [dist_comm C B, dist_comm C (midpoint ℝ A B)] at h
    nlinarith
  obtain ⟨huS, hva, hwa, hvsum, hwsum⟩ := median_estimates a b c u v w hc hcb hba
    hu2 hv2 hw2
  have hsa : (b + c) / 2 ≤ a := by linarith
  have huA : dist (midpoint ℝ B C) B = a / 2 := by
    simp [a, dist_midpoint_left, div_eq_mul_inv, mul_comm]
  have huB : dist (midpoint ℝ B C) C = a / 2 := by
    simp [a, dist_midpoint_right, div_eq_mul_inv, mul_comm]
  have hvA : dist (midpoint ℝ A C) A = b / 2 := by
    simp [b, dist_midpoint_left, div_eq_mul_inv, mul_comm, dist_comm A C]
  have hvB : dist (midpoint ℝ A C) C = b / 2 := by
    simp [b, dist_midpoint_right, div_eq_mul_inv, mul_comm, dist_comm A C]
  have hwA : dist (midpoint ℝ A B) A = c / 2 := by
    simp [c, dist_midpoint_left, div_eq_mul_inv, mul_comm]
  have hwB : dist (midpoint ℝ A B) B = c / 2 := by
    simp [c, dist_midpoint_right, div_eq_mul_inv, mul_comm]
  have hpS : dist P A ≤ (b + c) / 2 := by
    apply convex_le_on_hull (convexOn_dist A convex_univ) (T :=
      {midpoint ℝ B C, midpoint ℝ A C, midpoint ℝ A B}) ?_ P hP
    intro Q hQ
    simp only [mem_insert_iff, mem_singleton_iff] at hQ
    rcases hQ with rfl | rfl | rfl
    · exact huS.le
    · rw [hvA]; linarith
    · rw [hwA]; linarith
  have hpB : dist P B ≤ a := by
    apply convex_le_on_hull (convexOn_dist B convex_univ) (T :=
      {midpoint ℝ B C, midpoint ℝ A C, midpoint ℝ A B}) ?_ P hP
    intro Q hQ
    simp only [mem_insert_iff, mem_singleton_iff] at hQ
    rcases hQ with rfl | rfl | rfl
    · rw [huA]; linarith
    · exact hva.le
    · rw [hwB]; linarith
  have hpC : dist P C ≤ a := by
    apply convex_le_on_hull (convexOn_dist C convex_univ) (T :=
      {midpoint ℝ B C, midpoint ℝ A C, midpoint ℝ A B}) ?_ P hP
    intro Q hQ
    simp only [mem_insert_iff, mem_singleton_iff] at hQ
    rcases hQ with rfl | rfl | rfl
    · rw [huB]; linarith
    · rw [hvB]; linarith
    · exact hwa.le
  have hpSum : dist P A + dist P B + dist P C < a + (b + c) / 2 := by
    apply convex_lt_on_hull (((convexOn_dist A convex_univ).add
      (convexOn_dist B convex_univ)).add (convexOn_dist C convex_univ)) (T :=
      {midpoint ℝ B C, midpoint ℝ A C, midpoint ℝ A B}) ?_ P hP
    intro Q hQ
    simp only [mem_insert_iff, mem_singleton_iff] at hQ
    rcases hQ with rfl | rfl | rfl
    · change u + dist (midpoint ℝ B C) B + dist (midpoint ℝ B C) C < _
      rw [huA, huB]; linarith
    · change dist (midpoint ℝ A C) A + v + dist (midpoint ℝ A C) C < _
      rw [hvA, hvB]; linarith
    · change dist (midpoint ℝ A B) A + dist (midpoint ℝ A B) B + w < _
      rw [hwA, hwB]; linarith
  exact ⟨hpS, hpS.trans hsa, hpB, hpC, hpSum⟩

end ZengFeiYang
