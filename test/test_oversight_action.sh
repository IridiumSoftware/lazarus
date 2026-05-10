#!/bin/bash
# test_oversight_action.sh — exercises LZ-011 (oversight Tier 1
# forensic logging).
#
# Strategy: redirect HOME to a temporary directory, invoke
# oversight_action.sh with a synthetic OverSight argument set,
# and assert that exactly one well-formed JSONL record was
# appended to the redirected log path.
#
# Runs locally on macOS: bash test/test_oversight_action.sh
# Exit 0 on PASS, non-zero on FAIL.

set -u

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SCRIPT="$REPO_ROOT/oversight_action.sh"

if [ ! -x "$SCRIPT" ]; then
    echo "FAIL: $SCRIPT is not executable"
    exit 1
fi

TEST_HOME=$(mktemp -d)
trap 'rm -rf "$TEST_HOME"' EXIT

LOG_FILE="$TEST_HOME/.face_sentinel/oversight_events.jsonl"

# Synthetic OverSight invocation: camera turned on by this very
# shell's PID. The script will run `ps -o ...` against $$, which
# is a real process, so executable/command will populate.
HOME="$TEST_HOME" "$SCRIPT" \
    -device camera \
    -event on \
    -process $$ \
    -activeCount 1

if [ ! -f "$LOG_FILE" ]; then
    echo "FAIL: log file not created at $LOG_FILE"
    exit 1
fi

LINE_COUNT=$(wc -l < "$LOG_FILE" | tr -d ' ')
if [ "$LINE_COUNT" != "1" ]; then
    echo "FAIL: expected 1 log line, got $LINE_COUNT"
    cat "$LOG_FILE"
    exit 1
fi

# Validate JSON shape.
python3 - "$LOG_FILE" <<'PY'
import json, sys
with open(sys.argv[1]) as f:
    record = json.loads(f.read().strip())

required = {"ts", "device", "event", "pid", "activeCount", "executable", "command"}
missing = required - record.keys()
if missing:
    print(f"FAIL: missing keys: {sorted(missing)}")
    sys.exit(1)

if record["device"] != "camera":
    print(f"FAIL: device mismatch: {record['device']!r}")
    sys.exit(1)
if record["event"] != "on":
    print(f"FAIL: event mismatch: {record['event']!r}")
    sys.exit(1)
if record["activeCount"] != "1":
    print(f"FAIL: activeCount mismatch: {record['activeCount']!r}")
    sys.exit(1)
if not record["ts"].endswith("Z"):
    print(f"FAIL: ts not UTC-suffixed: {record['ts']!r}")
    sys.exit(1)
PY

PYRC=$?
if [ "$PYRC" != "0" ]; then
    exit 1
fi

# Second invocation: confirm append-only (line count goes to 2).
HOME="$TEST_HOME" "$SCRIPT" \
    -device microphone \
    -event off \
    -activeCount 0

LINE_COUNT=$(wc -l < "$LOG_FILE" | tr -d ' ')
if [ "$LINE_COUNT" != "2" ]; then
    echo "FAIL: expected 2 log lines after second invocation, got $LINE_COUNT"
    exit 1
fi

echo "PASS test_oversight_action.sh"
