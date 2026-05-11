"""
test_touchid_check.py — exercises LZ-015 (Touch ID opportunistic
pre-face gate).

Tests the `_touchid_check` helper across all three return paths
(ok / nonzero / unavailable) using a stub runner injected via the
`_runner` parameter. The real `subprocess.run` is never invoked.

Runs locally with no extra deps:
    python3 test/test_touchid_check.py
Exit 0 on PASS, non-zero on FAIL.
"""

import os
import subprocess
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, REPO_ROOT)

import face_sentinel as fs  # noqa: E402


def expect(label, actual, expected):
    if actual != expected:
        print(f"FAIL {label}: got {actual!r}, expected {expected!r}")
        sys.exit(1)


class _FakeCompleted:
    """Minimal stand-in for subprocess.CompletedProcess. We only
    use .returncode in the helper, so that's all this exposes."""
    def __init__(self, returncode):
        self.returncode = returncode


def runner_returns(rc):
    """Stub runner that ignores its arguments and returns a
    CompletedProcess-like object with the given returncode."""
    def _r(*args, **kwargs):
        return _FakeCompleted(rc)
    return _r


def runner_raises(exc):
    """Stub runner that ignores its arguments and raises `exc`."""
    def _r(*args, **kwargs):
        raise exc
    return _r


# ── Success path ──────────────────────────────────────────────────

expect("rc_zero_is_ok",
       fs._touchid_check(_runner=runner_returns(0)),
       "ok")


# ── Nonzero return paths ──────────────────────────────────────────

# bioutil returning 1, 2, or any other non-zero code → "nonzero".
expect("rc_one_is_nonzero",
       fs._touchid_check(_runner=runner_returns(1)),
       "nonzero")
expect("rc_two_is_nonzero",
       fs._touchid_check(_runner=runner_returns(2)),
       "nonzero")
expect("rc_127_is_nonzero",
       fs._touchid_check(_runner=runner_returns(127)),
       "nonzero")
expect("rc_negative_is_nonzero",
       fs._touchid_check(_runner=runner_returns(-1)),
       "nonzero")


# ── Unavailable paths ─────────────────────────────────────────────

# bioutil missing from $PATH → FileNotFoundError → "unavailable".
expect("file_not_found_is_unavailable",
       fs._touchid_check(_runner=runner_raises(FileNotFoundError("bioutil"))),
       "unavailable")

# bioutil hangs past the timeout → TimeoutExpired → "unavailable".
# subprocess.TimeoutExpired requires (cmd, timeout) constructor args.
expect("timeout_is_unavailable",
       fs._touchid_check(
           _runner=runner_raises(subprocess.TimeoutExpired(cmd=["bioutil", "-r"],
                                                            timeout=30))),
       "unavailable")


# ── Timeout parameter is plumbed through ──────────────────────────

# Verify the helper forwards the timeout argument to the runner.
captured = {}

def capturing_runner(*args, **kwargs):
    captured["timeout"] = kwargs.get("timeout")
    return _FakeCompleted(0)

fs._touchid_check(timeout_seconds=5, _runner=capturing_runner)
expect("timeout_arg_forwarded", captured.get("timeout"), 5)


# ── Default timeout value ─────────────────────────────────────────

# Spec says default is 30s; lock it here so accidental changes trip
# the test.
captured.clear()
fs._touchid_check(_runner=capturing_runner)
expect("default_timeout_is_30", captured.get("timeout"), 30)


# ── Other exceptions propagate (NOT silently swallowed) ──────────

# Only TimeoutExpired and FileNotFoundError are caught. Anything
# else (RuntimeError, OSError for non-ENOENT reasons, etc.) should
# bubble up — silently swallowing arbitrary exceptions would mask
# bugs. Verify this by injecting a RuntimeError and expecting it
# to be raised, not converted to "unavailable".

raised = False
try:
    fs._touchid_check(_runner=runner_raises(RuntimeError("unexpected")))
except RuntimeError:
    raised = True
expect("unexpected_exception_propagates", raised, True)


print("PASS test_touchid_check.py")
