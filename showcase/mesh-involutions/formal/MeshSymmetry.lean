import MeshDefinitions

/-! PARTIAL: inversion and reverse-complement symmetries for literal mesh predicates. -/
namespace Mesh

theorem geom_transpose {n : ℕ} (p : Perm n) (i j l h : Fin n)
    (_hij : i < j) (hlh : l < h)
    (ends : (p i = l ∧ p j = h) ∨ (p i = h ∧ p j = l))
    (hg : Geom p i j l h) : Geom p.symm l h i j := by
  have himem : p i = l ∨ p i = h := by tauto
  have hjmem : p j = l ∨ p j = h := by tauto
  refine ⟨?_, ?_, ?_⟩
  · intro t htl
    have ht := p.apply_symm_apply t
    rcases lt_trichotomy (p.symm t) i with hti | hti | hti
    · have hx := hg.1 (p.symm t) hti
      rw [ht] at hx
      exact False.elim ((not_lt_of_gt htl) hx)
    · have hx : t = p i := by rw [← ht, hti]
      rcases himem with hi | hi <;> rw [hi] at hx <;> omega
    · exact hti
  · intro t hlt hth
    have ht := p.apply_symm_apply t
    rcases lt_trichotomy (p.symm t) i with hti | hti | hti
    · exact hti
    · have hx : t = p i := by rw [← ht, hti]
      rcases himem with hi | hi <;> rw [hi] at hx <;> omega
    · rcases lt_trichotomy (p.symm t) j with htj | htj | htj
      · have hx := hg.2.1 (p.symm t) hti htj
        rw [ht] at hx
        exact False.elim ((not_lt_of_gt hlt) hx)
      · have hx : t = p j := by rw [← ht, htj]
        rcases hjmem with hj | hj <;> rw [hj] at hx <;> omega
      · exact False.elim (hg.2.2 (p.symm t) htj (by simpa using And.intro hlt hth))
  · intro t hht hpos
    have hx := hg.2.1 (p.symm t) hpos.1 hpos.2
    simp only [p.apply_symm_apply] at hx
    exact (not_lt_of_gt (lt_trans hlh hht)) hx

theorem A_inverse {n : ℕ} (p : Perm n) {i j : Fin n} (h : A p i j) :
    A p.symm (p i) (p j) := by
  refine ⟨h.2.1, ?_, ?_⟩
  · simpa using h.1
  · simpa using geom_transpose p i j (p i) (p j) h.1 h.2.1
      (Or.inl ⟨rfl, rfl⟩) h.2.2

theorem B_inverse {n : ℕ} (p : Perm n) {i j : Fin n} (h : B p i j) :
    B p.symm (p j) (p i) := by
  refine ⟨h.2.1, ?_, ?_⟩
  · simpa using h.1
  · simpa using geom_transpose p i j (p j) (p i) h.1 h.2.1
      (Or.inr ⟨rfl, rfl⟩) h.2.2

def transposeEdge {n : ℕ} (p : Perm n) (e : Fin n × Fin n) : Fin n × Fin n :=
  (min (p e.1) (p e.2), max (p e.1) (p e.2))

theorem transpose_twice {n : ℕ} (p : Perm n) {i j : Fin n} (hij : i < j) :
    transposeEdge p.symm (transposeEdge p (i, j)) = (i, j) := by
  have hn : p i ≠ p j := p.injective.ne (ne_of_lt hij)
  rcases lt_or_gt_of_ne hn with h | h
  · simp [transposeEdge, min_eq_left (le_of_lt h), max_eq_right (le_of_lt h),
      min_eq_left (le_of_lt hij), max_eq_right (le_of_lt hij)]
  · simp [transposeEdge, min_eq_right (le_of_lt h), max_eq_left (le_of_lt h),
      min_eq_right (le_of_lt hij), max_eq_left (le_of_lt hij)]

def rc {n : ℕ} (p : Perm n) : Perm n :=
  Fin.revPerm.trans (p.trans Fin.revPerm)

@[simp] theorem rc_apply {n : ℕ} (p : Perm n) (i : Fin n) :
    rc p i = (p i.rev).rev := rfl

@[simp] theorem rc_rc {n : ℕ} (p : Perm n) : rc (rc p) = p := by
  ext i
  simp

theorem rc_preserves_involutive {n : ℕ} {p : Perm n} (h : Function.Involutive p) :
    Function.Involutive (rc p) := by
  intro i
  simp only [rc_apply, Fin.rev_rev, h i.rev]

theorem rc_involutive_iff {n : ℕ} (p : Perm n) :
    Function.Involutive (rc p) ↔ Function.Involutive p := by
  constructor
  · intro h
    simpa using rc_preserves_involutive h
  · exact rc_preserves_involutive

theorem band_reverse {n : ℕ} (a : ℕ) (ha : a ≤ 2) (i j t : Fin n) :
    Band (2-a) j.rev i.rev t.rev ↔ Band a i j t := by
  interval_cases a <;> simp [Band, and_comm]

theorem min_rev {n : ℕ} (a b : Fin n) :
    min a.rev b.rev = (max a b).rev := by
  rcases le_total a b with h | h
  · simp [max_eq_right h, min_eq_right (Fin.rev_le_rev.mpr h)]
  · simp [max_eq_left h, min_eq_left (Fin.rev_le_rev.mpr h)]

theorem max_rev {n : ℕ} (a b : Fin n) :
    max a.rev b.rev = (min a b).rev := by
  rcases le_total a b with h | h
  · simp [min_eq_left h, max_eq_left (Fin.rev_le_rev.mpr h)]
  · simp [min_eq_right h, max_eq_right (Fin.rev_le_rev.mpr h)]

def reverseCell (c : ℕ × ℕ) : ℕ × ℕ := (2-c.1, 2-c.2)

theorem R_reverse : R' = R.image reverseCell := by decide

theorem R_coords (c : ℕ × ℕ) (hc : c ∈ R) : c.1 ≤ 2 ∧ c.2 ≤ 2 := by
  simp only [R, Finset.mem_insert, Finset.mem_singleton] at hc
  rcases hc with rfl | rfl | rfl | rfl <;> decide

theorem empty_reverse {n : ℕ} (p : Perm n) (i j : Fin n) :
    Empty R' (rc p) j.rev i.rev ↔ Empty R p i j := by
  have point (c : ℕ × ℕ) (hc : c ∈ R) (t : Fin n) :
      (Band (reverseCell c).1 j.rev i.rev t.rev ∧
        Band (reverseCell c).2
          (min (rc p j.rev) (rc p i.rev))
          (max (rc p j.rev) (rc p i.rev)) (rc p t.rev)) ↔
      (Band c.1 i j t ∧ Band c.2 (min (p i) (p j)) (max (p i) (p j)) (p t)) := by
    have h1 := (R_coords c hc).1
    have h2 := (R_coords c hc).2
    simp only [reverseCell, rc_apply, Fin.rev_rev, min_rev, max_rev]
    rw [min_comm (p j) (p i), max_comm (p j) (p i)]
    rw [band_reverse c.1 h1, band_reverse c.2 h2]
  constructor
  · intro h c hc t hp
    exact h (reverseCell c) (by rw [R_reverse]; exact Finset.mem_image_of_mem _ hc)
      t.rev ((point c hc t).mpr hp)
  · intro h c hc t hp
    rw [R_reverse] at hc
    obtain ⟨d, hd, rfl⟩ := Finset.mem_image.mp hc
    apply h d hd t.rev
    apply (point d hd t.rev).mp
    simpa using hp

theorem mesh_reverse {n : ℕ} (asc : Bool) (p : Perm n) (i j : Fin n) :
    MeshOcc asc R' (rc p) j.rev i.rev ↔ MeshOcc asc R p i j := by
  simp only [MeshOcc, Fin.rev_lt_rev, rc_apply, Fin.rev_rev, empty_reverse]

def reverseEdge {n : ℕ} : Equiv.Perm (Fin n × Fin n) :=
  Function.Involutive.toPerm (fun e => (e.2.rev, e.1.rev)) (by
    rintro ⟨i, j⟩
    simp)

@[simp] theorem reverseEdge_apply {n : ℕ} (i j : Fin n) :
    reverseEdge (i, j) = (j.rev, i.rev) := rfl

theorem occurrences_reverse_card {n : ℕ} (asc : Bool) (p : Perm n) :
    (occurrences asc R p).card = (occurrences asc R' (rc p)).card := by
  classical
  apply Finset.card_equiv reverseEdge
  rintro ⟨i, j⟩
  simp only [occurrences, Finset.mem_filter, Finset.mem_univ, true_and,
    reverseEdge_apply, mesh_reverse]

def rcEquiv (n : ℕ) : Equiv.Perm (Perm n) :=
  Function.Involutive.toPerm rc rc_rc

theorem distribution_reverse (n k : ℕ) (asc : Bool) :
    distribution n k asc R = distribution n k asc R' := by
  classical
  unfold distribution
  apply Finset.card_equiv (rcEquiv n)
  intro p
  simp only [Finset.mem_filter, Finset.mem_univ, true_and]
  change (Function.Involutive p ∧ (occurrences asc R p).card = k) ↔
    (Function.Involutive (rc p) ∧
      (occurrences asc R' (rc p)).card = k)
  rw [rc_involutive_iff, ← occurrences_reverse_card]

end Mesh
