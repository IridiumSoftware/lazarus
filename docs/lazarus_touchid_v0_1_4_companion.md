# Lazarus Touch ID v0.1.4 — port companion

Date: 2026-05-10. Owner: Aaron Green. Session continues from
v0.1.3 (leave-one-out --prune fix). This companion covers the
port of the Touch ID opportunistic pre-face gate from the
personal working copy.

## §1 — Computational basis

### Background

After the v0.1.3 ship, three trees held face_sentinel.py:

- `~/Desktop/lazarus/` — public, distributed.
- `~/Desktop/possibilistic-security/` — older clone (deleted
  in commit `fe08e70` earlier in this session).
- `~/Projects/Possibilistic_Security/` — personal daily
  driver.

The personal copy has a Touch ID step in `auth()` that lazarus
lacked. Aaron asked to port it so the two trees' auth flows
converge.

### What the port adds

A pre-face Touch ID gate. Before the camera capture step in
`auth()`, the script invokes `bioutil -r` — the macOS
biometric-records read tool. `bioutil` triggers the system
Touch ID prompt because reading biometric records requires
biometric authentication. Three outcomes:

| Outcome | Cause | Behavior |
|---|---|---|
| `"ok"` | bioutil returned 0 | Touch ID prompt succeeded; proceed to face check |
| `"nonzero"` | bioutil returned non-zero | Prompt dismissed, no enrolled fingerprints, or other failure; warn + proceed to face check (fail-open) |
| `"unavailable"` | bioutil missing or timed out | Touch ID hardware unavailable; warn + proceed to face check (fail-open) |

### Files modified

- `face_sentinel.py`:
  - +1 helper: `_touchid_check(timeout_seconds=30, _runner=None)`.
    The `_runner` parameter is for testability — production
    callers leave it `None` (the helper defaults to
    `subprocess.run`); tests inject a stub.
  - `auth()` now runs `_touchid_check()` as Step 1, before
    the existing face-capture step. Each outcome is printed
    to stdout (so the user knows what's happening) and
    logged to `sentinel.log` as `touchid_ok` /
    `touchid_nonzero` / `touchid_unavailable`.

### Files added

- `test/test_touchid_check.py` — 11 assertions over the three
  return paths plus the testability surface (timeout
  forwarding, default value lock, exception propagation).
- `docs/lazarus_touchid_v0_1_4_companion.md` — this file.

### Files updated

- `LAZARUS_SPEC.md` — LZ-015 entry added under a new v0.1.4
  section. LZ-004 description updated to mention Touch ID as
  a step before face match.
- `artifact_registry.md` — LZ-015 row added; counts
  (15 / 0 / 5 / 0 / 0 / 7 / 3) and A1–A6 self-check
  refreshed.
- `.github/workflows/test.yml` — fifth test step.
- `dashboard.md` — status summary, recent-completed.
- `changelog.md` — v0.1.4 entry at top.

### Dependencies

None added. `subprocess` is stdlib; `bioutil` ships with
macOS (since the introduction of Touch ID-equipped Macs).

### Build / test commands

```bash
bash test/test_oversight_action.sh
python3 test/test_network_monitor_classify.py
python3 test/test_liveness_check.py
python3 test/test_prune_logic.py
python3 test/test_touchid_check.py
```

All five PASS as of this session, locally and on
`macos-latest` CI.

## §2 — Results

### §2.1 — Why fail-open

Lazarus targets the single-owner desktop case: one person
uses the machine, they want a strong-but-friction-light
guard against someone else picking it up. In this scenario:

- A legitimate owner on a Mac WITHOUT Touch ID hardware
  should still be able to authenticate. (Some Macs don't
  have a fingerprint sensor; external displays / docks
  often disable it.)
- A legitimate owner whose Touch ID hardware is glitching
  (cold finger, sweat, occlusion) should still be able to
  authenticate.
- An attacker who has the laptop but NOT the owner's
  fingerprint hits the bioutil prompt and either dismisses
  it (`"nonzero"`) or doesn't have a valid fingerprint to
  press (`"nonzero"`). Either way they fall through to the
  face check — which catches them.

The defensive value: an attacker can't *silently* skip past
the Touch ID gate; they have to actively dismiss the prompt,
and either outcome is logged. The Touch ID step raises the
bar in the common case (laptop snatched, owner not present)
without locking out the owner in the edge case (no Touch ID
hardware available).

### §2.2 — Honest framing

This is not a structural guarantee. An attacker who can:

- physically disable the Touch Bar / fingerprint sensor;
- intercept the `bioutil` invocation;
- replace `bioutil` itself on the system;
- run on a Mac without Touch ID at all (where the attacker
  IS the legitimate owner of that hardware);

…bypasses this layer entirely. The defensive value is
real but bounded. A stricter `--strict-touchid` mode that
treats `"nonzero"` and `"unavailable"` as hard failures
would close the easy bypasses, but at the cost of
unrecoverable lock-out on Touch-ID-less hardware. Held as
future work — would warrant its own spec entry (LZ-NNN) and
a clear escape hatch for headless / no-hardware setups.

### §2.3 — bioutil semantics

`bioutil -r` reads enrolled biometric records. Per the macOS
man pages, this operation requires biometric authentication
— invoking it from a non-privileged context triggers the
system Touch ID prompt. Empirically this matches Aaron's
production behavior: running `bioutil -r` interactively
displays the Touch ID prompt; pressing an enrolled finger
returns exit 0; dismissing or pressing an unenrolled finger
returns non-zero.

We do NOT use `sudo bioutil -r` — the privileged path would
require either a stored password or an admin auth dialog,
both of which defeat the "lightweight pre-face gate"
intent.

## §3 — Verification

### §3.1 — `_touchid_check` (LZ-015, pure helper)

Test artifact: `test/test_touchid_check.py`. 11 assertions
across three return paths and four testability concerns:

**Return paths:**
- `runner_returns(0)` → `"ok"`.
- `runner_returns(1)` / `(2)` / `(127)` / `(-1)` → `"nonzero"`.
- `runner_raises(FileNotFoundError)` → `"unavailable"`.
- `runner_raises(TimeoutExpired)` → `"unavailable"`.

**Testability:**
- `timeout_seconds=5` is forwarded to the runner.
- Default `timeout_seconds == 30` (value lock).
- Unexpected exceptions (`RuntimeError`) propagate; they
  are NOT silently converted to `"unavailable"` — only the
  two named exceptions are caught.

PASS on macOS Darwin 25.4.0 with system Python 3.

### §3.2 — `auth()` integration

Manual evidence — the integration runs against real Touch
ID hardware on the development rig. Sequence:

1. `python3 face_sentinel.py --auth`.
2. Stdout: `"Touch ID verification..."`.
3. System prompt appears requesting Touch ID.
4. Owner presses enrolled fingerprint.
5. Stdout: `"Capturing face..."` (Step 2 begins).
6. Camera captures, face matches.
7. Stdout: `"AUTH OK. Face distance: ..."`.
8. `state.json` updated with `authenticated=true`,
   `mode="normal"`.
9. `sentinel.log` carries a `touchid_ok` event followed by
   `auth_ok`.

If the owner dismisses the Touch ID prompt instead:
- Stdout: `"Touch ID check returned non-zero. Proceeding
  with face check."`
- `sentinel.log` carries `touchid_nonzero`.
- Face check proceeds; if it succeeds, auth still succeeds.

This manual flow was the canonical Aaron-personal-tree
behavior under the original (pre-port) implementation and
is unchanged by the port.

### §3.3 — Self-audit (A0 / A1–A6)

- **A0** — `CLAUDE.md` claims still match observable
  practice (now 15 entries, 5 tested).
- **A1** — All 15 LZ-IDs in `LAZARUS_SPEC.md` have rows in
  `artifact_registry.md`.
- **A2** — Logic tier and Status fields match between spec
  and registry.
- **A3** — Tests cited at `test/test_*.{sh,py}` exist and
  run. Source files cited (`face_sentinel.py`) exist per
  `git ls-files`.
- **A4** — All `:tested` entries carry `example-tested`.
  All `:argued` entries carry `manual` or `example-tested`.
  All `:open` entries carry `none`.
- **A5** — Counts in spec, registry, dashboard all read
  15 / 0 / 5 / 0 / 0 / 7 / 3.
- **A6** — Five tests run on every push via
  `.github/workflows/test.yml` on `macos-latest`.

## §4 — Spec impact

One new entry:

| LZ-ID | Key | Logic tier | Evidence type | Status |
|---|---|---|---|---|
| LZ-015 | Touch ID opportunistic pre-face gate | Operational | example-tested | :tested |

One existing entry updated (LZ-004 — auth-clears-shakespeare):
the Description now mentions Touch ID as the gate preceding
face match. Status unchanged (`:argued`).

No other spec changes.

## §5 — Future work

- **`--strict-touchid` flag.** Treat `"nonzero"` /
  `"unavailable"` as hard failures (exit 1). Would warrant a
  new spec entry (LZ-NNN) and CLI documentation.
- **`--no-touchid` flag.** For headless workflows or testing,
  explicit opt-out of the Touch ID step. Lower priority than
  strict mode; can be folded into one flag with three values
  (`auto` / `strict` / `off`).
- **LAContext-based Swift helper.** Replace `bioutil` with a
  small Swift binary that uses `LAContext.evaluatePolicy(
  .deviceOwnerAuthenticationWithBiometrics)`. Cleaner API,
  more honest semantics (specifically asks for biometric
  auth rather than reading-records-as-side-effect), and
  Apple's recommended path. Held until/unless the
  `bioutil`-based path causes issues.
