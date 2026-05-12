# Dashboard — Lazarus

Last updated: 2026-05-12 (post-v0.1.28 — **LZ-031 decoupling-triad-backbone lands as fourth cross-Triad joint-closure entry.** TCE Discovery.Triadic cross-Triad pass at engine v0.2.12 (commit `a9ddfea`) surfaced `[LL-002, LZ-001, PH-004]` at score 23.00 — the **Decoupling axis** of the Triad. Three V-DECOUPLING flavors: LavaLamp visual/security separation (LL-002, `:tested`) + Lazarus visual-skin/security-state producer-consumer split (LZ-001, `:tested`) + PharOS membrane Bool-only output (PH-004, `:proved`). LZ-031 records Lazarus's leg with citations to LL-002 + PH-004. Mirror entries at LavaLamp LL-050 + PharOS PH-018. Status `:argued`, Boundary tier. **Structurally distinct from LZ-028 No-Oracle Backbone** despite sharing LL-002 + PH-004 legs — the distinguishing leg is LZ-001 visual-skin decoupling (this entry) vs LZ-012 companion-read-only (LZ-028); LL-002 + PH-004 serve dual invariants. **Two promotion paths**: (1) operational integration test exercising visual-refactor/skin-swap/membrane-Bool-only invariance, or (2) Lean composition via parallel `DecouplingBackbone.lean` reusing the v0.1.26 Lake git deps plus a new local `VisualSkinDecoupling.lean` — **no new Mathlib dep required**, lower cost than LZ-029's path. Counts: 30/7/21/0/0/2/0 → **31/7/21/0/0/3/0**. Predecessor v0.1.27 — **LZ-030 defense-in-depth-triad-backbone lands as third cross-Triad joint-closure entry.** TCE Discovery.Triadic cross-Triad pass at engine v0.2.12 (commit `a9ddfea`) surfaced `[LL-030, PH-005, LZ-022]` at score 20.00 — three V-DEFENSE-IN-DEPTH layers at three deployments: substrate (LavaLamp LL-030 sensor-defense joint-closure, `:tested`) + OS-membrane (PharOS PH-005 PAM composition atop LavaLamp triads, `:argued`) + runtime (Lazarus LZ-022 prevent+detect+control exfil triangle, `:tested`). LZ-030 records Lazarus's leg with citations to LL-030 + PH-005. Mirror entries at LavaLamp LL-049 + PharOS PH-017. Status `:argued`, Operational tier. **Promotion path is operational rather than Lean-algorithmic** — unlike LZ-028/LZ-029 which run through cross-repo Lake-dep Lean composition, LZ-030 needs a cross-Triad runtime integration test exercising all three V-DEFENSE-IN-DEPTH layers jointly (natural home: a new `triad-integration/` test bundle in the TCE engine repo). **PH-005 promotion as side effect** — the same cross-Triad integration test that promotes LZ-030 / LL-049 / PH-017 also promotes the bottleneck PH-005 leg from `:argued` to `:tested`. **Honest framing**: score 20.00 is the highest-scoring cross-Triad triple where all three legs are real operational defense entries (LL-030 substrate + PH-005 OS-membrane + LZ-022 runtime), in contrast to LZ-028 + LZ-029 which involve formal/abstract claims. Counts: 29/7/21/0/0/1/0 → **30/7/21/0/0/2/0**. Predecessor v0.1.26 — **LZ-028 cross-Triad composition upgraded to use concrete imports for ALL THREE legs.** Adds `src/lean4/CompanionDiscipline.lean` (concrete LZ-012 formalisation: 3-constructor `LlmOutput {observe, flag, watch}` + theorems) and a new Lake git dep on `lavalamp-hermetic` (LavaLamp commit `1a2534f`) which ships `LL002Visual.lean` (concrete LL-002 formalisation: 2-constructor `VisualOutput {locked, unlocked}` + theorems). `TriadBackbone.lean` swaps the previously-local abstract `VisualOutput` / `LlmOutput` definitions for these concrete cross-repo imports — the `no_oracle_triad_backbone` composition theorem is unchanged in shape but each leg is now backed by its home-repo canonical Lean formalisation. LZ-012 + LL-002 stay `:tested` (Lean modules are layered companions, not replacements). `lake build` returns **21 jobs** (was 17) with zero `sorry`. The Triad now has three hermetic Lean packages — `pharos-lean`, `lavalamp-hermetic`, `lazarus-lean` — composing across two cross-repo Lake git deps. Counts unchanged at **29/7/21/0/0/1/0**. Predecessor v0.1.25 — LZ-029 lean-stack-triad-backbone lands as second cross-Triad joint-closure entry. TCE Discovery.Triadic cross-Triad pass at engine v0.2.12 (commit `a9ddfea`) surfaced `[LL-006, PH-004, LZ-026]` at score 20.50 — the **formal-verification backbone** of the Triad and the only cross-Triad triple where every leg is already `:proved` via a Lean theorem. LZ-029 records Lazarus's leg (LZ-026 composed-correctness 3-cycle) with citations to LavaLamp LL-006 (detection-probability bound) + PharOS PH-004 (membrane Bool-only). Mirror entries at LavaLamp LL-047 + PharOS PH-015. Status `:argued`, Boundary tier. Promotion to `:proved` requires extending the v0.1.24 cross-repo Lake-dep umbrella with a second git dep on LavaLamp at a pinned commit; outstanding obstacle is the Mathlib transitive dep from LavaLamp's track (~2500-job compile vs current ~30s). All three legs are concretely Lean-proved, so no abstraction is needed (in contrast to LZ-028 where LL-002 + LZ-012 are modelled as abstract finite-output types). Counts: 28/7/21/0/0/0/0 → **29/7/21/0/0/1/0**. Predecessor v0.1.24 — **LZ-028 no-oracle-triad-backbone → `:proved` via the FIRST cross-repo Lean proof in the Triad.** New `src/lean4/TriadBackbone.lean` imports `PharOS.Membrane` through a Lake git dependency pinning PharOS commit `e3eaee1` (v0.0.12) — the build fetches PharOS's hermetic Lean tree, brings `MembraneOutput` + `membrane_one_bit_channel` into scope, and composes with locally-defined abstract `VisualOutput` (LL-002 leg, 2-state) + `LlmOutput` (LZ-012 leg, 3-state) into the composition theorem `no_oracle_triad_backbone`. The joint Triad output is a 12-element finite type (2 × 3 × 2) — cardinality bound is the formal counterpart of "no real-valued distance can be encoded in the joint output." `lake build` returns 17 jobs with zero `sorry`. **`:argued` reaches zero.** All joint-closure entries (TCE intra-deployment LZ-022..LZ-026 + cross-Triad LZ-028) are now promoted. Counts shift: 28/6/21/0/0/1/0 → **28/7/21/0/0/0/0**.).

## Status summary

- Spec: 31 LZ-NNN entries in `LAZARUS_SPEC.md`.
- Counts: **31 / 7 / 21 / 0 / 0 / 3 / 0** (total / proved /
  tested / verified / benchmarked / argued / open).
  Seven `:proved` entries — LZ-016/LZ-017/LZ-018 base
  modules, LZ-024/LZ-025/LZ-026 intra-deployment
  composition theorems (FaceReferencePool / LivenessJoint /
  Composed), and **LZ-028 no-oracle-triad-backbone via
  `TriadBackbone.lean` — the FIRST cross-repo Lean proof
  in any Triad deployment**. Three `:argued` entries —
  **LZ-029 lean-stack-triad-backbone** at v0.1.25 (the only
  triple where every leg is Lean-proved: LL-006 + PH-004 +
  LZ-026; promotion requires extending the v0.1.24 cross-
  repo umbrella with a second Lake git dep on LavaLamp);
  **LZ-030 defense-in-depth-triad-backbone** at v0.1.27
  (substrate + OS-membrane + runtime V-DEFENSE-IN-DEPTH
  via `[LL-030, PH-005, LZ-022]` at score 20.00; promotion
  is operational and side-effect-promotes PH-005); and
  **LZ-031 decoupling-triad-backbone** at v0.1.28 (Decoupling
  axis via `[LL-002, LZ-001, PH-004]` at score 23.00 —
  structurally distinct from LZ-028 despite sharing LL-002 +
  PH-004 legs because Lazarus's leg shifts from LZ-012 to
  LZ-001; two promotion paths — operational integration
  test OR Lean composition with no new Mathlib dep). Mirror
  entries at LavaLamp LL-047/LL-049/LL-050 + PharOS
  PH-015/PH-017/PH-018. `:open` at zero. LZ-027 break-glass
  recovery at `:tested`. All TCE-surfaced intra-deployment
  joint-closures (LZ-022..LZ-026) are promoted; all four
  top-scoring cross-Triad joint-closures from the TCE
  v0.2.12 pass are now in the spec (LZ-028 `:proved`,
  LZ-029/LZ-030/LZ-031 `:argued`).
- Tests: full suite passes locally and on `macos-latest`
  via CI on every push.
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
  - `test/test_oversight_tier2.sh` (LZ-021)
  - `test/test_network_exfil_joint_closure.py` (LZ-022)
  - `test/test_prompt_contract_joint_closure.py` (LZ-023)
  - `src/lean4/FaceReferencePool.lean` (LZ-024, lean-proved, 3 theorems)
  - `src/lean4/LivenessJoint.lean` (LZ-025, lean-proved, 3 theorems)
  - `src/lean4/Composed.lean` (LZ-026, lean-proved, 4 theorems)
  - `test/test_recovery.py` (LZ-027)
  - `src/lean4/CompanionDiscipline.lean` (LZ-012 layered Lean companion, 3 theorems on `LlmOutput {observe, flag, watch}`)
  - `src/lean4/TriadBackbone.lean` (LZ-028, lean-proved, cross-repo via Lake git deps on pharos-lean@e3eaee1 + lavalamp-hermetic@1a2534f)
- CI: `.github/workflows/test.yml` runs the full test suite
  on `macos-latest` on every push. Outstanding:
  `actions/checkout@v4` Node.js 20 deprecation (deadline
  Sept 2026; bump when v5 ships).
- Public release shape: face sentinel + network monitor +
  honeypot + OverSight Tier 1 logger + `/lazarus` companion.

## Priority stack (highest leverage first)

Reordered 2026-05-11 after Brian Crabtree's external Triad
review surfaced break-glass / lockout-risk as the
highest-impact gap in the current shipping surface.

1. **Lean expansion** on the existing `:tested` entries.
   The cross-module composition pattern is now well-
   established (LZ-024/LZ-025/LZ-026 intra-deployment +
   LZ-028 cross-repo). Natural next candidates:
   LZ-006 prune-bounded list invariant, LZ-007 watch-loop
   state-machine, LZ-013 byte-diff inequalities — each
   ~30-50 lines of Lean. Cross-repo dep on `pharos-lean`
   is now part of Lazarus's build, so a future LL-002 /
   LZ-012 Lean formalisation could be similarly imported
   to upgrade `TriadBackbone.lean`'s LavaLamp/Lazarus
   legs from abstract models to concrete imports.

2. **Mirror promotions for LL-046 + PH-014.** LZ-028's
   promotion to `:proved` via cross-repo Lean opens the
   same path for the two mirror entries — both are
   currently `:argued`. LavaLamp LL-046 and PharOS PH-014
   could each `import` Lazarus's `TriadBackbone.lean`
   (via Lake git dep on this Lazarus repo) and use the
   same composition theorem from their own perspective.
   This would close the cross-Triad No-Oracle Backbone
   to `:proved` in all three deployment specs.

3. **`LAZARUS_RECOVERY_SPEC.md` + Lazarus.jl absorption
   decision.** Brian's review framed a forward Julia
   resurrection layer (Shamir + Hardware Envelope + TPM)
   as the long-horizon evolution of lazarus. Architectural
   choice still pending: (A) absorb into current repo as
   LZ-NNN, (B) spin out as a fourth Triad-deployment repo,
   (C) extend LavaLamp. Spec-doc work blocked until the
   architectural call is made.

4. **TPM/SEP binding (deferred — PharOS dependency).**
   The substrate-binding portion of the proposed Lazarus.jl
   needs hardware-root-of-trust patterns to land in PharOS
   first (v0.0.7 roadmap). Hold until that pattern
   stabilizes.

### Lower-priority items (carried from earlier reviews)

- **Runtime LLM-behavior harness — Approach B**: partially
  addressed in v0.1.16 (LZ-020 transcript audit, point-in-
  time). Anthropic-API integration held until model-drift
  becomes a concrete failure mode.
- **LZ-002 calibration fixture set**: face-data
  identifiability problem; held until a clean fixture
  source emerges.
- **OverSight Tier 2b** (screen lock via `pmset`): opt-in
  via sentinel-file design; ships when an actual use case
  surfaces.
- **`auth()` cleanup**: pop `lockout_reason` +
  `liveness_delta` on success (currently
  `test_auth_clears_shakespeare.py` locks the documented
  linger behavior).

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

- 2026-05-12 — v0.1.26: **LZ-028 cross-Triad composition
  upgraded to concrete imports for all three legs.** Closes
  the v0.1.24 follow-up promise ("if LavaLamp later lands a
  Lean formalisation of LL-002 and Lazarus lands one for
  LZ-012, the abstract types can be swapped for concrete
  imports without invalidating the composition theorem")
  in one session. New `src/lean4/CompanionDiscipline.lean`
  (Lazarus repo) — 3 theorems on a 3-constructor
  `LlmOutput {observe, flag, watch}` formalising LZ-012's
  type-level cardinality. New Lake git dep on
  `lavalamp-hermetic` (LavaLamp commit `1a2534f`) which
  introduces a hermetic sibling Lean package to LavaLamp's
  Mathlib-using `src/lean4/` track — ships
  `LL002Visual.lean` with 3 theorems on a 2-constructor
  `VisualOutput {locked, unlocked}` formalising LL-002's
  type-level cardinality. `TriadBackbone.lean` swaps the
  previously-local abstract definitions for these concrete
  cross-repo imports; the `no_oracle_triad_backbone`
  composition theorem is unchanged in shape (cardinality
  2 × 3 × 2 = 12) but each leg is now backed by its
  home-repo canonical formalisation. `lake build` returns
  **21 jobs** (was 17 pre-v0.1.26; +4 cover the new
  CompanionDiscipline + LL002Visual builds across two
  repos) with zero `sorry`. LZ-012 + LL-002 stay `:tested`;
  the Lean modules are layered companions. Counts
  unchanged at 29 / 7 / 21 / 0 / 0 / 1 / 0.
- 2026-05-12 — v0.1.24: **LZ-028 no-oracle-triad-backbone
  → `:proved` via the FIRST cross-repo Lean proof in any
  Triad deployment.** New `src/lean4/TriadBackbone.lean`
  imports `PharOS.Membrane` through a Lake git dependency
  pinning PharOS commit `e3eaee1` (v0.0.12). Three
  theorems + 1 enumeration def + 1 cardinality witness:
  `visual_one_bit_channel` (LL-002 leg modelled as
  2-state `VisualOutput`), `llm_finite_channel` (LZ-012
  leg modelled as 3-state `LlmOutput`),
  `pharos_one_bit_channel` (PharOS leg lifted from the
  cross-repo-imported `membrane_one_bit_channel`),
  `triadOutputs` (12-element canonical enumeration),
  `no_oracle_triad_backbone` (composition: every joint
  Triad output is in `triadOutputs`, proved by structural
  case analysis on all 12 inhabitants),
  `triad_output_cardinality` (= 12 by `rfl`). The
  cardinality bound is the formal counterpart of "no
  real-valued distance can be encoded in the joint
  output." `lake build` fetches pharos-lean, builds 17
  jobs with zero `sorry`. **`:argued` count reaches
  zero** — every Lazarus spec entry now carries runnable
  evidence at its highest available tier. Counts:
  28 / 6 / 21 / 0 / 0 / 1 / 0 → **28 / 7 / 21 / 0 / 0 /
  0 / 0**.
- 2026-05-12 — v0.1.23: **LZ-024 + LZ-025 both promoted to
  `:proved` via two new hermetic Lean 4 modules; LZ-028
  no-oracle-triad-backbone added at `:argued`.**
  (1) `src/lean4/FaceReferencePool.lean` — three theorems
  (`filter_length_le_bound`, `outliers_preserves_bound`,
  `face_reference_correctness`) prove the LZ-016 outliers
  filter respects both abstract subset (LZ-016
  `outliers_subset`) AND the LZ-006 bounded-pool size
  invariant when applied to LZ-014's pruning workflow.
  (2) `src/lean4/LivenessJoint.lean` — three theorems
  (`liveness_static_photo_fails`,
  `liveness_pass_implies_motion`, `liveness_equivalence`)
  chain LZ-017's metric properties (`deltaCount_self`,
  `deltaCount_zero_iff_eq`) with LZ-013's threshold
  semantics to justify LZ-007's watch-loop routing
  decisions formally. `lake build` returns 13 jobs with
  zero `sorry`. **All five TCE Discovery.Triadic intra-
  deployment joint-closure entries (LZ-022..LZ-026) are
  now promoted** — three `:tested` (LZ-022/LZ-023) +
  three `:proved` (LZ-024/LZ-025/LZ-026). Per-deployment
  TCE arc closes. (3) LZ-028 no-oracle-triad-backbone
  enters at `:argued` — first cross-deployment joint-
  closure entry; mirror entries at LavaLamp LL-046 +
  PharOS PH-014. Counts:
  27 / 4 / 21 / 0 / 0 / 2 / 0 → **28 / 6 / 21 / 0 / 0 /
  1 / 0**.
- 2026-05-11 — v0.1.22: **LZ-022 network-exfiltration-
  joint-closure → `:tested`** via
  `test/test_network_exfil_joint_closure.py`. Second
  TCE-surfaced joint-closure entry to land an integration
  test (after LZ-023 at v0.1.21). The 7-section harness
  exercises the V-NETWORK-EXFIL defense triangle in one
  process: (1) LZ-005/LZ-010/LZ-019 component tests pass
  in sequence; (2) independent re-grep of
  `face_compare.swift` for Swift networking symbols +
  `face_sentinel.py` for Python networking imports with a
  size-guard against silent stub-replacement;
  (3) TEST-EXFIL honeypot listener on port 38082 receives
  a simulated POST /upload exfil payload, JSONL log
  record asserted; (4) `auth(strict_touchid=True)` driven
  with stubbed `_touchid_check → "nonzero"`, hard-exit
  with code 1 verified, downstream IO stubbed as
  control-leg breach detectors; (5) default opt-in
  semantics intact via `inspect.signature`; (6) spec-level
  LZ-022 names all three components + V-NETWORK-EXFIL
  anchor + prevent/detect/control framing; (7) component
  entries retain their V-related framing. Counts:
  27 / 4 / 20 / 0 / 0 / 3 / 0 → **27 / 4 / 21 / 0 / 0 /
  2 / 0**.
- 2026-05-11 — v0.1.21: **first two TCE joint-closure
  promotions — LZ-023 → `:tested` + LZ-026 → `:proved`.**
  (1) `test/test_prompt_contract_joint_closure.py` (8
  sections exercising the LZ-001 ∧ LZ-003 ∧ LZ-012
  conjunction — first joint-closure entry to land an
  integration test). (2) `src/lean4/Composed.lean` (4
  hermetic Lean 4 theorems chaining
  `Lazarus.Liveness.deltaCount_self` (LZ-017) + an inline
  outlier-zero lemma from `Lazarus.Outliers.isOutlier`
  (LZ-016) + `Lazarus.Classify.classify_system_priority`
  (LZ-018) into `composed_correctness` — the FIRST
  `:proved`-status entry derived from a TCE finding
  across the entire Triad). Also: registry catch-up rows
  for LZ-022/024/025/026/027 + A1–A6 refresh. Counts:
  27 / 3 / 19 / 0 / 0 / 5 / 0 → **27 / 4 / 20 / 0 / 0 /
  3 / 0**.
- 2026-05-11 — v0.1.20: **TCE joint-closures (LZ-022..LZ-026)
  + break-glass recovery (LZ-027).** Two arcs merged into one
  spec commit. (1) The third per-deployment TCE
  Discovery.Triadic pass surfaced 4 HIGH-band conjunctive
  triples + 1 directional 3-cycle from the 19-entry Lazarus
  corpus — all five enter the spec at `:argued` per
  conjunctive-claim discipline. The 3-cycle [LZ-016, LZ-017,
  LZ-018] is the first directional cycle across all three
  Triad-deployment TCE passes. (2) LZ-027 spec entry for
  `--recover` (Touch ID + optional recovery-token) closes the
  fail-closed availability risk surfaced in Brian Crabtree's
  external Triad review. Implementation + test ship in
  v0.1.21. Counts:
  21 / 3 / 18 / 0 / 0 / 0 / 0 → **27 / 3 / 19 / 0 / 0 / 5 /
  0**. TCE driver + companion at triadic-coordination-engine
  commit 3fcccf3.
- 2026-05-11 — v0.1.17: **LZ-021 OverSight Tier 2**
  (allowlist + state-flip). `oversight_action.sh` gains a
  built-in + user-file allowlist; on non-allowlisted
  on-events writes `state.json` with `mode=shakespeare` +
  `lockout_reason="oversight_unallowed"` and appends an
  `oversight_tier2_alert` event to `sentinel.log`.
  Off-events stay Tier 1-only. Tier 2b (screen lock)
  explicitly deferred. New test covers 6 subtests including
  comment/blank-line edge cases. Counts:
  20 / 3 / 17 / 0 / 0 / 0 / 0 → **21 / 3 / 18 / 0 / 0 / 0 /
  0**.
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
