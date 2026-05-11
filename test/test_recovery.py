"""
test_recovery.py — exercises LZ-027 (break-glass recovery from
persistent Shakespeare-mode lockout).

`face_sentinel.recover()` provides two recovery methods:
  1. Touch ID success (preferred).
  2. Recovery-token match against
     ~/.face_sentinel/recovery_token.txt.

Either method, on success, flips state.json to mode="normal"
and logs `recovery_used`. Neither available → exit 1.

This test drives `recover()` with stubbed `_touchid_check` and
tempdir-redirected `STATE_FILE` / `LOG_FILE` / `RECOVERY_TOKEN_FILE`.
Six branches covered:

  1. Touch ID succeeds            → state flipped, method=touchid
  2. Touch ID fails + no token    → exit 1, recovery_denied event
  3. Touch ID fails + bad token   → exit 1, token_mismatch event
  4. Touch ID fails + good token  → state flipped, method=token
  5. Already-normal pre-state     → success path (no-op-equivalent;
                                     refreshes auth_time but doesn't
                                     log a prior_mode=shakespeare clear)
  6. Token supplied but no saved  → exit 1, no_saved_token event

Runs locally with no extra deps:
    python3 test/test_recovery.py
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


def drive_recover(touchid_result: str,
                   initial_state: dict,
                   token_supplied: str = None,
                   saved_token: str = None):
    """Run recover() with `_touchid_check` stubbed to return
    `touchid_result`, optional saved recovery token written to
    the tempdir, optional CLI-supplied `token_supplied`.
    Returns (state, events, exit_code)."""
    tmpdir = Path(tempfile.mkdtemp(prefix="lz022_"))

    saved = {
        "REF_DIR": fs.REF_DIR,
        "CAP_DIR": fs.CAP_DIR,
        "LOG_FILE": fs.LOG_FILE,
        "STATE_FILE": fs.STATE_FILE,
        "BG_SNAPSHOT": fs.BG_SNAPSHOT,
        "RECOVERY_TOKEN_FILE": fs.RECOVERY_TOKEN_FILE,
        "_touchid_check": fs._touchid_check,
    }

    try:
        fs.REF_DIR = tmpdir / "reference"
        fs.CAP_DIR = tmpdir / "captures"
        fs.LOG_FILE = tmpdir / "sentinel.log"
        fs.STATE_FILE = tmpdir / "state.json"
        fs.BG_SNAPSHOT = tmpdir / "background.jpg"
        fs.RECOVERY_TOKEN_FILE = tmpdir / "recovery_token.txt"
        fs.REF_DIR.mkdir(parents=True, exist_ok=True)
        fs.CAP_DIR.mkdir(parents=True, exist_ok=True)

        if saved_token is not None:
            fs.RECOVERY_TOKEN_FILE.write_text(saved_token + "\n")
            fs.RECOVERY_TOKEN_FILE.chmod(0o600)

        fs.save_state(initial_state)
        fs._touchid_check = lambda **kwargs: touchid_result

        exit_code = None
        with contextlib.redirect_stdout(io.StringIO()):
            try:
                fs.recover(token=token_supplied)
            except SystemExit as e:
                exit_code = e.code

        state = fs.load_state() if fs.STATE_FILE.exists() else {}
        return state, read_log_events(fs.LOG_FILE), exit_code
    finally:
        for k, v in saved.items():
            setattr(fs, k, v)
        shutil.rmtree(tmpdir, ignore_errors=True)


SHAKESPEARE_STATE = {
    "mode": "shakespeare",
    "authenticated": False,
    "lockout_time": "2026-05-10T02:20:03Z",
    "lockout_distance": 0.0,
    "lockout_reason": "liveness_fail",
}


# ── Branch 1: Touch ID succeeds → recovery via touchid ────────────

state, events, exit_code = drive_recover("ok", SHAKESPEARE_STATE)
expect("touchid_ok: no exit", exit_code, None)
expect("touchid_ok: mode normal", state.get("mode"), "normal")
expect("touchid_ok: authenticated True",
       state.get("authenticated"), True)
expect("touchid_ok: lockout_time popped",
       "lockout_time" in state, False)
expect("touchid_ok: lockout_distance popped",
       "lockout_distance" in state, False)

ev = event_names(events)
expect("touchid_ok: recovery_used logged",
       "recovery_used" in ev, True)
recovery_event = [e for e in events if e.get("event") == "recovery_used"][0]
expect("touchid_ok: method=touchid",
       recovery_event.get("method"), "touchid")
expect("touchid_ok: prior_mode=shakespeare logged",
       recovery_event.get("prior_mode"), "shakespeare")


# ── Branch 2: Touch ID fails + no token supplied / no saved ───────

state, events, exit_code = drive_recover("nonzero", SHAKESPEARE_STATE)
expect("no_token: exit code 1", exit_code, 1)
expect("no_token: state.mode still shakespeare",
       state.get("mode"), "shakespeare")
ev = event_names(events)
expect("no_token: recovery_denied logged",
       "recovery_denied" in ev, True)
denied = [e for e in events if e.get("event") == "recovery_denied"][0]
expect("no_token: reason=no_method_available",
       denied.get("reason"), "no_method_available")


# ── Branch 3: Touch ID fails + bad token (no saved token) ─────────

state, events, exit_code = drive_recover("unavailable",
                                          SHAKESPEARE_STATE,
                                          token_supplied="ff" * 32)
expect("bad_token_no_saved: exit code 1", exit_code, 1)
expect("bad_token_no_saved: state.mode still shakespeare",
       state.get("mode"), "shakespeare")
ev = event_names(events)
denied = [e for e in events if e.get("event") == "recovery_denied"]
expect("bad_token_no_saved: 1 recovery_denied event",
       len(denied), 1)
expect("bad_token_no_saved: reason=token_supplied_but_none_saved",
       denied[0].get("reason"), "token_supplied_but_none_saved")


# ── Branch 4: Touch ID fails + bad token (saved token mismatches) ─

state, events, exit_code = drive_recover("nonzero",
                                          SHAKESPEARE_STATE,
                                          token_supplied="aa" * 32,
                                          saved_token="bb" * 32)
expect("token_mismatch: exit code 1", exit_code, 1)
expect("token_mismatch: state.mode still shakespeare",
       state.get("mode"), "shakespeare")
ev = event_names(events)
denied = [e for e in events if e.get("event") == "recovery_denied"]
expect("token_mismatch: 1 recovery_denied event",
       len(denied), 1)
expect("token_mismatch: reason=token_mismatch",
       denied[0].get("reason"), "token_mismatch")


# ── Branch 5: Touch ID fails + good token → recovery via token ────

GOOD_TOKEN = "cd" * 32
state, events, exit_code = drive_recover("nonzero",
                                          SHAKESPEARE_STATE,
                                          token_supplied=GOOD_TOKEN,
                                          saved_token=GOOD_TOKEN)
expect("good_token: no exit", exit_code, None)
expect("good_token: mode normal", state.get("mode"), "normal")
expect("good_token: authenticated True",
       state.get("authenticated"), True)
ev = event_names(events)
recovery_event = [e for e in events if e.get("event") == "recovery_used"][0]
expect("good_token: method=token",
       recovery_event.get("method"), "token")
expect("good_token: prior_mode=shakespeare logged",
       recovery_event.get("prior_mode"), "shakespeare")


# ── Branch 6: token whitespace insensitivity ──────────────────────

# Saved token file might end with "\n" or trailing whitespace.
# recover() should strip and still match.
state, events, exit_code = drive_recover("nonzero",
                                          SHAKESPEARE_STATE,
                                          token_supplied="  " + GOOD_TOKEN + "  ",
                                          saved_token=GOOD_TOKEN)
expect("good_token_whitespace: no exit", exit_code, None)
expect("good_token_whitespace: mode normal",
       state.get("mode"), "normal")


# ── Branch 7: already-normal state + Touch ID succeeds ─────────────

# Edge case — running --recover when not actually locked out.
# Behavior: still runs through, sets authenticated=True,
# logs recovery_used with prior_mode=normal. The recovery_used
# event with prior_mode=normal is the signal that this was a
# false alarm / paranoid use.
NORMAL_STATE = {"mode": "normal", "authenticated": False}
state, events, exit_code = drive_recover("ok", NORMAL_STATE)
expect("already_normal: no exit", exit_code, None)
expect("already_normal: mode normal", state.get("mode"), "normal")
recovery_event = [e for e in events if e.get("event") == "recovery_used"][0]
expect("already_normal: prior_mode=normal logged",
       recovery_event.get("prior_mode"), "normal")


# ── Default-parameter check ───────────────────────────────────────

import inspect  # noqa: E402
sig = inspect.signature(fs.recover)
token_param = sig.parameters.get("token")
if token_param is None:
    print("FAIL: recover() missing token parameter")
    sys.exit(1)
expect("recover token default is None",
       token_param.default, None)


# ── RECOVERY_TOKEN_FILE path matches BASE_DIR ─────────────────────

# Lock the path so a refactor that moves recovery_token.txt
# elsewhere surfaces.
expected_path = str(fs.BASE_DIR / "recovery_token.txt")
# After the test restored fs.RECOVERY_TOKEN_FILE, this should
# be the production path.
expect("RECOVERY_TOKEN_FILE points at BASE_DIR/recovery_token.txt",
       str(fs.RECOVERY_TOKEN_FILE), expected_path)


print("PASS test_recovery.py")
