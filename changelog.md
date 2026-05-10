# Changelog — Lazarus

## v0.1.2 — 2026-05-10 — anti-spoof liveness probe

Defends against static-photo presentation attacks (printed
photos, iPad/phone screens held up showing a still image).
Ports the byte-diff liveness check from the working version at
`~/Projects/Possibilistic_Security/face_sentinel.py` and
introduces it as a tracked spec entry.

### Added

- `face_sentinel.py`:
  - `LIVENESS_DELTA_MIN = 0.008` and
    `LIVENESS_GAP_SECONDS = 1.0` constants with calibration
    notes inline.
  - `_liveness_delta(bytes_a, bytes_b)` — pure byte-diff ratio
    helper (returns `None` on length mismatch / empty input).
  - `liveness_check(first_capture)` — full IO-bound wrapper:
    waits 1s, captures a second full-resolution frame,
    downsizes both to 64×48 BMP via `sips`, returns
    `{"live": bool, "delta": float, "reason": str}`. Fails
    open on infrastructure errors (camera retry, sips, size
    mismatch).
  - `check_once()` is_match branch now runs the liveness probe
    before accepting the match. On `static_likely`, treats as
    a mismatch with `lockout_reason="liveness_fail"` and
    `liveness_delta=<measured>` written to `state.json`.
  - `check_once()` wrapped in try/finally so `tmp_full` lives
    across the match branch (symmetric source format on both
    liveness frames; deferred deletion in finally).
- `test/test_liveness_check.py` — exercises the pure byte-diff
  helper (12 assertions), the threshold constant, the
  inequality direction (`>=` boundary), and a fixed set of
  representative deltas (static photo, calibrated real face,
  just-below / at-threshold / just-above).
- `LAZARUS_SPEC.md` — new LZ-013 entry under v0.1.2 section.
- `artifact_registry.md` — LZ-013 row + counts bumped.
- `.github/workflows/test.yml` — CI now runs the liveness test.
- `docs/lazarus_liveness_v0_1_2_companion.md` — companion doc
  per the standard.

### Status changes

- LZ-013 enters the spec at `:tested` (pure byte-diff math is
  test-backed; IO-bound wrapper covered by manual evidence in
  the companion doc).
- Counts: 12 / 0 / 2 / 0 / 0 / 7 / 3 → **13 / 0 / 3 / 0 / 0 /
  7 / 3**.

### Why now

User flagged that the v0.1.0 sentinel could be defeated by
holding up a printed photo. The liveness check was already
present in the personal working copy at `~/Projects/
Possibilistic_Security/face_sentinel.py` but had never been
ported to the public lazarus repo. This commit closes that gap.

### Notes

- Catches: printed photos, iPad/phone-screen replays of a still
  image.
- Misses: video playback, 3D-printed mask, deepfake stream
  (v2 territory — active illumination flash / blink challenge
  / depth sensor).
- The threshold (0.008) is calibrated against a single
  developer's real-face data (~0.015 sitting still). A fixture
  set of attack-vector captures with measured deltas would
  promote this from `:tested` to a stronger evidence tier.

## v0.1.1 — 2026-05-10 — CI on macos-latest

### Added

- `.github/workflows/test.yml` — runs the v0.1.0 test suite on
  `macos-latest` on every push to master and on every pull
  request. Two test steps:
  - LZ-011 — `bash test/test_oversight_action.sh`
  - LZ-009 — `python3 test/test_network_monitor_classify.py`
  Plus a `face_compare` Swift build sanity check (verifies the
  swiftc invocation in the README install steps still works
  on a clean macOS runner). Timeout: 5 minutes.

### Status changes

- None at the spec level. CI integration was the next-cheapest
  promotion in the priority stack but doesn't itself raise any
  LZ-NNN status — it makes the existing `:tested` entries
  load-bearing on every push, which is the operational value.

### Notes

- macOS-only by design (Apple Vision). No Linux/Windows runner.
- First CI run will land when this commit pushes to master;
  the workflow has not yet been observed to pass on a GitHub
  runner. If it fails, the fix is in the workflow file or in
  the test scripts — no spec changes required.

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
