# Lazarus v0.1.0 — first formal spec companion

Date: 2026-05-10. Owner: Aaron Green. Session: rigor uplift —
bringing Lazarus to LavaLamp / PharOS-level documentation +
test discipline.

## §1 — Computational basis

The session produced no source-code changes to the runtime
components (`face_sentinel.py`, `face_compare.swift`,
`network_monitor.py`, `network_honeypot.py`,
`oversight_action.sh`, `lazarus.md`). All changes are
documentation + tests.

Files added:

- `LAZARUS_SPEC.md` — formal spec, 12 entries.
- `artifact_registry.md` — registry table + A1–A6 self-check.
- `dashboard.md` — status + priority stack.
- `changelog.md` — versioned history; v0.1.0 entry at top.
- `CLAUDE.md` — project-local conventions.
- `test/test_oversight_action.sh` — exercises LZ-011.
- `test/test_network_monitor_classify.py` — exercises LZ-009.
- `docs/lazarus_v0_1_0_companion.md` — this file.

Dependencies: Python 3 (standard library only) for the Python
test, bash + python3 for the shell test. No new runtime deps.

Build / test commands:

```bash
chmod +x test/test_oversight_action.sh
bash test/test_oversight_action.sh
python3 test/test_network_monitor_classify.py
```

Both PASS as of this session.

Test fixture data: none committed. The OverSight test
constructs synthetic input via env-redirected `$HOME` and the
test's own PID; the network-monitor test uses dictionary
literals.

## §2 — Results

Twelve LZ-NNN spec entries cover the v0.1 public release. Two
land at `:tested` with runnable artifacts; seven at `:argued`
with cited manual evidence; three at `:open` with explicit
promotion paths.

Counts: **12 / 0 / 2 / 0 / 0 / 7 / 3** (total / proved /
tested / verified / benchmarked / argued / open).

`:tested` entries:

- **LZ-009** — network-monitor classification. The four-class
  partition (SYSTEM / KNOWN / AI_WATCH / OTHER) and the
  evaluation-order rule (SYSTEM > KNOWN > AI_WATCH > OTHER)
  are exercised by 11 assertions over synthetic connection
  records.
- **LZ-011** — oversight Tier 1 forensic logging. The script
  is invoked with `$HOME` redirected to a tempdir; the test
  asserts on JSONL shape (7 required keys), value
  correctness, UTC timestamp suffix, and append-only
  behavior across two invocations.

`:argued` entries (manual evidence cited in spec):

- LZ-001 — visual-skin / security-primitive decoupling.
- LZ-002 — face-match distance bands (18 / 25 / 35).
- LZ-003 — Shakespeare mode as companion refusal.
- LZ-004 — `--auth` clears Shakespeare. (In-session
  demonstration noted in §3.1; not yet a CI artifact.)
- LZ-005 — Apple Vision local-only.
- LZ-010 — network honeypot port listeners.
- LZ-012 — companion read-only discipline.

`:open` entries (test path documented):

- LZ-006 — reference-storage bounded.
- LZ-007 — watch-loop state transitions.
- LZ-008 — `--peek` JSON output shape.

## §3 — Verification

### §3.1 — In-session demonstration of LZ-003 / LZ-004

During the session, the live state of `~/.face_sentinel/state.
json` had `mode: "shakespeare"` set by the watch daemon at
2026-05-08T02:20:03Z (lockout reason: `liveness_fail`,
distance 1.02). The `/lazarus` companion correctly entered
Shakespeare mode on invocation, refusing diagnostics and
responding only with Bard quotes (LZ-003 demonstrated).

The owner ran `python3 face_sentinel.py --auth`, which (after
compiling the missing `face_compare` Swift binary)
authenticated successfully, set `mode: "normal"`, cleared
`lockout_time` and `lockout_distance`, and printed
`AUTH OK. Shakespeare mode cleared.` (LZ-004 demonstrated).

This is a one-shot human demonstration, not a CI-runnable
test. LZ-003 and LZ-004 are honestly held at `:argued` until
a stub-driven test exercises the state-machine transitions.

### §3.2 — LZ-009 verification

`test/test_network_monitor_classify.py` imports
`network_monitor` and asserts:

- 3 SYSTEM classifications (local subnet, loopback, Apple 17.x).
- 3 KNOWN classifications (api.anthropic.com, github.com,
  Cloudflare 1.1.1.1).
- 2 AI_WATCH classifications (`claude` / `node` to non-
  allowlisted destinations).
- 1 OTHER classification (unknown process to unknown
  destination).
- 2 evaluation-order assertions (SYSTEM > KNOWN, KNOWN >
  AI_WATCH).
- 3 defensive checks on the static allowlists themselves.

Total: 11 assertions. All pass on macOS Darwin 25.4.0
with system Python 3.

### §3.3 — LZ-011 verification

`test/test_oversight_action.sh` invokes
`oversight_action.sh` twice with synthetic OverSight argument
sets (camera-on by `$$`; microphone-off with no PID), with
`HOME` redirected to a `mktemp -d` tempdir.

Assertions:

- Log file exists at the redirected path after first invocation.
- Exactly 1 line after first invocation, exactly 2 after
  second (append-only).
- The first record contains all 7 required keys: `ts`,
  `device`, `event`, `pid`, `activeCount`, `executable`,
  `command`.
- Field values match the input arguments.
- Timestamp ends in `Z` (UTC).

Total: 6 assertions. PASS on macOS 25.4.0.

### §3.4 — Self-audit (A0 / A1–A6)

- **A0** — `CLAUDE.md` claims match observable practice
  (12 entries, 2 tested, single owner, mac-only, no deps).
- **A1** — All 12 LZ-IDs in `LAZARUS_SPEC.md` have rows in
  `artifact_registry.md`.
- **A2** — Logic tier and Status fields match between spec
  and registry; Key column compresses for table readability.
- **A3** — Tests cited at `test/test_oversight_action.sh`
  and `test/test_network_monitor_classify.py` exist and run.
  Source files cited (`face_sentinel.py`, etc.) all exist
  per `git ls-files`.
- **A4** — All `:tested` entries carry `example-tested`. All
  `:argued` entries carry `manual` or `example-tested`.
  All `:open` entries carry `none`. No status-evidence
  mismatch.
- **A5** — Counts in `LAZARUS_SPEC.md` final section,
  `artifact_registry.md` Counts section, and `dashboard.md`
  Status summary all read 12 / 0 / 2 / 0 / 0 / 7 / 3.
- **A6** — LZ-009 and LZ-011 tests run from `test/` and
  PASS locally; CI integration is queued in `dashboard.md`.

## §4 — Spec impact

This session is the spec-creation session for v0.1.0. All
twelve LZ-NNN entries are introduced here:

| LZ-ID | Key | Logic tier | Evidence type | Status |
|---|---|---|---|---|
| LZ-001 | visual-skin/security decoupling | Boundary | manual | :argued |
| LZ-002 | face-match distance bands | Operational | manual | :argued |
| LZ-003 | shakespeare-mode companion refusal | Operational | manual | :argued |
| LZ-004 | --auth clears shakespeare | Operational | example-tested | :argued |
| LZ-005 | apple-vision local-only | Boundary | manual | :argued |
| LZ-006 | reference-storage bounded | Operational | none | :open |
| LZ-007 | watch-loop state transitions | Operational | none | :open |
| LZ-008 | --peek JSON output shape | Boundary | none | :open |
| LZ-009 | network-monitor classification | Operational | example-tested | :tested |
| LZ-010 | network-honeypot port listeners | Operational | manual | :argued |
| LZ-011 | oversight Tier 1 forensic logging | Operational | example-tested | :tested |
| LZ-012 | companion read-only discipline | Boundary | manual | :argued |

Promotion queue is in `dashboard.md` §Priority stack. The
highest-leverage next step is a `FACE_COMPARE_STUB` env-var
shim in `face_sentinel.run_face_compare` that unlocks tests
for LZ-006 / LZ-007 / LZ-008 in a single small patch.
