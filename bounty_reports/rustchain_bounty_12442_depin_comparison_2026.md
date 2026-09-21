# RustChain bounty #12442 — RustChain vs Helium / DePIN in 2026

Claimant: `@fsalmon1991`  
RTC wallet: `RTC7f216de84caae4f0fb1bddf3f22e08f76e06bd63`  
Requested reward: **3 RTC**  
AI disclosure: AI-assisted research/drafting; factual claims were checked against current public sources before submission.

## Comparison

A useful comparison starts with a current-state correction: **Helium no longer uses Proof-of-Coverage (PoC)**. Helium's own documentation says PoC was removed from its networks on **July 6, 2026**. Today, community-operated Hotspots still provide LoRaWAN IoT coverage and mobile Wi-Fi offload, and operators are rewarded for supplying useful wireless infrastructure. That makes Helium's physical resource primarily **network service at a location**.

RustChain is trying to prove a different physical fact. Proof-of-Antiquity treats the **machine itself—especially old hardware—as the scarce resource**, using multiple hardware-fingerprint signals such as cache timing, clock/thermal behavior and anti-emulation checks. Instead of asking, “did this radio provide useful coverage?”, RustChain asks, “is this a distinct physical machine, and what does its hardware history imply?” Antiquity multipliers then make preservation part of the reward model.

### Hardware + anti-spoof trade-off

Helium's strength is obvious external utility: if a Hotspot carries IoT or mobile traffic, the network is providing a service people can buy. Its anti-abuse problem is correspondingly operational—location, traffic, device integrity and fraud controls. RustChain's model potentially raises the cost of Sybil farming by making one software image pretending to be hundreds of machines less useful; the attacker has to defeat several physical fingerprints, not just clone an identifier.

But RustChain also carries the harder validation burden. Hardware fingerprints must remain discriminative across legitimate machines, stable enough over time, and resistant to emulation without producing false positives. Helium does not need to prove that a 15-year-old CPU is genuinely old; it needs to verify that infrastructure is delivering wireless utility. That is a simpler value proposition for customers.

### Token model

Helium's HNT has a known maximum-supply framework, a two-year halving schedule, burn-and-mint Data Credits, and capped net emissions. RustChain instead ties miner rewards to participation plus hardware-antiquity weighting, so two valid machines can earn differently based on the physical hardware class/age being preserved. That creates a preservation incentive, but it also means RustChain ultimately needs utility beyond “old hardware exists” if rewards are to stay economically meaningful.

### What each does better

**Helium:** clearer real-world demand, deployed wireless infrastructure, and a mature usage model where Data Credits pay for network traffic.

**RustChain:** a more unusual DePIN primitive—turning verifiable hardware identity and preservation into something economically measurable, with a consensus model designed around diverse physical machines rather than purpose-built radios or maximum compute throughput.

So they are better viewed as **orthogonal DePIN models**: Helium monetizes *service delivered by physical infrastructure*; RustChain monetizes *verifiable physical hardware provenance and antiquity*.

## Sources checked

- Helium network overview: https://docs.helium.com/
- Helium HNT economics: https://docs.helium.com/tokens/hnt-token/
- Helium Oracle Data / PoC deprecation notice: https://docs.helium.com/network-data/oracle-data/
- Helium Data Credits: https://docs.helium.com/tokens/data-credit/
- RustChain bounty specification: https://github.com/Scottcjn/rustchain-bounties/issues/12442

## Verification notes

- No `fsalmon1991` claim was found in the fetched #12442 comment history before submission.
- The bounty is open and advertises **3 RTC**, one claim per writer.
- The comparison intentionally corrects stale descriptions of Helium rather than repeating the bounty prompt's older PoC framing.
- No benchmark, payout, network-usage, or profitability result was fabricated.
