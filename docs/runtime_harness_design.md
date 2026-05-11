# Runtime LLM-Behavior Harness — Design

Date: 2026-05-11. Owner: Aaron Green.

## Context

By v0.1.15 lazarus carries 19 LZ-NNN spec entries: 3 lean-proved
(LZ-016 outliers, LZ-017 liveness metric, LZ-018 priority
dispatcher) and 16 tested. Four of those tested entries are
*prompt-layer* claims — they assert that the `/lazarus`
companion behaves a certain way at runtime, but the test
evidence is a static lint on the prompt-source files:

| Entry | Runtime claim | Static evidence |
|---|---|---|
| **LZ-001** | Visual skin can be swapped without changing the security state machine | Producer/consumer architecture lint (`test_visual_skin_decoupling.py`) |
| **LZ-003** | `mode=="shakespeare"` causes the LLM to refuse diagnostics and emit only Bard quotes | Six-layer prompt-contract lint (`test_shakespeare_mode_refusal.py`) |
| **LZ-004** | `--auth` flips state back to normal and the next `/lazarus` invocation reads it | State-machine drive against stubbed dependencies (`test_auth_clears_shakespeare.py`) |
| **LZ-012** | The companion does not write code / commit / change settings | Six-prohibition lint + counter-positive permissive-language scan (`test_companion_readonly_discipline.py`) |

Each test catches the failure mode "developer refactored the
prompt and accidentally weakened a directive." None of them
catches the failure mode "the LLM ignored the prompt anyway."

This design doc explores how to close that gap honestly.

## What "runtime" means here

`/lazarus` is a Claude Code *slash command*. The runtime
environment is:

1. The Claude Code agent loop (model + tool dispatcher +
   conversation history).
2. The `lazarus.md` prompt loaded into the system slot.
3. The state file at `~/.face_sentinel/state.json` that the
   prompt instructs the model to read first.
4. The tools the agent has registered (Bash, Read, Edit,
   etc.).

The runtime claim is: given (2) + (3) saying `mode:
"shakespeare"`, when (4) makes a Bash tool available, the
model should NOT call Bash and should instead emit a
Shakespeare quote.

Testing this faithfully requires replicating (1)–(4) end-to-
end. The Anthropic API alone reproduces (2) + a synthetic
user message, but not the Claude Code agent loop or the tool
dispatcher in their lazarus-specific configuration.

## Three approaches

### A. Recorded-transcript audit

**Mechanism.** Manually run `/lazarus` against fixture
state.json files, capture the transcripts, save them as
files under `test/transcripts/`. A Python test reads the
transcripts and asserts on content (Shakespeare vocabulary
present, status fields absent for Shakespeare-mode; reverse
for normal-mode).

**Pros.**
- Zero cost per CI run.
- Tests the ACTUAL runtime — every byte in the transcript
  came from a real /lazarus session with the real Claude
  Code agent loop, tools, and lazarus.md prompt.
- Reusable: a single transcript can satisfy multiple
  assertions (Shakespeare quotes + absence of Bash tool
  calls + absence of diagnostic data).
- Honest failure mode: when the prompt changes, the test
  needs the transcript refreshed. The staleness is visible
  in `git log`.

**Cons.**
- Transcripts are point-in-time. They don't catch
  regressions from model updates between captures.
- Manual capture is friction. Requires Aaron to actually
  run /lazarus and save the output when refreshing.
- Privacy: real transcripts contain network/auth data that
  needs scrubbing before committing.

**When this is the right choice.** When the prompt is
stable and the goal is "lock the existing behavior so a
refactor doesn't accidentally break it." Refresh cycle
roughly matches the prompt-change cycle.

### B. Anthropic API integration test

**Mechanism.** Use `anthropic.messages.create` with
`lazarus.md` as the system prompt + a synthetic user message
("system status please") + a tool spec mimicking Bash.
Assert on the response: contains Shakespeare-mode vocabulary,
doesn't invoke the Bash tool.

**Pros.**
- Live evidence — each CI run gets a fresh response from
  the current model.
- Catches model-update drift: if Anthropic ships a model
  that ignores Shakespeare refusal directives, the test
  catches it immediately.
- No manual transcript capture.

**Cons.**
- Non-deterministic. LLM outputs vary; assertions must be
  shape-based, not literal. False positives possible.
- API costs per CI run (~$0.01–$0.05 with Opus pricing).
- CI complexity: needs `ANTHROPIC_API_KEY` secret.
- **API context ≠ Claude Code context.** The
  `messages.create` invocation doesn't include the agent
  loop, the slash-command framing, or the precise tool-
  dispatch behavior. The test would prove "Claude respects
  this system prompt" but not "the lazarus slash command
  works."
- Probabilistic flakiness: with ~5% intrinsic non-
  determinism, even a well-aligned test fails occasionally.
  Requires retry logic or probabilistic assertions.

**When this is the right choice.** When the load-bearing
concern is "the model itself drifts," not "the prompt
drifts." Useful as a canary that runs nightly rather than
per-push.

### C. Probabilistic property suite

**Mechanism.** Run approach B `N` times (e.g., 5–10), assert
that ≥M succeed (e.g., 8 out of 10). Statistical control
over the ~5% intrinsic LLM non-determinism.

**Pros.**
- Most rigorous statistical evidence for the live runtime
  claim.

**Cons.**
- N× the cost and time of approach B.
- Still doesn't close the API-vs-Claude-Code-context gap.
- Adds CI brittleness — flakes are mathematically expected
  even when the system is healthy.

**When this is the right choice.** When the runtime claim
is load-bearing for downstream regulatory / audit purposes.
Not the case for lazarus today.

## Recommended path — staged

**v0.1.16 (proposed).** Ship approach A as a stub. Capture
2–3 redacted transcripts from a real /lazarus session
(Shakespeare mode + normal mode + maybe a read-only-
discipline check where someone asks the companion to write
code). Test asserts on transcript shape. Documented
limitation: transcripts are point-in-time; refresh on
prompt changes.

This gives lazarus a runtime-LLM-behavior `:tested` entry
without committing to API costs or non-determinism. It's
honest evidence for the conservative claim "this prompt
DID work this way in a real session."

**Future v0.1.NN (if needed).** If the prompt-contract +
recorded-transcript layers prove inadequate — e.g., a
real-world refactor lands the prompt in a state where the
static lint passes but the model actually misbehaves — add
approach B as an opt-in `nightly` workflow. Gate on
`ANTHROPIC_API_KEY`; skip cleanly in normal CI.

Approach C is not recommended for lazarus. The cost and
flakiness overhead exceed the load-bearing-ness of the
runtime claim. lazarus is a single-developer companion; the
strict-audit use case is more LavaLamp / PharOS territory.

## Honest framing for the spec

When LZ-020 lands at `:tested` via approach A, the spec
entry should state:

> Evidence: example-tested. Transcripts under
> `test/transcripts/` are real /lazarus session outputs
> from a specific date; the test asserts on their content
> (Shakespeare vocabulary present, no diagnostic data
> leakage for Shakespeare-mode transcripts; status fields
> present, no Bard vocabulary for normal-mode transcripts).
>
> Honest scope: this evidence is point-in-time. Model
> updates after the capture date can introduce drift; this
> test will not catch them. Refresh the transcripts when
> the prompt changes, and consider an API-based runtime
> harness if model-drift becomes a load-bearing concern
> (see `docs/runtime_harness_design.md` Approach B).

The "point-in-time" caveat is the key honest framing — it
prevents the test from being read as a stronger guarantee
than it is.

## Privacy considerations

`/lazarus` normal-mode output includes:
- LAN-IPs of the test machine
- MAC address surface (factory vs randomized)
- VPN relay location + provider
- Mullvad route info
- Sentinel auth state + last-mismatch timestamps

This is operational data. Before committing transcripts to
the public lazarus repo, network values get redacted to
placeholders (`192.168.x.x`, `<RELAY>`, etc.). The
assertions check for the SHAPE (presence of the field
labels) and the absence of Shakespeare vocabulary, not the
specific values.

## What this design does NOT promise

- **Does not test the slash-command framing.** Claude Code
  slash commands have unique loading semantics (system
  prompt position, tool registry, conversation prefix).
  Approach A is the closest because the transcripts were
  produced by the actual slash command; approach B would
  require reproducing this framing manually.
- **Does not catch silent model drift.** Approach A
  captures a moment; the next model update could shift
  behavior subtly while the transcript test still passes.
- **Does not prove safety.** Refusal-when-Shakespeare is
  a *defensive* behavior, not a *safety* property. The
  defense is at the prompt-layer and is bypassable by an
  attacker who can edit the state file or the prompt.

## Recommendation

Ship approach A as v0.1.16 with the honest caveats. Revisit
approach B if and when prompt-contract drift becomes a
real-world failure mode.
