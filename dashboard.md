# Dashboard — Lazarus

Last updated: 2026-05-10 (post-v0.1.0 rigor scaffold).

## Status summary

- Spec: 12 LZ-NNN entries in `LAZARUS_SPEC.md`.
- Counts: **12 / 0 / 2 / 0 / 0 / 7 / 3** (total / proved /
  tested / verified / benchmarked / argued / open).
- Tests: 2/2 passing locally.
  - `test/test_network_monitor_classify.py` (LZ-009)
  - `test/test_oversight_action.sh` (LZ-011)
- CI: not yet wired. `.github/workflows/test.yml` is the next
  cheap promotion.
- Public release shape: face sentinel + network monitor +
  honeypot + OverSight Tier 1 logger + `/lazarus` companion.

## Priority stack (highest leverage first)

1. **Wire CI** — `.github/workflows/test.yml` running both
   tests on `macos-latest`. Lazarus is mac-only by design
   (Apple Vision), so no Linux runner. ~15 minutes.

2. **LZ-006 / LZ-007 / LZ-008 promotion** — three `:open`
   entries that all become `:tested` once `face_compare` is
   stub-able. Suggested approach: introduce a
   `FACE_COMPARE_STUB=<json>` env var that
   `run_face_compare()` reads first; if set, return the
   parsed JSON instead of invoking the binary. One small
   patch unlocks all three tests.

3. **LZ-005 grep-lint** — CI step that grep-fails on
   networking imports (`URLSession`, `Network`, `urllib`,
   `requests`, `socket`) in `face_compare.swift` /
   `face_sentinel.py`. Promotes LZ-005 to `:tested`. ~10
   minutes.

4. **LZ-002 fixture set** — small set of (image, expected
   band) JPEGs for the distance-band claim. Requires care to
   not commit identifiable face data; consider synthetic /
   public-domain reference images. Promotes LZ-002 to
   `:tested`.

5. **OverSight Tier 2** — auto-lockdown on non-allowlisted
   camera/mic activation. Documented inline in
   `oversight_action.sh`. New spec entry LZ-013 + companion
   doc + test.

6. **LZ-010 honeypot loop-connect test** — fragile in CI;
   defer until the rest of the stack is green.

## Open questions

- Cross-deployment dependency planning. LavaLamp's heartbeat
  channel (LL-039) could augment Lazarus auth ("Lazarus
  re-auth requires LavaLamp daemon liveness within N seconds")
  — same pattern PharOS already uses. New spec entry if
  pursued.
- Should the `lazarus.md` slash-command file in the public
  repo and the `~/.claude/skills/lazarus.md` (or wherever
  user installs it) stay verbatim-synced, or are user-level
  customizations expected? The README §Customization says
  "Bring your own checks / lockout mode / VPN", which
  implies divergence. Suggests we don't try to enforce
  identity.

## Recently completed

- 2026-05-10 — v0.1.0 rigor scaffold landed:
  `LAZARUS_SPEC.md`, `artifact_registry.md`, `dashboard.md`,
  `changelog.md`, `CLAUDE.md`, two passing tests, companion
  doc. LZ-009 and LZ-011 backed by runnable tests. Other 10
  entries `:argued` or `:open` with explicit promotion paths.
- 2026-05-10 — `oversight_action.sh` (Tier 1 OverSight
  forensic logger) added in commit `076795c`.
