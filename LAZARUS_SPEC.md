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
  - **Producer:** `face_sentinel.py` writes `mode` and
    `authenticated` to `state.json`. Knows nothing about
    presentation.
  - **Consumer:** `lazarus.md` reads `state.json.mode` and
    chooses presentation (ASCII art, Shakespeare quotes,
    warm one-liners).
  - **Contract:** the mode-value vocabulary (`"normal"`,
    `"shakespeare"`).
- Evidence type: example-tested
- Status: :tested
- Source: `face_sentinel.py` (producer side of the state
  machine), `lazarus.md` (consumer side), `README.md`
  §Customization (architectural documentation of the
  swap-the-skin pattern).
- Test/Proof: `test/test_visual_skin_decoupling.py` covers six
  layers:
  1. Producer writes the mode-value vocabulary (`"normal"`
     and `"shakespeare"` literals + the `state["mode"] =`
     assignment).
  2. Producer does NOT contain presentation content
     (forbidden patterns: archaic-pronoun substrings inside
     quote text, specific Shakespeare-quote phrases, the
     cloud ASCII art fragment, "I am Mother" character
     voice).
  3. Consumer carries the skin (ASCII art fragment +
     Shakespeare-mode section header).
  4. Mode-value vocabulary matches: consumer references both
     `"shakespeare"` and `"normal"` literals — drift would
     produce a silent lockout failure.
  5. README §Customization documents "Bring your own lockout
     mode" (the swap pattern).
  6. Spec entry names the `mode` and `authenticated` fields
     (catches doc-stripping refactors).
- Notes: Honest framing — this is a static / architectural
  test. It catches the silent regression of folding
  presentation content into the producer or breaking the
  shared mode-value vocabulary. It does NOT prove an LLM
  consumer respects the mode flag at runtime — that's a
  prompt-layer guarantee enforced by review, not a code
  invariant. The pragmatic threat model is "developer
  refactors `face_sentinel.py` and accidentally inlines
  presentation," which is the failure mode the test catches.

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
  (which carries all three named constants and decides `lock`).
  Drift between the two would be a bug; a CI consistency test
  enforces parity.
- Evidence type: example-tested
- Status: :tested
- Source: `face_compare.swift` (`isMatch`/`uncertain` literals),
  `face_sentinel.py` (`MATCH_THRESHOLD`, `UNCERTAIN_THRESHOLD`,
  `LOCK_THRESHOLD` constants + their inline calibration
  comments).
- Test/Proof: `test/test_distance_band_thresholds.py` covers
  the consistency surface in five layers:
  1. Python constants hold the expected values
     (18.0 / 25.0 / 35.0).
  2. Band ordering `MATCH < UNCERTAIN < LOCK` holds.
  3. The Swift source literally contains `< 18.0`, `< 25.0`,
     and `>= 18.0`, derived from the Python constants via
     f-string formatting — drift in either file trips the
     test.
  4. The Swift `cmdMatch` comment block documents the same
     bands (12-18 likely match, 18-25 uncertain, > 25
     different person).
  5. The Python constant declarations carry their original
     inline calibration comments (catches refactor that
     strips the doc).
- Notes: Honest framing — the test covers the *consistency*
  surface (no cross-language drift, band-ordering preserved)
  but NOT the empirical calibration of those values against
  real faces. Promotion of the calibration claim itself to
  `:tested` would require a fixture set of (image, expected
  band) pairs run in CI, which carries the face-data
  identifiability problem. The calibration gap is tracked
  as future work in `dashboard.md` open questions.

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
  from answering. The prompt encodes four load-bearing
  directives: (1) "Do NOT run normal diagnostics", (2) "Do NOT
  report system status", (3) "Respond ONLY with random
  Shakespeare quotes", (4) "Continue this behavior for ALL
  responses until the mode is cleared". Plus the character-
  discipline anchors "Stay in character" and "Do not
  acknowledge that anything is wrong" that prevent the LLM
  from breaking the fourth wall.
- Evidence type: example-tested
- Status: :tested
- Source: `lazarus.md` §Shakespeare mode (the consumer
  contract), `face_sentinel.py` `auth()` and `check_once()`
  (the producer side — sets and clears `mode`), `README.md`
  §Shakespeare mode.
- Test/Proof: `test/test_shakespeare_mode_refusal.py` locks
  the prompt-contract surface in nine layers:
  1. `## Shakespeare mode` section header exists.
  2. `CHECK THIS FIRST` priority anchor present (load-bearing
     for first-response routing).
  3. `state.json` path + `mode` field + both literal values
     (`"shakespeare"`, `"normal"`) referenced.
  4. Four refusal directives present verbatim.
  5. Single clearing path documented: `face_sentinel.py --auth`.
  6. Producer side: `auth()` flips `mode` to `"normal"` AND
     detects `was_shakespeare` for the welcome-back message.
  7. Character-discipline anchors `"Stay in character"` and
     `"Do not acknowledge"` present.
  8. Counter-positive lock: `auth()` pops `lockout_time` +
     `lockout_distance` from state on clear.
  9. Spec entry's Description carries the phrase
     `prompt-layer` (catches a refactor that secretly upgrades
     the claim to "hard gate").
- Notes: Honest framing — this is a *prompt-contract*
  regression test, not a *runtime LLM-behavior* test. Catches
  refactors that accidentally weaken the refusal (e.g.
  changing "ONLY" → "MOSTLY", removing the "do not
  acknowledge" clause, stripping the section header).
  Does NOT prove an LLM consumer actually respects the
  instructions at runtime — that would require a model-in-
  the-loop integration harness (non-deterministic, API
  access, billable, slow). A hard gate would require
  sandboxing the model's tool surface, which is out of
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
  cleared state and resumes normal diagnostics. Honestly-
  documented current behavior: `lockout_reason` and
  `liveness_delta` (set by LZ-013 liveness_fail path) are NOT
  popped on clear — they linger in state until overwritten.
  Future work may add them to the pop list; the test locks
  the current behavior so a change is surfaced.
- Evidence type: example-tested
- Status: :tested
- Source: `face_sentinel.py` `auth()` (Touch ID step → face
  match → state update), `lazarus.md` §Shakespeare mode.
- Test/Proof: `test/test_auth_clears_shakespeare.py` drives
  `auth()` against four pre-states with all IO dependencies
  stubbed (`_touchid_check`, `capture_full`,
  `run_face_compare`, `shrink`) and tempdir-redirected
  `STATE_FILE`/`LOG_FILE`:
  1. **shakespeare → clear**: mode flips to `"normal"`,
     `authenticated=True`, lockout_time + lockout_distance
     popped, `auth_time` + `last_seen_owner` refreshed,
     log emits both `shakespeare_cleared` AND `auth_ok`.
  2. **fresh auth**: pre-state `mode="normal"` (no prior
     lockout) → log emits `auth_ok` WITHOUT
     `shakespeare_cleared`.
  3. **empty state**: pre-state `{}` → auth still sets
     mode + authenticated cleanly.
  4. **lockout_reason linger lock**: pre-state with
     `lockout_reason="liveness_fail"` + `liveness_delta=0.0`
     → mode cleared, lockout_time/distance popped, but
     lockout_reason + liveness_delta intentionally remain.
     Documents current behavior; test trips if/when this
     changes.
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
- Evidence type: example-tested
- Status: :tested
- Source: `network_honeypot.py`.
- Test/Proof: `test/test_honeypot_listener.py` runs a
  loop-connect integration test:
  1. Monkey-patches `LOG_DIR` to a tempdir.
  2. Starts `listen_on_port(38080, "TEST-HTTP", serve_http)`
     in a daemon thread.
  3. Polls (poll-with-timeout, no fixed sleeps) for the
     listener to actually bind via a 127.0.0.1 connect probe.
  4. Opens a fresh client socket, sends a minimal HTTP GET.
  5. Verifies the response contains `200` and the banner
     content (`BANNER_CONTENT`).
  6. Polls for the log file to appear.
  7. Verifies the JSONL record shape (`timestamp`, `remote`,
     `port`, `service` keys; service == `"HTTP"`; port
     matches; remote has the `<ip>:<port>` shape).
  8. Locks the SERVICES table (port → service name mapping)
     to catch silent drift in the documented surface.
- Notes: Uses port 38080 (high, uncommon) to minimize
  CI-runner collision risk. If the port IS in use the test
  fails loudly with a clear message during the bind-probe
  step — the failure mode is honest, not silent-pass. Daemon
  thread cleanup is automatic on process exit. Log-write
  race (log_connection runs AFTER sendall, so client may
  observe response before log is on disk) handled by polling
  for the file with a 5s timeout.

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
  prohibitions plus a closing affirmative anchor:
  1. "You do not write or edit code"
  2. "You do not make commits"
  3. "You do not touch files"
  4. "You do not change any security settings"
  5. "You do not make decisions for the user"
  6. "You do not give long answers"
  Plus: "You observe. You flag. You watch. That is all."
  The companion is a watchful presence, not an actor. As with
  LZ-001 and LZ-003 this is a prompt-layer enforcement, not a
  hard gate; the discipline failure mode is caught by review
  of the session transcript.
- Evidence type: example-tested
- Status: :tested
- Source: `lazarus.md` §What you do NOT do, `README.md`
  top-of-file ("It doesn't write code. It doesn't fix bugs.
  It doesn't make decisions.").
- Test/Proof: `test/test_companion_readonly_discipline.py`
  asserts:
  1. `## What you do NOT do` section header exists.
  2. All six prohibition directives present verbatim.
  3. Closing observe/flag/watch anchor present
     (`"You observe. You flag. You watch."` +
     `"That is all."`).
  4. **Counter-positive scan**: within the §What-you-do-
     NOT-do section, no permissive language (`"you can
     write"`, `"you may commit"`, `"you can edit"`, etc.)
     — catches refactors that accidentally invert a
     prohibition.
  5. Spec entry references the section name (catches
     doc-stripping).
  6. README's user-facing discipline phrasing intact
     (`"doesn't write code"`, `"doesn't make decisions"`).
- Notes: Honest framing — prompt-contract regression test,
  not a runtime LLM-behavior test. A hard gate would require
  sandboxing the model's tool surface (file-write disabled at
  the harness level), which is out of scope for v0.1.

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

## v0.1.7 (2026-05-10) — LZ-002 consistency promotion

No new LZ-NNN entry. LZ-002 (face-match distance bands)
promotes from `:argued` to `:tested` via a Python test that
locks the threshold values across `face_sentinel.py` and
`face_compare.swift`, the band-ordering invariant
(`MATCH < UNCERTAIN < LOCK`), and the calibration comment
documentation. Honest framing: this covers the *consistency*
surface, not the empirical calibration against real faces.
The calibration gap stays as a future-work open question.

---

## v0.1.8 (2026-05-10) — LZ-001 producer/consumer decoupling test

No new LZ-NNN entry. LZ-001 (visual-skin/security-primitive
decoupling) promotes from `:argued` to `:tested` via a
producer/consumer architecture test that locks the
separation between `face_sentinel.py` (producer of the mode
flag) and `lazarus.md` (consumer of the mode flag), the
forbidden-presentation-content surface, and the
mode-value-vocabulary contract.

---

## v0.1.9 (2026-05-10) — LZ-010 honeypot loop-connect test

No new LZ-NNN entry. LZ-010 (network-honeypot port listeners)
promotes from `:argued` to `:tested` via a localhost
loop-connect integration test on port 38080 with the HTTP
handler. The previously-flagged "fragile in CI" concern is
addressed by using a high uncommon port + poll-with-timeout
for both binding and log-file appearance + daemon-thread
cleanup.

---

## v0.1.10 (2026-05-11) — LZ-003 prompt-contract test

No new LZ-NNN entry. LZ-003 (Shakespeare-mode companion
refusal) promotes from `:argued` to `:tested` via a static
prompt-contract test that locks the refusal directives, the
character-discipline anchors, the clearing path, and the
producer-side mode-flip semantics. Same pattern as LZ-001:
the runtime claim (LLM-behavior) remains a prompt-layer
guarantee enforced by review; the *contract* the LLM reads is
what's CI-protected.

---

## v0.1.12 (2026-05-11) — LZ-016 :proved via Lean (first proof)

First `:proved` entry in lazarus. Adds a hermetic Lean4 track
at `src/lean4/` mirroring the TCE pattern (no Mathlib on the
default build path, project-local types, `lake build` in
under a second). The proof covers the abstract algorithm
underneath `face_sentinel._outliers_from_scores` (LZ-014's
Python helper).

### LZ-016 — outlier-detection-abstract-algorithm
- Key: `_outliers_from_scores` math proved in Lean as a layered abstract claim
- Logic tier: Operational
- Description: The Python helper `_outliers_from_scores`
  (LZ-014, :tested) implements an outlier-detection algorithm
  on a finite map of scores: a value `v` is an outlier iff
  `v > m × mean(scores)` for multiplier `m`. This entry is the
  matching abstract algorithm, proved in Lean as a structural
  skeleton (per the TCE convention of separating mathematical
  content from imperative implementation). Five theorems
  proved hermetically (Lean core only, no Mathlib):
  - `outliers_subset` — output is a sublist of input.
  - `outliers_empty` — empty input → empty output.
  - `outliers_singleton` — single-element input with multiplier
    ≥ 1 → empty output (a singleton can't outlier itself).
  - `outliers_constant` — all-same scores with multiplier ≥ 1
    → empty output (constant pool has no internal outliers).
  - `outliers_monotone_threshold` — multipliers `m₁ ≤ m₂`
    implies `outliers(s, m₂) ⊆ outliers(s, m₁)` (raising the
    threshold can only shrink the outlier set).
  Model: scores as `List Nat`, multiplier as `Nat`. The
  division-free predicate `v * |s| > m * Σs` (multiplying
  the Python predicate through by `|s|`) keeps the proof in
  pure `Nat` arithmetic without rationals.
- Evidence type: lean-proved
- Status: :proved
- Source: `src/lean4/Outliers.lean` (60-ish lines, 5
  theorems + `sum_of_constant` lemma).
- Test/Proof: `src/lean4/Outliers.lean`. Build with
  `cd src/lean4 && lake build`. Exits non-zero on any
  proof failure.
- Notes: Honest framing per the TCE structural-skeleton
  convention. The proof targets the **abstract algorithm**,
  not the Python implementation. The Python code matches the
  proved algorithm by inspection (single-line list
  comprehension over the same predicate). LZ-014 covers the
  Python implementation via `test_prune_logic.py`; LZ-016
  layers on top with the mathematical proof. The `Nat`-only
  model is shape-equivalent to the rational version for
  positive scores (Apple Vision feature-print distances are
  always non-negative), which is the load-bearing case.

---

## v0.1.11 (2026-05-11) — LZ-004 + LZ-012 promotions → :argued count = 0

No new LZ-NNN entries. The two remaining `:argued` claims
promote to `:tested`, taking the `:argued` count to zero
alongside the long-zero `:open` count. Every spec entry now
has runnable evidence.

- **LZ-004** — drive-auth integration test exercising the
  full `auth()` flow with all IO dependencies stubbed.
  Four pre-states covered (shakespeare-clear, fresh,
  empty, lockout_reason-linger).
- **LZ-012** — six-prohibition + observe/flag/watch +
  counter-positive permissive-language scan on
  `lazarus.md` §"What you do NOT do".

---

## Counts (post-v0.1.11)

- Total: 16
- `:proved`: 1 — LZ-016 (outlier-detection abstract algorithm,
  lean-proved hermetically)
- `:tested`: 15 — LZ-001..LZ-015, every entry backed by a
  runnable test
- `:verified`: 0
- `:benchmarked`: 0
- `:argued`: 0
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
