"""
test_prune_logic.py — exercises LZ-014 (reference-pool quality
scoring via leave-one-out nearest-neighbor).

Tests the pure outlier-detection helper `_outliers_from_scores`
and the `PRUNE_OUTLIER_MULTIPLIER` constant. The IO-bound parts
of `prune_cmd` (subprocess to face_compare, tempdir symlink
construction) are exercised by manual runs against the real
~/.face_sentinel/reference/ pool, recorded in
docs/lazarus_prune_v0_1_3_companion.md.

Runs locally with no extra deps:
    python3 test/test_prune_logic.py
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


# ── Empty input ────────────────────────────────────────────────────

expect("empty_no_outliers", fs._outliers_from_scores({}), {})
expect("empty_with_explicit_multiplier", fs._outliers_from_scores({}, multiplier=3.0), {})


# ── No outliers (all near average) ─────────────────────────────────

# Tight cluster around 5.0; nothing exceeds 2× average (10.0).
scores = {"a": 4.5, "b": 5.0, "c": 5.5, "d": 5.2}
expect("tight_cluster_no_outliers",
       fs._outliers_from_scores(scores),
       {})


# ── Single clear outlier ───────────────────────────────────────────

# Average = (5+5+5+5+50)/5 = 14.0. 2x = 28.0. 50 > 28 → outlier.
scores = {"a": 5.0, "b": 5.0, "c": 5.0, "d": 5.0, "e": 50.0}
result = fs._outliers_from_scores(scores)
expect("single_outlier_count", len(result), 1)
expect("single_outlier_name", "e" in result, True)
expect("single_outlier_value", result["e"], 50.0)


# ── Multiple outliers ──────────────────────────────────────────────

# Average = (1+1+1+10+10)/5 = 4.6. 2x = 9.2. 10 > 9.2 → both 10s are outliers.
scores = {"a": 1.0, "b": 1.0, "c": 1.0, "d": 10.0, "e": 10.0}
result = fs._outliers_from_scores(scores)
expect("two_outliers_count", len(result), 2)
expect("two_outliers_d", result["d"], 10.0)
expect("two_outliers_e", result["e"], 10.0)


# ── Boundary: at exactly 2× average → NOT an outlier (strict >) ────

# Average = (1+1+1+1+6)/5 = 2.0. 2x = 4.0. 6 > 4 → outlier.
# Average = (3+3+3+3+12)/5 = 4.8. 2x = 9.6. 12 > 9.6 → outlier.
# Construct a case where one value sits exactly at 2× average:
# values = [1, 1, 1, 1, x] with avg = (4+x)/5; 2*avg = (8+2x)/5 = x
#   → 8 + 2x = 5x → x = 8/3 ≈ 2.667. (4 + 2.667)/5 = 1.333; 2× = 2.667 = x. ✓
# x exactly equals 2*avg, so the strict > rule excludes it.
import importlib  # noqa: E402

scores = {"a": 1.0, "b": 1.0, "c": 1.0, "d": 1.0, "e": 8.0 / 3.0}
result = fs._outliers_from_scores(scores)
expect("at_boundary_not_outlier", len(result), 0)


# ── Custom multiplier ──────────────────────────────────────────────

# Multiplier 1.5 (less conservative) catches more.
scores = {"a": 5.0, "b": 5.0, "c": 5.0, "d": 8.0}  # avg=5.75, 1.5x=8.625
result = fs._outliers_from_scores(scores, multiplier=1.5)
expect("multiplier_1p5_no_outliers", len(result), 0)

scores = {"a": 5.0, "b": 5.0, "c": 5.0, "d": 9.0}  # avg=6.0, 1.5x=9.0
result = fs._outliers_from_scores(scores, multiplier=1.5)
expect("multiplier_1p5_at_boundary_excluded", len(result), 0)

scores = {"a": 5.0, "b": 5.0, "c": 5.0, "d": 10.0}  # avg=6.25, 1.5x=9.375
result = fs._outliers_from_scores(scores, multiplier=1.5)
expect("multiplier_1p5_above_boundary", len(result), 1)


# ── Default multiplier value ───────────────────────────────────────

expect("multiplier_default", fs.PRUNE_OUTLIER_MULTIPLIER, 2.0)


# ── Single-element pool: nothing to compare against ────────────────

# A single ref's score is itself the average; can't exceed any
# multiplier > 1.0 of itself.
expect("single_score_no_outlier",
       fs._outliers_from_scores({"only": 5.0}),
       {})


print("PASS test_prune_logic.py")
