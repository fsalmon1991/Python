# Assembly map

## Edit rhythm

- **0:00–0:25:** fast hook, 2–4 second cuts, high-contrast green/red language.
- **0:25–1:35:** slow enough to read source excerpts; 6–10 second shots.
- **1:35–2:38:** rule-by-rule cadence; one rule per visual card.
- **2:38–3:35:** practical deployment explanation; emphasize `--diff origin/main`.
- **3:35–4:10:** implementation close-ups.
- **4:10–end:** conceptual payoff and clean end card.

## Audio

Use original narration or licensed/TTS narration. Background audio should be original, public-domain, or properly licensed. No copyrighted song is required. Keep music at least 14 dB below narration.

## Lower thirds

- `falsegreen — high-precision linter`
- `FG001 — failure returns a success-shaped value`
- `FG002 — status code without body verification`
- `FG003 — CI/shell failure intentionally swallowed`
- `FG005 — failed lookup defaults to authoritative empty`
- `--diff origin/main — gate the delta, not the legacy baseline`

## On-screen source convention

For source captures, place a small footer:
`Source: Scottcjn/Rustchain @ 217ba85e — tools/falsegreen/...`

For any reconstructed illustration, place:
`Illustration — behavior derived from cited source, not live production output`

## Fact-safety pass before export

- Confirm every numeric claim still matches `SOURCES.md`.
- Do not say the current repository has exactly the historical count reported in the README; say the README reports the August 18 sweep found “15+”.
- Do not imply FalseGreen proves a system is healthy; it targets specific failure shapes.
- Do not show fabricated terminal success/failure output as if captured live.
- Do not make financial claims about RTC.
