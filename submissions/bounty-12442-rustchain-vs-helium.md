## RustChain vs Helium: physical infrastructure, different proofs

Helium and RustChain both connect rewards to physical machines, but they verify different resources. Helium's useful resource is wireless coverage and traffic: community Hotspots provide LoRaWAN and mobile offload coverage, while Data Credits pay for network usage. Historically Helium used Proof-of-Coverage (PoC), but its own docs say PoC was removed on July 6, 2026. A current comparison should not describe PoC as its live reward mechanism.

RustChain's Proof of Antiquity (RIP-200) instead makes hardware identity the scarce resource. Its protocol defines “1 CPU = 1 vote,” weighted by antiquity. A signed miner attestation includes six checks: clock drift, cache timing, SIMD identity, thermal entropy, instruction jitter, and hypervisor/behavioral heuristics. The aim is not to prove coverage or useful compute; it is to make “this is real physical hardware of this class” expensive to fake.

That creates opposite hardware incentives. Helium allows compatible LoRaWAN gateways to join permissionlessly, including Raspberry Pi + radio-concentrator setups. That helps operators add coverage where users need it. RustChain weights older PowerPC and retro systems more heavily, creating a reuse/preservation incentive. The downside: a vintage machine's attestation is less directly useful to an outside customer than wireless connectivity.

Their anti-Sybil surfaces differ too. Helium identifies gateways and ties them to traffic/location rules; its historical PoC reasoned about spatial relationships between radios. RustChain combines timing and anti-emulation signals to make mass VM spoofing harder. But trusted attestation nodes validate those signals, so fingerprint quality and validator behavior remain part of RustChain's security model. Six checks only matter if they survive adversarial testing.

Token economics diverge as well. Helium HNT has a known maximum supply, a two-year halving schedule and capped net emissions; HNT is burned to create USD-pegged Data Credits used for traffic. RustChain documents a capped RTC supply and an epoch pot distributed among enrolled miners by weight. Helium ties demand more directly to network usage, while RustChain ties relative rewards more strongly to verified hardware age.

Helium's advantage is concrete external utility. RustChain's distinctive idea is turning hardware age itself into a verifiable participation dimension without requiring new purpose-built equipment.

The strongest framing is not “RustChain beats Helium.” Helium monetizes coverage; RustChain experiments with monetizing verifiable physical history. Both are DePIN, but the physical resource being proved is fundamentally different.

Sources: RustChain `docs/PROTOCOL_v1.1.md`; Helium docs on network overview, Hotspot onboarding, HNT economics, and PoC deprecation.

AI disclosure: produced with AI assistance and checked against project docs.

Wallet: RTC7f216de84caae4f0fb1bddf3f22e08f76e06bd63
