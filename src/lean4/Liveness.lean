-- Liveness.lean — hermetic Lean4 proof of the byte-diff metric
-- underlying `face_sentinel._liveness_delta` (LZ-013, :tested via
-- `test/test_liveness_check.py`).
--
-- LZ-017 spec entry: the abstract metric proved as a structural
-- skeleton. The Python helper `_liveness_delta(bytes_a, bytes_b)`
-- returns the fraction of byte positions where the two equal-
-- length sequences differ (a discrete Hamming-style metric over
-- the 64×48 BMP downsamples produced by `sips`). This file
-- proves the four canonical metric properties on the abstract
-- algorithm: self-distance is zero, symmetry, bounded by length,
-- and zero iff equal.
--
-- Model. Byte sequences as `List Nat` (each byte 0..255 fits in
-- Nat; in practice the Python implementation reads `bytes` which
-- decompose into Nat). The metric is unnormalized — the
-- numerator (`deltaCount`) is the absolute diff count over the
-- shared positions. The normalization step (`diffs / len`) and
-- the threshold check (`live = delta ≥ LIVENESS_DELTA_MIN`) live
-- one layer up; the metric properties themselves don't depend on
-- the normalization.
--
-- Equal-length precondition. The Python implementation returns
-- `None` on length mismatch and `None` on empty input; the
-- caller treats both as "fail open." The Lean theorems below
-- carry an explicit `a.length = b.length` hypothesis where it
-- matters; the function is total in Lean (defined as 0 on
-- length-mismatch cases) but the math only applies to the
-- equal-length subset.
--
-- Theorems proved (hermetic — Lean core only, no Mathlib):
--   - deltaCount_self:           delta(a, a) = 0
--   - deltaCount_symm:           delta(a, b) = delta(b, a)
--   - deltaCount_le_length:      delta(a, b) ≤ a.length
--   - deltaCount_zero_iff_eq:    (delta(a, b) = 0) ↔ (a = b),
--                                under the same-length hypothesis

namespace Lazarus.Liveness

/-- Byte-diff count: for two equal-length lists `a` and `b`,
    the number of positions where `a[i] ≠ b[i]`. Returns 0 on
    length-mismatch cases (those are out of mathematical scope
    — the Python implementation returns `None` and the caller
    fails open). -/
def deltaCount : List Nat → List Nat → Nat
  | [], [] => 0
  | x :: xs, y :: ys =>
    (if x = y then 0 else 1) + deltaCount xs ys
  | _, _ => 0

-- ── Theorem 1: self-distance is zero ───────────────────────────────

theorem deltaCount_self (a : List Nat) : deltaCount a a = 0 := by
  induction a with
  | nil => rfl
  | cons hd tl ih =>
    unfold deltaCount
    simp [ih]

-- ── Theorem 2: symmetry (under equal-length precondition) ─────────

theorem deltaCount_symm (a b : List Nat)
    (hlen : a.length = b.length) :
    deltaCount a b = deltaCount b a := by
  induction a generalizing b with
  | nil =>
    -- a = [], so b = [] by hlen
    cases b with
    | nil => rfl
    | cons _ _ => simp at hlen
  | cons hd tl ih =>
    cases b with
    | nil => simp at hlen
    | cons hd' tl' =>
      unfold deltaCount
      have htl : tl.length = tl'.length := by
        simp [List.length_cons] at hlen; omega
      rw [ih tl' htl]
      -- Goal: (if hd = hd' then 0 else 1) + deltaCount tl' tl
      --     = (if hd' = hd then 0 else 1) + deltaCount tl' tl
      -- The `if` expressions are symmetric via Eq.comm.
      congr 1
      by_cases h : hd = hd'
      · -- if branches both evaluate to 0 — rw closes via rfl
        rw [h]
      · -- if branches both evaluate to 1
        have h' : hd' ≠ hd := fun heq => h heq.symm
        rw [if_neg h, if_neg h']

-- ── Theorem 3: bounded by length ───────────────────────────────────

theorem deltaCount_le_length (a b : List Nat) :
    deltaCount a b ≤ a.length := by
  induction a generalizing b with
  | nil =>
    cases b with
    | nil => simp [deltaCount]
    | cons _ _ => simp [deltaCount]
  | cons hd tl ih =>
    cases b with
    | nil => simp [deltaCount]
    | cons hd' tl' =>
      -- Goal: deltaCount (hd :: tl) (hd' :: tl') ≤ (hd :: tl).length
      -- i.e., (if hd = hd' then 0 else 1) + deltaCount tl tl' ≤ tl.length + 1
      have htl := ih tl'
      by_cases h : hd = hd'
      · -- if-branch is 0
        show (if hd = hd' then 0 else 1) + deltaCount tl tl' ≤ tl.length + 1
        simp [h]
        omega
      · -- if-branch is 1
        show (if hd = hd' then 0 else 1) + deltaCount tl tl' ≤ tl.length + 1
        simp [h]
        omega

-- ── Theorem 4: zero ↔ equal (under equal-length precondition) ─────

theorem deltaCount_zero_iff_eq (a b : List Nat)
    (hlen : a.length = b.length) :
    deltaCount a b = 0 ↔ a = b := by
  induction a generalizing b with
  | nil =>
    cases b with
    | nil => simp [deltaCount]
    | cons _ _ => simp at hlen
  | cons hd tl ih =>
    cases b with
    | nil => simp at hlen
    | cons hd' tl' =>
      have htl : tl.length = tl'.length := by
        simp [List.length_cons] at hlen; omega
      constructor
      · intro hsum
        -- deltaCount (hd :: tl) (hd' :: tl') = 0
        -- =  (if hd = hd' then 0 else 1) + deltaCount tl tl' = 0
        -- ⟹ if branch is 0 AND deltaCount tl tl' = 0
        by_cases h : hd = hd'
        · -- Heads equal: if-branch is 0, so the recursive call is 0
          have htlc : deltaCount tl tl' = 0 := by
            simp [deltaCount, h] at hsum
            exact hsum
          have htl_eq : tl = tl' := (ih tl' htl).mp htlc
          rw [h, htl_eq]
        · -- Heads unequal: if-branch is 1, sum is ≥ 1 ≠ 0 — contradict
          exfalso
          simp [deltaCount, h] at hsum
      · intro heq
        -- a = b directly: rewrite and apply self-distance theorem
        rw [heq]
        exact deltaCount_self _

end Lazarus.Liveness
