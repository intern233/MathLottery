import MeshStructure

/-! PARTIAL: ordered components and their exact outside-region characterization. -/
namespace Mesh

def IncTo {α : Type*} [LT α] (x : ℕ → α) (m : ℕ) : Prop :=
  ∀ a b, a < b → b ≤ m → x a < x b

theorem IncTo.mono {α : Type*} [LinearOrder α] {x : ℕ → α} {m a b : ℕ}
    (hx : IncTo x m) (hab : a ≤ b) (hbm : b ≤ m) : x a ≤ x b := by
  rcases eq_or_lt_of_le hab with h | h
  · rw [h]
  · exact le_of_lt (hx a b h hbm)

theorem IncTo.reflect {α : Type*} [LinearOrder α] {x : ℕ → α} {m a b : ℕ}
    (hx : IncTo x m) (ham : a ≤ m) (hab : x a < x b) : a < b := by
  by_contra h
  exact (not_lt_of_ge (hx.mono (le_of_not_gt h) ham)) hab

theorem chain_cases {α : Type*} [LinearOrder α] (x : ℕ → α) (m : ℕ)
    (hx : IncTo x m) (t : α) :
    t < x 0 ∨ (∃ a, a ≤ m ∧ t = x a) ∨
      (∃ k, 1 ≤ k ∧ k ≤ m ∧ x (k - 1) < t ∧ t < x k) ∨ x m < t := by
  induction m with
  | zero =>
    rcases lt_trichotomy t (x 0) with h | h | h
    · exact Or.inl h
    · exact Or.inr (Or.inl ⟨0, le_rfl, h⟩)
    · exact Or.inr (Or.inr (Or.inr h))
  | succ m ih =>
    have hx' : IncTo x m := fun a b hab hbm => hx a b hab (by omega)
    rcases ih hx' with h | ⟨a, ha, ht⟩ | ⟨k, hk, hkm, hkt, htk⟩ | h
    · exact Or.inl h
    · exact Or.inr (Or.inl ⟨a, by omega, ht⟩)
    · exact Or.inr (Or.inr (Or.inl ⟨k, hk, by omega, hkt, htk⟩))
    · rcases lt_trichotomy t (x (m+1)) with ht | ht | ht
      · exact Or.inr (Or.inr (Or.inl ⟨m+1, by omega, le_rfl, by simpa, ht⟩))
      · exact Or.inr (Or.inl ⟨m+1, le_rfl, ht⟩)
      · exact Or.inr (Or.inr (Or.inr ht))

def DecTo {n : ℕ} (v : ℕ → Fin n) (m : ℕ) : Prop :=
  IncTo (α := (Fin n)ᵒᵈ) v m

theorem DecTo.lt {n : ℕ} {v : ℕ → Fin n} {m a b : ℕ}
    (hv : DecTo v m) (hab : a < b) (hbm : b ≤ m) : v b < v a :=
  hv a b hab hbm

theorem DecTo.le {n : ℕ} {v : ℕ → Fin n} {m a b : ℕ}
    (hv : DecTo v m) (hab : a ≤ b) (hbm : b ≤ m) : v b ≤ v a :=
  IncTo.mono (α := (Fin n)ᵒᵈ) hv hab hbm

def StarLayout {n : ℕ} (p : Perm n) (x v : ℕ → Fin n) (m : ℕ) : Prop :=
  p (x m) = v 0 ∧ ∀ a, a < m → p (x a) = v (a + 1)

def PathLayout {n : ℕ} (p : Perm n) (x v : ℕ → Fin n) (m : ℕ) : Prop :=
  ∀ a, a ≤ m → p (x a) = v a

def StarEdges {n : ℕ} (p : Perm n) (x : ℕ → Fin n) (m : ℕ) : Prop :=
  ∀ h, 1 ≤ h → h ≤ m → A p (x (h - 1)) (x m)

def PathEdges {n : ℕ} (p : Perm n) (x : ℕ → Fin n) (m : ℕ) : Prop :=
  ∀ h, 1 ≤ h → h ≤ m → B p (x (h - 1)) (x h)

def Outside {n : ℕ} (p : Perm n) (x v : ℕ → Fin n) (m : ℕ) : Prop :=
  (∀ t, t < x 0 → v 1 < p t) ∧
  (∀ k, 1 ≤ k → k < m → ∀ t, x (k-1) < t → t < x k →
    v (k+1) < p t ∧ p t < v k) ∧
  (∀ t, x (m-1) < t → t < x m → p t < v m) ∧
  (∀ t, x m < t → ¬ (v m < p t ∧ p t < v 0))

theorem star_outside {n : ℕ} {p : Perm n} {x v : ℕ → Fin n} {m : ℕ}
    (hm : 1 ≤ m) (hx : IncTo x m) (hl : StarLayout p x v m)
    (he : StarEdges p x m) : Outside p x v m := by
  have leaf : ∀ h, 1 ≤ h → h ≤ m → p (x (h-1)) = v h := by
    intro h hh hhm
    have hh' := hl.2 (h-1) (by omega)
    simpa [Nat.sub_add_cancel hh] using hh'
  refine ⟨?_, ?_, ?_, ?_⟩
  · intro t ht
    have hh := (he 1 le_rfl hm).2.2.1 t (by simpa using ht)
    change p (x 0) < p t at hh
    rw [hl.2 0 (by omega)] at hh
    exact hh
  · intro k hk hkm t hlt htr
    have hk1 : k+1 ≤ m := by omega
    have lower := (he (k+1) (by omega) hk1).2.2.1 t (by simpa using htr)
    have upper := (he k hk (by omega)).2.2.2.1 t hlt
      (lt_trans htr (hx k m hkm le_rfl))
    constructor
    · change p (x k) < p t at lower
      rw [hl.2 k hkm] at lower
      exact lower
    · simpa [leaf k hk (by omega)] using upper
  · intro t ht1 ht2
    have hh := (he m hm le_rfl).2.2.2.1 t ht1 ht2
    simpa [leaf m hm le_rfl] using hh
  · intro t ht
    have hh := (he m hm le_rfl).2.2.2.2 t ht
    simpa [leaf m hm le_rfl, hl.1] using hh

theorem path_outside {n : ℕ} {p : Perm n} {x v : ℕ → Fin n} {m : ℕ}
    (hm : 1 ≤ m) (hx : IncTo x m) (hv : DecTo v m)
    (hl : PathLayout p x v m) (he : PathEdges p x m) :
    Outside p x v m := by
  refine ⟨?_, ?_, ?_, ?_⟩
  · intro t ht
    have hh := (he 1 le_rfl hm).2.2.1 t (by simpa using ht)
    simpa [hl 1 hm] using hh
  · intro k hk hkm t hlt htr
    have hk1 : k+1 ≤ m := by omega
    have lower := (he (k+1) (by omega) hk1).2.2.1 t (by simpa using htr)
    have upper := (he k hk (by omega)).2.2.2.1 t hlt htr
    constructor
    · simpa [hl (k+1) hk1] using lower
    · simpa [hl k (by omega)] using upper
  · intro t ht1 ht2
    have hh := (he m hm le_rfl).2.2.2.1 t ht1 ht2
    simpa [hl m le_rfl] using hh
  · intro t ht hbad
    rcases chain_cases (α := (Fin n)ᵒᵈ) v m hv (p t) with
      h | ⟨a, ha, hta⟩ | ⟨k, hk, hkm, hkt, htk⟩ | h
    · exact (not_lt_of_gt hbad.2) h
    · have hval : p t = p (x a) := hta.trans (hl a ha).symm
      have hpos := p.injective hval
      have hax := hx.mono ha le_rfl
      rw [hpos] at ht
      exact (not_lt_of_ge hax) ht
    · have hh := (he k hk hkm).2.2.2.2 t
        (lt_of_le_of_lt (hx.mono hkm le_rfl) ht)
      apply hh
      rw [hl k hkm, hl (k-1) (by omega)]
      exact ⟨htk, hkt⟩
    · exact (not_lt_of_gt hbad.1) h

theorem outside_left {n : ℕ} {p : Perm n} {x v : ℕ → Fin n} {m s : ℕ}
    (hx : IncTo x m) (hv : DecTo v m) (ho : Outside p x v m)
    (hs : s ≤ 1) (hl : ∀ a, a < m → p (x a) = v (a+s))
    {h : ℕ} (hh : 1 ≤ h) (hhm : h ≤ m) {t : Fin n}
    (ht : t < x (h-1)) : v h < p t := by
  have hx' : IncTo x (h-1) := fun a b hab hbm => hx a b hab (by omega)
  rcases chain_cases x (h-1) hx' t with
    ht0 | ⟨a, ha, hta⟩ | ⟨k, hk, hkm, hkt, htk⟩ | htt
  · exact lt_of_le_of_lt (hv.le hh hhm) (ho.1 t ht0)
  · rw [hta] at ht ⊢
    have ha' := hx.reflect (show a ≤ m by omega) ht
    rw [hl a (by omega)]
    exact hv.lt (by omega) hhm
  · have hh' := (ho.2.1 k hk (by omega) t hkt htk).1
    exact lt_of_le_of_lt (hv.le (by omega : k+1 ≤ h) hhm) hh'
  · exact False.elim ((not_lt_of_gt ht) htt)

theorem outside_gap_upper {n : ℕ} {p : Perm n} {x v : ℕ → Fin n} {m k : ℕ}
    (ho : Outside p x v m) (hk : 1 ≤ k) (hkm : k ≤ m) {t : Fin n}
    (hkt : x (k-1) < t) (htk : t < x k) : p t < v k := by
  rcases eq_or_lt_of_le hkm with rfl | hkm
  · exact ho.2.2.1 t hkt htk
  · exact (ho.2.1 k hk hkm t hkt htk).2

theorem outside_star_middle {n : ℕ} {p : Perm n} {x v : ℕ → Fin n} {m : ℕ}
    (hx : IncTo x m) (hv : DecTo v m) (ho : Outside p x v m)
    (hl : StarLayout p x v m) {h : ℕ} (hh : 1 ≤ h) (hhm : h ≤ m)
    {t : Fin n} (htl : x (h-1) < t) (htr : t < x m) : p t < v h := by
  rcases chain_cases x m hx t with
    ht0 | ⟨a, ha, hta⟩ | ⟨k, hk, hkm, hkt, htk⟩ | htt
  · have h0 := hx.mono (show 0 ≤ h-1 by omega) (show h-1 ≤ m by omega)
    exact False.elim ((not_lt_of_ge h0) (lt_trans htl ht0))
  · rw [hta] at htl htr ⊢
    have ha1 := hx.reflect (show h-1 ≤ m by omega) htl
    have ha2 := hx.reflect ha htr
    rw [hl.2 a ha2]
    exact hv.lt (by omega) (by omega)
  · have hh' := hx.reflect (show h-1 ≤ m by omega) (lt_trans htl htk)
    have upper := outside_gap_upper ho hk hkm hkt htk
    exact lt_of_lt_of_le upper (hv.le (by omega : h ≤ k) hkm)
  · exact False.elim ((not_lt_of_gt htr) htt)

theorem outside_star {n : ℕ} {p : Perm n} {x v : ℕ → Fin n} {m : ℕ}
    (hx : IncTo x m) (hv : DecTo v m)
    (hl : StarLayout p x v m) (ho : Outside p x v m) : StarEdges p x m := by
  intro h hh hhm
  have hpred : h-1 < m := by omega
  have leaf : p (x (h-1)) = v h := by
    simpa [Nat.sub_add_cancel hh] using hl.2 (h-1) hpred
  refine ⟨hx (h-1) m hpred le_rfl, ?_, ?_⟩
  · rw [leaf, hl.1]
    exact hv.lt (by omega) hhm
  · rw [show Geom p (x (h-1)) (x m) (p (x (h-1))) (p (x m)) ↔
        Geom p (x (h-1)) (x m) (v h) (v 0) by rw [leaf, hl.1]]
    refine ⟨?_, ?_, ?_⟩
    · intro t ht
      exact outside_left hx hv ho (s := 1) le_rfl hl.2 hh hhm ht
    · intro t htl htr
      exact outside_star_middle hx hv ho hl hh hhm htl htr
    · intro t ht hbad
      exact ho.2.2.2 t ht ⟨lt_of_le_of_lt (hv.le hhm le_rfl) hbad.1, hbad.2⟩

theorem outside_path_right {n : ℕ} {p : Perm n} {x v : ℕ → Fin n} {m h : ℕ}
    (hx : IncTo x m) (hv : DecTo v m) (ho : Outside p x v m)
    (hl : PathLayout p x v m) (hh : 1 ≤ h) (hhm : h ≤ m)
    {t : Fin n} (ht : x h < t) : ¬ (v h < p t ∧ p t < v (h-1)) := by
  intro hbad
  rcases chain_cases x m hx t with
    ht0 | ⟨a, ha, hta⟩ | ⟨k, hk, hkm, hkt, htk⟩ | htt
  · have h0 := hx.mono (show 0 ≤ h by omega) hhm
    exact (not_lt_of_ge h0) (lt_trans ht ht0)
  · rw [hta] at ht hbad
    have ha' := hx.reflect hhm ht
    rw [hl a ha] at hbad
    exact (not_lt_of_gt (hv.lt ha' ha)) hbad.1
  · have hhk := hx.reflect hhm (lt_trans ht htk)
    have upper := outside_gap_upper ho hk hkm hkt htk
    exact (not_lt_of_gt (lt_trans upper (hv.lt hhk hkm))) hbad.1
  · apply ho.2.2.2 t htt
    exact ⟨lt_of_le_of_lt (hv.le hhm le_rfl) hbad.1,
      lt_of_lt_of_le hbad.2 (hv.le (show 0 ≤ h-1 by omega) (by omega))⟩

theorem outside_path {n : ℕ} {p : Perm n} {x v : ℕ → Fin n} {m : ℕ}
    (hx : IncTo x m) (hv : DecTo v m)
    (hl : PathLayout p x v m) (ho : Outside p x v m) : PathEdges p x m := by
  intro h hh hhm
  have hpred : h-1 < h := by omega
  have hhpred : h-1 ≤ m := by omega
  refine ⟨hx (h-1) h hpred hhm, ?_, ?_⟩
  · rw [hl h hhm, hl (h-1) hhpred]
    exact hv.lt hpred hhm
  · rw [show Geom p (x (h-1)) (x h) (p (x h)) (p (x (h-1))) ↔
        Geom p (x (h-1)) (x h) (v h) (v (h-1)) by rw [hl h hhm, hl (h-1) hhpred]]
    refine ⟨?_, ?_, ?_⟩
    · intro t ht
      apply outside_left hx hv ho (s := 0) (by omega) ?_ hh hhm ht
      intro a ha
      simpa using hl a (le_of_lt ha)
    · intro t htl htr
      exact outside_gap_upper ho hh hhm htl htr
    · intro t ht
      exact outside_path_right hx hv ho hl hh hhm ht

theorem star_characterization {n : ℕ} {p : Perm n} {x v : ℕ → Fin n} {m : ℕ}
    (hm : 1 ≤ m) (hx : IncTo x m) (hv : DecTo v m) (hl : StarLayout p x v m) :
    StarEdges p x m ↔ Outside p x v m :=
  ⟨star_outside hm hx hl, outside_star hx hv hl⟩

theorem path_characterization {n : ℕ} {p : Perm n} {x v : ℕ → Fin n} {m : ℕ}
    (hm : 1 ≤ m) (hx : IncTo x m) (hv : DecTo v m) (hl : PathLayout p x v m) :
    PathEdges p x m ↔ Outside p x v m :=
  ⟨path_outside hm hx hv hl, outside_path hx hv hl⟩

end Mesh
