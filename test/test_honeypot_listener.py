"""
test_honeypot_listener.py — exercises LZ-010 (network-honeypot
port listeners).

Loop-connect integration test:
1. Monkey-patch LOG_DIR to a tempdir.
2. Start `listen_on_port(38080, "TEST-HTTP", serve_http)` in a
   daemon thread (dies cleanly when the test process exits).
3. Poll for the listener to actually bind (via `127.0.0.1`
   connect with timeout — no fixed sleeps).
4. Open a fresh client socket, send a minimal HTTP GET.
5. Verify the response is an HTTP 200 with the banner content.
6. Poll for the log file to appear (log_connection runs AFTER
   sendall, so there's a brief window between client-receives
   and log-on-disk).
7. Verify the JSONL log record shape.

Fragility notes — what could fail and why it's acceptable:
- **Port 38080 already bound on CI runner.** The
  poll-for-binding step times out and reports a clear FAIL.
  Picking a high uncommon port keeps the collision odds low;
  if it ever does happen, the failure mode is "test fails
  loudly" not "test silently passes."
- **Log-write race.** log_connection runs AFTER sendall;
  the client could observe the response before the server
  completes the write. Polling for the file with a 5s
  timeout handles this without a fixed sleep.

Runs locally on macOS or Linux:
    python3 test/test_honeypot_listener.py
Exit 0 on PASS, non-zero on FAIL.
"""

import json
import os
import shutil
import socket
import sys
import tempfile
import threading
import time
from datetime import datetime
from pathlib import Path

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, REPO_ROOT)

import network_honeypot as nh  # noqa: E402


def fail(msg):
    print(f"FAIL test_honeypot_listener.py: {msg}")
    sys.exit(1)


# ── Setup tempdir for logs ─────────────────────────────────────────

tmpdir = tempfile.mkdtemp(prefix="lz010_")
saved_log_dir = nh.LOG_DIR
nh.LOG_DIR = tmpdir


# ── Pick a high uncommon port ──────────────────────────────────────

PORT = 38080


# ── Start listener in daemon thread ────────────────────────────────

listener_thread = threading.Thread(
    target=nh.listen_on_port,
    args=(PORT, "TEST-HTTP", nh.serve_http),
    daemon=True,
)
listener_thread.start()


# ── Poll for the listener to bind ──────────────────────────────────

bind_deadline = time.time() + 5.0
bound = False
while time.time() < bind_deadline:
    probe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    probe.settimeout(0.5)
    try:
        probe.connect(("127.0.0.1", PORT))
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
    shutil.rmtree(tmpdir, ignore_errors=True)
    fail(f"listener never bound on port {PORT} within 5s — "
         f"is the port in use? (this is the known fragility)")


# ── Loop-connect: send HTTP GET, read response ─────────────────────

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.settimeout(3.0)
try:
    client.connect(("127.0.0.1", PORT))
    client.sendall(b"GET / HTTP/1.0\r\nHost: localhost\r\n\r\n")

    response = b""
    end = time.time() + 3.0
    while time.time() < end:
        try:
            chunk = client.recv(4096)
            if not chunk:
                break
            response += chunk
        except socket.timeout:
            break
finally:
    try:
        client.close()
    except Exception:
        pass


# ── Verify response shape ──────────────────────────────────────────

if b"200" not in response:
    nh.LOG_DIR = saved_log_dir
    shutil.rmtree(tmpdir, ignore_errors=True)
    fail(f"expected HTTP 200 in response, got: {response[:200]!r}")

# DEFAULT_BANNER contains "monitored honeypot" — the response should
# echo that text in the body. (If a HONEYPOT_BANNER.txt has been
# placed next to network_honeypot.py the content will be different;
# the test in that case looks for any substring of the configured
# banner.)
banner_text = nh.BANNER_CONTENT.strip()
if banner_text and banner_text.encode() not in response:
    nh.LOG_DIR = saved_log_dir
    shutil.rmtree(tmpdir, ignore_errors=True)
    fail(f"expected banner content in response, got: {response[:300]!r}")


# ── Poll for log file ──────────────────────────────────────────────

today = datetime.now().strftime("%Y-%m-%d")
log_path = os.path.join(tmpdir, f"honeypot_{today}.jsonl")
log_deadline = time.time() + 5.0
while time.time() < log_deadline:
    if os.path.exists(log_path) and os.path.getsize(log_path) > 0:
        break
    time.sleep(0.05)

if not os.path.exists(log_path):
    nh.LOG_DIR = saved_log_dir
    shutil.rmtree(tmpdir, ignore_errors=True)
    fail(f"log file never appeared at {log_path} within 5s")


# ── Verify JSONL record shape ──────────────────────────────────────

with open(log_path) as f:
    lines = [line.strip() for line in f if line.strip()]

if not lines:
    nh.LOG_DIR = saved_log_dir
    shutil.rmtree(tmpdir, ignore_errors=True)
    fail("log file exists but is empty")

try:
    record = json.loads(lines[0])
except json.JSONDecodeError as e:
    nh.LOG_DIR = saved_log_dir
    shutil.rmtree(tmpdir, ignore_errors=True)
    fail(f"log line is not valid JSON: {e}: {lines[0]!r}")

required_fields = {"timestamp", "remote", "port", "service"}
missing = required_fields - record.keys()
if missing:
    nh.LOG_DIR = saved_log_dir
    shutil.rmtree(tmpdir, ignore_errors=True)
    fail(f"log record missing required fields: {sorted(missing)}: {record!r}")

if record["service"] != "HTTP":
    nh.LOG_DIR = saved_log_dir
    shutil.rmtree(tmpdir, ignore_errors=True)
    fail(f"log record service mismatch: {record['service']!r} != 'HTTP'")

if record["port"] != PORT:
    nh.LOG_DIR = saved_log_dir
    shutil.rmtree(tmpdir, ignore_errors=True)
    fail(f"log record port mismatch: {record['port']!r} != {PORT}")

# remote is "<ip>:<port>" of the connecting client. Sanity check
# format: at least one colon, IP portion non-empty.
if ":" not in record["remote"] or not record["remote"].split(":")[0]:
    nh.LOG_DIR = saved_log_dir
    shutil.rmtree(tmpdir, ignore_errors=True)
    fail(f"log record remote field malformed: {record['remote']!r}")


# ── SERVICES table sanity check ────────────────────────────────────

# Lock the documented port → service mapping so it doesn't silently
# drift. The spec entry names these specific ports.
expected_services = {
    8080: "HTTP-Admin",
    2222: "SSH",
    21: "FTP",
    3306: "MySQL",
    8443: "HTTPS-Mgmt",
}
for port, name in expected_services.items():
    if port not in nh.SERVICES:
        nh.LOG_DIR = saved_log_dir
        shutil.rmtree(tmpdir, ignore_errors=True)
        fail(f"SERVICES table missing port {port}")
    actual_name, _ = nh.SERVICES[port]
    if actual_name != name:
        nh.LOG_DIR = saved_log_dir
        shutil.rmtree(tmpdir, ignore_errors=True)
        fail(f"SERVICES[{port}] name {actual_name!r} != {name!r}")


# ── Teardown ───────────────────────────────────────────────────────

nh.LOG_DIR = saved_log_dir
shutil.rmtree(tmpdir, ignore_errors=True)
print("PASS test_honeypot_listener.py")
