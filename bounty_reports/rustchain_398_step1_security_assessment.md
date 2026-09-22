# RustChain #398 — Step 1 Security Assessment

**Claimant:** @fsalmon1991  
**Bounty:** Scottcjn/rustchain-bounties #398, Step 1 — “Read the Architecture”  
**Requested reward:** 10 RTC  
**RTC wallet:** `RTC7f216de84caae4f0fb1bddf3f22e08f76e06bd63`  
**AI assistance:** Yes. This assessment was prepared with AI assistance from public source code and documentation; no production exploitation was performed.

## Scope and sources reviewed

I reviewed the current public RustChain repository at commit `217ba85ef9cab3daac0da7b822c79437693444df`, focusing on `docs/API.md`, `docs/attestation-flow.md`, `specs/RIP_POA_SPEC_v1.0.md`, `node/hardware_fingerprint_replay.py`, `node/anti_double_mining.py`, `node/fingerprint_checks.py`, and the epoch-determinism/settlement references exposed by the repository. This is a source review, not a claim that I exercised attacks against production.

## 1. How `/attest/submit` works

RustChain’s attestation path is the identity gate that turns a wallet/miner into an epoch-eligible participant. The public API documents `POST /attest/submit` as the endpoint for submitting a hardware fingerprint for epoch enrollment. The RIP-PoA specification gives the more complete model: the miner sends a wallet/miner identifier, a nonce and commitment, device metadata, signals, and a fingerprint composed of physical-behavior checks. The checks include oscillator/clock behavior, cache timing, SIMD identity, thermal drift, instruction-path jitter, device-age evidence, anti-emulation evidence, and ROM fingerprinting.

The important security property is that the node is not supposed to trust the client’s statement that a check passed. RIP-PoA explicitly says the server re-evaluates raw fingerprint evidence. The server validates the fingerprint, derives a canonical verified device rather than blindly accepting self-reported architecture, records a successful attestation in `miner_attest_recent`, and enrolls the miner for the current epoch with an antiquity-derived weight. The flow documentation also shows Ed25519 signature verification before enrollment and duplicate-hardware checks before a miner is admitted. Failed virtualization evidence produces a VM rejection; duplicate physical hardware is intended to be rejected or collapsed so one machine cannot earn as multiple identities.

Replay resistance is layered on top. `node/hardware_fingerprint_replay.py` hashes normalized fingerprint material, records prior submissions, rejects recently repeated fingerprint hashes under different nonces, detects nonce reuse across identities, checks entropy-profile collisions between wallets, and supports a per-hardware submission-rate limit. This matters because a valid captured fingerprint is only useful to an attacker if the server will accept it as fresh evidence for another identity.

## 2. How fingerprinting fights VM farms

RustChain’s 1-CPU-1-vote design has a Sybil problem unless “one CPU” means a distinct physical machine rather than a process, container, VM, or emulator. RIP-PoA addresses this by combining several signals that are harder to fake consistently than a model string. Clock-skew and oscillator variance look for real timing noise; cache tests look for a non-flat memory hierarchy; SIMD checks cross-check architecture-specific capabilities; thermal measurements look for load-dependent physical behavior; instruction jitter looks for pipeline-level variance; anti-emulation checks inspect virtualization indicators; age/provenance checks are used to validate antiquity claims.

The defense is stronger as a *cross-checking system* than any single threshold is by itself. A VM may spoof CPUID strings, but it also has to produce cache, timing, thermal, SIMD and jitter evidence that is internally consistent with the architecture it claims. The specification also states that the server can override a claimed architecture when measured evidence contradicts it. Finally, anti-double-mining logic in `node/anti_double_mining.py` groups enrolled miners by a machine-identity hash and selects one representative miner when multiple miner IDs map to the same physical identity. That provides a second line of defense at settlement time even if multiple logical identities reach enrollment.

## 3. Epoch reward calculation and distribution

The active RIP-PoA specification defines a 1.5 RTC per-epoch reward pot. Valid attestation causes the miner to be entered in the epoch enrollment snapshot with a weight corresponding to its time-aged antiquity multiplier. At settlement, weights are summed to `total_weight`, then each miner receives `(weight / total_weight) * PER_EPOCH_URTC`; the last miner receives the integer remainder so rounding does not create or destroy part of the epoch pot.

That makes the security of `epoch_enroll` and machine identity directly financial: manipulating eligibility or weight changes the fraction of a fixed reward pool received by every other miner. `node/anti_double_mining.py` therefore prefers the per-epoch `epoch_enroll` snapshot when grouping miners and selecting a representative per machine. It also prefers the highest enrolled weight for an identity before using entropy score, recency and a deterministic miner-ID tie-breaker. The repository’s determinism and settlement tests check that reward sums remain equal to the epoch budget, which is the right invariant for preventing silent inflation through rounding or replayed settlement.

## 4. Potential attack vector / risk to prioritize: settlement identity degradation when the epoch snapshot is absent

The most concrete risk I would prioritize from this review is the fallback path in `node/anti_double_mining.py` when an epoch has no `epoch_enroll` rows. Both `detect_duplicate_identities()` and `get_epoch_miner_groups()` explicitly fall back to a time-window query over `miner_attest_recent`, and the source itself warns that this path “may drop miners if delayed.” This is not a claim that I exploited production, but it is a real security boundary because anti-double-mining and reward assignment are financial-integrity controls.

If a settlement is delayed, partially migrated, restored from an inconsistent backup, or otherwise reaches the fallback without its canonical epoch snapshot, a live/recent-attestation table can differ from the set that was actually eligible during the epoch. A miner whose recent row aged outside the queried window can disappear from grouping, while identity information may be reconstructed using the latest fingerprint history rather than the exact epoch-time profile. The resulting failure mode is primarily integrity/fairness rather than theft of arbitrary funds: duplicate identities could be grouped incorrectly, legitimate miners could be excluded from the denominator, or representative selection could differ from the canonical epoch state.

The hardening direction is to treat the epoch enrollment snapshot as consensus-critical settlement input, not an optional optimization. If `epoch_enroll` is missing or incomplete for an epoch that should be settled, fail closed and require deterministic recovery/reconstruction from immutable epoch evidence instead of silently using mutable recent-state tables. A stored snapshot hash/row count, explicit schema/version marker, and pre-settlement invariant that every eligible miner has the required epoch-time identity material would make this boundary auditable. The existing code comments already recognize the fallback weakness; converting that warning into a hard invariant would reduce an avoidable path where operational state can influence financial results.

## Conclusion

RustChain’s security model is coherent: signed attestation establishes a miner identity, multi-signal physical fingerprinting raises the cost of VM/emulator Sybils, replay and duplicate-identity defenses protect that identity over time, and weighted epoch settlement distributes a fixed reward pot. The central risk is therefore not only whether each hardware check is individually hard to spoof, but whether the *same validated identity state* is carried deterministically from attestation through enrollment to settlement. I would focus hardening work on making that state transition fail-closed, versioned, and reproducible so operational fallbacks cannot change who gets paid.

## Public source references

- RustChain API: https://github.com/Scottcjn/Rustchain/blob/main/docs/API.md
- Attestation flow: https://github.com/Scottcjn/Rustchain/blob/main/docs/attestation-flow.md
- RIP-PoA specification: https://github.com/Scottcjn/Rustchain/blob/main/specs/RIP_POA_SPEC_v1.0.md
- Replay defense: https://github.com/Scottcjn/Rustchain/blob/main/node/hardware_fingerprint_replay.py
- Anti-double-mining / settlement identity: https://github.com/Scottcjn/Rustchain/blob/main/node/anti_double_mining.py
- Fingerprint producer/validation checks: https://github.com/Scottcjn/Rustchain/blob/main/node/fingerprint_checks.py
