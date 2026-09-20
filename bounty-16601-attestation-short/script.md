# Narration Script

**Target:** 55–58 seconds at roughly 125–135 words per minute.

> RustChain does not treat “I’m on real hardware” as enough by itself.
>
> Its documented attestation flow collects system information, runs six hardware checks, builds a fingerprint, signs that payload with an Ed25519 key, and submits it to `/attest/submit`.
>
> The node then verifies the signature, validates the fingerprint, and checks whether the same hardware is already bound to another wallet.
>
> The six documented checks cover clock skew, cache timing, SIMD behavior, thermal entropy, instruction jitter, and behavioral heuristics.
>
> Valid, unique hardware can be enrolled, and the flow records an antiquity multiplier for that miner.
>
> The important distinction: that multiplier is a protocol weight. It is not a CPU speed benchmark, and it is not a guaranteed earnings rate.
>
> RustChain’s design is trying to make hardware identity observable before reward weighting begins.

## Narration QA

- No invented benchmark numbers.
- No claim that a multiplier guarantees profit.
- No claim that the documented checks are impossible to spoof; the script only describes the published flow.
- All technical statements are mapped in `SOURCES.md`.
