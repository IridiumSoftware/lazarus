#!/bin/bash
# test_oversight_tier2.sh — exercises LZ-021 (OverSight Tier 2
# allowlist + state-flip on non-allowlisted activation).
#
# Strategy: same HOME-redirection pattern as test_oversight_action.sh
# (LZ-011). Each subtest invokes oversight_action.sh with synthetic
# args and asserts on state.json + sentinel.log + oversight_events.jsonl.
#
# The test uses the running shell's pid (`$$`) as the synthetic
# process. `ps -o comm= -p $$` returns "bash", which is NOT in the
# default allowlist — so non-allowlisted on-events with $$ trigger
# Tier 2. To exercise the allowlisted path, the test creates a user
# allowlist file containing "bash".
#
# Runs locally:  bash test/test_oversight_tier2.sh
# Exit 0 on PASS, non-zero on FAIL.

set -u

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SCRIPT="$REPO_ROOT/oversight_action.sh"

if [ ! -x "$SCRIPT" ]; then
    echo "FAIL: $SCRIPT not executable"
    exit 1
fi

# Helper: read a JSON value out of state.json via python3.
read_state() {
    local home_dir="$1" key="$2"
    python3 -c "
import json, sys
try:
    d = json.load(open('$home_dir/.face_sentinel/state.json'))
    v = d.get('$key', '')
    print(v)
except Exception:
    print('')
" 2>/dev/null
}

# Helper: check sentinel.log for a specific event name.
sentinel_log_has_event() {
    local home_dir="$1" event_name="$2"
    local log_file="$home_dir/.face_sentinel/sentinel.log"
    [ -f "$log_file" ] || return 1
    grep -q "\"event\": \"$event_name\"" "$log_file"
}

# ── Subtest 1: on-event + non-allowlisted exec → Tier 2 fires ─────

echo "==Subtest 1: on-event + non-allowlisted exec (default)=="
TH=$(mktemp -d)
trap 'rm -rf "$TH"' EXIT

HOME="$TH" "$SCRIPT" -device camera -event on -process $$ -activeCount 1

# Tier 1: oversight_events.jsonl should exist with one record.
if [ ! -f "$TH/.face_sentinel/oversight_events.jsonl" ]; then
    echo "FAIL subtest 1: Tier 1 JSONL not created"; exit 1
fi
LINES=$(wc -l < "$TH/.face_sentinel/oversight_events.jsonl" | tr -d ' ')
if [ "$LINES" != "1" ]; then
    echo "FAIL subtest 1: expected 1 JSONL line, got $LINES"; exit 1
fi

# Tier 2: state.json should exist with mode=shakespeare.
mode=$(read_state "$TH" "mode")
if [ "$mode" != "shakespeare" ]; then
    echo "FAIL subtest 1: state.mode = $mode (expected 'shakespeare')"; exit 1
fi
reason=$(read_state "$TH" "lockout_reason")
if [ "$reason" != "oversight_unallowed" ]; then
    echo "FAIL subtest 1: state.lockout_reason = $reason"; exit 1
fi
authed=$(read_state "$TH" "authenticated")
if [ "$authed" != "False" ]; then
    echo "FAIL subtest 1: state.authenticated = $authed (expected False)"; exit 1
fi
# Oversight-specific fields populated.
alert_exec=$(read_state "$TH" "oversight_alert_executable")
if [ "$alert_exec" != "bash" ]; then
    echo "FAIL subtest 1: state.oversight_alert_executable = $alert_exec (expected 'bash')"; exit 1
fi

# Tier 2: sentinel.log should have the oversight_tier2_alert event.
if ! sentinel_log_has_event "$TH" "oversight_tier2_alert"; then
    echo "FAIL subtest 1: sentinel.log missing oversight_tier2_alert"
    cat "$TH/.face_sentinel/sentinel.log" 2>/dev/null
    exit 1
fi
echo "  ok"

# ── Subtest 2: on-event + allowlisted exec → no Tier 2 ────────────

echo "==Subtest 2: on-event + allowlisted exec (via user file)=="
TH=$(mktemp -d)
mkdir -p "$TH/.face_sentinel"
echo "bash" > "$TH/.face_sentinel/oversight_allowlist.txt"

HOME="$TH" "$SCRIPT" -device camera -event on -process $$ -activeCount 1

# Tier 1: JSONL exists.
if [ ! -f "$TH/.face_sentinel/oversight_events.jsonl" ]; then
    echo "FAIL subtest 2: Tier 1 JSONL not created"; exit 1
fi

# Tier 2: state.json should NOT exist (no Tier 2 trigger).
if [ -f "$TH/.face_sentinel/state.json" ]; then
    echo "FAIL subtest 2: state.json was created despite allowlisted exec"
    cat "$TH/.face_sentinel/state.json"; exit 1
fi

# Tier 2: sentinel.log should NOT have tier2_alert (or should not
# exist).
if sentinel_log_has_event "$TH" "oversight_tier2_alert"; then
    echo "FAIL subtest 2: sentinel.log has unexpected tier2_alert"; exit 1
fi
rm -rf "$TH"
echo "  ok"

# ── Subtest 3: off-event → no Tier 2 regardless of allowlist ──────

echo "==Subtest 3: off-event + non-allowlisted exec=="
TH=$(mktemp -d)

HOME="$TH" "$SCRIPT" -device camera -event off -process $$ -activeCount 0

# Tier 1 logged.
if [ ! -f "$TH/.face_sentinel/oversight_events.jsonl" ]; then
    echo "FAIL subtest 3: Tier 1 JSONL not created"; exit 1
fi
# But no Tier 2 state.json or alert.
if [ -f "$TH/.face_sentinel/state.json" ]; then
    echo "FAIL subtest 3: state.json created on off-event"; exit 1
fi
if sentinel_log_has_event "$TH" "oversight_tier2_alert"; then
    echo "FAIL subtest 3: sentinel.log has unexpected tier2_alert on off-event"; exit 1
fi
rm -rf "$TH"
echo "  ok"

# ── Subtest 4: commented allowlist line is ignored ────────────────

echo "==Subtest 4: '# bash' comment line does NOT allowlist 'bash'=="
TH=$(mktemp -d)
mkdir -p "$TH/.face_sentinel"
cat > "$TH/.face_sentinel/oversight_allowlist.txt" <<'ALLOW'
# This is a comment; the next line should NOT match
# bash
ALLOW

HOME="$TH" "$SCRIPT" -device camera -event on -process $$ -activeCount 1

# Since "bash" is commented out (not allowlisted), Tier 2 should
# fire.
mode=$(read_state "$TH" "mode")
if [ "$mode" != "shakespeare" ]; then
    echo "FAIL subtest 4: state.mode = $mode (expected 'shakespeare' — comment should not allowlist)"
    exit 1
fi
rm -rf "$TH"
echo "  ok"

# ── Subtest 5: blank lines in allowlist are ignored ───────────────

echo "==Subtest 5: blank lines in allowlist do not allowlist anything=="
TH=$(mktemp -d)
mkdir -p "$TH/.face_sentinel"
cat > "$TH/.face_sentinel/oversight_allowlist.txt" <<'ALLOW'


ALLOW

HOME="$TH" "$SCRIPT" -device camera -event on -process $$ -activeCount 1

mode=$(read_state "$TH" "mode")
if [ "$mode" != "shakespeare" ]; then
    echo "FAIL subtest 5: blank-only allowlist should not allowlist anything"
    exit 1
fi
rm -rf "$TH"
echo "  ok"

# ── Subtest 6: known default-allowlist entry (FaceTime) ───────────
#
# Use a synthetic test by creating a script that returns "FaceTime"
# from ps. Simpler: just rely on the python3 entry being in default,
# since we can use the current python3's pid. Find a python3
# process if one is running; skip if not.

echo "==Subtest 6: default allowlist contains 'python3'=="
TH=$(mktemp -d)

# Start a python3 sleep in the background to get a python3 pid.
python3 -c "import time; time.sleep(2)" &
PY_PID=$!
sleep 0.2  # let python3 process come up

# Verify the exec name is what we expect; otherwise skip gracefully.
PY_EXEC=$(ps -o comm= -p "$PY_PID" 2>/dev/null | xargs basename 2>/dev/null)
if [ "$PY_EXEC" = "python3" ] || [ "$PY_EXEC" = "Python" ]; then
    HOME="$TH" "$SCRIPT" -device camera -event on -process "$PY_PID" -activeCount 1
    if [ -f "$TH/.face_sentinel/state.json" ]; then
        echo "FAIL subtest 6: state.json created despite default-allowlisted python3"
        cat "$TH/.face_sentinel/state.json"
        wait "$PY_PID" 2>/dev/null || true
        exit 1
    fi
    echo "  ok (python3 default-allowlisted, no Tier 2 trigger)"
else
    echo "  skipped (could not get python3 process, got exec=$PY_EXEC)"
fi
wait "$PY_PID" 2>/dev/null || true
rm -rf "$TH"

echo ""
echo "PASS test_oversight_tier2.sh"
