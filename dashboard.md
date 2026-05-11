# Dashboard — Lazarus

Last updated: 2026-05-11 (post-v0.1.16 — runtime-LLM-behavior transcript audit landed as LZ-020).

## Status summary

- Spec: 20 LZ-NNN entries in `LAZARUS_SPEC.md`.
- Counts: **20 / 3 / 17 / 0 / 0 / 0 / 0** (total / proved /
  tested / verified / benchmarked / argued / open).
  Three `:proved` entries (LZ-016 outliers, LZ-017 liveness
  metric, LZ-018 classification dispatcher) via hermetic
  Lean4 proofs. `:argued` and `:open` both at zero.
- Tests: 15/15 passing locally and on `macos-latest` via CI.
  - `test/test_visual_skin_decoupling.py` (LZ-001)
  - `test/test_distance_band_thresholds.py` (LZ-002)
  - `test/test_shakespeare_mode_refusal.py` (LZ-003)
  - `test/test_auth_clears_shakespeare.py` (LZ-004)
  - `test/test_no_networking_imports.sh` (LZ-005)
  - `test/test_reference_bounds.py` (LZ-006)
  - `test/test_watch_state_transitions.py` (LZ-007)
  - `test/test_peek_output.py` (LZ-008)
  - `test/test_network_monitor_classify.py` (LZ-009)
  - `test/test_honeypot_listener.py` (LZ-010)
  - `test/test_oversight_action.sh` (LZ-011)
  - `test/test_companion_readonly_discipline.py` (LZ-012)
  - `test/test_liveness_check.py` (LZ-013)
  - `test/test_prune_logic.py` (LZ-014)
  - `test/test_touchid_check.py` (LZ-015)
  - `src/lean4/Outliers.lean` (LZ-016, lean-proved, 5 theorems)
  - `src/lean4/Liveness.lean` (LZ-017, lean-proved, 4 theorems)
  - `src/lean4/Classify.lean` (LZ-018, lean-proved, 6 theorems)
  - `test/test_auth_strict_touchid.py` (LZ-019)
  - `test/test_runtime_harness.py` + `test/transcripts/` (LZ-020)
- CI: `.github/workflows/test.yml` runs the full test suite
  on `macos-latest` on every push. Outstanding:
  `actions/checkout@v4` Node.js 20 deprecation (deadline
  Sept 2026; bump when v5 ships).
- Public release shape: face sentinel + network monitor +
  honeypot + OverSight Tier 1 logger + `/lazarus` companion.

## Priority stack (highest leverage first)

The 15-entry spec is fully test-covered as of v0.1.11. The
remaining priority items are forward work — new features and
new claims, not existing-claim promotions.

1. **OverSight Tier 2** — auto-lockdown on non-allowlisted
   camera/mic activation. Documented inline in
   `oversight_action.sh`. New spec entry **LZ-016** +
   companion doc + test.

2. ~~`--strict-touchid` flag~~ — shipped at v0.1.15 as
   LZ-019. The `--no-touchid` escape hatch was considered
   and deferred; opportunistic mode (default) covers the
   hardware-less case.

3. **Runtime LLM-behavior harness** — partially addressed
   in v0.1.16 (LZ-020 transcript audit, point-in-time
   evidence). The Anthropic-API integration test (approach
   B in `docs/runtime_harness_design.md`) is held until
   model-drift becomes a concrete failure mode.

4. **LZ-002 calibration fixture set** — covered as a
   future-work open question (face-data identifiability
   problem). Adding a fixture set of (image, expected band)
   pairs would lift LZ-002's `example-tested` evidence to
   include the empirical calibration claim, not just the
   threshold-band consistency claim.

5. **Cleanup item — auth() should pop lockout_reason +
   liveness_delta** — `test_auth_clears_shakespeare.py`
   currently locks the documented behavior that these
   linger after auth. If you want auth to fully reset the
   lockout metadata, add the pops and update the test.
   Low priority; lingering data doesn't affect security
   (mode flip is what matters).

## Open questions

- **LZ-002 calibration gap.** The v0.1.7 consistency test
  locks threshold values across files but does not validate
  the empirical calibration (18/25/35 against real face
  distances). Closing this requires committing fixture
  images, which carries the face-data identifiability problem
  (real faces) or license/sourcing burden (PD historical
  portraits, AI-generated synthetics). Held until a clean
  fixture source emerges.
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

- 2026-05-11 — v0.1.16: **LZ-020 runtime-LLM-behavior
  transcript audit**. `test/transcripts/` carries two real
  /lazarus session captures (Shakespeare-mode + normal-
  mode, network values redacted) from 2026-05-10. New test
  `test_runtime_harness.py` asserts on transcript SHAPE:
  Bard vocabulary presence/absence, diagnostic field
  presence/absence, sustained refusal across 5 user turns,
  privacy-redaction guard. Plus `docs/runtime_harness_
  design.md` covering the architectural options (transcript
  / API integration / probabilistic suite) and the
  recommended staged path. Counts: 19 / 3 / 16 / 0 / 0 / 0
  / 0 → **20 / 3 / 17 / 0 / 0 / 0 / 0**.
- 2026-05-11 — v0.1.15: **`--strict-touchid` hard-gate
  flag (LZ-019)**. New CLI flag on `face_sentinel.py --auth`;
  when set, any non-"ok" Touch ID outcome exits non-zero
  before the face-match step. Default behavior (LZ-015
  opportunistic / fail-open) unchanged. New test exercises
  five branches (strict×3 outcomes + non-strict×2 outcomes)
  plus a default-parameter lock via `inspect.signature`.
  Counts: 18 / 3 / 15 / 0 / 0 / 0 / 0 → **19 / 3 / 16 / 0 /
  0 / 0 / 0**.
- 2026-05-11 — v0.1.14: **third `:proved` entry. LZ-018**
  proves the priority-ordered classification dispatcher
  underlying LZ-009 (`network_monitor.classify`).
  `src/lean4/Classify.lean` — 6 theorems: 4 priority cases
  + exhaustive + disjoint. Proof is abstracted over the
  three predicates (`is_system`, `is_known_good`,
  `is_ai_related`), so the priority order is structural
  rather than predicate-dependent. Counts:
  17 / 2 / 15 / 0 / 0 / 0 / 0 → **18 / 3 / 15 / 0 / 0 / 0 /
  0**.
- 2026-05-11 — v0.1.13: **second `:proved` entry. LZ-017**
  proves the byte-diff metric properties underlying the
  LZ-013 liveness probe (4 theorems: self-zero, symmetry,
  length-bounded, zero-iff-equal). `src/lean4/Liveness.lean`
  added alongside `Outliers.lean`. Counts:
  16 / 1 / 15 / 0 / 0 / 0 / 0 → **17 / 2 / 15 / 0 / 0 / 0 /
  0**.
- 2026-05-11 — v0.1.12: **first `:proved` entry. LZ-016**
  adds the abstract outlier-detection algorithm proved in
  Lean4 hermetically (`src/lean4/Outliers.lean`, 5 theorems:
  subset, empty, singleton, constant, monotone). Layered
  companion to LZ-014's Python implementation. Counts:
  15 / 0 / 15 / 0 / 0 / 0 / 0 → **16 / 1 / 15 / 0 / 0 / 0 /
  0**. New `src/lean4/` directory mirrors TCE's hermetic
  pattern (no Mathlib, project-local types, `lake build`
  under 1s).
- 2026-05-11 — v0.1.11: **LZ-004 + LZ-012 promoted to
  `:tested`**. Two new tests
  (`test_auth_clears_shakespeare.py` drives the full
  `auth()` flow with all IO stubbed across 4 pre-states;
  `test_companion_readonly_discipline.py` locks the six
  prohibition directives + observe/flag/watch + counter-
  positive permissive-language scan). Counts:
  15 / 0 / 13 / 0 / 0 / 2 / 0 → **15 / 0 / 15 / 0 / 0 /
  0 / 0**. **Every LZ-NNN entry now has runnable
  evidence; `:argued` and `:open` both reach zero.**
- 2026-05-11 — v0.1.10: LZ-003 Shakespeare-mode prompt-contract
  test (`test_shakespeare_mode_refusal.py`). Nine-layer static
  lint on `lazarus.md` §Shakespeare mode + `face_sentinel.py`
  auth-side mode-flip. Locks the four refusal directives,
  character-discipline anchors, and the clearing path. Same
  pattern as LZ-001 — *prompt-contract* test, not a *runtime
  LLM-behavior* test. Counts: 15 / 0 / 12 / 0 / 0 / 3 / 0 →
  **15 / 0 / 13 / 0 / 0 / 2 / 0**.
- 2026-05-10 — v0.1.9: LZ-010 honeypot loop-connect test
  (`test_honeypot_listener.py`). Binds a TEST-HTTP listener
  on port 38080 in a daemon thread, polls for bind, opens a
  fresh client socket, sends HTTP GET, verifies 200
  response + banner content, polls for log file, asserts on
  JSONL record shape. The previously-flagged CI fragility is
  addressed via poll-with-timeout + high uncommon port.
  Counts: 15 / 0 / 11 / 0 / 0 / 4 / 0 → **15 / 0 / 12 / 0 /
  0 / 3 / 0**.
- 2026-05-10 — v0.1.8: LZ-001 producer/consumer decoupling
  test (`test_visual_skin_decoupling.py`). Locks the
  architectural separation: `face_sentinel.py` (producer)
  writes mode-vocabulary literals without carrying
  presentation content; `lazarus.md` (consumer) carries the
  ASCII art + Shakespeare-mode affordance; both files
  reference the same `"normal"` / `"shakespeare"` strings;
  README §Customization documents the swap pattern. Counts:
  15 / 0 / 10 / 0 / 0 / 5 / 0 → **15 / 0 / 11 / 0 / 0 /
  4 / 0**.
- 2026-05-10 — v0.1.7: LZ-002 band-consistency test
  (`test_distance_band_thresholds.py`). Locks threshold
  values (MATCH=18.0, UNCERTAIN=25.0, LOCK=35.0), band
  ordering, Python↔Swift cross-language literal parity, and
  the calibration comment-block documentation. Honest
  framing: covers consistency, not empirical calibration
  against real faces — the latter held as future-work
  open question. Counts: 15 / 0 / 9 / 0 / 0 / 6 / 0 →
  **15 / 0 / 10 / 0 / 0 / 5 / 0**.
- 2026-05-10 — v0.1.6: LZ-005 grep-lint
  (`test_no_networking_imports.sh`). Greps `face_compare.swift`
  and `face_sentinel.py` for networking-symbol substrings on
  every CI push; size guard prevents silent pass on empty
  files. Promotes LZ-005 to `:tested`. Counts: 15 / 0 / 8 / 0
  / 0 / 7 / 0 → **15 / 0 / 9 / 0 / 0 / 6 / 0**.
- 2026-05-10 — v0.1.5: LZ-006 / LZ-007 / LZ-008 promoted from
  `:open` to `:tested`. Three new test files
  (`test_reference_bounds.py`, `test_watch_state_transitions.py`,
  `test_peek_output.py`), one drive-by bug fix in
  `prune_oldest` (under-cap negative-index guard), and one
  test affordance (`FACE_COMPARE_STUB` env var). `:open`
  count reaches zero; counts go from 15 / 0 / 5 / 0 / 0 / 7
  / 3 to **15 / 0 / 8 / 0 / 0 / 7 / 0**. CI now runs eight
  tests on every push.
- 2026-05-10 — v0.1.4: Touch ID opportunistic pre-face gate
  (LZ-015) ports from `~/Projects/Possibilistic_Security/
  face_sentinel.py`. `--auth` is now two-factor (fingerprint
  + face), fail-open if biometric hardware is unavailable.
  Three test paths (ok / nonzero / unavailable) covered via
  injected stub runner.
- 2026-05-10 — v0.1.3: leave-one-out pool quality scoring
  (LZ-014). The previous `--prune` was effectively a no-op
  (every ref scored 0 because it matched against itself);
  the new implementation builds a per-ref leave-one-out
  symlink pool and scores against that. Real-pool sweep:
  50 refs, average leave-one-out distance 0.35, no outliers.
- 2026-05-10 — v0.1.2: anti-spoof liveness probe (LZ-013) ports
  from `~/Projects/Possibilistic_Security/face_sentinel.py`.
  Two-capture byte-diff at 64×48 BMP catches static-photo
  attacks; threshold 0.008. Real face calibration ~0.015. CI
  now runs three tests.
- 2026-05-10 — v0.1.1: `.github/workflows/test.yml` lands.
  Runs both v0.1.0 tests on `macos-latest` plus a
  `face_compare` build sanity check. First run pending.
- 2026-05-10 — v0.1.0 rigor scaffold landed:
  `LAZARUS_SPEC.md`, `artifact_registry.md`, `dashboard.md`,
  `changelog.md`, `CLAUDE.md`, two passing tests, companion
  doc. LZ-009 and LZ-011 backed by runnable tests. Other 10
  entries `:argued` or `:open` with explicit promotion paths.
- 2026-05-10 — `oversight_action.sh` (Tier 1 OverSight
  forensic logger) added in commit `076795c`.
