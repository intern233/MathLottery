import MedialAlgebra
import MedialGeometry
import Mathlib.Analysis.InnerProductSpace.PiL2
import Mathlib.Analysis.Convex.Topology

/-!
Zeng--Fei--Yang, Conjecture 5, printed page 51 of
"Tracing the Origins and Generalizations of a Class of Moving Point Inequalities".

The closed-hull theorem is stronger than the original: it works in every
real inner product space, on the entire filled medial triangle, and requires
only A ≠ B and the ordered side lengths. The final theorem specializes to
nondegenerate triangles in the Euclidean plane and strict interior points.
-/

namespace ZengFeiYang
set_option autoImplicit false
open Set

variable {E : Type*} [NormedAddCommGroup E] [InnerProductSpace ℝ E]

/-- Full weighted inequality, including all boundary points of the medial triangle. -/
theorem conjecture5_closed (A B C P : E) (hAB : A ≠ B)
    (hcb : dist A B ≤ dist C A) (hba : dist C A ≤ dist B C)
    (hP : P ∈ convexHull ℝ {midpoint ℝ B C, midpoint ℝ A C, midpoint ℝ A B})
    (x y z : ℝ) (hx : 0 < x) (hy : 0 < y) (hz : 0 < z)
    (n : ℕ) (hn : 1 ≤ n) :
    x * dist P A ^ n + y * dist P B ^ n + z * dist P C ^ n <
      max x y * ((dist C A + dist A B) / 2) ^ n + max y z * dist B C ^ n := by
  obtain ⟨hpS, hpa, hqa, hra, hsum⟩ := medial_distance_bounds A B C P hAB hcb hba hP
  have hc : 0 < dist A B := dist_pos.mpr hAB
  have hs : 0 < (dist C A + dist A B) / 2 := by linarith
  have hsa : (dist C A + dist A B) / 2 ≤ dist B C := by linarith
  have hpow := three_power_lt (dist B C) ((dist C A + dist A B) / 2)
    (dist P A) (dist P B) (dist P C) hs hsa dist_nonneg dist_nonneg dist_nonneg
    hpa hqa hra hsum n hn
  exact weighted_lt (dist B C ^ n) (((dist C A + dist A B) / 2) ^ n)
    (dist P A ^ n) (dist P B ^ n) (dist P C ^ n) x y z
    (pow_nonneg dist_nonneg n) (pow_nonneg dist_nonneg n) (pow_nonneg dist_nonneg n)
    (pow_le_pow_left₀ dist_nonneg hpS n) (pow_le_pow_left₀ dist_nonneg hra n)
    hpow hx hy hz

/-- The set called the filled medial triangle is indeed closed. -/
theorem medialTriangle_isClosed (A B C : E) : IsClosed (medialTriangle A B C) := by
  exact (Set.toFinite {midpoint ℝ B C, midpoint ℝ A C, midpoint ℝ A B}).isCompact_convexHull ℝ |>.isClosed

/-- Original scope: a nondegenerate Euclidean plane triangle and an interior
point of the triangle whose vertices are the three actual midpoints. -/
theorem conjecture5_original (A B C P : EuclideanSpace ℝ (Fin 2))
    (hnd : AffineIndependent ℝ ![A, B, C])
    (hcb : dist A B ≤ dist C A) (hba : dist C A ≤ dist B C)
    (hP : P ∈ interior (convexHull ℝ
      {midpoint ℝ B C, midpoint ℝ A C, midpoint ℝ A B}))
    (x y z : ℝ) (hx : 0 < x) (hy : 0 < y) (hz : 0 < z)
    (n : ℕ) (hn : 1 ≤ n) :
    x * dist P A ^ n + y * dist P B ^ n + z * dist P C ^ n <
      max x y * ((dist A B + dist C A) / 2) ^ n + max y z * dist B C ^ n := by
  have hAB : A ≠ B := by
    intro h
    have h01 : (0 : Fin 3) = 1 := hnd.injective (by simpa using h)
    exact (by decide : (0 : Fin 3) ≠ 1) h01
  simpa only [add_comm (dist A B) (dist C A)] using
    conjecture5_closed A B C P hAB hcb hba (interior_subset hP) x y z hx hy hz n hn

end ZengFeiYang

#check @ZengFeiYang.conjecture5_closed
#check @ZengFeiYang.conjecture5_original
#print axioms ZengFeiYang.conjecture5_closed
#print axioms ZengFeiYang.conjecture5_original
