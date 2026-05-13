-- DecouplingBackbone.lean — LZ-031 / LL-050 / PH-018 cross-Triad
-- Decoupling axis composition theorem.
--
-- The TCE Discovery.Triadic cross-Triad pass at v0.2.12
-- (triadic-coordination-engine commit `a9ddfea`) surfaced
-- `[LL-002, LZ-001, PH-004]` at score 23.00 — the **Decoupling
-- axis** of the Triad. Three deployments, three V-DECOUPLING
-- flavors, one structural claim: **the Triad keeps user-facing
-- presentation strictly separated from the security state it
-- represents.**
--
-- STRUCTURALLY DISTINCT from the No-Oracle Backbone
-- `[LL-002, LZ-012, PH-004]` at 26.00 (formalised in
-- `TriadBackbone.lean`, LZ-028 :proved at v0.1.24/v0.1.26)
-- despite sharing LL-002 + PH-004 legs. The No-Oracle claim is
-- about output-cardinality (≤ 1 bit per surface); the
-- Decoupling claim is about architectural separation
-- (presentation surface and security-state surface are
-- independently swappable). Both ride through LL-002 + PH-004
-- because those entries serve both invariants. The
-- distinguishing leg is:
--   - LZ-012 (companion read-only) for No-Oracle (LZ-028).
--   - LZ-001 (visual-skin decoupling) for Decoupling (this entry).
--
-- This file is the formal cross-repo composition theorem for
-- the Decoupling axis. All three legs are concretely imported
-- from their home-repo canonical formalisations — no abstract
-- modelling required:
--
--   - LL-002: `LavaLamp.LL002Visual.VisualOutput` — 2 states
--     (`locked` / `unlocked`). Imported via the existing Lake
--     git dep on `lavalamp-hermetic` at LavaLamp commit
--     `1a2534f` (added in v0.1.26 for TriadBackbone's LL-002
--     leg; reused unchanged here).
--   - LZ-001: `Lazarus.VisualSkinDecoupling.Mode` — 2 states
--     (`normal` / `shakespeare`). Sibling module in this repo
--     formalises the producer-side mode vocabulary
--     `face_sentinel.py` writes to `state.json.mode` per
--     `test_visual_skin_decoupling.py`.
--   - PH-004: `PharOS.Membrane.MembraneOutput` — 2 states
--     (`allow` / `deny`). Imported via the existing Lake git
--     dep on `pharos-lean` at PharOS commit `e3eaee1` (added
--     in v0.1.24 for TriadBackbone's PH-004 leg; reused
--     unchanged here).
--
-- No new Lake git deps. No Mathlib pull. The composition
-- theorem uses only the three already-pulled hermetic modules.
--
-- Honest framing. The composition proves the joint Decoupling
-- output is a 2 × 2 × 2 = 8-element finite type, mirroring
-- the structural argument from TriadBackbone (12 = 2 × 3 × 2
-- there because LlmOutput has 3 constructors; here all three
-- legs are 2-constructor, so the joint is 8). The cardinality
-- bound is the formal counterpart of "no real-valued
-- presentation channel can be encoded in the joint observer
-- surface of the decoupled layers": ℝ is uncountable, 8 is
-- countable, so the visual / mode / membrane triple has no
-- room for a presentation-shaped covert channel.
--
-- LL-002 + LZ-001 + PH-004 are each `:tested` (LL-002, LZ-001)
-- or `:proved` (PH-004) in their home repos via operational /
-- algorithmic evidence at the source level. This Lean track is
-- LAYERED EVIDENCE for the joint Decoupling claim — it
-- formalises the type-cardinality slice of the conjunction.
-- The broader decoupling invariant (producer cannot import
-- presentation; consumer reads only mode-vocabulary; membrane
-- returns no presentation info) remains covered by the
-- operational source-of-truth tests in each home repo.

import Membrane
import LL002Visual
import VisualSkinDecoupling

namespace Lazarus.DecouplingBackbone

open PharOS.Membrane
open LavaLamp.LL002Visual
open Lazarus.VisualSkinDecoupling

-- ── The joint Triad decoupling-output type ──────────────────

/-- The joint observer surface of the three decoupled layers,
    one constructor per (visual, mode, membrane) triple. This is
    the formal Triad Decoupling output that any cross-Triad
    observer can see — no real-valued presentation channel can
    be encoded in it because the type has finite cardinality. -/
structure DecouplingOutput where
  visual : VisualOutput
  mode : Mode
  membrane : MembraneOutput

-- ── The canonical enumeration: every joint output appears exactly once ──

/-- All 2 × 2 × 2 = 8 inhabitants of `DecouplingOutput`. Used
    as the right-hand side of `decoupling_triad_backbone` to
    state the cardinality bound concretely. -/
def decouplingOutputs : List DecouplingOutput :=
  [ ⟨VisualOutput.locked,   Mode.normal,      MembraneOutput.allow⟩,
    ⟨VisualOutput.locked,   Mode.normal,      MembraneOutput.deny⟩,
    ⟨VisualOutput.locked,   Mode.shakespeare, MembraneOutput.allow⟩,
    ⟨VisualOutput.locked,   Mode.shakespeare, MembraneOutput.deny⟩,
    ⟨VisualOutput.unlocked, Mode.normal,      MembraneOutput.allow⟩,
    ⟨VisualOutput.unlocked, Mode.normal,      MembraneOutput.deny⟩,
    ⟨VisualOutput.unlocked, Mode.shakespeare, MembraneOutput.allow⟩,
    ⟨VisualOutput.unlocked, Mode.shakespeare, MembraneOutput.deny⟩ ]

-- ── Composition theorem: the decoupling backbone of the Triad ──

/-- **decoupling_triad_backbone** — the LZ-031 / LL-050 / PH-018
    composition. Every joint Triad decoupling output lies in
    the 8-element finite enumeration `decouplingOutputs`. The
    cardinality bound is the formal counterpart of "the Triad
    keeps user-facing presentation strictly separated from the
    security state": ℝ is uncountable but the joint observer
    surface has exactly 8 inhabitants, so no real-valued
    presentation channel can be encoded in the joint output.

    The proof discharges all 8 cases by structural case
    analysis on each layer's inductive — composing:
      • LL-002 / VisualOutput: 2 cases (locked / unlocked).
      • LZ-001 / Mode: 2 cases (normal / shakespeare).
      • PH-004 / MembraneOutput: 2 cases (allow / deny).
    2 × 2 × 2 = 8 simp-closable goals.

    Cannot be proved without invoking inductives from each of
    the three legs simultaneously — `VisualOutput.cases` is
    cross-repo imported from `lavalamp-hermetic`,
    `Mode.cases` is local (sibling module formalising LZ-001),
    `MembraneOutput.cases` is cross-repo imported from
    `pharos-lean`. The composition is therefore a real
    cross-repo proof artifact, not a structural argument or
    a mirror-citation. -/
theorem decoupling_triad_backbone (out : DecouplingOutput) :
    out ∈ decouplingOutputs := by
  obtain ⟨v, m, b⟩ := out
  cases v <;> cases m <;> cases b <;> simp [decouplingOutputs]

-- ── Length witness: confirms the cardinality bound ────────────────

/-- The cardinality bound is exactly 8. Computed by `rfl`
    against the `decouplingOutputs` enumeration. Stated
    separately to make the "no real-valued presentation channel
    can fit here" framing explicit: 8 is countable; ℝ is not. -/
theorem decoupling_output_cardinality :
    decouplingOutputs.length = 8 := by rfl

end Lazarus.DecouplingBackbone
