import MeshRotation
import MeshSymmetry

/-! PARTIAL: permutation-level and individual-edge equivariance on an actual component. -/
namespace Mesh

def inversePositions {n : ℕ} (v : ℕ → Fin n) (m : ℕ) (a : ℕ) := v (m-a)
def inverseValues {n : ℕ} (x : ℕ → Fin n) (m : ℕ) (a : ℕ) := x (m-a)

theorem inversePositions_inc {n m : ℕ} {v : ℕ → Fin n} (hv : DecTo v m) :
    IncTo (inversePositions v m) m := by
  intro a b hab hbm
  exact hv.lt (by omega : m-b < m-a) (by omega)

theorem inverseValues_dec {n m : ℕ} {x : ℕ → Fin n} (hx : IncTo x m) :
    DecTo (inverseValues x m) m := by
  intro a b hab hbm
  exact hx (m-b) (m-a) (by omega) (by omega)

theorem inverse_star_layout {n m : ℕ} {p : Perm n} {x v : ℕ → Fin n}
    (hl : StarLayout p x v m) :
    StarLayout p.symm (inversePositions v m) (inverseValues x m) m := by
  constructor
  · change p.symm (v (m-m)) = x (m-0)
    simp only [Nat.sub_self, Nat.sub_zero]
    exact p.symm_apply_eq.mpr hl.1.symm
  · intro a ha
    change p.symm (v (m-a)) = x (m-(a+1))
    apply p.symm_apply_eq.mpr
    rw [hl.2 (m-(a+1)) (by omega)]
    congr 1
    omega

theorem inverse_rotation {n m : ℕ} {p : Perm n} {x v : ℕ → Fin n}
    (hx : IncTo x m) (hv : DecTo v m) (hl : StarLayout p x v m) :
    rotateForward p.symm (inversePositions_inc hv) = (rotateForward p hx).symm := by
  classical
  have hpl := rotateForward_layout hx hl
  have htl := rotateForward_layout (inversePositions_inc hv) (inverse_star_layout hl)
  apply Equiv.ext
  intro t
  by_cases hmem : ∃ a, a ≤ m ∧ t = v a
  · obtain ⟨a, ha, rfl⟩ := hmem
    have hi : inversePositions v m (m-a) = v a := by
      simp only [inversePositions]
      congr 1
      omega
    have ht := htl (m-a) (by omega)
    rw [hi] at ht
    have hi' : inverseValues x m (m-a) = x a := by
      simp only [inverseValues]
      congr 1
      omega
    rw [hi'] at ht
    rw [ht]
    exact ((rotateForward p hx).symm_apply_eq.mpr (hpl a ha).symm).symm
  · have hnotv : ∀ a, a ≤ m → t ≠ v a := by
      intro a ha ht
      exact hmem ⟨a, ha, ht⟩
    have hnotxt : ∀ a, a ≤ m → t ≠ inversePositions v m a := by
      intro a ha
      exact hnotv (m-a) (by omega)
    rw [rotateForward_fixed p.symm (inversePositions_inc hv) t hnotxt]
    have hnotx : ∀ a, a ≤ m → p.symm t ≠ x a := by
      intro a ha heq
      have heq' : t = p (x a) := by rw [← p.apply_symm_apply t, heq]
      rcases eq_or_lt_of_le ha with rfl | ha
      · rw [hl.1] at heq'
        exact hnotv 0 (Nat.zero_le _) heq'
      · rw [hl.2 a ha] at heq'
        exact hnotv (a+1) (by omega) heq'
    apply ((rotateForward p hx).symm_apply_eq.mpr ?_).symm
    rw [rotateForward_fixed p hx (p.symm t) hnotx]
    simp

theorem transpose_star_edge {n m : ℕ} {p : Perm n} {x v : ℕ → Fin n}
    (hv : DecTo v m) (hl : StarLayout p x v m) {h : ℕ}
    (hh : 1 ≤ h) (hhm : h ≤ m) :
    transposeEdge p (x (h-1), x m) = (v h, v 0) := by
  have leaf : p (x (h-1)) = v h := by
    simpa [Nat.sub_add_cancel hh] using hl.2 (h-1) (by omega)
  have hvh := hv.lt (by omega : 0 < h) hhm
  simp only [transposeEdge, leaf, hl.1,
    min_eq_left (le_of_lt hvh), max_eq_right (le_of_lt hvh)]

theorem transpose_path_edge {n m : ℕ} {p : Perm n} {x v : ℕ → Fin n}
    (hv : DecTo v m) (hl : PathLayout p x v m) {h : ℕ}
    (hh : 1 ≤ h) (hhm : h ≤ m) :
    transposeEdge p (x (h-1), x h) = (v h, v (h-1)) := by
  have hvh := hv.lt (by omega : h-1 < h) hhm
  simp only [transposeEdge, hl h hhm, hl (h-1) (by omega),
    min_eq_right (le_of_lt hvh), max_eq_left (le_of_lt hvh)]

theorem star_edge_index_under_inverse {n m : ℕ} {p : Perm n} {x v : ℕ → Fin n}
    (hv : DecTo v m) (hl : StarLayout p x v m) {h : ℕ}
    (hh : 1 ≤ h) (hhm : h ≤ m) :
    transposeEdge p (x (h-1), x m) =
      (inversePositions v m ((m-h+1)-1), inversePositions v m m) := by
  rw [transpose_star_edge hv hl hh hhm]
  simp only [inversePositions, Nat.sub_self]
  congr 2
  omega

theorem individual_edge_equivariance {n m : ℕ} {p : Perm n} {x v : ℕ → Fin n}
    (hx : IncTo x m) (hv : DecTo v m) (hl : StarLayout p x v m) {h : ℕ}
    (hh : 1 ≤ h) (hhm : h ≤ m) :
    transposeEdge (rotateForward p hx) (x (h-1), x h) =
      (inversePositions v m ((m-h+1)-1), inversePositions v m (m-h+1)) := by
  rw [transpose_path_edge hv (rotateForward_layout hx hl) hh hhm]
  simp only [inversePositions]
  congr 2 <;> omega

end Mesh
