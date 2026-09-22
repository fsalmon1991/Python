# Script — A Transformer on a 1988 Sega Genesis

**Target runtime:** 52–58 seconds at ~140–155 words/minute  
**Format:** vertical short, 9:16  
**Disclosure:** AI-assisted script; facts independently checked against the upstream repository.

## Narration

A 1988 Sega Genesis is running a transformer live—not a lookup table.

The project runs an integer-only ternary language model on the console’s 7.67 megahertz Motorola 68000, with no FPU and 64 kilobytes of work RAM.

The trick is the cartridge. Its ROM is memory-mapped, so model data can stay on the cartridge instead of being copied into scarce RAM. Ternary weights—minus one, zero, plus one—also turn much of the math into adds and subtracts.

On a real Genesis Model 1, the team operator-timed generation at about 1.97 tokens per second.

Separately, their exact-cycle MAME benchmark cut a 38-pass run from 220,579,814 cycles to 131,766,162: a 1.674-times speedup.

That benchmark is headless, so don’t confuse it with the on-screen rate. The interesting result is simpler: careful data layout made a tiny 1988 console a real inference target.
