# artifact_registry.md — Lazarus

Version: 0.1.23 (**LZ-024 + LZ-025 both promoted to
`:proved`** via two new hermetic Lean 4 modules. (1)
`src/lean4/FaceReferencePool.lean` — `face_reference_correctness`
proves the LZ-016 outliers filter respects both abstract
subset (LZ-016 `outliers_subset`) AND the LZ-006 bounded-pool
size invariant when applied to LZ-014's pruning workflow.
(2) `src/lean4/LivenessJoint.lean` — `liveness_static_photo_fails`
+ `liveness_pass_implies_motion` + `liveness_equivalence`
chain LZ-017's metric theorems (`deltaCount_self`,
`deltaCount_zero_iff_eq`) with LZ-013's threshold semantics
to justify LZ-007's watch-loop routing decisions formally.
All five TCE Discovery.Triadic intra-deployment joint-closure
entries (LZ-022..LZ-026) are now promoted — three to `:tested`
via integration tests (LZ-022/LZ-023) and three to `:proved`
via cross-module Lean theorems (LZ-024/LZ-025/LZ-026; counts
total `:proved` 6 since LZ-016/LZ-017/LZ-018 are also
:proved as base modules). Lazarus is now the most-formal
deployment in the Triad. Counts:
28 / 6 / 21 / 0 / 0 / 1 / 0.)

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
| LZ-022 | network-exfiltration joint closure | Operational | example-tested | test/test_network_exfil_joint_closure.py (7 sections: component tests pass as conjunction + LZ-005 independent re-grep of Swift networking symbols + Python networking imports with size-guard + LZ-010 runtime TEST-EXFIL listener on port 38082 with JSONL record assertion + LZ-019 strict_touchid=True hard-exit on stubbed "nonzero" with control-leg breach detector on downstream IO + default opt-in semantics intact via inspect.signature + spec-level conjunction LZ-022 names LZ-005/LZ-010/LZ-019 + V-NETWORK-EXFIL anchor + prevent/detect/control framing + component entries retain local/honeypot/strict V-related framing) | LAZARUS_SPEC.md LZ-005 + LZ-010 + LZ-019 entries; face_compare.swift (LZ-005 source surface) + network_honeypot.py (LZ-010 detection surface) + face_sentinel.py auth() strict-touchid branch (LZ-019 control surface) | :tested |
| LZ-023 | prompt-contract joint closure | Boundary | example-tested | test/test_prompt_contract_joint_closure.py (8 sections: component-tests-as-conjunction + both contract sections coexist + section-local extraction + mode-vocab unified + no cross-section permissive bleed + no producer write-directive leak + LZ-012 cross-references LZ-001/LZ-003 + LZ-023 entry names all three components) | LAZARUS_SPEC.md LZ-001 + LZ-003 + LZ-012 entries; face_sentinel.py (producer) + lazarus.md (consumer: §Shakespeare mode + §What you do NOT do) | :tested |
| LZ-024 | face-reference lean-scaffold joint closure | Operational | lean-proved | src/lean4/FaceReferencePool.lean (3 hermetic Lean 4 theorems: filter_length_le_bound bridge lemma; outliers_preserves_bound applied to Outliers.outliers; face_reference_correctness composition theorem proving that applying the LZ-016 outliers filter to a bounded pool yields a result satisfying both LZ-016's outliers_subset AND LZ-006's bounded-pool size invariant — cannot be proved without invoking lemmas from each of the three previously-separate spec entries) — built hermetically via `lake build` (13 jobs, zero `sorry`) | src/lean4/FaceReferencePool.lean layered on src/lean4/Outliers.lean (LZ-016); face_sentinel.py prune_oldest()/MAX_REFERENCES (LZ-006) + _outliers_from_scores()/_prune_score_one() (LZ-014) | :proved |
| LZ-025 | liveness lean-scaffold joint closure | Operational | lean-proved | src/lean4/LivenessJoint.lean (3 hermetic Lean 4 theorems: liveness_static_photo_fails forward composition — byte-identical captures yield deltaCount = 0 < threshold, justifying LZ-007's mode-flip-to-shakespeare branch; liveness_pass_implies_motion converse — threshold-passing implies the captures are not byte-identical; liveness_equivalence — full LZ-017 deltaCount_zero_iff_eq characterisation of the LZ-013 anti-spoof decision under equal-length precondition) — built hermetically via `lake build` (13 jobs, zero `sorry`) | src/lean4/LivenessJoint.lean layered on src/lean4/Liveness.lean (LZ-017); face_sentinel.py check_once() is_match branch (LZ-007) + _liveness_delta()/liveness_check()/LIVENESS_DELTA_MIN (LZ-013) | :proved |
| LZ-026 | categorical triadic closure of lean-proved trio | Boundary | lean-proved | src/lean4/Composed.lean (4 hermetic Lean 4 theorems: zero_not_outlier + zero_notin_outliers + self_match_yields_zero_distance + composed_correctness — the last chains Liveness.deltaCount_self (LZ-017) + an inline outlier-zero lemma from Outliers.isOutlier (LZ-016) + Classify.classify_system_priority (LZ-018) into an end-to-end pipeline assertion; cannot be proved without invoking lemmas from each of the three previously-separate Lean-proved modules) — built hermetically via `lake build` (9 jobs, zero `sorry`) | src/lean4/Composed.lean layered on src/lean4/Outliers.lean (LZ-016) + src/lean4/Liveness.lean (LZ-017) + src/lean4/Classify.lean (LZ-018) | :proved |
| LZ-027 | break-glass recovery (--recover with Touch ID + recovery-token) | Operational | example-tested | test/test_recovery.py (7 branches: Touch ID succeeds; no method available; token supplied + no saved; token mismatch; good token; whitespace-padded token; already-normal pre-state with Touch ID — plus 2 locks: default-parameter via inspect.signature + RECOVERY_TOKEN_FILE path lock against BASE_DIR / "recovery_token.txt") | face_sentinel.py recover() + _read_recovery_token() + RECOVERY_TOKEN_FILE constant + argparse `--recover` + `--token` flags + CLI dispatch | :tested |
| LZ-028 | no-oracle-triad-backbone | Boundary | manual | LAZARUS_SPEC.md LZ-028 entry (TCE Discovery.Triadic cross-Triad pass at engine v0.2.12 commit a9ddfea surfaced [LL-002, LZ-012, PH-004] as the top-scoring triple at 26.00 across the unified 82-entry Triad corpus; first cross-deployment joint-closure entry in Lazarus; mirror entries at LavaLamp LL-046 + PharOS PH-014) — no cross-Triad integration test yet | LAZARUS_SPEC.md LZ-012 entry (this deployment's leg); LAVALAMP_SPEC.md LL-002 entry (visual-security decoupling); PHAROS_SPEC.md PH-004 entry (membrane Bool-only Lean theorem); TCE companion docs/triad_discovery_companion.md in triadic-coordination-engine repo | :argued |

## Counts

- Total: 28
- `:proved`: 6 (LZ-016 outliers + LZ-017 liveness metric +
  LZ-018 classification dispatcher + LZ-024 face-reference
  scaffold + LZ-025 liveness scaffold + LZ-026 composed-
  correctness 3-cycle — all six lean-proved hermetically
  via `lake build` in `src/lean4/`)
- `:tested`: 21 — LZ-001 through LZ-015 + LZ-019 + LZ-020 +
  LZ-021 + LZ-022 + LZ-023 + LZ-027
- `:verified`: 0
- `:benchmarked`: 0
- `:argued`: 1 — LZ-028 (first cross-deployment joint-
  closure entry in Lazarus; mirror entries at LL-046 +
  PH-014; awaits a cross-Triad integration test exercising
  the No-Oracle Backbone conjunction across all three
  deployments)
- `:open`: 0

## Cross-audit A1–A6 self-check (post-v0.1.23)

- **A1 — Coverage.** Every LZ-ID in `LAZARUS_SPEC.md` has a row
  here. ✓ (28 of 28).
- **A2 — Logic & Status parity.** Spec → registry Logic tier and
  Status fields match exactly. Key column compresses spec keys
  for table readability (e.g. spec
  "visual-skin/security-primitive decoupling" → registry
  "visual-skin/security decoupling"); LZ-ID is the canonical
  link. ✓.
- **A3 — Evidence exists.** All 21 `:tested` entries cite
  runnable artifacts under `test/` (plus six `:proved` Lean
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
  - **LZ-022 → `test/test_network_exfil_joint_closure.py`**
    (7 sections exercising the LZ-005 ∧ LZ-010 ∧ LZ-019
    V-NETWORK-EXFIL conjunction in one end-to-end harness:
    source-level grep + runtime honeypot listener +
    runtime strict-Touch-ID hard-gate)
  - **LZ-023 → `test/test_prompt_contract_joint_closure.py`**
    (8 sections exercising the LZ-001 ∧ LZ-003 ∧ LZ-012
    conjunction)
  - **LZ-024 → `src/lean4/FaceReferencePool.lean`** (3
    theorems including `face_reference_correctness` —
    LZ-016 outliers filter preserves both abstract subset
    and LZ-006 bounded-pool size invariant)
  - **LZ-025 → `src/lean4/LivenessJoint.lean`** (3
    theorems including `liveness_equivalence` — full
    LZ-017-grounded characterisation of the LZ-013
    anti-spoof primitive's decision)
  - **LZ-026 → `src/lean4/Composed.lean`** (4 theorems
    chaining lemmas from Outliers + Liveness + Classify into
    `composed_correctness`)
  - **LZ-027 → `test/test_recovery.py`** (7 branches + 2
    locks; ships in v0.1.19's bundled commit)
  The one remaining `:argued` entry (LZ-028
  no-oracle-triad-backbone, first cross-deployment joint-
  closure in Lazarus) cites the TCE Discovery.Triadic
  cross-Triad pass companion in triadic-coordination-engine
  commit `a9ddfea`; mirror entries at LavaLamp LL-046 +
  PharOS PH-014.
- **A4 — Status honesty.** All 21 `:tested` entries carry
  `example-tested`; LZ-016, LZ-017, LZ-018, LZ-024, LZ-025,
  LZ-026 carry `lean-proved` matching `:proved`; LZ-028
  carries `manual` matching `:argued` (cross-deployment
  structural argument from the TCE cross-Triad pass —
  joint integration test would span three deployments).
  LZ-020 carries the point-in-time caveat; LZ-021 defers
  Tier 2b screen-lock as opt-in future work; LZ-027
  acknowledges the Touch-ID-hardware-fail-AND-no-token gap
  rather than pretending it's solved; LZ-023's promotion
  is honestly framed as a static joint test, not a runtime
  LLM-behavior test; LZ-022's promotion is honest about
  the static + dynamic harness boundary; LZ-024 and LZ-025
  honestly frame the abstract metric content they prove —
  LZ-024 does not model the leave-one-out symlink
  construction, LZ-025 does not model camera I/O or the
  `sips` BMP downsample (both are operational layers
  outside the metric content); LZ-026's
  `composed_correctness` is honest about chaining existing
  per-module lemmas at the Lean level. The three new
  v0.1.23 Lean modules (FaceReferencePool, LivenessJoint,
  Composed-at-v0.1.21) all add **composition theorems**
  over pre-existing Lean modules — they don't introduce
  new mathematical content, only formalise the cross-
  module structure the TCE pass surfaced informally.
- **A5 — Stale counts.** Counts above (28 / 6 / 21 / 0 / 0 /
  1 / 0) match `LAZARUS_SPEC.md` final-section counts and
  `dashboard.md` summary.
- **A6 — Test sync.** All 21 `:tested` entries are exercised
  by tests under `test/` that run on `macos-latest` via
  `.github/workflows/test.yml` on every push. The six
  `:proved` Lean entries (LZ-016/LZ-017/LZ-018 base modules
  + LZ-024/LZ-025/LZ-026 composition theorems) are
  exercised by `lake build` in the same workflow. Locally
  each test runs via `python3 test/<file>` or
  `bash test/<file>`; the Lean build is
  `cd src/lean4 && lake build`.

## Dependencies on other Triad-Deployment spec entries

Lazarus is the most-mature deployment in the Triad and stands on
its own; it does not yet share artifacts with LavaLamp or PharOS.
Cross-deployment dependencies (e.g. consuming LavaLamp's
heartbeat for additional auth gating) are out of scope for v0.1
and would be tracked here as Lazarus spec entries acquire LL-NNN
or PH-NNN prerequisites.
