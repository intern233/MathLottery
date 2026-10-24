import Mathlib.Data.Fintype.Perm
import Mathlib.Data.Fintype.Prod
import Mathlib.Data.Fin.Rev
import Mathlib.Data.Finset.Card
import Mathlib.Tactic.IntervalCases
import Mathlib.Tactic.Tauto

/-!
PARTIAL formalization of corrected Conjecture 1.
Definitions use actual finite permutations and literal open rank rectangles.
No theorem in this file is asserted to prove the cross-pair distribution identity.
-/

namespace Mesh

abbrev Perm (n : ℕ) := Equiv.Perm (Fin n)

def boundary {n : ℕ} (l h : Fin n) : ℕ → ℕ
  | 0 => 0
  | 1 => l.val + 1
  | 2 => h.val + 1
  | _ => n + 1

def Band {n : ℕ} (a : ℕ) (l h t : Fin n) : Prop :=
  (a = 0 ∧ t < l) ∨ (a = 1 ∧ l < t ∧ t < h) ∨ (a = 2 ∧ h < t)

theorem band_literal {n : ℕ} (a : ℕ) (ha : a ≤ 2) (l h t : Fin n) :
    Band a l h t ↔
      boundary l h a < t.val + 1 ∧ t.val + 1 < boundary l h (a + 1) := by
  interval_cases a <;> simp [Band, boundary]

def R : Finset (ℕ × ℕ) := {(0, 0), (1, 1), (1, 2), (2, 1)}
def R' : Finset (ℕ × ℕ) := {(2, 2), (0, 1), (1, 1), (1, 0)}

def Empty {n : ℕ} (S : Finset (ℕ × ℕ)) (p : Perm n) (i j : Fin n) : Prop :=
  ∀ c ∈ S, ∀ t : Fin n,
    ¬ (Band c.1 i j t ∧ Band c.2 (min (p i) (p j)) (max (p i) (p j)) (p t))

def MeshOcc {n : ℕ} (asc : Bool) (S : Finset (ℕ × ℕ))
    (p : Perm n) (i j : Fin n) : Prop :=
  i < j ∧ (if asc then p i < p j else p j < p i) ∧ Empty S p i j

def Geom {n : ℕ} (p : Perm n) (i j l h : Fin n) : Prop :=
  (∀ t, t < i → l < p t) ∧
  (∀ t, i < t → t < j → p t < l) ∧
  (∀ t, j < t → ¬ (l < p t ∧ p t < h))

def A {n : ℕ} (p : Perm n) (i j : Fin n) : Prop :=
  i < j ∧ p i < p j ∧ Geom p i j (p i) (p j)

def B {n : ℕ} (p : Perm n) (i j : Fin n) : Prop :=
  i < j ∧ p j < p i ∧ Geom p i j (p j) (p i)

theorem empty_R_expansion {n : ℕ} (p : Perm n) (i j : Fin n) :
    Empty R p i j ↔
    (∀ t, t < i → ¬ (p t < min (p i) (p j))) ∧
    (∀ t, i < t → t < j →
      ¬ (min (p i) (p j) < p t ∧ p t < max (p i) (p j))) ∧
    (∀ t, i < t → t < j → ¬ (max (p i) (p j) < p t)) ∧
    (∀ t, j < t →
      ¬ (min (p i) (p j) < p t ∧ p t < max (p i) (p j))) := by
  simp only [Empty, R, Finset.mem_insert, Finset.mem_singleton,
    forall_eq_or_imp, forall_eq, Band]
  simp only [Nat.reduceEqDiff, true_and, false_and, or_false, false_or, not_and]
  simp only [and_imp]

theorem forbidden_iff_geom {n : ℕ} (p : Perm n) (i j l h : Fin n)
    (hij : i < j) (hlh : l < h)
    (ends : (p i = l ∧ p j = h) ∨ (p i = h ∧ p j = l)) :
    ((∀ t, t < i → ¬ (p t < l)) ∧
      (∀ t, i < t → t < j → ¬ (l < p t ∧ p t < h)) ∧
      (∀ t, i < t → t < j → ¬ (h < p t)) ∧
      (∀ t, j < t → ¬ (l < p t ∧ p t < h))) ↔ Geom p i j l h := by
  have ne_ends : ∀ t, t ≠ i → t ≠ j → p t ≠ l ∧ p t ≠ h := by
    intro t hti htj
    have hi := p.injective.ne hti
    have hj := p.injective.ne htj
    rcases ends with ⟨rfl, rfl⟩ | ⟨rfl, rfl⟩ <;> tauto
  constructor
  · rintro ⟨hL, hM, hU, hQ⟩
    refine ⟨?_, ?_, hQ⟩
    · intro t hti
      have hn := (ne_ends t (ne_of_lt hti) (ne_of_lt (lt_trans hti hij))).1
      have hh := hL t hti
      exact lt_of_le_of_ne (le_of_not_gt hh) (Ne.symm hn)
    · intro t hit htj
      have hn := ne_ends t (ne_of_gt hit) (ne_of_lt htj)
      have h1 := hM t hit htj
      have h2 := hU t hit htj
      rcases lt_trichotomy (p t) l with hh | hh | hh
      · exact hh
      · exact False.elim (hn.1 hh)
      · exact False.elim (h1 ⟨hh, lt_of_le_of_ne (le_of_not_gt h2) hn.2⟩)
  · rintro ⟨hL, hM, hQ⟩
    refine ⟨?_, ?_, ?_, hQ⟩
    · intro t ht
      exact not_lt_of_gt (hL t ht)
    · intro t hi hj hh
      exact (not_lt_of_gt (hM t hi hj)) hh.1
    · intro t hi hj
      exact not_lt_of_gt (lt_trans (hM t hi hj) hlh)

theorem mesh_A {n : ℕ} (p : Perm n) (i j : Fin n) :
    MeshOcc true R p i j ↔ A p i j := by
  simp only [MeshOcc, ↓reduceIte, A]
  constructor
  · rintro ⟨hij, hv, he⟩
    refine ⟨hij, hv, ?_⟩
    rw [empty_R_expansion, min_eq_left (le_of_lt hv), max_eq_right (le_of_lt hv)] at he
    exact (forbidden_iff_geom p i j (p i) (p j) hij hv (Or.inl ⟨rfl, rfl⟩)).mp he
  · rintro ⟨hij, hv, hg⟩
    refine ⟨hij, hv, ?_⟩
    rw [empty_R_expansion, min_eq_left (le_of_lt hv), max_eq_right (le_of_lt hv)]
    exact (forbidden_iff_geom p i j (p i) (p j) hij hv (Or.inl ⟨rfl, rfl⟩)).mpr hg

theorem mesh_B {n : ℕ} (p : Perm n) (i j : Fin n) :
    MeshOcc false R p i j ↔ B p i j := by
  simp only [MeshOcc, Bool.false_eq_true, ↓reduceIte, B]
  constructor
  · rintro ⟨hij, hv, he⟩
    refine ⟨hij, hv, ?_⟩
    rw [empty_R_expansion, min_eq_right (le_of_lt hv), max_eq_left (le_of_lt hv)] at he
    exact (forbidden_iff_geom p i j (p j) (p i) hij hv (Or.inr ⟨rfl, rfl⟩)).mp he
  · rintro ⟨hij, hv, hg⟩
    refine ⟨hij, hv, ?_⟩
    rw [empty_R_expansion, min_eq_right (le_of_lt hv), max_eq_left (le_of_lt hv)]
    exact (forbidden_iff_geom p i j (p j) (p i) hij hv (Or.inr ⟨rfl, rfl⟩)).mpr hg

noncomputable def occurrences {n : ℕ} (asc : Bool) (S : Finset (ℕ × ℕ))
    (p : Perm n) : Finset (Fin n × Fin n) := by
  classical
  exact Finset.univ.filter (fun e => MeshOcc asc S p e.1 e.2)

noncomputable def distribution (n k : ℕ) (asc : Bool) (S : Finset (ℕ × ℕ)) : ℕ := by
  classical
  exact (Finset.univ.filter (fun p : Perm n =>
    Function.Involutive p ∧ (occurrences asc S p).card = k)).card

def correctedConjecture : Prop :=
  ∀ n k : ℕ,
    distribution n k true R = distribution n k true R' ∧
    distribution n k true R = distribution n k false R' ∧
    distribution n k true R = distribution n k false R

end Mesh
