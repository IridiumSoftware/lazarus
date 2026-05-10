# CLAUDE.md — Lazarus

## Project identity

A local visual-presence + network-posture security companion for
Claude Code. The face sentinel performs camera-driven identity
verification using Apple Vision feature prints; on mismatch, the
`/lazarus` slash command shifts into Shakespeare mode (the LLM
responds only with Bard quotes), denying productive use to the
intruder. The network monitor watches outbound connections from
AI tools; the honeypot listens on commonly-scanned ports and
logs probes; the OverSight handler forensically logs every
camera/mic activation.

Lazarus is the most-mature of the three Triad Deployments
(LavaLamp, Lazarus, PharOS — see the LavaLamp repo's
threat-landscape companion). It was built in one session, runs
locally on macOS, and depends on the Apple Neural Engine for
face comparison — *no cloud component*.

**Status (2026-05-10).** v0.1.0 — public release backed by the
standard rigor stack. 12 LZ-NNN spec entries, 2 `:tested`
(LZ-009, LZ-011), 7 `:argued`, 3 `:open`. Tests run locally
via `bash test/test_oversight_action.sh` and
`python3 test/test_network_monitor_classify.py`. CI not yet
wired.

**Owner:** Aaron Green.

## Orientation

Read `dashboard.md` first, every session — status summary,
priority stack, open questions. Start with `git status` to
confirm a clean working directory; if not, commit or stash
before starting new work.

For claim status, see `LAZARUS_SPEC.md` directly. For history,
`changelog.md` or `git log`. For the file inventory,
`git ls-files`.

## Ground truth hierarchy

1. **`LAZARUS_SPEC.md`** — Formal spec. Every named claim
   about Lazarus (a behavior, an architectural invariant, a
   security property, a forensic-logging guarantee) gets an
   LZ-ID, a logic tier, an evidence type, and a status. If
   it's not in the spec, it's not established.

2. **`artifact_registry.md`** — Maps every spec entry to its
   evidence file. No registry row → no traceable evidence.

3. **`README.md`** — User-facing artefact. Describes what the
   tool does, how to install it, and the threat model. Does
   not encode formal claims; the spec does.

4. **Test suites** — `test/`. Failures are spec-consistency
   failures, not just code failures. A test that lapses to
   skipped or `xfail` requires a spec status downgrade.

5. **`dashboard.md`** — Current status + priority stack. No
   scorecard copy — that lives in the spec only.

6. **Companion docs** — `docs/*_companion.md`. Permanent
   record of each substantive session.

7. **Everything else** — Source files, slash command, build
   notes. Supporting.

## Evidence types

Every spec entry must declare what kind of justification
supports it.

| Type | Meaning | Sufficient for `:proved`? |
|------|---------|---------------------------|
| **lean-proved** | Machine-verified Lean4 proof | Yes |
| **type-checked** | Property enforced by a type system (Swift, Haskell) | Yes |
| **algebraic** | Symbolic / exact-arithmetic proof | Yes |
| **property-tested** | Generative property test passes | No → `:verified` |
| **example-tested** | Hand-written test case passes | No → `:tested` |
| **benchmarked** | Performance target met by recorded benchmark | No → `:benchmarked` |
| **manual** | Human inspection or written argument | **No** → `:argued` only |
| **none** | Claim exists, no verification yet | No → `:open` |

**Rule.** A spec entry may have `status: :proved` only if its
evidence type is `lean-proved`, `type-checked`, or `algebraic`.

## Language tooling

- **Python 3.10+** — face_sentinel, network_monitor,
  network_honeypot, plus all Python tests. No external runtime
  dependencies; standard library only. (`opencv-python` is
  listed in the README install steps but is not currently
  imported by any v0.1.0 code path — safe to drop in a future
  cleanup.)
- **Swift** — `face_compare.swift`, compiled via `swiftc -O
  -framework Vision -framework AppKit`. Output binary
  `face_compare` is gitignored; users compile locally.
- **Bash** — `oversight_action.sh`, plus shell tests.
- **macOS only** — Apple Vision is the face-comparison
  backend; Linux / Windows are out of scope (PRs welcome per
  README).

## Package management discipline

Lazarus has zero runtime dependencies beyond what ships with
macOS + `imagesnap` (Homebrew). There's no `requirements.txt`,
no `Package.swift`, no lockfile to maintain — by design.
External-dependency growth would be a regression on the
"runs locally with no surprises" property and should be
justified in a companion doc.

## Code commenting standard

Every source file producing a result referenced by the spec
must be self-documenting for its conventions. Specifically:

1. **Conventions in force** — distance thresholds, file paths,
   process-name / hostname allowlists. The actual numbers
   should be `CAPS_CONSTANTS` at the top of each file with a
   comment explaining the value.
2. **Why this primitive set** — face vs. fingerprint vs.
   keystroke; HTTP/SSH/FTP/MySQL ports vs. some other set.
   When the choice is non-obvious, a comment explains.
3. **Performance-critical assumptions** — `imagesnap` is a
   subprocess, `face_compare` is a subprocess. Latency budget
   is comfortable (~90s watch interval) so subprocess
   overhead is fine.
4. **API stability** — `lazarus.md` is the slash-command
   contract; it is **STABLE**. The Python/Swift internals are
   **EXPERIMENTAL** — their shapes can change.

## Artifact registry rules

The artifact registry (`artifact_registry.md`) bridges spec to
evidence:

1. **Coverage** — every spec entry has a registry row.
2. **Columns** — LZ-ID, Key, Logic tier, Evidence Type,
   Test/Proof file, Source file, Status.
3. **Consistency** — Logic and Status must match
   `LAZARUS_SPEC.md` exactly. Key column may compress for
   table readability; LZ-ID is the canonical link.
4. **No orphans** — every referenced file exists in
   `git ls-files`.

## Cross-audit protocol

Cross-audits catch drift between spec, registry, code, and
dashboard. Run when integrating substantial new work or
preparing a release.

| Check | What to verify |
|---|---|
| **A0 — Self-audit** | Every claim *this CLAUDE.md* makes about how Lazarus operates matches observable practice. Drift is fixed here, not in the project. |
| **A1 — Coverage** | Every LZ-ID has a registry row. |
| **A2 — Logic & Status parity** | Logic tier and Status match the spec exactly. Key may compress. |
| **A3 — Evidence exists** | Every Test/Proof and Source file in the registry exists. |
| **A4 — Status honesty** | No entry has a status its evidence type can't support. |
| **A5 — Stale counts** | Counts cited in dashboard match the spec. |
| **A6 — Test sync** | Every spec entry with a Test/Proof file is exercised by a test that runs. |

## Companion doc standard

Every substantive session produces a companion doc in `docs/`.
The companion is the permanent record — chat history is
ephemeral. If a design decision was made in conversation but
not captured in the companion, it does not exist.

**§1 — Computational basis.** What was built or run, with
files, dependencies, and test data.

**§2 — Results.** What was found. Precise.

**§3 — Verification.** For each result destined for the spec,
state which evidence type applies and the artifact establishing
it.

**§4 — Spec impact.** Proposed LZ-ID, Key, Logic tier,
Evidence type, Status.

## Workflow rules

- **One task per conversation.** Don't combine discovery with
  integration.
- **The spec is ground truth.** Conflicts get resolved toward
  the spec.
- **Honest framing.** "Type-checked" beats "proved" when types
  are the only enforcement. "Tested at one fixture set" beats
  "scales to all inputs."
- **Stubs that return data are forbidden.** Unimplemented
  functions must `raise NotImplementedError` or `error`, not
  return placeholder values.
- **Test before committing.** A commit must compile and pass
  the test suite for any component it touches.
- **Default to push after each user-review checkpoint.** This
  repo has an online presence (github.com/IridiumSoftware/
  lazarus); local-only commits are a regression on
  "discoverable progress."

## After completing a task

Two tiers, depending on what the session changed:

**Small session** (bugfix, comment pass, single small feature):
1. Tests pass for the touched component.
2. `dashboard.md` updated *only if* the project state changed
   materially.
3. Companion doc written *only if* the work warrants permanent
   record.
4. `git commit` with specific files staged (never blind
   `git add -A`).

**Large session** (adds spec entries, introduces a primitive,
materially changes the public API):
1. **`LAZARUS_SPEC.md`** — add or edit entries.
2. **Tests** — add or update tests; run them; all must pass.
3. **`artifact_registry.md`** — add rows; verify evidence
   type and status.
4. **`dashboard.md`** — update priority stack and status
   summary.
5. **`changelog.md`** — versioned entry at the top.
6. **Companion doc** — `docs/<topic>_companion.md`.
7. **`git commit`** — message matches the changelog entry.

The default is small; promote to large only when the trigger
criteria genuinely apply.

## Key principles

- **Lazarus is a watchful companion, not an enforcement
  layer.** Shakespeare mode and read-only discipline are
  prompt-layer protocols. Defensive value comes from raising
  the bar on intruder productivity, not from technically
  preventing model output.
- **Local-only.** No cloud component, ever. Apple Vision
  on-device, log files in `~/.face_sentinel/` and `./logs/`,
  no telemetry.
- **The spec captures what is established, not what is
  aspirational.** A planned test goes in `dashboard.md`'s
  priority stack; the corresponding spec entry stays `:open`
  until the test exists.
- **Build our own when the dependency cost exceeds the
  implementation cost.** Lazarus has no runtime deps beyond
  macOS + imagesnap. Adding any is a documented decision.

## What not to do

- Don't modify `LAZARUS_SPEC.md` without explicit instruction
  or a clear derivation from the session's results.
- Don't conflate evidence types. `example-tested` is not
  `lean-proved`.
- Don't return placeholder values from unimplemented
  functions.
- Don't commit build artifacts. `.gitignore` covers the
  `face_compare` binary, `.paper-index.json`, and `logs/`.
- Don't add spec entries without registry rows.
- Don't call a result "proved" unless its evidence type is
  `lean-proved`, `type-checked`, or `algebraic`. Use honest
  language.
