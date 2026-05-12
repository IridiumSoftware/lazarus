# Changelog — Lazarus

## v0.1.22 — 2026-05-11 — LZ-022 network-exfiltration joint closure → `:tested`

Third TCE Discovery.Triadic joint-closure promotion in three
versions (v0.1.21 landed LZ-023 → `:tested` and LZ-026 → `:proved`
in a single commit; v0.1.22 lands LZ-022 → `:tested` here).
Now four of the five TCE-surfaced joint-closure entries are
promoted; two `:argued` Lean-scaffold clusters remain (LZ-024,
LZ-025).

### LZ-022 network-exfiltration-joint-closure → `:tested`

New `test/test_network_exfil_joint_closure.py` — 7-section
end-to-end harness exercising the LZ-005 ∧ LZ-010 ∧ LZ-019
V-NETWORK-EXFIL defense triangle (PREVENTION + DETECTION +
CONTROL) in one Python process:

1. **Component tests as conjunction** — runs
   `test_no_networking_imports.sh` (LZ-005),
   `test_honeypot_listener.py` (LZ-010), and
   `test_auth_strict_touchid.py` (LZ-019) via subprocess;
   asserts all three pass before proceeding.
2. **LZ-005 source-level prevention re-verified** —
   independent re-grep of `face_compare.swift` for Swift
   networking symbols (URLSession, NWConnection,
   CFNetwork, etc.) and `face_sentinel.py` for Python
   networking imports (import socket, urlopen, etc.),
   with a size-guard against silent stub-replacement.
   This duplicates LZ-005's grep-lint deliberately —
   if the .sh test's size guard breaks, the joint test
   still catches a regression.
3. **LZ-010 runtime detection** — starts a TEST-EXFIL
   honeypot listener on port 38082 in a daemon thread,
   opens a client socket and sends a simulated
   `POST /upload HTTP/1.0` exfil payload, polls for the
   JSONL log record, asserts service/port/remote fields.
4. **LZ-019 runtime control** — drives
   `auth(strict_touchid=True)` with `_touchid_check`
   stubbed to return `"nonzero"`; asserts SystemExit(1)
   before face-match. Downstream IO (`capture_full`,
   `run_face_compare`, `shrink`) is stubbed to call
   `fail()` — if auth ever reaches them despite
   strict+nonzero, the test reports a control-leg
   breach.
5. **Default opt-in semantics intact** — locks
   `auth(strict_touchid=False)` default via
   `inspect.signature`. A refactor flipping the default
   to True would break LZ-015's fail-open semantics
   (hardware-less Macs).
6. **Spec-level conjunction** — LZ-022 entry names
   LZ-005, LZ-010, LZ-019; carries the V-NETWORK-EXFIL
   anchor; retains the prevent/detect/control framing.
7. **Component entries retain V-related framing** —
   LZ-005 retains "local" framing; LZ-010 retains
   "honeypot" framing; LZ-019 retains "strict" framing.

### Honest framing

Static + dynamic joint test in one harness. Catches
refactors that split the V-NETWORK-EXFIL defense along
weak seams (silently allowing a networking import,
removing the honeypot SERVICES table, flipping
strict_touchid default). Does NOT prove a real
exfiltration attempt would be defeated — a determined
adversary could obfuscate networking calls (LZ-005
bypass), bind a non-honeypot port (LZ-010 bypass), or
disable Touch ID hardware (LZ-019 bypass). Each
component's own honest-framing notes carry into the
conjunction.

### Files changed

- `test/test_network_exfil_joint_closure.py` (new) —
  7-section LZ-022 joint test, ~330 lines.
- `LAZARUS_SPEC.md` — LZ-022 status `:argued` → `:tested`;
  evidence type `manual` → `example-tested`; Test/Proof +
  Source fields populated; Counts header → (post-v0.1.22);
  Counts block refreshed.
- `artifact_registry.md` — LZ-022 row flipped to
  `:tested` + cites the new test; Counts refreshed
  (27 / 4 / 21 / 0 / 0 / 2 / 0); A1-A6 self-check
  updated.
- `dashboard.md` — last-updated stamp; counts refreshed;
  tests list extended with the new test; priority stack
  drops LZ-022 from the remaining-promotions item; new
  v0.1.22 recently-completed bullet.
- `.github/workflows/test.yml` — new
  `LZ-022 — test_network_exfil_joint_closure.py` step.
- `changelog.md` — this entry.

### Counts

- After v0.1.21: 27 / 4 / 20 / 0 / 0 / 3 / 0
- After v0.1.22: **27 / 4 / 21 / 0 / 0 / 2 / 0**
  (:tested +1 LZ-022, :argued −1)

### What's left in the TCE-surfaced `:argued` band

- **LZ-024 face-reference-lean-scaffold-joint-closure** —
  needs reference-pool integration test asserting LZ-016
  outlier properties on the operational pruning path.
  Potential `:proved` promotion path parallel to LZ-026
  if a `face_reference_correctness` theorem fits cleanly
  on top of the existing `Outliers.lean` content.
- **LZ-025 liveness-lean-scaffold-joint-closure** —
  needs watch-loop integration test asserting LZ-017
  metric properties on the operational data path.
  Same potential `:proved` promotion shape (parallel to
  LZ-026 on the liveness axis).

---

## v0.1.21 — 2026-05-11 — first two TCE joint-closure promotions: LZ-023 (:tested) + LZ-026 (:proved)

Two of the five TCE Discovery.Triadic joint-closure entries
shipped at v0.1.20 (`:argued`) get promoted in this release. Both
land via the per-entry promotion paths documented in the `Notes:`
fields of the original LZ-022..LZ-026 spec entries.

### LZ-023 prompt-contract-joint-closure → `:tested`

New `test/test_prompt_contract_joint_closure.py` — 8 sections
exercising the LZ-001 ∧ LZ-003 ∧ LZ-012 conjunction:
- Component tests for LZ-001 + LZ-003 + LZ-012 all coexist
  as fixtures.
- Both prompt-contract sections (Shakespeare-mode refusal +
  companion-read-only six-prohibitions) exist in lazarus.md.
- Mode vocabulary is unified across the three sources.
- No cross-section permissive-language bleed.
- No producer-side write-directive leak into the consumer surface.
- Spec cross-references between LZ-001/LZ-003/LZ-012 are
  bidirectional in the spec body.

First of the five TCE-surfaced joint-closure entries to land
a joint integration test. Per the conjunctive-claim discipline,
this is what promotes the joint claim — sub-claim evidence
(each of LZ-001/LZ-003/LZ-012 being individually `:tested`)
does NOT promote the joint claim alone.

### LZ-026 categorical-triadic-closure-of-lean-proved-trio → `:proved`

New `src/lean4/Composed.lean` formalises the cross-module
composition at the Lean level — the directional 3-cycle
(LZ-016 → LZ-018 → LZ-017 → LZ-016 in the spec mention
graph) is now a compiling proof artifact rather than
informal spec-body structure.

Four hermetic Lean 4 theorems:
- `zero_not_outlier` — bridge lemma: `Lazarus.Outliers.
  isOutlier 0 m s = false` for any m, s (the LHS reduces
  to `0 > m * s.sum` which is false).
- `zero_notin_outliers` — corollary: 0 is never an
  element of `Lazarus.Outliers.outliers m s`. Via
  `List.mem_filter` + `zero_not_outlier`.
- `self_match_yields_zero_distance` — `Lazarus.Liveness.
  deltaCount_self` (LZ-017) lifted to `0 ∈ references.map
  (deltaCount candidate)` when candidate ∈ references.
- `composed_correctness` — the full composition. When the
  candidate is byte-identical to at least one reference
  AND `isSystem` fires on the classification key, the
  pipeline (which uses all three modules — Liveness for
  distance, Outliers for the outlier-filter escape hatch,
  Classify for the final dispatch) returns `Class.system`.
  Proof chains `self_match_yields_zero_distance` (Liveness),
  `zero_notin_outliers` (Outliers), and `Lazarus.Classify.
  classify_system_priority` (Classify) into one statement
  that cannot be proved without invoking lemmas from each
  of the three previously-separate Lean-proved modules.

This is the **first `:proved`-status spec entry derived from
a TCE Discovery.Triadic finding across the entire Triad**.
LavaLamp's TCE-surfaced LL-030..LL-038 are all `:tested`;
PharOS's pass produced no promotions; Lazarus's remaining
LZ-022/024/025 are still `:argued`. The 3-cycle finding —
the only directional cycle across all three per-deployment
TCE passes — is now formally anchored.

`lake build` returns 9 jobs with zero `sorry` warnings.

### Registry catch-up

Aaron's parallel session also folded in artifact_registry.md
rows for LZ-022/024/025/026/027 (missing through the
v0.1.18-v0.1.20 drift) + refreshed the A1–A6 self-check.

### Files changed

- `src/lean4/Composed.lean` (new) — 4 theorems, ~180 lines.
- `src/lean4/lakefile.lean` — adds `Composed` as a fourth
  `@[default_target]` lean_lib.
- `test/test_prompt_contract_joint_closure.py` (new) —
  8-section LZ-023 joint-conjunction test.
- `LAZARUS_SPEC.md` — LZ-023 status :argued → :tested with
  source field pointing at the new test; LZ-026 status
  :argued → :proved with evidence type lean-proved + source
  field pointing at Composed.lean; Counts table refreshed.
- `dashboard.md` — last-updated stamp + counts.
- `artifact_registry.md` — 5 new rows + A1–A6 refresh.
- `changelog.md` — this entry.

### Counts

- After v0.1.20: 27 / 3 / 19 / 0 / 0 / 5 / 0
- After v0.1.21: **27 / 4 / 20 / 0 / 0 / 3 / 0**
  (:proved +1 LZ-026, :tested +1 LZ-023, :argued −2)

### What's left in the TCE-surfaced :argued band

- **LZ-022 network-exfiltration-joint-closure** — needs a
  scripted scenario exercising LZ-005 ∧ LZ-010 ∧ LZ-019
  conjunction.
- **LZ-024 face-reference-lean-scaffold-joint-closure** —
  needs reference-pool integration test asserting LZ-016
  outlier properties on the operational pruning path.
- **LZ-025 liveness-lean-scaffold-joint-closure** — needs
  watch-loop integration test asserting LZ-017 metric
  properties on the operational data path.

---

## v0.1.20 — 2026-05-11 — TCE joint-closures (LZ-022..LZ-026) + break-glass recovery (LZ-027)

The third per-deployment Discovery.Triadic engine pass in the
Triad Deployments series (after LavaLamp's LL-030..LL-038 surfacing
at engine v0.2.4 / v0.2.9 and PharOS's 10-entry pass at engine
v0.2.10). Engine pass details + companion in the
triadic-coordination-engine repo:
- driver: `src/haskell/test/LazarusDiscovery.hs`
- companion: `docs/lazarus_discovery_companion.md`
- engine version: v0.2.11, commit 3fcccf3
- corpus: 19 entries (LZ-001..LZ-019; the pass predates Aaron's
  parallel LZ-020 / LZ-021 additions but the structural findings
  stand independently)

Five new spec entries surfaced from the pass, all added at
`:argued` per the conjunctive-claim discipline (sub-claim evidence
— each component's individual `:tested`/`:proved` status — does
NOT promote the joint claim; promotion to `:tested` requires a
joint integration test exercising the conjunction):

- **LZ-022 network-exfiltration-joint-closure** — TCE STRICT
  HIGH-band triple [LZ-005, LZ-010, LZ-019] at score 10.00.
  Three-angle V-NETWORK-EXFIL defense: prevent (LZ-005
  apple-vision-local-only) + detect (LZ-010 honeypot) + control
  (LZ-019 strict-touchid).
- **LZ-023 prompt-contract-joint-closure** — TCE STRICT HIGH-band
  triple [LZ-001, LZ-003, LZ-012] at score 10.00. The prompt-
  contract enforcement triple: visual decoupling + Shakespeare-
  mode refusal + companion-read-only discipline (LZ-012 mentions
  both LZ-001 and LZ-003 in its body, anchoring the triple as a
  spec-level structural unit).
- **LZ-024 face-reference-lean-scaffold-joint-closure** — TCE
  STRICT HIGH-band triple [LZ-006, LZ-014, LZ-016] at score 9.50,
  status-diversity 2 (tested + tested + proved). Proof-scaffold-
  meets-implementation cluster on the face-reference axis.
- **LZ-025 liveness-lean-scaffold-joint-closure** — TCE STRICT
  HIGH-band triple [LZ-007, LZ-013, LZ-017] at score 9.50,
  status-diversity 2. Parallel shape to LZ-024 on the liveness
  axis.
- **LZ-026 categorical-triadic-closure-of-lean-proved-trio** —
  THE ONLY directional 3-cycle in the Lazarus mention graph:
  LZ-016 mentions LZ-018 → LZ-018 mentions LZ-017 → LZ-017
  mentions LZ-016 closes the cycle. First-of-its-kind across all
  three Triad-deployment TCE passes (LavaLamp 44-entry corpus:
  0 cycles; PharOS 10-entry: 0; Lazarus 19-entry: exactly 1,
  here). The Lean-proved compositional scaffold — three abstract
  modules that mutually constrain each other as proof obligations.
  Cleanest `:proved`-promotion target among the five since the
  Lean modules already exist; needs a new `composed_correctness`
  theorem in `src/lean4/` formalising the 3-cycle dependency.

### Also added — LZ-027 break-glass recovery

Closes the operational fail-closed risk surfaced in Brian
Crabtree's external Triad review (2026-05-11): prior to
v0.1.20, a persistent Shakespeare-mode lockout (camera
failure, `face_compare` regression, LZ-013 threshold
mis-calibration) had no documented recovery path other than
manually editing `~/.face_sentinel/state.json` from a Terminal
that hadn't loaded `/lazarus`. New `--recover` command
provides a documented two-method break-glass surface.

Spec-only at this commit. The `face_sentinel.py` implementation
+ `test/test_recovery.py` test file land in a follow-up commit
so the joint TCE / break-glass governance update is reviewable
as a single atomic spec change.

Surface (shipping at v0.1.21):

- `face_sentinel.py`:
  - `recover(token: str = None)` — break-glass entry point.
    Two methods in priority order: (1) Touch ID via
    `_touchid_check()`; (2) recovery-token match against
    `~/.face_sentinel/recovery_token.txt` (64-char hex,
    `hmac.compare_digest` for timing safety, whitespace
    stripped before compare). Either method on success
    flips `state.json` to `mode="normal"`,
    `authenticated=True`, refreshes `auth_time` +
    `last_seen_owner`, pops `lockout_time` +
    `lockout_distance`, logs `recovery_used` with method
    + `prior_mode` + `prior_lockout_reason`.
  - `_read_recovery_token()` — reads the token file,
    returns empty string on missing/unreadable.
  - `RECOVERY_TOKEN_FILE` constant — `BASE_DIR /
    "recovery_token.txt"`.
  - argparse `--recover` (mutex with --auth/--enroll/etc.)
    and `--token <hex>` (modifier for the no-Touch-ID
    path). Dispatched via `recover(token=args.token)`.
- `test/test_recovery.py` — 7 branches + 2 locks
  (default-parameter via `inspect.signature` and
  `RECOVERY_TOKEN_FILE` path lock).

### Status changes

- **LZ-022..LZ-026** enter the spec at `:argued` with
  evidence type `manual`. Five joint-closure entries from
  the TCE pass.
- **LZ-027** enters the spec at `:tested` with evidence
  type `example-tested` (spec entry only; implementation
  lands at v0.1.21).
- Counts: 21/3/18/0/0/0/0 → **27/3/19/0/0/5/0**. The
  `:argued` count goes from 0 to 5 (honest per
  conjunctive-claim discipline); all 5 carry explicit
  promotion paths in their `Notes:` fields. `:tested` goes
  18 → 19 (LZ-027).

### Honest framing — break-glass recovery

Recovery paths weaken the cryptographic story but strengthen
the operational story — without them false-positive lockouts
have no off-ramp and the system is unusable as a daily-driver
sentinel. Recovery use rate should be near-zero in steady
state; high rate signals the primitive is mis-calibrated.

The recovery surface does NOT expand the auth surface — an
attacker with the owner's Touch ID finger or the recovery
token can clear lockout, but those are the same two factors
the owner uses to auth in the first place. Storing the
recovery token in a password manager (not in
`~/.face_sentinel/` itself) separates the blast radius.

**What this DOESN'T cover.** If Touch ID hardware fails AND
no recovery token was provisioned, the owner is still locked
out and must edit `state.json` manually. The spec
acknowledges this gap rather than pretending it's solved.

### Files changed

- `LAZARUS_SPEC.md` — new v0.1.20 section with LZ-022..LZ-026
  joint-closure entries + LZ-027 break-glass entry; counts
  refreshed.
- `dashboard.md` — last-updated stamp; counts refreshed;
  priority stack reordered; tests list extended.
- `changelog.md` — this entry.

No source code changes in this commit. TCE entries capture
spec discoveries from the engine (driver shipped at
triadic-coordination-engine commit 3fcccf3); LZ-027
implementation lands at v0.1.21.

---

## v0.1.17 — 2026-05-11 — OverSight Tier 2 allowlist + state-flip (LZ-021)

The OverSight integration gains its second tier: on non-
allowlisted camera/mic activation, the script writes
`state.json` with `mode=shakespeare` and emits an
`oversight_tier2_alert` event. The next `/lazarus`
invocation reads the flipped state and shifts into refusal
mode. Tier 1 logging (LZ-011) is unchanged.

### Added

- `oversight_action.sh` Tier 2 block:
  - **Built-in allowlist** of 12 default executables
    (imagesnap, python3, Python, FaceTime, zoom.us,
    Photo Booth, Photos, Safari, coreaudiod,
    VTDecoderXPCService, AppleCameraAssistant,
    screencaptureui).
  - **User allowlist** at
    `~/.face_sentinel/oversight_allowlist.txt` (one
    executable basename per line; `#` comments and blank
    lines ignored).
  - **On-event + non-allowlisted exec** → inline Python
    writes `state.json` with `mode=shakespeare`,
    `authenticated=false`, `lockout_time=<now>`,
    `lockout_reason="oversight_unallowed"`, plus
    `oversight_alert_executable`,
    `oversight_alert_pid`, `oversight_alert_device`
    fields. AND appends `oversight_tier2_alert` to
    `sentinel.log`.
  - **Off-events never trigger Tier 2** — they're
    bookkeeping, not activation.
- `test/test_oversight_tier2.sh` — 6 subtests:
  1. on-event + non-allowlisted (bash via $$) →
     Tier 2 fires.
  2. on-event + allowlisted via user file →
     no Tier 2.
  3. off-event + non-allowlisted →
     no Tier 2.
  4. `# bash` comment line does NOT allowlist bash →
     Tier 2 fires.
  5. Blank-line-only allowlist file →
     no allowlisting → Tier 2 fires.
  6. Default allowlist contains `python3` (verified via a
     live `python3` background process).
- `.github/workflows/test.yml` — new CI step
  `LZ-021 — test_oversight_tier2.sh`.

### Status changes

- **LZ-021** enters the spec at `:tested` with evidence
  type `example-tested`.
- **LZ-011** description amended: notes that Tier 2 landed
  at v0.1.17 as LZ-021, and that Tier 1's behavior is
  unchanged. Status / evidence remain.
- Counts: 20 / 3 / 17 / 0 / 0 / 0 / 0 → **21 / 3 / 18 / 0 /
  0 / 0 / 0**.

### Tier 2b deferred (honest framing)

`pmset displaysleepnow` to physically lock the screen on
Tier 2 alert is deliberately NOT shipped. Screen-lock-on-
unallowlisted is aggressive enough to risk disrupting
legitimate but unanticipated workflows (a freshly installed
video tool, WebRTC on a different browser, a screen
recorder). Tier 2a (state-flip only) signals the companion
to refuse without taking the user's screen down — the
softer move. Tier 2b is documented as future work; the
proposed shape is an opt-in sentinel file (e.g.
`~/.face_sentinel/oversight_lockscreen`) that
`oversight_action.sh` checks before invoking `pmset`. One
config-file-touch when needed.

## v0.1.16 — 2026-05-11 — runtime-LLM-behavior transcript audit (LZ-020)

First runtime evidence for the prompt-layer claims
(LZ-001/003/004/012). Real /lazarus session transcripts
captured 2026-05-10, asserted on for shape. Plus a design
doc covering the broader architectural options.

### Added

- `docs/runtime_harness_design.md` — design doc covering
  three approaches (recorded-transcript audit, Anthropic-
  API integration, probabilistic property suite) with
  tradeoffs, the API-vs-Claude-Code-context asymmetry, and
  a staged recommendation (transcript stub now; API
  integration deferred until model-drift becomes a
  load-bearing concern).
- `test/transcripts/shakespeare_mode_session.txt` — real
  /lazarus invocation with `mode=shakespeare` captured
  2026-05-10. Five user turns; every LAZARUS reply is in
  Bard mode (sustained refusal directive holds in practice).
- `test/transcripts/normal_mode_session.txt` — normal-mode
  invocation post-auth-clear. Network values redacted to
  placeholders for the public repo; the test asserts on
  field labels (MONITORS/VPN/NETWORK/ROUTE/SENTINEL/
  PARASITES), not values.
- `test/test_runtime_harness.py` — eight-block test:
  1. Shakespeare transcript: ≥1 Bard vocabulary pattern
     (from 11 named patterns) AND no diagnostic field
     labels.
  2. Sustained refusal: ≥2 user turns each paired with a
     Bard response.
  3. Normal transcript: ALL six diagnostic field labels
     present AND no Bard vocabulary.
  4. Normal transcript carries the ASCII-art cloud and the
     literal `mode: normal` line.
  5. Privacy redaction guard: no concrete private IPv4
     (last two octets numeric), no literal MAC address.
  6. Design doc anchors: `Recorded-transcript audit`,
     `Anthropic API integration`, `point-in-time`.
- `.github/workflows/test.yml` — new CI step
  `LZ-020 — test_runtime_harness.py`.

### Status changes

- **LZ-020** enters the spec at `:tested` with evidence
  type `example-tested`.
- Counts: 19 / 3 / 16 / 0 / 0 / 0 / 0 → **20 / 3 / 17 / 0 /
  0 / 0 / 0**.

### Honest framing

This is *point-in-time* evidence — the transcripts froze a
specific runtime behavior from 2026-05-10. Model updates
after that date can introduce drift this test will not
catch. The mitigation is to refresh the transcripts when
the prompt changes. The escalation path (if model-drift
becomes a load-bearing concern) is the Anthropic-API
integration test outlined as Approach B in the design doc.

The slash-command framing — Claude Code agent loop +
tool registry + state file read — is the actual runtime
environment the transcripts captured. An API integration
test (`messages.create`) reproduces the prompt-loading but
not the agent loop or tool dispatcher in their
lazarus-specific configuration. The transcript approach is
therefore the more faithful evidence even with the
point-in-time caveat.

### Iteration note

The Shakespeare transcript fixture contains a `#` comment
block describing what the test should check; that block
mentioned the diagnostic field names ("no MONITORS, VPN,
NETWORK fields"), which the initial test flagged as
forbidden-substring-present false positives. Fixed by
adding a `load_transcript_content()` helper that strips
`#` comment lines before assertion. Real transcript content
(USER/LAZARUS turns + the literal status block in normal
mode) passes assertions cleanly.

## v0.1.15 — 2026-05-11 — `--strict-touchid` hard-gate (LZ-019)

New operational feature, not a promotion. Adds the
`--strict-touchid` CLI flag to `face_sentinel.py --auth`,
promoting Touch ID from opportunistic / fail-open (LZ-015)
to a hard auth gate when the user opts in. Default behavior
unchanged — opportunistic mode remains the default and the
fail-open story for hardware-less Macs is preserved.

### Added

- `face_sentinel.py`:
  - `auth()` now takes a `strict_touchid: bool = False`
    parameter. Default `False` preserves legacy
    opportunistic behavior.
  - Step 1 (Touch ID gate) branches on `strict_touchid`:
    when `True` and `_touchid_check()` returns anything
    other than `"ok"`, the function prints a diagnostic,
    logs `touchid_strict_fail` with the offending result,
    and `sys.exit(1)` before reaching the face-match step.
  - argparse `--strict-touchid` flag wired into the CLI;
    dispatched via `auth(strict_touchid=args.strict_touchid)`.
- `test/test_auth_strict_touchid.py` — 5 branches plus a
  default-parameter lock:
  1. strict + ok → proceeds (face match completes, mode →
     "normal", `touchid_ok` + `auth_ok` logged).
  2. strict + nonzero → exit 1, `touchid_strict_fail` with
     `result="nonzero"` logged, no downstream events.
  3. strict + unavailable → exit 1, `touchid_strict_fail`
     with `result="unavailable"`.
  4. non-strict + nonzero → unchanged from LZ-015 (proceeds,
     `touchid_nonzero` logged).
  5. non-strict + unavailable → unchanged from LZ-015.
  Plus `inspect.signature(auth)` assertion locks
  `strict_touchid` default at `False`.
- `.github/workflows/test.yml` — new CI step
  `LZ-019 — test_auth_strict_touchid.py`.

### Status changes

- **LZ-019** enters the spec at `:tested` with evidence type
  `example-tested`.
- LZ-015's Notes field updated: the deferred-future-work
  note now points at LZ-019 as the shipped strict
  alternative (still opt-in; default remains
  opportunistic).
- Counts: 18 / 3 / 15 / 0 / 0 / 0 / 0 → **19 / 3 / 16 / 0 /
  0 / 0 / 0**.

### Honest framing

Strict mode raises the bar in the common case (laptop
snatched, owner not present, attacker dismisses or can't
satisfy the Touch ID prompt → strict mode prevents the
face check from running at all). It is NOT a structural
guarantee — an attacker who can disable / occupy / spoof
Touch ID hardware bypasses regardless. Honest framing
matches LZ-015's: the defensive value is at the
prompt/hardware-interaction layer, not at the substrate
level.

The `--no-touchid` escape hatch (proposed in the dashboard
priority stack) is deliberately NOT shipped — opportunistic
mode (the default) already accommodates Touch-ID-less
hardware via the `"unavailable"` fail-open path. Adding a
third mode would be a feature-creep without a concrete use
case.

## v0.1.14 — 2026-05-11 — third `:proved` entry (LZ-018, classification dispatcher)

Adds LZ-018: priority-ordered classification dispatcher
proved in Lean4 as the abstract content underlying LZ-009's
`network_monitor.classify`. Same hermetic pattern as v0.1.12
and v0.1.13.

### Added

- `src/lean4/Classify.lean` — `Class` inductive (4
  constructors: `system`, `known`, `aiWatch`, `other`) + the
  `classify` dispatcher function + 6 theorems:
  - `classify_system_priority` — `isSystem c = true` →
    result is SYSTEM regardless of the other predicates.
  - `classify_known_priority` — `¬isSystem ∧ isKnown` →
    KNOWN.
  - `classify_aiWatch_priority` — `¬isSystem ∧ ¬isKnown ∧
    isAI` → AI_WATCH.
  - `classify_other_default` — all three false → OTHER.
  - `classify_exhaustive` — for any input, result is one of
    the four constructors.
  - `classify_disjoint` — the four constructors are pairwise
    distinct (corollary of inductive constructor
    disjointness).
- `src/lean4/lakefile.lean` — third `@[default_target]`
  stanza adds `Classify` to the default build set so
  `lake build` compiles all three proofs.

### Status changes

- **LZ-018** enters the spec at `:proved` with evidence type
  `lean-proved`. Third lazarus entry at this tier
  (alongside LZ-016 outliers and LZ-017 liveness metric).
- Counts: 17 / 2 / 15 / 0 / 0 / 0 / 0 → **18 / 3 / 15 / 0 /
  0 / 0 / 0**.

### Honest framing

The proof is abstracted over the three boolean predicates
(`is_system`, `is_known_good`, `is_ai_related`) — it doesn't
depend on what the allowlists (`SYSTEM_PREFIXES`, etc.)
actually contain, only on the cascade structure. The value
of this abstraction: the priority order is structural rather
than empirical. LZ-009's Python test exercises specific
connection records; LZ-018 proves the dispatch correctness
for any combination of predicate values, including
degenerate cases (all three true, all three false, only AI
true, etc.).

The `classify_disjoint` corollary would catch a refactor
that accidentally collapsed two classes into one (e.g.
removing the `Class.known` constructor and re-routing KNOWN
to OTHER) — the explicit disjointness proof would fail to
typecheck once the inductive structure changes.

### Iteration note

One v4.29.1 friction: the lakefile sets `autoImplicit :=
false`, which means `α` in `∀ α (f : α → Bool), ...`
positions doesn't get implicit-bound automatically. Fixed
by adding explicit `{α : Type}` parameters to the
dispatcher def and all six theorems. The fix is a clean
six-line patch; the proofs themselves needed no other
adjustments.

Build time: ~180ms for Classify.lean.

## v0.1.13 — 2026-05-11 — second `:proved` entry (LZ-017, liveness metric)

Adds LZ-017: byte-diff metric properties proved in Lean4 as
the abstract mathematical content underlying the LZ-013
liveness probe. Same hermetic pattern as v0.1.12.

### Added

- `src/lean4/Liveness.lean` — four metric theorems:
  - `deltaCount_self` — `delta(a, a) = 0`. A sequence
    compared with itself has zero diffs.
  - `deltaCount_symm` — `delta(a, b) = delta(b, a)` (under
    the equal-length precondition).
  - `deltaCount_le_length` — `delta(a, b) ≤ |a|`. Bounded by
    sequence length (corollary: normalized delta ≤ 1.0).
  - `deltaCount_zero_iff_eq` — `delta(a, b) = 0 ↔ a = b`
    (under equal-length precondition). Discriminating: zero
    distance exactly characterizes equality.
- `src/lean4/lakefile.lean` — second `@[default_target]`
  stanza adds `Liveness` to the default build set so
  `lake build` compiles both proofs.

### Status changes

- **LZ-017** enters the spec at `:proved` with evidence type
  `lean-proved`. Second lazarus entry at this tier
  (alongside LZ-016 outlier-detection).
- Counts: 16 / 1 / 15 / 0 / 0 / 0 / 0 → **17 / 2 / 15 / 0 /
  0 / 0 / 0**.

### Honest framing

Structural-skeleton convention applies. The proof targets
the abstract metric (the `deltaCount` numerator); the
Python `_liveness_delta` normalizes by length and applies
the `LIVENESS_DELTA_MIN` threshold — those two steps are
shape-preserving and don't affect the metric properties.
LZ-013 covers the Python implementation via
`test/test_liveness_check.py`; LZ-017 layers on with the
mathematical proof.

Equal-length precondition: theorems carrying the same-length
hypothesis (symmetry, zero-iff-eq) make this explicit. The
function is total in Lean (returns 0 on length-mismatch
cases) but the metric properties only apply to the
equal-length subset. The Python implementation returns
`None` on length mismatch and the caller fails open —
that's an operational concern outside the metric content.

### Iteration notes

Three v4.29.1 API frictions during writing:
1. `simp [h, h.symm]` in the symmetry proof looped at max
   recursion depth — gave simp both `hd = hd'` and
   `hd' = hd` as rewrite rules, creating an infinite
   pingpong. Replaced with explicit `rw [if_neg h, if_neg h']`
   for the unequal branch and `rw [h]` (auto-rfls) for the
   equal branch.
2. `simp` after `rw [h]` reported "no goals to be solved"
   — rw auto-rfl'd the equality. Dropped the trailing simp.
3. `cases heq` / `List.head_eq_of_cons_eq` /
   `List.tail_eq_of_cons_eq` API uncertainties in
   `deltaCount_zero_iff_eq` — rewrote as a direct
   `by_cases` on head equality with `exfalso` for the
   unequal branch.

Build time after fixes: ~190ms for Liveness.lean.

## v0.1.12 — 2026-05-11 — first `:proved` entry (LZ-016, lean-proved)

Lazarus gains a hermetic Lean4 track at `src/lean4/` and ships
its first machine-verified proof: LZ-016, the abstract
outlier-detection algorithm that underlies LZ-014's Python
helper. Counts: 15 / 0 / 15 / 0 / 0 / 0 / 0 → **16 / 1 / 15 /
0 / 0 / 0 / 0**.

### Added

- `src/lean4/` — new directory mirroring the
  Triadic-Coordination-Engine hermetic pattern.
  - `lean-toolchain` — pins Lean v4.29.1 (matches the system
    Lean on macOS arm64).
  - `lakefile.lean` — single hermetic package, no external
    dependencies (no Mathlib on the default build path).
  - `.gitignore` — excludes `.lake/` and `*.olean` build
    artifacts.
  - `Outliers.lean` — the LZ-016 proof. Five theorems:
    - `outliers_subset` — output ⊆ input.
    - `outliers_empty` — empty input → empty output.
    - `outliers_singleton` — single-element input with
      multiplier ≥ 1 → empty (singleton can't outlier itself).
    - `outliers_constant` — all-same scores with multiplier
      ≥ 1 → empty (constant pool has no internal outliers).
    - `outliers_monotone_threshold` — `m₁ ≤ m₂` implies
      `outliers(s, m₂) ⊆ outliers(s, m₁)`.
- `.github/workflows/test.yml` — new "LZ-016 — Lean proof"
  CI step that installs `elan` (so the toolchain pin
  resolves) and runs `lake build` on `src/lean4/`. The CI
  step exits non-zero on any proof failure.

### Status changes

- **LZ-016** enters the spec at `:proved` with evidence
  type `lean-proved`. First lazarus entry at this tier.
- Counts: 15 / 0 / 15 / 0 / 0 / 0 / 0 → **16 / 1 / 15 / 0 /
  0 / 0 / 0**.

### Honest framing

Per the TCE structural-skeleton convention, this proof
targets the **abstract algorithm**, not the Python
implementation. The Python code (`_outliers_from_scores`)
matches the proved algorithm by inspection (single-line list
comprehension over the same predicate). LZ-014 covers the
Python implementation via `test/test_prune_logic.py`; LZ-016
layers on top with the mathematical proof.

Model: scores as `List Nat`, multiplier as `Nat`. The
division-free predicate `v * |s| > m * Σs` (multiplying the
Python predicate through by `|s|`) keeps the proof in pure
Nat arithmetic without rationals or Mathlib. This `Nat`-only
model is shape-equivalent to the rational version for
non-negative scores, which is the load-bearing case (Apple
Vision feature-print distances are always non-negative).

### Build notes

Local: `cd src/lean4 && lake build`. After elan resolves the
toolchain (first build), incremental builds run in ~150ms.

### Iteration note

First proof attempt failed on three API mismatches with Lean
v4.29.1:
1. `List.mem_of_mem_filter` doesn't exist — replaced with
   `(List.mem_filter.mp hv).1`.
2. `List.mem_cons_self hd tl` is a term-level instance, not
   an applied lemma — replaced with `List.mem_cons.mpr
   (Or.inl rfl)`.
3. `simp only [decide_eq_false_iff_not]` made no progress in
   the constant-pool theorem — replaced with an explicit
   `decide_eq_false` term derived from `omega`.

The final proof builds clean in ~150ms.

## v0.1.11 — 2026-05-11 — LZ-004 + LZ-012 → :argued = 0

Closes the last two `:argued` claims. Every LZ-NNN entry in
the spec now has runnable evidence under `test/`. Counts
reach **15 / 0 / 15 / 0 / 0 / 0 / 0**.

### Added

- `test/test_auth_clears_shakespeare.py` (LZ-004) — drives
  `face_sentinel.auth()` with all IO dependencies stubbed
  (`_touchid_check`, `capture_full`, `run_face_compare`,
  `shrink`) across four pre-state branches:
  1. **shakespeare → clear**: pre-state has
     `mode="shakespeare"` + `lockout_time` + `lockout_distance`.
     Post-state: `mode="normal"`, `authenticated=True`,
     lockout fields popped, `auth_time` + `last_seen_owner`
     refreshed. Log emits both `shakespeare_cleared` AND
     `auth_ok`.
  2. **fresh auth**: pre-state `mode="normal"`. Post:
     unchanged mode, `authenticated=True`. Log emits
     `auth_ok` only (no `shakespeare_cleared`).
  3. **empty state**: pre-state `{}`. Post: mode and
     authenticated set cleanly from scratch.
  4. **lockout_reason linger lock**: pre-state with
     `lockout_reason="liveness_fail"` + `liveness_delta`.
     Post: mode/lockout_time/lockout_distance cleared, but
     `lockout_reason` + `liveness_delta` intentionally
     linger. Documents current behavior so a future change
     trips the test.
- `test/test_companion_readonly_discipline.py` (LZ-012) —
  static prompt-contract lint on `lazarus.md` §"What you
  do NOT do":
  1. Section header exists.
  2. All six prohibition directives present verbatim.
  3. Closing observe/flag/watch + "That is all." anchor.
  4. **Counter-positive scan**: within the prohibition
     section, no permissive-language patterns (`"you can
     write"`, `"you may commit"`, etc.) — catches refactors
     that accidentally invert a prohibition.
  5. Spec entry references the section name.
  6. README's user-facing discipline phrasing intact.
- `.github/workflows/test.yml` — two new CI steps.

### Status changes

- LZ-004 → `:argued` to `:tested`.
- LZ-012 → `:argued` to `:tested`.
- Counts: 15 / 0 / 13 / 0 / 0 / 2 / 0 → **15 / 0 / 15 / 0 /
  0 / 0 / 0**. Every LZ-NNN entry now backed by a runnable
  test.

### Honest framing

All four prompt-layer LLM-behavior claims (LZ-001, LZ-003,
LZ-004, LZ-012) are now `:tested` via static prompt-contract
tests rather than runtime LLM-behavior tests. The tests catch
refactors that weaken the contract; they do NOT prove an LLM
consumer respects the contract at runtime. The pragmatic
threat model is "developer accidentally inverts a directive
during a refactor" — which the tests catch. A model-in-the-
loop integration harness would close the runtime gap; it's
tracked as priority #3 in the dashboard, held until/unless
the prompt-contract layer demonstrates inadequacy in
practice.

### Cleanup pointer

The LZ-004 test locks the current behavior where `auth()`
pops `lockout_time` + `lockout_distance` but NOT
`lockout_reason` + `liveness_delta`. If you want a fully-
clean post-auth state, add those two pops and update the
test alongside. Low priority; doesn't affect security
(mode flip is what matters).

## v0.1.10 — 2026-05-11 — LZ-003 Shakespeare-mode prompt-contract test

Promotes LZ-003 (Shakespeare-mode companion refusal) from
`:argued` to `:tested` via a static prompt-contract test on
`lazarus.md` §Shakespeare mode plus the producer-side
`face_sentinel.py auth()` mode-flip. Same pattern as LZ-001:
the *runtime* claim (LLM-behavior) stays a prompt-layer
guarantee enforced by review; the *contract* the LLM reads
is what's CI-protected.

### Added

- `test/test_shakespeare_mode_refusal.py` — nine-layer static
  lint:
  1. `## Shakespeare mode` section header exists.
  2. `CHECK THIS FIRST` priority anchor (load-bearing for
     first-response routing).
  3. State-path + mode-field references + both literal
     values (`"shakespeare"`, `"normal"`).
  4. Four refusal directives present verbatim:
     - `"Do NOT run normal diagnostics"`
     - `"Do NOT report system status"`
     - `"Respond ONLY with random Shakespeare quotes"`
     - `"Continue this behavior for ALL responses until the
       mode is cleared"`
  5. Single clearing path: `face_sentinel.py --auth`.
  6. Producer side: `auth()` flips mode → `"normal"` AND
     reads `was_shakespeare` for the welcome-back message.
  7. Character-discipline anchors `"Stay in character"` +
     `"Do not acknowledge"`.
  8. Counter-positive lock: `auth()` pops `lockout_time` +
     `lockout_distance` from state on clear.
  9. Spec entry's Description carries the phrase
     `prompt-layer` (catches refactors that secretly upgrade
     the claim to "hard gate").
- `.github/workflows/test.yml` — runs the test as the
  thirteenth CI step.

### Status changes

- LZ-003 → `:argued` to `:tested`. Evidence type → `manual`
  to `example-tested`.
- Counts: 15 / 0 / 12 / 0 / 0 / 3 / 0 → **15 / 0 / 13 / 0 /
  0 / 2 / 0**.

### Honest framing

This test catches refactors that accidentally weaken the
refusal (e.g. "ONLY" → "MOSTLY", removing the "do not
acknowledge" clause, deleting the section header). It does
NOT prove an LLM consumer actually respects the instructions
at runtime — that would require a model-in-the-loop
integration harness (non-deterministic, API access, billable,
slow). A hard gate would require sandboxing the model's tool
surface, which is out of scope.

### Iteration note

First implementation asserted on an `"Examples of Shakespeare
mode responses"` section header that doesn't exist in
`lazarus.md` (the example quotes live in `README.md`, not
the slash-command spec). Replaced with the two
character-discipline anchors `"Stay in character"` and
`"Do not acknowledge"` that ARE in the prompt and are
load-bearing for the in-character refusal style.

## v0.1.9 — 2026-05-10 — LZ-010 honeypot loop-connect test

Promotes LZ-010 (network-honeypot port listeners) from
`:argued` to `:tested` via a localhost loop-connect
integration test. The previously-flagged "fragile in CI"
concern is addressed; the test passes on `macos-latest` with
a clear failure mode if its port is unavailable.

### Added

- `test/test_honeypot_listener.py` — eight-step integration
  test:
  1. Monkey-patches `LOG_DIR` to a tempdir.
  2. Starts `listen_on_port(38080, "TEST-HTTP", serve_http)`
     in a daemon thread.
  3. Polls with timeout (no fixed sleeps) for the listener
     to actually bind via a 127.0.0.1 connect probe.
  4. Opens a fresh client socket, sends a minimal HTTP GET.
  5. Verifies the response contains `200` and the banner
     content.
  6. Polls for the log file to appear.
  7. Verifies the JSONL record shape (`timestamp`, `remote`,
     `port`, `service` keys; service == `"HTTP"`; port
     matches; remote has `<ip>:<port>` shape).
  8. Locks the SERVICES table (port → service-name mapping
     for the five documented ports).
- `.github/workflows/test.yml` — runs the new test as the
  twelfth step on every push.

### Status changes

- LZ-010 → `:argued` to `:tested`. Evidence type → `manual`
  to `example-tested`.
- Counts: 15 / 0 / 11 / 0 / 0 / 4 / 0 → **15 / 0 / 12 / 0 /
  0 / 3 / 0**.

### Fragility mitigations

The v0.1.0 spec entry deferred this test as "fragile in CI."
Concrete mitigations:
- **Port 38080** — high, uncommon. If collision occurs the
  test fails loudly during the bind-probe step with a
  clear message; honest failure beats silent pass.
- **Poll-with-timeout** instead of fixed sleeps for both
  binding (5s) and log-file appearance (5s). No flaky
  "did the listener come up yet?" race.
- **Daemon thread** — the listener thread dies cleanly on
  process exit. No orphan listeners.
- **Log-write race handled** — `log_connection` runs after
  `sendall` in `serve_http`, so the client can observe the
  response before the log line is on disk. The test
  accommodates this by polling for the file.

### Honest framing

The test runs ONE listener on ONE port; it does not exercise
all five SERVICES entries at runtime. The SERVICES table
lock catches drift in the documented surface (port number
or service-name rename) without requiring five concurrent
port-binds in the test.

## v0.1.8 — 2026-05-10 — LZ-001 producer/consumer decoupling test

Promotes LZ-001 (visual-skin/security-primitive decoupling)
from `:argued` to `:tested` via a static architecture test
that locks the producer/consumer separation between
`face_sentinel.py` and `lazarus.md`.

### Added

- `test/test_visual_skin_decoupling.py` — six layers of
  architectural check:
  1. Producer writes mode-value vocabulary (`"normal"` and
     `"shakespeare"` literals + `state["mode"] =`
     assignment).
  2. Producer is free of presentation content. Forbidden
     patterns:
     - archaic-pronoun substrings inside quote text (`doth`,
       `thou`, `thee`, `thy`) with word-boundary matching
       so common English words like "without" don't false-
       positive
     - four specific Shakespeare-quote phrases
     - the cloud ASCII-art fragment
     - "I am Mother" character-voice string
  3. Consumer carries the skin (ASCII-art fragment +
     Shakespeare-mode section header).
  4. Mode-value vocabulary parity: consumer references both
     `"shakespeare"` and `"normal"` literals.
  5. README §Customization documents the swap pattern
     ("Bring your own lockout mode").
  6. Spec entry names the `mode` and `authenticated` fields.
- `.github/workflows/test.yml` — runs the new test as the
  eleventh step on every push.

### Status changes

- LZ-001 → `:argued` to `:tested`. Evidence type → `manual`
  to `example-tested`.
- Counts: 15 / 0 / 10 / 0 / 0 / 5 / 0 → **15 / 0 / 11 / 0 /
  0 / 4 / 0**.

### Honest framing

This is a static / architectural test. It cannot directly
prove that an LLM consumer respects the mode flag at
runtime — that's a prompt-layer guarantee enforced by
review of the conversation transcript. What the test DOES
catch is the silent regression where a refactor folds
presentation content into the producer or breaks the shared
mode-value vocabulary. The pragmatic threat model is
"developer accidentally inlines a Shakespeare quote in
face_sentinel.py during a refactor," which the test
catches.

### Iteration note

First implementation banned `\bBard\b` as a forbidden
pattern; that immediately tripped because the producer's
module docstring uses "Bard" as a descriptive label for
the lockout mode ("Claude speaks only in Bard"). Walked
back to allow the descriptive label (and "Shakespeare" by
extension) while continuing to ban actual quote text
(archaic pronouns, named quote phrases). Honest framing:
the test policy is "no presentation content," not "no
mention of the skin's name."

## v0.1.7 — 2026-05-10 — LZ-002 band-consistency test

Promotes LZ-002 (face-match distance bands) from `:argued`
to `:tested` via a Python test that locks threshold values
and band ordering across Python (`face_sentinel.py`) and
Swift (`face_compare.swift`).

### Added

- `test/test_distance_band_thresholds.py` — five layers of
  consistency check:
  1. Python constants hold expected values (MATCH=18.0,
     UNCERTAIN=25.0, LOCK=35.0).
  2. Band ordering: MATCH < UNCERTAIN < LOCK.
  3. Cross-language consistency: `face_compare.swift`
     contains the literal strings `< 18.0`, `< 25.0`, and
     `>= 18.0`, derived from the Python constants via
     f-string formatting. Catches the silent threshold-
     drift failure mode where someone updates one file
     without the other.
  4. Swift `cmdMatch` comment block documents the same
     bands (12-18 likely match, 18-25 uncertain, > 25
     different person).
  5. Python constant declarations carry their original
     inline calibration comments.
- `.github/workflows/test.yml` — runs the threshold test
  on every push as the tenth step.

### Status changes

- LZ-002 → `:argued` to `:tested`. Evidence type → `manual`
  to `example-tested`.
- Counts: 15 / 0 / 9 / 0 / 0 / 6 / 0 → **15 / 0 / 10 / 0 /
  0 / 5 / 0**.

### Honest framing

The test covers the *consistency* surface (no drift across
files, band ordering preserved, documentation in sync). It
does NOT validate the empirical calibration of the 18/25/35
thresholds against real face distances. That requires a
fixture set of (image, expected band) pairs, which carries
either an identifiability problem (real faces) or
licensing / sourcing burden (PD portraits, AI-generated
synthetics). The calibration gap is tracked as a
future-work open question in `dashboard.md`.

## v0.1.6 — 2026-05-10 — LZ-005 grep-lint

Promotes LZ-005 (apple-vision-local-only) from `:argued` to
`:tested` via a CI grep-lint that enforces the no-networking
claim on every push.

### Added

- `test/test_no_networking_imports.sh` — greps
  `face_compare.swift` for Swift networking symbols
  (`URLSession`, `URLProtocol`, `NSURLConnection`,
  `import Network`, `NWConnection`, `NWListener`,
  `CFNetwork`) and `face_sentinel.py` for Python networking
  imports (`import socket`, `from socket`, `import urllib`,
  `from urllib`, `import requests`, `from requests`,
  `import http.`, `from http`, `urlopen`). Plus a size
  guard so the negative test doesn't silently pass on an
  empty / stub-replaced source file (face_compare.swift ≥
  50 lines, face_sentinel.py ≥ 200 lines).
- `.github/workflows/test.yml` — runs the lint on every
  push as the ninth test step.

### Status changes

- LZ-005 → `:argued` to `:tested`. Evidence type → `manual`
  to `example-tested`.
- Counts: 15 / 0 / 8 / 0 / 0 / 7 / 0 → **15 / 0 / 9 / 0 /
  0 / 6 / 0**.

### Honest framing

The lint is a source-text regression check, not a runtime
security guarantee. A determined adversary who obfuscates,
minifies, or dynamically dispatches networking calls could
bypass it. The defensive value is catching accidental
introduction of network dependencies during refactoring —
which is the realistic threat model for a single-developer
project.

Promotion to a runtime guarantee would require sandboxing or
network-namespace isolation (Linux only) or sandbox-exec
on macOS. Held as future work.

## v0.1.5 — 2026-05-10 — `:open` count reaches zero

Three test files promote the three remaining `:open` spec
entries from v0.1.0 — LZ-006 (reference-storage-bounded),
LZ-007 (watch-loop-state-transitions), LZ-008
(peek-json-output-shape) — to `:tested`. Plus one drive-by
bug fix in `prune_oldest` and one test affordance
(`FACE_COMPARE_STUB` env var) that delivers what the v0.1.0
dashboard promised as the top priority.

### Added

- `face_sentinel.py`:
  - `FACE_COMPARE_STUB` env-var check at the top of
    `run_face_compare()`. When set, the function short-
    circuits the subprocess invocation and returns the
    parsed JSON directly. Used for manual testing and
    shell-driven verification; production callers leave
    the env var unset.
- `test/test_reference_bounds.py` — LZ-006. Tests
  `prune_oldest` across under-cap (no-op), at-cap (no-op),
  over-by-one (removes oldest by mtime), over-by-ten,
  all-three-files-deleted-per-ref, mtime-vs-alphabetical
  ordering, and the regression case for the negative-index
  bug. Plus a value lock on `MAX_REFERENCES == 50`.
- `test/test_watch_state_transitions.py` — LZ-007. Tests
  `check_once` across 8 branches (no-face × 3, match × 2,
  uncertain, mismatch × 2) plus 2 early-return paths
  (capture-fail, match-error). Uses module-level
  monkey-patching of `capture_full` / `run_face_compare` /
  `liveness_check` / `backgrounds_similar` / `shrink` /
  `lock_screen` plus tempdir overrides for state-file
  paths. Plus a value lock on `LOCK_THRESHOLD == 35.0`.
- `test/test_peek_output.py` — LZ-008. Tests `peek()` JSON
  output across 5 branches (capture-fail, empty desk,
  owner, uncertain, stranger). Uses `FACE_COMPARE_STUB`
  env-var plus monkey-patched `capture_full`. Verifies
  output is a single line of well-formed JSON with the
  spec'd field shape and the `sys.exit(1)` path on capture
  failure.
- `docs/lazarus_open_promotion_v0_1_5_companion.md` —
  companion doc per standard.

### Fixed

- `face_sentinel.py prune_oldest()`: added `if to_remove
  <= 0: return` guard. Without it, calling the function
  with N < MAX_REFERENCES would compute a negative slice
  index and silently delete all-but-newest. The production
  caller (`enroll()`) already guarded against this, but
  exposing the function to direct test / CLI use made the
  latent bug real. The regression test
  (`test_under_cap_guard_not_negative_index_disaster`)
  locks the fix in.

### Status changes

- LZ-006 → `:open` to `:tested`.
- LZ-007 → `:open` to `:tested`.
- LZ-008 → `:open` to `:tested`.
- Counts: 15 / 0 / 5 / 0 / 0 / 7 / 3 → **15 / 0 / 8 / 0 / 0
  / 7 / 0**. `:open` count reaches zero.

### Notes

- The v0.1.0 dashboard's #1 priority item — `FACE_COMPARE_
  STUB` env-var to unlock LZ-006/007/008 — is now done.
  Two of the three tests (LZ-006, LZ-007) used module-level
  monkey-patching instead, which is cleaner Python practice
  than env-var fishing; LZ-008 uses the env-var path so the
  affordance has both an in-source consumer and a CI
  exerciser.
- Dashboard drive-by cleanups: line about "runs both tests"
  (stale from v0.1.1) updated to "runs the full test
  suite"; OverSight Tier 2 entry corrected from "LZ-013"
  (taken by liveness) to "LZ-016" (next available ID).

## v0.1.4 — 2026-05-10 — Touch ID opportunistic pre-face gate

`face_sentinel.py --auth` is now two-factor: Touch ID
(fingerprint) before face match. Ports the Touch ID step from
the personal working copy at `~/Projects/Possibilistic_Security/
face_sentinel.py`. Fail-open semantics — Touch ID strengthens
auth when available but never blocks on hardware that's missing
or misbehaving.

### Added

- `face_sentinel.py`:
  - `_touchid_check(timeout_seconds=30, _runner=None)` helper.
    Returns `"ok"` / `"nonzero"` / `"unavailable"` based on
    `bioutil -r` outcome. The `_runner` parameter is injected
    by tests; production callers leave it `None`.
  - `auth()` now runs `_touchid_check()` as Step 1 before
    face capture. Each outcome is printed to stdout and
    logged to `sentinel.log` as `touchid_ok` /
    `touchid_nonzero` / `touchid_unavailable`.
- `test/test_touchid_check.py` — exercises all three return
  paths via injected stubs, plus timeout-parameter plumbing,
  default-timeout value lock (30s), and the guarantee that
  unexpected exceptions propagate (only `TimeoutExpired` and
  `FileNotFoundError` are caught).
- `LAZARUS_SPEC.md` — new LZ-015 entry under a v0.1.4 section.
  LZ-004 description updated to acknowledge the Touch ID
  step preceding face match.
- `artifact_registry.md` — LZ-015 row + counts bumped +
  A1–A6 refresh.
- `.github/workflows/test.yml` — CI runs the Touch ID test.
- `docs/lazarus_touchid_v0_1_4_companion.md` — companion doc
  per standard.

### Status changes

- LZ-015 enters the spec at `:tested`.
- Counts: 14 / 0 / 4 / 0 / 0 / 7 / 3 → **15 / 0 / 5 / 0 / 0 /
  7 / 3**.

### Honest framing

Fail-open Touch ID is the right default for a single-owner
desktop tool, but it is not a structural guarantee. An
attacker who can disable / occupy / spoof Touch ID hardware
(or who is the legitimate owner on a Mac without Touch ID at
all) bypasses this layer entirely. The defensive value is
raising the bar in the common case — someone with the laptop
but without the owner's fingerprint. A stricter
`--strict-touchid` flag turning this into a hard gate is
future work.

### Why now

Same session, same trigger as the prior cleanup: the personal
working copy at `~/Projects/Possibilistic_Security/` had the
Touch ID step but lazarus didn't. Aaron flagged this in the
v0.1.3 wrap-up as the "feature lazarus is missing." This
commit ports it; from this point forward the two copies'
auth flows converge (modulo the `last_seen_aaron` vs
`last_seen_owner` field-naming difference).

## v0.1.3 — 2026-05-10 — leave-one-out pool quality scoring

Fixes a v0.1.0 bug in `face_sentinel.py --prune`: the previous
implementation matched each reference against the full pool
*including itself*, so every ref's best distance was 0
(self-match), the average was 0, and no outlier was ever
flagged. The tool was effectively a no-op that always
reported "All references consistent."

The fix uses Python-only logic — no Swift binary changes — by
constructing a per-ref leave-one-out pool of symlinks and
scoring against that.

### Added

- `face_sentinel.py`:
  - `PRUNE_OUTLIER_MULTIPLIER = 2.0` constant.
  - `_outliers_from_scores(scores, multiplier)` — pure
    helper, returns the subset of scores exceeding
    `multiplier × mean`.
  - `_prune_score_one(target, all_metas)` — leave-one-out
    nearest-neighbor score for a single ref. Builds a
    tempdir of symlinks to all OTHER refs, runs
    `face_compare match`, returns the best distance. Cleanup
    in `finally`.
- `test/test_prune_logic.py` — exercises the pure
  outlier-detection helper across empty / no-outlier /
  single-outlier / multiple-outlier / boundary (strict `>`)
  / custom-multiplier / single-element cases.
- `LAZARUS_SPEC.md` — new LZ-014 entry under v0.1.3 section.
- `artifact_registry.md` — LZ-014 row + counts bumped + A1–A6
  refresh.
- `.github/workflows/test.yml` — CI runs the prune-logic
  test.
- `docs/lazarus_prune_v0_1_3_companion.md` — companion doc
  per standard, including real-pool sweep results.

### Changed

- `face_sentinel.py prune_cmd()` rewritten to call
  `_prune_score_one` per ref and `_outliers_from_scores` on
  the result. Output now shows the leave-one-out average and
  surfaces flagged outliers with a guidance footnote that
  the algorithm cannot distinguish off-distribution refs
  from legitimate rare-condition refs — the human decides
  what to retire. Reports only; never auto-deletes.

### Status changes

- LZ-014 enters the spec at `:tested`.
- Counts: 13 / 0 / 3 / 0 / 0 / 7 / 3 → **14 / 0 / 4 / 0 / 0 /
  7 / 3**.

### Real-pool sweep result

Run on the live `~/.face_sentinel/reference/` pool (50 refs,
post the v0.1.3 enrollment session that added 12 fresh
kitchen-background captures): **average leave-one-out
nearest-neighbor distance 0.35, no outliers** (no ref's
nearest non-self neighbor exceeds 0.70). Pool is internally
coherent; no refs warrant retirement.

### Notes

- The default 2.0 multiplier is conservative — it only flags
  refs whose nearest non-self neighbor is at least *twice*
  the average. A pool with high overall coherence (like the
  current one at 0.35 average) gives the multiplier little
  to bite on. Drop to 1.5 for a stricter pass after pose /
  background variation expands.
- Symlinks are O(1); the per-ref tempdir construction adds
  negligible overhead vs the `face_compare` subprocess. Full
  50-ref sweep ran in ~30 s on the development rig.

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
