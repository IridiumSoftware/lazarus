"""
test_reference_bounds.py — exercises LZ-006 (reference-pool
storage bounds via prune_oldest).

Tests prune_oldest's behavior across pool-size scenarios:
- Under cap → no-op (guard prevents negative-index disaster).
- At cap → no-op.
- Over cap by 1 → removes single oldest by mtime.
- Over cap by 10 → removes 10 oldest.
- Each removal deletes ALL three files (.json, .fpdata, .jpg)
  for the same ref stem.
- Mtime-based ordering (NOT alphabetical/lexicographic).

Uses module-level monkey-patching of REF_DIR so the test does
not touch the real ~/.face_sentinel/reference/ pool.

Runs locally with no extra deps:
    python3 test/test_reference_bounds.py
Exit 0 on PASS, non-zero on FAIL.
"""

import os
import shutil
import sys
import tempfile
import time
from pathlib import Path

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, REPO_ROOT)

import face_sentinel as fs  # noqa: E402


def expect(label, actual, expected):
    if actual != expected:
        print(f"FAIL {label}: got {actual!r}, expected {expected!r}")
        sys.exit(1)


def make_ref(directory: Path, stem: str, age_seconds: int = 0) -> None:
    """Create a synthetic (.json, .fpdata, .jpg) triple with mtime
    offset back from `now` by `age_seconds` seconds."""
    for ext in ("json", "fpdata", "jpg"):
        (directory / f"{stem}.{ext}").write_text("synthetic")
    mtime = time.time() - age_seconds
    for ext in ("json", "fpdata", "jpg"):
        os.utime(directory / f"{stem}.{ext}", (mtime, mtime))


def count_jsons(directory: Path) -> int:
    return len(list(directory.glob("*.json")))


def run_test(name, body):
    tmpdir = Path(tempfile.mkdtemp(prefix="lz006_"))
    saved_ref_dir = fs.REF_DIR
    saved_log_file = fs.LOG_FILE
    fs.REF_DIR = tmpdir
    fs.LOG_FILE = tmpdir / "sentinel.log"
    try:
        body(tmpdir)
        print(f"  ok: {name}")
    finally:
        fs.REF_DIR = saved_ref_dir
        fs.LOG_FILE = saved_log_file
        shutil.rmtree(tmpdir, ignore_errors=True)


# ── Test cases ─────────────────────────────────────────────────────


def test_under_cap_is_noop(tmpdir):
    """49 refs in pool, MAX=50 → prune_oldest does nothing."""
    for i in range(49):
        make_ref(tmpdir, f"ref_{i:04d}", age_seconds=49 - i)
    expect("under_cap_before", count_jsons(tmpdir), 49)
    fs.prune_oldest()
    expect("under_cap_after", count_jsons(tmpdir), 49)


def test_at_cap_is_noop(tmpdir):
    """Exactly 50 refs in pool, MAX=50 → no-op."""
    for i in range(50):
        make_ref(tmpdir, f"ref_{i:04d}", age_seconds=50 - i)
    expect("at_cap_before", count_jsons(tmpdir), 50)
    fs.prune_oldest()
    expect("at_cap_after", count_jsons(tmpdir), 50)


def test_over_by_one_removes_oldest(tmpdir):
    """51 refs → prune_oldest removes the single oldest."""
    # ref_0000 is oldest (age 51); ref_0050 is newest (age 1).
    for i in range(51):
        make_ref(tmpdir, f"ref_{i:04d}", age_seconds=51 - i)
    expect("over_by_one_before", count_jsons(tmpdir), 51)
    fs.prune_oldest()
    expect("over_by_one_after", count_jsons(tmpdir), 50)
    # The oldest (ref_0000) should be gone.
    expect("oldest_removed",
           (tmpdir / "ref_0000.json").exists(),
           False)
    # The next-oldest (ref_0001) should still be present.
    expect("second_oldest_kept",
           (tmpdir / "ref_0001.json").exists(),
           True)


def test_over_by_ten_removes_ten_oldest(tmpdir):
    """60 refs → prune_oldest removes the 10 oldest."""
    for i in range(60):
        make_ref(tmpdir, f"ref_{i:04d}", age_seconds=60 - i)
    fs.prune_oldest()
    expect("over_by_ten_after", count_jsons(tmpdir), 50)
    # The 10 oldest (ref_0000..ref_0009) should be gone.
    for i in range(10):
        expect(f"oldest_removed_{i}",
               (tmpdir / f"ref_{i:04d}.json").exists(),
               False)
    # ref_0010 onwards should remain.
    for i in range(10, 60):
        expect(f"kept_{i}",
               (tmpdir / f"ref_{i:04d}.json").exists(),
               True)


def test_all_three_files_deleted_per_ref(tmpdir):
    """When a ref is pruned, all three of (.json, .fpdata, .jpg) go."""
    for i in range(51):
        make_ref(tmpdir, f"ref_{i:04d}", age_seconds=51 - i)
    fs.prune_oldest()
    for ext in ("json", "fpdata", "jpg"):
        expect(f"ref_0000_{ext}_gone",
               (tmpdir / f"ref_0000.{ext}").exists(),
               False)


def test_mtime_not_alphabetical(tmpdir):
    """Ordering is by mtime, NOT by filename. A lexicographically-late
    name with the oldest mtime should be pruned first."""
    # Lexicographic order: "ref_aaa" < "ref_zzz" but we assign
    # ref_zzz the oldest mtime so it should be pruned first.
    for i in range(50):
        make_ref(tmpdir, f"ref_aaa_{i:04d}", age_seconds=1)  # newest
    make_ref(tmpdir, "ref_zzz_old", age_seconds=999)         # oldest
    expect("mtime_before", count_jsons(tmpdir), 51)
    fs.prune_oldest()
    expect("mtime_after", count_jsons(tmpdir), 50)
    expect("zzz_old_gone (mtime, not alpha)",
           (tmpdir / "ref_zzz_old.json").exists(),
           False)
    # All the aaa_ refs should remain.
    for i in range(50):
        expect(f"aaa_{i}_kept",
               (tmpdir / f"ref_aaa_{i:04d}.json").exists(),
               True)


def test_under_cap_guard_not_negative_index_disaster(tmpdir):
    """Regression test for the under-cap bug: prior to v0.1.5, calling
    prune_oldest with N < MAX_REFERENCES would compute
    to_remove = N - 50 (negative) and metas[:negative] would delete
    all-but-newest. After the fix, it's a clean no-op."""
    for i in range(5):  # way under cap
        make_ref(tmpdir, f"ref_{i:04d}", age_seconds=5 - i)
    expect("regression_before", count_jsons(tmpdir), 5)
    fs.prune_oldest()
    expect("regression_after_should_still_be_5", count_jsons(tmpdir), 5)


# ── Run ────────────────────────────────────────────────────────────

run_test("under_cap_is_noop", test_under_cap_is_noop)
run_test("at_cap_is_noop", test_at_cap_is_noop)
run_test("over_by_one_removes_oldest", test_over_by_one_removes_oldest)
run_test("over_by_ten_removes_ten_oldest", test_over_by_ten_removes_ten_oldest)
run_test("all_three_files_deleted_per_ref", test_all_three_files_deleted_per_ref)
run_test("mtime_not_alphabetical", test_mtime_not_alphabetical)
run_test("under_cap_guard_not_negative_index_disaster",
         test_under_cap_guard_not_negative_index_disaster)


# ── MAX_REFERENCES lock ────────────────────────────────────────────

# Lock the spec'd cap value here so changes trip the test.
expect("max_references_value", fs.MAX_REFERENCES, 50)


print("PASS test_reference_bounds.py")
