# Sources and claim map

All factual claims in the short are grounded in the upstream public repository.

## Source 1 — upstream README
https://github.com/Scottcjn/legend-of-elya-genesis/blob/main/README.md

Supports:
- real Sega Genesis Model 1 hardware demo
- Motorola 68000 at 7.67 MHz
- no FPU and no 32-bit multiply
- 64 KB work RAM
- integer-only ternary language model
- weights stored on the cartridge
- cartridge ROM is memory-mapped; expert activation can be pointer repointing rather than copying model data into RAM
- real-hardware operator-timed generation around 1.97 tokens/sec
- distinction between on-screen generation and headless benchmark figures
- ternary weights use {-1, 0, +1}

## Source 2 — optimization journal / exact-cycle benchmark
https://github.com/Scottcjn/legend-of-elya-genesis/blob/main/FINDINGS.md

Supports:
- MAME 0.277 used as the exact-cycle benchmark instrument
- original run: 220,579,814 cycles
- optimized input-major `wff2` run: 131,766,162 cycles
- resulting running-total speedup: 1.674×
- benchmark covers 38 forward passes (14 prompt + 24 generated)
- benchmark shell is headless with display and interrupts off, so it is not the same workload as the on-screen real-console demonstration

## Accuracy constraints used by this package

- Never present 2.21 tok/s from the headless benchmark as the real on-screen console rate.
- Never revive the retracted 11.3× claim; the repository explicitly corrects it to 1.674× for the measured optimization chain.
- Never claim this demonstrates general-purpose modern LLM performance; it is a small integer-only ternary transformer built for the Genesis constraints.
- Never claim guaranteed earnings, token returns, or investment value.
