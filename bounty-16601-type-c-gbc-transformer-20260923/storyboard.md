# Vertical storyboard — 9:16, ~53 seconds

Use 1080×1920 or 720×1280. All visuals can be original motion graphics; no third-party footage is necessary.

| Time | Visual | On-screen text / capture direction |
|---|---|---|
| 0:00–0:05 | Dark background. Original generic translucent handheld silhouette slides in; a tiny matrix of numbers lights up inside it. | **A TRANSFORMER. ON A GAME BOY COLOR.** Small subline: “local inference — not streaming” |
| 0:05–0:14 | Animate three blocks entering a cartridge: `TinyStories-260K` → `Q8` → `MBC5 banks`; then arrows from cartridge to CPU. | “quantized model • bank-switched cartridge • fixed-point inference” |
| 0:14–0:24 | Large stopwatch counts rapidly to `~45 min`. Beside it, a 16-step progress bar fills one cell at a time. | `16 forward passes` / `~0.0059 tok/s` / `1 token ≈ 2m49s` |
| 0:24–0:35 | Terminal-style text types on screen, character by character. Do **not** imply this was generated during the video; label it as the documented hardware output. | “Documented hardware output:” then `Ares was a big, farmer. He was very happy` |
| 0:35–0:46 | Memory diagram: `16-token context`; `KV CACHE → cartridge SRAM`; small base-memory box marked `< 8 KB WRAM`. | “16-token context” / “greedy decoding” / “KV cache in cartridge SRAM” |
| 0:46–0:53 | Return to handheld silhouette. Transformer blocks glow; speedometer stays deliberately near zero. | **NOT PRACTICAL. STILL REAL.** / “Transformer inference on stock GBC hardware” |

## Optional source-image shot
The upstream README includes a photo/screenshot showing TinyStories Q8 running locally on a Game Boy Color. If Elyan Labs wants to use it, source it directly from the upstream project and retain attribution to `maddiedreese/gbc-transformer`; otherwise use the original generic silhouette sequence above.

## Editing notes
- Fast visual cadence, but do not accelerate or fake a real-time GBC inference run.
- Never show `45 min` as a measured stopwatch recording unless the publisher actually records a full run; the source calls it an **estimated elapsed time**.
- No invented benchmark comparisons, token prices, earnings claims, or RustChain reward claims.
- No copyrighted Nintendo game footage is required.
