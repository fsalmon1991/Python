# Storyboard — 9:16 Vertical Short

All shots can be produced from the cited public GitHub pages and simple original motion graphics. No third-party stock media is required.

## 0:00–0:04 — Hook

**Narration:** “RustChain does not treat ‘I’m on real hardware’ as enough by itself.”

**Visual:** Black background. Large centered text: `REAL HARDWARE? PROVE IT.` Fade in a small terminal-style label: `RustChain attestation`.

**Capture:** Original title card; no external asset.

## 0:04–0:13 — The attestation pipeline

**Narration:** “Its documented attestation flow collects system information, runs six hardware checks, builds a fingerprint, signs that payload with an Ed25519 key, and submits it to /attest/submit.”

**Visual:** Vertical flow animation with five stacked boxes:
1. Collect system info
2. 6 hardware checks
3. Fingerprint JSON
4. Ed25519 signature
5. `POST /attest/submit`

**Capture:** Recreate the sequence from `docs/attestation-flow.md` as original text/shape graphics. Do not screenshot unrelated UI.

## 0:13–0:22 — Node-side validation

**Narration:** “The node then verifies the signature, validates the fingerprint, and checks whether the same hardware is already bound to another wallet.”

**Visual:** Split screen. Left: signed payload icon. Right: three checkmarks appearing one at a time: `signature`, `fingerprint`, `duplicate hardware`.

**Capture:** Original diagram based on the sequence diagram in the cited source.

## 0:22–0:36 — Six checks

**Narration:** “The six documented checks cover clock skew, cache timing, SIMD behavior, thermal entropy, instruction jitter, and behavioral heuristics.”

**Visual:** 2×3 grid of labels, each appearing on beat:
- Clock skew
- Cache timing
- SIMD identity
- Thermal entropy
- Instruction jitter
- Behavioral heuristics

**Capture:** Use the six validation section headings from `docs/attestation-flow.md`. Keep descriptions off-screen to avoid overclaiming.

## 0:36–0:46 — Enrollment and multiplier

**Narration:** “Valid, unique hardware can be enrolled, and the flow records an antiquity multiplier for that miner.”

**Visual:** Green path: `VALID + UNIQUE → ENROLLED`. Under it: `multiplier: protocol weight`.

**Capture:** Recreate from the lifecycle diagram. Do not present the example `2.5` as a universal value.

## 0:46–0:54 — What the multiplier is not

**Narration:** “The important distinction: that multiplier is a protocol weight. It is not a CPU speed benchmark, and it is not a guaranteed earnings rate.”

**Visual:** Three rows:
- `Protocol weight` ✓
- `CPU speed benchmark` ✕
- `Guaranteed earnings` ✕

**Capture:** Original explanatory graphic. This is a clarification to prevent viewers from misreading the documented multiplier.

## 0:54–0:58 — Close

**Narration:** “RustChain’s design is trying to make hardware identity observable before reward weighting begins.”

**Visual:** Flow collapses to: `hardware evidence → identity check → weighting` with small footer `Sources: github.com/Scottcjn/Rustchain`.

## Editing notes

- Canvas: 1080×1920.
- Safe area: keep all critical text inside center 80% width and away from bottom 15%.
- Use monospace typography for endpoint/code labels.
- No logo is necessary; if the publisher uses a RustChain logo, source it only from the official repository/channel and confirm usage rights.
- Keep cuts fast enough for a Short but leave each of the six-check labels readable for at least ~1 second.
