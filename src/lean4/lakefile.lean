-- lakefile.lean — hermetic Lean4 build for the Lazarus formal track.
--
-- Mirrors the Triadic-Coordination-Engine pattern: no external
-- dependencies on the default build path. `lake build` runs
-- against `Init`/`Std` only, exits non-zero on any proof failure,
-- and completes in under a second after the first compile.
--
-- The first (and currently only) target is `Outliers.lean`, the
-- Lean-proved abstract version of the outlier-detection algorithm
-- whose Python implementation lives at
-- `face_sentinel._outliers_from_scores` (LZ-014). The Lean proof
-- targets a layered companion claim — see LAZARUS_SPEC.md LZ-016.

import Lake
open Lake DSL

package «lazarus-lean» where
  leanOptions := #[
    ⟨`pp.unicode.fun, true⟩,
    ⟨`autoImplicit, false⟩,
    ⟨`relaxedAutoImplicit, false⟩
  ]

@[default_target]
lean_lib «Outliers» where
  srcDir := "."

@[default_target]
lean_lib «Liveness» where
  srcDir := "."

@[default_target]
lean_lib «Classify» where
  srcDir := "."

-- LZ-026 composition theorem — promotes the directional 3-cycle
-- (LZ-016 ∧ LZ-017 ∧ LZ-018) from :argued to :proved by
-- formalising the cross-module composition at the Lean level.
-- Depends on Outliers + Liveness + Classify.
@[default_target]
lean_lib «Composed» where
  srcDir := "."

-- LZ-024 face-reference Lean-scaffold joint closure
-- (LZ-006 ∧ LZ-014 ∧ LZ-016) — promotes :argued → :proved by
-- formalising that the LZ-016 abstract outlier filter preserves
-- both the LZ-016 subset property and the LZ-006 bounded-pool
-- size invariant when applied to LZ-014's pruning workflow.
-- Depends on Outliers.
@[default_target]
lean_lib «FaceReferencePool» where
  srcDir := "."

-- LZ-025 liveness Lean-scaffold joint closure
-- (LZ-007 ∧ LZ-013 ∧ LZ-017) — promotes :argued → :proved by
-- formalising that the LZ-017 metric's static-photo defense
-- (forward + converse + full equivalence) correctly determines
-- the LZ-007 watch-loop's mode-flip branch under LZ-013's
-- threshold semantics. Depends on Liveness.
@[default_target]
lean_lib «LivenessJoint» where
  srcDir := "."
