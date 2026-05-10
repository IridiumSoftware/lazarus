"""
test_network_monitor_classify.py — exercises LZ-009
(network-monitor classification).

Imports network_monitor.classify directly and asserts on the
four-class partition (SYSTEM / KNOWN / AI_WATCH / OTHER) plus
the explicit evaluation-order rule (SYSTEM > KNOWN > AI_WATCH >
OTHER).

Runs locally on macOS or Linux:
    python3 test/test_network_monitor_classify.py
Exit 0 on PASS, non-zero on FAIL.
"""

import os
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, REPO_ROOT)

import network_monitor as nm  # noqa: E402


def expect(label, conn, expected):
    actual = nm.classify(conn)
    if actual != expected:
        print(f"FAIL {label}: classify({conn!r}) -> {actual!r}, expected {expected!r}")
        sys.exit(1)


# SYSTEM: any connection to a SYSTEM_PREFIXES address, regardless of process.
expect("system_local_subnet",
       {"process": "node", "connection": "node->192.168.50.1:443"},
       "SYSTEM")
expect("system_loopback",
       {"process": "claude", "connection": "claude->127.0.0.1:8080"},
       "SYSTEM")
expect("system_apple_17",
       {"process": "node", "connection": "node->17.253.1.2:443"},
       "SYSTEM")

# KNOWN: known-good destination, but not on a SYSTEM prefix.
expect("known_anthropic",
       {"process": "node", "connection": "node->api.anthropic.com:443"},
       "KNOWN")
expect("known_github",
       {"process": "git", "connection": "git->github.com:22"},
       "KNOWN")
expect("known_cloudflare",
       {"process": "curl", "connection": "curl->1.1.1.1:443"},
       "KNOWN")

# AI_WATCH: AI process, not system, not known-good.
expect("ai_watch_claude_unknown",
       {"process": "claude", "connection": "claude->203.0.113.5:443"},
       "AI_WATCH")
expect("ai_watch_node_unknown",
       {"process": "node", "connection": "node->203.0.113.5:443"},
       "AI_WATCH")

# OTHER: non-AI process, non-system, non-known-good.
expect("other_unknown_process",
       {"process": "weirdthing", "connection": "weirdthing->203.0.113.5:443"},
       "OTHER")

# Order rule: SYSTEM beats KNOWN even when destination is in KNOWN_GOOD.
# (A connection to api.anthropic.com over loopback would be both, but the
# textual representation of "->" puts the destination after the arrow, and
# is_system tests the literal prefix on the whole string, so a 127.0.0.1
# destination is SYSTEM regardless of process.)
expect("order_system_over_known",
       {"process": "node", "connection": "node->127.0.0.1:443"},
       "SYSTEM")

# Order rule: KNOWN beats AI_WATCH (so AI processes hitting allowlisted
# destinations are KNOWN, not flagged).
expect("order_known_over_ai",
       {"process": "claude", "connection": "claude->api.anthropic.com:443"},
       "KNOWN")

# Allowlist surface — defensive checks on the module's static config so
# accidental deletions trip the test.
assert "api.anthropic.com" in nm.KNOWN_GOOD, "KNOWN_GOOD lost api.anthropic.com"
assert "claude" in nm.AI_PROCESSES, "AI_PROCESSES lost claude"
assert any(p.startswith("192.168.") for p in nm.SYSTEM_PREFIXES), \
    "SYSTEM_PREFIXES lost 192.168."

print("PASS test_network_monitor_classify.py")
