"""
test_visual_skin_decoupling.py — exercises LZ-001 (visual-skin
/ security-primitive decoupling).

Tests the producer/consumer architecture of the
companion-lockout mechanism:

  PRODUCER  face_sentinel.py — writes mode values
            ("normal" / "shakespeare") to state.json. Does
            NOT carry Bard-quote text or ASCII art.

  CONSUMER  lazarus.md — the slash-command spec the LLM
            reads. Contains the ASCII art and the
            Shakespeare-mode affordance. Reads
            state.json.mode and chooses presentation.

  CONTRACT  Both files share the mode-value vocabulary
            (the string "shakespeare" is the lockout
            signal). Changing the visual skin in lazarus.md
            (Klingon, silence, Rickroll lyrics) requires no
            change to the producer.

This is an architectural / static test — it cannot directly
prove that an LLM consumer respects the mode flag at runtime
(that's a prompt-layer guarantee enforced by review). What
the test DOES catch is the silent regression where a
refactor accidentally folds presentation content into the
producer or breaks the shared mode-value vocabulary.

Runs locally with no extra deps:
    python3 test/test_visual_skin_decoupling.py
Exit 0 on PASS, non-zero on FAIL.
"""

import os
import re
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


def expect_no_regex_match(label, haystack, pattern):
    if re.search(pattern, haystack):
        match = re.search(pattern, haystack)
        # Show a small surrounding context window for debugging.
        start = max(0, match.start() - 30)
        end = min(len(haystack), match.end() + 30)
        ctx = haystack[start:end].replace("\n", "\\n")
        print(f"FAIL {label}: pattern {pattern!r} matched: ...{ctx}...")
        sys.exit(1)


# ── Load sources ───────────────────────────────────────────────────

with open(os.path.join(REPO_ROOT, "face_sentinel.py")) as f:
    producer = f.read()

with open(os.path.join(REPO_ROOT, "lazarus.md")) as f:
    consumer = f.read()


# ── 1. Producer writes the mode-value vocabulary ──────────────────

# face_sentinel.py must write both "normal" (OK state) and
# "shakespeare" (lockout state) as mode values. These are the
# documented mode signals.
expect_contains("producer writes mode='normal'",
                producer, '"normal"')
expect_contains("producer writes mode='shakespeare'",
                producer, '"shakespeare"')

# More structural: the literal `state["mode"] =` assignment must
# exist (catches a refactor that removes the field entirely).
expect_contains("producer assigns to state[\"mode\"]",
                producer, 'state["mode"] =')


# ── 2. Producer does NOT contain presentation content ────────────

# The Bard-quote affordance and the ASCII art live in the consumer
# (lazarus.md). The producer should never carry them. Forbidden
# patterns use word-boundary matching where the substring would
# false-positive on common English words (e.g. "thou" inside
# "without"). Quote phrases are checked literally — they're long
# enough that substring matching is safe.

FORBIDDEN_SKIN_PATTERNS = [
    # Shakespeare-quote vocabulary (word-bounded). The producer
    # may reference "Shakespeare mode" / "Bard" as descriptive
    # labels for the lockout state — those are shorthand, not
    # presentation. But archaic-pronoun substrings only appear
    # inside actual quote text, which is presentation content.
    r"\bdoth\b",
    r"\bthou\b",
    r"\bthee\b",
    r"\bthy\b",
    # Specific quote phrases (literal, case-sensitive).
    r"What light through yonder",
    r"All the world's a stage",
    r"Out, out, brief candle",
    r"Lord, what fools these mortals",
    # The cloud ASCII art — a distinctive fragment.
    r"~ o   o ~",
    # First-person skin-character voice — should live only in
    # lazarus.md / the skill prompt, not in the producer.
    r"I am Mother",
]

for pat in FORBIDDEN_SKIN_PATTERNS:
    expect_no_regex_match(f"producer skin-leak {pat!r}",
                          producer, pat)


# ── 3. Consumer carries the skin ──────────────────────────────────

# The cloud ASCII art lives in lazarus.md. We check for a stable
# fragment of the art so the test trips if the skin moves out of
# this file entirely.
expect_contains("consumer holds ASCII-art skin",
                consumer, "~ o   o ~")

# The Shakespeare-mode section is the named affordance.
expect_contains("consumer documents Shakespeare mode",
                consumer.lower(), "shakespeare mode")


# ── 4. Mode-value vocabulary matches across files ─────────────────

# The consumer must reference the same mode strings the producer
# writes. If the producer renames the lockout state from
# "shakespeare" to "klingon" without updating the consumer, the
# consumer would never trigger and the lockout becomes silent.

# Both files must contain "shakespeare" (the lockout mode signal).
expect_contains("consumer references 'shakespeare' mode value",
                consumer, '"shakespeare"')

# Both files must contain "normal" (the OK mode signal).
expect_contains("consumer references 'normal' mode value",
                consumer, '"normal"')


# ── 5. README documents the swap pattern ──────────────────────────

# README §Customization is the architectural documentation of
# LZ-001 — it tells users that the skin is replaceable. If that
# section disappears, the architectural claim loses its public
# face. (The test verifies the doc, not the test, so a future
# README refactor that just relocates the section without removing
# the claim will trip this — easy fix, intentional friction.)
with open(os.path.join(REPO_ROOT, "README.md")) as f:
    readme = f.read()

expect_contains("README documents swap pattern",
                readme, "Bring your own lockout mode")


# ── 6. State-machine field surface is documented in spec ──────────

# The full state.json field set is documented in LAZARUS_SPEC.md
# under LZ-001. Verify the mode field is named — if a refactor
# strips it from the spec, the test catches the doc drift.
with open(os.path.join(REPO_ROOT, "LAZARUS_SPEC.md")) as f:
    spec = f.read()

expect_contains("spec LZ-001 names the mode field",
                spec, "`mode`")
expect_contains("spec LZ-001 names the authenticated field",
                spec, "`authenticated`")


print("PASS test_visual_skin_decoupling.py")
