-- LivenessJoint.lean — LZ-025 liveness Lean-scaffold joint
-- closure: LZ-007 ∧ LZ-013 ∧ LZ-017.
--
-- The TCE Discovery.Triadic pass surfaced LZ-025 as a STRICT
-- HIGH-band triple at score 9.50, status-diversity 2: a
-- proof-scaffold-meets-implementation cluster on the liveness
-- axis (parallel shape to LZ-024 on the face-reference axis).
-- Three components:
--
--   LZ-007 (watch-loop state transitions) — Python state
--          machine in `face_sentinel.check_once`: capture →
--          match → liveness-probe → mode-flip. The liveness
--          branch consumes LZ-013's verdict.
--   LZ-013 (anti-spoof liveness probe) — Python
--          `_liveness_delta` + `liveness_check` + threshold
--          `LIVENESS_DELTA_MIN`. Two-capture byte-diff;
--          static-photo attacks produce delta = 0, real faces
--          produce delta > 0.
--   LZ-017 (liveness metric abstract properties) — Lean-proved
--          Hamming-style metric in Liveness.lean
--          (deltaCount_self, deltaCount_symm, deltaCount_zero_iff_eq,
--          deltaCount_le_length).
--
-- This file formalises two cross-module properties of the
-- composition. Both have the same shape: chain LZ-017's
-- metric theorems with LZ-013's threshold semantics so the
-- LZ-007 watch loop's routing decisions are justified at the
-- Lean level.
--
-- Promotes LZ-025 from `:argued` to `:proved`.

import Liveness

namespace Lazarus.LivenessJoint

open Lazarus.Liveness

-- ── Theorem liveness_static_photo_fails — the LZ-025 forward composition ──
--
-- The static-photo attack defense. Premise: an attacker holds
-- a printed photo (or a phone screen displaying a still image)
-- between consecutive frames. The two captures are byte-
-- identical at the BMP downsample (modelled here as
-- `capA = capB`). Conclusion: the LZ-017 metric returns 0,
-- which is strictly below any positive threshold (LZ-013's
-- `LIVENESS_DELTA_MIN > 0` in the imperative implementation —
-- modelled here as `1 ≤ threshold`).
--
-- The LZ-007 watch-loop consequence: on `delta < threshold`
-- the state machine takes the liveness-fail branch and flips
-- mode to "shakespeare." This theorem discharges the metric
-- side of that branch decision.
--
-- The proof chains:
--   LZ-017.deltaCount_self : ∀ a, deltaCount a a = 0
--   LZ-013 threshold positivity : 1 ≤ threshold
-- ⟹ 0 < threshold.

theorem liveness_static_photo_fails
    (capA capB : List Nat) (threshold : Nat)
    (hEq      : capA = capB)
    (hThresh  : 1 ≤ threshold) :
    deltaCount capA capB < threshold := by
  rw [hEq, deltaCount_self]
  exact hThresh

-- ── Theorem liveness_pass_implies_motion — the LZ-025 converse composition ──
--
-- The contrapositive direction. Premise: the liveness threshold
-- check passes — the metric returned at least 1 (i.e., at least
-- one byte position differs between the two captures). Conclusion:
-- the two captures are NOT byte-identical — some pixel-level
-- variation occurred between them.
--
-- LZ-007 watch-loop consequence: on `delta ≥ threshold` the
-- state machine credits the frame as live and routes through
-- the face-match step. This theorem rules out the static-photo
-- attacker that an LZ-013-style probe is designed to catch — if
-- the captures matched exactly, delta would be 0 and the
-- threshold check would fail (the forward theorem above).
--
-- Proof: assume the captures ARE equal and derive a contradiction
-- with the threshold-passing hypothesis (deltaCount_self gives
-- 0 ≥ 1, false by omega).

theorem liveness_pass_implies_motion
    (capA capB : List Nat)
    (hPass : 1 ≤ deltaCount capA capB) :
    capA ≠ capB := by
  intro hEq
  rw [hEq, deltaCount_self] at hPass
  omega

-- ── Theorem liveness_equivalence — full LZ-017-grounded characterisation ──
--
-- For two captures of equal length (the metric's well-defined
-- subset — LZ-017 carries the equal-length precondition where
-- it matters), the LZ-013 threshold-fails-iff-static-photo
-- equivalence holds. Drops out of LZ-017's
-- `deltaCount_zero_iff_eq` characterisation.
--
-- This is the cleanest statement of the LZ-025 joint claim:
-- the LZ-013 anti-spoof primitive's decision is fully
-- determined by capture equality, with no slack or
-- ambiguity at the metric level. Watch-loop state transitions
-- (LZ-007) routed on this decision are therefore correct
-- under the metric.

theorem liveness_equivalence
    (capA capB : List Nat)
    (hlen : capA.length = capB.length) :
    (deltaCount capA capB = 0) ↔ (capA = capB) :=
  deltaCount_zero_iff_eq capA capB hlen

end Lazarus.LivenessJoint
