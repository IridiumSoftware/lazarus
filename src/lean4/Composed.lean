-- Composed.lean — LZ-026 composition theorem for the Lean-proved
-- trio (LZ-016 Outliers + LZ-017 Liveness + LZ-018 Classify).
--
-- The TCE Discovery.Triadic pass on the Lazarus 19-entry spec
-- corpus (triadic-coordination-engine commit 3fcccf3) surfaced
-- LZ-026 as the only directional 3-cycle across all three Triad-
-- deployment TCE passes: LZ-016 mentions LZ-018 → LZ-018 mentions
-- LZ-017 → LZ-017 mentions LZ-016 closes the cycle in the spec
-- mention graph. Each Lean-proved entry textually references
-- another as a proof obligation, but the existing per-module
-- theorems do not formally compose at the Lean level.
--
-- This file lifts that informal compositional structure to a
-- formal cross-module theorem. The pipeline below is a minimal
-- end-to-end use of all three modules in a single function. The
-- composition theorem `composed_correctness` proves that on a
-- self-match (candidate is byte-identical to at least one
-- reference), with a system predicate that fires, the pipeline
-- returns `Class.system` — a single forward statement that can
-- only be discharged by chaining Liveness + Outliers + Classify
-- lemmas together.
--
-- Promotes LZ-026 from `:argued` to `:proved`.

import Outliers
import Liveness
import Classify

namespace Lazarus.Composed

open Lazarus.Outliers
open Lazarus.Liveness
open Lazarus.Classify

-- ── Pipeline definition ──────────────────────────────────────────
--
-- The three steps:
--   1. Liveness.deltaCount  — compute distance from candidate to
--                             each reference.
--   2. Outliers.outliers     — identify anomalous distances at
--                             threshold m (used for the aiWatch
--                             escape hatch below).
--   3. Classify.classify     — priority dispatcher on the
--                             classification key.
--
-- Decision rule:
--   • If the candidate matches at least one reference exactly
--     (deltaCount = 0 against some reference) AND that match is
--     not flagged as an outlier, run classify on the key.
--   • Otherwise, treat as suspicious and return aiWatch.
--
-- The decision rule is illustrative; the load-bearing structural
-- content of this file is the cross-module proof below.

def pipeline {α : Type}
    (candidate : List Nat)
    (references : List (List Nat))
    (outlierThreshold : Nat)
    (key : α)
    (isSystem isKnown isAI : α → Bool) : Class :=
  -- Inline to avoid let-bindings the proof has to unfold past.
  if (references.map (deltaCount candidate)).contains 0
      && !(outliers outlierThreshold
              (references.map (deltaCount candidate))).contains 0 then
    classify isSystem isKnown isAI key
  else
    Class.aiWatch

-- ── Lemma 1: zero is never an outlier ────────────────────────────
--
-- For any threshold `m` and any list `s`, the value `0` is NOT
-- flagged as an outlier by Outliers.isOutlier. Reason: the
-- outlier predicate is `v * s.length > m * s.sum`, and at
-- `v = 0` the LHS is always 0, so `0 > m * s.sum` is false for
-- any natural `m, s`.
--
-- This is the bridge lemma: a Liveness-produced zero-distance
-- never gets caught by the Outliers filter. Lives in this
-- composition module because neither Outliers.lean nor
-- Liveness.lean reaches across the module boundary in
-- isolation — the composition is what surfaces this property.

theorem zero_not_outlier (m : Nat) (s : List Nat) :
    isOutlier 0 m s = false := by
  unfold isOutlier
  simp

-- ── Lemma 2: zero is filtered out of `outliers` ─────────────────
--
-- The outliers list never contains 0. Direct consequence of
-- Lemma 1 plus the definition of `outliers` as a filter:
-- `List.mem_filter` says an element is in `s.filter p` iff it's
-- in `s` and `p` is true on it; for value 0, `isOutlier 0 m s`
-- is `false` by Lemma 1, so 0 is excluded.

theorem zero_notin_outliers (m : Nat) (s : List Nat) :
    ¬ (0 ∈ outliers m s) := by
  unfold outliers
  intro h
  rw [List.mem_filter] at h
  obtain ⟨_, hOut⟩ := h
  rw [zero_not_outlier] at hOut
  exact Bool.noConfusion hOut

-- ── Lemma 3: candidate-in-references → 0 ∈ distance map ─────────
--
-- If the candidate is byte-identical to at least one reference,
-- then its deltaCount against that reference is 0 (by
-- Liveness.deltaCount_self), so the distance map contains a 0.

theorem self_match_yields_zero_distance
    (candidate : List Nat) (references : List (List Nat))
    (h : candidate ∈ references) :
    0 ∈ references.map (deltaCount candidate) := by
  rw [List.mem_map]
  exact ⟨candidate, h, deltaCount_self candidate⟩

-- ── Theorem composed_correctness — the LZ-026 composition ───────
--
-- The full cross-module property. When:
--   • the candidate is byte-identical to at least one reference
--     (Liveness: self-distance = 0),
--   • the system predicate fires on the classification key
--     (Classify: priority gives Class.system),
-- the pipeline returns `Class.system`. The proof chains:
--   1. Liveness.deltaCount_self  (via self_match_yields_zero_distance)
--   2. The zero-not-outlier bridge (zero_notin_outliers)
--   3. Classify.classify_system_priority
-- into a single end-to-end statement.
--
-- This is the formal compositional content the LZ-026 directional
-- 3-cycle was pointing at in the spec mention graph.

theorem composed_correctness {α : Type}
    (candidate : List Nat) (references : List (List Nat))
    (outlierThreshold : Nat)
    (key : α) (isSystem isKnown isAI : α → Bool)
    (hRef    : candidate ∈ references)
    (hSystem : isSystem key = true) :
    pipeline candidate references outlierThreshold
              key isSystem isKnown isAI = Class.system := by
  -- Unfold the pipeline definition.
  unfold pipeline
  -- The `zeroPresent` branch: by Liveness, 0 is in the distance
  -- map because the candidate matches at least one reference.
  have hZeroIn : 0 ∈ references.map (deltaCount candidate) :=
    self_match_yields_zero_distance candidate references hRef
  -- Bool-form of the same fact for the `contains` check.
  have hPresent :
      (references.map (deltaCount candidate)).contains 0 = true := by
    rw [List.contains_iff_exists_mem_beq]
    refine ⟨0, hZeroIn, ?_⟩
    rfl
  -- The `zeroOutlier` branch is false: 0 is not in `outliers _ _`.
  -- Use the membership characterization of `contains` (it's
  -- decidable equality search) plus zero_notin_outliers.
  have hNotOut :
      (outliers outlierThreshold
        (references.map (deltaCount candidate))).contains 0 = false := by
    rw [Bool.eq_false_iff]
    intro hC
    rw [List.contains_iff_exists_mem_beq] at hC
    obtain ⟨x, hxMem, hxEq⟩ := hC
    -- hxEq : (0 == x) = true; since both sides are Nat, x = 0.
    have hx0 : x = 0 := by
      cases x with
      | zero => rfl
      | succ n => simp at hxEq
    rw [hx0] at hxMem
    exact zero_notin_outliers outlierThreshold
            (references.map (deltaCount candidate)) hxMem
  -- Reduce the `if` using both facts.
  rw [hPresent, hNotOut]
  simp
  -- All that remains is `classify ... = Class.system` under
  -- `isSystem key = true`, which is exactly classify_system_priority.
  exact classify_system_priority isSystem isKnown isAI key hSystem

end Lazarus.Composed
