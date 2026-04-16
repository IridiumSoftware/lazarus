"""
network_monitor.py — AI Tool Network Monitor
═════════════════════════════════════════════

Monitors outbound connections from AI tools and logs them.
Know what your AI agents are talking to and when.

Run: python3 network_monitor.py
Run continuous: python3 network_monitor.py --watch
Run with logging: python3 network_monitor.py --watch --log
"""

import subprocess
import sys
import time
import json
import os
from datetime import datetime

# Processes to watch — add your AI tool process names here
AI_PROCESSES = {
    "claude",
    "anthropic",
    "node",           # Claude Code runs on node
    "python",         # Many AI tools run as python
    "curl",           # API calls
    "wget",
    "git",            # Pushing to repos
    "ssh",
    "gpg",
}

# Known-good destinations (won't alert, still logged)
# Customize this for your setup
KNOWN_GOOD = {
    "api.anthropic.com",
    "github.com",
    "ssh.github.com",
    "objects.githubusercontent.com",
    "api.github.com",
    "1.1.1.1",
    "1.0.0.1",
    "keys.openpgp.org",
}

# System / local destinations (suppress noise)
SYSTEM_PREFIXES = [
    "17.",              # Apple
    "192.168.",         # Local
    "127.0.0.1",        # Localhost
    "10.",              # Local
    "::1",              # IPv6 localhost
]

LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")


def get_connections():
    """Get current outbound connections using lsof."""
    try:
        result = subprocess.run(
            ["lsof", "-i", "-n", "-P", "+c", "0"],
            capture_output=True, text=True, timeout=10
        )
        connections = []
        for line in result.stdout.strip().split("\n")[1:]:
            parts = line.split()
            if len(parts) >= 9:
                name = parts[8] if len(parts) > 8 else ""
                if "ESTABLISHED" not in line and "->" not in name:
                    continue
                connections.append({
                    "process": parts[0],
                    "pid": parts[1],
                    "user": parts[2],
                    "connection": name,
                    "full_line": line,
                })
        return connections
    except Exception as e:
        print(f"  Error reading connections: {e}")
        return []


def is_ai_related(conn):
    proc = conn["process"].lower()
    return any(ai in proc for ai in AI_PROCESSES)


def is_system(conn):
    dest = conn["connection"]
    return any(dest.startswith(p) or f"->{p}" in dest for p in SYSTEM_PREFIXES)


def is_known_good(conn):
    dest = conn["connection"]
    return any(kg in dest for kg in KNOWN_GOOD)


def classify(conn):
    if is_system(conn):
        return "SYSTEM"
    if is_known_good(conn):
        return "KNOWN"
    if is_ai_related(conn):
        return "AI_WATCH"
    return "OTHER"


def display(connections, show_all=False):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n{'='*60}")
    print(f"  Network Monitor — {now}")
    print(f"{'='*60}")

    ai_conns = []
    unknown_conns = []
    known_count = 0
    system_count = 0

    for conn in connections:
        cls = classify(conn)
        if cls == "AI_WATCH":
            ai_conns.append(conn)
        elif cls == "OTHER":
            unknown_conns.append(conn)
        elif cls == "KNOWN":
            known_count += 1
        elif cls == "SYSTEM":
            system_count += 1

    if ai_conns:
        print(f"\n  AI TOOL CONNECTIONS ({len(ai_conns)}):")
        for c in ai_conns:
            print(f"    > {c['process']} (PID {c['pid']}): {c['connection']}")

    if unknown_conns:
        print(f"\n  UNKNOWN CONNECTIONS ({len(unknown_conns)}):")
        for c in unknown_conns:
            kg = "+" if is_known_good(c) else "?"
            print(f"    {kg} {c['process']} (PID {c['pid']}): {c['connection']}")

    if show_all:
        print(f"\n  Known-good: {known_count} | System/local: {system_count}")

    if not ai_conns and not unknown_conns:
        print(f"\n  All clear. {known_count} known-good, {system_count} system.")

    print(f"{'='*60}")
    return ai_conns, unknown_conns


def log_to_file(connections):
    os.makedirs(LOG_DIR, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    log_path = os.path.join(LOG_DIR, f"network_{today}.jsonl")

    now = datetime.now().isoformat()
    with open(log_path, "a") as f:
        for conn in connections:
            entry = {
                "timestamp": now,
                "process": conn["process"],
                "pid": conn["pid"],
                "connection": conn["connection"],
                "classification": classify(conn),
            }
            f.write(json.dumps(entry) + "\n")


def run_once(show_all=False, log=False):
    conns = get_connections()
    ai, unknown = display(conns, show_all=show_all)
    if log:
        log_to_file(conns)
    return ai, unknown


def watch(interval=10, log=False):
    print(f"Watching every {interval}s. Ctrl+C to stop.")
    try:
        while True:
            run_once(show_all=True, log=log)
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    args = sys.argv[1:]

    if "--watch" in args:
        do_log = "--log" in args
        interval = 10
        for a in args:
            if a.isdigit():
                interval = int(a)
        watch(interval=interval, log=do_log)
    else:
        do_log = "--log" in args
        run_once(show_all=True, log=do_log)
