"""
test_network_exfil_joint_closure.py — exercises LZ-022
(network-exfiltration joint closure: LZ-005 ∧ LZ-010 ∧ LZ-019).

The conjunctive claim is that the three-angle V-NETWORK-EXFIL
defense — LZ-005 apple-vision local-only (PREVENTION), LZ-010
network-honeypot port listeners (DETECTION), LZ-019 strict
Touch ID hard-gate (CONTROL) — holds as a JOINT defense triangle.
Each component has its own :tested entry; this test exercises
the conjunction in a single end-to-end harness.

Per CLAUDE.md's conjunctive-claim discipline, sub-claim evidence
does not promote a joint claim — promotion to :tested requires a
joint integration test exercising the conjunction explicitly.
This file is that test.

What this catches that the three component tests miss:
- Defense-layer attrition — a refactor that disables one of the
  three layers (e.g. silently allows a networking import in the
  Swift binary; removes the SERVICES table; defaults
  strict_touchid to True without preserving the opt-in
  semantics) would change the joint claim's blast radius even
  if the surviving two layers still pass their component tests.
- V-tag drift — the joint claim is anchored on the
  V-NETWORK-EXFIL attack class. If a future spec edit strips
  that anchor from LZ-022 or from one of the three component
  entries, the joint claim's framing weakens.
- Single-pass operational composition — none of the three
  component tests run all three layers in one process. This
  test does, asserting that the three defensive surfaces are
  simultaneously operational in a single-Python-process scenario.

Honest framing: static + dynamic joint test in one harness.
Catches refactors that split the V-NETWORK-EXFIL defense along
weak seams. Does NOT prove a real exfiltration attempt would
be defeated — a determined adversary could obfuscate networking
calls (LZ-005 bypass), bind a non-honeypot port (LZ-010 bypass),
or disable Touch ID hardware (LZ-019 bypass). Each component's
own honest-framing notes carry forward into the conjunction.

Runs locally with no extra deps:
    python3 test/test_network_exfil_joint_closure.py
Exit 0 on PASS, non-zero on FAIL.
"""

import contextlib
import io
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
from datetime import datetime
from pathlib import Path

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, REPO_ROOT)


def fail(msg):
    print(f"FAIL test_network_exfil_joint_closure.py: {msg}")
    sys.exit(1)


def expect(label, actual, expected):
    if actual != expected:
        fail(f"{label}: got {actual!r}, expected {expected!r}")


def expect_contains(label, haystack, needle):
    if needle not in haystack:
        fail(f"{label}: {needle!r} not found")


def expect_no_regex_match(label, haystack, pattern, flags=0):
    m = re.search(pattern, haystack, flags)
    if m:
        start = max(0, m.start() - 40)
        end = min(len(haystack), m.end() + 40)
        ctx = haystack[start:end].replace("\n", "\\n")
        fail(f"{label}: pattern {pattern!r} matched: ...{ctx}...")


# ── Section 1 — Component tests pass as a conjunction ──────────────

# Sub-claim evidence is necessary for the joint claim, just not
# sufficient. Running the three components in sequence asserts
# the triple is currently intact at the component level; the
# joint-specific checks below (sections 2-6) then layer on top.

COMPONENT_TESTS = [
    ("test_no_networking_imports.sh", "bash"),   # LZ-005
    ("test_honeypot_listener.py", sys.executable),  # LZ-010
    ("test_auth_strict_touchid.py", sys.executable),  # LZ-019
]
for fname, runner in COMPONENT_TESTS:
    path = os.path.join(TEST_DIR, fname)
    r = subprocess.run([runner, path], capture_output=True, text=True)
    if r.returncode != 0:
        sys.stdout.write(r.stdout)
        sys.stderr.write(r.stderr)
        fail(f"component test {fname}: exit {r.returncode}")


# ── Section 2 — Layer 1 (LZ-005) source-level prevention re-verified ──

# Independent re-grep here (not delegated to the .sh script) so the
# joint test asserts directly on the *source files* rather than
# trusting the subprocess. Catches a refactor that disables the
# grep-lint but leaves a networking import in place (the .sh test
# would fail-open if its size guard breaks).

with open(os.path.join(REPO_ROOT, "face_compare.swift")) as f:
    swift_src = f.read()
with open(os.path.join(REPO_ROOT, "face_sentinel.py")) as f:
    sentinel_src = f.read()

# Size guard (LZ-005 has its own; we re-state for joint-test
# self-sufficiency).
if len(swift_src) < 1000:
    fail(f"face_compare.swift suspiciously small ({len(swift_src)}b)")
if len(sentinel_src) < 5000:
    fail(f"face_sentinel.py suspiciously small ({len(sentinel_src)}b)")

# Swift networking symbols.
SWIFT_NETWORKING = [
    r"\bURLSession\b",
    r"\bURLProtocol\b",
    r"\bNSURLConnection\b",
    r"\bimport Network\b",
    r"\bNWConnection\b",
    r"\bNWListener\b",
    r"\bCFNetwork\b",
]
for pat in SWIFT_NETWORKING:
    expect_no_regex_match(f"LZ-005 swift: {pat!r}", swift_src, pat)

# Python networking imports.
PYTHON_NETWORKING = [
    r"^\s*import socket\b",
    r"^\s*from socket\b",
    r"^\s*import urllib\b",
    r"^\s*from urllib\b",
    r"^\s*import requests\b",
    r"^\s*from requests\b",
    r"^\s*import http\.",
    r"^\s*from http\b",
    r"\burlopen\(",
]
for pat in PYTHON_NETWORKING:
    expect_no_regex_match(f"LZ-005 python: {pat!r}",
                          sentinel_src, pat, re.MULTILINE)


# ── Section 3 — Layer 2 (LZ-010) runtime detection ──────────────────

# Stand up a TEST-HTTP honeypot listener in this process, connect
# to it, verify the JSONL log record appears. This is a slim
# subset of test_honeypot_listener.py — the *joint* assertion
# here is that the layer remains operational when invoked
# alongside the other two layers in one process.

import network_honeypot as nh  # noqa: E402

honeypot_tmpdir = tempfile.mkdtemp(prefix="lz022_honeypot_")
saved_log_dir = nh.LOG_DIR
nh.LOG_DIR = honeypot_tmpdir

# Pick a different port than test_honeypot_listener.py uses so
# the two tests can run back-to-back in CI without bind races.
HONEYPOT_PORT = 38082

listener_thread = threading.Thread(
    target=nh.listen_on_port,
    args=(HONEYPOT_PORT, "TEST-EXFIL", nh.serve_http),
    daemon=True,
)
listener_thread.start()

# Poll for bind.
bind_deadline = time.time() + 5.0
bound = False
while time.time() < bind_deadline:
    probe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    probe.settimeout(0.5)
    try:
        probe.connect(("127.0.0.1", HONEYPOT_PORT))
        bound = True
        probe.close()
        break
    except (ConnectionRefusedError, OSError):
        time.sleep(0.05)
    finally:
        try:
            probe.close()
        except Exception:
            pass

if not bound:
    nh.LOG_DIR = saved_log_dir
    shutil.rmtree(honeypot_tmpdir, ignore_errors=True)
    fail(f"LZ-010: listener never bound on port {HONEYPOT_PORT} within 5s")

# Simulated exfil attempt: connect + send HTTP GET (as an exfil
# tool might to a corporate proxy or C2 endpoint).
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.settimeout(3.0)
exfil_payload = b"POST /upload HTTP/1.0\r\nHost: attacker\r\n\r\nface_data"
try:
    client.connect(("127.0.0.1", HONEYPOT_PORT))
    client.sendall(exfil_payload)
    # Drain response so the server can log_connection.
    end = time.time() + 3.0
    while time.time() < end:
        try:
            chunk = client.recv(4096)
            if not chunk:
                break
        except socket.timeout:
            break
finally:
    try:
        client.close()
    except Exception:
        pass

# Poll for log file.
today = datetime.now().strftime("%Y-%m-%d")
log_path = os.path.join(honeypot_tmpdir, f"honeypot_{today}.jsonl")
log_deadline = time.time() + 5.0
while time.time() < log_deadline:
    if os.path.exists(log_path) and os.path.getsize(log_path) > 0:
        break
    time.sleep(0.05)

if not os.path.exists(log_path):
    nh.LOG_DIR = saved_log_dir
    shutil.rmtree(honeypot_tmpdir, ignore_errors=True)
    fail(f"LZ-010: log file never appeared at {log_path}")

with open(log_path) as f:
    record = json.loads(f.readline().strip())

# The exfil attempt was DETECTED — assert the trap fired.
expect("LZ-010: log service field", record.get("service"), "HTTP")
expect("LZ-010: log port field", record.get("port"), HONEYPOT_PORT)
if "remote" not in record or ":" not in record["remote"]:
    nh.LOG_DIR = saved_log_dir
    shutil.rmtree(honeypot_tmpdir, ignore_errors=True)
    fail(f"LZ-010: log remote field malformed: {record!r}")

# Teardown honeypot.
nh.LOG_DIR = saved_log_dir
shutil.rmtree(honeypot_tmpdir, ignore_errors=True)


# ── Section 4 — Layer 3 (LZ-019) runtime control ────────────────────

# Drive face_sentinel.auth(strict_touchid=True) with the touchid
# probe returning a non-"ok" outcome and assert auth hard-exits
# before reaching the face-match step. This is the conjunction's
# CONTROL leg — even if the other two layers are bypassed, a
# strict-mode user requires Touch ID to clear the lockout that
# would otherwise let them re-enter the post-exfil-detection
# state.

import face_sentinel as fs  # noqa: E402

auth_tmpdir = Path(tempfile.mkdtemp(prefix="lz022_auth_"))
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
    fs.REF_DIR = auth_tmpdir / "reference"
    fs.CAP_DIR = auth_tmpdir / "captures"
    fs.LOG_FILE = auth_tmpdir / "sentinel.log"
    fs.STATE_FILE = auth_tmpdir / "state.json"
    fs.BG_SNAPSHOT = auth_tmpdir / "background.jpg"
    fs.REF_DIR.mkdir(parents=True, exist_ok=True)
    fs.CAP_DIR.mkdir(parents=True, exist_ok=True)
    (fs.REF_DIR / "ref_synthetic.json").write_text("{}")

    # Stub _touchid_check to return "nonzero" — a denied biometric
    # outcome. In strict mode this must abort before face compare.
    fs._touchid_check = lambda **kwargs: "nonzero"

    # Stub the downstream IO so any failure here would be a
    # control-leg breach (auth should never reach these).
    fs.capture_full = lambda path: fail(
        "LZ-019 breach: capture_full reached despite strict + nonzero")
    fs.run_face_compare = lambda *args, **kwargs: fail(
        "LZ-019 breach: run_face_compare reached despite strict + nonzero")
    fs.shrink = lambda src, dst, width=320: fail(
        "LZ-019 breach: shrink reached despite strict + nonzero")

    exit_code = None
    with contextlib.redirect_stdout(io.StringIO()):
        try:
            fs.auth(strict_touchid=True)
        except SystemExit as e:
            exit_code = e.code

    expect("LZ-019: strict+nonzero hard-exits with code 1",
           exit_code, 1)

    # Verify log entry — touchid_strict_fail with result=nonzero.
    log_events = []
    if fs.LOG_FILE.exists():
        for line in fs.LOG_FILE.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                log_events.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    strict_fail = [e for e in log_events
                   if e.get("event") == "touchid_strict_fail"]
    if not strict_fail:
        fail("LZ-019: touchid_strict_fail event not logged")
    expect("LZ-019: strict_fail result=nonzero",
           strict_fail[0].get("result"), "nonzero")

    # State must not have been mutated — auth exited before the
    # state-flip step. (If state.json exists at all, mode must
    # not be "normal".)
    if fs.STATE_FILE.exists():
        state = json.loads(fs.STATE_FILE.read_text())
        if state.get("mode") == "normal":
            fail("LZ-019: state mode flipped to 'normal' despite "
                 "strict-fail — control-leg breach")
finally:
    for k, v in saved.items():
        setattr(fs, k, v)
    shutil.rmtree(auth_tmpdir, ignore_errors=True)


# ── Section 5 — Default opt-in semantics intact ─────────────────────

# LZ-019's defensive value depends on strict_touchid being opt-in
# (default False). If a refactor silently flips the default to
# True, the conjunction's CONTROL leg becomes mandatory and the
# fail-open path for hardware-less Macs (LZ-015) breaks — a
# different kind of joint-claim attrition. Lock the default.
import inspect  # noqa: E402
sig = inspect.signature(fs.auth)
strict_param = sig.parameters.get("strict_touchid")
if strict_param is None:
    fail("LZ-019: auth() missing strict_touchid parameter")
expect("LZ-019: auth default strict_touchid=False",
       strict_param.default, False)


# ── Section 6 — Spec-level conjunction ──────────────────────────────

with open(os.path.join(REPO_ROOT, "LAZARUS_SPEC.md")) as f:
    spec = f.read()


def extract_spec_entry(spec_text, entry_header):
    start = spec_text.find(entry_header)
    if start == -1:
        fail(f"spec entry not found: {entry_header!r}")
    next_entry = spec_text.find("\n### LZ-", start + len(entry_header))
    next_section = spec_text.find("\n## ", start + len(entry_header))
    ends = [e for e in (next_entry, next_section) if e != -1]
    end = min(ends) if ends else len(spec_text)
    return spec_text[start:end]


lz022_body = extract_spec_entry(
    spec, "### LZ-022 — network-exfiltration-joint-closure")

# LZ-022 names all three components.
expect_contains("LZ-022 names LZ-005 component", lz022_body, "LZ-005")
expect_contains("LZ-022 names LZ-010 component", lz022_body, "LZ-010")
expect_contains("LZ-022 names LZ-019 component", lz022_body, "LZ-019")

# LZ-022 carries the V-NETWORK-EXFIL anchor — the attack class
# the conjunction defends against. If a refactor strips this from
# the body, the joint claim's framing weakens.
expect_contains("LZ-022 cites V-NETWORK-EXFIL anchor",
                lz022_body, "V-NETWORK-EXFIL")

# Defense triangle framing must remain — prevent + detect + control
# are the structural shape of the conjunction.
defense_triangle_keywords = ["prevent", "detect", "control"]
for kw in defense_triangle_keywords:
    if kw not in lz022_body.lower():
        fail(f"LZ-022 body missing '{kw}' framing for defense triangle")


# ── Section 7 — Component entries retain V-related framing ──────────

# The conjunction holds only if the three component entries each
# carry their angle of the V-NETWORK-EXFIL framing. If a future
# spec edit secretly removes the local-only claim from LZ-005,
# the honeypot framing from LZ-010, or the strict-mode framing
# from LZ-019, the joint claim's evidence weakens.

lz005_body = extract_spec_entry(spec, "### LZ-005 — apple-vision-local-only")
expect_contains("LZ-005 retains local-only framing",
                lz005_body.lower(), "local")

lz010_body = extract_spec_entry(
    spec, "### LZ-010 — network-honeypot-port-listeners")
expect_contains("LZ-010 retains honeypot framing",
                lz010_body.lower(), "honeypot")

lz019_body = extract_spec_entry(
    spec, "### LZ-019 — strict-touchid-hard-gate")
expect_contains("LZ-019 retains strict-mode framing",
                lz019_body.lower(), "strict")


print("PASS test_network_exfil_joint_closure.py")
