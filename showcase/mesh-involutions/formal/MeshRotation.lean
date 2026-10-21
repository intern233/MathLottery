import MeshComponents
import Mathlib.Logic.Equiv.Fintype
import Mathlib.Logic.Equiv.Fin.Rotate

/-! PARTIAL: explicit single-component rotations, both directions and their inverse. -/
namespace Mesh

def positionEmbedding {n m : ℕ} {x : ℕ → Fin n} (hx : IncTo x m) :
    Fin (m+1) ↪ Fin n where
  toFun a := x a.val
  inj' := by
    intro a b hab
    apply Fin.ext
    rcases lt_trichotomy a.val b.val with h | h | h
    · have hh := hx a.val b.val h (by omega)
      exact False.elim (ne_of_lt hh hab)
    · exact h
    · have hh := hx b.val a.val h (by omega)
      exact False.elim (ne_of_lt hh hab.symm)

noncomputable def positionShift {n m : ℕ} {x : ℕ → Fin n} (hx : IncTo x m) : Perm n := by
  classical
  exact (finRotate (m+1)).viaFintypeEmbedding (positionEmbedding hx)

theorem positionShift_next {n m : ℕ} {x : ℕ → Fin n} (hx : IncTo x m)
    (a : ℕ) (ha : a < m) : positionShift hx (x a) = x (a+1) := by
  have h := Equiv.Perm.viaFintypeEmbedding_apply_image (finRotate (m+1))
    (positionEmbedding hx) (⟨a, by omega⟩ : Fin (m+1))
  rw [finRotate_of_lt ha] at h
  exact h

theorem positionShift_last {n m : ℕ} {x : ℕ → Fin n} (hx : IncTo x m) :
    positionShift hx (x m) = x 0 := by
  have h := Equiv.Perm.viaFintypeEmbedding_apply_image (finRotate (m+1))
    (positionEmbedding hx) (Fin.last m)
  rw [finRotate_last] at h
  exact h

theorem positionShift_fixed {n m : ℕ} {x : ℕ → Fin n} (hx : IncTo x m)
    (t : Fin n) (ht : ∀ a, a ≤ m → t ≠ x a) : positionShift hx t = t := by
  apply Equiv.Perm.viaFintypeEmbedding_apply_notMem_range
  rintro ⟨a, ha⟩
  exact ht a.val (by omega) ha.symm

noncomputable def rotateForward {n m : ℕ} {x : ℕ → Fin n}
    (p : Perm n) (hx : IncTo x m) : Perm n := (positionShift hx).symm.trans p

noncomputable def rotateBackward {n m : ℕ} {x : ℕ → Fin n}
    (p : Perm n) (hx : IncTo x m) : Perm n := (positionShift hx).trans p

theorem rotateForward_first {n m : ℕ} {x : ℕ → Fin n}
    (p : Perm n) (hx : IncTo x m) : rotateForward p hx (x 0) = p (x m) := by
  change p ((positionShift hx).symm (x 0)) = p (x m)
  rw [(positionShift hx).symm_apply_eq.mpr (positionShift_last hx).symm]

theorem rotateForward_next {n m : ℕ} {x : ℕ → Fin n}
    (p : Perm n) (hx : IncTo x m) (a : ℕ) (ha : a < m) :
    rotateForward p hx (x (a+1)) = p (x a) := by
  change p ((positionShift hx).symm (x (a+1))) = p (x a)
  rw [(positionShift hx).symm_apply_eq.mpr (positionShift_next hx a ha).symm]

theorem rotateBackward_next {n m : ℕ} {x : ℕ → Fin n}
    (p : Perm n) (hx : IncTo x m) (a : ℕ) (ha : a < m) :
    rotateBackward p hx (x a) = p (x (a+1)) := by
  change p (positionShift hx (x a)) = p (x (a+1))
  rw [positionShift_next hx a ha]

theorem rotateBackward_last {n m : ℕ} {x : ℕ → Fin n}
    (p : Perm n) (hx : IncTo x m) : rotateBackward p hx (x m) = p (x 0) := by
  change p (positionShift hx (x m)) = p (x 0)
  rw [positionShift_last hx]

theorem rotateForward_fixed {n m : ℕ} {x : ℕ → Fin n}
    (p : Perm n) (hx : IncTo x m) (t : Fin n) (ht : ∀ a, a ≤ m → t ≠ x a) :
    rotateForward p hx t = p t := by
  change p ((positionShift hx).symm t) = p t
  rw [(positionShift hx).symm_apply_eq.mpr (positionShift_fixed hx t ht).symm]

theorem rotateBackward_fixed {n m : ℕ} {x : ℕ → Fin n}
    (p : Perm n) (hx : IncTo x m) (t : Fin n) (ht : ∀ a, a ≤ m → t ≠ x a) :
    rotateBackward p hx t = p t := by
  change p (positionShift hx t) = p t
  rw [positionShift_fixed hx t ht]

theorem rotate_backward_forward {n m : ℕ} {x : ℕ → Fin n}
    (p : Perm n) (hx : IncTo x m) :
    rotateBackward (rotateForward p hx) hx = p := by
  ext t
  simp [rotateBackward, rotateForward]

theorem rotate_forward_backward {n m : ℕ} {x : ℕ → Fin n}
    (p : Perm n) (hx : IncTo x m) :
    rotateForward (rotateBackward p hx) hx = p := by
  ext t
  simp [rotateBackward, rotateForward]

theorem outside_transfer {n m : ℕ} {p q : Perm n} {x v : ℕ → Fin n}
    (hx : IncTo x m) (ho : Outside p x v m)
    (heq : ∀ t, (∀ a, a ≤ m → t ≠ x a) → q t = p t) : Outside q x v m := by
  have before : ∀ t, t < x 0 → q t = p t := by
    intro t ht
    apply heq t
    intro a ha hta
    rw [hta] at ht
    exact (not_lt_of_ge (hx.mono (Nat.zero_le _) ha)) ht
  have after : ∀ t, x m < t → q t = p t := by
    intro t ht
    apply heq t
    intro a ha hta
    rw [hta] at ht
    exact (not_lt_of_ge (hx.mono ha le_rfl)) ht
  have gap : ∀ k, 1 ≤ k → k ≤ m → ∀ t, x (k-1) < t → t < x k → q t = p t := by
    intro k hk hkm t hlt htr
    apply heq t
    intro a ha hta
    rw [hta] at hlt htr
    have h1 := hx.reflect (show k-1 ≤ m by omega) hlt
    have h2 := hx.reflect ha htr
    omega
  refine ⟨?_, ?_, ?_, ?_⟩
  · intro t ht
    rw [before t ht]
    exact ho.1 t ht
  · intro k hk hkm t hlt htr
    rw [gap k hk (le_of_lt hkm) t hlt htr]
    exact ho.2.1 k hk hkm t hlt htr
  · intro t hlt htr
    have hm : 1 ≤ m := by
      by_contra h
      have hm : m = 0 := by omega
      simp only [hm, Nat.zero_sub] at hlt htr
      exact (not_lt_of_gt hlt) htr
    rw [gap m hm le_rfl t hlt htr]
    exact ho.2.2.1 t hlt htr
  · intro t ht
    rw [after t ht]
    exact ho.2.2.2 t ht

theorem rotateForward_layout {n m : ℕ} {p : Perm n} {x v : ℕ → Fin n}
    (hx : IncTo x m) (hl : StarLayout p x v m) :
    PathLayout (rotateForward p hx) x v m := by
  intro a ha
  cases a with
  | zero => rw [rotateForward_first, hl.1]
  | succ a =>
    rw [rotateForward_next p hx a (by omega)]
    exact hl.2 a (by omega)

theorem rotateBackward_layout {n m : ℕ} {p : Perm n} {x v : ℕ → Fin n}
    (hx : IncTo x m) (hl : PathLayout p x v m) :
    StarLayout (rotateBackward p hx) x v m := by
  constructor
  · rw [rotateBackward_last, hl 0 (Nat.zero_le _)]
  · intro a ha
    rw [rotateBackward_next p hx a ha, hl (a+1) (by omega)]

theorem single_star_to_path {n m : ℕ} {p : Perm n} {x v : ℕ → Fin n}
    (hm : 1 ≤ m) (hx : IncTo x m) (hv : DecTo v m)
    (hl : StarLayout p x v m) (he : StarEdges p x m) :
    PathEdges (rotateForward p hx) x m := by
  apply outside_path hx hv (rotateForward_layout hx hl)
  exact outside_transfer hx (star_outside hm hx hl he) (rotateForward_fixed p hx)

theorem single_path_to_star {n m : ℕ} {p : Perm n} {x v : ℕ → Fin n}
    (hm : 1 ≤ m) (hx : IncTo x m) (hv : DecTo v m)
    (hl : PathLayout p x v m) (he : PathEdges p x m) :
    StarEdges (rotateBackward p hx) x m := by
  apply outside_star hx hv (rotateBackward_layout hx hl)
  exact outside_transfer hx (path_outside hm hx hv hl he) (rotateBackward_fixed p hx)

end Mesh
