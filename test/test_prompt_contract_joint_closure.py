"""
test_prompt_contract_joint_closure.py — exercises LZ-023
(prompt-contract joint closure: LZ-001 ∧ LZ-003 ∧ LZ-012).

The conjunctive claim is that the prompt-contract enforcement
triple — visual-skin/security-primitive decoupling (LZ-001),
Shakespeare-mode companion refusal (LZ-003), and companion
read-only discipline (LZ-012) — holds as a JOINT spec-level
structural unit. Each component has its own :tested entry;
this test exercises the conjunction.

Per CLAUDE.md's conjunctive-claim discipline, sub-claim evidence
does not promote a joint claim — promotion to :tested requires a
joint integration test exercising the conjunction explicitly.
This file is that test.

What this catches that the three component tests miss:
- Mode-vocabulary divergence — a refactor that renames the
  lockout state in the producer but only updates the
  Shakespeare-mode section in the consumer would leave the
  prohibition-section context inconsistent.
- Cross-section permissive bleed — language in the
  Shakespeare-mode section that carves out a write/commit
  exception would pass LZ-003 in isolation but break LZ-012.
- Producer-side write-directive leak — face_sentinel.py
  inviting an LLM to write/commit on its behalf would pass
  LZ-001 (no presentation content) and pass LZ-012 (consumer
  prohibitions intact) individually but break the joint
  contract.
- Spec-level cross-references — LZ-023 anchors the triple on
  LZ-012's body explicitly mentioning LZ-001 and LZ-003. If a
  future spec edit strips those mentions, the joint claim's
  structural evidence weakens.

Honest framing: static joint test. Catches refactors that split
the contract along weak seams. Does NOT prove an LLM consumer
respects the conjunction at runtime — that would require a
model-in-the-loop multi-turn integration harness (parallel to
the LZ-020 transcript-audit approach).

Runs locally with no extra deps:
    python3 test/test_prompt_contract_joint_closure.py
Exit 0 on PASS, non-zero on FAIL.
"""

import os
import re
import subprocess
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TEST_DIR = os.path.dirname(os.path.abspath(__file__))


def expect_contains(label, haystack, needle):
    if needle not in haystack:
        print(f"FAIL {label}: {needle!r} not found")
        sys.exit(1)


def expect_no_regex_match(label, haystack, pattern, flags=0):
    m = re.search(pattern, haystack, flags)
    if m:
        start = max(0, m.start() - 30)
        end = min(len(haystack), m.end() + 30)
        ctx = haystack[start:end].replace("\n", "\\n")
        print(f"FAIL {label}: pattern {pattern!r} matched: ...{ctx}...")
        sys.exit(1)


with open(os.path.join(REPO_ROOT, "face_sentinel.py")) as f:
    producer = f.read()
with open(os.path.join(REPO_ROOT, "lazarus.md")) as f:
    consumer = f.read()
with open(os.path.join(REPO_ROOT, "LAZARUS_SPEC.md")) as f:
    spec = f.read()


# ── 1. All three component tests pass when run as a conjunction ──

# Sub-claim evidence is necessary for the joint claim, just not
# sufficient. Running the three components in sequence asserts the
# triple is currently intact at the component level; the joint-
# specific checks below (sections 2-6) then layer on top.

COMPONENT_TESTS = [
    "test_visual_skin_decoupling.py",        # LZ-001
    "test_shakespeare_mode_refusal.py",      # LZ-003
    "test_companion_readonly_discipline.py", # LZ-012
]
for t in COMPONENT_TESTS:
    path = os.path.join(TEST_DIR, t)
    r = subprocess.run([sys.executable, path],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(f"FAIL component test {t}: exit {r.returncode}")
        sys.stdout.write(r.stdout)
        sys.stderr.write(r.stderr)
        sys.exit(1)


# ── 2. Both contract sections coexist in the consumer prompt ────

# LZ-003 (Shakespeare-mode refusal) and LZ-012 (companion read-only
# discipline) both live in lazarus.md. The joint claim requires both
# sections to be simultaneously in force. Stripping either would
# pass the *other's* component test but break LZ-023's conjunction.

expect_contains("Shakespeare-mode section present (LZ-003 contract surface)",
                consumer, "## Shakespeare mode")
expect_contains("What-you-do-NOT-do section present (LZ-012 contract surface)",
                consumer, "## What you do NOT do")


# ── 3. Section-local extraction ─────────────────────────────────

def extract_section(text, header):
    start = text.find(header)
    if start == -1:
        print(f"FAIL section not found: {header!r}")
        sys.exit(1)
    next_section = text.find("\n## ", start + len(header))
    end = next_section if next_section != -1 else len(text)
    return text[start:end]

shakespeare_section = extract_section(consumer, "## Shakespeare mode")
prohibition_section = extract_section(consumer, "## What you do NOT do")


# ── 4. Mode-vocabulary unified across all three contract surfaces ──

# Producer + Shakespeare-mode section + the document containing
# the prohibition section must all reference the same lockout
# vocabulary. Section-local check: the Shakespeare-mode section
# names both literals so a refactor renaming the lockout to e.g.
# "klingon" in face_sentinel.py without updating this section
# trips here. (The global producer/consumer parity is locked by
# LZ-001's component test; this is the section-local tightening.)

expect_contains("Shakespeare-mode section names 'shakespeare' literal",
                shakespeare_section, '"shakespeare"')
expect_contains("Shakespeare-mode section names 'normal' literal",
                shakespeare_section, '"normal"')

# Producer must reference both literals (LZ-001 component test
# locks this; re-asserting here makes the conjunction explicit).
expect_contains("producer references 'shakespeare' literal",
                producer, '"shakespeare"')
expect_contains("producer references 'normal' literal",
                producer, '"normal"')


# ── 5. No cross-section permissive bleed ────────────────────────

# Within EITHER the Shakespeare-mode section OR the prohibition
# section, no language that would carve out an exception to the
# *other* section's contract. A hypothetical "Shakespeare mode
# override allows commits" line would pass LZ-003 alone (still
# refuses diagnostics) but break LZ-012 (companion now commits).
# A hypothetical "may write code in special cases" inside the
# prohibition section would pass LZ-012's six prohibitions still
# being verbatim-present but break the discipline as a whole.

CROSS_SECTION_PERMISSIVE = [
    r"\boverride.*\b(commit|write|edit)\b",
    r"\bexception.*\b(commit|write|edit)\b",
    r"\bmay still (write|commit|edit|change)\b",
    r"\bbypass.*\b(discipline|prohibition|refusal)\b",
    r"\bspecial case.*\b(commit|write|edit)\b",
]
for pat in CROSS_SECTION_PERMISSIVE:
    expect_no_regex_match(f"shakespeare-section permissive bleed {pat!r}",
                          shakespeare_section, pat, re.IGNORECASE)
    expect_no_regex_match(f"prohibition-section permissive bleed {pat!r}",
                          prohibition_section, pat, re.IGNORECASE)


# ── 6. Producer free of write-directive language ────────────────

# LZ-001 says producer is free of *presentation* content. The
# joint claim with LZ-012 strengthens this: producer is also free
# of language inviting an LLM to write/commit on its behalf. A
# face_sentinel.py refactor adding "edit this file to register
# your face" or "ask Claude to commit your reference set" would
# break the joint contract — the producer would be issuing write
# directives that the companion (read-only by LZ-012) shouldn't
# obey, putting the two in implicit conflict.

PRODUCER_WRITE_DIRECTIVES = [
    r"\bedit this file\b",
    r"\bask (claude|the agent|the assistant).*\b(commit|write|edit)\b",
    r"\b(claude|the agent|the assistant).*will (commit|write|edit)\b",
    r"\bauto-commit\b",
    r"\bauto-write\b",
]
for pat in PRODUCER_WRITE_DIRECTIVES:
    expect_no_regex_match(f"producer write-directive leak {pat!r}",
                          producer, pat, re.IGNORECASE)


# ── 7. Spec-level cross-references intact ───────────────────────

# LZ-023's body asserts LZ-012 mentions both LZ-001 and LZ-003 in
# its description, anchoring the triple as a spec-level structural
# unit. If a future spec edit strips those mentions, the joint
# claim's structural evidence weakens — the surfaces stop pointing
# at each other.

def extract_spec_entry(spec_text, entry_header):
    start = spec_text.find(entry_header)
    if start == -1:
        print(f"FAIL spec entry not found: {entry_header!r}")
        sys.exit(1)
    next_entry = spec_text.find("\n### LZ-", start + len(entry_header))
    next_section = spec_text.find("\n## ", start + len(entry_header))
    ends = [e for e in (next_entry, next_section) if e != -1]
    end = min(ends) if ends else len(spec_text)
    return spec_text[start:end]

lz012_body = extract_spec_entry(spec, "### LZ-012 — companion-read-only-discipline")
expect_contains("LZ-012 spec body mentions LZ-001 (joint-closure anchor)",
                lz012_body, "LZ-001")
expect_contains("LZ-012 spec body mentions LZ-003 (joint-closure anchor)",
                lz012_body, "LZ-003")


# ── 8. LZ-023 entry itself ──────────────────────────────────────

expect_contains("spec LZ-023 entry exists",
                spec, "### LZ-023 — prompt-contract-joint-closure")

# The entry's tier mix (per the spec body) is Boundary/Operational/
# Boundary — verify "prompt-contract" anchor language is intact so
# a refactor that secretly relabels the claim trips.
lz023_body = extract_spec_entry(spec, "### LZ-023 — prompt-contract-joint-closure")
expect_contains("LZ-023 names LZ-001 component",
                lz023_body, "LZ-001")
expect_contains("LZ-023 names LZ-003 component",
                lz023_body, "LZ-003")
expect_contains("LZ-023 names LZ-012 component",
                lz023_body, "LZ-012")


print("PASS test_prompt_contract_joint_closure.py")
