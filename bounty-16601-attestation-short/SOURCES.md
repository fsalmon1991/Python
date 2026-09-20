# Source Map

All RustChain technical claims in this package are pinned to public repository commit:

`217ba85ef9cab3daac0da7b822c79437693444df`

This avoids silently changing the factual basis if upstream documentation changes later.

## Source 1 — Attestation flow

https://github.com/Scottcjn/Rustchain/blob/217ba85ef9cab3daac0da7b822c79437693444df/docs/attestation-flow.md

Supports these narration claims:

- The attestation process is used to prove authentic physical hardware and enroll a miner.
- The client collects system information.
- The documented flow runs six hardware checks.
- It generates fingerprint JSON.
- The payload is signed with an Ed25519 key.
- The client submits to `POST /attest/submit`.
- The node verifies the signature.
- The node validates the fingerprint.
- The node checks for duplicate hardware / hardware already bound to another wallet.
- Valid and unique hardware can be enrolled.
- An antiquity multiplier is recorded/assigned as part of enrollment.
- The six documented validation areas are clock skew, cache timing, SIMD identity, thermal entropy, instruction jitter, and behavioral heuristics.

Relevant sections in the source:

- `Attestation Lifecycle`
- `What Miners Send`
- `Signature Generation`
- `Hardware Fingerprint Validation`
- `Duplicate Hardware Check`
- `Antiquity Multiplier Assignment`
- `Enrollment Process`

## Source 2 — API reference

https://github.com/Scottcjn/Rustchain/blob/217ba85ef9cab3daac0da7b822c79437693444df/docs/API_REFERENCE.md

Supports:

- `POST /attest/submit` is the documented attestation endpoint.
- The endpoint is described as submitting a hardware fingerprint for epoch enrollment.
- The API reference describes the purpose as validating genuine physical hardware rather than a VM.
- Authentication for this write endpoint is documented as an Ed25519 signature.

## Source 3 — Current multiplier implementation

https://github.com/Scottcjn/Rustchain/blob/217ba85ef9cab3daac0da7b822c79437693444df/cpu_architecture_detection.py

Supports:

- RustChain contains code for calculating an antiquity multiplier from CPU/hardware characteristics.

The Short intentionally does **not** quote a specific multiplier value because a single example value could be mistaken for a universal rate.

## Editorial clarification — not an upstream performance claim

Narration line:

> “That multiplier is a protocol weight. It is not a CPU speed benchmark, and it is not a guaranteed earnings rate.”

This sentence is deliberately a limitation/clarification rather than a claim that RustChain makes about performance. The source material uses the multiplier in enrollment/reward weighting; it does not establish that the numeric multiplier is a measured CPU speed ratio or a guaranteed financial return. The Short therefore avoids converting the documented multiplier into either claim.

## Bounty specification

https://github.com/Scottcjn/rustchain-bounties/issues/16601

Package C requires a ≤60-second script, vertical-format visuals or exact capture instructions, a hook line, and metadata. This repository directory supplies those deliverables plus this source map.
