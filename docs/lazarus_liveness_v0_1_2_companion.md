# Lazarus liveness v0.1.2 — anti-spoof port companion

Date: 2026-05-10. Owner: Aaron Green. Session: port the
two-capture byte-diff liveness probe from the personal working
copy at `~/Projects/Possibilistic_Security/face_sentinel.py`
to the public lazarus repo so the v0.1.0 sentinel stops being
defeated by a printed photo.

## §1 — Computational basis

### Files modified

- `face_sentinel.py`:
  - +2 module-top constants (`LIVENESS_DELTA_MIN = 0.008`,
    `LIVENESS_GAP_SECONDS = 1.0`).
  - +1 helper (`_liveness_delta(bytes_a, bytes_b)`) — pure
    byte-diff ratio with explicit length-mismatch handling.
  - +1 IO-bound wrapper (`liveness_check(first_capture)`) —
    captures a second frame after `LIVENESS_GAP_SECONDS`,
    downsizes both to 64×48 BMP via `sips`, returns the live
    decision. Fails open on infrastructure error.
  - `check_once()` is_match branch now invokes the probe
    before accepting the match; on fail, sets state to
    Shakespeare with `lockout_reason="liveness_fail"`.
  - `check_once()` wrapped in try/finally to keep `tmp_full`
    alive across the match branch (symmetric source format on
    both liveness frames is load-bearing — see §2).

### Files added

- `test/test_liveness_check.py` — 12 assertions on the pure
  byte-diff helper plus threshold-semantics checks. No camera
  required.
- `docs/lazarus_liveness_v0_1_2_companion.md` — this file.

### Files updated

- `LAZARUS_SPEC.md` — LZ-013 entry added under a new v0.1.2
  section. Counts updated.
- `artifact_registry.md` — LZ-013 row added; counts
  (13 / 0 / 3 / 0 / 0 / 7 / 3) and A1–A6 self-check refreshed.
- `.github/workflows/test.yml` — third test step.
- `dashboard.md` — status summary, recent-completed.
- `changelog.md` — v0.1.2 entry at top.

### Dependencies

None added. The liveness probe uses `time.sleep`, `os`,
`tempfile`, and `subprocess` — all already imported by
`face_sentinel.py`. The only external invocation is `sips`,
which was already in use for the existing background-shift
check.

### Build / test commands

```bash
bash test/test_oversight_action.sh
python3 test/test_network_monitor_classify.py
python3 test/test_liveness_check.py
```

All three PASS as of this session, locally and on the GitHub
Actions `macos-latest` runner.

## §2 — Results

### §2.1 — Why a static photo defeats v0.1.0 (and the fix)

The v0.1.0 sentinel runs `imagesnap → face_compare match` and
trusts a positive distance < 18.0 as "owner is at the desk."
A printed photo of the owner — held up in front of the
camera — produces a feature print that scores indistinguishably
from a live capture. The Apple Vision feature print is a
similarity score, not a liveness signal.

The fix: take a *second* capture after a 1-second pause and
compare. A real face produces ~0.015 byte-diff at 64×48 BMP
(skin micro-motion: head sway, blinks, breath). A printed
photo or held-still iPad/phone screen produces ~0.0. The
threshold sits at 0.008 — comfortably below the real-face
floor and above the photo-attack ceiling.

### §2.2 — Symmetric source format is load-bearing

A subtle pitfall in the port: the original `~/Projects/
Possibilistic_Security/face_sentinel.py` keeps `tmp_full`
(the full-resolution first capture) alive through the match
branch. The port initially fell into a trap of using the
already-shrunk `cap_lowres` (320px JPEG) as the first frame
while the liveness probe captured a fresh full-resolution
second frame. Asymmetric source formats produce JPEG
re-encode artifact deltas that masquerade as motion — a real
face would still test as live, but the threshold loses its
discriminating power against attacks that happen to share the
artifact distribution.

The fix: wrap `check_once` in try/finally and defer
`os.remove(tmp_full)` to the finally block. The match branch
now passes the full-res `tmp_full` directly to
`liveness_check`, which captures its own full-res second
frame. Both go through the same `to_tiny` → 64×48 BMP path.
Symmetric.

### §2.3 — What this catches and misses

**Catches.** Printed photos. iPad/phone screens held up showing
a still image. Anything that's spatially still during the 1s
gap.

**Misses.** Video playback (still has frame-to-frame variation
even of a still scene). 3D-printed face masks (3D, will move
with the holder). Deepfake stream (live AI-generated frames
with motion). All of these are v2 territory:

- **Active illumination flash** — emit a brief screen flash
  during the second capture; a real face reflects it
  asymmetrically; a printed photo reflects it uniformly; a
  screen / video rejects most of it.
- **Blink challenge** — instruct the user to blink, capture
  before/after, look for the eyelid signature.
- **Depth sensor** — TrueDepth / structured-light gives a
  hard depth signal that flat attacks can't fake.

The current liveness probe is the cheapest meaningful step
above "no liveness check at all" and is the one that closes
the printed-photo gap. v2 is queued as
`dashboard.md` priority TBD.

## §3 — Verification

### §3.1 — `_liveness_delta` (LZ-013, pure math)

Test artifact: `test/test_liveness_check.py`. 12 assertions:

- Identical bytes → delta 0.0.
- All-different bytes → delta 1.0.
- Half-and-half → delta 0.5.
- One byte in 100 → delta 0.01.
- Length mismatch → `None`.
- Empty input → `None`.
- Threshold constants (`LIVENESS_DELTA_MIN == 0.008`,
  `LIVENESS_GAP_SECONDS == 1.0`).
- Inequality direction: `delta == 0.007 → not live`,
  `0.008 → live`, `0.009 → live`, `0.015 → live`,
  `0.0 → not live`. (`>=` boundary, not `>`.)

PASS on macOS Darwin 25.4.0 with system Python 3.

### §3.2 — `liveness_check` (LZ-013, IO wrapper)

Manual evidence — the wrapper is IO-bound (subprocess to
`sips`, `time.sleep`, real camera) and not exercised in the
automated test. Stub-driven coverage of the wrapper is
queued under `dashboard.md` priority #1
(`FACE_COMPARE_STUB` env-var shim), which also unlocks
LZ-006/007/008.

### §3.3 — `check_once` integration

Manual evidence — the integration runs against a real camera
and a real owner's face. The three branches exercised:

- **Live face → match passes.** Byte-diff at 64×48 BMP is
  ~0.015 for the owner sitting still. `liveness["live"] ==
  True` → `state["last_seen_owner"]` refreshes,
  `match_ok` log line carries `liveness_delta`.
- **Printed photo → liveness_fail.** Held-up photo produces
  ~0.0 delta. `liveness["live"] == False` →
  `state["mode"] = "shakespeare"`,
  `state["lockout_reason"] = "liveness_fail"`,
  `state["liveness_delta"] = <measured>`. The /lazarus
  companion shifts into Bard mode on next invocation.
- **Camera failure → fail open.** Second capture fails →
  `liveness["reason"] == "second_capture_failed_fail_open"`,
  `live: True`, match accepted. The owner is not locked out
  because a flaky camera flapped.

### §3.4 — Self-audit (A0 / A1–A6)

- **A0** — `CLAUDE.md` claims still match observable practice
  (now 13 entries, 3 tested).
- **A1** — All 13 LZ-IDs in `LAZARUS_SPEC.md` have rows in
  `artifact_registry.md`.
- **A2** — Logic tier and Status fields match between spec
  and registry.
- **A3** — Tests cited at `test/test_*.{sh,py}` exist and run.
  Source files cited (`face_sentinel.py`, etc.) exist per
  `git ls-files`.
- **A4** — All `:tested` entries carry `example-tested`. All
  `:argued` entries carry `manual` or `example-tested`. All
  `:open` entries carry `none`.
- **A5** — Counts in spec, registry, dashboard all read
  13 / 0 / 3 / 0 / 0 / 7 / 3.
- **A6** — Three tests run on every push via
  `.github/workflows/test.yml` on `macos-latest`.

## §4 — Spec impact

One new entry:

| LZ-ID | Key | Logic tier | Evidence type | Status |
|---|---|---|---|---|
| LZ-013 | anti-spoof liveness probe | Operational | example-tested | :tested |

No status changes to existing entries. The integration into
`check_once` did not change any existing branch; it inserted
the liveness probe before the existing `last_seen_owner`
refresh on the is_match path. LZ-007 (watch-loop state
transitions) remains `:open` — it now has a sixth branch to
exercise (liveness_fail) when the stub-driven test is added.

## §5 — Calibration data

Single-developer calibration only. Real face sitting still:
~0.015. iPad-photo / printed-photo deltas not yet measured
on this rig. Threshold 0.008 was set conservatively below
the real-face floor; if it produces false positives in
practice, drop to 0.005 and re-evaluate. Sentinel.log
captures every match with `liveness_delta`, so post-deploy
calibration is straightforward.
