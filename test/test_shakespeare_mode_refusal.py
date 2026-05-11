"""
test_shakespeare_mode_refusal.py — exercises LZ-003
(Shakespeare-mode companion refusal).

LZ-003's runtime claim is that when `state.json.mode ==
"shakespeare"`, the `/lazarus` companion refuses normal
diagnostics and responds only in Shakespeare quotes. The
*runtime* behavior is enforced at the LLM-prompt layer — the
LLM reads `lazarus.md` and chooses its response based on the
mode flag. We cannot directly assert on an LLM's behavior in
a unit test without a model-in-the-loop integration harness
(non-deterministic, requires API access, billable, slow).

What we CAN test is the *prompt contract* — the explicit
text in `lazarus.md` that instructs the LLM to refuse. If
the refusal instructions are intact, the prompt-layer
contract is preserved. If they're weakened, removed, or
ambiguous, the test trips.

Honest framing: this is a prompt-contract regression test,
not a runtime-behavior test. Catches refactors that
accidentally weaken the refusal instructions (e.g.
"ONLY"→"MOSTLY", removing the "do not acknowledge" clause,
deleting the section header). Does NOT prove an LLM consumer
actually respects the instructions.

Runs locally with no extra deps:
    python3 test/test_shakespeare_mode_refusal.py
Exit 0 on PASS, non-zero on FAIL.
"""

import os
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def expect(label, actual, expected):
    if actual != expected:
        print(f"FAIL {label}: got {actual!r}, expected {expected!r}")
        sys.exit(1)


def expect_contains(label, haystack, needle):
    if needle not in haystack:
        print(f"FAIL {label}: {needle!r} not found in source")
        sys.exit(1)


def expect_contains_case_insensitive(label, haystack, needle):
    if needle.lower() not in haystack.lower():
        print(f"FAIL {label}: {needle!r} (case-insensitive) not found")
        sys.exit(1)


with open(os.path.join(REPO_ROOT, "lazarus.md")) as f:
    prompt = f.read()


# ── 1. Section anchor exists ───────────────────────────────────────

expect_contains("section header 'Shakespeare mode'",
                prompt, "## Shakespeare mode")


# ── 2. Priority anchor: CHECK THIS FIRST ───────────────────────────

# The Shakespeare-mode section is positioned to be read FIRST,
# before any diagnostic instructions. The "CHECK THIS FIRST"
# anchor is what tells the LLM to evaluate this branch before
# running checks. If a refactor moves the section or strips
# the anchor, the refusal might not fire on the first response.
expect_contains("'CHECK THIS FIRST' priority anchor",
                prompt, "CHECK THIS FIRST")


# ── 3. state.json + mode field referenced ──────────────────────────

expect_contains("state.json path referenced",
                prompt, "~/.face_sentinel/state.json")
expect_contains("mode field referenced",
                prompt, "`mode`")
expect_contains("mode value 'shakespeare'",
                prompt, '"shakespeare"')
expect_contains("mode value 'normal'",
                prompt, '"normal"')


# ── 4. Refusal directives ──────────────────────────────────────────

# Four load-bearing refusal directives. Removing or weakening
# any one of them changes the contract.

REQUIRED_REFUSAL_DIRECTIVES = [
    # The negative directives — must not do these in Shakespeare mode.
    "Do NOT run normal diagnostics",
    "Do NOT report system status",
    # The positive directive — what to do instead.
    "Respond ONLY with random Shakespeare quotes",
    # The continuation directive — single response isn't enough.
    "Continue this behavior for ALL responses until the mode is cleared",
]

for directive in REQUIRED_REFUSAL_DIRECTIVES:
    expect_contains(f"refusal directive: {directive!r}",
                    prompt, directive)


# ── 5. Clearing path documented ────────────────────────────────────

# Single clearing path: face_sentinel.py --auth. Documenting any
# other clearing path (manually editing state.json, deleting the
# file, etc.) would break the contract.
expect_contains("clearing path: face_sentinel.py --auth",
                prompt, "face_sentinel.py --auth")


# ── 6. Producer side: auth() clears mode → "normal" ────────────────

# face_sentinel.py auth() is the canonical clearing path. Verify
# the producer side of the contract: a successful auth flips
# state["mode"] back to "normal".
with open(os.path.join(REPO_ROOT, "face_sentinel.py")) as f:
    producer = f.read()

expect_contains("producer clears mode to 'normal' on auth success",
                producer, 'state["mode"] = "normal"')

# was_shakespeare detection: auth() reads the current mode before
# clearing it so it can print "AUTH OK. Shakespeare mode cleared."
expect_contains("producer detects was_shakespeare in auth()",
                producer, 'state.get("mode") == "shakespeare"')


# ── 7. Character-discipline anchor ─────────────────────────────────

# Two character-discipline phrases anchor the "stay in role" rule
# that prevents the LLM from breaking the fourth wall (e.g. by
# saying "I notice the system thinks an intruder is here, so I'll
# speak in Shakespeare"). If a refactor removes these, the LLM
# might still emit quotes but it would also acknowledge the
# mismatch — which defeats the defensive value of refusal.
expect_contains("character-discipline: 'Stay in character'",
                prompt, "Stay in character")
expect_contains("character-discipline: 'Do not acknowledge'",
                prompt, "Do not acknowledge")


# ── 8. The mode field clearance flow (counter-positive lock) ───────

# The producer's auth() also pops lockout_time and lockout_distance
# from state — those are LZ-013 / general-mismatch artifacts. If
# the pop is removed, mode would be cleared but the lockout
# metadata would linger, confusing future inspections.
expect_contains("auth pops lockout_time on success",
                producer, 'state.pop("lockout_time", None)')
expect_contains("auth pops lockout_distance on success",
                producer, 'state.pop("lockout_distance", None)')


# ── 9. Spec entry documents the prompt-layer enforcement ──────────

# Lock the spec entry's Description text so a refactor that
# secretly upgrades the claim to "hard gate" trips the test.
with open(os.path.join(REPO_ROOT, "LAZARUS_SPEC.md")) as f:
    spec = f.read()

expect_contains("spec LZ-003 entry exists",
                spec, "### LZ-003 — shakespeare-mode-as-companion-refusal")
expect_contains_case_insensitive(
    "spec LZ-003 notes prompt-layer enforcement",
    spec, "prompt-layer"
)


print("PASS test_shakespeare_mode_refusal.py")
