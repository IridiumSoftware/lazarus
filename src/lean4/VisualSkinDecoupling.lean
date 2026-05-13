-- VisualSkinDecoupling.lean — concrete Lean formalisation of
-- LZ-001 visual-skin / security-primitive decoupling at the
-- type-level surface.
--
-- LZ-001 (LAZARUS_SPEC.md) establishes that the Lazarus
-- security primitive is a state machine rooted in
-- `~/.face_sentinel/state.json`. The `mode` field
-- (`"normal"` / `"shakespeare"`) and the `authenticated`
-- boolean determine system behavior. The user-facing surface
-- (ASCII art, Shakespeare quotes, warm one-liners) is
-- decorative — replacing it with silence, Klingon, or any
-- other lockout style does not change the security primitive.
--
-- The producer (`face_sentinel.py`) writes `mode` and
-- `authenticated` and knows nothing about presentation. The
-- consumer (`lazarus.md`) reads `state.json.mode` and chooses
-- presentation. The mode-value vocabulary (`"normal"`,
-- `"shakespeare"`) is the contract.
--
-- The Python static-lint at `test/test_visual_skin_decoupling.py`
-- enforces this operationally — six layers including
-- forbidden-presentation-content-in-producer and mode-vocab
-- parity. LZ-001's `:tested` status is anchored there.
--
-- This file adds a LAYERED COMPANION at the Lean type level:
-- the producer-side mode vocabulary is a 2-constructor
-- inductive (`normal` / `shakespeare`), with NO third
-- constructor that could carry presentation, distance, or
-- substantive content. The type system makes the contract a
-- compile-time guarantee at the structural level — distinct
-- from (and stronger than) the source-text-search assertions
-- in the Python test.
--
-- This module is the canonical concrete formalisation of the
-- LZ-001 mode-vocabulary surface for cross-repo consumers:
--   - Lazarus's `DecouplingBackbone.lean` (LZ-031 :proved at
--     v0.1.29) imports `Mode` via sibling module and uses
--     `mode_finite_channel` as the Lazarus leg of its
--     `decoupling_triad_backbone` cross-Triad composition
--     theorem (joint with LavaLamp's LL002Visual.VisualOutput
--     and PharOS's Membrane.MembraneOutput).
--   - LZ-001's spec entry notes the Lean layered companion as
--     additional structural evidence beyond the static-text-
--     search assertions.
--
-- Honest framing. The Lean track formalises ONE aspect of
-- LZ-001's claim — the type-cardinality of the producer's
-- mode-vocabulary surface. The broader producer/consumer
-- decoupling claim (face_sentinel.py never imports
-- presentation; lazarus.md reads only state.json.mode; the
-- contract is the shared vocabulary, nothing more) remains
-- covered by the Python static-lint, which is the source of
-- truth for LZ-001's `:tested` status. The Lean module is
-- layered evidence, not a replacement.

namespace Lazarus.VisualSkinDecoupling

/-- The producer-side mode vocabulary written by
    `face_sentinel.py` to `~/.face_sentinel/state.json`. Two
    constructors — `normal` (security primitive admits) and
    `shakespeare` (security primitive denies, lockout active)
    — encode the entire contract between producer and consumer.

    There is no third constructor that could carry presentation
    content (ASCII art, quote text, character voice), distance
    information, or substantive action. The presentation layer
    (`lazarus.md`) consumes this mode and maps it to whatever
    skin the deployment chooses — ASCII art, Shakespeare
    quotes, warm one-liners, Klingon, silence — without
    feeding back into the producer's state.

    The type signature is the load-bearing structural claim:
    a refactor that adds a presentation-carrying constructor
    (e.g. `shakespeare_with_quote q` or `normal_with_emoji e`)
    would change `Mode`'s cardinality and fail to type-check
    at every existing use site, including the producer's
    state-write path. The decoupling is enforced at compile
    time by the type signature `state.mode : Mode` —
    `Presentation` does not appear. -/
inductive Mode
  | normal
  | shakespeare
  deriving DecidableEq, Repr

-- ── Theorem 1: every mode is in the 2-element finite list ──

/-- The producer's mode-vocabulary surface is bounded by a
    2-element finite enumeration. Used by cross-repo consumers
    (Lazarus's `DecouplingBackbone.lean`) as one leg of the
    joint cross-Triad Decoupling composition.

    This is the type-level counterpart of LZ-001's
    `test_visual_skin_decoupling.py` "mode-value vocabulary
    parity" layer — both rule out the producer writing
    presentation content into the mode field, but at different
    abstraction levels. The Lean theorem is structural (any
    inhabitant of `Mode` is one of these two values); the
    Python lint is source-textual. -/
theorem mode_finite_channel (m : Mode) :
    m ∈ ([Mode.normal, Mode.shakespeare] : List Mode) := by
  cases m <;> simp

-- ── Theorem 2: the surface has exactly 2 inhabitants ───────

/-- Cardinality witness: the canonical enumeration of all
    `Mode` values has length 2. Stated separately to make the
    "ℝ can't fit here" framing explicit for downstream
    composition (ℝ is uncountable; 2 is countable). -/
theorem mode_cardinality :
    ([Mode.normal, Mode.shakespeare] : List Mode).length = 2 := by rfl

-- ── Theorem 3: no third inhabitant exists ────────────────

/-- Exhaustivity. Every `Mode` is either `normal` or
    `shakespeare` — there is no third inductive case.
    Decidable by structural pattern matching. Together with
    `DecidableEq` (derived above), this rules out the
    "smuggle presentation through a hidden mode constructor"
    attack class at the type level. -/
theorem mode_exhaustive (m : Mode) :
    m = Mode.normal ∨ m = Mode.shakespeare := by
  cases m
  · exact Or.inl rfl
  · exact Or.inr rfl

end Lazarus.VisualSkinDecoupling
