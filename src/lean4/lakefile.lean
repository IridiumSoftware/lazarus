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

-- Cross-repo dependency on PharOS's hermetic Lean tree.
-- Required by TriadBackbone (LZ-028 cross-Triad no-oracle
-- backbone), which imports PharOS.Membrane to bring the
-- already-proved PH-004 LL-017-membrane-preservation theorem
-- into the joint composition. PharOS's lakefile lives at
-- `src/lean4/` in the PharOS repo and ships its own hermetic
-- (no-Mathlib) Lean tree, so this dep adds no transitive
-- Mathlib load.
require «pharos-lean» from git
  "https://github.com/IridiumSoftware/pharos.git" @ "e3eaee1" / "src/lean4"

-- Cross-repo dependency on LavaLamp's hermetic Lean tree.
-- The main LavaLamp Lean tree at `src/lean4/` carries Mathlib
-- (LL-006 / LL-019 / LL-020 / LL-021 round-3 theorems); the
-- hermetic sibling at `src/lean4-hermetic/` is a separate Lake
-- package with no Mathlib dep. TriadBackbone imports
-- `LavaLamp.LL002Visual` from this hermetic sibling — the
-- LL-002 visual-security-decoupling type-level surface —
-- without dragging Mathlib into Lazarus's build.
require «lavalamp-hermetic» from git
  "https://github.com/IridiumSoftware/lavalamp.git" @ "1a2534f" / "src/lean4-hermetic"

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

-- LZ-012 companion-read-only-discipline — concrete Lean
-- formalisation of the type-level finite-output surface (the
-- `observe / flag / watch` enum from `lazarus.md`). Layered
-- companion to LZ-012's existing :tested static-lint evidence.
-- Imported by TriadBackbone (LZ-028) as the Lazarus leg of
-- the cross-Triad No-Oracle Backbone composition.
@[default_target]
lean_lib «CompanionDiscipline» where
  srcDir := "."

-- LZ-028 no-oracle-triad-backbone — cross-repo composition.
-- TCE cross-Triad pass surfaced [LL-002, LZ-012, PH-004] as
-- the top-scoring triple across the unified 82-entry Triad
-- corpus at score 26.00. Promotes LZ-028 :argued → :proved by
-- importing PharOS's already-proved membrane Lean theorem AND
-- modelling LavaLamp's LL-002 + Lazarus's LZ-012 legs as
-- abstract finite-output types in this file, then composing
-- the three legs into a 12-element finite Triad output.
-- Depends on Membrane (via pharos-lean git dep above).
@[default_target]
lean_lib «TriadBackbone» where
  srcDir := "."

-- LZ-001 visual-skin / security-primitive decoupling —
-- concrete Lean formalisation of the producer-side mode
-- vocabulary (the `normal / shakespeare` enum face_sentinel.py
-- writes to ~/.face_sentinel/state.json.mode). Layered
-- companion to LZ-001's existing :tested static-text-search
-- evidence in test/test_visual_skin_decoupling.py.
-- Imported by DecouplingBackbone (LZ-031) as the Lazarus leg
-- of the cross-Triad Decoupling axis composition.
@[default_target]
lean_lib «VisualSkinDecoupling» where
  srcDir := "."

-- LZ-031 / LL-050 / PH-018 decoupling-triad-backbone —
-- cross-repo composition. TCE cross-Triad pass surfaced
-- [LL-002, LZ-001, PH-004] at score 23.00 — the Decoupling
-- axis. Promotes the three mirror entries from :argued to
-- :proved by composing concrete imports from all three home
-- repos (no abstract modelling):
--   - LavaLamp.LL002Visual (via existing lavalamp-hermetic dep)
--   - Lazarus.VisualSkinDecoupling (sibling module above)
--   - PharOS.Membrane (via existing pharos-lean dep)
-- The composition is structurally distinct from
-- TriadBackbone (LZ-028) despite reusing LL-002 + PH-004 —
-- the distinguishing leg shifts from LZ-012 (companion-read-
-- only) to LZ-001 (visual-skin decoupling). Joint cardinality
-- 2 × 2 × 2 = 8 (vs TriadBackbone's 2 × 3 × 2 = 12).
-- No new Lake git deps required. No Mathlib pull.
@[default_target]
lean_lib «DecouplingBackbone» where
  srcDir := "."
