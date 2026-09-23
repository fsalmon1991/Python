# Sources and claim map

Reviewed upstream snapshot: `Scottcjn/rustchain-dos-miner` at commit `7fc1d136bfe6fadce6bdca7df112deb00435ee66`.

## Claim 1 — target hardware families
**Claim:** The DOS “Fossil Edition” targets 8086/286/386/486/Pentium DOS systems.

Primary source:
- https://github.com/Scottcjn/rustchain-dos-miner/blob/7fc1d136bfe6fadce6bdca7df112deb00435ee66/README.md

Corroborating source-code header:
- https://github.com/Scottcjn/rustchain-dos-miner/blob/7fc1d136bfe6fadce6bdca7df112deb00435ee66/rustchain_dos_miner.c

## Claim 2 — 640 KB minimum
**Claim:** The README lists 640 KB conventional memory minimum.

Source:
- README `Requirements → Hardware`: https://github.com/Scottcjn/rustchain-dos-miner/blob/7fc1d136bfe6fadce6bdca7df112deb00435ee66/README.md

## Claim 3 — project-documented antiquity multipliers
**Claim:** The README’s table lists:
- 8086/8088 — 4.0×
- 286 — 3.8×
- 386 — 3.5×
- 486 — 3.0×
- Pentium — 2.5×

Source:
- README `Antiquity Multiplier`: https://github.com/Scottcjn/rustchain-dos-miner/blob/7fc1d136bfe6fadce6bdca7df112deb00435ee66/README.md

**Editorial limitation:** These are presented only as values documented by the project. This package does not independently verify realized rewards or imply guaranteed earnings.

## Claim 4 — offline attestation workflow
**Claim:** The project documents an offline workflow that stores an attestation in `ATTEST.TXT` and transfers it to a networked computer for submission.

Sources:
- README `Offline Mode`: https://github.com/Scottcjn/rustchain-dos-miner/blob/7fc1d136bfe6fadce6bdca7df112deb00435ee66/README.md
- `RTCMINE.BAT`, which checks for `ATTEST.TXT` and tells the user the attestation is saved there: https://github.com/Scottcjn/rustchain-dos-miner/blob/7fc1d136bfe6fadce6bdca7df112deb00435ee66/RTCMINE.BAT
- `dos_bridge.py`, described as watching `ATTEST.TXT` changes and submitting attestations to nodes: https://github.com/Scottcjn/rustchain-dos-miner/blob/7fc1d136bfe6fadce6bdca7df112deb00435ee66/dos_bridge.py
- `COMPLETE_SYSTEM.md`, which documents a minimal 8086/286 configuration using offline attestation to `ATTEST.TXT`: https://github.com/Scottcjn/rustchain-dos-miner/blob/7fc1d136bfe6fadce6bdca7df112deb00435ee66/COMPLETE_SYSTEM.md

## Claim 5 — experimental framing
This package intentionally calls RustChain an **experimental network** rather than making a financial or performance promise. No token-price prediction, return estimate, or guaranteed acceptance claim is made.

## Bounty source
Current package requirements and Type C cap were checked against:
- https://github.com/Scottcjn/rustchain-bounties/issues/16601

At review time the issue specifies Type C as a ≤60-second Shorts/clip kit with a script, vertical visuals or exact capture instructions, hook, and metadata; the current rule states a maximum of five Type C packages per person all-time.
