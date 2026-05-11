# Lazarus :open-promotion v0.1.5 — companion

Date: 2026-05-10. Owner: Aaron Green. Session continues from
v0.1.4 (Touch ID port). This companion covers the v0.1.5 work
that promotes the three remaining `:open` entries — LZ-006,
LZ-007, LZ-008 — to `:tested`, plus a drive-by bug fix and a
test affordance.

## §1 — Computational basis

### Background

After v0.1.4, the spec carried three `:open` entries from
v0.1.0 with promotion paths documented but no test artifacts:

- **LZ-006** (reference-storage-bounded): `prune_oldest`
  removes oldest refs over cap.
- **LZ-007** (watch-loop-state-transitions): `check_once`'s
  multi-branch state machine.
- **LZ-008** (peek-json-output-shape): `--peek`'s JSON
  output contract.

The v0.1.0 dashboard listed "`FACE_COMPARE_STUB` env var" as
the #1 priority item — a single test affordance that would
unlock all three. This session delivers that plus the three
tests.

### What changed

- Added `FACE_COMPARE_STUB` env-var check in
  `run_face_compare()`. When set, returns parsed JSON
  directly without invoking the binary. ~10 lines.
- Fixed a latent bug in `prune_oldest`: the function
  computes `to_remove = len(metas) - MAX_REFERENCES`. When
  the pool is under cap, this is negative; `metas[:to_remove]`
  with a negative index selects all-but-newest, which would
  silently delete most refs. The production caller
  (`enroll()`) already guarded against this, but exposing
  the function to direct test/CLI use surfaced the bug.
  Added `if to_remove <= 0: return`.
- Wrote three new tests:
  - `test/test_reference_bounds.py` (LZ-006) — 7 test
    cases via tempdir + monkey-patched `REF_DIR`.
  - `test/test_watch_state_transitions.py` (LZ-007) — 10
    test cases (8 branches + 2 early-returns) via
    module-level monkey-patching of `capture_full`,
    `run_face_compare`, `liveness_check`,
    `backgrounds_similar`, `shrink`, `lock_screen`, plus
    tempdir overrides for state-file paths.
  - `test/test_peek_output.py` (LZ-008) — 7 test cases
    (5 branches + output-shape + distance-rounding) via
    `FACE_COMPARE_STUB` env-var + monkey-patched
    `capture_full`.

### Files modified

- `face_sentinel.py` — added FACE_COMPARE_STUB shim
  (+9 lines) and prune_oldest guard (+7 lines including
  comment).
- `LAZARUS_SPEC.md` — LZ-006/007/008 entries rewritten with
  `:tested` status, evidence type `example-tested`, and
  Test/Proof citations. LZ-007 description expanded to 8
  branches (was 5; now lists A/B/C/D/E/F/G/H matching the
  test file). New v0.1.5 section heading. Counts updated.
- `artifact_registry.md` — three rows updated; counts and
  A1–A6 self-check refreshed.
- `.github/workflows/test.yml` — three new test steps.
- `dashboard.md` — status summary, priority stack (dropped
  the now-completed LZ-006/007/008 item; bumped OverSight
  Tier 2 from "LZ-013" to "LZ-016"; corrected the stale
  "runs both tests" line), recent-completed.
- `changelog.md` — v0.1.5 entry at top.

### Files added

- `test/test_reference_bounds.py`
- `test/test_watch_state_transitions.py`
- `test/test_peek_output.py`
- `docs/lazarus_open_promotion_v0_1_5_companion.md`
  (this file)

### Dependencies

None added. All tests use stdlib only (`tempfile`, `os`,
`shutil`, `contextlib`, `io`, `json`, `pathlib`).

### Build / test commands

```bash
bash test/test_oversight_action.sh
python3 test/test_network_monitor_classify.py
python3 test/test_liveness_check.py
python3 test/test_prune_logic.py
python3 test/test_touchid_check.py
python3 test/test_reference_bounds.py
python3 test/test_peek_output.py
python3 test/test_watch_state_transitions.py
```

All eight PASS as of this session, locally and on
`macos-latest` CI.

## §2 — Results

### §2.1 — Why three different test patterns

The three tests use three different approaches by design:

- **LZ-006** uses only `REF_DIR` patching plus a small
  synthetic ref-triple factory. No subprocess stubbing
  needed because `prune_oldest` is pure filesystem
  operations.
- **LZ-007** uses module-level monkey-patching of six
  functions plus five module-level path constants. This is
  the heaviest fixture in the suite — `check_once` is
  the heaviest function. Patching at the module level
  intercepts internal calls because Python resolves names
  at call time.
- **LZ-008** uses the `FACE_COMPARE_STUB` env-var (delivers
  the v0.1.0 dashboard plan) plus a small `capture_full`
  monkey-patch. Cleaner shape because `peek()` is shallow.

The `FACE_COMPARE_STUB` env var is still useful even
though only one of the three tests uses it: it's an
affordance for ad-hoc shell-driven manual testing
("`FACE_COMPARE_STUB='{"faces": 0}' python3
face_sentinel.py --peek`"), and it serves as a documented,
production-visible test surface.

### §2.2 — The prune_oldest bug

Before this commit, calling `prune_oldest` with an
under-cap pool would silently delete most references. The
math:

```python
to_remove = len(metas) - MAX_REFERENCES  # e.g. 5 - 50 = -45
for meta_path in metas[:to_remove]:      # metas[:-45]
    ... delete ...
```

Python's slice with a negative `stop` index drops the last
N elements. So `metas[:-45]` on a 5-element list returns
`[]` and nothing gets deleted — but on a 60-element list it
would return the first 15. This means the bug was both
under-cap-safe AND over-cap-safe, but in a way that depends
on the negative slicing semantics.

Wait — re-read more carefully. For `len(metas) = 5`,
`to_remove = -45`. `metas[:-45]` with a 5-element list:
since `-45` is less than `-len(metas) = -5`, the slice is
empty. So the bug is silent under-cap. Phew.

For `len(metas) = 49`, `to_remove = -1`. `metas[:-1]` on a
49-element list returns the first 48 — that's the disaster
case. **49 refs → delete 48.**

The fix is `if to_remove <= 0: return`. The regression test
locks this in.

### §2.3 — LZ-007 branch coverage

Eight branches plus two early-return paths exercised. The
state-machine model:

```
capture_fail (early return)
match_error (early return)
        ↓
   faces == 0
        ├── last_seen_owner set
        │       ├── bg unchanged → A (no_face owner_walked_away)
        │       └── bg shifted   → B (no_face + bg_shift)
        └── no last_seen_owner   → C (no_face owner_never_seen)
   faces > 0
        ├── is_match
        │       ├── liveness live    → D (match_ok + liveness_delta)
        │       └── liveness not live → E (Shakespeare + liveness_fail)
        ├── uncertain               → F (uncertain event)
        └── mismatch
                ├── distance ≤ LOCK_THRESHOLD → G (Shakespeare)
                └── distance > LOCK_THRESHOLD → H (Shakespeare + lock)
```

Each path's test asserts on `state.json` mutations and
`sentinel.log` event sequence. The `lock_screen` call in
branch H is verified via a stub that records invocations.

### §2.4 — LZ-008 contract verification

The peek-output contract from the spec:

- Empty: `{"desk": "empty", "faces": 0}`
- Occupied: `{"desk": "occupied", "who": "...", "faces": N,
  "distance": F}` where `who ∈ {owner, uncertain,
  stranger}` and `distance` is rounded to 1 decimal.
- Capture failure: `{"desk": "unknown", "error": "capture
  failed"}` + `sys.exit(1)`.

All five branches asserted. Plus:
- Output is exactly one newline-terminated line (no
  trailing garbage).
- Distance rounding: `12.345678` → `12.3`.

## §3 — Verification

### §3.1 — Test pass on macOS Darwin 25.4.0 with system Python 3

All eight tests run cleanly:

```
PASS test_oversight_action.sh
PASS test_network_monitor_classify.py
PASS test_liveness_check.py
PASS test_prune_logic.py
PASS test_touchid_check.py
PASS test_reference_bounds.py
PASS test_peek_output.py
PASS test_watch_state_transitions.py
```

### §3.2 — Self-audit (A0 / A1–A6)

- **A0** — `CLAUDE.md` claims still match observable
  practice (now 15 entries, 8 tested, 0 open).
- **A1** — All 15 LZ-IDs in `LAZARUS_SPEC.md` have rows in
  `artifact_registry.md`.
- **A2** — Logic tier and Status fields match between spec
  and registry.
- **A3** — Tests cited at `test/test_*.{sh,py}` exist and
  run. Source files cited (`face_sentinel.py`, etc.) exist
  per `git ls-files`.
- **A4** — All `:tested` entries carry `example-tested`.
  All `:argued` entries carry `manual` or `example-tested`.
  No `:open` entries remain. No status-evidence mismatch.
- **A5** — Counts in spec, registry, dashboard all read
  15 / 0 / 8 / 0 / 0 / 7 / 0.
- **A6** — All eight tests run on every push via
  `.github/workflows/test.yml` on `macos-latest`.

## §4 — Spec impact

Three status promotions, zero new entries:

| LZ-ID | Before | After |
|---|---|---|
| LZ-006 | :open / none | :tested / example-tested |
| LZ-007 | :open / none | :tested / example-tested |
| LZ-008 | :open / none | :tested / example-tested |

LZ-007's description was updated to reflect the 8 branches
(was documented as 5). The LZ-013 liveness fold-in was
already referenced in the v0.1.2 update; this v0.1.5 update
adds explicit A/B/C/D/E/F/G/H labels matching the test
file's case naming for cross-reference.

## §5 — Future work

The `:argued` set is the remaining surface. Six promotion
candidates ordered by leverage (per dashboard):

1. **LZ-005 grep-lint** — cheap (~10 min). Promotes Apple
   Vision local-only claim to `:tested`.
2. **LZ-002 fixture set** — needs synthetic / public-domain
   reference images.
3. **OverSight Tier 2** (LZ-016) — new entry + test.
4. **LZ-010 honeypot loop-connect** — fragile in CI.
5. **`--strict-touchid`** — new entry; held until a real
   use case surfaces.
6. **LZ-001 / LZ-003 / LZ-012** — visual-skin /
   shakespeare-refusal / read-only-discipline. These are
   prompt-layer claims; the test harness would need
   transcript-level audit tooling. Long-tail.
