# artifact_registry.md — Lazarus

Version: 0.1.16 (LZ-020 — runtime-LLM-behavior transcript
audit — added 2026-05-11; recorded-transcript stub for the
prompt-layer claims plus a design doc covering the broader
runtime-harness architecture. Counts: 20 / 3 / 17 / 0 / 0 /
0 / 0.)

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
| LZ-003 | shakespeare-mode companion refusal | Operational | example-tested | test/test_shakespeare_mode_refusal.py (9-layer prompt-contract lint: section anchor + CHECK-THIS-FIRST + state-path + mode-vocab + 4 refusal directives + clearing path + producer mode-flip + character-discipline anchors + spec phrase lock) | lazarus.md §Shakespeare mode (consumer) + face_sentinel.py auth/check_once (producer mode set/clear) | :tested |
| LZ-004 | --auth clears shakespeare | Operational | example-tested | test/test_auth_clears_shakespeare.py (4 pre-state branches: shakespeare-clear, fresh, empty, lockout_reason-linger; full auth() drive with all IO stubbed) | face_sentinel.py auth() | :tested |
| LZ-005 | apple-vision local-only | Boundary | example-tested | test/test_no_networking_imports.sh (grep-lint on every CI push + non-trivial-size guard) | face_compare.swift + face_sentinel.py (no networking imports) | :tested |
| LZ-006 | reference-storage bounded | Operational | example-tested | test/test_reference_bounds.py | face_sentinel.py prune_oldest() + enroll() + MAX_REFERENCES constant | :tested |
| LZ-007 | watch-loop state transitions | Operational | example-tested | test/test_watch_state_transitions.py (8 branches + 2 early-return paths via module-patching) | face_sentinel.py check_once() | :tested |
| LZ-008 | --peek JSON output shape | Boundary | example-tested | test/test_peek_output.py (5 branches via FACE_COMPARE_STUB env-var + monkey-patched capture_full) | face_sentinel.py peek() | :tested |
| LZ-009 | network-monitor classification | Operational | example-tested | test/test_network_monitor_classify.py | network_monitor.py classify() + AI_PROCESSES + KNOWN_GOOD + SYSTEM_PREFIXES | :tested |
| LZ-010 | network-honeypot port listeners | Operational | example-tested | test/test_honeypot_listener.py (loop-connect on 127.0.0.1:38080: bind + HTTP GET + 200 response + banner content + JSONL log record shape + SERVICES table lock) | network_honeypot.py | :tested |
| LZ-011 | oversight Tier 1 forensic logging | Operational | example-tested | test/test_oversight_action.sh | oversight_action.sh | :tested |
| LZ-012 | companion read-only discipline | Boundary | example-tested | test/test_companion_readonly_discipline.py (6-prohibition + observe/flag/watch + counter-positive permissive-language scan + README discipline phrasing lock) | lazarus.md §What you do NOT do + README.md top-of-file discipline phrasing | :tested |
| LZ-013 | anti-spoof liveness probe | Operational | example-tested | test/test_liveness_check.py + docs/lazarus_liveness_v0_1_2_companion.md (manual evidence for the IO-bound wrapper) | face_sentinel.py _liveness_delta() + liveness_check() + check_once() is_match branch + LIVENESS_DELTA_MIN/LIVENESS_GAP_SECONDS constants | :tested |
| LZ-014 | reference-pool leave-one-out pruning | Operational | example-tested | test/test_prune_logic.py + docs/lazarus_prune_v0_1_3_companion.md (manual evidence for the IO-bound _prune_score_one) | face_sentinel.py _outliers_from_scores() + _prune_score_one() + prune_cmd() + PRUNE_OUTLIER_MULTIPLIER constant | :tested |
| LZ-015 | Touch ID opportunistic pre-face gate | Operational | example-tested | test/test_touchid_check.py + docs/lazarus_touchid_v0_1_4_companion.md (manual evidence for real bioutil invocation) | face_sentinel.py _touchid_check() + auth() Step 1 block | :tested |
| LZ-016 | outlier-detection abstract algorithm | Operational | lean-proved | src/lean4/Outliers.lean (5 theorems: subset, empty, singleton, constant, monotone) — built hermetically via `cd src/lean4 && lake build` | src/lean4/Outliers.lean (abstract algorithm) layered on face_sentinel.py _outliers_from_scores (LZ-014, Python implementation) | :proved |
| LZ-017 | liveness metric abstract properties | Operational | lean-proved | src/lean4/Liveness.lean (4 theorems: self-zero, symmetry, length-bounded, zero-iff-equal) — built hermetically via `lake build` | src/lean4/Liveness.lean (abstract Hamming-style metric) layered on face_sentinel.py _liveness_delta (LZ-013, Python implementation) | :proved |
| LZ-018 | classification dispatcher priority | Operational | lean-proved | src/lean4/Classify.lean (6 theorems: 4 priority cases + exhaustive + disjoint) — built hermetically via `lake build` | src/lean4/Classify.lean (abstract priority dispatcher) layered on network_monitor.py classify (LZ-009, Python implementation) | :proved |
| LZ-019 | strict Touch ID hard-gate | Operational | example-tested | test/test_auth_strict_touchid.py (5 branches: strict×3 outcomes + non-strict×2 outcomes + default-parameter lock via inspect.signature) | face_sentinel.py auth() Step 1 strict branch + argparse `--strict-touchid` flag + CLI dispatch | :tested |
| LZ-020 | runtime-LLM-behavior transcript audit | Operational | example-tested | test/test_runtime_harness.py + test/transcripts/shakespeare_mode_session.txt + test/transcripts/normal_mode_session.txt + docs/runtime_harness_design.md (point-in-time recorded transcripts; assertions on shape, sustained refusal, privacy redaction) | test/transcripts/ (real /lazarus session captures, network values redacted) | :tested |

## Counts

- Total: 20
- `:proved`: 3 (LZ-016 outliers + LZ-017 liveness metric +
  LZ-018 classification dispatcher, all lean-proved
  hermetically)
- `:tested`: 17 — LZ-001 through LZ-015 + LZ-019 + LZ-020
- `:verified`: 0
- `:benchmarked`: 0
- `:argued`: 0
- `:open`: 0

## Cross-audit A1–A6 self-check (post-v0.1.16)

- **A1 — Coverage.** Every LZ-ID in `LAZARUS_SPEC.md` has a row
  here. ✓ (20 of 20).
- **A2 — Logic & Status parity.** Spec → registry Logic tier and
  Status fields match exactly. Key column compresses spec keys
  for table readability (e.g. spec
  "visual-skin/security-primitive decoupling" → registry
  "visual-skin/security decoupling"); LZ-ID is the canonical
  link. ✓.
- **A3 — Evidence exists.** All 15 `:tested` entries cite
  runnable artifacts under `test/`, plus LZ-016 cites
  `src/lean4/Outliers.lean`:
  - LZ-001 → `test/test_visual_skin_decoupling.py`
  - LZ-002 → `test/test_distance_band_thresholds.py`
  - LZ-003 → `test/test_shakespeare_mode_refusal.py`
  - LZ-004 → `test/test_auth_clears_shakespeare.py`
  - LZ-005 → `test/test_no_networking_imports.sh`
  - LZ-006 → `test/test_reference_bounds.py`
  - LZ-007 → `test/test_watch_state_transitions.py`
  - LZ-008 → `test/test_peek_output.py`
  - LZ-009 → `test/test_network_monitor_classify.py`
  - LZ-010 → `test/test_honeypot_listener.py`
  - LZ-011 → `test/test_oversight_action.sh`
  - LZ-012 → `test/test_companion_readonly_discipline.py`
  - LZ-013 → `test/test_liveness_check.py` +
    `docs/lazarus_liveness_v0_1_2_companion.md`
  - LZ-014 → `test/test_prune_logic.py` +
    `docs/lazarus_prune_v0_1_3_companion.md`
  - LZ-015 → `test/test_touchid_check.py` +
    `docs/lazarus_touchid_v0_1_4_companion.md`
  - LZ-016 → `src/lean4/Outliers.lean` (5 theorems built
    hermetically via `lake build`)
  - LZ-017 → `src/lean4/Liveness.lean` (4 theorems built
    hermetically via `lake build`)
  - LZ-018 → `src/lean4/Classify.lean` (6 theorems built
    hermetically via `lake build`)
  - LZ-019 → `test/test_auth_strict_touchid.py` (5 branches +
    default-parameter lock)
  - LZ-020 → `test/test_runtime_harness.py` +
    `test/transcripts/` (real /lazarus session captures with
    network values redacted) +
    `docs/runtime_harness_design.md` (broader architecture)
  No `:argued` or `:open` entries remain.
- **A4 — Status honesty.** All 17 `:tested` entries carry
  `example-tested`; LZ-016, LZ-017, and LZ-018 carry
  `lean-proved` matching their `:proved` status. LZ-020's
  spec entry carries the explicit point-in-time caveat
  marking the transcript audit as honest evidence for
  "this DID work in a real session," not "this will work
  in every future session." No `:argued` or `:open`
  entries remain.
- **A5 — Stale counts.** Counts above (20 / 3 / 17 / 0 / 0 /
  0 / 0) match `LAZARUS_SPEC.md` final-section counts and
  `dashboard.md` summary.
- **A6 — Test sync.** All 15 `:tested` entries are exercised
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
  `python3 test/test_visual_skin_decoupling.py`,
  `python3 test/test_honeypot_listener.py`,
  `python3 test/test_shakespeare_mode_refusal.py`,
  `python3 test/test_auth_clears_shakespeare.py`,
  `python3 test/test_companion_readonly_discipline.py`.

## Dependencies on other Triad-Deployment spec entries

Lazarus is the most-mature deployment in the Triad and stands on
its own; it does not yet share artifacts with LavaLamp or PharOS.
Cross-deployment dependencies (e.g. consuming LavaLamp's
heartbeat for additional auth gating) are out of scope for v0.1
and would be tracked here as Lazarus spec entries acquire LL-NNN
or PH-NNN prerequisites.
