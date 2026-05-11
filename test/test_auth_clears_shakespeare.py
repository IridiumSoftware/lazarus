"""
test_auth_clears_shakespeare.py — exercises LZ-004
(--auth clears Shakespeare mode).

Drives `face_sentinel.auth()` with all camera / face-compare /
Touch ID / sips dependencies stubbed and asserts on the
producer-side state transitions:

  Pre:  state.json = {mode: "shakespeare", authenticated: false,
                       lockout_time: "...", lockout_distance: ...}
  Post: state.json = {mode: "normal", authenticated: true,
                      auth_time: <now>, last_seen_owner: <now>}
        — lockout_time, lockout_distance removed.
        — sentinel.log carries `auth_ok` + `shakespeare_cleared`.

Plus the "fresh auth" case where the pre-state is already
normal (no prior Shakespeare lockout) — auth() emits `auth_ok`
without the shakespeare_cleared event.

Uses module-level monkey-patching of file-path globals and
the four IO dependencies (`_touchid_check`, `capture_full`,
`run_face_compare`, `shrink`). Test is fully hermetic — no
camera, no biometrics, no real subprocess calls.

Runs locally with no extra deps:
    python3 test/test_auth_clears_shakespeare.py
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


def drive_auth(initial_state: dict):
    """Run auth() against a stubbed environment with the given
    initial state.json. Returns (final_state, events, exit_code).

    Stubs:
      - _touchid_check → "ok"
      - capture_full   → creates dummy file at path, returns True
      - run_face_compare → returns a clean match
      - shrink         → creates dummy file at dst, no-op otherwise
    """
    tmpdir = Path(tempfile.mkdtemp(prefix="lz004_"))

    # Save originals so we can restore in finally.
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

        # Need at least one .json ref so the ref_count check passes.
        (fs.REF_DIR / "ref_synthetic.json").write_text("{}")

        # Pre-populate state.json with the requested initial state.
        fs.save_state(initial_state)

        # Stubs.
        fs._touchid_check = lambda **kwargs: "ok"

        def stub_capture_full(path):
            Path(path).write_bytes(b"x")
            return True
        fs.capture_full = stub_capture_full

        fs.run_face_compare = lambda *args, **kwargs: {
            "faces": 1,
            "match": True,
            "distance": 12.5,
        }

        def stub_shrink(src, dst, width=320):
            Path(dst).write_bytes(b"x")
        fs.shrink = stub_shrink

        # Run auth(). Suppress stdout to keep the test output
        # clean; auth() prints status lines that aren't load-
        # bearing for the contract being tested.
        exit_code = None
        with contextlib.redirect_stdout(io.StringIO()):
            try:
                fs.auth()
            except SystemExit as e:
                exit_code = e.code

        return fs.load_state(), read_log_events(fs.LOG_FILE), exit_code
    finally:
        for k, v in saved.items():
            setattr(fs, k, v)
        shutil.rmtree(tmpdir, ignore_errors=True)


# ── Branch 1: pre-Shakespeare-mode → cleared ───────────────────────

initial = {
    "mode": "shakespeare",
    "authenticated": False,
    "lockout_time": "2026-05-10T02:20:03Z",
    "lockout_distance": 1.02,
    "lockout_reason": "liveness_fail",
}
state, events, exit_code = drive_auth(initial)

# auth() should complete without sys.exit on the success path.
expect("shakespeare→clear: no exit", exit_code, None)

# Mode flipped back to "normal".
expect("shakespeare→clear: mode is normal",
       state.get("mode"), "normal")

# authenticated → True.
expect("shakespeare→clear: authenticated True",
       state.get("authenticated"), True)

# lockout_time + lockout_distance removed.
expect("shakespeare→clear: lockout_time popped",
       "lockout_time" in state, False)
expect("shakespeare→clear: lockout_distance popped",
       "lockout_distance" in state, False)

# auth_time + last_seen_owner refreshed (just check they're set).
if not state.get("auth_time"):
    print(f"FAIL shakespeare→clear: auth_time not set")
    sys.exit(1)
if not state.get("last_seen_owner"):
    print(f"FAIL shakespeare→clear: last_seen_owner not set")
    sys.exit(1)

# Log emits both shakespeare_cleared AND auth_ok.
ev = event_names(events)
expect("shakespeare→clear: shakespeare_cleared logged",
       "shakespeare_cleared" in ev, True)
expect("shakespeare→clear: auth_ok logged",
       "auth_ok" in ev, True)


# ── Branch 2: fresh auth (no prior Shakespeare) ────────────────────

initial = {"mode": "normal", "authenticated": False}
state, events, exit_code = drive_auth(initial)

expect("fresh: no exit", exit_code, None)
expect("fresh: mode is normal", state.get("mode"), "normal")
expect("fresh: authenticated True", state.get("authenticated"), True)

# No shakespeare_cleared event — was_shakespeare was False.
ev = event_names(events)
expect("fresh: no shakespeare_cleared",
       "shakespeare_cleared" in ev, False)
expect("fresh: auth_ok logged",
       "auth_ok" in ev, True)


# ── Branch 3: never-authenticated state ────────────────────────────

# Empty state.json (no mode key). auth() should still complete
# cleanly and set the fields.
initial = {}
state, events, exit_code = drive_auth(initial)
expect("empty: no exit", exit_code, None)
expect("empty: mode set to normal", state.get("mode"), "normal")
expect("empty: authenticated True", state.get("authenticated"), True)


# ── Branch 4: lockout_reason field also cleared ────────────────────

# Per LZ-013 (liveness probe), a liveness_fail lockout writes
# lockout_reason="liveness_fail" + liveness_delta to state. The
# auth() function pops lockout_time and lockout_distance but
# NOT lockout_reason / liveness_delta. Document this honestly:
# the test asserts what actually happens, not what we wish
# happened. Future work could clean these up; for now lock
# the current behavior so it's surfaced if it changes.

initial = {
    "mode": "shakespeare",
    "lockout_time": "...",
    "lockout_distance": 0.0,
    "lockout_reason": "liveness_fail",
    "liveness_delta": 0.0,
}
state, events, exit_code = drive_auth(initial)
expect("liveness-cleared: mode normal",
       state.get("mode"), "normal")
expect("liveness-cleared: lockout_time gone",
       "lockout_time" in state, False)
expect("liveness-cleared: lockout_distance gone",
       "lockout_distance" in state, False)
# Documenting: lockout_reason + liveness_delta currently
# linger after auth. If this changes, this assertion will trip
# and the test can be updated alongside the producer fix.
expect("liveness-cleared: lockout_reason still present (documented behavior)",
       state.get("lockout_reason"), "liveness_fail")
expect("liveness-cleared: liveness_delta still present (documented behavior)",
       state.get("liveness_delta"), 0.0)


print("PASS test_auth_clears_shakespeare.py")
