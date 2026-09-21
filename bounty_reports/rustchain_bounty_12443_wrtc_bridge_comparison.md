## wRTC vs generalized cross-chain bridges: reserve release first, messaging second

RustChain’s current Solana path is narrower than Wormhole, LayerZero, or Axelar. The key architectural detail is that wRTC is **not an unlimited lock-and-mint bridge**. RustChain’s current `docs/wrtc.md` records a fixed 8.3M-token SPL supply with both mint and freeze authority burned. Native RTC deposits therefore authorize a 1:1 **release of already-minted wRTC from a published reserve**, through an authenticated queued process signed out-of-band. On the return path, wRTC is burned on Solana before native RTC is released. That caps Solana-side supply, so compromising a mint key cannot create arbitrary new wRTC.

That does not make the bridge trustless. Its critical boundaries move to reserve custody, recognition of native RTC deposits, authorization of reserve withdrawals, duplicate/replay prevention, and native-side release after a Solana burn. wRTC trades a broad verification stack for a simpler invariant: circulating wRTC should be explainable by fixed supply, reserve movements, burns, and corresponding native RTC movements. The strongest controls are public reserve reconciliation, immutable transfer IDs, idempotent processing, bounded signing authority, and a documented recovery/pause procedure.

Wormhole solves a larger problem. Guardians observe source-chain messages and a 13-of-19 quorum signs a VAA that destination contracts can verify. That supports generalized messaging across many chains, but users inherit Guardian-set and contract-verification assumptions. LayerZero V2 is more configurable: applications choose Decentralized Verifier Networks (DVNs) for verification, while permissionless Executors deliver messages. The advantage is modularity; the cost is a larger configuration surface whose security depends on the application’s DVN choices and endpoint/message-library assumptions.

DEX integration is separate from bridge safety. wRTC is already a normal 6-decimal SPL token with a documented Raydium market; Raydium does not need to understand RustChain’s bridge. Jupiter can route wRTC once usable liquidity is discoverable. An Orca pool is technically possible, but I would not claim one exists without on-chain evidence.

The honest trade-off is scope. Wormhole and LayerZero are reusable interoperability layers. wRTC is a purpose-built Solana liquidity gateway whose best security property is a burned mint authority and auditable reserve model, but whose operational custody and reconciliation still matter. If RustChain expands the bridge, hardening accounting and replay boundaries is more valuable than adding complexity simply to resemble larger bridge networks.

**RTC wallet:** `RTC7f216de84caae4f0fb1bddf3f22e08f76e06bd63`

**AI disclosure:** Prepared with AI assistance and checked against current RustChain wRTC, Wormhole, and LayerZero documentation.

### Verification sources
- RustChain current wRTC guide: `docs/wrtc.md` (fixed 8.3M supply, mint/freeze authority burned, reserve-release custody model, Raydium/Jupiter references)
- Wormhole current Guardian/VAA docs: 19 Guardians; 13-of-19 VAA quorum
- LayerZero V2 architecture docs: configurable DVNs + permissionless Executors
