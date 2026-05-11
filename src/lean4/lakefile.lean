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
