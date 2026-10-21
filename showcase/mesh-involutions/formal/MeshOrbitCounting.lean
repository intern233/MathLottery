import Mathlib.Algebra.BigOperators.Ring.Finset
import Mathlib.Algebra.Polynomial.Coeff
import Mathlib.Data.Finset.Powerset
import Mathlib.Algebra.BigOperators.Group.Finset.Basic
import Mathlib.Tactic.Tauto

/-!
PARTIAL: unconditional finite orbit expansion.
This proves the orbit-weight substitution step; it does not assume or supply
the marked-object bijection for the mesh patterns.
-/
namespace Mesh.OrbitCounting

open scoped BigOperators
variable {α : Type*} [DecidableEq α]

def orbit (τ : α → α) (a : α) : Finset α := {a, τ a}
def orbits (τ : α → α) (S : Finset α) : Finset (Finset α) := S.image (orbit τ)
def Stable (τ : α → α) (S : Finset α) : Prop := ∀ a ∈ S, τ a ∈ S
def InvolOn (τ : α → α) (S : Finset α) : Prop := ∀ a ∈ S, τ (τ a) = a
def unionOrbits (U : Finset (Finset α)) : Finset α := U.biUnion id

theorem self_mem_orbit (τ : α → α) (a : α) : a ∈ orbit τ a := by simp [orbit]

theorem orbit_eq_of_mem {τ : α → α} {a b : α} (ha : τ (τ a) = a)
    (hb : b ∈ orbit τ a) : orbit τ b = orbit τ a := by
  simp only [orbit, Finset.mem_insert, Finset.mem_singleton] at hb
  rcases hb with rfl | rfl
  · rfl
  · simp [orbit, ha, Finset.pair_comm]

theorem union_all_orbits {τ : α → α} {S : Finset α} (hs : Stable τ S) :
    unionOrbits (orbits τ S) = S := by
  ext a
  simp only [unionOrbits, Finset.mem_biUnion, orbits, Finset.mem_image, id_eq]
  constructor
  · rintro ⟨O, ⟨b, hb, rfl⟩, ha⟩
    simp only [orbit, Finset.mem_insert, Finset.mem_singleton] at ha
    rcases ha with rfl | rfl
    · exact hb
    · exact hs b hb
  · intro ha
    exact ⟨orbit τ a, ⟨a, ha, rfl⟩, self_mem_orbit τ a⟩

theorem orbits_mono {τ : α → α} {S T : Finset α} (h : S ⊆ T) :
    orbits τ S ⊆ orbits τ T := Finset.image_subset_image h

theorem union_sub_orbits {τ : α → α} {S : Finset α} {U : Finset (Finset α)}
    (hs : Stable τ S) (hU : U ⊆ orbits τ S) : unionOrbits U ⊆ S := by
  rw [← union_all_orbits hs]
  intro a ha
  obtain ⟨O, hO, haO⟩ := Finset.mem_biUnion.mp ha
  exact Finset.mem_biUnion.mpr ⟨O, hU hO, haO⟩

theorem union_sub_stable {τ : α → α} {S : Finset α} {U : Finset (Finset α)}
    (hi : InvolOn τ S) (hU : U ⊆ orbits τ S) : Stable τ (unionOrbits U) := by
  intro a ha
  obtain ⟨O, hO, haO⟩ := Finset.mem_biUnion.mp ha
  obtain ⟨b, hb, hOb⟩ := Finset.mem_image.mp (hU hO)
  change orbit τ b = O at hOb
  rw [← hOb] at haO
  apply Finset.mem_biUnion.mpr
  refine ⟨O, hO, ?_⟩
  rw [← hOb]
  change τ a ∈ orbit τ b
  change a ∈ orbit τ b at haO
  simp only [orbit, Finset.mem_insert, Finset.mem_singleton] at haO ⊢
  rcases haO with rfl | rfl
  · exact Or.inr rfl
  · exact Or.inl (hi b hb)

theorem orbits_union_sub {τ : α → α} {S : Finset α} {U : Finset (Finset α)}
    (hi : InvolOn τ S) (hU : U ⊆ orbits τ S) :
    orbits τ (unionOrbits U) = U := by
  ext O
  constructor
  · intro hO
    obtain ⟨a, ha, rfl⟩ := Finset.mem_image.mp hO
    obtain ⟨P, hP, haP⟩ := Finset.mem_biUnion.mp ha
    obtain ⟨b, hb, rfl⟩ := Finset.mem_image.mp (hU hP)
    change a ∈ orbit τ b at haP
    rw [orbit_eq_of_mem (hi b hb) haP]
    exact hP
  · intro hO
    obtain ⟨b, hb, rfl⟩ := Finset.mem_image.mp (hU hO)
    apply Finset.mem_image.mpr
    exact ⟨b, Finset.mem_biUnion.mpr ⟨orbit τ b, hO, self_mem_orbit τ b⟩, rfl⟩

theorem distinct_orbits_disjoint {τ : α → α} {S : Finset α}
    (hi : InvolOn τ S) :
    (orbits τ S : Set (Finset α)).PairwiseDisjoint id := by
  intro O hO P hP hne
  apply Finset.disjoint_left.mpr
  intro a haO haP
  obtain ⟨b, hb, rfl⟩ := Finset.mem_image.mp hO
  obtain ⟨c, hc, rfl⟩ := Finset.mem_image.mp hP
  apply hne
  exact (orbit_eq_of_mem (hi b hb) haO).symm.trans (orbit_eq_of_mem (hi c hc) haP)

theorem sum_orbit_cards {τ : α → α} {S : Finset α}
    (hs : Stable τ S) (hi : InvolOn τ S) :
    ∑ O ∈ orbits τ S, O.card = S.card := by
  calc
    ∑ O ∈ orbits τ S, O.card = (unionOrbits (orbits τ S)).card :=
      (Finset.card_biUnion (distinct_orbits_disjoint hi)).symm
    _ = S.card := congrArg Finset.card (union_all_orbits hs)

noncomputable def invariantSubsets (τ : α → α) (S : Finset α) : Finset (Finset α) := by
  classical
  exact S.powerset.filter (Stable τ)

theorem invariant_subsets_sum {τ : α → α} {S : Finset α}
    (hs : Stable τ S) (hi : InvolOn τ S)
    {β : Type*} [AddCommMonoid β] (F : Finset (Finset α) → β) :
    (∑ M ∈ invariantSubsets τ S, F (orbits τ M)) =
      ∑ U ∈ (orbits τ S).powerset, F U := by
  classical
  refine Finset.sum_bij (fun M _ => orbits τ M) ?_ ?_ ?_ ?_
  · intro M hM
    simp only [invariantSubsets, Finset.mem_filter, Finset.mem_powerset] at hM ⊢
    exact orbits_mono hM.1
  · intro M hM N hN hMN
    simp only [invariantSubsets, Finset.mem_filter, Finset.mem_powerset] at hM hN
    have hm := union_all_orbits hM.2
    have hn := union_all_orbits hN.2
    rw [hMN] at hm
    exact hm.symm.trans hn
  · intro U hU
    have hu := Finset.mem_powerset.mp hU
    refine ⟨unionOrbits U, ?_, orbits_union_sub hi hu⟩
    simp only [invariantSubsets, Finset.mem_filter, Finset.mem_powerset]
    exact ⟨union_sub_orbits hs hu, union_sub_stable hi hu⟩
  · intro M hM
    rfl

theorem weighted_invariant_subset_expansion {τ : α → α} {S : Finset α}
    (hs : Stable τ S) (hi : InvolOn τ S) {K : Type*} [CommRing K] (z : K) :
    (∑ M ∈ invariantSubsets τ S, ∏ O ∈ orbits τ M, (z ^ O.card - 1)) =
      z ^ S.card := by
  rw [invariant_subsets_sum hs hi (fun U => ∏ O ∈ U, (z ^ O.card - 1))]
  rw [← Finset.prod_add_one]
  simp only [sub_add_cancel]
  rw [Finset.prod_pow_eq_pow_sum, sum_orbit_cards hs hi]

theorem orbit_size_one_or_two {τ : α → α} {a : α} :
    (orbit τ a).card = 1 ∨ (orbit τ a).card = 2 := by
  by_cases h : a = τ a
  · left
    simp [orbit, ← h]
  · right
    simp [orbit, h]

end Mesh.OrbitCounting
