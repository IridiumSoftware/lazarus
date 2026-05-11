# artifact_registry.md — Lazarus

Version: 0.1.8 (LZ-001 promoted from :argued to :tested via
producer/consumer decoupling test on 2026-05-10; same-day
arc covers v0.1.0 first formal spec through v0.1.8.
Fifteen LZ-NNN spec entries; eleven backed by runnable
tests. The remaining four `:argued` are prompt-layer LLM-
behavior claims (LZ-003/004/012) and the honeypot loop-
connect (LZ-010). Counts: 15 / 0 / 11 / 0 / 0 / 4 / 0.)

## Coverage rule

Every spec LZ-ID must have a row here. `git ls-files` must
contain every Test/Proof and Source path listed.

## Columns

- **LZ-ID** — matches `LAZARUS_SPEC.md`.
- **Key** — short name from the spec entry.
- **Logic tier** — `Core` / `Operational` / `Boundary`.
- **Evidence type** — `lean-proved` / `type-checked` /
  `algebraic` / `property-tested` / `example-tested` /
  `benchmarked` / `manual` / `none`.
- **Test/Proof file** — path to the artifact establishing the
  claim. `—` if none yet.
- **Source file** — path to the implementation the claim
  describes. `—` if none yet.
- **Status** — `:proved` / `:verified` / `:tested` /
  `:benchmarked` / `:argued` / `:open`.

---

## Spec entries

| LZ-ID | Key | Logic tier | Evidence type | Test/Proof file | Source file | Status |
|---|---|---|---|---|---|---|
| LZ-001 | visual-skin/security decoupling | Boundary | example-tested | test/test_visual_skin_decoupling.py (producer/consumer architecture lint: mode-vocab vocabulary parity + forbidden presentation-content patterns + skin-in-consumer + README/spec doc anchors) | face_sentinel.py (producer) + lazarus.md (consumer) | :tested |
| LZ-002 | face-match distance bands | Operational | example-tested | test/test_distance_band_thresholds.py (consistency surface: Python constants + band ordering + Swift literal parity + comment-block doc lock) | face_compare.swift (cmdMatch thresholds) + face_sentinel.py (MATCH/UNCERTAIN/LOCK_THRESHOLD constants) | :tested |
| LZ-003 | shakespeare-mode companion refusal | Operational | manual | lazarus.md §Shakespeare mode + LAZARUS_SPEC.md LZ-003 | lazarus.md (companion prompt) + face_sentinel.py (mode field in state.json) | :argued |
| LZ-004 | --auth clears shakespeare | Operational | example-tested | docs/lazarus_v0_1_0_companion.md §3.1 (in-session demo) | face_sentinel.py auth() lines 188–205 | :argued |
| LZ-005 | apple-vision local-only | Boundary | example-tested | test/test_no_networking_imports.sh (grep-lint on every CI push + non-trivial-size guard) | face_compare.swift + face_sentinel.py (no networking imports) | :tested |
| LZ-006 | reference-storage bounded | Operational | example-tested | test/test_reference_bounds.py | face_sentinel.py prune_oldest() + enroll() + MAX_REFERENCES constant | :tested |
| LZ-007 | watch-loop state transitions | Operational | example-tested | test/test_watch_state_transitions.py (8 branches + 2 early-return paths via module-patching) | face_sentinel.py check_once() | :tested |
| LZ-008 | --peek JSON output shape | Boundary | example-tested | test/test_peek_output.py (5 branches via FACE_COMPARE_STUB env-var + monkey-patched capture_full) | face_sentinel.py peek() | :tested |
| LZ-009 | network-monitor classification | Operational | example-tested | test/test_network_monitor_classify.py | network_monitor.py classify() + AI_PROCESSES + KNOWN_GOOD + SYSTEM_PREFIXES | :tested |
| LZ-010 | network-honeypot port listeners | Operational | manual | LAZARUS_SPEC.md LZ-010 + README.md §What it does | network_honeypot.py | :argued |
| LZ-011 | oversight Tier 1 forensic logging | Operational | example-tested | test/test_oversight_action.sh | oversight_action.sh | :tested |
| LZ-012 | companion read-only discipline | Boundary | manual | lazarus.md §What you do NOT do + LAZARUS_SPEC.md LZ-012 | lazarus.md | :argued |
| LZ-013 | anti-spoof liveness probe | Operational | example-tested | test/test_liveness_check.py + docs/lazarus_liveness_v0_1_2_companion.md (manual evidence for the IO-bound wrapper) | face_sentinel.py _liveness_delta() + liveness_check() + check_once() is_match branch + LIVENESS_DELTA_MIN/LIVENESS_GAP_SECONDS constants | :tested |
| LZ-014 | reference-pool leave-one-out pruning | Operational | example-tested | test/test_prune_logic.py + docs/lazarus_prune_v0_1_3_companion.md (manual evidence for the IO-bound _prune_score_one) | face_sentinel.py _outliers_from_scores() + _prune_score_one() + prune_cmd() + PRUNE_OUTLIER_MULTIPLIER constant | :tested |
| LZ-015 | Touch ID opportunistic pre-face gate | Operational | example-tested | test/test_touchid_check.py + docs/lazarus_touchid_v0_1_4_companion.md (manual evidence for real bioutil invocation) | face_sentinel.py _touchid_check() + auth() Step 1 block | :tested |

## Counts

- Total: 15
- `:proved`: 0
- `:tested`: 11 (LZ-001, LZ-002, LZ-005, LZ-006, LZ-007, LZ-008,
  LZ-009, LZ-011, LZ-013, LZ-014, LZ-015)
- `:verified`: 0
- `:benchmarked`: 0
- `:argued`: 4 (LZ-003, LZ-004, LZ-010, LZ-012)
- `:open`: 0

## Cross-audit A1–A6 self-check (post-v0.1.8)

- **A1 — Coverage.** Every LZ-ID in `LAZARUS_SPEC.md` has a row
  here. ✓ (15 of 15).
- **A2 — Logic & Status parity.** Spec → registry Logic tier and
  Status fields match exactly. Key column compresses spec keys
  for table readability (e.g. spec
  "visual-skin/security-primitive decoupling" → registry
  "visual-skin/security decoupling"); LZ-ID is the canonical
  link. ✓.
- **A3 — Evidence exists.** All 11 `:tested` entries cite
  runnable artifacts under `test/`:
  - LZ-001 → `test/test_visual_skin_decoupling.py`
  - LZ-002 → `test/test_distance_band_thresholds.py`
  - LZ-005 → `test/test_no_networking_imports.sh`
  - LZ-006 → `test/test_reference_bounds.py`
  - LZ-007 → `test/test_watch_state_transitions.py`
  - LZ-008 → `test/test_peek_output.py`
  - LZ-009 → `test/test_network_monitor_classify.py`
  - LZ-011 → `test/test_oversight_action.sh`
  - LZ-013 → `test/test_liveness_check.py` +
    `docs/lazarus_liveness_v0_1_2_companion.md`
  - LZ-014 → `test/test_prune_logic.py` +
    `docs/lazarus_prune_v0_1_3_companion.md`
  - LZ-015 → `test/test_touchid_check.py` +
    `docs/lazarus_touchid_v0_1_4_companion.md`
  The four `:argued` entries cite manual evidence in spec /
  companion / README. The `:open` count is zero.
- **A4 — Status honesty.** Eleven `:tested` entries carry
  `example-tested`. Four `:argued` entries carry `manual` or
  `example-tested` (LZ-004 has an in-session demonstration
  but no CI artifact yet). No `:open` entries remain. No
  entry has a status its evidence type cannot support.
- **A5 — Stale counts.** Counts above (15 / 0 / 11 / 0 / 0 /
  4 / 0) match `LAZARUS_SPEC.md` final-section counts and
  `dashboard.md` summary.
- **A6 — Test sync.** All 11 `:tested` entries are exercised
  by tests under `test/` that run on `macos-latest` via
  `.github/workflows/test.yml` on every push. Locally:
  `bash test/test_oversight_action.sh`,
  `python3 test/test_network_monitor_classify.py`,
  `python3 test/test_liveness_check.py`,
  `python3 test/test_prune_logic.py`,
  `python3 test/test_touchid_check.py`,
  `python3 test/test_reference_bounds.py`,
  `python3 test/test_peek_output.py`,
  `python3 test/test_watch_state_transitions.py`,
  `bash test/test_no_networking_imports.sh`,
  `python3 test/test_distance_band_thresholds.py`,
  `python3 test/test_visual_skin_decoupling.py`.

## Dependencies on other Triad-Deployment spec entries

Lazarus is the most-mature deployment in the Triad and stands on
its own; it does not yet share artifacts with LavaLamp or PharOS.
Cross-deployment dependencies (e.g. consuming LavaLamp's
heartbeat for additional auth gating) are out of scope for v0.1
and would be tracked here as Lazarus spec entries acquire LL-NNN
or PH-NNN prerequisites.
