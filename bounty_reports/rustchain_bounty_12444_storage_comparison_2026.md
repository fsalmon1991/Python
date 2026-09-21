# RustChain bounty #12444 — Proof of Antiquity vs Proof of Storage in 2026

Claimant: `@fsalmon1991`  
RTC wallet: `RTC7f216de84caae4f0fb1bddf3f22e08f76e06bd63`  
Requested reward: **3 RTC**  
AI disclosure: AI-assisted research/drafting; factual claims were checked against current public sources before submission.

## Comparison

Proof-of-storage networks and RustChain both make a physical resource economically relevant, but the resource is fundamentally different. **Filecoin and Chia make replaceable storage capacity scarce; Proof of Antiquity tries to make non-fungible hardware history scarce.**

Filecoin uses Proof-of-Replication to show that a storage provider created a unique copy of data, then Proof-of-Spacetime to show that the copy remains stored. Its WindowPoSt process audits pledged sectors repeatedly; current Filecoin mainnet uses 32 GiB and 64 GiB sectors. Chia's Proof of Space instead lets a farmer reserve disk space in plot files and answer cryptographic challenges, while Proof of Time orders the process. Chia is also in a live protocol transition: its current documentation says Proof of Space 2 is planned around a November 2026 hard fork, followed by a gradual replotting period into 2027. That makes older descriptions of Chia as a permanently “plot once and forget it” system increasingly stale.

RustChain asks a different question. Its Proof-of-Antiquity model uses multiple hardware-attestation signals—such as cache timing, clock/thermal behavior and anti-emulation checks—to distinguish physical machines and weight older hardware. Storage proofs mainly answer **“is the promised space/data really available?”** PoA aims to answer **“is this a distinct physical machine whose substrate and age are difficult to synthesize at scale?”**

That distinction changes hardware economics. Storage is deliberately fungible: a failed drive can be replaced, data can be resealed, and Chia plots can be recreated. Antiquity is intentionally less fungible. Replacing an old machine with a new server may increase performance, but it destroys the very history the reward model values. That can encourage reuse instead of replacement—but the environmental claim should not be overstated. Keeping inefficient vintage hardware powered forever is not automatically greener than replacement; the benefit depends on energy use, embodied manufacturing cost, useful workload, and how much e-waste is actually avoided.

The verification trade-off is equally important. Filecoin's proof system can cryptographically verify continued storage without caring whether the provider uses a ten-year-old server or a new datacenter. Chia can verify committed plot space without needing to identify a unique disk by age. RustChain's advantage is stronger coupling between reward and physical identity, potentially raising Sybil costs; its burden is proving that the fingerprint remains stable for honest machines while resisting emulation and spoofing.

On sustainability, storage networks have an external product: clients can pay for storage/retrieval, while block rewards bootstrap supply. RustChain's preservation incentive is distinctive, but long-run rewards still need utility beyond “this hardware is old.” Agent services, attestation, or other paid network activity matter because preservation by itself does not create unlimited economic demand.

**Filecoin does better:** verifiable storage of useful data at scale.  
**Chia does better:** space-based consensus that can farm on ordinary storage, with a mature challenge/proof model.  
**RustChain does better:** makes hardware identity, reuse and age first-class economic variables instead of treating hardware as interchangeable capacity.

The cleanest framing is therefore **space versus provenance**: proof-of-storage monetizes *capacity held over time*; Proof of Antiquity attempts to monetize *physical history preserved over time*.

## Sources checked

- Filecoin glossary / PoRep / PoSt / WindowPoSt: https://docs.filecoin.io/reference/general/glossary
- Filecoin mainnet sector parameters: https://docs.filecoin.io/networks/mainnet
- Chia Proof of Space: https://docs.chia.net/chia-blockchain/consensus/proof-of-space-1.0/
- Chia Proof of Space 2 timeline: https://docs.chia.net/chia-blockchain/consensus/proof-of-space-2.0/new-proof-timeline/
- Chia PoS2 introduction: https://docs.chia.net/chia-blockchain/consensus/proof-of-space-2.0/new-proof-introduction/
- RustChain bounty specification: https://github.com/Scottcjn/rustchain-bounties/issues/12444

## Verification notes

- No `fsalmon1991` claim was found in the fetched #12444 comment history before submission.
- The bounty is open and advertises **3 RTC**, one claim per writer.
- Current 2026 Chia documentation was used so the comparison does not repeat obsolete plotting assumptions.
- No benchmark, profitability result, storage-demand statistic, or environmental impact number was fabricated.
