# artifact_registry.md — Lazarus

Version: 0.1.0 (first formal spec of the public release shipped
on 2026-05-10. Twelve LZ-NNN spec entries cover the visual
sentinel, network monitor + honeypot, and OverSight Tier 1
forensic logger. Counts: 12 / 0 / 2 / 0 / 0 / 7 / 3.)

## Coverage rule

Every spec LZ-ID must have a row here. `git ls-files` must
contain every Test/Proof and Source path listed.

## Columns

- **LZ-ID** — matches `LAZARUS_SPEC.md`.
- **Key** — short name from the spec entry.
- **Logic tier** — `Core` / `Operational` / `Boundary`.
- **Evidence type** — `lean-proved` / `type-checked` /
  `algebraic` / `property-tested` / `example-tested` /
  `benchmarked` / `manual` / `none`.
- **Test/Proof file** — path to the artifact establishing the
  claim. `—` if none yet.
- **Source file** — path to the implementation the claim
  describes. `—` if none yet.
- **Status** — `:proved` / `:verified` / `:tested` /
  `:benchmarked` / `:argued` / `:open`.

---

## Spec entries

| LZ-ID | Key | Logic tier | Evidence type | Test/Proof file | Source file | Status |
|---|---|---|---|---|---|---|
| LZ-001 | visual-skin/security decoupling | Boundary | manual | LAZARUS_SPEC.md LZ-001 + lazarus.md §Customization | face_sentinel.py (state machine) + lazarus.md (companion prompt) | :argued |
| LZ-002 | face-match distance bands | Operational | manual | LAZARUS_SPEC.md LZ-002 (calibration notes) | face_compare.swift (cmdMatch thresholds) + face_sentinel.py (MATCH/UNCERTAIN/LOCK_THRESHOLD) | :argued |
| LZ-003 | shakespeare-mode companion refusal | Operational | manual | lazarus.md §Shakespeare mode + LAZARUS_SPEC.md LZ-003 | lazarus.md (companion prompt) + face_sentinel.py (mode field in state.json) | :argued |
| LZ-004 | --auth clears shakespeare | Operational | example-tested | docs/lazarus_v0_1_0_companion.md §3.1 (in-session demo) | face_sentinel.py auth() lines 188–205 | :argued |
| LZ-005 | apple-vision local-only | Boundary | manual | LAZARUS_SPEC.md LZ-005 (inspection notes) | face_compare.swift + face_sentinel.py (no networking imports) | :argued |
| LZ-006 | reference-storage bounded | Operational | none | — (planned: test/test_reference_bounds.sh) | face_sentinel.py prune_oldest() + prune_cmd() | :open |
| LZ-007 | watch-loop state transitions | Operational | none | — (planned: test/test_watch_state_transitions.py with stubbed face_compare) | face_sentinel.py check_once() lines 296–367 | :open |
| LZ-008 | --peek JSON output shape | Boundary | none | — (planned: test/test_peek_output.py with stubbed face_compare) | face_sentinel.py peek() lines 383–415 | :open |
| LZ-009 | network-monitor classification | Operational | example-tested | test/test_network_monitor_classify.py | network_monitor.py classify() + AI_PROCESSES + KNOWN_GOOD + SYSTEM_PREFIXES | :tested |
| LZ-010 | network-honeypot port listeners | Operational | manual | LAZARUS_SPEC.md LZ-010 + README.md §What it does | network_honeypot.py | :argued |
| LZ-011 | oversight Tier 1 forensic logging | Operational | example-tested | test/test_oversight_action.sh | oversight_action.sh | :tested |
| LZ-012 | companion read-only discipline | Boundary | manual | lazarus.md §What you do NOT do + LAZARUS_SPEC.md LZ-012 | lazarus.md | :argued |

## Counts

- Total: 12
- `:proved`: 0
- `:tested`: 2 (LZ-009, LZ-011)
- `:verified`: 0
- `:benchmarked`: 0
- `:argued`: 7 (LZ-001, LZ-002, LZ-003, LZ-004, LZ-005, LZ-010, LZ-012)
- `:open`: 3 (LZ-006, LZ-007, LZ-008)

## Cross-audit A1–A6 self-check (post-v0.1.0)

- **A1 — Coverage.** Every LZ-ID in `LAZARUS_SPEC.md` has a row
  here. ✓ (12 of 12).
- **A2 — Logic & Status parity.** Spec → registry Logic tier and
  Status fields match exactly. Key column compresses spec keys
  for table readability (e.g. spec
  "visual-skin/security-primitive decoupling" → registry
  "visual-skin/security decoupling"); LZ-ID is the canonical
  link. ✓.
- **A3 — Evidence exists.** LZ-009 cites
  `test/test_network_monitor_classify.py` (exists; runs from
  repo root). LZ-011 cites `test/test_oversight_action.sh`
  (exists; runs from repo root). The seven `:argued` entries
  cite manual evidence in spec / companion / README. The three
  `:open` entries cite "—" honestly.
- **A4 — Status honesty.** Two `:tested` entries carry
  `example-tested`. Seven `:argued` entries carry `manual` or
  `example-tested` (LZ-004 has an in-session demonstration but
  no CI artifact yet). Three `:open` entries carry `none`. No
  entry has a status its evidence type cannot support.
- **A5 — Stale counts.** Counts above (12 / 0 / 2 / 0 / 0 / 7 /
  3) match `LAZARUS_SPEC.md` final-section counts and
  `dashboard.md` summary.
- **A6 — Test sync.** LZ-009 and LZ-011 tests run from
  `test/`. CI integration (`.github/workflows/test.yml`) is
  forthcoming; the tests are runnable locally on macOS with
  `bash test/test_oversight_action.sh` and
  `python3 test/test_network_monitor_classify.py`.

## Dependencies on other Triad-Deployment spec entries

Lazarus is the most-mature deployment in the Triad and stands on
its own; it does not yet share artifacts with LavaLamp or PharOS.
Cross-deployment dependencies (e.g. consuming LavaLamp's
heartbeat for additional auth gating) are out of scope for v0.1
and would be tracked here as Lazarus spec entries acquire LL-NNN
or PH-NNN prerequisites.
