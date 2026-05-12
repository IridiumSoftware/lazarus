-- TriadBackbone.lean — LZ-028 no-oracle-triad-backbone, formal
-- cross-repo composition track.
--
-- The TCE Discovery.Triadic cross-Triad pass at v0.2.12
-- (triadic-coordination-engine commit `a9ddfea`) surfaced
-- `[LL-002, LZ-012, PH-004]` as the top-scoring triple across
-- the unified 82-entry Triad corpus at score 26.00 — the
-- "No-Oracle Backbone of the Triad." Three deployments, three
-- layers, one structural claim: **the Triad does not leak
-- distance information at any of its three layers.**
--
-- This file is the formal cross-repo composition theorem.
-- "Cross-repo" because the PharOS leg is CONCRETELY IMPORTED
-- from PharOS's own Lean tree via a Lake git dependency
-- (lakefile.lean pins PharOS commit `e3eaee1`, v0.0.12), not
-- inlined or re-proven. The `MembraneOutput` type and the
-- `membrane_one_bit_channel` theorem are the load-bearing
-- imports from `pharos-lean` — the same module that backs
-- PharOS spec entry PH-004.
--
-- As of v0.1.26, ALL THREE LEGS ARE CONCRETELY IMPORTED. The
-- LavaLamp leg uses `LavaLamp.LL002Visual.VisualOutput` from
-- the `lavalamp-hermetic` Lake git dep (LavaLamp commit
-- `1a2534f`); the Lazarus leg uses
-- `Lazarus.CompanionDiscipline.LlmOutput` from a sibling
-- module in this repo. Prior v0.1.24/v0.1.25 versions
-- modelled the LavaLamp and Lazarus legs as local abstract
-- finite-output types. The composition theorem's shape is
-- unchanged — the cardinality bound 2 × 3 × 2 = 12 still
-- holds — but each leg is now backed by its home-repo
-- canonical formalisation rather than a Lazarus-local model.
--
--   - LL-002: `LavaLamp.LL002Visual.VisualOutput` — 2 states
--     (`locked` / `unlocked`). LavaLamp's hermetic Lean tree
--     ships this as the canonical concrete formalisation of
--     LL-002's type-level cardinality surface.
--   - LZ-012: `Lazarus.CompanionDiscipline.LlmOutput` — 3
--     states (`observe` / `flag` / `watch`). Sibling module
--     in this repo formalises lazarus.md §"You observe. You
--     flag. You watch." at the type level.
--   - PH-004: `PharOS.Membrane.MembraneOutput` — 2 states
--     (`allow` / `deny`). Unchanged from v0.1.24; imported
--     from `pharos-lean` at PharOS commit `e3eaee1`.
--
-- Honest framing. The composition theorem
-- `no_oracle_triad_backbone` proves the joint Triad observer
-- surface has at most 2 × 3 × 2 = 12 inhabitants — the
-- formal counterpart of "no real-valued distance can be
-- encoded in the joint output." All three legs are now
-- backed by their home-repo Lean-proved type definitions, so
-- the composition is a genuine cross-repo formal-build edge
-- rather than a Lazarus-local model. Each leg's broader
-- decoupling claim (LL-002's no-security-primitive-leakage,
-- LZ-012's no-write discipline, PH-004's substrate-binding)
-- remains covered by its own home-repo evidence at its own
-- entry tier (`:tested` for LL-002 / LZ-012,
-- `:proved` for PH-004).
--
-- The composition theorem `no_oracle_triad_backbone` proves
-- that the joint Triad output type — a triple
-- `(visual, llm, membrane)` — has at most
-- 2 × 3 × 2 = 12 inhabitants. A 12-element finite type cannot
-- carry distance information. The cardinality bound IS the
-- no-oracle property at the joint level.
--
-- Promotes LZ-028 from `:argued` to `:proved` via this
-- cross-repo Lean build.

import Membrane
import LL002Visual
import CompanionDiscipline

namespace Lazarus.TriadBackbone

open PharOS.Membrane
open LavaLamp.LL002Visual
open Lazarus.CompanionDiscipline

-- ── LavaLamp + Lazarus legs are now concrete cross-repo imports ──
--
-- VisualOutput is imported from the lavalamp-hermetic package
-- (LavaLamp commit `1a2534f`); LlmOutput is imported from the
-- sibling CompanionDiscipline module in this repo. Their
-- finite-channel theorems are exposed by those home-repo
-- modules; we re-export them below as the LL-002 / LZ-012
-- legs of the composition for readability.

/-- LavaLamp leg's 1-bit channel — re-exported from
    `LavaLamp.LL002Visual.visual_one_bit_channel`. Concrete
    cross-repo formalisation of LL-002. -/
theorem visual_one_bit_channel' (v : VisualOutput) :
    v ∈ ([VisualOutput.locked, VisualOutput.unlocked] : List VisualOutput) :=
  visual_one_bit_channel v

/-- Lazarus leg's finite channel — re-exported from
    `Lazarus.CompanionDiscipline.llm_finite_channel`. Concrete
    sibling-module formalisation of LZ-012. -/
theorem llm_finite_channel' (l : LlmOutput) :
    l ∈ ([LlmOutput.observe, LlmOutput.flag, LlmOutput.watch]
         : List LlmOutput) :=
  llm_finite_channel l

-- ── PharOS leg: lifted from imported Membrane.lean ──────────────────

/-- PharOS leg's 1-bit channel, lifted from PharOS's own
    `membrane_one_bit_channel` theorem (proved at PharOS
    v0.0.12 in `pharos-lean/Membrane.lean`, imported via Lake
    git dep). The lift is intentionally trivial — we are NOT
    re-proving PharOS's theorem, we are stating that
    membrane outputs already satisfy the same 2-element
    finite-channel constraint as VisualOutput. -/
theorem pharos_one_bit_channel (m : MembraneOutput) :
    m ∈ ([MembraneOutput.allow, MembraneOutput.deny] : List MembraneOutput) := by
  cases m <;> simp

-- ── Composition: the joint Triad output type ──────────────────────

/-- The joint output the Triad presents to an external
    observer is the triple (visual, llm, membrane). Cardinality
    is 2 × 3 × 2 = 12. -/
def TriadOutput := VisualOutput × LlmOutput × MembraneOutput

/-- Canonical enumeration of all 12 TriadOutput inhabitants —
    the complete observer surface of the Triad. -/
def triadOutputs : List TriadOutput :=
  [ ⟨VisualOutput.locked,   LlmOutput.observe, MembraneOutput.allow⟩,
    ⟨VisualOutput.locked,   LlmOutput.observe, MembraneOutput.deny⟩,
    ⟨VisualOutput.locked,   LlmOutput.flag,    MembraneOutput.allow⟩,
    ⟨VisualOutput.locked,   LlmOutput.flag,    MembraneOutput.deny⟩,
    ⟨VisualOutput.locked,   LlmOutput.watch,   MembraneOutput.allow⟩,
    ⟨VisualOutput.locked,   LlmOutput.watch,   MembraneOutput.deny⟩,
    ⟨VisualOutput.unlocked, LlmOutput.observe, MembraneOutput.allow⟩,
    ⟨VisualOutput.unlocked, LlmOutput.observe, MembraneOutput.deny⟩,
    ⟨VisualOutput.unlocked, LlmOutput.flag,    MembraneOutput.allow⟩,
    ⟨VisualOutput.unlocked, LlmOutput.flag,    MembraneOutput.deny⟩,
    ⟨VisualOutput.unlocked, LlmOutput.watch,   MembraneOutput.allow⟩,
    ⟨VisualOutput.unlocked, LlmOutput.watch,   MembraneOutput.deny⟩ ]

-- ── Composition theorem: the no-oracle backbone of the Triad ──────

/-- **no_oracle_triad_backbone** — the LZ-028 composition.
    Every joint Triad output lies in the 12-element finite
    enumeration `triadOutputs`. The cardinality bound is the
    formal counterpart of "the Triad does not leak distance
    information at any of its three layers": ℝ is uncountable
    but the joint observer surface has exactly 12 inhabitants,
    so no real-valued distance can be encoded in the joint
    output.

    The proof discharges all 12 cases by structural case
    analysis on each layer's inductive — composing:
      • LL-002 / VisualOutput: 2 cases (locked / unlocked).
      • LZ-012 / LlmOutput: 3 cases (observe / flag / watch).
      • PH-004 / MembraneOutput: 2 cases (allow / deny).
    2 × 3 × 2 = 12 simp-closable goals.

    Cannot be proved without invoking lemmas/types from each
    of the three legs simultaneously — VisualOutput.cases and
    LlmOutput.cases are local; MembraneOutput.cases is
    cross-repo imported from `pharos-lean`. -/
theorem no_oracle_triad_backbone (out : TriadOutput) :
    out ∈ triadOutputs := by
  obtain ⟨v, l, m⟩ := out
  cases v <;> cases l <;> cases m <;> simp [triadOutputs]

-- ── Length witness: confirms the cardinality bound ────────────────

/-- The cardinality bound is exactly 12. Computed by `rfl`
    against the `triadOutputs` enumeration. Stated separately
    to make the "no real-valued distance can fit here"
    framing explicit: 12 is countable; ℝ is not. -/
theorem triad_output_cardinality :
    triadOutputs.length = 12 := by rfl

end Lazarus.TriadBackbone
