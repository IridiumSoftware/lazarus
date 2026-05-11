# LAZARUS_SPEC.md

Formal spec for Lazarus — the visual-presence + network-posture
companion in the Triad Deployments portfolio. Spec entries follow
the LL-NNN pattern from LavaLamp's `LAVALAMP_SPEC.md`, prefixed
`LZ-NNN`. Companion documents live in `docs/`; the public-facing
artefact is `README.md`.

---

## v0.1.0 (2026-05-10) — first formal spec of the public release

The initial spec captures the v0.1 public release: face sentinel
(VNFeaturePrintObservation distance bands), Shakespeare-mode
companion lockout, network monitor + honeypot, and the OverSight
Tier 1 forensic camera/mic event logger. Twelve LZ-NNN entries.

### LZ-001 — visual-skin/security-primitive decoupling
- Key: companion appearance is decorative; mode flag is the security state
- Logic tier: Boundary
- Description: The Lazarus security primitive is a state machine
  rooted in `~/.face_sentinel/state.json`. The `mode` field
  (`"normal"` / `"shakespeare"`) and the `authenticated` boolean
  determine system behavior. The user-facing surface (the
  `~~~~~` ASCII art, the Shakespeare-quote affordance, the warm
  one-line observations) is decorative — replacing it with
  silence, Klingon, or any other lockout style does not change
  the security primitive. Same architectural separation as
  LavaLamp LL-002.
- Evidence type: manual
- Status: :argued
- Source: `face_sentinel.py` (state machine), `lazarus.md`
  (companion prompt), `README.md` §Customization.
- Notes: Promotion to `:tested` requires a test that swaps the
  visual skin and confirms the security state machine is
  unchanged. Held at `:argued` until that test exists.

### LZ-002 — face-match-distance-bands
- Key: VNFeaturePrintObservation distance bands 18 / 25 / 35
- Logic tier: Operational
- Description: Face matching uses Apple Vision's
  `VNGenerateImageFeaturePrintRequest` and the native
  `computeDistance` between two `VNFeaturePrintObservation`s.
  Distance thresholds are empirically calibrated:
  - `< 18.0` → match (same person)
  - `18.0 – 25.0` → uncertain (kept for human review)
  - `25.0 – 35.0` → mismatch (Shakespeare mode)
  - `> 35.0` → hard mismatch (Shakespeare mode + screen lock)
  The thresholds are duplicated between `face_compare.swift`
  (which decides `match` / `uncertain`) and `face_sentinel.py`
  (which decides `lock`). Drift between the two would be a bug.
- Evidence type: manual
- Status: :argued
- Source: `face_compare.swift` (`isMatch`/`uncertain`),
  `face_sentinel.py` (`MATCH_THRESHOLD`, `UNCERTAIN_THRESHOLD`,
  `LOCK_THRESHOLD`).
- Notes: Calibrated against the original developer's reference
  set; not formally derived. Promotion to `:tested` requires a
  fixture set of (image, expected band) pairs run in CI.

### LZ-003 — shakespeare-mode-as-companion-refusal
- Key: mode=="shakespeare" causes /lazarus to refuse normal diagnostics
- Logic tier: Operational
- Description: When `state.json.mode == "shakespeare"`, the
  `/lazarus` slash command (`lazarus.md`) instructs the LLM to
  respond only with Shakespeare quotes and to skip all
  diagnostic checks. Refusal is enforced at the *prompt layer*,
  not by code restriction — a different LLM, or a model that
  ignores the instruction, would defeat this layer. The
  defensive value is that the intruder's productive use of
  Claude is blocked, not that the model is technically prevented
  from answering.
- Evidence type: manual
- Status: :argued
- Source: `lazarus.md` §Shakespeare mode, `face_sentinel.py`
  (`watch` and `auth` set/clear `mode`), `README.md` §Shakespeare
  mode.
- Notes: Honest framing — this is a behavioral protocol, not a
  hard gate. `:argued` is the correct tier; a hard gate would
  require sandboxing the model's tool surface, which is out of
  scope.

### LZ-004 — auth-clears-shakespeare
- Key: --auth on a successful face match resets mode to "normal"
- Logic tier: Operational
- Description: When `face_sentinel.py --auth` succeeds (Touch ID
  gate per LZ-015, face detected, distance < `MATCH_THRESHOLD`),
  the script overwrites `state.json` with `authenticated=true`,
  `auth_time=<now>`, `last_seen_owner=<now>`,
  `mode="normal"`, and removes `lockout_time` and
  `lockout_distance`. The next `/lazarus` invocation reads the
  cleared state and resumes normal diagnostics.
- Evidence type: example-tested (in-session demonstration)
- Status: :argued
- Source: `face_sentinel.py` `auth()` (Touch ID step → face
  match → state update), `lazarus.md` §Shakespeare mode.
- Notes: Demonstrated live during the v0.1.0 rigor session
  (companion doc §3). Not yet a CI-runnable artifact — the
  match step requires a real camera and a real face. Held at
  `:argued`; promotion to `:tested` would require a stubbed
  `face_compare` binary that returns canned distances for
  fixture images.

### LZ-005 — apple-vision-local-only
- Key: face comparison runs entirely on-device via Vision framework
- Logic tier: Boundary
- Description: All face detection and feature-print extraction
  happens via Apple's Vision framework on the Apple Neural
  Engine. No image, no feature print, and no distance is sent
  off-device. References are stored under
  `~/.face_sentinel/reference/` as `.fpdata` (binary feature
  print) + `.json` (metadata) + `.jpg` (low-res cached source).
  `face_compare.swift` makes no network calls; `face_sentinel.py`
  makes no network calls. Enforced by a CI grep-lint on the two
  source files for networking-symbol substrings (see Test/Proof).
- Evidence type: example-tested
- Status: :tested
- Source: `face_compare.swift` (no `URLSession` / `URLProtocol`
  / `NSURLConnection` / `import Network` / `NWConnection` /
  `NWListener` / `CFNetwork`), `face_sentinel.py` (no
  `import socket` / `from socket` / `import urllib` /
  `from urllib` / `import requests` / `from requests` /
  `import http.` / `from http` / `urlopen`).
- Test/Proof: `test/test_no_networking_imports.sh` runs the
  full lint on every CI push. Plus a guard that asserts the
  files are non-trivially-sized (face_compare.swift ≥ 50
  lines, face_sentinel.py ≥ 200 lines) so the negative test
  doesn't silently pass on an empty/stub-replaced file.
- Notes: Honest framing — the lint is a source-text regression
  check, not a runtime security guarantee. A determined
  adversary who obfuscates, minifies, or dynamically dispatches
  networking calls could bypass it. The defensive value is
  catching accidental introduction of network dependencies
  during refactoring. Promotion to a runtime guarantee would
  require sandboxing / network-namespace isolation, which is
  out of scope for the v0.1 release.

### LZ-006 — reference-storage-bounded
- Key: <=50 references, ~30KB each, oldest pruned
- Logic tier: Operational
- Description: `face_sentinel.py` enforces `MAX_REFERENCES = 50`
  via `prune_oldest`, which sorts references by mtime and
  deletes the oldest until the count is at or below cap. Each
  reference is a (`.fpdata`, `.json`, `.jpg`) triple; the JPEG
  is downscaled to 480px via `sips`. The companion `--prune`
  command (LZ-014) reports outliers via leave-one-out
  nearest-neighbor scoring. `prune_oldest` guards against the
  under-cap negative-index case via `if to_remove <= 0: return`
  (fixed in v0.1.5 — without this, calling the function under
  cap would silently delete all-but-newest).
- Evidence type: example-tested
- Status: :tested
- Source: `face_sentinel.py` `enroll()` / `prune_oldest()`.
- Test/Proof: `test/test_reference_bounds.py` covers
  under-cap (no-op), at-cap (no-op), over-by-one (removes
  oldest by mtime), over-by-ten, all-three-files-per-ref
  removal, mtime-vs-alphabetical ordering, and the
  regression test for the negative-index bug. Plus a value
  lock on `MAX_REFERENCES == 50`.

### LZ-007 — watch-loop-state-transitions
- Key: check_once handles 8 branches over the capture+match cycle
- Logic tier: Operational
- Description: The `--watch` daemon's `check_once` function is
  an 8-branch state machine (post-v0.1.2 anti-spoof liveness
  fold-in):
  - **A.** `faces == 0` + `last_seen_owner` set + bg unchanged
    → `no_face owner_walked_away`, return.
  - **B.** `faces == 0` + `last_seen_owner` set + bg shifted →
    `no_face owner_walked_away` + `bg_shift`, return.
  - **C.** `faces == 0` + no `last_seen_owner` →
    `no_face owner_never_seen`, return.
  - **D.** `is_match` + liveness `live` → refresh
    `last_seen_owner`, log `match_ok` with `liveness_delta`.
  - **E.** `is_match` + liveness `not live` (LZ-013) →
    `liveness_fail` → `mode="shakespeare"`,
    `lockout_reason="liveness_fail"`, `authenticated=false`.
  - **F.** `uncertain` → log `uncertain`, no state change,
    keep capture for review.
  - **G.** mismatch + distance ≤ `LOCK_THRESHOLD` →
    `mode="shakespeare"`, `authenticated=false`, log
    `MISMATCH`.
  - **H.** mismatch + distance > `LOCK_THRESHOLD` → branch G
    plus `lock_screen()` and `LOCK` log event.
  Plus early-return paths for `capture_fail` (camera failure)
  and `match_error` (face_compare error).
- Evidence type: example-tested
- Status: :tested
- Source: `face_sentinel.py` `check_once()`.
- Test/Proof: `test/test_watch_state_transitions.py`
  exercises all 8 branches + 2 early-return paths by
  module-patching `capture_full`, `run_face_compare`,
  `liveness_check`, `backgrounds_similar`, `shrink`,
  `lock_screen` plus tempdir overrides for `REF_DIR`,
  `CAP_DIR`, `LOG_FILE`, `STATE_FILE`, `BG_SNAPSHOT`.
  Assertions cover the resulting `state.json` mutations
  and the `sentinel.log` event sequence. Plus a value lock
  on `LOCK_THRESHOLD == 35.0`.

### LZ-008 — peek-json-output-shape
- Key: --peek emits a single line of JSON with desk/who/faces/distance
- Logic tier: Boundary
- Description: `face_sentinel.py --peek` emits exactly one line
  of JSON to stdout suitable for remote consumption (e.g. via
  Tailscale SSH). Shape:
  - empty desk: `{"desk": "empty", "faces": 0}`
  - occupied: `{"desk": "occupied", "who": "owner"|"uncertain"|
    "stranger", "faces": <int>, "distance": <float, 1dp>}`
  - capture failure: `{"desk": "unknown", "error": "capture
    failed"}` (with `sys.exit(1)`)
- Evidence type: example-tested
- Status: :tested
- Source: `face_sentinel.py` `peek()`.
- Test/Proof: `test/test_peek_output.py` exercises all 5
  branches (capture-fail, empty, owner, uncertain, stranger)
  using the `FACE_COMPARE_STUB` env-var shim plus a
  monkey-patched `capture_full`. Assertions cover the
  output JSON shape (desk/who/faces/distance fields), the
  single-line property (no trailing garbage), the
  `sys.exit(1)` code path on capture failure, and the
  distance-rounded-to-1-decimal contract.

### LZ-009 — network-monitor-classification
- Key: outbound conns classified as AI_WATCH / KNOWN / SYSTEM / OTHER
- Logic tier: Operational
- Description: `network_monitor.py` `classify(conn)` partitions
  every observed outbound connection into one of four classes
  using three explicit allowlists:
  - `SYSTEM_PREFIXES` (e.g. `192.168.`, `127.0.0.1`, Apple's
    `17.`) → `SYSTEM`
  - `KNOWN_GOOD` (e.g. `api.anthropic.com`, `github.com`) →
    `KNOWN`
  - `AI_PROCESSES` (e.g. `claude`, `node`, `python`) →
    `AI_WATCH`
  - else → `OTHER`
  Order of evaluation is SYSTEM → KNOWN → AI_WATCH → OTHER, so
  AI processes hitting known-good destinations classify as
  `KNOWN`, not `AI_WATCH`.
- Evidence type: example-tested
- Status: :tested
- Source: `network_monitor.py` `classify()` + module-level
  allowlists.
- Test/Proof: `test/test_network_monitor_classify.py`.

### LZ-010 — network-honeypot-port-listeners
- Key: listens on 5 commonly-scanned ports, logs every connection
- Logic tier: Operational
- Description: `network_honeypot.py` binds five TCP listeners on
  `0.0.0.0`: 8080 (HTTP fake admin), 2222 (fake SSH banner), 21
  (FTP), 3306 (MySQL), 8443 (HTTPS-mgmt). Each handler emits a
  protocol-appropriate banner, reads the client's input, sends
  `BANNER_CONTENT` (or a default), logs to
  `./logs/honeypot_<date>.jsonl`. Port 21 needs root; the
  others bind unprivileged. Each listener runs on its own
  daemon thread; per-connection handlers are also daemon
  threads with 5s socket timeout.
- Evidence type: manual
- Status: :argued
- Source: `network_honeypot.py`.
- Notes: Promotion to `:tested` requires a localhost
  loop-connect test (open socket to 127.0.0.1:8080, expect a
  200 response with the banner, assert a JSONL log line was
  appended). Held at `:argued` because port-binding tests are
  fragile in CI; deferred to a follow-up session.

### LZ-011 — oversight-tier1-forensic-logging
- Key: every camera/mic event appended as a JSONL record
- Logic tier: Operational
- Description: `oversight_action.sh` is invoked by OverSight
  (objective-see) on every camera or microphone on/off event
  with `-device camera|microphone -event on|off -process <pid>
  -activeCount <N>`. The script appends a single JSONL record to
  `~/.face_sentinel/oversight_events.jsonl` with timestamp
  (UTC), device, event, pid, activeCount, executable
  (`ps -o comm=`), and full command (`ps -o command=`). Tier 1
  is forensic only — no active response. Tier 2 (auto-lockdown
  on non-allowlisted activation) is documented inline as the
  next layer.
- Evidence type: example-tested
- Status: :tested
- Source: `oversight_action.sh`.
- Test/Proof: `test/test_oversight_action.sh`.

### LZ-012 — companion-read-only-discipline
- Key: /lazarus skill MUST NOT write code, edit files, or commit
- Logic tier: Boundary
- Description: The `/lazarus` slash command (`lazarus.md`)
  contains an explicit "What you do NOT do" section listing six
  prohibitions: no writing/editing code, no commits, no file
  touching, no security-setting changes, no decisions for the
  user, no long answers. The companion is a watchful presence,
  not an actor. As with LZ-003 this is a prompt-layer
  enforcement, not a hard gate; the discipline failure mode is
  caught by review of the session transcript.
- Evidence type: manual
- Status: :argued
- Source: `lazarus.md` §What you do NOT do.
- Notes: Promotion to `:tested` requires a transcript-level
  audit harness, which is out of scope for v0.1.

---

## v0.1.2 (2026-05-10) — anti-spoof liveness probe

The watch loop now defends against static-photo presentation
attacks: a real face has ~0.015 byte-diff between two captures
~1s apart (subtle skin micro-motion); a printed photo or
iPad/phone-screen has ~0.0. One new spec entry.

### LZ-013 — anti-spoof-liveness-probe
- Key: byte-diff between two captures ~1s apart catches static-photo attacks
- Logic tier: Operational
- Description: On a positive face match in `check_once`, the
  watch loop runs a liveness probe before accepting the match.
  The probe takes a second full-resolution capture
  `LIVENESS_GAP_SECONDS` (1.0s) after the first, downsizes
  both to a 64×48 BMP via `sips`, and counts byte-level
  differences. The "live" decision is
  `delta >= LIVENESS_DELTA_MIN` (0.008).
  - Real face sitting still: ~0.015 delta (subtle skin
    micro-motion: head sway, blinks, breath). Above
    threshold → live.
  - Printed photo / iPad-screen attack: ~0.0 delta. Below
    threshold → `static_likely`, treated as a mismatch with
    `lockout_reason="liveness_fail"`.
  Infrastructure errors (camera retry failure, sips failure,
  size mismatch) fail open so a flaky camera doesn't lock the
  owner out. To preserve the liveness threshold against JPEG
  re-encode artifacts, both frames must be sourced as fresh
  full-resolution captures and downsized symmetrically; the
  watch loop holds `tmp_full` alive across the match branch
  in a `try/finally` block.
- Evidence type: example-tested
- Status: :tested
- Source: `face_sentinel.py` `_liveness_delta()`,
  `liveness_check()`, and `check_once()` is_match branch.
  Constants `LIVENESS_DELTA_MIN` (0.008) and
  `LIVENESS_GAP_SECONDS` (1.0) at module top.
- Test/Proof: `test/test_liveness_check.py` exercises the pure
  byte-diff math, the threshold constant, and the inequality
  semantics (`>=` boundary). The IO-bound `liveness_check`
  wrapper (subprocess to `sips`, `time.sleep`, fail-open
  branches) is covered by manual runs against real cameras
  and presentation-attack fixtures, recorded in
  `docs/lazarus_liveness_v0_1_2_companion.md`.
- Notes: Catches printed photos and iPad/phone-screen attacks.
  Misses video playback, 3D-printed mask, deepfake stream —
  those are v2 territory (active illumination flash / blink
  challenge / depth sensor). Promotion path to a stronger
  evidence tier would be a fixture set of attack-vector
  captures (printed photo, screen, video loop) with measured
  deltas; held at `:tested` for now.

---

## v0.1.3 (2026-05-10) — leave-one-out pool quality scoring

The v0.1.0 `--prune` was effectively a no-op: it scored each
ref by matching against the full pool (including itself), so
every score was 0 (self-match) and no outlier ever got
flagged. v0.1.3 fixes the algorithm to leave-one-out
nearest-neighbor: each ref is scored against a temporary pool
that excludes the ref itself. One new spec entry.

### LZ-014 — reference-pool-leave-one-out-pruning
- Key: --prune scores each ref's nearest non-self neighbor distance
- Logic tier: Operational
- Description: `face_sentinel.py --prune` scores every
  reference by computing its leave-one-out nearest-neighbor
  distance — its similarity to the closest *other* reference
  in the pool. The implementation builds a temporary
  directory containing every ref's `(.json, .fpdata, .jpg)`
  triple as a symlink EXCEPT the target ref, runs
  `face_compare match <target.jpg> <tempdir>`, and records
  the resulting best-distance. After scoring all refs, the
  tool reports the pool's average leave-one-out distance and
  flags outliers — refs whose nearest non-self neighbor is
  more than `PRUNE_OUTLIER_MULTIPLIER` (default 2.0) times
  the average. Outliers are likely off-distribution captures
  (different person, occluded face, bad lighting) that hurt
  match quality. The tool reports only — it does not
  auto-delete; the human decides what to retire because the
  algorithm cannot distinguish a genuine off-distribution
  ref from a legitimate rare-condition ref that improves
  coverage.
- Evidence type: example-tested
- Status: :tested
- Source: `face_sentinel.py` `_outliers_from_scores()`,
  `_prune_score_one()`, `prune_cmd()`, and the
  `PRUNE_OUTLIER_MULTIPLIER` (2.0) constant.
- Test/Proof: `test/test_prune_logic.py` exercises the pure
  outlier-detection helper across empty, no-outlier,
  single-outlier, multiple-outlier, boundary (strict `>`),
  custom-multiplier, and single-element pool cases (10
  assertions). The IO-bound `_prune_score_one` (subprocess
  to `face_compare`, tempdir + symlink construction) is
  covered by manual runs against the real pool, recorded in
  `docs/lazarus_prune_v0_1_3_companion.md`.
- Notes: The previous (v0.1.0) implementation matched each
  ref against the full pool *including itself*, so the best
  distance was always 0 (the ref matching itself), every
  ref's score was 0, and no outlier was ever flagged. The
  new implementation uses Python-only logic — no Swift
  binary changes — by constructing a leave-one-out symlink
  pool per ref. Symlinks are O(1) and never modify the
  originals. Cleanup is deferred to a `finally` block.

---

## v0.1.4 (2026-05-10) — Touch ID opportunistic pre-face gate

`face_sentinel.py --auth` now runs a Touch ID gate before the
face-match step. Two factors: fingerprint + face. Fail-open
semantics — Touch ID strengthens auth when available but never
blocks a legitimate owner on a machine without biometric
hardware (or with hardware that's misbehaving).

### LZ-015 — touchid-opportunistic-pre-face-gate
- Key: --auth runs Touch ID via `bioutil -r` before face capture
- Logic tier: Operational
- Description: Before the face-match step, `auth()` invokes
  `bioutil -r` via `_touchid_check()`. The macOS `bioutil`
  binary reads enrolled biometric records — an operation that
  requires biometric authentication, triggering the system
  Touch ID prompt. Three outcomes:
  - `bioutil` returns 0 → `"ok"` (Touch ID succeeded) →
    `auth_event "touchid_ok"` logged, face check proceeds.
  - `bioutil` returns non-zero → `"nonzero"` (prompt
    dismissed, no fingerprints enrolled, hardware error) →
    warning printed, `"touchid_nonzero"` logged, face check
    proceeds anyway (fail-open).
  - `bioutil` is missing (`FileNotFoundError`) or hangs past
    the 30s timeout (`TimeoutExpired`) → `"unavailable"` →
    warning printed, `"touchid_unavailable"` logged, face
    check proceeds.
- Evidence type: example-tested
- Status: :tested
- Source: `face_sentinel.py` `_touchid_check()` helper +
  `auth()` Step 1 block.
- Test/Proof: `test/test_touchid_check.py` exercises all
  three return paths (ok / nonzero / unavailable) using an
  injected `_runner` stub. Also covers: timeout-parameter
  plumbing, default-timeout value lock (30s), and the
  guarantee that unexpected exceptions (not `TimeoutExpired`
  / `FileNotFoundError`) propagate rather than being
  silently swallowed.
- Notes: Fail-open is the right default for a single-owner
  desktop tool — biometric hardware flakes shouldn't lock
  legitimate owners out. A stricter `--strict-touchid` flag
  that turns Touch ID into a hard gate is future work; it
  would warrant a separate spec entry (LZ-NNN) and a clear
  story for the headless / no-hardware scenarios. Honest
  framing: in fail-open mode, an attacker who can disable or
  occupy the Touch ID hardware bypasses this layer entirely
  — the defensive value comes from raising the bar in the
  common case (someone with the laptop but without the
  owner's fingerprint), not from a structural guarantee.

---

## v0.1.5 (2026-05-10) — :open entries promoted to :tested

No new LZ-NNN entries. The three `:open` entries from v0.1.0
(LZ-006 reference-storage-bounded, LZ-007
watch-loop-state-transitions, LZ-008 peek-json-output-shape)
are promoted to `:tested` via three new test files. Plus one
drive-by fix: `prune_oldest` now guards against the under-cap
negative-index case (previously it would have silently
deleted all-but-newest if ever called with N < MAX_REFERENCES;
production callers already guarded against this, but exposing
the function to direct test / CLI use made the latent bug
real). Plus one test affordance: `FACE_COMPARE_STUB` env var
short-circuits `run_face_compare` for shell-driven manual
testing.

The `:open` count drops to zero. Every spec entry now has at
least manual evidence (`:argued`) or runnable evidence
(`:tested`).

---

## v0.1.6 (2026-05-10) — LZ-005 grep-lint

No new LZ-NNN entry. LZ-005 (apple-vision-local-only) promotes
from `:argued` to `:tested` via a shell-script grep-lint that
runs on every CI push against `face_compare.swift` and
`face_sentinel.py`. The lint fails on networking-symbol
substrings (Swift: `URLSession`, `import Network`, etc.;
Python: `import socket`, `urllib`, `requests`, etc.). Plus a
size guard so the negative test doesn't silently pass on an
empty / stub-replaced source file.

---

## Counts (post-v0.1.6)

- Total: 15
- `:proved`: 0
- `:tested`: 9 (LZ-005, LZ-006, LZ-007, LZ-008, LZ-009, LZ-011,
  LZ-013, LZ-014, LZ-015)
- `:verified`: 0
- `:benchmarked`: 0
- `:argued`: 6 (LZ-001, LZ-002, LZ-003, LZ-004, LZ-010, LZ-012)
- `:open`: 0

Promotion queue (highest-leverage, ordered by ease):
1. **LZ-006 / LZ-007 / LZ-008** — all three are exercisable
   without real hardware by stubbing `run_face_compare`. One
   test session each; would lift `:open` count to 0.
2. **LZ-002** — fixture-driven (image, expected band) test set;
   needs a small set of reference + probe JPEGs.
3. **LZ-005** — CI lint that grep-fails on networking imports
   in the face-comparison sources. Cheap; high-value.
4. **LZ-010** — localhost loop-connect test. Fragile in CI;
   defer until a stable shape is found.
5. **LZ-001 / LZ-003 / LZ-012** — visual-skin / refusal /
   read-only-discipline are prompt-layer claims; tooling for
   transcript-level audit is the long-tail item.
