# Narration Script

**Target duration:** 42–52 seconds  
**Word count:** 112

> One physical machine. Five different miner IDs. Should it get five rewards?
>
> RustChain’s anti-double-mining path says no.
>
> It builds a machine identity hash from the device architecture plus stable hardware-fingerprint data. During epoch settlement, miner IDs that resolve to the same machine identity are grouped, and the code selects one representative miner for reward treatment.
>
> That enforces the RIP-200 idea of **one CPU, one vote** more directly than trusting a username or miner ID.
>
> But this is not magic Sybil-proofing. RustChain’s own security notes document limits around cross-node settlement and identity rotation.
>
> The core idea is simpler: changing your miner name should not turn one physical CPU into five.

## On-screen hook

**1 CPU + 5 MINER IDs ≠ 5 REWARDS**

## Accuracy note

Describe this as the implemented same-node / same-epoch anti-double-mining path, not as a universal proof that double mining is impossible.