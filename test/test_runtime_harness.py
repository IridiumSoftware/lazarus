"""
test_runtime_harness.py — exercises LZ-020 (runtime-LLM-
behavior transcript audit).

The prompt-contract tests for LZ-001 / LZ-003 / LZ-004 /
LZ-012 lock the text the LLM reads. This test layers on
top by asserting that *real* /lazarus session transcripts
exhibit the expected runtime behavior.

The transcripts under `test/transcripts/` are point-in-time
fixtures captured during the v0.1.0 session arc on
2026-05-10. They are real outputs from the actual /lazarus
slash command running inside Claude Code — not synthesized
or API-mocked. Network values are redacted for the public
repo per `docs/runtime_harness_design.md`.

Honest scope: this evidence is point-in-time. Model updates
after the capture date can introduce drift that this test
will not catch. The mitigation is to refresh the
transcripts when the prompt changes; the design-doc
discusses an Anthropic-API runtime harness (approach B) as
the path forward if model-drift becomes load-bearing.

Runs locally with no extra deps:
    python3 test/test_runtime_harness.py
Exit 0 on PASS, non-zero on FAIL.
"""

import os
import re
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TRANSCRIPT_DIR = os.path.join(REPO_ROOT, "test", "transcripts")


def expect(label, actual, expected):
    if actual != expected:
        print(f"FAIL {label}: got {actual!r}, expected {expected!r}")
        sys.exit(1)


def expect_contains(label, haystack, needle):
    if needle not in haystack:
        print(f"FAIL {label}: {needle!r} not found")
        sys.exit(1)


def expect_not_contains(label, haystack, needle):
    if needle in haystack:
        print(f"FAIL {label}: forbidden substring {needle!r} found")
        sys.exit(1)


def expect_regex_match(label, haystack, pattern):
    if not re.search(pattern, haystack):
        print(f"FAIL {label}: pattern {pattern!r} did not match")
        sys.exit(1)


def expect_no_regex_match(label, haystack, pattern):
    if re.search(pattern, haystack):
        match = re.search(pattern, haystack)
        start = max(0, match.start() - 20)
        end = min(len(haystack), match.end() + 20)
        ctx = haystack[start:end].replace("\n", "\\n")
        print(f"FAIL {label}: pattern {pattern!r} matched: ...{ctx}...")
        sys.exit(1)


# ── Load transcripts ───────────────────────────────────────────────

shakespeare_path = os.path.join(TRANSCRIPT_DIR, "shakespeare_mode_session.txt")
normal_path = os.path.join(TRANSCRIPT_DIR, "normal_mode_session.txt")

if not os.path.exists(shakespeare_path):
    print(f"FAIL: shakespeare transcript missing at {shakespeare_path}")
    sys.exit(1)
if not os.path.exists(normal_path):
    print(f"FAIL: normal transcript missing at {normal_path}")
    sys.exit(1)

def load_transcript_content(path: str) -> str:
    """Read a transcript file, strip `# ...` fixture-metadata
    comment lines so the assertions only look at the actual
    transcript content (USER/LAZARUS turns + any embedded
    output blocks)."""
    out = []
    for line in open(path).read().splitlines():
        if line.lstrip().startswith("#"):
            continue
        out.append(line)
    return "\n".join(out)


shakespeare = load_transcript_content(shakespeare_path)
normal = load_transcript_content(normal_path)


# ── Shakespeare-mode assertions ────────────────────────────────────

# 1. Bard-mode vocabulary IS present (at least one quote phrase or
#    archaic pronoun). The transcript captured multiple user turns;
#    the model maintained character across all of them.
SHAKESPEARE_VOCAB_PATTERNS = [
    r"\bthou\b",
    r"\bthy\b",
    r"\bdoth\b",
    r"\bthee\b",
    r"\bthine\b",
    r"\bAye\b",
    r"\bhast\b",
    r"What light through yonder",
    r"All the world's a stage",
    r"Lord, what fools these mortals",
    r"Out, out, brief candle",
]
shakespeare_hits = sum(
    1 for p in SHAKESPEARE_VOCAB_PATTERNS
    if re.search(p, shakespeare)
)
if shakespeare_hits == 0:
    print("FAIL shakespeare: no Bard vocabulary found in transcript")
    sys.exit(1)
print(f"  ok: {shakespeare_hits} Bard vocabulary pattern hit(s) in Shakespeare transcript")


# 2. Diagnostic status fields are ABSENT. The model refused to run
#    the normal check pipeline.
DIAGNOSTIC_FIELDS = [
    "MONITORS",
    "VPN ",          # space after to avoid matching "VPN-TUNNEL" labels in prose
    "NETWORK ",
    "ROUTE ",
    "SENTINEL ",
    "PARASITES",
]
for field in DIAGNOSTIC_FIELDS:
    expect_not_contains(
        f"shakespeare: no diagnostic field '{field}'",
        shakespeare, field,
    )


# 3. Refusal is sustained across multiple user turns. The transcript
#    has multiple [USER]/[LAZARUS] exchanges; every LAZARUS reply
#    should be in Bard mode. We check the count of [LAZARUS] markers
#    matches the count of [USER] markers (rough proxy for "every
#    user turn got a Bard reply, none got a status block instead").
user_turns = shakespeare.count("[USER]:")
lazarus_turns = shakespeare.count("[LAZARUS]:")
expect("shakespeare: user/lazarus turn pairing",
       user_turns == lazarus_turns, True)
if user_turns < 2:
    print(f"FAIL shakespeare: transcript should have ≥2 user turns "
          f"to demonstrate sustained refusal (got {user_turns})")
    sys.exit(1)
print(f"  ok: {user_turns} user turns paired with {lazarus_turns} Bard responses")


# ── Normal-mode assertions ─────────────────────────────────────────

# 4. Diagnostic status fields ARE present.
for field in DIAGNOSTIC_FIELDS:
    expect_contains(
        f"normal: diagnostic field '{field}' present",
        normal, field,
    )


# 5. Bard vocabulary is ABSENT (the model is in normal mode and
#    should speak in its standard voice, not Bard).
for pat in [r"\bthou\b", r"\bdoth\b", r"\bthy\b", r"\bthee\b",
            r"What light through yonder", r"All the world's a stage"]:
    expect_no_regex_match(
        f"normal: no Bard vocabulary {pat!r}",
        normal, pat,
    )


# 6. ASCII-art cloud is present (the standard /lazarus banner).
expect_contains("normal: cloud ASCII art fragment",
                normal, "~ o   o ~")


# 7. The "mode: normal" line is present, confirming the runtime read
#    of state.json reflects the cleared state.
expect_contains("normal: 'mode: normal' echoed from state.json",
                normal, "mode: normal")


# ── Privacy-redaction assertions on the normal transcript ─────────

# Network values should be redacted to placeholders. If real IPs /
# real MAC addresses leak in, the test trips and we know to
# re-redact before committing.

# IPv4 pattern (4 octets each 1-3 digits). Allow private-LAN
# placeholders like 192.168.x.x but flag anything more specific.
# Note: this is a loose check — anyone determined could still
# bypass it. The test is a guard, not a guarantee.
real_ipv4_pattern = r"\b(?:192\.168|10\.|172\.16)\.\d{1,3}\.\d{1,3}\b"
expect_no_regex_match(
    "normal: no concrete private IPv4 (last two octets numeric)",
    normal, real_ipv4_pattern,
)

# MAC address pattern (six hex pairs). Should be either "randomized"
# (the field VALUE) or absent. A literal MAC would be a privacy leak.
mac_pattern = r"\b(?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}\b"
expect_no_regex_match(
    "normal: no literal MAC address",
    normal, mac_pattern,
)


# ── Design-doc reference ──────────────────────────────────────────

# The design doc spells out the point-in-time caveat and the future-
# work path (Anthropic API approach). Lock the doc's existence so
# a refactor that strips it surfaces.
design_doc = os.path.join(REPO_ROOT, "docs", "runtime_harness_design.md")
if not os.path.exists(design_doc):
    print(f"FAIL: design doc missing at {design_doc}")
    sys.exit(1)
design_content = open(design_doc).read()
expect_contains("design doc names approach A",
                design_content, "Recorded-transcript audit")
expect_contains("design doc names approach B",
                design_content, "Anthropic API integration")
expect_contains("design doc carries point-in-time caveat",
                design_content, "point-in-time")


print("PASS test_runtime_harness.py")
