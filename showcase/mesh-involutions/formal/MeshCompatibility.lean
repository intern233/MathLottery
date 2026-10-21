import MeshRotation

/-! PARTIAL: the nontrivial effect of an outer rotation on an inner component. -/
namespace Mesh

def ExteriorSafe {n : ℕ} (first last low high t z : Fin n) : Prop :=
  (t < first ∧ high < z) ∨ (last < t ∧ (z < low ∨ high < z))

theorem outside_exterior_transfer {n r : ℕ} {p q : Perm n} {y w : ℕ → Fin n}
    (hr : 1 ≤ r) (hy : IncTo y r) (hw : DecTo w r) (ho : Outside p y w r)
    (hs : ∀ t, q t = p t ∨ ExteriorSafe (y 0) (y r) (w r) (w 0) t (q t)) :
    Outside q y w r := by
  have y0yr := hy.mono (Nat.zero_le r) le_rfl
  have inner_eq : ∀ t, y 0 ≤ t → t ≤ y r → q t = p t := by
    intro t ht0 htr
    rcases hs t with he | ⟨ht, _⟩ | ⟨ht, _⟩
    · exact he
    · exact False.elim ((not_lt_of_ge ht0) ht)
    · exact False.elim ((not_lt_of_ge htr) ht)
  refine ⟨?_, ?_, ?_, ?_⟩
  · intro t ht
    rcases hs t with he | ⟨_, hv⟩ | ⟨htr, _⟩
    · rw [he]
      exact ho.1 t ht
    · exact lt_of_le_of_lt (hw.le (Nat.zero_le 1) hr) hv
    · exact False.elim ((not_lt_of_ge y0yr) (lt_trans htr ht))
  · intro k hk hkr t hlt htr
    have ht0 := le_of_lt (lt_of_le_of_lt
      (hy.mono (Nat.zero_le (k-1)) (by omega)) hlt)
    have htr' := le_of_lt (lt_of_lt_of_le htr (hy.mono (le_of_lt hkr) le_rfl))
    rw [inner_eq t ht0 htr']
    exact ho.2.1 k hk hkr t hlt htr
  · intro t hlt htr
    have ht0 := le_of_lt (lt_of_le_of_lt
      (hy.mono (Nat.zero_le (r-1)) (by omega)) hlt)
    rw [inner_eq t ht0 (le_of_lt htr)]
    exact ho.2.2.1 t hlt htr
  · intro t ht hbad
    rcases hs t with he | ⟨ht0, _⟩ | ⟨_, hv | hv⟩
    · rw [he] at hbad
      exact ho.2.2.2 t ht hbad
    · exact (not_lt_of_ge y0yr) (lt_trans ht ht0)
    · exact (not_lt_of_gt hv) hbad.1
    · exact (not_lt_of_gt hv) hbad.2

def starValue {n : ℕ} (v : ℕ → Fin n) (m a : ℕ) : Fin n :=
  if a < m then v (a+1) else v 0

theorem outer_value_options {n m k : ℕ} {x v : ℕ → Fin n}
    (hx : IncTo x m) (hv : DecTo v m) (first last low high : Fin n)
    (hk : 1 ≤ k) (hkm : k ≤ m)
    (hleft : x (k-1) < first) (hright : last < x k)
    (hu : high < v k) (hl : k < m → v (k+1) < low)
    (a : ℕ) (ha : a ≤ m) :
    ExteriorSafe first last low high (x a) (v a) ∧
      ExteriorSafe first last low high (x a) (starValue v m a) := by
  by_cases hak : a < k
  · have ht : x a < first := lt_of_le_of_lt (hx.mono (by omega) (by omega)) hleft
    have hpath : high < v a := lt_of_lt_of_le hu (hv.le (le_of_lt hak) hkm)
    have hstar : high < v (a+1) := lt_of_lt_of_le hu (hv.le (by omega) hkm)
    exact ⟨Or.inl ⟨ht, hpath⟩, Or.inl ⟨ht, by simpa [starValue, show a < m by omega]⟩⟩
  · have hka : k ≤ a := by omega
    have ht : last < x a := lt_of_lt_of_le hright (hx.mono hka ha)
    have hpath : v a < low ∨ high < v a := by
      rcases eq_or_lt_of_le hka with h | h
      · rw [← h]
        exact Or.inr hu
      · exact Or.inl (lt_of_le_of_lt (hv.le (by omega : k+1 ≤ a) ha) (hl (by omega)))
    have hstar : starValue v m a < low ∨ high < starValue v m a := by
      by_cases ham : a < m
      · rw [starValue, if_pos ham]
        exact Or.inl (lt_of_le_of_lt (hv.le (by omega : k+1 ≤ a+1) (by omega)) (hl (by omega)))
      · rw [starValue, if_neg ham]
        exact Or.inr (lt_of_lt_of_le hu (hv.le (Nat.zero_le k) hkm))
    exact ⟨Or.inr ⟨ht, hpath⟩, Or.inr ⟨ht, hstar⟩⟩

theorem rotateForward_preserves_inner {n m r k : ℕ} {p : Perm n}
    {x v y w : ℕ → Fin n}
    (hx : IncTo x m) (hv : DecTo v m) (hlx : StarLayout p x v m)
    (hr : 1 ≤ r) (hy : IncTo y r) (hw : DecTo w r) (hoy : Outside p y w r)
    (hk : 1 ≤ k) (hkm : k ≤ m)
    (hleft : x (k-1) < y 0) (hright : y r < x k)
    (hu : w 0 < v k) (hl : k < m → v (k+1) < w r) :
    Outside (rotateForward p hx) y w r := by
  classical
  apply outside_exterior_transfer hr hy hw hoy
  intro t
  by_cases ht : ∃ a, a ≤ m ∧ t = x a
  · obtain ⟨a, ha, rfl⟩ := ht
    right
    rw [rotateForward_layout hx hlx a ha]
    exact (outer_value_options hx hv (y 0) (y r) (w r) (w 0)
      hk hkm hleft hright hu hl a ha).1
  · left
    apply rotateForward_fixed
    intro a ha hh
    exact ht ⟨a, ha, hh⟩

theorem rotateBackward_preserves_inner {n m r k : ℕ} {p : Perm n}
    {x v y w : ℕ → Fin n}
    (hx : IncTo x m) (hv : DecTo v m) (hlx : PathLayout p x v m)
    (hr : 1 ≤ r) (hy : IncTo y r) (hw : DecTo w r) (hoy : Outside p y w r)
    (hk : 1 ≤ k) (hkm : k ≤ m)
    (hleft : x (k-1) < y 0) (hright : y r < x k)
    (hu : w 0 < v k) (hl : k < m → v (k+1) < w r) :
    Outside (rotateBackward p hx) y w r := by
  classical
  apply outside_exterior_transfer hr hy hw hoy
  intro t
  by_cases ht : ∃ a, a ≤ m ∧ t = x a
  · obtain ⟨a, ha, rfl⟩ := ht
    right
    have hval : rotateBackward p hx (x a) = starValue v m a := by
      by_cases ham : a < m
      · rw [rotateBackward_next p hx a ham, hlx (a+1) (by omega),
          starValue, if_pos ham]
      · have ham' : a = m := by omega
        subst a
        rw [rotateBackward_last, hlx 0 (Nat.zero_le _), starValue, if_neg (lt_irrefl m)]
    rw [hval]
    exact (outer_value_options hx hv (y 0) (y r) (w r) (w 0)
      hk hkm hleft hright hu hl a ha).2
  · left
    apply rotateBackward_fixed
    intro a ha hh
    exact ht ⟨a, ha, hh⟩

theorem star_values_covered {n m : ℕ} {p : Perm n} {x v : ℕ → Fin n}
    (hl : StarLayout p x v m) (a : ℕ) (ha : a ≤ m) :
    ∃ b, b ≤ m ∧ p (x b) = v a := by
  cases a with
  | zero => exact ⟨m, le_rfl, hl.1⟩
  | succ a => exact ⟨a, by omega, hl.2 a (by omega)⟩

theorem path_values_covered {n m : ℕ} {p : Perm n} {x v : ℕ → Fin n}
    (hl : PathLayout p x v m) (a : ℕ) (ha : a ≤ m) :
    ∃ b, b ≤ m ∧ p (x b) = v a := ⟨a, ha, hl a ha⟩

theorem nested_value_bounds {n m r k : ℕ} {p : Perm n} {x v y w : ℕ → Fin n}
    (hy : IncTo y r) (hox : Outside p x v m)
    (hcover : ∀ a, a ≤ r → ∃ b, b ≤ r ∧ p (y b) = w a)
    (hk : 1 ≤ k) (hkm : k ≤ m)
    (hleft : x (k-1) < y 0) (hright : y r < x k) :
    w 0 < v k ∧ (k < m → v (k+1) < w r) := by
  have in_gap : ∀ b, b ≤ r → x (k-1) < y b ∧ y b < x k := by
    intro b hb
    exact ⟨lt_of_lt_of_le hleft (hy.mono (Nat.zero_le b) hb),
      lt_of_le_of_lt (hy.mono hb le_rfl) hright⟩
  constructor
  · obtain ⟨b, hb, heq⟩ := hcover 0 (Nat.zero_le _)
    have ht := in_gap b hb
    rw [← heq]
    exact outside_gap_upper hox hk hkm ht.1 ht.2
  · intro hkm
    obtain ⟨b, hb, heq⟩ := hcover r le_rfl
    have ht := in_gap b hb
    rw [← heq]
    exact (hox.2.1 k hk hkm (y b) ht.1 ht.2).1

end Mesh
