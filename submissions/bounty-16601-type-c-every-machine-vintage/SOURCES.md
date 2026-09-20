# Sources and Claim Map

All factual claims are pinned to this reviewed RustChain revision:

**Commit:** `217ba85ef9cab3daac0da7b822c79437693444df`  
**README:** https://github.com/Scottcjn/Rustchain/blob/217ba85ef9cab3daac0da7b822c79437693444df/README.md

No live endpoint values are used in the narration, so the package remains reproducible from the pinned repository state.

| Claim used in package | Source location in pinned README | Source text / evidence |
|---|---|---|
| RustChain positions itself as a system where older hardware can receive greater protocol weight than newer hardware. | Opening section + “Every Machine Becomes Vintage” | README headline: “The blockchain where old hardware outearns new hardware.” The later section says hardware can appreciate in protocol value as it ages. |
| PowerPC G4 (2003) is listed at `2.5×`. | “Why This Exists” hardware multiplier table | Row: `PowerPC G4 (2003) | 2.5x | ANCIENT`. |
| Modern x86_64 is listed at `0.8×`. | “Why This Exists” hardware multiplier table | Row: `Modern x86_64 | 0.8x | MODERN`. |
| The package must not frame the multiplier difference as a raw-speed benchmark. | “Why This Exists” + Proof-of-Antiquity description | README states Proof of Antiquity rewards hardware for surviving, not for being fast; older machines receive higher multipliers. |
| Example Ryzen 9 progression: 2026 `0.8×`, 2031 `1.3×`, 2036 `1.8×`, 2041 `2.2×`. | “Every Machine Becomes Vintage” code block | The README gives those four dated multiplier values for the same example machine. |
| RustChain describes six hardware fingerprint checks. | “AI-Augmented Consensus” → “Hardware Fingerprinting (6 Checks No VM Can Fake)” | The six listed checks are clock-skew/oscillator drift, cache timing fingerprint, SIMD unit identity, thermal drift entropy, instruction path jitter, and anti-emulation detection. |
| The closing line “Every machine becomes vintage” is part of the project’s published thesis. | “Every Machine Becomes Vintage” | Section heading and surrounding text explicitly make this claim. |

## Claims intentionally excluded

To keep the short factual and low-risk, this package does **not** use:

- token prices or exchange-rate claims;
- dollar-profit or ROI claims;
- statements that a protocol multiplier equals a guaranteed real-world earning;
- uncited environmental-impact numbers;
- claims about current live miner counts;
- external market-size, VC-funding, or competitor statistics;
- the README phrase “2.5x more than a modern Threadripper” as a mathematical ratio. Instead the script reports the two documented protocol multipliers separately: `2.5×` and `0.8×`.
