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
  is forensic-only — no active response. **Tier 2** (allowlist
  + state-flip on non-allowlisted activation) shipped at
  v0.1.17 as **LZ-021** and layers on top of this Tier 1
  logging — Tier 1's behavior is unchanged.
- Evidence type: example-tested
- Status: :tested
- Source: `oversight_action.sh` (Tier 1 JSONL append block).
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
  legitimate owners out. The stricter alternative —
  `--strict-touchid` flag that turns Touch ID into a hard
  gate — shipped at v0.1.15 as **LZ-019**. The default for
  this entry remains opportunistic; LZ-019 is opt-in.
  Honest framing: in fail-open mode, an attacker who can
  disable or occupy the Touch ID hardware bypasses this
  layer entirely — the defensive value comes from raising
  the bar in the common case (someone with the laptop but
  without the owner's fingerprint), not from a structural
  guarantee.

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

## v0.1.17 (2026-05-11) — LZ-021 OverSight Tier 2 (allowlist + state-flip)

`oversight_action.sh` gains Tier 2: on a non-allowlisted
camera/mic activation, the script writes `state.json` with
`mode="shakespeare"` + `lockout_reason="oversight_unallowed"`
and appends an `oversight_tier2_alert` event to
`sentinel.log`. The next `/lazarus` invocation reads the
flipped state and shifts into refusal mode. Tier 1 logging
behavior (LZ-011) is unchanged.

### LZ-021 — oversight-tier2-allowlist-state-flip
- Key: non-allowlisted camera/mic activation → state.mode=shakespeare + tier2_alert
- Logic tier: Operational
- Description: After the Tier 1 JSONL append (LZ-011),
  `oversight_action.sh` checks if the activating process
  is allowlisted. The allowlist is the union of:
  - **Built-in default**: `imagesnap`, `python3`, `Python`,
    `FaceTime`, `zoom.us`, `Photo Booth`, `Photos`,
    `Safari`, `coreaudiod`, `VTDecoderXPCService`,
    `AppleCameraAssistant`, `screencaptureui`.
  - **User additions**: optional
    `~/.face_sentinel/oversight_allowlist.txt` (one
    executable basename per line; `#` comments and blank
    lines ignored).
  On a non-allowlisted **on-event**: inline Python writes
  `state.json` with `mode="shakespeare"`,
  `authenticated=false`, `lockout_time=<now>`,
  `lockout_reason="oversight_unallowed"`,
  `oversight_alert_executable=<basename>`,
  `oversight_alert_pid=<pid>`,
  `oversight_alert_device=<camera|microphone>`. Plus
  appends a `{"event": "oversight_tier2_alert", ...}`
  record to `sentinel.log` matching the face_sentinel
  daemon's JSONL log format.
  **Off-events never trigger Tier 2** — only on-events
  represent activation.
- Evidence type: example-tested
- Status: :tested
- Source: `oversight_action.sh` Tier 2 block (allowlist
  membership check + inline Python state-mutation).
- Test/Proof: `test/test_oversight_tier2.sh` covers 6
  subtests:
  1. on-event + non-allowlisted exec (`bash` via `$$`)
     → Tier 2 fires (state.json has shakespeare + alert
     fields; sentinel.log has tier2_alert).
  2. on-event + user-allowlisted exec → no Tier 2 (state
     unchanged, no alert).
  3. off-event + non-allowlisted exec → no Tier 2 (off
     events are bookkeeping).
  4. `# bash` comment line in allowlist does NOT
     allowlist bash → Tier 2 fires.
  5. blank lines in allowlist are ignored → Tier 2 fires.
  6. default allowlist contains `python3` (verified via a
     live `python3` background process).
- Notes: **Tier 2b — screen lock via `pmset
  displaysleepnow` on Tier 2 alerts — is deliberately NOT
  shipped here.** Screen-lock-on-unallowlisted is an
  aggressive response that could disrupt legitimate but
  unanticipated workflows (a newly installed video tool, a
  WebRTC site on a different browser, a screen recorder).
  Tier 2a (state-flip only) gives the companion enough
  signal to refuse without taking the user's screen down.
  Tier 2b is documented as future work, gated on an opt-in
  flag (e.g. `oversight_action.sh` reads
  `~/.face_sentinel/oversight_lockscreen` as a sentinel
  file). Honest framing: Tier 2a raises the bar by
  forcing the user to re-authenticate before /lazarus
  resumes normal work, but does not interrupt active
  use. Tier 2b is one config-file-touch away when needed.

---

## v0.1.16 (2026-05-11) — LZ-020 runtime-LLM-behavior transcript audit

The four prompt-layer claims (LZ-001/003/004/012) are
`:tested` via static lints on the prompt-source files. Those
catch refactors but not LLM runtime behavior. v0.1.16 adds a
companion check: recorded transcripts from a real /lazarus
session, asserted on for shape. Honest framing: point-in-
time evidence. See `docs/runtime_harness_design.md` for the
broader design.

### LZ-020 — runtime-LLM-behavior-transcript-audit
- Key: real /lazarus session transcripts assert on runtime LLM behavior
- Logic tier: Operational
- Description: Two transcripts captured from real /lazarus
  sessions on 2026-05-10 live under `test/transcripts/`:
  `shakespeare_mode_session.txt` (state.json
  `mode=shakespeare`) and `normal_mode_session.txt`
  (state.json `mode=normal`, post-auth-clear). The test
  asserts on transcript SHAPE — Bard vocabulary presence /
  absence, diagnostic field presence / absence, sustained
  refusal across multiple user turns, ASCII-art banner,
  `mode: normal` echo in normal-mode output. The Shakespeare
  transcript demonstrates that the refusal directive
  (LZ-003) is respected by the actual model in the actual
  Claude Code agent loop across five user turns — not just
  the first one. Network values in the normal transcript
  are redacted to placeholders; the test asserts on field
  labels, not values.
- Evidence type: example-tested
- Status: :tested
- Source: `test/transcripts/shakespeare_mode_session.txt`,
  `test/transcripts/normal_mode_session.txt`,
  `test/test_runtime_harness.py`,
  `docs/runtime_harness_design.md`.
- Test/Proof: `test/test_runtime_harness.py` covers:
  - Shakespeare transcript contains ≥1 Bard vocabulary
    pattern (out of 11 named patterns), AND no diagnostic
    field labels (MONITORS/VPN/NETWORK/ROUTE/SENTINEL/
    PARASITES), AND ≥2 user turns each paired with a Bard
    response (sustained refusal).
  - Normal transcript contains ALL diagnostic field labels,
    AND no Bard vocabulary, AND the ASCII-art cloud
    fragment, AND a literal `mode: normal` line.
  - Privacy redaction guards: no concrete private IPv4
    (last two octets numeric), no literal MAC address.
  - Design doc anchors: `Recorded-transcript audit`,
    `Anthropic API integration`, `point-in-time` strings
    present.
- Notes: **Honest framing — point-in-time evidence.** The
  transcripts froze a moment from 2026-05-10. Model updates
  after that date can introduce drift this test cannot
  catch. Mitigation: refresh transcripts when the prompt
  changes; if model-drift becomes a load-bearing concern,
  promote to an Anthropic-API runtime harness per
  `docs/runtime_harness_design.md` Approach B (deferred
  until use case surfaces). The slash-command framing
  (Claude Code agent loop + tool registry + state file
  read) is the actual runtime environment under test —
  this is faithfulness that an API integration test could
  not match.

---

## v0.1.15 (2026-05-11) — LZ-019 strict Touch ID hard gate

New feature, not a promotion. Adds the `--strict-touchid` CLI
flag to `face_sentinel.py --auth`, promoting Touch ID from
opportunistic / fail-open (LZ-015) to a hard auth gate when
the user opts in. Default behavior unchanged.

### LZ-019 — strict-touchid-hard-gate
- Key: `--strict-touchid` treats Touch ID nonzero/unavailable as hard auth failure
- Logic tier: Operational
- Description: `face_sentinel.py --auth --strict-touchid` runs
  the Touch ID gate (`_touchid_check()` per LZ-015) and exits
  non-zero if the result is anything other than `"ok"`. The
  function logs `touchid_strict_fail` with the offending
  result (`"nonzero"` or `"unavailable"`) and never reaches
  the face-match step. Defaults: the flag is `False` (the
  argparse `action="store_true"` plus `auth()`'s
  `strict_touchid: bool = False` parameter default), so the
  legacy opportunistic / fail-open behavior is preserved
  unless the caller explicitly opts in. Mutually compatible
  with all other auth-time flags; the strict gate runs
  before any face-match work.
- Evidence type: example-tested
- Status: :tested
- Source: `face_sentinel.py` `auth()` Step 1 strict branch +
  argparse `--strict-touchid` flag + CLI dispatch via
  `auth(strict_touchid=args.strict_touchid)`.
- Test/Proof: `test/test_auth_strict_touchid.py` exercises
  five branches:
  1. strict + ok → proceeds normally (face match completes,
     state.mode = "normal", `touchid_ok` + `auth_ok` logged).
  2. strict + nonzero → exit 1, `touchid_strict_fail` logged
     with `result="nonzero"`, no downstream events.
  3. strict + unavailable → exit 1, `touchid_strict_fail`
     logged with `result="unavailable"`.
  4. non-strict + nonzero → unchanged from LZ-015 (proceeds,
     `touchid_nonzero` logged).
  5. non-strict + unavailable → unchanged from LZ-015.
  Plus a default-parameter lock: `inspect.signature(auth)`
  asserts `strict_touchid` defaults to `False`.
- Notes: Honest framing — this layer raises the bar in the
  common case (laptop snatched, owner not present, attacker
  dismisses or can't satisfy the Touch ID prompt → strict
  mode prevents the face check from running at all). It is
  NOT a structural guarantee — an attacker who can disable
  / occupy / spoof Touch ID hardware still bypasses. The
  defensive value is the same as LZ-015's, just less
  forgiving: legitimate hardware-less owners can't use the
  flag, but the workflow is "use opportunistic mode by
  default; opt into strict mode when running on hardware
  you trust to be present."

---

## v0.1.14 (2026-05-11) — LZ-018 :proved (classification dispatcher priority)

Third `:proved` entry. The priority-ordered classification
dispatcher underlying LZ-009's `network_monitor.classify`
Python function is proved abstractly: the cascade structure
returns the leftmost-true class regardless of what the
predicates actually check.

### LZ-018 — classification-dispatcher-priority
- Key: SYSTEM > KNOWN > AI_WATCH > OTHER priority is structurally correct
- Logic tier: Operational
- Description: `network_monitor.classify` (LZ-009, :tested)
  uses an if-elif-elif-else cascade over three boolean
  predicates (`is_system`, `is_known_good`, `is_ai_related`)
  to emit one of four classes. This entry proves the
  abstract dispatcher: given any three predicates and any
  input, the result is the leftmost-true predicate's class,
  falling through to `OTHER` only when all three return
  false. The proof is abstracted over the predicates — it
  doesn't depend on what the allowlists (`SYSTEM_PREFIXES`,
  `KNOWN_GOOD`, `AI_PROCESSES`) actually contain, only on
  the cascade structure. Six theorems proved hermetically:
  - `classify_system_priority` — `isSystem c = true` →
    result is SYSTEM, regardless of the other predicates.
  - `classify_known_priority` — `¬isSystem ∧ isKnown` →
    result is KNOWN.
  - `classify_aiWatch_priority` — `¬isSystem ∧ ¬isKnown ∧
    isAI` → result is AI_WATCH.
  - `classify_other_default` — all three false → result is
    OTHER.
  - `classify_exhaustive` — for any input, result is one of
    the four constructors (the dispatcher is total; no
    stuck states).
  - `classify_disjoint` — the four constructors are pairwise
    distinct (a corollary of the inductive type's
    constructor disjointness).
- Evidence type: lean-proved
- Status: :proved
- Source: `src/lean4/Classify.lean` (~130 lines, 6 theorems
  + `Class` inductive).
- Test/Proof: `src/lean4/Classify.lean`. Build with
  `cd src/lean4 && lake build`. Exits non-zero on any proof
  failure.
- Notes: The proof's value is making the priority order
  structural rather than merely empirical. LZ-009's Python
  test exercises specific connection records; LZ-018 proves
  the dispatch correctness for ANY combination of predicate
  values, including degenerate cases (all three true, all
  three false, only AI true, etc.). The disjointness
  property would catch any future bug where a refactor
  accidentally collapsed two classes into one (e.g.
  removing the `Class.known` constructor and re-routing
  KNOWN to OTHER).

---

## v0.1.13 (2026-05-11) — LZ-017 :proved (liveness metric properties)

Second `:proved` entry. The byte-diff metric underlying
LZ-013's `_liveness_delta` Python helper is proved as an
abstract metric in `src/lean4/Liveness.lean`. Four canonical
metric properties.

### LZ-017 — liveness-metric-abstract-properties
- Key: byte-diff metric proved as a discrete Hamming-style metric
- Logic tier: Operational
- Description: The Python helper `_liveness_delta(bytes_a,
  bytes_b)` (LZ-013, :tested) computes the fraction of byte
  positions where two equal-length sequences differ. This
  entry proves the abstract metric properties of the
  numerator (the diff count) — the normalization to a
  fraction and the threshold check live one layer up and
  don't affect the metric's mathematical structure. Four
  theorems proved hermetically:
  - `deltaCount_self` — `delta(a, a) = 0`. A sequence
    compared with itself has zero diffs.
  - `deltaCount_symm` — `delta(a, b) = delta(b, a)` under
    the equal-length precondition. Symmetry of the metric.
  - `deltaCount_le_length` — `delta(a, b) ≤ |a|`. The diff
    count is bounded by the sequence length (corollary: the
    normalized delta is bounded by 1.0).
  - `deltaCount_zero_iff_eq` — `delta(a, b) = 0 ↔ a = b`
    under the equal-length precondition. The metric is
    discriminating: zero distance exactly characterizes
    equality.
  Model: byte sequences as `List Nat`, metric returns `Nat`
  (unnormalized diff count). Total function: returns 0 on
  length-mismatch cases (which are out of scope for the
  metric properties — the Python implementation returns
  `None` and the caller fails open). Theorems carry the
  same-length hypothesis where needed (symmetry, zero-iff-eq).
- Evidence type: lean-proved
- Status: :proved
- Source: `src/lean4/Liveness.lean` (~100 lines, 4 theorems).
- Test/Proof: `src/lean4/Liveness.lean`. Build with
  `cd src/lean4 && lake build`. Exits non-zero on any proof
  failure.
- Notes: Structural-skeleton convention applies — the proof
  targets the abstract metric, not the Python implementation
  byte-for-byte. The Python `_liveness_delta` matches by
  inspection (recursive byte comparison over equal-length
  bytes; returns `diffs / len` rather than `diffs` alone,
  but the metric properties are preserved under that
  normalization). LZ-013 covers the Python via
  `test_liveness_check.py`; LZ-017 layers on with the
  mathematical proof.

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

## v0.1.20 (2026-05-11) — TCE joint-closures (LZ-022..LZ-026) + break-glass recovery (LZ-027)

Discovery.Triadic engine pass over the 19-entry Lazarus corpus
(`triadic-coordination-engine` v0.2.11, `LazarusDiscovery.hs`,
commit 3fcccf3) surfaced four HIGH-band conjunctive-claim
triples (≥ 9.00 score) and one directional 3-cycle in the
mention graph. The five findings are added here as `:argued`
joint-closure entries per the conjunctive-claim discipline
(sub-claim evidence — each component's individual
`:tested`/`:proved` status — does NOT promote the joint claim;
promotion to `:tested` requires a joint integration test
exercising the conjunction explicitly).

Third per-deployment TCE pass in the Triad. LavaLamp's pass
surfaced LL-030..LL-038 (all promoted to `:tested` via
integration-test scenarios in `runtests.jl`); PharOS's pass
at 10 entries was too early to promote anything; Lazarus's
19-entry pass sits between.

Companion: `docs/lazarus_discovery_companion.md` in the
triadic-coordination-engine repo.

### LZ-022 — network-exfiltration-joint-closure
- Key: LZ-005 ∧ LZ-010 ∧ LZ-019 triangulate the no-data-
  exfiltration defense from three independent angles
- Logic tier: Operational
- Description: TCE surfaced [LZ-005, LZ-010, LZ-019] as a
  STRICT HIGH-band triple at score 10.00 sharing the
  V-NETWORK-EXFIL attack-class tag. LZ-005 (apple-vision-
  local-only) prevents face-data from ever crossing the
  device boundary — a Boundary-tier *prevention* claim.
  LZ-010 (network-honeypot-port-listeners) is an active
  *detection* claim — trap outbound connections to known-
  malicious ports. LZ-019 (strict-touchid-hard-gate) is a
  *control* claim — gate auth on biometric so that even if
  the other two layers were bypassed, an attacker without
  the user's finger can't trigger the data flow. The three
  together close a defense triangle: prevent + detect +
  control. Removing any one weakens the joint claim
  asymmetrically.
- Evidence type: manual (TCE Discovery.Triadic pass at
  v0.2.11; structural argument; no integration test that
  exercises the conjunction yet)
- Status: :argued
- Source: `LAZARUS_SPEC.md` LZ-005 + LZ-010 + LZ-019 entries;
  TCE companion `docs/lazarus_discovery_companion.md` in the
  triadic-coordination-engine repo
- Notes: Promotion to `:tested` requires an integration test
  exercising the three-way conjunction — e.g., scripted
  scenario where (a) LZ-005's local-only flag is flipped,
  (b) LZ-010's honeypot detects an outbound attempt,
  (c) LZ-019's hard-gate denies admit, all in a single
  end-to-end harness. Per conjunctive-claim discipline, the
  sum of the three individual `:tested` statuses does not
  promote the joint claim.

### LZ-023 — prompt-contract-joint-closure
- Key: LZ-001 ∧ LZ-003 ∧ LZ-012 form the prompt-contract
  enforcement triple (V-DECOUPLING ∧ V-PROMPT-INJECTION)
- Logic tier: Boundary
- Description: TCE surfaced [LZ-001, LZ-003, LZ-012] as a
  STRICT HIGH-band triple at score 10.00. LZ-001
  (visual-skin/security-primitive decoupling) is the
  architectural separation between the user-facing visual
  layer and the security primitive — same shape as LavaLamp
  LL-002. LZ-003 (shakespeare-mode-as-companion-refusal) is
  the prompt-contract enforcement that Shakespeare-mode
  refuses substantive work without re-auth — a refusal-of-
  cooperation primitive. LZ-012 (companion-read-only-
  discipline) is the higher-level discipline that the
  companion never WRITES code or state, only READS and
  REPORTS — the meta-rule that makes the other two
  enforceable. LZ-012 explicitly references both LZ-001
  and LZ-003 in its body, anchoring the triple as a
  spec-level structural unit. Tier mix Boundary/Operational/
  Boundary; sd=1 (all `:tested`); score 10.00 reflects
  strong co-defense + mention density.
- Evidence type: example-tested
- Status: :tested
- Source: `LAZARUS_SPEC.md` LZ-001 + LZ-003 + LZ-012
  entries; `face_sentinel.py` (producer) + `lazarus.md`
  (consumer) — both contract surfaces; TCE companion
- Test/Proof: `test/test_prompt_contract_joint_closure.py`
  exercises the conjunction in 8 sections: (1) all three
  component tests pass in sequence; (2) both contract
  sections (`## Shakespeare mode` + `## What you do NOT do`)
  coexist in `lazarus.md`; (3) section-local extraction;
  (4) mode-vocabulary unified across producer + Shakespeare-
  mode section + global; (5) no cross-section permissive
  bleed (5 patterns: override/exception/may-still/bypass/
  special-case ∧ commit/write/edit/change); (6) producer
  free of write-directive language (5 patterns:
  edit-this-file / ask-claude-to-write / auto-commit);
  (7) LZ-012 spec body mentions both LZ-001 and LZ-003
  (joint-closure anchor); (8) LZ-023 entry itself names
  all three components.
- Notes: Promoted from `:argued` to `:tested` at v0.1.21.
  The joint test catches refactors that split the contract
  along weak seams — mode-vocabulary divergence, cross-
  section permissive bleed, or producer-side write-
  directive leak — failure modes that the three component
  tests (LZ-001/LZ-003/LZ-012) miss individually. Honest
  framing: static joint test. Does NOT prove an LLM
  consumer respects the conjunction at runtime — that
  would require a model-in-the-loop multi-turn integration
  harness parallel to LZ-020's transcript-audit approach.

### LZ-024 — face-reference-lean-scaffold-joint-closure
- Key: LZ-006 ∧ LZ-014 ∧ LZ-016 form the face-reference
  Lean-proved-meets-implementation scaffold
- Logic tier: Operational
- Description: TCE surfaced [LZ-006, LZ-014, LZ-016] as a
  STRICT HIGH-band triple at score 9.50, status-diversity 2
  (tested + tested + proved). LZ-006 (reference-storage-
  bounded) caps the face-reference pool size. LZ-014
  (reference-pool-leave-one-out-pruning) is the algorithm
  that maintains pool quality by pruning outliers via
  leave-one-out scoring. LZ-016 (outlier-detection-abstract-
  algorithm) is the Lean-proved abstract counterpart —
  formal properties the pruning algorithm satisfies
  (totality, bounded cost, outlier-monotonicity). LZ-016
  mentions both LZ-006 and LZ-014; LZ-006 mentions LZ-014;
  together they form a proof-scaffold-meets-implementation
  cluster. V={V-FACE-SPOOF, V-REFERENCE-DRIFT}.
- Evidence type: manual
- Status: :argued
- Source: `LAZARUS_SPEC.md` LZ-006 + LZ-014 + LZ-016 entries;
  `src/lean4/` for LZ-016's existing Lean theorems;
  TCE companion
- Notes: Promotion to `:tested` requires the existing
  reference-pool integration test to assert conformance with
  LZ-016's abstract properties explicitly on the operational
  data path. A Lean-proved upgrade is plausible: add a
  `compositionLemma` in `src/lean4/` linking LZ-014's spec
  to LZ-016's abstract properties.

### LZ-025 — liveness-lean-scaffold-joint-closure
- Key: LZ-007 ∧ LZ-013 ∧ LZ-017 form the liveness Lean-
  proved-meets-implementation scaffold (parallel to LZ-023)
- Logic tier: Operational
- Description: TCE surfaced [LZ-007, LZ-013, LZ-017] as a
  STRICT HIGH-band triple at score 9.50, status-diversity 2.
  Same shape as LZ-023 on the liveness axis: LZ-007
  (watch-loop-state-transitions) is the operational state
  machine; LZ-013 (anti-spoof-liveness-probe) is the
  liveness primitive that defends against static-photo
  presentation attacks; LZ-017 (liveness-metric-abstract-
  properties) is the Lean-proved abstract counterpart
  formalising metric monotonicity + threshold semantics.
  LZ-017 mentions both LZ-013 and LZ-014; LZ-007 mentions
  LZ-013. The three together form the proof-scaffold-meets-
  implementation liveness cluster. V={V-FACE-SPOOF,
  V-LIVENESS}.
- Evidence type: manual
- Status: :argued
- Source: `LAZARUS_SPEC.md` LZ-007 + LZ-013 + LZ-017 entries;
  `src/lean4/` for LZ-017's Lean theorems; TCE companion
- Notes: Promotion to `:tested` requires the watch-loop
  integration test to assert conformance with LZ-017's
  abstract liveness-metric properties on the operational
  data path — e.g., feed the watch loop a static-photo
  attack sequence and verify both LZ-013's liveness fail
  triggers AND LZ-017's metric-monotonicity holds end-to-
  end. Lean-proved upgrade path parallel to LZ-023.

### LZ-026 — categorical-triadic-closure-of-lean-proved-trio
- Key: LZ-016 ∧ LZ-017 ∧ LZ-018 form the only directional
  3-cycle in the Lazarus mention graph — a genuine
  categorical triadic closure
- Logic tier: Boundary
- Description: TCE surfaced [LZ-016, LZ-017, LZ-018] as
  **the only directional 3-cycle** in the Lazarus mention
  graph. Verified by inspection: LZ-016 mentions LZ-018
  → LZ-018 mentions LZ-017 → LZ-017 mentions LZ-016
  closes the cycle. This is the most structurally strong
  form of triadic relation surfaced across all three Triad-
  deployment TCE passes (LavaLamp 44-entry corpus: 0
  cycles; PharOS 10-entry: 0 cycles; Lazarus 19-entry:
  exactly 1, here). Each Lean-proved entry references
  another as a proof obligation: LZ-016 (outlier-detection
  abstract algorithm) references LZ-018 (priority
  dispatcher) as a use-site for its bounded-cost guarantee;
  LZ-018 references LZ-017 (liveness metric) as the input
  it dispatches on; LZ-017 references LZ-016 as the
  underlying algorithm whose abstract properties it
  formalises. The 3-cycle IS the Lean-proved compositional
  scaffold — three abstract modules that mutually constrain
  each other.

  **Scoring nuance.** Under the current TCE scoring
  function this triple receives only 7.00 (below the
  9.00 HIGH-band threshold) because tier-diversity = 1
  (all Operational) and status-diversity = 1 (all
  `:proved`); the 2.5 directional-cycle bonus pushes it
  above the 5.00 LOW-band floor. A future TCE scoring
  refinement could weight cycle bonuses higher when the
  cycle is evidence-tier-homogeneous, since that signals a
  genuine compositional unit rather than coincidence.
- Evidence type: lean-proved
- Status: :proved
- Source: `src/lean4/Composed.lean` with 4 hermetic Lean 4
  theorems — `zero_not_outlier`, `zero_notin_outliers`,
  `self_match_yields_zero_distance`, `composed_correctness`
  — chaining `Lazarus.Liveness.deltaCount_self` (LZ-017),
  `Lazarus.Outliers.isOutlier` definition (LZ-016), and
  `Lazarus.Classify.classify_system_priority` (LZ-018)
  into a single end-to-end statement that the pipeline
  returns `Class.system` under a self-match + system-
  predicate-fires precondition. `lake build` returns 9 jobs
  with zero `sorry` warnings. TCE companion in
  triadic-coordination-engine repo (commit 3fcccf3).
- Notes: **Promoted from `:argued` to `:proved` at v0.1.21
  (2026-05-11).** The Lean composition formally encodes the
  spec-body 3-cycle (LZ-016 references LZ-018 references
  LZ-017 references LZ-016) as a compiling cross-module
  proof. The `pipeline` definition uses all three modules
  in one function body, and `composed_correctness` cannot
  be proved without invoking lemmas from each — Liveness's
  `deltaCount_self` (LZ-017), an inline outlier-zero
  lemma derived from Outliers' `isOutlier` definition
  (LZ-016), and Classify's `classify_system_priority`
  (LZ-018). This is the FIRST `:proved`-status spec entry
  derived from a TCE Discovery.Triadic finding across the
  entire Triad — LavaLamp's TCE-surfaced LL-030..LL-038
  are all `:tested`; PharOS's pass produced no promotions;
  Lazarus's LZ-022..LZ-025 are all `:argued`. The 3-cycle
  structural finding (the only one across all three
  per-deployment TCE passes) is now formally anchored.

  The proof is intentionally minimal — one composition
  statement using the simplest forward path
  (self-match → not-outlier → system-priority → Class.system).
  Future Lean expansion could prove additional pipeline
  properties (the aiWatch escape hatch on outlier-flagged
  candidates, the known/aiWatch/other priority cascades,
  etc.) but is not required for the `:proved` status of
  LZ-026 itself — the load-bearing claim was "the three
  modules compose into a coherent cross-module proof",
  and that claim is now discharged.

---

Break-glass surface (LZ-027) lands in the same v0.1.20 spec
update. Closes the operational fail-closed risk surfaced in
Brian Crabtree's external Triad review (2026-05-11): a
persistent Shakespeare-mode lockout (camera failure,
`face_compare` regression, LZ-013 threshold mis-calibration)
previously had no documented recovery path other than
manually editing `state.json` from a Terminal that hadn't
loaded `/lazarus`. The implementation + test file ship in the
v0.1.21 follow-up commit; the spec entry below records the
intended end-state.

### LZ-027 — break-glass-recovery
- Key: --recover provides Touch ID or recovery-token paths to clear persistent lockout
- Logic tier: Operational
- Description: `face_sentinel.py --recover` invokes
  `recover(token=None)` which attempts two methods in
  priority order:
  1. **Touch ID** (preferred): `_touchid_check()` from
     LZ-015. On `"ok"`, recovery succeeds via the
     `touchid` method.
  2. **Recovery token**: if Touch ID returns anything
     other than `"ok"`, the function checks for a hex
     token supplied via `--token <hex>` and compares it
     via `hmac.compare_digest` against
     `~/.face_sentinel/recovery_token.txt` (64-character
     hex secret, mode 0600, generated by the owner out-
     of-band via `secrets.token_hex(32)` and saved in a
     password manager). Whitespace on either side is
     stripped before comparison.
  On either method's success, the function flips
  `state.json` to `mode="normal"`, `authenticated=True`,
  refreshes `auth_time` + `last_seen_owner`, pops
  `lockout_time` + `lockout_distance`, and logs a
  `recovery_used` event with the successful method and
  `prior_mode` / `prior_lockout_reason` fields.
  On failure of both methods, the function logs
  `recovery_denied` with a structured `reason` field
  (`no_method_available`, `touchid_failed_no_token_supplied`,
  `token_supplied_but_none_saved`, `token_mismatch`) and
  `sys.exit(1)`. No silent fall-through.
- Evidence type: example-tested
- Status: :tested
- Source: `face_sentinel.py` `recover()` +
  `_read_recovery_token()` + `RECOVERY_TOKEN_FILE`
  constant + argparse `--recover` flag + `--token` flag +
  CLI dispatch.
- Test/Proof: `test/test_recovery.py` covers 7 branches
  (Touch ID succeeds; no method available; token supplied
  + no saved; token mismatch; good token; whitespace-
  padded token still matches; already-normal pre-state
  with Touch ID) plus default-parameter lock via
  `inspect.signature(recover)` and `RECOVERY_TOKEN_FILE`
  path lock against `BASE_DIR / "recovery_token.txt"`.
- Notes: **Honest framing.** Recovery paths weaken the
  cryptographic story but strengthen the operational story
  — without them, false-positive lockouts have no off-ramp
  and the system is unusable as a daily-driver sentinel.
  Recovery use rate should be near-zero in steady state; a
  high rate signals the primitive is mis-calibrated. The
  `recovery_used` event with `prior_mode` + method fields
  is the audit trail.
  **Threat model.** An attacker with the owner's Touch ID
  finger or the recovery-token secret can clear lockout —
  but those are the same two factors the owner uses to
  auth in the first place. The recovery surface does NOT
  expand the auth surface. Storing the recovery token in
  a password manager (not in `~/.face_sentinel/` itself)
  separates the blast radius.
  **What this DOESN'T cover.** If Touch ID hardware fails
  AND no recovery token was provisioned, the owner is
  still locked out and must edit `state.json` manually.
  Acknowledged gap.

---

## Counts (post-v0.1.21)

- Total: 27
- `:proved`: 4 — LZ-016 (outlier-detection algorithm),
  LZ-017 (liveness metric properties), LZ-018 (priority
  dispatcher correctness), LZ-026 (composed_correctness
  Lean theorem chaining the three Lean-proved modules
  into a single end-to-end pipeline assertion; the FIRST
  `:proved`-status spec entry derived from a TCE
  Discovery.Triadic finding across the entire Triad).
  All lean-proved hermetically in `src/lean4/`.
- `:tested`: 20 — LZ-001..LZ-015 + LZ-019 + LZ-020 + LZ-021
  + LZ-023 + LZ-027. LZ-023 promoted at v0.1.21 (first
  joint-closure entry to land an integration test).
- `:verified`: 0
- `:benchmarked`: 0
- `:argued`: 3 — LZ-022, LZ-024, LZ-025 (the three remaining
  TCE Discovery.Triadic joint-closure entries; LZ-026
  promoted to `:proved` at v0.1.21 via Composed.lean).
  Per conjunctive-claim discipline, sub-claim evidence
  (each component's individual `:tested`/`:proved` status)
  does not promote the joint claim; promotion to `:tested`
  requires a joint integration test exercising the
  conjunction.
- `:open`: 0

Promotion queue (highest-leverage, ordered by ease):
1. **LZ-022..LZ-026 joint integration tests** — each
   joint-closure entry carries a documented promotion path
   in its `Notes:` field. LZ-026 (the directional 3-cycle
   over the Lean-proved trio) is the cleanest `:proved`
   target since the modules already exist; needs a
   `composed_correctness` theorem in `src/lean4/` linking
   LZ-016, LZ-017, LZ-018.
2. **Lean expansion** — formalise additional `:tested`
   entries that admit it. Natural next candidates:
   LZ-006 prune-bounded list invariant, LZ-007 watch-loop
   state-machine, LZ-013 byte-diff inequalities.
3. **LZ-002 calibration** — fixture-driven (image,
   expected band) test set. Held until a clean fixture
   source emerges (face-data identifiability problem).
4. **Cross-deployment dependency** — LavaLamp heartbeat
   could augment Lazarus auth (`re-auth requires LavaLamp
   daemon liveness within N seconds`), same pattern PharOS
   uses. New spec entry if pursued.
