"""
test_distance_band_thresholds.py — exercises LZ-002
(face-match distance bands), consistency surface.

Tests the *consistency* of the 18/25/35 distance-band claim
across files and the band-ordering invariant. Does NOT test
the empirical calibration of those values against real faces
— that requires a fixture set of (image, expected band)
pairs and is tracked separately as future work (see
dashboard.md).

Specifically asserts:

1. Python constants in `face_sentinel.py`:
   - MATCH_THRESHOLD == 18.0
   - UNCERTAIN_THRESHOLD == 25.0
   - LOCK_THRESHOLD == 35.0

2. Band ordering: MATCH < UNCERTAIN < LOCK.

3. Cross-language consistency: `face_compare.swift` contains
   the literal threshold values `< 18.0` and `< 25.0` that
   correspond to the Python `MATCH_THRESHOLD` and
   `UNCERTAIN_THRESHOLD` constants. Catches the silent
   threshold-drift failure mode where someone updates the
   Python constant without touching the Swift literal (or
   vice versa).

4. The Swift comment block at the top of `cmdMatch`
   documents the same bands (12-18 likely match, 18-25
   uncertain, > 25 different person). Catches doc drift.

Note: face_compare.swift does NOT carry the LOCK_THRESHOLD
(35.0); the lock decision happens only in Python because
lock_screen() is a Python-side call to pmset / osascript.
So Swift consistency covers MATCH + UNCERTAIN only, which
is correct.

Runs locally with no extra deps:
    python3 test/test_distance_band_thresholds.py
Exit 0 on PASS, non-zero on FAIL.
"""

import os
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, REPO_ROOT)

import face_sentinel as fs  # noqa: E402


def expect(label, actual, expected):
    if actual != expected:
        print(f"FAIL {label}: got {actual!r}, expected {expected!r}")
        sys.exit(1)


def expect_contains(label, haystack, needle):
    if needle not in haystack:
        print(f"FAIL {label}: {needle!r} not found in source")
        sys.exit(1)


# ── 1. Python constants ────────────────────────────────────────────

expect("MATCH_THRESHOLD", fs.MATCH_THRESHOLD, 18.0)
expect("UNCERTAIN_THRESHOLD", fs.UNCERTAIN_THRESHOLD, 25.0)
expect("LOCK_THRESHOLD", fs.LOCK_THRESHOLD, 35.0)


# ── 2. Band ordering ───────────────────────────────────────────────

# Strict less-than chain — accidentally setting MATCH > UNCERTAIN
# (or any other swap) would create unreachable bands.
expect("MATCH < UNCERTAIN",
       fs.MATCH_THRESHOLD < fs.UNCERTAIN_THRESHOLD, True)
expect("UNCERTAIN < LOCK",
       fs.UNCERTAIN_THRESHOLD < fs.LOCK_THRESHOLD, True)


# ── 3. Cross-language consistency (Python ↔ Swift) ────────────────

swift_path = os.path.join(REPO_ROOT, "face_compare.swift")
with open(swift_path, "r") as f:
    swift_src = f.read()

# The Swift source has two runtime threshold comparisons in cmdMatch:
#   let isMatch = bestDist < 18.0
#   let uncertain = bestDist >= 18.0 && bestDist < 25.0
# Both must literally contain the Python threshold values formatted
# as "< X.X". Use f-string formatting to derive the expected
# substring from the Python constant — if the Python constant
# changes (e.g. to 19.0), this assertion catches the missing
# Swift update.

expect_contains("Swift match threshold literal",
                swift_src, f"< {fs.MATCH_THRESHOLD}")
expect_contains("Swift uncertain threshold literal",
                swift_src, f"< {fs.UNCERTAIN_THRESHOLD}")

# Belt-and-suspenders: also verify the >= boundary at the
# uncertain lower edge.
expect_contains("Swift uncertain lower boundary",
                swift_src, f">= {fs.MATCH_THRESHOLD}")


# ── 4. Swift comment-block doc consistency ────────────────────────

# The cmdMatch function carries a comment block documenting the
# bands. Drift between the runtime values and the comment block
# would mislead future readers. Lock the comment lines:
#   //   < 12.0 = strong match
#   //   12-18  = likely match
#   //   18-25  = uncertain
#   //   > 25   = different person

expect_contains("Swift doc band: 12-18 likely match",
                swift_src, "12-18")
expect_contains("Swift doc band: 18-25 uncertain",
                swift_src, "18-25")
expect_contains("Swift doc band: > 25 different person",
                swift_src, "> 25")


# ── 5. Python comment-block doc consistency ───────────────────────

# face_sentinel.py also has a calibration comment block on the
# constants. Verify the LIVENESS adjacent doc isn't accidentally
# treating the face-match bands as liveness bands by checking the
# constant declarations are preceded / followed by the right
# inline labels.

py_path = os.path.join(REPO_ROOT, "face_sentinel.py")
with open(py_path, "r") as f:
    py_src = f.read()

# Verify each named constant has its band-meaning comment intact.
# These match the existing inline comments; if someone strips
# them during a refactor, the test trips and reminds them to
# put them back (or update this lock).
expect_contains("Python doc: MATCH below = match",
                py_src, "Vision distance: below = match")
expect_contains("Python doc: UNCERTAIN comment",
                py_src, "Between match and this = uncertain")
expect_contains("Python doc: LOCK comment",
                py_src, "Above this = lock screen")


print("PASS test_distance_band_thresholds.py")
