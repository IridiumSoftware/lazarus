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
- Description: When `face_sentinel.py --auth` succeeds (face
  detected, distance < `MATCH_THRESHOLD`), the script overwrites
  `state.json` with `authenticated=true`,
  `auth_time=<now>`, `last_seen_owner=<now>`,
  `mode="normal"`, and removes `lockout_time` and
  `lockout_distance`. The next `/lazarus` invocation reads the
  cleared state and resumes normal diagnostics.
- Evidence type: example-tested (in-session demonstration)
- Status: :argued
- Source: `face_sentinel.py` `auth()` lines 188–205,
  `lazarus.md` §Shakespeare mode.
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
  makes no network calls. Confirmed by inspection.
- Evidence type: manual
- Status: :argued
- Source: `face_compare.swift` (no `URLSession`, no `Network`
  imports), `face_sentinel.py` (only subprocess calls to
  `imagesnap` / `sips` / `face_compare` / `pmset` /
  `osascript`).
- Notes: Promotion to `:tested` requires a CI lint that grep-
  fails on `URLSession` / `Network.framework` / `urllib` /
  `requests` / `socket` in the face-comparison source files.

### LZ-006 — reference-storage-bounded
- Key: <=50 references, ~30KB each, oldest pruned
- Logic tier: Operational
- Description: `face_sentinel.py` enforces `MAX_REFERENCES = 50`
  via `prune_oldest`, which sorts references by mtime and
  deletes the oldest until the count is at or below cap. Each
  reference is a (`.fpdata`, `.json`, `.jpg`) triple; the JPEG
  is downscaled to 480px via `sips`. The `--prune` command
  flags references whose self-distance exceeds 2× the average
  (likely outliers).
- Evidence type: example-tested
- Status: :open
- Source: `face_sentinel.py` `enroll()` / `prune_oldest()` /
  `prune_cmd()`.
- Notes: Test/Proof file pending — a `test/test_reference_bounds.sh`
  fixture-driven test would create 51 fake reference triples
  (no actual images required since the test only exercises the
  pruning loop), call `enroll` or `prune_oldest`, and assert
  the count returns to 50.

### LZ-007 — watch-loop-state-transitions
- Key: check_once handles 5 branches (match, no-face+seen,
  bg-shift, uncertain, mismatch)
- Logic tier: Operational
- Description: The `--watch` daemon's `check_once` function is a
  five-branch state machine over the result of one capture +
  match cycle:
  1. `faces == 0` and `last_seen_owner` set: passive ok unless
     background has shifted (then `bg_shift` event).
  2. `faces == 0` and no prior owner sighting: `no_face` event,
     no state change.
  3. `is_match`: run the LZ-013 liveness probe; on
     `static_likely`, fall through to the same Shakespeare-mode
     state transition as branch 5; otherwise refresh
     `last_seen_owner`, log `match_ok`.
  4. `uncertain`: log `uncertain` event, keep capture for
     review, no state change.
  5. mismatch: set `mode="shakespeare"`,
     `authenticated=false`, log `MISMATCH`; if distance >
     `LOCK_THRESHOLD`, also `lock_screen()`.
- Evidence type: example-tested
- Status: :open
- Source: `face_sentinel.py` `check_once()`.
- Notes: Test/Proof file pending. The branches can be exercised
  without a camera by stubbing `run_face_compare` and
  `liveness_check` and feeding synthetic JSON (faces, distance,
  match, uncertain, live), then asserting on the resulting
  state.json + log lines.

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
    failed"}`
- Evidence type: example-tested
- Status: :open
- Source: `face_sentinel.py` `peek()` lines 383–415.
- Notes: Test/Proof file pending. Like LZ-007, exercisable with
  a stubbed `run_face_compare` returning canned JSON.

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

## Counts (post-v0.1.3)

- Total: 14
- `:proved`: 0
- `:tested`: 4 (LZ-009, LZ-011, LZ-013, LZ-014)
- `:verified`: 0
- `:benchmarked`: 0
- `:argued`: 7 (LZ-001, LZ-002, LZ-003, LZ-004, LZ-005, LZ-010, LZ-012)
- `:open`: 3 (LZ-006, LZ-007, LZ-008)

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
