"""
test_watch_state_transitions.py — exercises LZ-007 (watch-loop
state transitions in check_once).

Tests all 8 branches of check_once's state machine:

  A — no_face + last_seen_owner + bg unchanged
  B — no_face + last_seen_owner + bg shifted
  C — no_face + no last_seen_owner
  D — is_match + live
  E — is_match + not live (liveness_fail → Shakespeare)
  F — uncertain
  G — mismatch + distance below LOCK_THRESHOLD
  H — mismatch + distance above LOCK_THRESHOLD (locks screen)

Each branch is exercised by:
- Redirecting REF_DIR / CAP_DIR / LOG_FILE / STATE_FILE /
  BG_SNAPSHOT to a per-test tempdir.
- Module-patching capture_full, run_face_compare, liveness_check,
  backgrounds_similar, lock_screen with stubs that return canned
  responses.
- Calling check_once() once.
- Asserting on state.json contents and log entries.

Runs locally with no extra deps:
    python3 test/test_watch_state_transitions.py
Exit 0 on PASS, non-zero on FAIL.
"""

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


def make_stub_capture_full(success=True):
    def _stub(path):
        if success:
            Path(path).write_bytes(b"x")
            return True
        return False
    return _stub


def make_stub_face_compare(response):
    def _stub(*args, **kwargs):
        return response
    return _stub


def make_stub_liveness(live, delta=0.0, reason="ok"):
    def _stub(first_capture):
        return {"live": live, "delta": delta, "reason": reason}
    return _stub


def make_stub_backgrounds_similar(similar):
    def _stub(a, b):
        return similar
    return _stub


def stub_shrink(src, dst, width=320):
    """Stub for the sips-driven downsizer: just creates a dummy
    file at the destination path. Real sips would fail on our
    dummy capture bytes, so we need this for cap_lowres to exist
    for the downstream bg_shift / cleanup checks."""
    Path(dst).write_bytes(b"x")


_lock_screen_calls = []


def stub_lock_screen():
    _lock_screen_calls.append(True)


def read_log_events(log_path: Path) -> list:
    """Parse log.jsonl into a list of event dicts."""
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


def run_branch(name, *, initial_state, face_compare_response,
               capture_success=True,
               liveness_live=True, liveness_delta=0.0, liveness_reason="ok",
               bg_similar=True, bg_snapshot_exists=True,
               cap_dir_should_have_capture=False):
    """Drive check_once with the given stubs and return
    (state, events, lock_screen_was_called)."""
    tmpdir = Path(tempfile.mkdtemp(prefix="lz007_"))

    # Save originals so we can restore in finally.
    saved = {
        "REF_DIR": fs.REF_DIR,
        "CAP_DIR": fs.CAP_DIR,
        "LOG_FILE": fs.LOG_FILE,
        "STATE_FILE": fs.STATE_FILE,
        "BG_SNAPSHOT": fs.BG_SNAPSHOT,
        "capture_full": fs.capture_full,
        "run_face_compare": fs.run_face_compare,
        "liveness_check": fs.liveness_check,
        "backgrounds_similar": fs.backgrounds_similar,
        "lock_screen": fs.lock_screen,
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
        if bg_snapshot_exists:
            fs.BG_SNAPSHOT.write_bytes(b"bg")

        fs.save_state(initial_state)

        fs.capture_full = make_stub_capture_full(success=capture_success)
        fs.run_face_compare = make_stub_face_compare(face_compare_response)
        fs.liveness_check = make_stub_liveness(
            live=liveness_live, delta=liveness_delta, reason=liveness_reason)
        fs.backgrounds_similar = make_stub_backgrounds_similar(bg_similar)
        fs.shrink = stub_shrink

        _lock_screen_calls.clear()
        fs.lock_screen = stub_lock_screen

        fs.check_once()

        final_state = fs.load_state()
        events = read_log_events(fs.LOG_FILE)
        lock_called = len(_lock_screen_calls) > 0
        captures = list(fs.CAP_DIR.glob("watch_*.jpg"))
        if cap_dir_should_have_capture:
            expect(f"{name}: capture present", len(captures) >= 1, True)
        return final_state, events, lock_called
    finally:
        for k, v in saved.items():
            setattr(fs, k, v)
        shutil.rmtree(tmpdir, ignore_errors=True)


# ── Branch A: no_face + owner seen + bg unchanged ──────────────────

state, events, lock_called = run_branch(
    "A",
    initial_state={"authenticated": True,
                   "last_seen_owner": "2026-05-10T00:00:00"},
    face_compare_response={"faces": 0},
    bg_similar=True,
)
# State unchanged (we still trust the owner walked away).
expect("A: state.last_seen_owner unchanged",
       state.get("last_seen_owner"), "2026-05-10T00:00:00")
expect("A: state.mode not shakespeare",
       state.get("mode"), None)
# One no_face event with owner_walked_away note. NO bg_shift.
ev = event_names(events)
expect("A: no_face logged", "no_face" in ev, True)
expect("A: no bg_shift", "bg_shift" not in ev, True)
walk_event = [e for e in events if e.get("event") == "no_face"][0]
expect("A: walked_away note",
       walk_event.get("note"), "owner_walked_away")


# ── Branch B: no_face + owner seen + bg shifted ────────────────────

state, events, lock_called = run_branch(
    "B",
    initial_state={"authenticated": True,
                   "last_seen_owner": "2026-05-10T00:00:00"},
    face_compare_response={"faces": 0},
    bg_similar=False,
)
ev = event_names(events)
expect("B: no_face logged", "no_face" in ev, True)
expect("B: bg_shift logged", "bg_shift" in ev, True)


# ── Branch C: no_face + no owner seen ──────────────────────────────

state, events, lock_called = run_branch(
    "C",
    initial_state={},  # no last_seen_owner
    face_compare_response={"faces": 0},
)
ev = event_names(events)
no_face_evs = [e for e in events if e.get("event") == "no_face"]
expect("C: no_face logged", len(no_face_evs), 1)
expect("C: owner_never_seen note",
       no_face_evs[0].get("note"), "owner_never_seen")
expect("C: no bg_shift", "bg_shift" not in ev, True)


# ── Branch D: is_match + live ──────────────────────────────────────

state, events, lock_called = run_branch(
    "D",
    initial_state={"authenticated": True,
                   "last_seen_owner": "2026-05-09T00:00:00"},
    face_compare_response={"faces": 1, "match": True, "uncertain": False,
                           "distance": 12.5},
    liveness_live=True, liveness_delta=0.018, liveness_reason="ok",
)
# state.last_seen_owner should be refreshed (not the stale 2026-05-09).
expect("D: last_seen_owner refreshed (not stale)",
       state.get("last_seen_owner") != "2026-05-09T00:00:00", True)
# No Shakespeare mode.
expect("D: mode not shakespeare",
       state.get("mode"), None)
ev = event_names(events)
expect("D: match_ok logged", "match_ok" in ev, True)
match_ok = [e for e in events if e.get("event") == "match_ok"][0]
expect("D: match_ok carries liveness_delta",
       "liveness_delta" in match_ok, True)


# ── Branch E: is_match + not live (liveness_fail) ─────────────────

state, events, lock_called = run_branch(
    "E",
    initial_state={"authenticated": True,
                   "last_seen_owner": "2026-05-10T00:00:00"},
    face_compare_response={"faces": 1, "match": True, "uncertain": False,
                           "distance": 12.5},
    liveness_live=False, liveness_delta=0.0, liveness_reason="static_likely",
)
expect("E: mode is shakespeare",
       state.get("mode"), "shakespeare")
expect("E: lockout_reason is liveness_fail",
       state.get("lockout_reason"), "liveness_fail")
expect("E: authenticated cleared",
       state.get("authenticated"), False)
ev = event_names(events)
expect("E: liveness_fail logged", "liveness_fail" in ev, True)
expect("E: shakespeare_mode logged", "shakespeare_mode" in ev, True)


# ── Branch F: uncertain ────────────────────────────────────────────

state, events, lock_called = run_branch(
    "F",
    initial_state={"authenticated": True,
                   "last_seen_owner": "2026-05-10T00:00:00"},
    face_compare_response={"faces": 1, "match": False, "uncertain": True,
                           "distance": 22.0},
)
# Uncertain doesn't change state.
expect("F: mode not shakespeare",
       state.get("mode"), None)
expect("F: authenticated unchanged",
       state.get("authenticated"), True)
ev = event_names(events)
expect("F: uncertain logged", "uncertain" in ev, True)


# ── Branch G: mismatch below LOCK_THRESHOLD ────────────────────────

state, events, lock_called = run_branch(
    "G",
    initial_state={"authenticated": True,
                   "last_seen_owner": "2026-05-10T00:00:00"},
    face_compare_response={"faces": 1, "match": False, "uncertain": False,
                           "distance": 30.0},  # < LOCK_THRESHOLD (35)
)
expect("G: mode is shakespeare",
       state.get("mode"), "shakespeare")
expect("G: authenticated cleared",
       state.get("authenticated"), False)
expect("G: lock_screen NOT called", lock_called, False)
ev = event_names(events)
expect("G: MISMATCH logged", "MISMATCH" in ev, True)
expect("G: no LOCK event", "LOCK" not in ev, True)


# ── Branch H: mismatch above LOCK_THRESHOLD ────────────────────────

state, events, lock_called = run_branch(
    "H",
    initial_state={"authenticated": True,
                   "last_seen_owner": "2026-05-10T00:00:00"},
    face_compare_response={"faces": 1, "match": False, "uncertain": False,
                           "distance": 40.0},  # > LOCK_THRESHOLD (35)
)
expect("H: mode is shakespeare",
       state.get("mode"), "shakespeare")
expect("H: lock_screen called", lock_called, True)
ev = event_names(events)
expect("H: LOCK event logged", "LOCK" in ev, True)


# ── Capture-fail early return ──────────────────────────────────────

state, events, lock_called = run_branch(
    "capture_fail",
    initial_state={"authenticated": True},
    face_compare_response={"faces": 0},  # won't be reached
    capture_success=False,
)
ev = event_names(events)
expect("capture_fail: capture_fail event logged",
       "capture_fail" in ev, True)
# No downstream events.
expect("capture_fail: no match_ok",
       "match_ok" not in ev, True)


# ── match_error early return ───────────────────────────────────────

state, events, lock_called = run_branch(
    "match_error",
    initial_state={"authenticated": True},
    face_compare_response={"error": "stub: face_compare failed"},
)
ev = event_names(events)
expect("match_error: match_error event logged",
       "match_error" in ev, True)
expect("match_error: no match_ok",
       "match_ok" not in ev, True)


# ── LOCK_THRESHOLD value lock ──────────────────────────────────────

expect("LOCK_THRESHOLD value", fs.LOCK_THRESHOLD, 35.0)


print("PASS test_watch_state_transitions.py")
