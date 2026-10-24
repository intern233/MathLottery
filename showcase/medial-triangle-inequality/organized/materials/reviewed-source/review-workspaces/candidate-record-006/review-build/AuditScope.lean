import Conjecture5

/- Independent semantic checks; not part of the immutable candidate. -/
set_option autoImplicit false
set_option pp.universes true

#print ZengFeiYang.conjecture5_original
#print ZengFeiYang.conjecture5_closed
#check @ZengFeiYang.medial_distance_bounds
#check @ZengFeiYang.median_estimates
#check @ZengFeiYang.three_power_lt
#check @ZengFeiYang.weighted_lt
#print axioms ZengFeiYang.median_estimates
#print axioms ZengFeiYang.medial_distance_bounds
#print axioms ZengFeiYang.three_power_lt
#print axioms ZengFeiYang.weighted_lt
#print axioms ZengFeiYang.medialTriangle_isClosed

example (A B C : EuclideanSpace ℝ (Fin 2)) :
    AffineIndependent ℝ ![A, B, C] ↔
      ¬ Collinear ℝ ({A, B, C} : Set (EuclideanSpace ℝ (Fin 2))) :=
  affineIndependent_iff_not_collinear_set

example (u : EuclideanSpace ℝ (Fin 2)) :
    ‖u‖ ^ 2 = (u 0) ^ 2 + (u 1) ^ 2 := by
  simpa [Fin.sum_univ_two] using EuclideanSpace.real_norm_sq_eq u

example (u v : EuclideanSpace ℝ (Fin 2)) :
    dist u v ^ 2 = (u 0 - v 0) ^ 2 + (u 1 - v 1) ^ 2 := by
  simpa [Fin.sum_univ_two, Real.dist_eq, sq_abs] using EuclideanSpace.dist_sq_eq u v

example (u v : EuclideanSpace ℝ (Fin 2)) :
    midpoint ℝ u v = (1 / 2 : ℝ) • (u + v) := by
  simpa using midpoint_eq_smul_add (R := ℝ) u v

-- A separately written expected original type must elaborate using the supplied theorem.
example (A B C P : EuclideanSpace ℝ (Fin 2))
    (hnd : ¬ Collinear ℝ ({A, B, C} : Set (EuclideanSpace ℝ (Fin 2))))
    (hbc : dist A B ≤ dist C A) (hab : dist C A ≤ dist B C)
    (hp : P ∈ interior (convexHull ℝ
      {midpoint ℝ B C, midpoint ℝ A C, midpoint ℝ A B}))
    (x y z : ℝ) (hx : 0 < x) (hy : 0 < y) (hz : 0 < z)
    (n : ℕ) (hn : 1 ≤ n) :
    x * dist P A ^ n + y * dist P B ^ n + z * dist P C ^ n <
      max x y * ((dist A B + dist C A) / 2) ^ n +
      max y z * dist B C ^ n :=
  ZengFeiYang.conjecture5_original A B C P
    (affineIndependent_iff_not_collinear_set.mpr hnd) hbc hab hp x y z hx hy hz n hn
