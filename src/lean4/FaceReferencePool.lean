-- FaceReferencePool.lean — LZ-024 face-reference Lean-scaffold
-- joint closure: LZ-006 ∧ LZ-014 ∧ LZ-016.
--
-- The TCE Discovery.Triadic pass surfaced LZ-024 as a STRICT
-- HIGH-band triple at score 9.50, status-diversity 2
-- (tested + tested + proved): a proof-scaffold-meets-implementation
-- cluster on the face-reference axis. Three components:
--
--   LZ-006 (reference-storage-bounded) — Python `prune_oldest()`
--          caps the pool at MAX_REFERENCES = 50. Bounded-pool
--          invariant.
--   LZ-014 (reference-pool leave-one-out pruning) — Python
--          `_outliers_from_scores` + `_prune_score_one` filters
--          outliers from leave-one-out per-ref scores.
--   LZ-016 (outlier-detection abstract algorithm) — Lean-proved
--          structural counterpart in Outliers.lean (totality,
--          bounded cost, outlier-monotonicity).
--
-- This file lifts the informal compositional structure to a
-- formal cross-module theorem. The joint claim — surfaced
-- structurally by the TCE pass but not formally composed at
-- the Lean level — is: pruning a bounded reference pool with
-- the abstract outlier filter yields a result that
--
--   (i)  is a subset of the original pool (LZ-016's
--        outliers_subset preserves the input membership)
--   (ii) retains the bounded-pool size invariant (LZ-006's
--        cap on |pool| ≤ N composes through the filter).
--
-- Both properties need to hold for the joint claim to hold —
-- losing (i) would mean the filter could fabricate scores not
-- present in the original pool; losing (ii) would mean the
-- filter could grow the pool past LZ-006's bound. The two
-- together formalise the cross-module composition.
--
-- Promotes LZ-024 from `:argued` to `:proved`.

import Outliers

namespace Lazarus.FaceReferencePool

open Lazarus.Outliers

-- ── Lemma 1: filter preserves any upper bound on length ──────────
--
-- A boolean filter on a list never grows the list. If the input
-- length is bounded by N, the output length is bounded by the
-- same N. This is the bounded-pool invariant (LZ-006) composing
-- through the LZ-014 / LZ-016 filter operation.

theorem filter_length_le_bound {α : Type}
    (p : α → Bool) (s : List α) (N : Nat)
    (hBound : s.length ≤ N) :
    (s.filter p).length ≤ N := by
  have hSub : (s.filter p).length ≤ s.length :=
    List.length_filter_le p s
  omega

-- ── Lemma 2: outliers preserves the bounded-pool invariant ──────
--
-- Direct corollary applied to `Outliers.outliers`, which is
-- defined as `s.filter (fun v => isOutlier v m s)`. The
-- bounded-pool size flows through the filter unchanged.

theorem outliers_preserves_bound (m N : Nat) (s : List Nat)
    (hBound : s.length ≤ N) :
    (outliers m s).length ≤ N := by
  unfold outliers
  exact filter_length_le_bound _ s N hBound

-- ── Theorem face_reference_correctness — the LZ-024 composition ──
--
-- The full joint claim. When the reference pool `s` is bounded
-- by `N` (LZ-006 invariant — in production N = MAX_REFERENCES =
-- 50), applying the abstract outlier filter at multiplier `m`
-- (LZ-014's pruning operation, modelled by LZ-016's `outliers`)
-- yields a result that:
--
--   • each element is in the original pool (LZ-016's
--     `outliers_subset` discharges this side);
--   • the size is still bounded by N (LZ-006 + the filter-
--     non-growth lemma above discharge this side).
--
-- Both conjuncts together formalise the joint claim that the
-- LZ-014 pruning algorithm respects both abstract correctness
-- (LZ-016) and the bounded-pool invariant (LZ-006). The cross-
-- module composition is what the TCE pass surfaced and what
-- the LZ-024 spec entry textually argued; this theorem makes
-- it a compiling proof artifact.

theorem face_reference_correctness (m N : Nat) (s : List Nat)
    (hBound : s.length ≤ N) :
    (∀ v ∈ outliers m s, v ∈ s)
    ∧ (outliers m s).length ≤ N := by
  refine ⟨?_, ?_⟩
  · -- Side (i): membership preservation — LZ-016.
    exact outliers_subset m s
  · -- Side (ii): size bound preservation — LZ-006 + filter
    -- non-growth.
    exact outliers_preserves_bound m N s hBound

end Lazarus.FaceReferencePool
