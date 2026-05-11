# Changelog — Lazarus

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
