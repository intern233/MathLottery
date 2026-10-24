import MeshDefinitions

/-! PARTIAL: structural consequences of the exact A and B occurrence predicates. -/
namespace Mesh

theorem A_unique_out {n : ℕ} {p : Perm n} {i j k : Fin n}
    (hij : A p i j) (hik : A p i k) : j = k := by
  rcases lt_trichotomy j k with h | h | h
  · have ht := hik.2.2.2.1 j hij.1 h
    exact False.elim ((not_lt_of_gt hij.2.1) ht)
  · exact h
  · have ht := hij.2.2.2.1 k hik.1 h
    exact False.elim ((not_lt_of_gt hik.2.1) ht)

theorem A_no_chain {n : ℕ} {p : Perm n} {i j k : Fin n}
    (hij : A p i j) (hjk : A p j k) : False := by
  have h := hjk.2.2.1 i hij.1
  exact (not_lt_of_gt hij.2.1) h

theorem A_leaves_decrease {n : ℕ} {p : Perm n} {i j r s : Fin n}
    (_hir : A p i r) (hjs : A p j s) (hij : i < j) : p j < p i :=
  hjs.2.2.1 i hij

theorem B_unique_in {n : ℕ} {p : Perm n} {i k j : Fin n}
    (hij : B p i j) (hkj : B p k j) : i = k := by
  rcases lt_trichotomy i k with h | h | h
  · have ht := hij.2.2.2.1 k h hkj.1
    exact False.elim ((not_lt_of_gt hkj.2.1) ht)
  · exact h
  · have ht := hkj.2.2.2.1 i h hij.1
    exact False.elim ((not_lt_of_gt hij.2.1) ht)

theorem B_unique_out {n : ℕ} {p : Perm n} {i j k : Fin n}
    (hij : B p i j) (hik : B p i k) : j = k := by
  rcases lt_trichotomy j k with h | h | h
  · have ht := hik.2.2.2.1 j hij.1 h
    exact False.elim (hij.2.2.2.2 k h ⟨ht, hik.2.1⟩)
  · exact h
  · have ht := hij.2.2.2.1 k hik.1 h
    exact False.elim (hik.2.2.2.2 j h ⟨ht, hij.2.1⟩)

theorem A_noncrossing {n : ℕ} {p : Perm n} {i j k l : Fin n}
    (hij : A p i j) (hkl : A p k l)
    (hik : i < k) (hkj : k < j) (hjl : j < l) : False := by
  have h1 := hij.2.2.2.1 k hik hkj
  have h2 := hkl.2.2.2.1 j hkj hjl
  exact (lt_irrefl (p i)) (lt_trans hij.2.1 (lt_trans h2 h1))

theorem B_noncrossing {n : ℕ} {p : Perm n} {i j k l : Fin n}
    (hij : B p i j) (hkl : B p k l)
    (hik : i < k) (hkj : k < j) (hjl : j < l) : False := by
  have h1 := hij.2.2.2.1 k hik hkj
  have h2 := hkl.2.2.2.1 j hkj hjl
  exact (lt_irrefl (p k)) (lt_trans h1 (lt_trans h2 hkl.2.1))

end Mesh
