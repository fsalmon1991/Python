# RustChain #12444 — Proof of Antiquity vs Proof of Storage

AI-assisted original analysis for the 3 RTC comparison bounty.

**Claimant:** @fsalmon1991  
**RTC wallet:** `RTC7f216de84caae4f0fb1bddf3f22e08f76e06bd63`

Proof-of-Storage systems and RustChain both turn a physical resource into Sybil resistance, but they meter different things. Filecoin asks whether a provider is storing committed data over time; Chia asks whether a farmer controls allocated disk space and combines that with proofs of time. RustChain’s Proof of Antiquity instead tries to bind participation to a real physical CPU/device and then weights that participation by an antiquity class. The scarce object is therefore not bytes but a hardware identity that is difficult to multiply cheaply with VMs.

That distinction matters for verification. Filecoin’s Proof of Replication/Proof of Spacetime family is cryptographic: a provider proves that specific data was encoded and remains stored. Chia’s plots let a farmer answer random Proof-of-Space challenges, while Timelords produce sequential VDF proofs showing that time has passed. These schemes do not care whether the disk is old or new; they care that the committed capacity exists. RustChain checks a different layer: clock behavior, cache timing, SIMD characteristics, thermal drift, instruction-path jitter and anti-emulation signals are used to decide whether the claimant behaves like real hardware rather than a VM/emulator. The age multiplier is then an economic classification layered on top of that physical-attestation problem.

The lifecycle incentives are almost inverted. Storage networks naturally reward adding or reserving more capacity. Chia can reuse otherwise-idle disks, but plotting/farming still creates demand for storage hardware. Filecoin has a direct service objective—durable, verifiable storage—so buying newer capacity can be economically rational. RustChain’s stated objective is preservation: an old PowerPC, retro x86 or other unusual machine can have *more* protocol weight than a modern host, so the economic signal favors keeping hardware useful instead of replacing it solely for performance.

That also exposes RustChain’s weaker side. Proof of Storage has a crisp external commodity: bytes retained for a customer or capacity committed to consensus. The verification target is mathematically narrow. RustChain has to infer “real hardware” from noisy physical measurements and then map that device into the correct antiquity tier without letting self-reported architecture or virtualization artifacts inflate rewards. That makes calibration, cross-validation and adversarial testing central to its security. Old hardware is also less energy-efficient per unit of compute, so preservation is not automatically environmentally superior in every workload.

The systems therefore solve different problems. If I need cryptographically verifiable decentralized storage, Filecoin/Chia-style mechanisms are the more direct tool. If I want to make *physical hardware identity and preservation* economically scarce—especially hardware that a normal compute market would discard—RustChain is the more unusual experiment. Proof of Storage prices space; Proof of Antiquity prices the difficulty of cheaply reproducing a trustworthy physical participant.

Sources checked: RustChain current README/bounty board; Filecoin documentation on storage proofs; Chia documentation on Proof of Space and Timelord/VDF Proofs of Time.
