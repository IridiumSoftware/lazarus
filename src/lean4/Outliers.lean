-- Outliers.lean — hermetic Lean4 proof of the abstract outlier-
-- detection algorithm whose Python implementation lives at
-- `face_sentinel._outliers_from_scores` (LZ-014, :tested via
-- `test/test_prune_logic.py`).
--
-- LZ-016 spec entry: the Python helper is example-tested as a
-- concrete algorithm; this Lean file is the matching abstract
-- algorithm proved as a structural skeleton (per the TCE
-- convention of proving the mathematical content separately
-- from its imperative implementation). Promotion to :proved
-- via lean-proved evidence.
--
-- Model. Scores are `List Nat` (Apple Vision distances are
-- non-negative reals in production; the algorithm's
-- correctness is shape-invariant under uniform scaling, so
-- Nat suffices for the mathematical content). The multiplier
-- is `m : Nat` (default 2 in production, matching
-- `PRUNE_OUTLIER_MULTIPLIER = 2.0`). To stay in pure Nat
-- without rationals or division we use the division-free
-- form of the outlier predicate:
--
--     v is an outlier ⟺ v * |s| > m * Σs
--
-- This is identical to the Python predicate `v > m * mean`
-- multiplied through by `|s|`, with the inequality direction
-- preserved (multiplying both sides of `a > b` by a positive
-- `c` preserves `>`).
--
-- Theorems proved (all hermetic — no Mathlib, only Lean core):
--   - outliers_subset: output is a sublist of input
--   - outliers_empty:  empty input → empty output
--   - outliers_singleton: |s| = 1 with m ≥ 1 → empty output
--   - outliers_constant: all-same `s` with m ≥ 1 → empty output
--   - outliers_monotone_threshold: m₁ ≤ m₂ implies
--     outliers m₂ s ⊆ outliers m₁ s (higher threshold = fewer
--     outliers).

namespace Lazarus.Outliers

/-- Outlier predicate (division-free form):
    `v` is an outlier of `s` at multiplier `m` iff
    `v * |s| > m * Σs`. -/
def isOutlier (v : Nat) (m : Nat) (s : List Nat) : Bool :=
  v * s.length > m * s.sum

/-- The outlier sublist: values from `s` satisfying
    `isOutlier _ m s`. -/
def outliers (m : Nat) (s : List Nat) : List Nat :=
  s.filter (fun v => isOutlier v m s)

-- ── Theorem 1: outliers is a sublist of input ─────────────────────

theorem outliers_subset (m : Nat) (s : List Nat) :
    ∀ v ∈ outliers m s, v ∈ s := by
  intro v hv
  unfold outliers at hv
  exact (List.mem_filter.mp hv).1

-- ── Theorem 2: empty input → empty output ──────────────────────────

theorem outliers_empty (m : Nat) : outliers m [] = [] := by
  unfold outliers
  rfl

-- ── Theorem 3: singleton input with m ≥ 1 → empty output ──────────

theorem outliers_singleton (m : Nat) (v : Nat) (hm : 1 ≤ m) :
    outliers m [v] = [] := by
  unfold outliers
  simp only [List.filter_cons, List.filter_nil]
  have hpred : isOutlier v m [v] = false := by
    unfold isOutlier
    simp only [List.length_singleton, List.sum_cons,
               List.sum_nil, Nat.add_zero, Nat.mul_one,
               decide_eq_false_iff_not]
    intro hgt
    have : v ≤ m * v := Nat.le_mul_of_pos_left v hm
    omega
  rw [hpred]
  rfl

-- ── Theorem 4: constant-pool with m ≥ 1 → empty output ────────────

/-- If every element of `s` equals `c`, then `s.sum = c * s.length`. -/
theorem sum_of_constant (c : Nat) (s : List Nat)
    (h : ∀ v ∈ s, v = c) : s.sum = c * s.length := by
  induction s with
  | nil => simp
  | cons hd tl ih =>
    have hhd : hd = c := h hd (List.mem_cons.mpr (Or.inl rfl))
    have htl : ∀ v ∈ tl, v = c := fun v hv =>
      h v (List.mem_cons.mpr (Or.inr hv))
    simp only [List.sum_cons, List.length_cons, ih htl, hhd]
    -- Goal: c + c * tl.length = c * (tl.length + 1)
    -- Expand RHS: c * tl.length + c.
    rw [Nat.mul_add, Nat.mul_one, Nat.add_comm]

theorem outliers_constant (m c : Nat) (s : List Nat)
    (hm : 1 ≤ m) (hc : ∀ v ∈ s, v = c) :
    outliers m s = [] := by
  -- Strategy: show every element of `s` is non-outlier, then
  -- conclude the filter is empty. We work with the raw boolean
  -- predicate `isOutlier v m s = false` to avoid wrestling with
  -- the `Bool`/`Prop` coercion in `List.filter_eq_nil_iff`.
  have key : ∀ v ∈ s, isOutlier v m s = false := by
    intro v hv
    have hvc : v = c := hc v hv
    have hsum : s.sum = c * s.length := sum_of_constant c s hc
    unfold isOutlier
    rw [hvc, hsum]
    -- Goal: (decide (c * s.length > m * (c * s.length))) = false
    have hle : c * s.length ≤ m * (c * s.length) :=
      Nat.le_mul_of_pos_left (c * s.length) hm
    have hnot : ¬ (c * s.length > m * (c * s.length)) := by omega
    exact decide_eq_false hnot
  unfold outliers
  exact List.filter_eq_nil_iff.mpr (fun v hv hp => by
    rw [key v hv] at hp
    exact Bool.noConfusion hp)

-- ── Theorem 5: monotone in multiplier ──────────────────────────────

theorem outliers_monotone_threshold {m₁ m₂ : Nat} (h : m₁ ≤ m₂)
    (s : List Nat) :
    ∀ v ∈ outliers m₂ s, v ∈ outliers m₁ s := by
  intro v hv
  unfold outliers at hv ⊢
  rw [List.mem_filter] at hv ⊢
  refine ⟨hv.1, ?_⟩
  unfold isOutlier at hv ⊢
  simp only [decide_eq_true_eq] at hv ⊢
  have hmul : m₁ * s.sum ≤ m₂ * s.sum :=
    Nat.mul_le_mul_right s.sum h
  omega

end Lazarus.Outliers
