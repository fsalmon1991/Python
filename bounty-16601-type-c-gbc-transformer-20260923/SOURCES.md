# Source map

Upstream repository: https://github.com/maddiedreese/gbc-transformer  
Pinned commit reviewed: [`28c443c1b0cb3d4536f4575bcdfd647a3ec8ad73`](https://github.com/maddiedreese/gbc-transformer/commit/28c443c1b0cb3d4536f4575bcdfd647a3ec8ad73)  
Pinned README: https://github.com/maddiedreese/gbc-transformer/blob/28c443c1b0cb3d4536f4575bcdfd647a3ec8ad73/README.md

## Claim-by-claim verification

| Package claim | Upstream evidence |
|---|---|
| TinyStories-260K runs locally on a stock Game Boy Color | README opening description and **Hardware Result** section |
| Input prompt `a`; documented full text `Ares was a big, farmer. He was very happy` | README **Hardware Result** bullets |
| 16 total transformer forward passes | README **Hardware Result** |
| Estimated elapsed time about 45 minutes | README **Hardware Result** — explicitly labeled **estimated elapsed time** |
| Throughput about 0.0059 tokens/sec / one token every 2m49s | README **Hardware Result** |
| Q8 model embedded as MBC5 bank-switched cartridge data | README **What Works** |
| On-device BPE tokenization using 512-token TinyStories tokenizer | README **What Works** |
| Integer/fixed-point inference with RoPE, attention, RMSNorm, SwiGLU-style MLP and greedy argmax decoding | README **What Works** |
| Cartridge SRAM KV cache keeps base WRAM below 8 KB | README **What Works** |
| Context capped at 16 tokens and greedy decoding only | README **Current Limitations** |
| Model shape dim=64, hidden_dim=172, layers=5, heads=8, kv_heads=4, vocab=512 | README **Current Limitations**; not used in narration, retained here for verification context |

## Verification notes
- The package intentionally says **about 45 minutes**, matching the upstream wording; it does not upgrade the estimate into an independently timed measurement.
- No speedup ratio, earnings figure, or mining-performance number was inferred.
- No claim in the narration depends on the separate 10.09× emulator benchmark listed in RustChain bounty #16517, avoiding a cross-source mismatch with the newer hardware README.
- The package uses the upstream documented output as a quoted example, clearly labeled as upstream hardware output rather than a run performed by @fsalmon1991.
