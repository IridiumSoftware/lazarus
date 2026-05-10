# Changelog — Lazarus

## v0.1.0 — 2026-05-10 — first formal spec of the public release

The public release is now backed by the standard Triad-Deployment
rigor stack (mirrors LavaLamp + PharOS). Twelve LZ-NNN spec
entries, two `:tested` and seven `:argued`. Two runnable tests
land at `test/`; other promotions are explicitly queued in
`dashboard.md`.

### Added

- `LAZARUS_SPEC.md` — formal spec, 12 entries (LZ-001 through
  LZ-012). Counts: 12 / 0 / 2 / 0 / 0 / 7 / 3.
- `artifact_registry.md` — every spec entry has a registry
  row; A1–A6 self-check passes.
- `dashboard.md` — status summary + priority stack + open
  questions.
- `changelog.md` — this file; future bumps go above this entry.
- `CLAUDE.md` — project-local conventions for working on this
  repo (mirrors LavaLamp + the project-level Triad CLAUDE.md
  pattern).
- `test/test_oversight_action.sh` — exercises LZ-011 (OverSight
  Tier 1 forensic logging). Redirects `$HOME` to a tempdir,
  invokes the script with synthetic args, asserts on JSONL
  shape and append-only behavior.
- `test/test_network_monitor_classify.py` — exercises LZ-009
  (network-monitor classification). Imports `network_monitor`
  directly and asserts on the SYSTEM > KNOWN > AI_WATCH >
  OTHER partition + the explicit allowlist surface.
- `docs/lazarus_v0_1_0_companion.md` — permanent record of this
  rigor session per the companion-doc standard.

### Status changes

- LZ-009 and LZ-011 enter the spec at `:tested` (both have
  runnable tests).
- LZ-001, LZ-002, LZ-003, LZ-004, LZ-005, LZ-010, LZ-012 enter
  at `:argued` (manual evidence in spec / README / inline
  comments).
- LZ-006, LZ-007, LZ-008 enter at `:open` with explicit
  promotion paths to `:tested` once `face_compare` is
  stub-able.

### Notes

- No code in `face_sentinel.py`, `face_compare.swift`,
  `network_monitor.py`, `network_honeypot.py`, or
  `oversight_action.sh` was modified by this commit. The
  rigor uplift is documentation + tests only.
- The README is unchanged (already user-facing); contributors
  are pointed at `LAZARUS_SPEC.md` and `CLAUDE.md` from a
  short addition near the top of the README.

## v0.0.1 (initial public release)

- `lazarus.md` slash command.
- `face_sentinel.py` + `face_compare.swift` (Apple Vision
  feature-print matcher).
- `network_monitor.py` + `network_honeypot.py`.
- README, LICENSE.
- Pushed to github.com/IridiumSoftware/lazarus on initial
  commit `b6b0a8c`.
