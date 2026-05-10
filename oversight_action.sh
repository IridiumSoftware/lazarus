#!/bin/bash
# oversight_action.sh — OverSight Action handler (Tier 1: forensic logging only).
#
# OverSight invokes this script on every camera/mic event with:
#   -device <camera|microphone>  -event <on|off>  -process <pid>  -activeCount <N>
# (-process is only set on activation events.)
#
# Behavior: appends one JSONL record per event to
#   ~/.face_sentinel/oversight_events.jsonl
#
# No active response. Watch the log for a week; if the only `executable`
# observed is `imagesnap`, the foundation is clean and Tier 2 (auto-lockdown
# on non-allowlisted activation) can be layered on top.

set -u

LOG_DIR="$HOME/.face_sentinel"
LOG_FILE="$LOG_DIR/oversight_events.jsonl"
mkdir -p "$LOG_DIR"

device=""
event=""
pid=""
active_count=""

while [ $# -gt 0 ]; do
    case "$1" in
        -device)      device="${2:-}";       shift 2 ;;
        -event)       event="${2:-}";        shift 2 ;;
        -process)     pid="${2:-}";          shift 2 ;;
        -activeCount) active_count="${2:-}"; shift 2 ;;
        *) shift ;;
    esac
done

proc_command=""
proc_executable=""
if [ -n "$pid" ]; then
    proc_command=$(ps -o command= -p "$pid" 2>/dev/null || true)
    proc_executable=$(ps -o comm= -p "$pid" 2>/dev/null || true)
fi

ts=$(date -u +%Y-%m-%dT%H:%M:%SZ)

/usr/bin/python3 - \
    "$ts" "$device" "$event" "$pid" "$active_count" \
    "$proc_command" "$proc_executable" "$LOG_FILE" <<'PY'
import json, sys
ts, device, event, pid, active_count, command, executable, logfile = sys.argv[1:]
record = {
    "ts": ts,
    "device": device,
    "event": event,
    "pid": pid,
    "activeCount": active_count,
    "executable": executable,
    "command": command,
}
with open(logfile, "a") as f:
    f.write(json.dumps(record) + "\n")
PY
