import MeshOrbitCounting

/-!
Controller continuation. Unconditional finite-set theorem: a bijection of
marked edges that intertwines transposition preserves their orbit weight.
This module does not construct the global mesh-pattern bijection.
-/
namespace Mesh.OrbitCounting

open scoped BigOperators

variable {α β : Type*} [DecidableEq α] [DecidableEq β]

theorem member_orbit_subset {τ : α → α} {S : Finset α}
    (hs : Stable τ S) {O : Finset α} (hO : O ∈ orbits τ S) : O ⊆ S := by
  obtain ⟨a, ha, rfl⟩ := Finset.mem_image.mp hO
  intro b hb
  simp only [orbit, Finset.mem_insert, Finset.mem_singleton] at hb
  rcases hb with rfl | rfl
  · exact ha
  · exact hs a ha

theorem orbit_image {τ : α → α} {υ : β → β} {f : α → β} {a : α}
    (h : f (τ a) = υ (f a)) : (orbit τ a).image f = orbit υ (f a) := by
  simp [orbit, h]

theorem orbits_transport {τ : α → α} {υ : β → β} {S : Finset α} {T : Finset β}
    (f : α → β) (himage : S.image f = T)
    (hcomm : ∀ a ∈ S, f (τ a) = υ (f a)) :
    (orbits τ S).image (Finset.image f) = orbits υ T := by
  subst T
  simp only [orbits, Finset.image_image]
  apply Finset.image_congr
  intro a ha
  exact orbit_image (hcomm a ha)

theorem orbit_weight_transport {τ : α → α} {υ : β → β}
    {S : Finset α} {T : Finset β} (hs : Stable τ S)
    (f : α → β) (hf : Set.BijOn f S T)
    (hcomm : ∀ a ∈ S, f (τ a) = υ (f a))
    {K : Type*} [CommRing K] (z : K) :
    (∏ O ∈ orbits τ S, (z ^ O.card - 1)) =
      ∏ O ∈ orbits υ T, (z ^ O.card - 1) := by
  have himage : S.image f = T :=
    Finset.image_eq_iff_surjOn_mapsTo.mpr ⟨hf.2.2, hf.1⟩
  rw [← orbits_transport f himage hcomm]
  rw [Finset.prod_image]
  · apply Finset.prod_congr rfl
    intro O hO
    rw [Finset.card_image_of_injOn (hf.2.1.mono (member_orbit_subset hs hO))]
  · intro O hO P hP heq
    exact (Finset.image_eq_image_iff_of_injOn hf.2.1
      (member_orbit_subset hs hO) (member_orbit_subset hs hP)).mp heq

end Mesh.OrbitCounting
