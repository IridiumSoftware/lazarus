"""
test_companion_readonly_discipline.py — exercises LZ-012
(companion read-only discipline).

LZ-012's runtime claim is that the `/lazarus` companion does
NOT write or edit code, does NOT make commits, does NOT
touch files, does NOT change security settings, does NOT
make decisions for the user, and does NOT give long answers.
The companion is a watchful presence — observe, flag, watch.

The *runtime* behavior is enforced at the LLM-prompt layer
(the same as LZ-001 and LZ-003). The *contract* is the six
prohibition directives in `lazarus.md` §"What you do NOT do"
plus the closing observe/flag/watch anchor.

Honest framing: this is a prompt-contract regression test,
not a runtime-behavior test. Catches refactors that strip
or weaken the prohibition directives. Does NOT prove an LLM
consumer actually refuses these actions at runtime.

Runs locally with no extra deps:
    python3 test/test_companion_readonly_discipline.py
Exit 0 on PASS, non-zero on FAIL.
"""

import os
import re
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def expect_contains(label, haystack, needle):
    if needle not in haystack:
        print(f"FAIL {label}: {needle!r} not found")
        sys.exit(1)


def expect_no_regex_match(label, haystack, pattern):
    if re.search(pattern, haystack):
        match = re.search(pattern, haystack)
        start = max(0, match.start() - 30)
        end = min(len(haystack), match.end() + 30)
        ctx = haystack[start:end].replace("\n", "\\n")
        print(f"FAIL {label}: pattern {pattern!r} matched: ...{ctx}...")
        sys.exit(1)


with open(os.path.join(REPO_ROOT, "lazarus.md")) as f:
    prompt = f.read()


# ── 1. Section anchor exists ───────────────────────────────────────

expect_contains("section header 'What you do NOT do'",
                prompt, "## What you do NOT do")


# ── 2. Six prohibition directives present verbatim ─────────────────

# Each directive is a load-bearing constraint on the companion's
# behavior. Weakening or removing any one changes the contract.
# These match the exact lines under §"What you do NOT do" in
# lazarus.md.

REQUIRED_PROHIBITIONS = [
    "You do not write or edit code",
    "You do not make commits",
    "You do not touch files",
    "You do not change any security settings",
    "You do not make decisions for the user",
    "You do not give long answers",
]

for directive in REQUIRED_PROHIBITIONS:
    expect_contains(f"prohibition: {directive!r}",
                    prompt, directive)


# ── 3. Closing observe-flag-watch anchor ───────────────────────────

# The section ends with "You observe. You flag. You watch. That
# is all." This is the positive framing of the discipline — what
# the companion *does* do, in contrast to the six prohibitions.
# If this line is stripped, the discipline becomes a pure "no"
# list with no anchor for the affirmative role.
expect_contains("closing observe/flag/watch anchor",
                prompt, "You observe. You flag. You watch.")
expect_contains("closing 'That is all' coda",
                prompt, "That is all.")


# ── 4. Counter-positive: no permissive language in the same section ─

# Scan a window around the §"What you do NOT do" section for any
# substring that would invert the discipline (e.g. "you may
# write code", "you can commit"). If a refactor accidentally
# adds a permission that conflicts with a prohibition, this
# trips.

section_start = prompt.find("## What you do NOT do")
section_end_search = prompt.find("## ", section_start + 5)
if section_end_search == -1:
    section_end_search = len(prompt)
section = prompt[section_start:section_end_search]

FORBIDDEN_PERMISSIVE_PATTERNS = [
    r"\byou can write\b",
    r"\byou may write\b",
    r"\byou can commit\b",
    r"\byou may commit\b",
    r"\byou can edit\b",
    r"\byou may edit\b",
    r"\byou can change\b",
    r"\byou may change\b",
    r"\byou can decide\b",
    r"\byou may decide\b",
]

for pat in FORBIDDEN_PERMISSIVE_PATTERNS:
    expect_no_regex_match(f"counter-positive: {pat!r} inside §What-you-do-NOT-do",
                          section, pat)


# ── 5. Spec entry documents the prompt-layer enforcement ──────────

with open(os.path.join(REPO_ROOT, "LAZARUS_SPEC.md")) as f:
    spec = f.read()

expect_contains("spec LZ-012 entry exists",
                spec, "### LZ-012 — companion-read-only-discipline")

# Spec entry should reference the actual §What-you-do-NOT-do
# section name (catches a refactor that secretly upgrades the
# claim to "hard gate" or strips the prompt-layer caveat).
expect_contains("spec LZ-012 references §What-you-do-NOT-do",
                spec, "What you do NOT do")


# ── 6. README also surfaces the discipline ─────────────────────────

# The README's top-of-file description ("It doesn't write code.
# It doesn't fix bugs. It doesn't make decisions. ...") is the
# user-facing surface of LZ-012. Lock the phrase so a README
# refactor that drops it would trip.
with open(os.path.join(REPO_ROOT, "README.md")) as f:
    readme = f.read()

expect_contains("README discipline phrasing: doesn't write code",
                readme, "doesn't write code")
expect_contains("README discipline phrasing: doesn't make decisions",
                readme, "doesn't make decisions")


print("PASS test_companion_readonly_discipline.py")
