# Lazarus prune v0.1.3 — leave-one-out pool quality scoring

Date: 2026-05-10. Owner: Aaron Green. Session continues from
the v0.1.2 anti-spoof liveness probe ship; this companion
covers the v0.1.3 fix to the broken `--prune` algorithm.

## §1 — Computational basis

### Background

After the v0.1.2 ship, Aaron ran `python3 face_sentinel.py
--prune` against the live `~/.face_sentinel/reference/` pool
(50 refs after a fresh enrollment session that added 12
kitchen-background captures). The output:

```
50 references. Testing quality...
Average self-distance: 0.0
All references consistent.
```

`Average self-distance: 0.0` is suspicious. Inspection of
`prune_cmd()` showed the bug: each ref was matched against
the full pool *including itself*, so the best distance was
always 0 (the ref matching itself), the average was 0, and
no outlier ever exceeded `2 × avg = 0`. The tool always
reported "consistent" regardless of pool quality.

### Fix

Python-only — no Swift / `face_compare` binary changes. New
flow per ref:

1. Build a temporary directory.
2. Symlink every OTHER ref's `(.json, .fpdata, .jpg)` triple
   into the tempdir, skipping the target ref itself.
3. Run `face_compare match <target.jpg> <tempdir>`. The
   resulting best-distance is the target ref's
   leave-one-out nearest-neighbor score.
4. Clean up symlinks + tempdir in `finally`.

After scoring all refs, compute the average, flag refs
whose score exceeds `PRUNE_OUTLIER_MULTIPLIER × avg`
(default 2.0).

### Files modified

- `face_sentinel.py`:
  - +1 module-top constant: `PRUNE_OUTLIER_MULTIPLIER = 2.0`.
  - +1 pure helper: `_outliers_from_scores(scores, multiplier)`.
  - +1 IO helper: `_prune_score_one(target_meta, all_metas)`.
  - `prune_cmd()` rewritten to call the new helpers and emit
    the leave-one-out average + outlier table with guidance.

### Files added

- `test/test_prune_logic.py` — 10 assertions on
  `_outliers_from_scores` covering empty / no-outlier /
  single-outlier / multiple-outliers / boundary (`>` not
  `>=`) / custom-multiplier / single-element cases plus
  the default-multiplier value lock.
- `docs/lazarus_prune_v0_1_3_companion.md` — this file.

### Files updated

- `LAZARUS_SPEC.md` — LZ-014 entry under a new v0.1.3
  section. Counts updated.
- `artifact_registry.md` — LZ-014 row added; counts (14 / 0
  / 4 / 0 / 0 / 7 / 3) and A1–A6 self-check refreshed.
- `.github/workflows/test.yml` — fourth test step.
- `dashboard.md` — status summary, recent-completed.
- `changelog.md` — v0.1.3 entry at top.

### Dependencies

None added. `tempfile` and `os.symlink` are Python stdlib.
The Swift binary stays as-is.

### Build / test commands

```bash
bash test/test_oversight_action.sh
python3 test/test_network_monitor_classify.py
python3 test/test_liveness_check.py
python3 test/test_prune_logic.py
```

All four PASS as of this session, locally and on
`macos-latest` CI.

## §2 — Results

### §2.1 — Algorithm correctness

The pure helper `_outliers_from_scores` is exercised by 10
assertions:

- Empty input → empty output.
- Tight cluster of 4 values around 5.0 → no outliers.
- Cluster of 4 values + one at 10× → single outlier flagged.
- Cluster of 3 values + two at 10× → both outliers flagged.
- Boundary case where `score == 2 × avg` exactly → strict
  `>` excludes it (NOT flagged).
- Custom multiplier 1.5 → catches values closer to the
  average.
- Single-element pool → no outliers (a value cannot exceed
  any multiplier > 1.0 of itself).

The strict `>` (not `>=`) boundary semantics is documented
in the test as `at_boundary_not_outlier`. A ref scoring
*exactly* at the threshold is treated as just-barely-OK.
This avoids flagging the edge of the cluster as outliers
when the multiplier happens to align with the data.

### §2.2 — Real-pool sweep

After the v0.1.3 implementation landed, ran the fixed
`--prune` against the live 50-ref pool:

```
50 references. Testing quality (leave-one-out)...
  scored 10/50
  scored 20/50
  scored 30/50
  scored 40/50
  scored 50/50
Average leave-one-out nearest-neighbor distance: 0.35
All references consistent.
```

**Average 0.35** in the Apple Vision feature-print distance
scale. Context:
- Match threshold: 18.0 (refs scoring above this against a
  query are not considered the same person).
- Uncertain band: 18.0–25.0.
- Hard mismatch + screen-lock: > 35.0.

A leave-one-out average of 0.35 means the pool is internally
*very* coherent: every ref has at least one near-twin in the
pool, and the gap to that twin is tiny compared to the match
threshold. Consequence: no refs warrant retirement on
quality grounds. The 12 fresh kitchen-background captures
fit cleanly with the existing 38-ref distribution.

### §2.3 — Why the algorithm cannot auto-delete

Reports-only is a deliberate design choice. The algorithm
flags refs whose nearest non-self neighbor is unusually far,
but it cannot distinguish two cases:

- **Genuine off-distribution ref.** A different person, an
  occluded face, a corrupted capture. These hurt match
  quality and should be retired.
- **Legitimate rare-condition ref.** A capture under unusual
  but valid conditions (extreme low light, profile angle,
  glasses-off when the rest of the pool wears glasses).
  These *improve* coverage by extending the matcher's
  acceptable range.

Both look identical to the algorithm — both are far from
their nearest neighbor. The human reviews the captured
`.jpg` files (visible in `~/.face_sentinel/reference/`) to
decide which is which.

## §3 — Verification

### §3.1 — `_outliers_from_scores` (LZ-014, pure math)

Test artifact: `test/test_prune_logic.py`. 10 assertions on
the pure helper, plus the default-multiplier value lock.
PASS on macOS Darwin 25.4.0 with system Python 3.

### §3.2 — `_prune_score_one` (LZ-014, IO wrapper)

Manual evidence — IO-bound (subprocess to `face_compare`,
tempdir + symlink construction). Real-pool sweep above
(§2.2) is the working evidence: 50 leave-one-out matches
ran without infrastructure failure, all returned valid
distances, the per-ref tempdir cleanup left no leftover
artifacts in `/tmp/`.

Failure-mode check: if `face_compare` returns an error, the
helper returns `999.0` (treated as outlier and surfaced).
This is the right default — surface the failure to the
human rather than silently exclude.

### §3.3 — `prune_cmd` integration

Manual evidence per §2.2. The flow is straightforward:
sort refs by mtime, score each via `_prune_score_one`, run
`_outliers_from_scores` on the result, format output.
Progress reporting fires every 10 refs to keep the user
informed during the (~30s for 50 refs) sweep.

### §3.4 — Self-audit (A0 / A1–A6)

- **A0** — `CLAUDE.md` claims still match observable
  practice (now 14 entries, 4 tested).
- **A1** — All 14 LZ-IDs in `LAZARUS_SPEC.md` have rows in
  `artifact_registry.md`.
- **A2** — Logic tier and Status fields match between spec
  and registry.
- **A3** — Tests cited at `test/test_*.{sh,py}` exist and
  run. Source files cited (`face_sentinel.py`, etc.) exist
  per `git ls-files`.
- **A4** — All `:tested` entries carry `example-tested`.
  All `:argued` entries carry `manual` or `example-tested`.
  All `:open` entries carry `none`.
- **A5** — Counts in spec, registry, dashboard all read
  14 / 0 / 4 / 0 / 0 / 7 / 3.
- **A6** — Four tests run on every push via
  `.github/workflows/test.yml` on `macos-latest`.

## §4 — Spec impact

One new entry:

| LZ-ID | Key | Logic tier | Evidence type | Status |
|---|---|---|---|---|
| LZ-014 | reference-pool leave-one-out pruning | Operational | example-tested | :tested |

No status changes to existing entries. The fix is
self-contained in `face_sentinel.py`'s prune path and does
not alter any other behavior. Match logic, watch loop,
liveness probe, and enroll path are all unchanged.

## §5 — Future work

- **Configurable multiplier via CLI.** `--prune
  --multiplier=1.5` for a stricter pass. Trivial to add
  when needed.
- **Auto-deletion mode (with confirmation).** A `--prune
  --delete` flag that retires confirmed outliers after a
  Y/N prompt per ref. Higher-stakes; held until the
  multiplier-tuning pattern stabilizes.
- **Pool-quality metrics over time.** Log the
  leave-one-out average to `~/.face_sentinel/sentinel.log`
  on each `--prune` run; trend over weeks gives an early
  signal that the pool is drifting (appearance change,
  haircut, glasses).
- **LZ-002 fixture set + LZ-014.** A small set of
  attack-vector reference files (different people, same
  person under attack conditions) would let LZ-002 (the
  18.0/25.0/35.0 distance bands) and LZ-014 (the outlier
  multiplier 2.0) graduate to a stronger evidence tier.
  Currently both are calibrated against a single
  developer's data.
