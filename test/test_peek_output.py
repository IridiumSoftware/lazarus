"""
test_peek_output.py — exercises LZ-008 (--peek JSON output shape).

Tests the `peek()` function's stdout JSON across 5 branches:
- capture_full fails → {"desk": "unknown", "error": "capture failed"}
- detect finds no face → {"desk": "empty", "faces": 0}
- match → {"desk": "occupied", "who": "owner", ...}
- uncertain → {"desk": "occupied", "who": "uncertain", ...}
- mismatch → {"desk": "occupied", "who": "stranger", ...}

Uses FACE_COMPARE_STUB env var to drive run_face_compare, and
module-level monkey-patching of capture_full to control the
camera step. The "capture failed" branch invokes sys.exit(1)
so we catch SystemExit in that case.

Runs locally with no extra deps:
    python3 test/test_peek_output.py
Exit 0 on PASS, non-zero on FAIL.
"""

import contextlib
import io
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, REPO_ROOT)

import face_sentinel as fs  # noqa: E402


def expect(label, actual, expected):
    if actual != expected:
        print(f"FAIL {label}: got {actual!r}, expected {expected!r}")
        sys.exit(1)


def capture_full_stub_success(path: str) -> bool:
    """Stub that creates an empty file at the requested path and
    returns True — emulates a successful camera capture."""
    Path(path).write_bytes(b"x")
    return True


def capture_full_stub_failure(path: str) -> bool:
    """Stub that simulates a failed camera capture."""
    return False


def with_fixture(face_compare_json, capture_stub):
    """Set up env-var stub for run_face_compare and module-patch
    capture_full. Returns the captured stdout as a string."""
    tmpdir = Path(tempfile.mkdtemp(prefix="lz008_"))
    saved_ref_dir = fs.REF_DIR
    saved_cap_dir = fs.CAP_DIR
    saved_log_file = fs.LOG_FILE
    saved_capture_full = fs.capture_full
    saved_face_compare_stub = os.environ.get("FACE_COMPARE_STUB")
    fs.REF_DIR = tmpdir / "reference"
    fs.CAP_DIR = tmpdir / "captures"
    fs.LOG_FILE = tmpdir / "sentinel.log"
    fs.capture_full = capture_stub
    if face_compare_json is not None:
        os.environ["FACE_COMPARE_STUB"] = face_compare_json
    elif "FACE_COMPARE_STUB" in os.environ:
        del os.environ["FACE_COMPARE_STUB"]
    out = io.StringIO()
    exit_code = None
    try:
        with contextlib.redirect_stdout(out):
            try:
                fs.peek()
            except SystemExit as e:
                exit_code = e.code
        return out.getvalue(), exit_code
    finally:
        fs.REF_DIR = saved_ref_dir
        fs.CAP_DIR = saved_cap_dir
        fs.LOG_FILE = saved_log_file
        fs.capture_full = saved_capture_full
        if saved_face_compare_stub is None:
            os.environ.pop("FACE_COMPARE_STUB", None)
        else:
            os.environ["FACE_COMPARE_STUB"] = saved_face_compare_stub
        shutil.rmtree(tmpdir, ignore_errors=True)


# ── Branch: capture_full fails ─────────────────────────────────────

stdout, exit_code = with_fixture(
    face_compare_json=None,
    capture_stub=capture_full_stub_failure,
)
expect("capture_fail_exit_code", exit_code, 1)
record = json.loads(stdout.strip())
expect("capture_fail_desk", record.get("desk"), "unknown")
expect("capture_fail_error", record.get("error"), "capture failed")


# ── Branch: empty desk (faces == 0) ────────────────────────────────

stdout, exit_code = with_fixture(
    face_compare_json='{"faces": 0}',
    capture_stub=capture_full_stub_success,
)
expect("empty_no_exit", exit_code, None)
record = json.loads(stdout.strip())
expect("empty_desk", record.get("desk"), "empty")
expect("empty_faces", record.get("faces"), 0)
# No "who" key on empty.
expect("empty_no_who_key", "who" in record, False)


# ── Branch: occupied + owner (match: true) ─────────────────────────

stdout, exit_code = with_fixture(
    face_compare_json='{"faces": 1, "match": true, "uncertain": false, "distance": 12.5}',
    capture_stub=capture_full_stub_success,
)
record = json.loads(stdout.strip())
expect("owner_desk", record.get("desk"), "occupied")
expect("owner_who", record.get("who"), "owner")
expect("owner_faces", record.get("faces"), 1)
expect("owner_distance", record.get("distance"), 12.5)


# ── Branch: occupied + uncertain ───────────────────────────────────

stdout, exit_code = with_fixture(
    face_compare_json='{"faces": 1, "match": false, "uncertain": true, "distance": 22.3}',
    capture_stub=capture_full_stub_success,
)
record = json.loads(stdout.strip())
expect("uncertain_desk", record.get("desk"), "occupied")
expect("uncertain_who", record.get("who"), "uncertain")
expect("uncertain_distance", record.get("distance"), 22.3)


# ── Branch: occupied + stranger (mismatch) ─────────────────────────

stdout, exit_code = with_fixture(
    face_compare_json='{"faces": 1, "match": false, "uncertain": false, "distance": 38.7}',
    capture_stub=capture_full_stub_success,
)
record = json.loads(stdout.strip())
expect("stranger_desk", record.get("desk"), "occupied")
expect("stranger_who", record.get("who"), "stranger")
expect("stranger_distance", record.get("distance"), 38.7)


# ── Output is exactly one line of JSON (no trailing extra content) ─

stdout, exit_code = with_fixture(
    face_compare_json='{"faces": 0}',
    capture_stub=capture_full_stub_success,
)
# Strip trailing newline; ensure result is one well-formed JSON line.
expect("single_line_no_trailing_garbage",
       stdout.count("\n"),
       1)


# ── distance is rounded to 1 decimal place ─────────────────────────

stdout, exit_code = with_fixture(
    face_compare_json='{"faces": 1, "match": true, "distance": 12.345678}',
    capture_stub=capture_full_stub_success,
)
record = json.loads(stdout.strip())
expect("distance_rounded_to_1dp", record.get("distance"), 12.3)


print("PASS test_peek_output.py")
