-- Classify.lean — hermetic Lean4 proof of the priority-ordered
-- classification dispatcher underlying `network_monitor.classify`
-- (LZ-009, :tested via `test/test_network_monitor_classify.py`).
--
-- LZ-018 spec entry: the abstract priority dispatcher proved as
-- a structural skeleton. The Python `classify` function uses an
-- if-elif-elif-else cascade over three boolean predicates
-- (`is_system`, `is_known_good`, `is_ai_related`) to emit one of
-- four classes (`SYSTEM`, `KNOWN`, `AI_WATCH`, `OTHER`). The
-- correctness claim is that the priority order is well-defined:
-- given any combination of predicate values, the result is
-- deterministically the leftmost true predicate's class, falling
-- through to `OTHER` only when all three return false.
--
-- Model. The four classes form an inductive type. The dispatcher
-- is a function `Class.classify` from three boolean predicates +
-- input to `Class`. Theorems are abstracted over the predicates
-- — they don't depend on what `is_system`/`is_known`/`is_ai`
-- actually check, only on the cascade structure.
--
-- Theorems proved (hermetic — Lean core only, no Mathlib):
--   - classify_system_priority: SYSTEM dispatch is unconditional
--   - classify_known_priority:  KNOWN fires when not-SYSTEM and
--                               is_known
--   - classify_aiWatch_priority: AI_WATCH fires when not-SYSTEM,
--                                not-KNOWN, is_ai
--   - classify_other_default:   OTHER fires when all three are
--                               false
--   - classify_exhaustive:      the dispatcher is total (returns
--                               one of the four classes for any
--                               input)

namespace Lazarus.Classify

/-- The four classification outcomes of `network_monitor.classify`. -/
inductive Class
  | system
  | known
  | aiWatch
  | other
  deriving DecidableEq, Repr

/-- Priority-ordered dispatcher. Abstract over the predicates so
    the proofs are independent of what `is_system` /
    `is_known_good` / `is_ai_related` actually check. -/
def classify {α : Type} (isSystem isKnown isAI : α → Bool) (c : α) : Class :=
  if isSystem c then
    Class.system
  else if isKnown c then
    Class.known
  else if isAI c then
    Class.aiWatch
  else
    Class.other

-- ── Theorem 1: SYSTEM priority is unconditional ────────────────────

/-- If `isSystem c` is true, the result is `Class.system` regardless
    of what the other two predicates say. This is the priority-
    overrides claim: SYSTEM beats KNOWN beats AI_WATCH. -/
theorem classify_system_priority {α : Type}
    (isSystem isKnown isAI : α → Bool) (c : α)
    (h : isSystem c = true) :
    classify isSystem isKnown isAI c = Class.system := by
  unfold classify
  rw [h]
  rfl

-- ── Theorem 2: KNOWN fires when not-SYSTEM and is_known ───────────

theorem classify_known_priority {α : Type}
    (isSystem isKnown isAI : α → Bool) (c : α)
    (hS : isSystem c = false) (hK : isKnown c = true) :
    classify isSystem isKnown isAI c = Class.known := by
  unfold classify
  rw [hS, hK]
  rfl

-- ── Theorem 3: AI_WATCH fires when not-SYSTEM, not-KNOWN, is_ai ──

theorem classify_aiWatch_priority {α : Type}
    (isSystem isKnown isAI : α → Bool) (c : α)
    (hS : isSystem c = false) (hK : isKnown c = false)
    (hA : isAI c = true) :
    classify isSystem isKnown isAI c = Class.aiWatch := by
  unfold classify
  rw [hS, hK, hA]
  rfl

-- ── Theorem 4: OTHER fires when all three predicates are false ────

theorem classify_other_default {α : Type}
    (isSystem isKnown isAI : α → Bool) (c : α)
    (hS : isSystem c = false) (hK : isKnown c = false)
    (hA : isAI c = false) :
    classify isSystem isKnown isAI c = Class.other := by
  unfold classify
  rw [hS, hK, hA]
  rfl

-- ── Theorem 5: dispatcher is exhaustive (always returns a Class) ──

/-- For any input, `classify` returns one of the four constructors.
    Total functions in Lean trivially satisfy this, but the
    theorem makes the partition explicit: there is no fifth class
    and no "stuck" state. -/
theorem classify_exhaustive {α : Type}
    (isSystem isKnown isAI : α → Bool) (c : α) :
    classify isSystem isKnown isAI c = Class.system ∨
    classify isSystem isKnown isAI c = Class.known ∨
    classify isSystem isKnown isAI c = Class.aiWatch ∨
    classify isSystem isKnown isAI c = Class.other := by
  unfold classify
  by_cases hS : isSystem c = true
  · simp [hS]
  · by_cases hK : isKnown c = true
    · -- not system, is known: result is known
      have hSf : isSystem c = false := by
        cases h : isSystem c with
        | true => exact absurd h hS
        | false => rfl
      simp [hSf, hK]
    · by_cases hA : isAI c = true
      · have hSf : isSystem c = false := by
          cases h : isSystem c with
          | true => exact absurd h hS
          | false => rfl
        have hKf : isKnown c = false := by
          cases h : isKnown c with
          | true => exact absurd h hK
          | false => rfl
        simp [hSf, hKf, hA]
      · have hSf : isSystem c = false := by
          cases h : isSystem c with
          | true => exact absurd h hS
          | false => rfl
        have hKf : isKnown c = false := by
          cases h : isKnown c with
          | true => exact absurd h hK
          | false => rfl
        have hAf : isAI c = false := by
          cases h : isAI c with
          | true => exact absurd h hA
          | false => rfl
        simp [hSf, hKf, hAf]

-- ── Corollary: partition is disjoint (one class per input) ────────

/-- The four cases in `classify_exhaustive` are mutually exclusive
    because `Class` is an inductive type with distinct constructors.
    Stated as a corollary: any two of the four results disagree. -/
theorem classify_disjoint :
    Class.system ≠ Class.known ∧
    Class.system ≠ Class.aiWatch ∧
    Class.system ≠ Class.other ∧
    Class.known ≠ Class.aiWatch ∧
    Class.known ≠ Class.other ∧
    Class.aiWatch ≠ Class.other := by
  refine ⟨?_, ?_, ?_, ?_, ?_, ?_⟩ <;> intro h <;> cases h

end Lazarus.Classify
