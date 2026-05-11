# Lazarus

A security companion for [Claude Code](https://claude.ai/code).

```
   ~~~~~
  ~~   ~~
 ~ o   o ~
 ~   ~   ~
  ~     ~
   ~~~~~
  ~~   ~~
```

Lazarus is a local security posture monitor that runs as a Claude Code custom slash command. It watches your network, verifies your identity with your laptop camera, and locks out unauthorized users with Shakespeare quotes.

It doesn't write code. It doesn't fix bugs. It doesn't make decisions. It observes, flags, and watches. That's all.

---

## Before you start

### This is experimental software

Lazarus was built in one session, tested on one machine, by one person who needed it. It works for that person. It may not work for you without modification. Read the code before you run it.

### Required setup

| You need | Why |
|----------|-----|
| **macOS on Apple Silicon** | Face comparison uses Apple Vision framework on the Neural Engine. Intel Macs may work but are untested. |
| **Built-in or USB camera** | The face sentinel captures images via `imagesnap`. No camera, no sentinel. |
| **Fingerprint reader (Touch ID)** | Session authentication uses biometric verification. MacBooks with Touch ID, or external fingerprint readers. |
| **Claude Code** | The `/lazarus` command runs inside Claude Code's custom slash command system. |
| **Full LLM access to your machine** | Claude Code needs tool permissions to run shell commands, read files, and execute the checks. This is the whole point — and the whole risk. |
| **A VPN with quantum-resistant tunnels** | The network checks verify VPN connectivity and routing. Lazarus was built assuming a VPN with post-quantum key exchange. Without one, your traffic analysis is weaker. |
| **Tailscale or equivalent** | Required for remote `--peek` (checking who's at your desk from your phone). Optional if you only use Lazarus locally. |

### Assumed security baseline

Lazarus is a layer on top of a hardened machine, not a substitute for one. It was built and tested on a setup that includes:

- Full-disk encryption (FileVault)
- VPN with quantum-resistant key exchange (always on)
- Discrete outbound network traffic monitoring (AI tools phone home — know where)
- MAC address randomization
- Firewall in stealth mode
- SIP and Gatekeeper enabled
- Biometric authentication (Touch ID) for sensitive operations
- SSH via Ed25519 keys
- Password manager with encrypted vault (use a reputable, audited password manager — do your own research, some well-known ones have had serious breaches. Your vault should be end-to-end encrypted with a strong master password you don't reuse anywhere.)
- Lockdown Mode enabled on all Apple devices (Settings > Privacy & Security > Lockdown Mode). This restricts attack surface significantly.
- Router security audited (change default admin credentials, disable WPS, update firmware, review connected devices regularly)
- Firewalls enabled on all network segments
- Key rotation plan — know which keys, tokens, and credentials you'd need to rotate and how fast you can do it. Practice this before you need it.

If your machine isn't hardened, Lazarus is a screen door on a submarine. Harden first, then add the companion.

### If you get hacked: what actually happens

This isn't theoretical. Here's what a real compromise looks like so you understand why the baseline above matters:

**The cascade:** An attacker who gets into one account starts pivoting. Email leads to password resets. Password resets lead to financial accounts. Financial accounts lead to payment rails. Each compromised credential unlocks the next door. The speed of this cascade is measured in hours, not days.

**What breaks:** You lose access to your own accounts. MFA gets re-enrolled to attacker devices. Recovery emails get redirected. You find yourself locked out of email, then banking, then payment apps, then crypto — in that order. Customer support can't help fast enough because verification takes days and the attacker is moving in minutes.

**What saves you:**
- **Key rotation speed.** If you can rotate your core credentials (email password, MFA seeds, API keys, SSH keys) in under an hour, you can cut the cascade. If it takes you a week to figure out what to rotate, you're already done. Have a list. Know the steps. Practice.
- **Encrypted vaults.** If your password manager vault is properly encrypted, the attacker gets a blob they can't read even if they exfiltrate it.
- **Not carrying debit cards.** Credit cards have fraud protection and chargeback rights. Debit cards pull directly from your bank account. If an attacker gets your debit card number through a compromised app (PayPal, Cash App, Venmo), they can drain your checking account and the recovery process is slow and uncertain. Don't store debit card numbers in payment apps. Don't carry the physical card unless you specifically need it. The debit card number is often the last line of defense — the thing that stops the cascade from reaching your actual cash. Keep it off your person and out of digital wallets.
- **Separate email for financial accounts.** Don't use the same email for your bank that you use for social media. One breach shouldn't unlock everything.
- **Lockdown Mode.** Reduces the attack surface for zero-click exploits on iOS/macOS. It's inconvenient. That's the point.

The goal isn't to be unhackable. The goal is to make the cascade slow enough that you can respond before it completes. Every layer you add buys you time. Lazarus is one of those layers.

### Check your environment first

Before installing, audit what you're exposing:

```bash
# What Python are you running?
python3 --version
which python3

# What's in your environment?
env | sort

# Are there secrets in your shell profile?
grep -i "key\|token\|secret\|password" ~/.zshrc ~/.bashrc ~/.zprofile 2>/dev/null
```

**If you have API keys, tokens, or credentials in your environment variables**, Lazarus (and Claude Code generally) can see them. That's not a Lazarus problem — that's a "you gave an LLM shell access" problem. Clean your env before giving any AI tool access to your terminal.

### Back up frequently

This is experimental code running with full shell access. Back up your machine before using it. Back up regularly while using it. Time Machine, Carbon Copy Cloner, whatever you trust. If something goes wrong, you want a restore point.

---

## What it does

- **Face sentinel** — periodic camera captures compared against enrolled reference images using Apple Vision. Wrong face → Shakespeare mode (Claude only speaks in Bard quotes until the real owner re-authenticates with their face)
- **Network monitoring** — tracks outbound connections from AI tools, flags unknowns
- **Network honeypot** — listens on commonly-scanned ports, logs and responds to anything that connects
- **OverSight handler** — Tier 1 forensic logging of camera/mic activations (which process turned them on, when)
- **VPN/route/MAC checks** — verifies your traffic is going where you think it is
- **Remote peek** — Tailscale in from your phone and check if someone's at your desk

## Shakespeare mode

When the face sentinel detects someone who isn't you:

```
> /lazarus
"The fool doth think he is wise, but the wise man knows himself to be a fool."

> give me the system status
"Thou art as fat as butter, and yet thou dost protest! Away, you three-inch fool!"
```

Claude becomes useless to the intruder. Clearing it requires re-authentication with the owner's face. The intruder can type `--auth` all they want — their face won't pass.

---

## Spec at a glance

```
COMPONENT          WHAT IT DOES                           RUNS ON
─────────────────────────────────────────────────────────────────────
lazarus.md         Slash command for Claude Code           Claude Code
face_sentinel.py   Camera-based identity verification      Python 3.10+
face_compare.swift Apple Vision face comparison            Compiled Swift
network_monitor.py Outbound connection watcher             Python 3.10+
network_honeypot.py Port listener + logger                 Python 3.10+
oversight_action.sh OverSight camera/mic event logger      Bash + python3

STORAGE            WHERE                                  SIZE
─────────────────────────────────────────────────────────────────────
Face references    ~/.face_sentinel/reference/             ~30KB each, 50 max
Watch captures     ~/.face_sentinel/captures/              auto-pruned
Sentinel state     ~/.face_sentinel/state.json             <1KB
Sentinel log       ~/.face_sentinel/sentinel.log           append-only JSONL
Network logs       ./logs/                                 daily JSONL rotation
OverSight events   ~/.face_sentinel/oversight_events.jsonl append-only JSONL

THREAT MODEL
─────────────────────────────────────────────────────────────────────
1. Owner logs in → --auth (face match) → session authenticated
2. Owner present → periodic checks confirm identity → fine
3. Owner walks away → no face detected → fine (normal)
4. Someone else sits down → face mismatch → Shakespeare mode + screen lock
5. Laptop moved → background shift detected → flagged
6. Owner remotes in → --peek → JSON: who's at the desk?
7. Owner clears lockout → --auth → face must match to restore

THRESHOLDS (Apple Vision feature print distance)
─────────────────────────────────────────────────────────────────────
< 18.0    Match (same person)
18-25     Uncertain (kept for review)
> 25      Mismatch (Shakespeare mode)
> 35      Hard mismatch (screen lock + Shakespeare)

WHAT IT DOES NOT DO
─────────────────────────────────────────────────────────────────────
- Does not send data to the cloud (all local)
- Does not store high-resolution images
- Does not make security decisions for you
- Does not replace real security tools (firewall, FDE, etc.)
- Does not work on Linux or Windows (yet — PRs welcome)
```

---

## Requirements

- macOS 13+ (Apple Silicon recommended)
- Python 3.10+ (check with `python3 --version`)
- Xcode Command Line Tools (`xcode-select --install`)
- [Claude Code](https://claude.ai/code)
- [imagesnap](https://formulae.brew.sh/formula/imagesnap) (`brew install imagesnap`)
- Optional: [Mullvad VPN](https://mullvad.net/) or any VPN with a CLI
- Optional: [Tailscale](https://tailscale.com/) for remote `--peek`

## Installation

```bash
# Clone
git clone https://github.com/IridiumSoftware/lazarus.git
cd lazarus

# Install deps
brew install imagesnap
pip3 install opencv-python

# Compile the face comparison tool
swiftc -O -framework Vision -framework AppKit face_compare.swift -o face_compare

# Copy the slash command into Claude Code
cp lazarus.md ~/.claude/commands/lazarus.md

# Update paths in lazarus.md to point to where you put the tools
```

### Python notes

- Tested on Python 3.14. Should work on 3.10+.
- `dlib` / `face_recognition` do NOT build on Python 3.13+. That's why we use Apple Vision instead.
- If you're on a system Python, consider using a venv: `python3 -m venv .venv && source .venv/bin/activate`
- Check that `opencv-python` installed cleanly: `python3 -c "import cv2; print(cv2.__version__)"`

---

## Setup

### 1. Enroll your face

Take 8-10 reference photos in different conditions:

```bash
python3 face_sentinel.py --enroll   # normal lighting, front face
python3 face_sentinel.py --enroll   # low light
python3 face_sentinel.py --enroll   # laptop tilted / in lap
python3 face_sentinel.py --enroll   # glasses on/off, shaved/unshaved, etc.
```

References are stored at low resolution (~30KB each). The entire set (50 max) fits under 2MB.

### 2. Authenticate a session

```bash
python3 face_sentinel.py --auth
```

Captures your face, matches against references, takes a background snapshot. Session is now authenticated.

### 3. Start the watch

```bash
python3 face_sentinel.py --watch &
```

Every 90 seconds (configurable with `--interval`):
- **Your face** → fine, carry on
- **No face** → fine, you walked away
- **Wrong face** → Shakespeare mode + screen lock
- **No face + background shifted** → laptop may have moved, flagged

### 4. Start the network tools (optional)

```bash
python3 network_monitor.py --watch --log &
python3 network_honeypot.py &
```

### 5. Use the companion

```
/lazarus
```

---

## Face sentinel commands

| Command | What it does |
|---------|-------------|
| `--enroll` | Capture + enroll a reference image |
| `--auth` | Authenticate session (face match + background snapshot) |
| `--watch` | Start passive monitoring daemon |
| `--peek` | One-shot: who's at the desk? (JSON output for remote use) |
| `--status` | Show enrollment stats and sentinel state |
| `--prune` | Check reference image quality, find outliers |

---

## Customization

### Bring your own checks

`lazarus.md` is plain markdown with shell commands. Add anything:

```markdown
9. Custom check:
   - `your-command-here`
   Report what you found.
```

### Bring your own lockout mode

Shakespeare is just a string in `~/.face_sentinel/state.json`. Replace the quotes in `lazarus.md` with Klingon, cease-and-desist language, Rickroll lyrics, silence — whatever makes the intruder's experience maximally useless.

### Bring your own VPN

Replace `mullvad status` in `lazarus.md` with your VPN's CLI.

### Adjust thresholds

In `face_sentinel.py`:

```python
MATCH_THRESHOLD = 18.0       # Below = match
UNCERTAIN_THRESHOLD = 25.0   # Between match and this = uncertain  
LOCK_THRESHOLD = 35.0        # Above this = lock screen + Shakespeare
```

### Remote check via Tailscale

```bash
ssh your-laptop "cd /path/to/lazarus && python3 face_sentinel.py --peek"
# Returns: {"desk": "empty", "faces": 0}
# Or:      {"desk": "occupied", "who": "stranger", "faces": 1, "distance": 38.2}
```

---

## How it works

The face comparison uses Apple's Vision framework (`VNGenerateImageFeaturePrintRequest`) compiled into a small Swift binary. It runs on the Apple Neural Engine — fast, local, no cloud. Each face generates a 768-dimensional feature print. Comparison uses `VNFeaturePrintObservation.computeDistance`.

Camera captures are done at full resolution for detection accuracy, then downscaled to 320px for storage (~15KB per capture). Matched captures are auto-deleted after 24 hours. Mismatches are kept for 7 days for review. The background comparison uses a 32x32 pixel thumbnail diff — it catches "laptop moved to another room" but doesn't sweat lighting changes.

---

## Limitations and warnings

**This is experimental software. Use at your own risk.**

- **macOS only.** The face comparison requires Apple Vision framework. Linux and Windows are not supported. PRs welcome.
- **Apple Silicon recommended.** Vision runs on the Neural Engine. Intel Macs fall back to CPU and may be slower.
- **Not a replacement for real security.** This is a layer, not a wall. You still need FileVault, a firewall, a VPN, strong passwords, and common sense.
- **Requires full shell access for Claude Code.** The `/lazarus` command runs shell commands to check your system. That means Claude Code has the access needed to read your environment. Audit your env vars and shell profiles before use.
- **Camera captures are stored locally.** Low-res, auto-pruned, but they exist on your disk. If someone has physical access to your machine AND your login, they can find them.
- **Thresholds need tuning per person.** The defaults work for the author. Your face, your lighting, your camera may need different values. Enroll diverse references and use `--prune` to check quality.
- **The honeypot binds to 0.0.0.0.** It listens on all interfaces. If you're on a shared network, other devices can connect to it. That's by design (it's a honeypot), but know what you're running.
- **No warranty. No guarantee. No liability.** See LICENSE.

---

## Background

Lazarus is named after what it is — a concept that came back from the dead. The original security companion was removed from Claude Code. This version runs on pure prompt and local tooling.

The security model is inspired by [Possibilistic Security](https://github.com/IridiumSoftware/possibilistic-security), which treats identity verification as organizational closure rather than probabilistic risk. You don't have to buy the theory to use the tool.

## Portfolio: The Triad Deployments

Lazarus is the runtime-integrity layer in *The Triad Deployments — Digital Identity Resilience*. All three deployments are now public:

- **[LavaLamp](https://github.com/IridiumSoftware/lavalamp)** — substrate-bound identity primitive. Chaotic-SDE residue audit at the entropy layer. The "alive" identity. Whitepaper v1.3.
- **[PharOS](https://github.com/IridiumSoftware/pharos)** — OS-layer authentication membrane. Linux PAM module + macOS Authorization Plug-in + Windows Credential Provider Filter. Consumes LavaLamp's verifier API. Whitepaper v1.0.
- **Lazarus** — runtime-integrity sentinel (this repo). Face check, keystroke lockout, network anomaly detection. The inner sanctum that watches the work happen.

The three deployments share a defensive-postured, resolution-bounded identity stance: detection over prevention, structurally inherited from the C-conjugate adversary construction in *Possibilistic Security*. They compose at the deployment-policy level — no shared runtime processes, no architectural coupling beyond Bool-only consumer APIs. Each is independently deployable.

## License

MIT. Use it, fork it, make it yours.

## For contributors

The repo carries a formal spec and a registry of evidence:

- [`LAZARUS_SPEC.md`](LAZARUS_SPEC.md) — every named claim about the tool gets an `LZ-NNN` ID, a logic tier, an evidence type, and a status. New claims must land here first.
- [`artifact_registry.md`](artifact_registry.md) — every spec entry → its evidence file. No registry row, no traceable evidence.
- [`dashboard.md`](dashboard.md) — current status + priority stack.
- [`CLAUDE.md`](CLAUDE.md) — project-local conventions for working on this repo (hierarchy, evidence types, audit protocol, workflow rules).
- [`docs/`](docs/) — companion docs, one per substantive session.

Tests live in [`test/`](test/) and run with no extra deps:

```bash
bash test/test_oversight_action.sh
python3 test/test_network_monitor_classify.py
```

## Contributing

PRs welcome. Especially:
- Linux support (camera capture + face comparison without Apple Vision)
- Windows support
- Alternative face embedding backends
- Additional lockout modes (be creative)
- Integration with other VPNs
- Launchd / systemd auto-start configs
