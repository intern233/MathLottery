import MeshComponents

/-! PARTIAL: gap nesting follows from the actual mesh occurrences. -/
namespace Mesh

def DisjointVertices {n m r : ℕ} (x y : ℕ → Fin n) : Prop :=
  ∀ a, a ≤ m → ∀ b, b ≤ r → x a ≠ y b

theorem star_gap_nesting {n m r : ℕ} {p : Perm n} {x y : ℕ → Fin n}
    (hm : 1 ≤ m) (hr : 1 ≤ r) (hx : IncTo x m) (hy : IncTo y r)
    (hdis : DisjointVertices (m := m) (r := r) x y)
    (hex : StarEdges p x m) (hey : StarEdges p y r)
    (hleft : x 0 < y 0) (hright : y 0 < x m) :
    ∃ k, 1 ≤ k ∧ k ≤ m ∧ x (k-1) < y 0 ∧ y r < x k := by
  have end_lt : y r < x m := by
    rcases lt_trichotomy (y r) (x m) with h | h | h
    · exact h
    · exact False.elim (hdis m le_rfl r le_rfl h.symm)
    · exact False.elim (A_noncrossing
        (by simpa using hex 1 le_rfl hm)
        (by simpa using hey 1 le_rfl hr) hleft hright h)
  rcases chain_cases x m hx (y 0) with
    ht | ⟨a, ha, hta⟩ | ⟨k, hk, hkm, hkt, htk⟩ | ht
  · exact False.elim ((not_lt_of_gt hleft) ht)
  · exact False.elim (hdis a ha 0 (Nat.zero_le _) hta.symm)
  · refine ⟨k, hk, hkm, hkt, ?_⟩
    rcases eq_or_lt_of_le hkm with rfl | hkm
    · exact end_lt
    · rcases lt_trichotomy (y r) (x k) with h | h | h
      · exact h
      · exact False.elim (hdis k (le_of_lt hkm) r le_rfl h.symm)
      · exact False.elim (A_noncrossing
          (by simpa using hey 1 le_rfl hr)
          (by simpa using hex (k+1) (by omega) (by omega)) htk h end_lt)
  · exact False.elim ((not_lt_of_gt hright) ht)

theorem path_gap_nesting {n m r : ℕ} {p : Perm n} {x y : ℕ → Fin n}
    (hx : IncTo x m) (hy : IncTo y r)
    (hdis : DisjointVertices (m := m) (r := r) x y)
    (hex : PathEdges p x m) (hey : PathEdges p y r)
    (hleft : x 0 < y 0) (hright : y 0 < x m) :
    ∃ k, 1 ≤ k ∧ k ≤ m ∧ x (k-1) < y 0 ∧ y r < x k := by
  rcases chain_cases x m hx (y 0) with
    ht | ⟨a, ha, hta⟩ | ⟨k, hk, hkm, hkt, htk⟩ | ht
  · exact False.elim ((not_lt_of_gt hleft) ht)
  · exact False.elim (hdis a ha 0 (Nat.zero_le _) hta.symm)
  · refine ⟨k, hk, hkm, hkt, ?_⟩
    rcases lt_trichotomy (y r) (x k) with h | h | h
    · exact h
    · exact False.elim (hdis k hkm r le_rfl h.symm)
    · rcases chain_cases y r hy (x k) with
        ht | ⟨b, hb, htb⟩ | ⟨l, hl, hlr, hlt, htl⟩ | ht
      · exact False.elim ((not_lt_of_gt htk) ht)
      · exact False.elim (hdis k hkm b hb htb)
      · have hlow : x (k-1) < y (l-1) :=
          lt_of_lt_of_le hkt (hy.mono (Nat.zero_le _) (by omega))
        exact False.elim (B_noncrossing (hex k hk hkm) (hey l hl hlr)
          hlow hlt htl)
      · exact False.elim ((not_lt_of_gt h) ht)
  · exact False.elim ((not_lt_of_gt hright) ht)

end Mesh
