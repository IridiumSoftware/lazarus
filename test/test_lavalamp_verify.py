"""
test_lavalamp_verify.py — exercises LZ-032 (LavaLamp substrate
cross-validation in Lazarus's auth path).

LZ-032 brings LL-040 / LL-043 v4 ECDSA P-256 protocol into
face_sentinel.py as a substrate-tier cross-check. The Python
client at `_lavalamp_query()` is a direct port of PharOS's
`pam_lavalamp.c try_ipc_query_v4`; this test exercises both the
protocol client in isolation (10 verdict scenarios) AND the
auth() gating logic (5 integration scenarios).

Verdict-code semantics:
  - ACCEPT  — 'A' + valid signature → proceed
  - REJECT  — 'R' + valid signature → hard fail (substrate caught
              an anomaly; refuse even on face match)
  - STALE   — 'S' + valid signature → fail-open default,
              fail-closed under --strict-lavalamp
  - NOSOCK  — socket or pubkey file missing → fail-open default,
              fail-closed under --strict-lavalamp
  - ERROR   — wire violation / signature mismatch / ts skew → hard
              fail (active tamper signal)

Runs locally with no extra deps beyond `cryptography` (already
imported elsewhere in the project):
    python3 test/test_lavalamp_verify.py
Exit 0 on PASS, non-zero on FAIL.

Mocks the v4 daemon side using a real ECDSA P-256 keypair from
`cryptography` so the verify path runs end-to-end (signatures
are computed and validated, not stubbed at the verify boundary).
"""

import contextlib
import inspect
import io
import json
import os
import shutil
import sys
import tempfile
import time
from pathlib import Path

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import (
    decode_dss_signature,
)

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


# ── Daemon-side helpers (mock the LavaLamp daemon) ───────────────────


def make_keypair():
    priv = ec.generate_private_key(ec.SECP256R1())
    pub = priv.public_key()
    # SEC1-compressed point (33 bytes, identical to what
    # LL-043's `get_uncompressed_pub` + `compress_pub` produces).
    pub_compressed = pub.public_bytes(
        encoding=serialization.Encoding.X962,
        format=serialization.PublicFormat.CompressedPoint,
    )
    assert len(pub_compressed) == 33
    return priv, pub_compressed


def sign_response(priv, nonce: bytes, result_byte: int, ts: int) -> bytes:
    """Build the 74-byte v4 response with a valid ECDSA P-256 signature."""
    ts_bytes = ts.to_bytes(8, "little", signed=True)
    signed_msg = nonce + bytes([result_byte]) + ts_bytes
    der_sig = priv.sign(signed_msg, ec.ECDSA(hashes.SHA256()))
    r, s = decode_dss_signature(der_sig)
    raw_sig = r.to_bytes(32, "big") + s.to_bytes(32, "big")
    return (bytes([fs.LAVALAMP_PROTOCOL_VERSION])
            + bytes([result_byte])
            + ts_bytes
            + raw_sig)


class MockSocket:
    """Stub the LavaLamp daemon socket end-to-end. Records the
    client-sent request, then plays back a daemon response."""

    def __init__(self, response_factory):
        # response_factory(request_bytes) -> response_bytes
        self._response_factory = response_factory
        self.sent = b""
        self._recv_buf = b""

    def settimeout(self, _t):
        pass

    def connect(self, _path):
        pass

    def sendall(self, data):
        self.sent += data
        if len(self.sent) == fs.LAVALAMP_REQUEST_LEN:
            self._recv_buf = self._response_factory(self.sent)

    def recv(self, n):
        if not self._recv_buf:
            return b""
        chunk = self._recv_buf[:n]
        self._recv_buf = self._recv_buf[n:]
        return chunk

    def close(self):
        pass


def with_sock_pub(test_fn):
    """Wrap a test fn so it gets an existing-socket-and-pubkey
    sandbox. Creates a temp dir, writes a placeholder pubkey + a
    placeholder socket file (just needs to exist; MockSocket
    handles the protocol), invokes the test, cleans up."""

    def wrapped(*args, **kwargs):
        tmp = tempfile.mkdtemp(prefix="lz032_")
        try:
            sock_path = Path(tmp) / "verify.sock"
            pub_path = Path(tmp) / "verify.pub"
            # Touch the socket file so Path.exists() returns True.
            sock_path.touch()
            # Create a real keypair to write the pubkey + sign with.
            priv, pub = make_keypair()
            pub_path.write_bytes(pub)
            return test_fn(*args, priv=priv, sock_path=sock_path,
                           pub_path=pub_path, **kwargs)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    return wrapped


# ── Section 1: _lavalamp_query verdict-code scenarios (10 cases) ──


@with_sock_pub
def test_accept_valid_signature(priv, sock_path, pub_path):
    """Good 'A' response + valid signature → LAVALAMP_ACCEPT."""
    now = 1_700_000_000
    factory = lambda req: sign_response(
        priv, req[1:], ord("A"), now
    )
    result = fs._lavalamp_query(
        sock_path=sock_path, pub_path=pub_path,
        _socket_factory=lambda: MockSocket(factory),
        _urandom=lambda n: b"X" * n,
        _now=lambda: now,
    )
    expect("ACCEPT path", result, fs.LAVALAMP_ACCEPT)


@with_sock_pub
def test_reject_valid_signature(priv, sock_path, pub_path):
    """Good 'R' response + valid signature → LAVALAMP_REJECT."""
    now = 1_700_000_000
    factory = lambda req: sign_response(
        priv, req[1:], ord("R"), now
    )
    result = fs._lavalamp_query(
        sock_path=sock_path, pub_path=pub_path,
        _socket_factory=lambda: MockSocket(factory),
        _urandom=lambda n: b"Y" * n,
        _now=lambda: now,
    )
    expect("REJECT path", result, fs.LAVALAMP_REJECT)


@with_sock_pub
def test_stale_valid_signature(priv, sock_path, pub_path):
    """Good 'S' response + valid signature → LAVALAMP_STALE."""
    now = 1_700_000_000
    factory = lambda req: sign_response(
        priv, req[1:], ord("S"), now
    )
    result = fs._lavalamp_query(
        sock_path=sock_path, pub_path=pub_path,
        _socket_factory=lambda: MockSocket(factory),
        _urandom=lambda n: b"Z" * n,
        _now=lambda: now,
    )
    expect("STALE path", result, fs.LAVALAMP_STALE)


@with_sock_pub
def test_ts_skew_rejection(priv, sock_path, pub_path):
    """Daemon ts > 30s old → LAVALAMP_ERROR even with valid sig.
    Same threshold as PharOS PH-007/PH-009 (IPC_TS_SKEW_S=30)."""
    now = 1_700_000_000
    daemon_ts = now - 60  # 60s skew, threshold is 30
    factory = lambda req: sign_response(
        priv, req[1:], ord("A"), daemon_ts
    )
    result = fs._lavalamp_query(
        sock_path=sock_path, pub_path=pub_path,
        _socket_factory=lambda: MockSocket(factory),
        _urandom=lambda n: b"X" * n,
        _now=lambda: now,
    )
    expect("ts skew → ERROR", result, fs.LAVALAMP_ERROR)


@with_sock_pub
def test_bad_signature_rejection(priv, sock_path, pub_path):
    """Valid wire format but signed with a DIFFERENT keypair →
    LAVALAMP_ERROR (signature does not validate against the
    pubkey file on disk)."""
    now = 1_700_000_000
    other_priv, _ = make_keypair()
    # Sign with other_priv, but pubkey file still points at priv.
    factory = lambda req: sign_response(
        other_priv, req[1:], ord("A"), now
    )
    result = fs._lavalamp_query(
        sock_path=sock_path, pub_path=pub_path,
        _socket_factory=lambda: MockSocket(factory),
        _urandom=lambda n: b"X" * n,
        _now=lambda: now,
    )
    expect("bad sig → ERROR", result, fs.LAVALAMP_ERROR)


@with_sock_pub
def test_bad_version_byte(priv, sock_path, pub_path):
    """Response version byte != 0x04 → LAVALAMP_ERROR."""
    now = 1_700_000_000

    def factory(req):
        good = sign_response(priv, req[1:], ord("A"), now)
        return bytes([0x03]) + good[1:]  # downgrade attack

    result = fs._lavalamp_query(
        sock_path=sock_path, pub_path=pub_path,
        _socket_factory=lambda: MockSocket(factory),
        _urandom=lambda n: b"X" * n,
        _now=lambda: now,
    )
    expect("bad version → ERROR", result, fs.LAVALAMP_ERROR)


@with_sock_pub
def test_unknown_result_byte(priv, sock_path, pub_path):
    """Result byte not in {A, R, S} → LAVALAMP_ERROR (signature
    still validates over whatever the byte is)."""
    now = 1_700_000_000
    factory = lambda req: sign_response(
        priv, req[1:], ord("Q"), now  # 'Q' is not a valid verdict
    )
    result = fs._lavalamp_query(
        sock_path=sock_path, pub_path=pub_path,
        _socket_factory=lambda: MockSocket(factory),
        _urandom=lambda n: b"X" * n,
        _now=lambda: now,
    )
    expect("unknown verdict → ERROR", result, fs.LAVALAMP_ERROR)


def test_missing_socket():
    """Socket file absent → LAVALAMP_NOSOCK (fail-open trigger)."""
    tmp = tempfile.mkdtemp(prefix="lz032_")
    try:
        sock_path = Path(tmp) / "verify.sock"  # not touched
        pub_path = Path(tmp) / "verify.pub"
        # Pubkey exists but socket doesn't.
        _, pub = make_keypair()
        pub_path.write_bytes(pub)
        result = fs._lavalamp_query(
            sock_path=sock_path, pub_path=pub_path,
        )
        expect("no socket → NOSOCK", result, fs.LAVALAMP_NOSOCK)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_missing_pubkey():
    """Pubkey file absent → LAVALAMP_NOSOCK."""
    tmp = tempfile.mkdtemp(prefix="lz032_")
    try:
        sock_path = Path(tmp) / "verify.sock"
        sock_path.touch()
        pub_path = Path(tmp) / "verify.pub"  # not written
        result = fs._lavalamp_query(
            sock_path=sock_path, pub_path=pub_path,
        )
        expect("no pubkey → NOSOCK", result, fs.LAVALAMP_NOSOCK)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_malformed_pubkey():
    """Pubkey file present but wrong length → LAVALAMP_ERROR."""
    tmp = tempfile.mkdtemp(prefix="lz032_")
    try:
        sock_path = Path(tmp) / "verify.sock"
        sock_path.touch()
        pub_path = Path(tmp) / "verify.pub"
        pub_path.write_bytes(b"\x02" * 10)  # 10 bytes, not 33
        result = fs._lavalamp_query(
            sock_path=sock_path, pub_path=pub_path,
        )
        expect("malformed pubkey → ERROR", result, fs.LAVALAMP_ERROR)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ── Section 2: auth() gating with the cross-check (5 cases) ──


def stub_camera_and_face(monkeypatched=None):
    """Stub face_sentinel module-level functions so auth() can run
    without a real camera or face_compare binary. Mirrors the
    pattern in test_auth_strict_touchid.py."""
    fs._touchid_check_orig = fs._touchid_check
    fs._lavalamp_query_orig = fs._lavalamp_query
    fs.capture_full_orig = fs.capture_full
    fs.run_face_compare_orig = fs.run_face_compare
    fs.shrink_orig = fs.shrink

    fs._touchid_check = lambda *a, **kw: "ok"

    def stub_capture_full(path):
        Path(path).write_bytes(b"x")
        return True
    fs.capture_full = stub_capture_full
    fs.run_face_compare = lambda *a, **kw: {
        "match": True, "faces": 1, "distance": 12.0,
    }
    fs.shrink = lambda *a, **kw: None


def restore_camera_and_face():
    fs._touchid_check = fs._touchid_check_orig
    fs._lavalamp_query = fs._lavalamp_query_orig
    fs.capture_full = fs.capture_full_orig
    fs.run_face_compare = fs.run_face_compare_orig
    fs.shrink = fs.shrink_orig


def run_auth_capturing(strict_lavalamp=False, lava_verdict="accept"):
    """Drive auth() with stubs and capture exit / log events.
    Returns (exit_code, list_of_log_events)."""
    tmp = Path(tempfile.mkdtemp(prefix="lz032_auth_"))
    fs.BASE_DIR = tmp
    fs.REF_DIR = tmp / "reference"
    fs.LOG_FILE = tmp / "sentinel.log"
    fs.STATE_FILE = tmp / "state.json"
    fs.BG_SNAPSHOT = tmp / "background.jpg"
    fs.REF_DIR.mkdir(parents=True, exist_ok=True)
    # Seed one reference so the ref-count gate passes.
    (fs.REF_DIR / "ref01.json").write_text("{}")

    stub_camera_and_face()
    fs._lavalamp_query = lambda *a, **kw: {
        "accept": fs.LAVALAMP_ACCEPT,
        "reject": fs.LAVALAMP_REJECT,
        "stale": fs.LAVALAMP_STALE,
        "nosock": fs.LAVALAMP_NOSOCK,
        "error": fs.LAVALAMP_ERROR,
    }[lava_verdict]

    exit_code = None
    out = io.StringIO()
    try:
        with contextlib.redirect_stdout(out):
            fs.auth(strict_touchid=False,
                    strict_lavalamp=strict_lavalamp)
    except SystemExit as e:
        exit_code = e.code if e.code is not None else 0
    finally:
        restore_camera_and_face()

    events = read_log_events(fs.LOG_FILE)
    shutil.rmtree(tmp, ignore_errors=True)
    return exit_code, events, out.getvalue()


def test_auth_lavalamp_accept_proceeds():
    """ACCEPT verdict + good face → auth completes successfully."""
    exit_code, events, _ = run_auth_capturing(lava_verdict="accept")
    expect("ACCEPT exit code", exit_code, None)
    event_names = [e.get("event") for e in events]
    if "lavalamp_accept" not in event_names:
        print(f"FAIL: missing lavalamp_accept event; got {event_names}")
        sys.exit(1)
    if "auth_ok" not in event_names:
        print(f"FAIL: missing auth_ok event; got {event_names}")
        sys.exit(1)


def test_auth_lavalamp_reject_hard_fail():
    """REJECT verdict → hard fail BEFORE camera, even in default mode."""
    exit_code, events, _ = run_auth_capturing(
        strict_lavalamp=False, lava_verdict="reject"
    )
    expect("REJECT exit code (default mode)", exit_code, 1)
    event_names = [e.get("event") for e in events]
    if "lavalamp_reject_hard_fail" not in event_names:
        print(f"FAIL: missing lavalamp_reject_hard_fail event; "
              f"got {event_names}")
        sys.exit(1)
    # auth_ok must NOT appear — REJECT short-circuits before face.
    if "auth_ok" in event_names:
        print(f"FAIL: auth_ok fired despite REJECT; got {event_names}")
        sys.exit(1)


def test_auth_lavalamp_error_hard_fail():
    """ERROR verdict → hard fail regardless of strict flag."""
    exit_code, events, _ = run_auth_capturing(
        strict_lavalamp=False, lava_verdict="error"
    )
    expect("ERROR exit code", exit_code, 1)
    event_names = [e.get("event") for e in events]
    if "lavalamp_error_hard_fail" not in event_names:
        print(f"FAIL: missing lavalamp_error_hard_fail event; "
              f"got {event_names}")
        sys.exit(1)


def test_auth_lavalamp_stale_default_proceeds():
    """STALE verdict + default mode → soft warn + proceed."""
    exit_code, events, _ = run_auth_capturing(
        strict_lavalamp=False, lava_verdict="stale"
    )
    expect("STALE exit code (default)", exit_code, None)
    event_names = [e.get("event") for e in events]
    if "lavalamp_stale" not in event_names:
        print(f"FAIL: missing lavalamp_stale event; got {event_names}")
        sys.exit(1)
    if "auth_ok" not in event_names:
        print(f"FAIL: missing auth_ok after STALE fall-through; "
              f"got {event_names}")
        sys.exit(1)


def test_auth_lavalamp_stale_strict_hard_fail():
    """STALE verdict + --strict-lavalamp → hard fail."""
    exit_code, events, _ = run_auth_capturing(
        strict_lavalamp=True, lava_verdict="stale"
    )
    expect("STALE exit code (strict)", exit_code, 1)
    event_names = [e.get("event") for e in events]
    if "lavalamp_strict_fail" not in event_names:
        print(f"FAIL: missing lavalamp_strict_fail event; "
              f"got {event_names}")
        sys.exit(1)


def test_auth_lavalamp_nosock_default_proceeds():
    """NOSOCK + default → fail-open: proceed with face check."""
    exit_code, events, _ = run_auth_capturing(
        strict_lavalamp=False, lava_verdict="nosock"
    )
    expect("NOSOCK exit code (default)", exit_code, None)
    event_names = [e.get("event") for e in events]
    if "lavalamp_nosock" not in event_names:
        print(f"FAIL: missing lavalamp_nosock event; got {event_names}")
        sys.exit(1)


def test_auth_signature_default_parameter_lock():
    """auth() default parameter values lock — both flags default
    to False (fail-open) per LZ-015 / LZ-032 design."""
    sig = inspect.signature(fs.auth)
    expect("strict_touchid default",
           sig.parameters["strict_touchid"].default, False)
    expect("strict_lavalamp default",
           sig.parameters["strict_lavalamp"].default, False)


# ── Driver ─────────────────────────────────────────────────────────


TESTS = [
    # Section 1: _lavalamp_query verdict-code scenarios
    test_accept_valid_signature,
    test_reject_valid_signature,
    test_stale_valid_signature,
    test_ts_skew_rejection,
    test_bad_signature_rejection,
    test_bad_version_byte,
    test_unknown_result_byte,
    test_missing_socket,
    test_missing_pubkey,
    test_malformed_pubkey,
    # Section 2: auth() integration
    test_auth_lavalamp_accept_proceeds,
    test_auth_lavalamp_reject_hard_fail,
    test_auth_lavalamp_error_hard_fail,
    test_auth_lavalamp_stale_default_proceeds,
    test_auth_lavalamp_stale_strict_hard_fail,
    test_auth_lavalamp_nosock_default_proceeds,
    test_auth_signature_default_parameter_lock,
]


def main():
    for t in TESTS:
        t()
        print(f"PASS {t.__name__}")
    print(f"\nAll {len(TESTS)} tests passed.")


if __name__ == "__main__":
    main()
