import MeshPolynomial
import MeshTransport
import Mathlib.Algebra.BigOperators.Group.Finset.Sigma

/-!
PARTIAL formalization, controller continuation.

The conclusion below is the exact literal all-n/all-k conjecture, but its
global marked-object transport is an explicit hypothesis, not a proved fact.
Constructing that transport from arbitrary occurrence subsets remains open in
this Lean development. No axiom or `sorry` supplies it.
-/
namespace Mesh

open scoped BigOperators

abbrev Marked (n : ℕ) := Σ _p : Perm n, Finset (Fin n × Fin n)

noncomputable def fixedMarked (n : ℕ) (asc : Bool) : Finset (Marked n) :=
  (involutions n).sigma fun p =>
    OrbitCounting.invariantSubsets (transposeEdge p) (occurrences asc R p)

theorem fixedMarked_info {n : ℕ} {asc : Bool} {a : Marked n}
    (ha : a ∈ fixedMarked n asc) :
    Function.Involutive a.1 ∧ a.2 ⊆ occurrences asc R a.1 ∧
      OrbitCounting.Stable (transposeEdge a.1) a.2 := by
  classical
  rcases Finset.mem_sigma.mp ha with ⟨hp, hM⟩
  simp only [involutions, Finset.mem_filter, Finset.mem_univ, true_and] at hp
  simp only [OrbitCounting.invariantSubsets, Finset.mem_filter,
    Finset.mem_powerset] at hM
  exact ⟨hp, hM⟩

theorem generating_as_fixedMarked (n : ℕ) (asc : Bool) :
    generating n asc R = ∑ a ∈ fixedMarked n asc, markedWeight a.1 a.2 := by
  rw [actual_generating_marked_expansion]
  exact Finset.sum_sigma' _ _ _

/-- The exact remaining construction. A witness must work on *all* marked
objects of the literal occurrences, and on each individual marked edge. -/
structure MarkedTransport (n : ℕ) where
  objectMap : Marked n → Marked n
  objects_bijective : Set.BijOn objectMap (fixedMarked n true) (fixedMarked n false)
  edgeMap : Marked n → (Fin n × Fin n) → (Fin n × Fin n)
  edges_bijective : ∀ a ∈ fixedMarked n true,
    Set.BijOn (edgeMap a) a.2 (objectMap a).2
  edges_equivariant : ∀ a ∈ fixedMarked n true, ∀ e ∈ a.2,
    edgeMap a (transposeEdge a.1 e) =
      transposeEdge (objectMap a).1 (edgeMap a e)

theorem MarkedTransport.preserves_weight {n : ℕ} (T : MarkedTransport n)
    (a : Marked n) (ha : a ∈ fixedMarked n true) :
    markedWeight a.1 a.2 = markedWeight (T.objectMap a).1 (T.objectMap a).2 := by
  classical
  exact OrbitCounting.orbit_weight_transport (fixedMarked_info ha).2.2
    (T.edgeMap a) (T.edges_bijective a ha) (T.edges_equivariant a ha)
    (Polynomial.X : Polynomial ℤ)

theorem generating_eq_of_markedTransport {n : ℕ} (T : MarkedTransport n) :
    generating n true R = generating n false R := by
  classical
  rw [generating_as_fixedMarked, generating_as_fixedMarked]
  refine Finset.sum_bij (fun a _ => T.objectMap a) ?_ ?_ ?_ ?_
  · intro a ha
    exact T.objects_bijective.1 ha
  · intro a ha b hb hab
    exact T.objects_bijective.2.1 ha hb hab
  · intro b hb
    obtain ⟨a, ha, hab⟩ := T.objects_bijective.2.2 hb
    exact ⟨a, ha, hab⟩
  · intro a ha
    exact T.preserves_weight a ha

/-- Conditional reduction only. There is deliberately no unconditional theorem
of type `correctedConjecture` in this partial development. -/
theorem correctedConjecture_of_markedTransport
    (h : ∀ n : ℕ, Nonempty (MarkedTransport n)) : correctedConjecture := by
  intro n k
  obtain ⟨T⟩ := h n
  have hab := (generating_eq_iff_distributions n true false R R).mp
    (generating_eq_of_markedTransport T) k
  exact ⟨distribution_reverse n k true,
    hab.trans (distribution_reverse n k false), hab⟩

end Mesh
