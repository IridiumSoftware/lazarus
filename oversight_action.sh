#!/bin/bash
# oversight_action.sh — OverSight Action handler.
#
# OverSight invokes this script on every camera/mic event with:
#   -device <camera|microphone>  -event <on|off>  -process <pid>  -activeCount <N>
# (-process is only set on activation events.)
#
# Tier 1 (LZ-011): forensic logging.
#   Every event is appended as one JSONL record to
#   ~/.face_sentinel/oversight_events.jsonl.
#
# Tier 2 (LZ-021): allowlist-driven state-flip on non-allowlisted
# activation.
#   On an `on`-event whose process executable is NOT in the
#   allowlist, the script ALSO writes state.json with
#   mode="shakespeare", lockout_reason="oversight_unallowed", and
#   appends an "oversight_tier2_alert" record to sentinel.log.
#   The next /lazarus invocation reads the flipped state and
#   shifts into Shakespeare-mode refusal.
#
# The allowlist is the union of:
#   - the built-in default (imagesnap, python3, FaceTime, etc.)
#   - any process executable names in ~/.face_sentinel/oversight_allowlist.txt
#     (one per line; lines starting with `#` are ignored)
#
# Tier 2b (screen lock via `pmset displaysleepnow`) is deliberately
# NOT included in this script. Screen-lock-on-unallowlisted is an
# aggressive response best deferred until an opt-in flag is
# designed; the spec acknowledges this in LZ-021's Notes.

set -u

LOG_DIR="$HOME/.face_sentinel"
LOG_FILE="$LOG_DIR/oversight_events.jsonl"
STATE_FILE="$LOG_DIR/state.json"
SENTINEL_LOG="$LOG_DIR/sentinel.log"
ALLOWLIST_FILE="$LOG_DIR/oversight_allowlist.txt"
mkdir -p "$LOG_DIR"

# Built-in default allowlist. Process executables (matching the
# `ps -o comm=` shape) that legitimately access camera/mic on a
# typical macOS dev box. Users can extend via ALLOWLIST_FILE.
DEFAULT_ALLOWLIST=(
    "imagesnap"                # face_sentinel's camera tool
    "python3"                  # face_sentinel.py runs via python3
    "Python"                   # python.app / Python.framework alias
    "FaceTime"
    "zoom.us"
    "Photo Booth"
    "Photos"
    "Safari"                   # WebRTC
    "coreaudiod"               # macOS audio daemon
    "VTDecoderXPCService"      # macOS video subsystem
    "AppleCameraAssistant"     # macOS camera daemon
    "screencaptureui"          # Screenshot / screen recording UI
)

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
    # `ps -o comm=` can return a path; strip to basename for
    # allowlist matching.
    proc_executable=$(basename "$proc_executable" 2>/dev/null || true)
fi

ts=$(date -u +%Y-%m-%dT%H:%M:%SZ)

# ── Tier 1: append JSONL record ────────────────────────────────────

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

# ── Tier 2: allowlist-driven state-flip ────────────────────────────

# Only on-events trigger Tier 2. Off-events are just session-end
# bookkeeping and don't represent a threat.
if [ "$event" != "on" ] || [ -z "$proc_executable" ]; then
    exit 0
fi

# Check allowlist membership (built-in + user file).
is_allowlisted() {
    local exe="$1"
    # Built-in default.
    for allowed in "${DEFAULT_ALLOWLIST[@]}"; do
        if [ "$exe" = "$allowed" ]; then
            return 0
        fi
    done
    # User file (optional). One executable name per line; `#`
    # comments and blank lines are ignored.
    if [ -f "$ALLOWLIST_FILE" ]; then
        while IFS= read -r line; do
            # Trim whitespace, skip comments + blanks.
            line=$(echo "$line" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
            case "$line" in
                ""|"#"*) continue ;;
            esac
            if [ "$exe" = "$line" ]; then
                return 0
            fi
        done < "$ALLOWLIST_FILE"
    fi
    return 1
}

if is_allowlisted "$proc_executable"; then
    # Allowlisted — Tier 1 logging only. Done.
    exit 0
fi

# Non-allowlisted on-event: trigger Tier 2 state-flip.
/usr/bin/python3 - \
    "$ts" "$device" "$pid" "$proc_executable" "$proc_command" \
    "$STATE_FILE" "$SENTINEL_LOG" <<'PY'
import json, os, sys
from pathlib import Path
ts, device, pid, executable, command, state_path, sentinel_log = sys.argv[1:]

# Load existing state.json (or start empty).
state = {}
if os.path.exists(state_path):
    try:
        with open(state_path) as f:
            state = json.load(f)
    except Exception:
        state = {}

# Tier 2 state-flip. Mirrors the liveness_fail / mismatch paths in
# face_sentinel.check_once: mode="shakespeare", authenticated=False,
# lockout_time + lockout_reason set, plus oversight-specific fields
# (executable + pid) so a future inspector can identify the
# offending process.
state["mode"] = "shakespeare"
state["authenticated"] = False
state["lockout_time"] = ts
state["lockout_reason"] = "oversight_unallowed"
state["oversight_alert_executable"] = executable
state["oversight_alert_pid"] = pid
state["oversight_alert_device"] = device

with open(state_path, "w") as f:
    json.dump(state, f, indent=2)

# Append a tier2_alert event to sentinel.log (matching the JSONL
# format the face_sentinel daemon uses for its own events).
with open(sentinel_log, "a") as f:
    f.write(json.dumps({
        "timestamp": ts,
        "event": "oversight_tier2_alert",
        "device": device,
        "pid": pid,
        "executable": executable,
        "command": command,
    }) + "\n")
PY
