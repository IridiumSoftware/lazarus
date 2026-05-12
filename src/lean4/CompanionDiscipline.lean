-- CompanionDiscipline.lean — concrete Lean formalisation of
-- LZ-012 companion-read-only-discipline at the type-level surface.
--
-- LZ-012 (LAZARUS_SPEC.md) establishes that the `/lazarus` LLM
-- companion's surface returns one of three verbs — observe,
-- flag, or watch — per `lazarus.md` §"You observe. You flag.
-- You watch. That is all." The companion never writes, never
-- executes substantive actions, never returns a distance-to-
-- threshold value. The static-text lint at
-- `test/test_companion_readonly_discipline.py` (six-prohibition
-- + counter-positive permissive-language scan) makes this
-- contract executable on every CI push.
--
-- This file adds a LAYERED COMPANION at the Lean type level:
-- the LLM surface's externally-observable output is a
-- 3-constructor inductive (`observe` / `flag` / `watch`), with
-- NO fourth constructor that could carry distance, residue, or
-- substantive action. The type system makes the read-only
-- discipline a compile-time guarantee at the structural level —
-- distinct from (and stronger than) the source-text-search
-- assertions in the Python test.
--
-- This module is the canonical concrete formalisation of the
-- LZ-012 finite-output surface. It is used by
-- `TriadBackbone.lean` (LZ-028 :proved at v0.1.24) which
-- composes the No-Oracle Backbone of the Triad. Before v0.1.26,
-- `TriadBackbone.lean` modelled this leg as a local abstract
-- inductive; v0.1.26 swaps the abstract model for this concrete
-- formalisation. The composition theorem
-- `no_oracle_triad_backbone` is unchanged in shape.
--
-- Honest framing. The Lean track formalises ONE aspect of
-- LZ-012's claim — the type-cardinality of the LLM-companion
-- output. The broader read-only-discipline claim (no commits,
-- no writes, no substantive actions) remains covered by the
-- Python static-lint, which is the source of truth for LZ-012's
-- `:tested` status. The Lean module is layered evidence, not a
-- replacement.

namespace Lazarus.CompanionDiscipline

/-- The `/lazarus` LLM-companion's externally-observable output.
    Three constructors — `observe` (passive sensor report),
    `flag` (active alert), `watch` (continuing to monitor) —
    encode the entire user-facing surface per `lazarus.md`
    §"You observe. You flag. You watch. That is all."

    There is no fourth constructor that could carry a distance
    value, a substantive action, or a write-side effect. A
    refactor that adds e.g. `commit_change s` or
    `flag_at_distance d` would change `LlmOutput`'s cardinality
    and fail to type-check at every existing use site. -/
inductive LlmOutput
  | observe
  | flag
  | watch
  deriving DecidableEq, Repr

-- ── Theorem 1: every output is in the 3-element finite list ──

/-- The LLM-companion's externally-observable surface is bounded
    by a 3-element finite enumeration. Used by
    `TriadBackbone.lean` (LZ-028) as the Lazarus leg of the
    cross-Triad No-Oracle Backbone composition.

    This is the type-level counterpart of LZ-012's Python
    static-lint "no permissive-language patterns inside the
    What-you-do-NOT-do section" — both rule out the LLM
    returning distance/substantive content, but at different
    abstraction levels. The Lean theorem is structural (any
    inhabitant of `LlmOutput` is one of these three values);
    the Python lint is source-textual. -/
theorem llm_finite_channel (l : LlmOutput) :
    l ∈ ([LlmOutput.observe, LlmOutput.flag, LlmOutput.watch]
         : List LlmOutput) := by
  cases l <;> simp

-- ── Theorem 2: the surface has exactly 3 inhabitants ───────

/-- Cardinality witness: the canonical enumeration of all
    `LlmOutput` values has length 3. Stated separately to make
    the "ℝ can't fit here" framing explicit for downstream
    composition (ℝ is uncountable; 3 is countable). -/
theorem llm_output_cardinality :
    ([LlmOutput.observe, LlmOutput.flag, LlmOutput.watch]
     : List LlmOutput).length = 3 := by rfl

-- ── Theorem 3: no fourth inhabitant exists ────────────────

/-- Exhaustivity. Every `LlmOutput` is `observe`, `flag`, or
    `watch` — there is no fourth inductive case. Decidable by
    structural pattern matching. Together with `DecidableEq`
    (derived above), this rules out the "smuggle distance
    through a hidden constructor" attack class at the type
    level, mirroring `lazarus.md` §"That is all." -/
theorem llm_exhaustive (l : LlmOutput) :
    l = LlmOutput.observe ∨ l = LlmOutput.flag ∨ l = LlmOutput.watch := by
  cases l
  · exact Or.inl rfl
  · exact Or.inr (Or.inl rfl)
  · exact Or.inr (Or.inr rfl)

end Lazarus.CompanionDiscipline
