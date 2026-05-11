"""
test_auth_strict_touchid.py — exercises LZ-019 (`--strict-touchid`
hard-gate mode).

LZ-019 promotes the Touch ID gate from opportunistic / fail-open
(LZ-015) to hard auth failure when the user passes
`--strict-touchid` on the CLI. The flag threads into
`auth(strict_touchid=True)`. On any non-"ok" outcome from
`_touchid_check()` the function logs `touchid_strict_fail` and
exits non-zero before reaching the face-match step.

The test drives `auth()` with all camera / face-compare / sips
dependencies stubbed (same pattern as
`test_auth_clears_shakespeare.py`) and asserts on:
- Exit code (None for proceeds, 1 for hard fail)
- Log events (touchid_strict_fail vs touchid_ok / touchid_nonzero /
  touchid_unavailable)
- State.json mutations (only when auth completes — strict-fail
  paths exit before state is touched)

Runs locally with no extra deps:
    python3 test/test_auth_strict_touchid.py
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


def read_log_events(log_path: Path) -> list:
    if not log_path.exists():
        return []
    out = []
    for line in log_path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    return out


def event_names(events: list) -> list:
    return [e.get("event") for e in events]


def drive_auth(touchid_result: str, strict: bool):
    """Run auth(strict_touchid=strict) with `_touchid_check` stubbed
    to return `touchid_result`. All other IO dependencies are
    stubbed for the success-path case (a "good" face-compare match
    + camera capture + sips downsize). Returns
    (state, events, exit_code)."""
    tmpdir = Path(tempfile.mkdtemp(prefix="lz019_"))

    saved = {
        "REF_DIR": fs.REF_DIR,
        "CAP_DIR": fs.CAP_DIR,
        "LOG_FILE": fs.LOG_FILE,
        "STATE_FILE": fs.STATE_FILE,
        "BG_SNAPSHOT": fs.BG_SNAPSHOT,
        "_touchid_check": fs._touchid_check,
        "capture_full": fs.capture_full,
        "run_face_compare": fs.run_face_compare,
        "shrink": fs.shrink,
    }

    try:
        fs.REF_DIR = tmpdir / "reference"
        fs.CAP_DIR = tmpdir / "captures"
        fs.LOG_FILE = tmpdir / "sentinel.log"
        fs.STATE_FILE = tmpdir / "state.json"
        fs.BG_SNAPSHOT = tmpdir / "background.jpg"
        fs.REF_DIR.mkdir(parents=True, exist_ok=True)
        fs.CAP_DIR.mkdir(parents=True, exist_ok=True)
        (fs.REF_DIR / "ref_synthetic.json").write_text("{}")

        # Stubs.
        fs._touchid_check = lambda **kwargs: touchid_result

        def stub_capture_full(path):
            Path(path).write_bytes(b"x")
            return True
        fs.capture_full = stub_capture_full

        fs.run_face_compare = lambda *args, **kwargs: {
            "faces": 1, "match": True, "distance": 12.5,
        }

        def stub_shrink(src, dst, width=320):
            Path(dst).write_bytes(b"x")
        fs.shrink = stub_shrink

        exit_code = None
        with contextlib.redirect_stdout(io.StringIO()):
            try:
                fs.auth(strict_touchid=strict)
            except SystemExit as e:
                exit_code = e.code

        state = fs.load_state() if fs.STATE_FILE.exists() else {}
        return state, read_log_events(fs.LOG_FILE), exit_code
    finally:
        for k, v in saved.items():
            setattr(fs, k, v)
        shutil.rmtree(tmpdir, ignore_errors=True)


# ── Branch 1: strict + ok → proceeds normally ──────────────────────

state, events, exit_code = drive_auth("ok", strict=True)
expect("strict_ok: no exit", exit_code, None)
expect("strict_ok: mode normal", state.get("mode"), "normal")
expect("strict_ok: authenticated True", state.get("authenticated"), True)
ev = event_names(events)
expect("strict_ok: touchid_ok logged",
       "touchid_ok" in ev, True)
expect("strict_ok: NO touchid_strict_fail",
       "touchid_strict_fail" in ev, False)
expect("strict_ok: auth_ok logged",
       "auth_ok" in ev, True)


# ── Branch 2: strict + nonzero → hard exit ─────────────────────────

state, events, exit_code = drive_auth("nonzero", strict=True)
expect("strict_nonzero: exit code 1", exit_code, 1)
ev = event_names(events)
expect("strict_nonzero: touchid_strict_fail logged",
       "touchid_strict_fail" in ev, True)
# No downstream events — auth exited before face check.
expect("strict_nonzero: no auth_ok",
       "auth_ok" in ev, False)
# Find the strict-fail event and check its `result` field.
fail_events = [e for e in events if e.get("event") == "touchid_strict_fail"]
expect("strict_nonzero: 1 strict_fail event",
       len(fail_events), 1)
expect("strict_nonzero: result field = nonzero",
       fail_events[0].get("result"), "nonzero")


# ── Branch 3: strict + unavailable → hard exit ─────────────────────

state, events, exit_code = drive_auth("unavailable", strict=True)
expect("strict_unavailable: exit code 1", exit_code, 1)
ev = event_names(events)
expect("strict_unavailable: touchid_strict_fail logged",
       "touchid_strict_fail" in ev, True)
fail_events = [e for e in events if e.get("event") == "touchid_strict_fail"]
expect("strict_unavailable: result field = unavailable",
       fail_events[0].get("result"), "unavailable")


# ── Branch 4: non-strict + nonzero → opportunistic (proceeds) ──────

# Sanity check that non-strict path is unchanged (regression
# guard for LZ-015's fail-open semantics).
state, events, exit_code = drive_auth("nonzero", strict=False)
expect("non_strict_nonzero: no exit", exit_code, None)
expect("non_strict_nonzero: mode normal", state.get("mode"), "normal")
ev = event_names(events)
expect("non_strict_nonzero: touchid_nonzero logged",
       "touchid_nonzero" in ev, True)
expect("non_strict_nonzero: NO touchid_strict_fail",
       "touchid_strict_fail" in ev, False)
expect("non_strict_nonzero: auth_ok logged",
       "auth_ok" in ev, True)


# ── Branch 5: non-strict + unavailable → opportunistic (proceeds) ──

state, events, exit_code = drive_auth("unavailable", strict=False)
expect("non_strict_unavailable: no exit", exit_code, None)
expect("non_strict_unavailable: mode normal",
       state.get("mode"), "normal")
ev = event_names(events)
expect("non_strict_unavailable: touchid_unavailable logged",
       "touchid_unavailable" in ev, True)
expect("non_strict_unavailable: NO touchid_strict_fail",
       "touchid_strict_fail" in ev, False)


# ── Default-parameter check ───────────────────────────────────────

# auth() with no arguments defaults to strict_touchid=False. Lock
# this via the function signature so a refactor that flips the
# default trips the test.
import inspect  # noqa: E402
sig = inspect.signature(fs.auth)
strict_param = sig.parameters.get("strict_touchid")
if strict_param is None:
    print("FAIL: auth() is missing the strict_touchid parameter")
    sys.exit(1)
expect("auth default strict_touchid is False",
       strict_param.default, False)


print("PASS test_auth_strict_touchid.py")
