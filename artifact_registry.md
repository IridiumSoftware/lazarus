# artifact_registry.md — Lazarus

Version: 0.1.21 (LZ-023 — prompt-contract joint-closure
promoted to `:tested` via `test/test_prompt_contract_joint_closure.py`,
first of the five TCE Discovery.Triadic joint-closure entries
to land an integration test. Catch-up rows added for LZ-022,
LZ-024, LZ-025, LZ-026 (remaining `:argued`) and LZ-027
(break-glass recovery, `:tested` since v0.1.19). Counts:
27 / 3 / 20 / 0 / 0 / 4 / 0.)

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
| LZ-021 | OverSight Tier 2 allowlist + state-flip | Operational | example-tested | test/test_oversight_tier2.sh (6 subtests: non-allowlisted on→trigger, allowlisted on→no trigger, off-event→no trigger, # comment ignored, blank lines ignored, default-allowlist python3) | oversight_action.sh Tier 2 block (allowlist check + inline Python state-mutation + sentinel.log alert append) | :tested |
| LZ-022 | network-exfiltration joint closure | Operational | manual | LAZARUS_SPEC.md LZ-022 entry (TCE Discovery.Triadic pass at engine v0.2.11; STRICT HIGH-band triple [LZ-005, LZ-010, LZ-019] at score 10.00; V-NETWORK-EXFIL co-defense via prevent + detect + control) — no joint integration test yet | LAZARUS_SPEC.md LZ-005 + LZ-010 + LZ-019 entries; face_compare.swift (LZ-005) + network_honeypot.py (LZ-010) + face_sentinel.py auth() strict-touchid (LZ-019) | :argued |
| LZ-023 | prompt-contract joint closure | Boundary | example-tested | test/test_prompt_contract_joint_closure.py (8 sections: component-tests-as-conjunction + both contract sections coexist + section-local extraction + mode-vocab unified + no cross-section permissive bleed + no producer write-directive leak + LZ-012 cross-references LZ-001/LZ-003 + LZ-023 entry names all three components) | LAZARUS_SPEC.md LZ-001 + LZ-003 + LZ-012 entries; face_sentinel.py (producer) + lazarus.md (consumer: §Shakespeare mode + §What you do NOT do) | :tested |
| LZ-024 | face-reference lean-scaffold joint closure | Operational | manual | LAZARUS_SPEC.md LZ-024 entry (TCE pass; STRICT HIGH-band [LZ-006, LZ-014, LZ-016] at score 9.50, sd=2 tested+tested+proved; proof-scaffold-meets-implementation cluster on face-reference axis) — promotion to :tested requires reference-pool integration test asserting conformance with LZ-016 abstract properties on operational data path | LAZARUS_SPEC.md LZ-006 + LZ-014 + LZ-016 entries; face_sentinel.py prune (LZ-006/LZ-014) + src/lean4/Outliers.lean (LZ-016) | :argued |
| LZ-025 | liveness lean-scaffold joint closure | Operational | manual | LAZARUS_SPEC.md LZ-025 entry (TCE pass; STRICT HIGH-band [LZ-007, LZ-013, LZ-017] at score 9.50, sd=2; proof-scaffold-meets-implementation cluster on liveness axis, parallel to LZ-024) — promotion to :tested requires watch-loop integration test asserting conformance with LZ-017 abstract properties on operational data path | LAZARUS_SPEC.md LZ-007 + LZ-013 + LZ-017 entries; face_sentinel.py check_once / liveness_check (LZ-007/LZ-013) + src/lean4/Liveness.lean (LZ-017) | :argued |
| LZ-026 | categorical triadic closure of lean-proved trio | Boundary | manual | LAZARUS_SPEC.md LZ-026 entry (TCE pass; the only directional 3-cycle in the Lazarus mention graph: LZ-016 → LZ-018 → LZ-017 → LZ-016; first-of-its-kind across all three Triad-deployment TCE passes — LavaLamp 44 entries: 0 cycles, PharOS 10 entries: 0, Lazarus 19 entries: 1) — promotion to :proved requires `composed_correctness` theorem in src/lean4/ formalising the 3-cycle compositional structure | LAZARUS_SPEC.md LZ-016 + LZ-017 + LZ-018 entries; src/lean4/Outliers.lean + Liveness.lean + Classify.lean | :argued |
| LZ-027 | break-glass recovery (--recover with Touch ID + recovery-token) | Operational | example-tested | test/test_recovery.py (7 branches: Touch ID succeeds; no method available; token supplied + no saved; token mismatch; good token; whitespace-padded token; already-normal pre-state with Touch ID — plus 2 locks: default-parameter via inspect.signature + RECOVERY_TOKEN_FILE path lock against BASE_DIR / "recovery_token.txt") | face_sentinel.py recover() + _read_recovery_token() + RECOVERY_TOKEN_FILE constant + argparse `--recover` + `--token` flags + CLI dispatch | :tested |

## Counts

- Total: 27
- `:proved`: 3 (LZ-016 outliers + LZ-017 liveness metric +
  LZ-018 classification dispatcher, all lean-proved
  hermetically)
- `:tested`: 20 — LZ-001 through LZ-015 + LZ-019 + LZ-020 +
  LZ-021 + LZ-023 + LZ-027
- `:verified`: 0
- `:benchmarked`: 0
- `:argued`: 4 — LZ-022, LZ-024, LZ-025, LZ-026 (TCE
  Discovery.Triadic joint-closure entries awaiting joint
  integration tests; LZ-026's path is to `:proved` via a
  `composed_correctness` Lean theorem)
- `:open`: 0

## Cross-audit A1–A6 self-check (post-v0.1.21)

- **A1 — Coverage.** Every LZ-ID in `LAZARUS_SPEC.md` has a row
  here. ✓ (27 of 27). Registry was stale through v0.1.18/v0.1.19/
  v0.1.20 (missing rows for LZ-022..LZ-027); catch-up rows added
  at v0.1.21 alongside the LZ-023 promotion.
- **A2 — Logic & Status parity.** Spec → registry Logic tier and
  Status fields match exactly. Key column compresses spec keys
  for table readability (e.g. spec
  "visual-skin/security-primitive decoupling" → registry
  "visual-skin/security decoupling"); LZ-ID is the canonical
  link. ✓.
- **A3 — Evidence exists.** All 20 `:tested` entries cite
  runnable artifacts under `test/` (plus three `:proved` Lean
  entries cite `src/lean4/`):
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
  - LZ-016 → `src/lean4/Outliers.lean` (5 theorems)
  - LZ-017 → `src/lean4/Liveness.lean` (4 theorems)
  - LZ-018 → `src/lean4/Classify.lean` (6 theorems)
  - LZ-019 → `test/test_auth_strict_touchid.py`
  - LZ-020 → `test/test_runtime_harness.py` +
    `test/transcripts/` + `docs/runtime_harness_design.md`
  - LZ-021 → `test/test_oversight_tier2.sh`
  - **LZ-023 → `test/test_prompt_contract_joint_closure.py`**
    (8 sections exercising the LZ-001 ∧ LZ-003 ∧ LZ-012
    conjunction)
  - **LZ-027 → `test/test_recovery.py`** (7 branches + 2
    locks; ships in v0.1.19's bundled commit)
  The four `:argued` entries (LZ-022, LZ-024, LZ-025, LZ-026)
  cite the TCE Discovery.Triadic pass companion in
  triadic-coordination-engine commit 3fcccf3.
- **A4 — Status honesty.** All 20 `:tested` entries carry
  `example-tested`; LZ-016, LZ-017, LZ-018 carry `lean-proved`
  matching `:proved`; LZ-022/024/025/026 carry `manual`
  matching `:argued` (joint-closure structural arguments from
  the TCE pass — explicit promotion paths documented per
  entry). LZ-020 carries the point-in-time caveat; LZ-021
  defers Tier 2b screen-lock as opt-in future work; LZ-027
  acknowledges the Touch-ID-hardware-fail-AND-no-token gap
  rather than pretending it's solved; LZ-023's promotion is
  honestly framed as a static joint test, not a runtime
  LLM-behavior test.
- **A5 — Stale counts.** Counts above (27 / 3 / 20 / 0 / 0 /
  4 / 0) match `LAZARUS_SPEC.md` final-section counts and
  `dashboard.md` summary.
- **A6 — Test sync.** All 20 `:tested` entries are exercised
  by tests under `test/` that run on `macos-latest` via
  `.github/workflows/test.yml` on every push. The three
  `:proved` Lean entries are exercised by `lake build` in the
  same workflow. Locally each test runs via `python3 test/<file>`
  or `bash test/<file>`; the Lean build is `cd src/lean4 && lake build`.

## Dependencies on other Triad-Deployment spec entries

Lazarus is the most-mature deployment in the Triad and stands on
its own; it does not yet share artifacts with LavaLamp or PharOS.
Cross-deployment dependencies (e.g. consuming LavaLamp's
heartbeat for additional auth gating) are out of scope for v0.1
and would be tracked here as Lazarus spec entries acquire LL-NNN
or PH-NNN prerequisites.
