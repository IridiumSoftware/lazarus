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
LIVENESS_DELTA_MIN = 0.008   # Min byte-diff between two captures ~1s apart;
                             # below = suspect static photo. Calibration data:
                             # a real face sitting still measures ~0.015
                             # (subtle skin micro-motion: head sway, blinks,
                             # breath); the threshold sits well below that.
                             # Catches printed photos and iPad-screen attacks;
                             # misses video playback, 3D-printed masks, and
                             # deepfake streams (those are v2 territory).
LIVENESS_GAP_SECONDS = 1.0   # Wait between first and second capture

# ── LavaLamp substrate cross-validation (LZ-032) ───────────────────
#
# LL-040 ships a per-startup AF_UNIX verify socket at
# ~/.lavalamp/verify.sock; LL-043 v4 protocol speaks 17-byte
# request / 74-byte ECDSA-P256-signed response with the SEC1-
# compressed daemon public key at ~/.lavalamp/verify.pub.
#
# Lazarus consumes that contract in auth() as a substrate-tier
# cross-check before authenticating: if LavaLamp's residue audit
# is REJECTing (LL-006 P_reject high), refuse auth even on a
# face-match. Hard fail on REJECT or signature ERROR (active
# threat signals); STALE / NOSOCK are fail-open by default
# (LavaLamp may not be installed) and fail-closed under
# --strict-lavalamp. Mirrors the LZ-015 / LZ-019 strict-touchid
# pattern.

LAVALAMP_SOCK = Path.home() / ".lavalamp" / "verify.sock"
LAVALAMP_PUB = Path.home() / ".lavalamp" / "verify.pub"
LAVALAMP_PROTOCOL_VERSION = 0x04
LAVALAMP_NONCE_LEN = 16
LAVALAMP_REQUEST_LEN = 17       # version + nonce
LAVALAMP_RESPONSE_LEN = 74      # version + result + 8-byte LE ts + 64-byte raw r||s sig
LAVALAMP_PUB_LEN = 33           # SEC1-compressed P-256 point
LAVALAMP_TIMEOUT_S = 2.0
LAVALAMP_TS_SKEW_S = 30

# Verdict codes returned by _lavalamp_query.
LAVALAMP_ACCEPT = "accept"      # daemon returned 'A' + valid signature
LAVALAMP_REJECT = "reject"      # daemon returned 'R'
LAVALAMP_STALE = "stale"        # daemon returned 'S' (cache > 120s)
LAVALAMP_NOSOCK = "nosock"      # socket or pubkey missing — daemon not running
LAVALAMP_ERROR = "error"        # protocol violation / bad signature / ts skew


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
    # Test affordance: FACE_COMPARE_STUB env var, if set, short-circuits
    # the subprocess invocation and returns the parsed JSON directly. Used
    # for manual testing and shell-driven verification. Production callers
    # leave the env var unset.
    stub = os.environ.get("FACE_COMPARE_STUB")
    if stub is not None:
        try:
            return json.loads(stub)
        except json.JSONDecodeError as e:
            return {"error": f"invalid FACE_COMPARE_STUB JSON: {e}"}

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


# ── Touch ID (opportunistic pre-face gate) ─────────────────────────
#
# Macs with Touch Bar / fingerprint hardware can be probed via the
# system `bioutil` binary. `bioutil -r` reads enrolled biometric
# records — an operation that requires biometric authentication,
# triggering the system Touch ID prompt. If the user presses an
# enrolled finger, the call returns 0. If they dismiss the prompt,
# or if no fingerprints are enrolled, it returns non-zero. If
# `bioutil` isn't installed or hangs past the timeout, we treat
# the gate as unavailable.
#
# Semantics: fail-open. Touch ID strengthens auth when available but
# never blocks a legitimate owner from authenticating on a machine
# without biometric hardware (or with hardware that's misbehaving).
# This is the right default for a single-owner desktop tool; a
# stricter mode where Touch ID is mandatory could be added behind
# a future `--strict-touchid` flag.

def _touchid_check(timeout_seconds: int = 30, _runner=None) -> str:
    """Run the system Touch ID gate. Returns one of:

      - "ok"           — bioutil returned 0 (Touch ID prompt succeeded)
      - "nonzero"      — bioutil returned non-zero (prompt dismissed,
                         no fingerprints enrolled, or other failure)
      - "unavailable"  — bioutil missing or timed out

    The `_runner` parameter is for testability — production callers
    leave it `None` to use `subprocess.run` directly; tests inject a
    stub that returns canned `CompletedProcess`-like objects or
    raises `TimeoutExpired` / `FileNotFoundError`.
    """
    runner = _runner if _runner is not None else subprocess.run
    try:
        result = runner(
            ["bioutil", "-r"],
            capture_output=True, text=True, timeout=timeout_seconds
        )
        return "ok" if result.returncode == 0 else "nonzero"
    except subprocess.TimeoutExpired:
        return "unavailable"
    except FileNotFoundError:
        return "unavailable"


# ── Liveness (anti-static-photo) ───────────────────────────────────
#
# Static-photo defense. A real face is never perfectly still — there's
# skin micro-motion (head sway, blinks, breath). A static photo —
# printed or held up on an iPad — produces near-identical consecutive
# captures. We grab a second frame ~1s after the first, downsize both
# to a small BMP, and count differing bytes. Below the threshold =
# suspect static.
#
# Catches: printed photos, iPad/phone screens held up showing a still.
# Misses:  video playback, 3D-printed mask, deepfake stream. Closing
#          those is v2 territory (active illumination flash / blink
#          challenge / depth sensor).

def _liveness_delta(bytes_a: bytes, bytes_b: bytes):
    """Pure byte-diff ratio between two equal-length byte sequences.
    Returns None on length mismatch or empty input. Exposed for unit
    tests; production code should use liveness_check()."""
    if not bytes_a or len(bytes_a) != len(bytes_b):
        return None
    diffs = sum(1 for a, b in zip(bytes_a, bytes_b) if a != b)
    return diffs / len(bytes_a)


def liveness_check(first_capture: str) -> dict:
    """Capture a second frame and check whether it varies from the first.

    Returns: {"live": bool, "delta": float, "reason": str}
    Fails open on infrastructure errors (camera retry failure, sips
    failure) so a flaky camera doesn't lock the owner out of their
    own machine.
    """
    import tempfile

    time.sleep(LIVENESS_GAP_SECONDS)
    second_full = tempfile.mktemp(suffix=".jpg")
    if not capture_full(second_full):
        return {"live": True, "delta": 0.0, "reason": "second_capture_failed_fail_open"}

    def to_tiny(src: str) -> str:
        dst = tempfile.mktemp(suffix=".bmp")
        subprocess.run(
            ["sips", "--resampleWidth", "64", "--resampleHeight", "48",
             "-s", "format", "bmp", src, "--out", dst],
            capture_output=True, timeout=10
        )
        return dst

    tiny_a = to_tiny(first_capture)
    tiny_b = to_tiny(second_full)
    os.remove(second_full)

    try:
        if not (os.path.exists(tiny_a) and os.path.exists(tiny_b)):
            return {"live": True, "delta": 0.0, "reason": "tiny_failed_fail_open"}

        bytes_a = open(tiny_a, "rb").read()
        bytes_b = open(tiny_b, "rb").read()

        delta = _liveness_delta(bytes_a, bytes_b)
        if delta is None:
            return {"live": True, "delta": 0.0, "reason": "size_mismatch_fail_open"}

        return {
            "live": delta >= LIVENESS_DELTA_MIN,
            "delta": delta,
            "reason": "static_likely" if delta < LIVENESS_DELTA_MIN else "ok",
        }
    finally:
        for p in (tiny_a, tiny_b):
            if os.path.exists(p):
                os.remove(p)


# ── LavaLamp substrate cross-check (LZ-032) ───────────────────────
#
# Speaks LL-043 v4 protocol against ~/.lavalamp/verify.sock to
# bring substrate-tier residue-audit state (LL-006) into Lazarus's
# auth decision. Port of pharos/src/c/pam_lavalamp/pam_lavalamp.c
# `try_ipc_query_v4`, same wire format, same ECDSA P-256
# verification.

def _lavalamp_query(sock_path: Path = None,
                    pub_path: Path = None,
                    timeout_s: float = LAVALAMP_TIMEOUT_S,
                    _socket_factory=None,
                    _urandom=None,
                    _now=None) -> str:
    """LL-043 v4 client. Returns one of LAVALAMP_ACCEPT / REJECT /
    STALE / NOSOCK / ERROR.

    Wire format (matches PharOS PH-009 reference client):
      Request  — 17 bytes: [version 0x04, nonce(16)]
      Response — 74 bytes: [version 0x04, result_byte,
                            ts_le_i64(8), sig_raw_r_s(64)]
      Signed message — nonce(16) || result_byte(1) || ts(8 LE)
      Verify       — ECDSA P-256, SHA-256, daemon pubkey from
                     ~/.lavalamp/verify.pub (33-byte SEC1 compressed)

    Test seams:
      `_socket_factory` — callable returning a socket-like object
        with sendall/recv/close. Default: socket.socket(AF_UNIX).
      `_urandom`        — callable(n) → bytes. Default: os.urandom.
      `_now`            — callable() → int seconds. Default: time.time.
      `sock_path` / `pub_path` — override defaults for testing.
    """
    import socket as _socket_mod
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import ec
    from cryptography.hazmat.primitives.asymmetric.utils import (
        encode_dss_signature,
    )
    from cryptography.exceptions import InvalidSignature

    sock_path = sock_path if sock_path is not None else LAVALAMP_SOCK
    pub_path = pub_path if pub_path is not None else LAVALAMP_PUB
    urandom = _urandom if _urandom is not None else os.urandom
    now_fn = _now if _now is not None else time.time

    # ─ Step 1: socket + pubkey must both be present ─
    try:
        if not Path(sock_path).exists():
            return LAVALAMP_NOSOCK
        if not Path(pub_path).exists():
            return LAVALAMP_NOSOCK
    except OSError:
        return LAVALAMP_NOSOCK

    # ─ Step 2: read pubkey, must be exactly 33 bytes SEC1-compressed ─
    try:
        pub_raw = Path(pub_path).read_bytes()
    except OSError:
        return LAVALAMP_NOSOCK
    if len(pub_raw) != LAVALAMP_PUB_LEN:
        return LAVALAMP_ERROR
    if pub_raw[0] not in (0x02, 0x03):
        # Not a SEC1-compressed P-256 point. Bad pubkey file.
        return LAVALAMP_ERROR
    try:
        pubkey = ec.EllipticCurvePublicKey.from_encoded_point(
            ec.SECP256R1(), pub_raw
        )
    except (ValueError, TypeError):
        return LAVALAMP_ERROR

    # ─ Step 3: build 17-byte request ─
    nonce = urandom(LAVALAMP_NONCE_LEN)
    if len(nonce) != LAVALAMP_NONCE_LEN:
        return LAVALAMP_ERROR
    request = bytes([LAVALAMP_PROTOCOL_VERSION]) + nonce

    # ─ Step 4: connect, send, receive ─
    if _socket_factory is not None:
        sock = _socket_factory()
    else:
        sock = _socket_mod.socket(_socket_mod.AF_UNIX,
                                   _socket_mod.SOCK_STREAM)
        sock.settimeout(timeout_s)
    try:
        try:
            sock.connect(str(sock_path))
        except (FileNotFoundError, ConnectionRefusedError):
            return LAVALAMP_NOSOCK
        except OSError:
            return LAVALAMP_ERROR
        try:
            sock.sendall(request)
        except OSError:
            return LAVALAMP_ERROR
        # Read exactly LAVALAMP_RESPONSE_LEN bytes.
        buf = bytearray()
        while len(buf) < LAVALAMP_RESPONSE_LEN:
            try:
                chunk = sock.recv(LAVALAMP_RESPONSE_LEN - len(buf))
            except OSError:
                return LAVALAMP_ERROR
            if not chunk:
                return LAVALAMP_ERROR
            buf.extend(chunk)
        response = bytes(buf)
    finally:
        try:
            sock.close()
        except OSError:
            pass

    # ─ Step 5: parse response ─
    if response[0] != LAVALAMP_PROTOCOL_VERSION:
        return LAVALAMP_ERROR
    result_byte = response[1]
    daemon_ts = int.from_bytes(response[2:10], "little", signed=True)
    sig_raw = response[10:74]
    if len(sig_raw) != 64:
        return LAVALAMP_ERROR

    # ─ Step 6: timestamp freshness ─
    now_ts = int(now_fn())
    if abs(now_ts - daemon_ts) > LAVALAMP_TS_SKEW_S:
        return LAVALAMP_ERROR

    # ─ Step 7: build signed message + verify ECDSA P-256 ─
    signed_msg = nonce + bytes([result_byte]) + response[2:10]
    r = int.from_bytes(sig_raw[:32], "big")
    s = int.from_bytes(sig_raw[32:], "big")
    try:
        der_sig = encode_dss_signature(r, s)
    except ValueError:
        return LAVALAMP_ERROR
    try:
        pubkey.verify(der_sig, signed_msg, ec.ECDSA(hashes.SHA256()))
    except InvalidSignature:
        return LAVALAMP_ERROR

    # ─ Step 8: dispatch on result byte ─
    if result_byte == ord("A"):
        return LAVALAMP_ACCEPT
    if result_byte == ord("R"):
        return LAVALAMP_REJECT
    if result_byte == ord("S"):
        return LAVALAMP_STALE
    return LAVALAMP_ERROR


# ── Auth (session opener) ─────────────────────────────────────────

def auth(strict_touchid: bool = False, strict_lavalamp: bool = False):
    """Session authentication: Touch ID + face match + background snapshot.

    When `strict_touchid` is True (set via the `--strict-touchid` CLI
    flag), any non-"ok" outcome from `_touchid_check()` is treated as
    a hard auth failure: the function prints a diagnostic, logs a
    `touchid_strict_fail` event, and exits non-zero before reaching
    the face-match step. Default behavior (False) is opportunistic
    fail-open per LZ-015 — Touch ID strengthens auth when available
    but never blocks a legitimate owner on hardware-less or
    misbehaving setups.
    """
    ensure_dirs()

    ref_count = len(list(REF_DIR.glob("*.json")))
    if ref_count == 0:
        print("No references enrolled. Run --enroll first to build your face set.")
        sys.exit(1)

    # Step 1: Touch ID gate. Default is opportunistic (fail-open per
    # LZ-015); --strict-touchid promotes non-"ok" outcomes to hard
    # auth failure (LZ-019).
    print("Touch ID verification...")
    touchid_result = _touchid_check()
    if touchid_result == "ok":
        log_event({"event": "touchid_ok"})
    elif strict_touchid:
        # Strict mode: any non-"ok" outcome is a hard auth failure.
        # No fall-through to face check.
        print(f"Touch ID strict-mode failure ({touchid_result}). "
              f"Auth denied.")
        log_event({"event": "touchid_strict_fail",
                   "result": touchid_result})
        sys.exit(1)
    elif touchid_result == "nonzero":
        print("Touch ID check returned non-zero. Proceeding with face check.")
        log_event({"event": "touchid_nonzero"})
    else:  # "unavailable"
        print("Touch ID unavailable. Proceeding with face check only.")
        log_event({"event": "touchid_unavailable"})

    # Step 1.5: LavaLamp substrate cross-check (LZ-032).
    # Brings LL-006 P_reject signal into Lazarus's auth decision.
    # REJECT (substrate audit caught something) and ERROR (signature
    # tamper) are hard fails regardless of strict_lavalamp. STALE and
    # NOSOCK fail-open by default (LavaLamp may not be installed) and
    # fail-closed under --strict-lavalamp.
    print("LavaLamp substrate cross-check...")
    lava_result = _lavalamp_query()
    if lava_result == LAVALAMP_ACCEPT:
        log_event({"event": "lavalamp_accept"})
    elif lava_result == LAVALAMP_REJECT:
        # Active threat signal from substrate. Refuse auth even if
        # face match would succeed.
        print("LavaLamp substrate REJECT. Auth denied "
              "(residue audit caught anomaly).")
        log_event({"event": "lavalamp_reject_hard_fail"})
        sys.exit(1)
    elif lava_result == LAVALAMP_ERROR:
        # Signature invalid or protocol tampered — active threat.
        print("LavaLamp substrate signature ERROR. Auth denied "
              "(possible tamper).")
        log_event({"event": "lavalamp_error_hard_fail"})
        sys.exit(1)
    elif strict_lavalamp:
        # Strict mode: STALE / NOSOCK are hard fails.
        print(f"LavaLamp substrate strict-mode failure "
              f"({lava_result}). Auth denied.")
        log_event({"event": "lavalamp_strict_fail",
                   "result": lava_result})
        sys.exit(1)
    elif lava_result == LAVALAMP_STALE:
        print("LavaLamp substrate STALE. Proceeding "
              "(daemon may be restarting).")
        log_event({"event": "lavalamp_stale"})
    else:  # LAVALAMP_NOSOCK
        print("LavaLamp daemon not running. Proceeding with face "
              "check only.")
        log_event({"event": "lavalamp_nosock"})

    # Step 2: Face capture + match
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


# ── Recovery (LZ-027 break-glass) ──────────────────────────────────
#
# When Shakespeare mode persists due to a camera failure, a
# face_compare regression, an LZ-013 liveness threshold mis-
# calibration (cold room, glasses change, etc.), or any other
# false-positive lockout, the legitimate owner needs a documented
# break-glass path that does NOT depend on the face-match
# pipeline. Without one, the only options are (a) edit state.json
# from a Terminal that hasn't loaded /lazarus, which is an
# accident-of-the-implementation rather than a feature, or
# (b) wait for the camera/face_compare situation to resolve,
# which may not happen.
#
# Two recovery methods, in priority order:
#
#   1. Touch ID success (LZ-015's _touchid_check returns "ok").
#      Most users will have Touch ID hardware and a single press
#      is faster than typing a token.
#
#   2. Recovery-token match. A 64-character hex secret stored at
#      ~/.face_sentinel/recovery_token.txt (mode 0600, generated
#      manually by the owner via `python3 -c "import secrets;
#      print(secrets.token_hex(32))"` and saved out-of-band —
#      e.g., in a password manager). The token is compared via
#      hmac.compare_digest for timing safety.
#
# Failure to satisfy EITHER method exits non-zero. Recovery use
# is logged as `recovery_used` with the method that succeeded,
# so a high recovery-use rate signals the primitive is
# mis-calibrated. Honest framing in LZ-027: recovery paths
# weaken the cryptographic story but strengthen the operational
# story — without them the system is unusable as a daily-driver
# sentinel because false-positive lockouts have no off-ramp.

RECOVERY_TOKEN_FILE = BASE_DIR / "recovery_token.txt"


def _read_recovery_token() -> str:
    """Read the recovery token from ~/.face_sentinel/recovery_token.txt
    (a 64-character hex secret, one line). Returns the trimmed
    contents, or empty string if the file is missing / unreadable.
    Production callers should compare via hmac.compare_digest."""
    if not RECOVERY_TOKEN_FILE.exists():
        return ""
    try:
        return RECOVERY_TOKEN_FILE.read_text().strip()
    except OSError:
        return ""


def recover(token: str = None) -> None:
    """Break-glass recovery from a persistent Shakespeare-mode
    lockout. Flips `state.json` back to mode="normal" via one of
    two methods:

      - Touch ID success (preferred; matches LZ-015 semantics).
      - Recovery-token match against
        ~/.face_sentinel/recovery_token.txt.

    Either method, on success, sets `mode="normal"`,
    `authenticated=true`, refreshes `auth_time` and
    `last_seen_owner`, pops `lockout_time` and
    `lockout_distance`, and logs a `recovery_used` event with
    the method that succeeded.

    If neither method is available (no Touch ID hardware AND no
    token file), or if both fail, exits non-zero. No silent
    fall-through.
    """
    import hmac as _hmac
    ensure_dirs()

    state = load_state()
    prior_mode = state.get("mode", "normal")
    prior_lockout_reason = state.get("lockout_reason")

    # ── Method 1: Touch ID ────────────────────────────────────────
    print("Recovery: attempting Touch ID...")
    touchid_result = _touchid_check()
    if touchid_result == "ok":
        method = "touchid"
        log_event({"event": "touchid_ok", "context": "recovery"})
    else:
        # Touch ID didn't succeed. Fall through to token check.
        print(f"Touch ID {touchid_result}. Trying recovery token...")
        log_event({"event": "touchid_" + touchid_result,
                   "context": "recovery"})

        if token is None:
            # User didn't supply a token on the CLI. Check the
            # token file via the helper.
            saved_token = _read_recovery_token()
            if not saved_token:
                print("ERROR: Touch ID failed and no recovery token "
                      "supplied or saved. Recovery denied.")
                log_event({"event": "recovery_denied",
                           "reason": "no_method_available"})
                sys.exit(1)
            print("ERROR: Touch ID failed. Pass --token <hex> to "
                  "use the saved recovery token.")
            log_event({"event": "recovery_denied",
                       "reason": "touchid_failed_no_token_supplied"})
            sys.exit(1)

        # User supplied a token. Compare it to the saved value
        # with timing-safe comparison.
        saved_token = _read_recovery_token()
        if not saved_token:
            print("ERROR: --token supplied but no recovery token "
                  "saved at ~/.face_sentinel/recovery_token.txt.")
            log_event({"event": "recovery_denied",
                       "reason": "token_supplied_but_none_saved"})
            sys.exit(1)
        if not _hmac.compare_digest(token.strip(), saved_token):
            print("ERROR: Recovery token mismatch. Recovery denied.")
            log_event({"event": "recovery_denied",
                       "reason": "token_mismatch"})
            sys.exit(1)
        method = "token"

    # ── Success path: flip state to normal ────────────────────────
    state["authenticated"] = True
    state["auth_time"] = datetime.now().isoformat()
    state["last_seen_owner"] = datetime.now().isoformat()
    state["mode"] = "normal"
    state.pop("lockout_time", None)
    state.pop("lockout_distance", None)
    save_state(state)

    print(f"RECOVERY OK. Method: {method}. Mode restored to normal.")
    if prior_mode == "shakespeare":
        print(f"  (cleared Shakespeare mode; prior lockout_reason: "
              f"{prior_lockout_reason or 'unset'})")
    log_event({"event": "recovery_used",
               "method": method,
               "prior_mode": prior_mode,
               "prior_lockout_reason": prior_lockout_reason})


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
    # Guard: under-cap → no-op. Without this, `metas[:to_remove]` with a
    # negative `to_remove` would silently delete all-but-newest. Callers
    # in production code (`enroll()`) guard against this, but expose the
    # function to tests / direct CLI use and the negative-index case
    # becomes dangerous.
    if to_remove <= 0:
        return
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

    # tmp_full is kept alive through the match branch so the liveness
    # probe sees the same source format as its own second capture
    # (asymmetric inputs produce JPEG-artifact byte deltas that can
    # masquerade as motion). Cleanup is deferred to the finally block.
    try:
        result = run_face_compare("match", tmp_full, str(REF_DIR))
        shrink(tmp_full, cap_lowres)

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
            # Liveness probe: catch static-photo presentation attacks.
            # tmp_full is the full-res first capture; liveness_check
            # captures a fresh full-res second frame and compares them
            # at 64x48 BMP. Symmetric source format on both frames.
            liveness = liveness_check(tmp_full)

            if not liveness["live"]:
                print(f"[LIVENESS_FAIL] delta={liveness['delta']:.4f} "
                      f"({liveness['reason']}) — possible static photo")
                log_event({"event": "liveness_fail",
                           "delta": liveness["delta"],
                           "reason": liveness["reason"],
                           "distance": distance,
                           "capture": os.path.basename(cap_lowres)})

                # Treat as mismatch — enter Shakespeare mode.
                state["mode"] = "shakespeare"
                state["lockout_time"] = datetime.now().isoformat()
                state["lockout_distance"] = distance
                state["lockout_reason"] = "liveness_fail"
                state["liveness_delta"] = liveness["delta"]
                state["authenticated"] = False
                save_state(state)
                log_event({"event": "shakespeare_mode",
                           "reason": "liveness_fail",
                           "delta": liveness["delta"]})
                return

            state["last_seen_owner"] = datetime.now().isoformat()
            save_state(state)
            log_event({"event": "match_ok",
                       "distance": distance,
                       "liveness_delta": liveness["delta"]})
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
    finally:
        if os.path.exists(tmp_full):
            os.remove(tmp_full)


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

PRUNE_OUTLIER_MULTIPLIER = 2.0  # A ref is an outlier if its leave-one-out
                                # nearest-neighbor distance is more than this
                                # multiple of the pool's average. Conservative
                                # default — any value > 1.0 will only flag
                                # refs that are *worse* than the average.


def _outliers_from_scores(scores: dict, multiplier: float = PRUNE_OUTLIER_MULTIPLIER) -> dict:
    """Pure helper: given a name -> distance map, return the subset whose
    distance exceeds `multiplier` × the mean. Exposed for unit tests."""
    if not scores:
        return {}
    avg = sum(scores.values()) / len(scores)
    return {k: v for k, v in scores.items() if v > avg * multiplier}


def _prune_score_one(target_meta: Path, all_metas: list) -> float:
    """Score one ref's leave-one-out nearest-neighbor distance.

    Builds a temporary directory containing every reference triple
    EXCEPT the target ref, runs `face_compare match` against the
    target's cached jpg over that pool, and returns the resulting
    best-distance. This is the ref's similarity to its closest
    *non-self* neighbor — the right question for outlier detection.

    Returns 999.0 on infrastructure error so the ref is treated as
    an outlier and surfaced for human review rather than silently
    skipped.
    """
    import tempfile

    target_stem = target_meta.stem
    target_jpg = REF_DIR / f"{target_stem}.jpg"
    if not target_jpg.exists():
        return 999.0

    tmpdir = tempfile.mkdtemp(prefix="face_sentinel_prune_")
    try:
        # Symlink every other ref's three files into the tempdir.
        # Symlinks are cheap; we never modify the originals.
        for meta in all_metas:
            if meta.stem == target_stem:
                continue
            for suffix in (".json", ".fpdata", ".jpg"):
                src = REF_DIR / f"{meta.stem}{suffix}"
                if src.exists():
                    os.symlink(str(src), os.path.join(tmpdir, f"{meta.stem}{suffix}"))

        result = run_face_compare("match", str(target_jpg), tmpdir)
        if "error" in result:
            return 999.0
        return float(result.get("distance", 999))
    finally:
        # Clean up symlinks + tempdir.
        for entry in os.listdir(tmpdir):
            try:
                os.unlink(os.path.join(tmpdir, entry))
            except OSError:
                pass
        try:
            os.rmdir(tmpdir)
        except OSError:
            pass


def prune_cmd():
    """Score the reference pool via leave-one-out nearest-neighbor and
    flag outliers (refs whose closest non-self neighbor is unusually
    far). Outliers are likely off-distribution captures (different
    person, occluded face, bad lighting) that hurt match quality.
    Reports only — does not auto-delete; the human decides what to
    retire."""
    ensure_dirs()
    metas = sorted(REF_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime)
    if not metas:
        print("No references to prune.")
        return
    if len(metas) < 2:
        print("Need at least 2 references to compute leave-one-out scores.")
        return

    print(f"{len(metas)} references. Testing quality (leave-one-out)...")
    scores = {}
    for i, meta_path in enumerate(metas, 1):
        if i % 10 == 0 or i == len(metas):
            print(f"  scored {i}/{len(metas)}")
        scores[meta_path.name] = _prune_score_one(meta_path, metas)

    if not scores:
        print("Could not score references.")
        return

    avg = sum(scores.values()) / len(scores)
    print(f"Average leave-one-out nearest-neighbor distance: {avg:.2f}")

    outliers = _outliers_from_scores(scores)
    if outliers:
        print(f"\n{len(outliers)} outlier(s) (distance > {PRUNE_OUTLIER_MULTIPLIER}× avg):")
        for name, dist in sorted(outliers.items(), key=lambda x: x[1], reverse=True):
            print(f"  {name}  distance={dist:.2f}")
        print("\nReview these manually before deleting. Genuine off-")
        print("distribution refs (different person, bad lighting, occluded)")
        print("hurt match quality; legitimate outliers (rare-condition refs)")
        print("improve coverage. The algorithm cannot tell them apart.")
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
    group.add_argument("--recover", action="store_true",
                       help="Break-glass recovery from persistent Shakespeare-mode "
                            "lockout (Touch ID + optional --token)")
    parser.add_argument("--interval", type=int, default=WATCH_INTERVAL,
                        help=f"Watch interval in seconds (default: {WATCH_INTERVAL})")
    parser.add_argument("--strict-touchid", action="store_true",
                        help="Treat Touch ID nonzero/unavailable as hard auth "
                             "failure (default: opportunistic / fail-open)")
    parser.add_argument("--strict-lavalamp", action="store_true",
                        help="Treat LavaLamp daemon STALE/NOSOCK as hard auth "
                             "failure (LZ-032; REJECT/ERROR are hard fails "
                             "regardless; default: opportunistic / fail-open)")
    parser.add_argument("--token", type=str, default=None,
                        help="Recovery token (hex). Used with --recover when "
                             "Touch ID is unavailable or fails.")

    args = parser.parse_args()

    if not COMPARE_BIN.exists():
        print(f"ERROR: face_compare not found at {COMPARE_BIN}")
        print("Build: swiftc -O -framework Vision -framework AppKit face_compare.swift -o face_compare")
        sys.exit(1)

    if args.auth:
        auth(strict_touchid=args.strict_touchid,
             strict_lavalamp=args.strict_lavalamp)
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
    elif args.recover:
        recover(token=args.token)
