"""
face_sentinel.py — Visual presence verification for Lazarus
═══════════════════════════════════════════════════════════

Threat model:
    1. Session opens with --auth: face match = "owner confirmed"
       Background snapshot taken as environment baseline.
    2. Passive --watch: periodic checks after auth.
       - face == owner → fine
       - no face → fine (walked away), BUT only if owner was last seen
       - face != owner → Shakespeare mode (Claude speaks only in Bard)
       - no face + background radically different → note (laptop moved)
    3. Remote --peek: Tailscale in, trigger one capture, see who's at the desk.

Camera policy:
    - Detect on FULL resolution (better accuracy), store LOW resolution
    - Reference images: ~15-30KB each, max 50, oldest auto-pruned
    - Watch captures: matched ones deleted after 24h, mismatches kept 7 days
    - Background snapshots: one stored per auth session, overwritten next session
"""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────

BASE_DIR = Path.home() / ".face_sentinel"
REF_DIR = BASE_DIR / "reference"
CAP_DIR = BASE_DIR / "captures"
LOG_FILE = BASE_DIR / "sentinel.log"
STATE_FILE = BASE_DIR / "state.json"
BG_SNAPSHOT = BASE_DIR / "background.jpg"
COMPARE_BIN = Path(__file__).parent / "face_compare"

# ── Config ─────────────────────────────────────────────────────────

WATCH_INTERVAL = 90          # Seconds between checks
MAX_REFERENCES = 50
MATCH_RETAIN_HOURS = 24
MISMATCH_RETAIN_DAYS = 7
MATCH_THRESHOLD = 18.0       # Vision distance: below = match
UNCERTAIN_THRESHOLD = 25.0   # Between match and this = uncertain
LOCK_THRESHOLD = 35.0        # Above this = lock screen
BG_CHANGE_THRESHOLD = 0.15   # Pixel diff ratio for "background changed"


def ensure_dirs():
    REF_DIR.mkdir(parents=True, exist_ok=True)
    CAP_DIR.mkdir(parents=True, exist_ok=True)


def log_event(event: dict):
    event["timestamp"] = datetime.now().isoformat()
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(event) + "\n")


def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {}


def save_state(state: dict):
    STATE_FILE.write_text(json.dumps(state, indent=2))


# ── Camera ─────────────────────────────────────────────────────────

def capture_full(output_path: str) -> bool:
    """Capture full-res image (for detection accuracy)."""
    try:
        result = subprocess.run(
            ["imagesnap", "-w", "2.0", output_path],
            capture_output=True, text=True, timeout=15
        )
        return result.returncode == 0 and os.path.exists(output_path)
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def shrink(src: str, dst: str, width: int = 320):
    """Downscale to low-res for storage."""
    subprocess.run(
        ["sips", "--resampleWidth", str(width), src, "--out", dst],
        capture_output=True, timeout=10
    )


def run_face_compare(cmd: str, image_path: str, dir_path: str = None) -> dict:
    args = [str(COMPARE_BIN), cmd, image_path]
    if dir_path:
        args.append(dir_path)
    try:
        result = subprocess.run(args, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            return {"error": f"exit {result.returncode}: {result.stderr.strip()}"}
        return json.loads(result.stdout.strip())
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError) as e:
        return {"error": str(e)}


# ── Background comparison (simple pixel diff) ─────────────────────

def backgrounds_similar(img_a: str, img_b: str) -> bool:
    """Quick check: are two images roughly the same scene?
    Uses tiny-resolution pixel comparison. Not fancy, just catches
    'laptop is now in a completely different room' scenarios.
    """
    import tempfile
    size = "32"

    def to_tiny(src):
        dst = tempfile.mktemp(suffix=".bmp")
        subprocess.run(
            ["sips", "--resampleWidth", size, "--resampleHeight", size,
             "-s", "format", "bmp", src, "--out", dst],
            capture_output=True, timeout=10
        )
        return dst

    tiny_a = to_tiny(img_a)
    tiny_b = to_tiny(img_b)

    if not os.path.exists(tiny_a) or not os.path.exists(tiny_b):
        return True  # Can't compare, fail open

    bytes_a = open(tiny_a, "rb").read()
    bytes_b = open(tiny_b, "rb").read()
    os.remove(tiny_a)
    os.remove(tiny_b)

    if len(bytes_a) != len(bytes_b):
        return False

    diffs = sum(1 for a, b in zip(bytes_a, bytes_b) if a != b)
    ratio = diffs / len(bytes_a)
    return ratio < BG_CHANGE_THRESHOLD


# ── Auth (session opener) ─────────────────────────────────────────

def auth():
    """Session authentication: face match + background snapshot."""
    ensure_dirs()

    ref_count = len(list(REF_DIR.glob("*.json")))
    if ref_count == 0:
        print("No references enrolled. Run --enroll first to build your face set.")
        sys.exit(1)

    # Face capture + match
    print("Capturing face...")
    tmp_full = "/tmp/face_sentinel_auth.jpg"
    if not capture_full(tmp_full):
        print("ERROR: Camera capture failed.")
        sys.exit(1)

    result = run_face_compare("match", tmp_full, str(REF_DIR))
    if "error" in result:
        print(f"ERROR: {result['error']}")
        sys.exit(1)

    if result.get("faces", 0) == 0:
        print("No face detected. Make sure you're in frame.")
        os.remove(tmp_full)
        sys.exit(1)

    if not result.get("match", False):
        dist = result.get("distance", "?")
        print(f"FACE MISMATCH. Distance: {dist}. Auth denied.")
        log_event({"event": "auth_fail", "distance": dist})
        os.remove(tmp_full)
        sys.exit(1)

    # Save background snapshot
    shrink(tmp_full, str(BG_SNAPSHOT), width=320)
    os.remove(tmp_full)

    state = load_state()
    was_shakespeare = state.get("mode") == "shakespeare"
    state["authenticated"] = True
    state["auth_time"] = datetime.now().isoformat()
    state["last_seen_owner"] = datetime.now().isoformat()
    state["mode"] = "normal"
    state.pop("lockout_time", None)
    state.pop("lockout_distance", None)
    save_state(state)

    dist = result.get("distance", "?")
    if was_shakespeare:
        print(f"AUTH OK. Shakespeare mode cleared. Welcome back.")
        log_event({"event": "shakespeare_cleared", "distance": dist})
    else:
        print(f"AUTH OK. Face distance: {dist}. Background snapshot saved.")
    print("Session authenticated. Run --watch to start passive monitoring.")
    log_event({"event": "auth_ok", "distance": dist})


# ── Enroll ─────────────────────────────────────────────────────────

def enroll():
    """Capture and enroll a reference image."""
    ensure_dirs()
    tmp_full = "/tmp/face_sentinel_enroll.jpg"

    print("Capturing reference image (hold still, look at camera)...")
    if not capture_full(tmp_full):
        print("ERROR: Camera capture failed. Is imagesnap installed?")
        sys.exit(1)

    detect = run_face_compare("detect", tmp_full)
    if "error" in detect:
        print(f"ERROR: {detect['error']}")
        os.remove(tmp_full)
        sys.exit(1)

    if detect.get("faces", 0) != 1:
        print(f"Need exactly 1 face, detected {detect.get('faces', 0)}. Try again.")
        os.remove(tmp_full)
        sys.exit(1)

    ref_ts = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    ref_image = str(REF_DIR / f"ref_{ref_ts}.jpg")
    shrink(tmp_full, ref_image, width=480)

    result = run_face_compare("enroll", tmp_full, str(REF_DIR))
    os.remove(tmp_full)

    if "error" in result:
        print(f"ERROR: {result['error']}")
        sys.exit(1)

    # Align jpg filename with Swift-generated metadata filename
    enrolled_name = result.get("enrolled", "")
    if enrolled_name:
        enrolled_stem = Path(enrolled_name).stem
        expected_jpg = REF_DIR / f"{enrolled_stem}.jpg"
        if not expected_jpg.exists() and os.path.exists(ref_image):
            os.rename(ref_image, str(expected_jpg))

    ref_count = len(list(REF_DIR.glob("*.json")))
    print(f"Enrolled. {result.get('elements', '?')} features extracted.")
    print(f"Total references: {ref_count}/{MAX_REFERENCES}")
    log_event({"event": "enroll", "ref": result.get("enrolled", ""), "refs_total": ref_count})

    if ref_count > MAX_REFERENCES:
        prune_oldest()


def prune_oldest():
    metas = sorted(REF_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime)
    to_remove = len(metas) - MAX_REFERENCES
    for meta_path in metas[:to_remove]:
        stem = meta_path.stem
        for f in REF_DIR.glob(f"{stem}.*"):
            f.unlink()
        print(f"  Pruned: {meta_path.name}")
    log_event({"event": "prune_refs", "removed": to_remove})


# ── Watch ──────────────────────────────────────────────────────────

def watch(interval: int):
    """Daemon mode: periodic capture + match after auth."""
    ensure_dirs()

    state = load_state()
    if not state.get("authenticated"):
        print("Session not authenticated. Run --auth first.")
        sys.exit(1)

    ref_count = len(list(REF_DIR.glob("*.json")))
    print(f"Sentinel active. {ref_count} refs. Interval: {interval}s.")
    print("Ctrl+C to stop.\n")
    log_event({"event": "watch_start", "refs": ref_count, "interval": interval})

    try:
        while True:
            check_once()
            prune_captures()
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nSentinel stopped.")
        log_event({"event": "watch_stop"})


def check_once():
    """Single capture + evaluation."""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    tmp_full = f"/tmp/face_sentinel_watch_{ts}.jpg"
    cap_lowres = str(CAP_DIR / f"watch_{ts}.jpg")

    if not capture_full(tmp_full):
        log_event({"event": "capture_fail"})
        return

    result = run_face_compare("match", tmp_full, str(REF_DIR))

    shrink(tmp_full, cap_lowres)
    os.remove(tmp_full)

    if "error" in result:
        log_event({"event": "match_error", "error": result["error"]})
        return

    state = load_state()
    faces = result.get("faces", 0)

    if faces == 0:
        if state.get("last_seen_owner"):
            log_event({"event": "no_face", "note": "owner_walked_away"})

            if BG_SNAPSHOT.exists() and os.path.exists(cap_lowres):
                if not backgrounds_similar(str(BG_SNAPSHOT), cap_lowres):
                    print(f"[BG_SHIFT] Background looks different. Laptop may have moved.")
                    log_event({"event": "bg_shift", "capture": os.path.basename(cap_lowres)})
                    return

            if os.path.exists(cap_lowres):
                os.remove(cap_lowres)
        else:
            log_event({"event": "no_face", "note": "owner_never_seen"})
        return

    distance = result.get("distance", 999)
    is_match = result.get("match", False)
    uncertain = result.get("uncertain", False)

    if is_match:
        state["last_seen_owner"] = datetime.now().isoformat()
        save_state(state)
        log_event({"event": "match_ok", "distance": distance})
        if os.path.exists(cap_lowres):
            os.remove(cap_lowres)

    elif uncertain:
        print(f"[UNCERTAIN] distance={distance:.1f} — keeping capture")
        log_event({"event": "uncertain", "distance": distance,
                   "capture": os.path.basename(cap_lowres)})

    else:
        # Wrong face — enter Shakespeare mode
        print(f"[MISMATCH] distance={distance:.1f} — WRONG FACE AT DESK")
        log_event({"event": "MISMATCH", "distance": distance,
                   "capture": os.path.basename(cap_lowres)})

        state["mode"] = "shakespeare"
        state["lockout_time"] = datetime.now().isoformat()
        state["lockout_distance"] = distance
        state["authenticated"] = False
        save_state(state)
        log_event({"event": "shakespeare_mode", "distance": distance})

        if distance > LOCK_THRESHOLD:
            print("[LOCK] Locking screen.")
            log_event({"event": "LOCK", "distance": distance})
            lock_screen()


def lock_screen():
    """Lock the screen via macOS."""
    try:
        subprocess.run(["pmset", "displaysleepnow"], capture_output=True, timeout=5)
    except Exception:
        subprocess.run(
            ["osascript", "-e",
             'tell application "System Events" to keystroke "q" using {command down, control down}'],
            capture_output=True, timeout=5
        )


# ── Peek (remote check) ───────────────────────────────────────────

def peek():
    """One-shot capture for remote check (e.g. via Tailscale SSH).
    Answers: is someone at the desk right now?"""
    ensure_dirs()
    tmp_full = "/tmp/face_sentinel_peek.jpg"

    if not capture_full(tmp_full):
        print(json.dumps({"desk": "unknown", "error": "capture failed"}))
        sys.exit(1)

    detect = run_face_compare("detect", tmp_full)
    faces = detect.get("faces", 0)

    if faces == 0:
        print(json.dumps({"desk": "empty", "faces": 0}))
        log_event({"event": "peek", "result": "empty"})
    else:
        result = run_face_compare("match", tmp_full, str(REF_DIR))
        is_match = result.get("match", False)
        distance = result.get("distance", 999)

        if is_match:
            who = "owner"
        elif result.get("uncertain", False):
            who = "uncertain"
        else:
            who = "stranger"

        print(json.dumps({"desk": "occupied", "who": who,
                          "faces": faces, "distance": round(distance, 1)}))
        log_event({"event": "peek", "result": who, "distance": distance})

    os.remove(tmp_full)


# ── Prune captures ────────────────────────────────────────────────

def prune_captures():
    now = datetime.now()
    match_cutoff = now - timedelta(hours=MATCH_RETAIN_HOURS)
    mismatch_cutoff = now - timedelta(days=MISMATCH_RETAIN_DAYS)

    mismatch_captures = set()
    if LOG_FILE.exists():
        with open(LOG_FILE) as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    if entry.get("event") in ("MISMATCH", "uncertain", "bg_shift"):
                        cap = entry.get("capture", "")
                        if cap:
                            mismatch_captures.add(cap)
                except json.JSONDecodeError:
                    continue

    for cap in CAP_DIR.glob("watch_*.jpg"):
        mtime = datetime.fromtimestamp(cap.stat().st_mtime)
        if cap.name in mismatch_captures:
            if mtime < mismatch_cutoff:
                cap.unlink()
        else:
            if mtime < match_cutoff:
                cap.unlink()


# ── Status ─────────────────────────────────────────────────────────

def status():
    """Quick status for /lazarus integration."""
    ensure_dirs()
    ref_count = len(list(REF_DIR.glob("*.json")))
    cap_count = len(list(CAP_DIR.glob("*.jpg")))
    state = load_state()

    ref_size = sum(f.stat().st_size for f in REF_DIR.iterdir()) if REF_DIR.exists() else 0
    cap_size = sum(f.stat().st_size for f in CAP_DIR.iterdir()) if CAP_DIR.exists() else 0

    authenticated = state.get("authenticated", False)
    auth_time = state.get("auth_time", "never")
    last_seen = state.get("last_seen_owner", "never")

    try:
        result = subprocess.run(
            ["pgrep", "-f", "face_sentinel.py.*--watch"],
            capture_output=True, text=True
        )
        watching = bool(result.stdout.strip())
    except Exception:
        watching = False

    last_mismatch = None
    if LOG_FILE.exists():
        with open(LOG_FILE) as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    if entry.get("event") == "MISMATCH":
                        last_mismatch = entry
                except json.JSONDecodeError:
                    continue

    print(f"Refs:        {ref_count}/{MAX_REFERENCES} ({ref_size//1024}KB)")
    print(f"Captures:    {cap_count} ({cap_size//1024}KB)")
    print(f"Auth:        {'yes' if authenticated else 'no'} (since {auth_time})")
    print(f"Last seen:   {last_seen}")
    print(f"Sentinel:    {'ACTIVE' if watching else 'stopped'}")
    if last_mismatch:
        print(f"Last MISMATCH: {last_mismatch.get('timestamp', '?')} "
              f"dist={last_mismatch.get('distance', '?')}")


# ── Prune refs command ─────────────────────────────────────────────

def prune_cmd():
    ensure_dirs()
    metas = sorted(REF_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime)
    if not metas:
        print("No references to prune.")
        return

    print(f"{len(metas)} references. Testing quality...")
    scores = {}
    for meta_path in metas:
        stem = meta_path.stem
        jpg = REF_DIR / f"{stem}.jpg"
        if not jpg.exists():
            continue
        result = run_face_compare("match", str(jpg), str(REF_DIR))
        if "error" not in result:
            scores[meta_path.name] = result.get("distance", 999)

    if not scores:
        print("Could not score references.")
        return

    avg = sum(scores.values()) / len(scores)
    print(f"Average self-distance: {avg:.1f}")

    outliers = {k: v for k, v in scores.items() if v > avg * 2}
    if outliers:
        print(f"\n{len(outliers)} outlier(s):")
        for name, dist in sorted(outliers.items(), key=lambda x: x[1], reverse=True):
            print(f"  {name}  distance={dist:.1f}")
    else:
        print("All references consistent.")


# ── Main ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Face sentinel — visual presence verification")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--auth", action="store_true", help="Authenticate session (face match)")
    group.add_argument("--enroll", action="store_true", help="Enroll a reference image")
    group.add_argument("--watch", action="store_true", help="Start passive watch daemon")
    group.add_argument("--peek", action="store_true", help="One-shot: who is at the desk?")
    group.add_argument("--prune", action="store_true", help="Check reference quality")
    group.add_argument("--status", action="store_true", help="Show status")
    parser.add_argument("--interval", type=int, default=WATCH_INTERVAL,
                        help=f"Watch interval in seconds (default: {WATCH_INTERVAL})")

    args = parser.parse_args()

    if not COMPARE_BIN.exists():
        print(f"ERROR: face_compare not found at {COMPARE_BIN}")
        print("Build: swiftc -O -framework Vision -framework AppKit face_compare.swift -o face_compare")
        sys.exit(1)

    if args.auth:
        auth()
    elif args.enroll:
        enroll()
    elif args.watch:
        watch(args.interval)
    elif args.peek:
        peek()
    elif args.prune:
        prune_cmd()
    elif args.status:
        status()
