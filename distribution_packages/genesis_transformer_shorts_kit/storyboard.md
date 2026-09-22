# Storyboard — 9:16 Shorts / Clip Kit

Target: 55 seconds, 1080×1920 vertical. No third-party stock assets required.

| Time | Visual / capture instruction | On-screen text | Narration cue |
|---|---|---|---|
| 0:00–0:05 | Start on a clean vertical title card. Animate a simple original outline of a 16-bit console and a small transformer-node diagram. | `A transformer on a 1988 Sega Genesis?` | “A 1988 Sega Genesis is running a transformer live—not a lookup table.” |
| 0:05–0:14 | Screen-record the upstream `legend-of-elya-genesis` README. Slowly zoom to the paragraph that states Motorola 68000 at 7.67 MHz, no FPU, 64 KB work RAM. Keep the GitHub repository name visible. | `68000 • 7.67 MHz • no FPU • 64 KB RAM` | Hardware sentence. |
| 0:14–0:25 | Replace repo capture with an original animated memory diagram: `Cartridge ROM → memory map → model weights`; show RAM as a tiny box that is not filled by the weights. Then animate three weight symbols: `-1  0  +1`. | `Memory-mapped ROM + ternary weights` | Cartridge / ternary explanation. |
| 0:25–0:33 | Return to a screen capture of the upstream README paragraph describing the real Genesis Model 1 and the ~1.97 tok/s operator-timed rate. Highlight only those words; do not crop away repo attribution. | `Real Model 1: ~1.97 tok/s (operator-timed)` | Real-hardware rate sentence. |
| 0:33–0:46 | Capture `FINDINGS.md` and highlight the before/after benchmark figures. Overlay a simple descending counter animation: `220,579,814 → 131,766,162 cycles`. | `Headless MAME benchmark: 1.674×` | Exact-cycle benchmark sentence. |
| 0:46–0:52 | Split screen: left label `REAL ON-SCREEN RUN`; right label `HEADLESS MAME BENCH`. Put a large `≠ same workload` between them. | `Do not mix these two measurements` | Caveat sentence. |
| 0:52–0:55 | End card with project/repo name and neutral CTA. | `Scottcjn/legend-of-elya-genesis`\n`Measured, corrected, reproducible.` | Final sentence. |

## Editing notes

- Keep every source capture long enough to read the repository owner/name.
- Do not reuse Sega promotional art, game footage, copyrighted music, or third-party stock assets.
- For the console silhouette and diagrams, create original vector shapes or generated graphics.
- Use neutral background music only if properly licensed; the package works without music.
- When showing the benchmark, label it `MAME 0.277 headless benchmark` so viewers do not mistake it for direct real-hardware timing.
- Do not say the project proves general-purpose LLM performance; it is a small, project-specific transformer inference demonstration.
