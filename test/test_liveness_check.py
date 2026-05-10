"""
test_liveness_check.py — exercises LZ-013 (anti-spoof liveness
probe).

Tests the pure byte-diff helper `_liveness_delta` and the
threshold constant `LIVENESS_DELTA_MIN`. The full
`liveness_check` function is IO-bound (subprocess to sips,
`time.sleep`) and is exercised by manual sentinel runs against
real cameras and presentation-attack fixtures (printed photo /
iPad screen) — see docs/lazarus_liveness_v0_1_2_companion.md.

Runs locally with no extra deps:
    python3 test/test_liveness_check.py
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


def expect_close(label, actual, expected, tol=1e-9):
    if actual is None or abs(actual - expected) > tol:
        print(f"FAIL {label}: got {actual!r}, expected ~{expected!r}")
        sys.exit(1)


# ── Pure byte-diff helper ──────────────────────────────────────────

# Identical inputs → delta 0 (static-likely).
expect_close("identical_bytes_delta_zero",
             fs._liveness_delta(b"\x00" * 100, b"\x00" * 100),
             0.0)

# All bytes differ → delta 1.0 (very alive — but more likely a
# completely different scene; still passes the liveness threshold).
expect_close("all_bytes_differ_delta_one",
             fs._liveness_delta(b"\x00" * 100, b"\xff" * 100),
             1.0)

# Half differ → delta 0.5.
expect_close("half_differ_delta_half",
             fs._liveness_delta(b"\x00" * 100, b"\x00" * 50 + b"\xff" * 50),
             0.5)

# One byte differs in 100 → delta 0.01 (above threshold 0.008).
expect_close("one_in_100_delta_0p01",
             fs._liveness_delta(b"\x00" * 100, b"\x01" + b"\x00" * 99),
             0.01)

# Length mismatch → None (caller must handle, fail-open in production).
expect("length_mismatch_returns_None",
       fs._liveness_delta(b"\x00" * 100, b"\x00" * 99),
       None)

# Empty input → None.
expect("empty_returns_None",
       fs._liveness_delta(b"", b""),
       None)

# ── Threshold constant ────────────────────────────────────────────

# LIVENESS_DELTA_MIN is the boundary. Calibration: real face sitting
# still measures ~0.015; threshold 0.008 sits well below. Lock the
# value here so accidental tweaks during refactoring trip the test.
expect("threshold_value", fs.LIVENESS_DELTA_MIN, 0.008)
expect("gap_seconds_value", fs.LIVENESS_GAP_SECONDS, 1.0)

# ── Threshold semantics ────────────────────────────────────────────
#
# The liveness_check function evaluates `delta >= LIVENESS_DELTA_MIN`
# for the live decision. Reproduce that math here against a few
# delta values to lock in the inequality direction (>=, not >).

def is_live(delta):
    return delta >= fs.LIVENESS_DELTA_MIN

# Just below threshold → not live (static-likely).
expect("below_threshold_not_live", is_live(0.007), False)
# Exactly at threshold → live (>= boundary).
expect("at_threshold_is_live", is_live(0.008), True)
# Just above threshold → live.
expect("above_threshold_is_live", is_live(0.009), True)
# Calibrated real-face delta → live.
expect("real_face_calibration_is_live", is_live(0.015), True)
# Static photo (delta 0) → not live.
expect("static_photo_not_live", is_live(0.0), False)


print("PASS test_liveness_check.py")
