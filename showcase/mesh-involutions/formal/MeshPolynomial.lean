import MeshSymmetry
import MeshOrbitCounting

/-!
PARTIAL: generating-polynomial equivalence for the literal all-n/all-k target,
and the orbit-weight expansion applied to actual mesh occurrences.
-/
namespace Mesh

open scoped BigOperators
open Polynomial

noncomputable def involutions (n : ℕ) : Finset (Perm n) := by
  classical
  exact Finset.univ.filter (Function.Involutive ·)

noncomputable def generating (n : ℕ) (asc : Bool) (S : Finset (ℕ × ℕ)) : Polynomial ℤ :=
  ∑ p ∈ involutions n, X ^ (occurrences asc S p).card

theorem distribution_as_filter (n k : ℕ) (asc : Bool) (S : Finset (ℕ × ℕ)) :
    distribution n k asc S =
      ((involutions n).filter (fun p => (occurrences asc S p).card = k)).card := by
  classical
  simp [distribution, involutions, Finset.filter_filter]

theorem generating_coeff (n k : ℕ) (asc : Bool) (S : Finset (ℕ × ℕ)) :
    (generating n asc S).coeff k = (distribution n k asc S : ℤ) := by
  classical
  rw [generating, Polynomial.finsetSum_coeff, distribution_as_filter, Finset.card_eq_sum_ones]
  simp only [Polynomial.coeff_X_pow, Nat.cast_sum, Finset.sum_filter]
  apply Finset.sum_congr rfl
  intro p hp
  by_cases h : k = (occurrences asc S p).card <;> simp [h, eq_comm]

theorem generating_eq_iff_distributions (n : ℕ) (a b : Bool)
    (S T : Finset (ℕ × ℕ)) :
    generating n a S = generating n b T ↔
      ∀ k : ℕ, distribution n k a S = distribution n k b T := by
  constructor
  · intro h k
    have hc := congrArg (fun P : Polynomial ℤ => P.coeff k) h
    rw [generating_coeff, generating_coeff] at hc
    exact Nat.cast_injective hc
  · intro h
    apply Polynomial.ext
    intro k
    rw [generating_coeff, generating_coeff, h k]

theorem involutive_symm {n : ℕ} {p : Perm n} (hp : Function.Involutive p) :
    p.symm = p := by
  apply Equiv.ext
  intro i
  exact p.symm_apply_eq.mpr (hp i).symm

theorem occurrence_transpose_stable {n : ℕ} (asc : Bool) {p : Perm n}
    (hp : Function.Involutive p) :
    OrbitCounting.Stable (transposeEdge p) (occurrences asc R p) := by
  classical
  rintro ⟨i,j⟩ he
  simp only [occurrences, Finset.mem_filter, Finset.mem_univ, true_and] at he ⊢
  cases asc with
  | false =>
    have hb := (mesh_B p i j).mp he
    have hb' := B_inverse p hb
    rw [involutive_symm hp] at hb'
    change MeshOcc false R p
      (min (p i) (p j)) (max (p i) (p j))
    rw [min_eq_right (le_of_lt hb.2.1), max_eq_left (le_of_lt hb.2.1)]
    exact (mesh_B p (p j) (p i)).mpr hb'
  | true =>
    have ha := (mesh_A p i j).mp he
    have ha' := A_inverse p ha
    rw [involutive_symm hp] at ha'
    change MeshOcc true R p
      (min (p i) (p j)) (max (p i) (p j))
    rw [min_eq_left (le_of_lt ha.2.1), max_eq_right (le_of_lt ha.2.1)]
    exact (mesh_A p (p i) (p j)).mpr ha'

theorem occurrence_transpose_involutive {n : ℕ} (asc : Bool) {p : Perm n}
    (hp : Function.Involutive p) :
    OrbitCounting.InvolOn (transposeEdge p) (occurrences asc R p) := by
  classical
  rintro ⟨i,j⟩ he
  simp only [occurrences, Finset.mem_filter, Finset.mem_univ, true_and] at he
  have hh := transpose_twice p he.1
  rwa [involutive_symm hp] at hh

noncomputable def markedWeight {n : ℕ} (p : Perm n) (M : Finset (Fin n × Fin n)) :
    Polynomial ℤ :=
  ∏ O ∈ OrbitCounting.orbits (transposeEdge p) M, (X ^ O.card - 1)

theorem actual_orbit_expansion {n : ℕ} (asc : Bool) {p : Perm n}
    (hp : Function.Involutive p) :
    (∑ M ∈ OrbitCounting.invariantSubsets (transposeEdge p) (occurrences asc R p),
      markedWeight p M) = (X : Polynomial ℤ) ^ (occurrences asc R p).card :=
  OrbitCounting.weighted_invariant_subset_expansion
    (occurrence_transpose_stable asc hp) (occurrence_transpose_involutive asc hp) X

theorem actual_generating_marked_expansion (n : ℕ) (asc : Bool) :
    generating n asc R =
      ∑ p ∈ involutions n,
        ∑ M ∈ OrbitCounting.invariantSubsets (transposeEdge p) (occurrences asc R p),
          markedWeight p M := by
  classical
  apply Finset.sum_congr rfl
  intro p hp
  exact (actual_orbit_expansion asc (Finset.mem_filter.mp hp).2).symm

end Mesh
