# 9:16 storyboard and capture plan

Target canvas: **1080 × 1920**, 30 fps. Target duration: **50–55 seconds**. Use only repository captures, text, simple vector shapes, and terminal-style cards; no third-party media is required.

| Time | Narration beat | Exact visual / capture instruction |
|---|---|---|
| 0:00–0:04 | “Most AI agents can call APIs…” | Black terminal-style background. Large centered hook: **“What if AI agents could hire each other?”** Animate three labeled nodes A, B, C into view. |
| 0:04–0:13 | Agent A posts 2 RTC research job | Screen-capture the public `run_pipeline()` Phase 1 block from `agent-economy-demo/autonomous_pipeline.py`, cropping to the `reward_rtc=2.0` line. Overlay arrow **A → B** and small label **2 RTC research job**. |
| 0:13–0:20 | B claims/delivers; A accepts | Four vertically stacked chips animate in sequence: **POST → CLAIM → DELIVER → ACCEPT**. Under ACCEPT, show **escrow → worker**. Capture the source's `accept_delivery()` log string mentioning reward paid and platform fee. |
| 0:20–0:30 | B posts 1.5 RTC job; C posts 1 RTC review | Rotate the three nodes into a triangle. Animate **B → C: 1.5 RTC** then **C → A: 1 RTC**. Capture the corresponding reward lines from the pipeline source if desired; otherwise render them as source-backed text cards. |
| 0:30–0:39 | Lifecycle explanation | Keep the triangle faint in the background. Center the lifecycle as one line broken vertically: **post / claim / deliver / accept / repeat**. Flash `/agent/jobs`, `/claim`, `/deliver`, `/accept` endpoint-style labels. |
| 0:39–0:48 | Work + delivery + acceptance + payment | Split-screen: left shows a code crop from `post_job()` / `deliver_job()`; right shows four checkboxes: **Work defined**, **Worker identified**, **Delivery recorded**, **Payment released**. Only check each box when its narration phrase lands. |
| 0:48–0:54 | Close | Return to A/B/C triangle with directional arrows A→B→C→A. Final kinetic line: **“3 agents · 3 jobs · 1 circular economy”**. Footer: **RIP-302 demo · RustChain** and author credit **@fsalmon1991**. |

## Accessibility / edit notes

- Burn in captions for every spoken line.
- Keep text inside a 90 px safe margin.
- Minimum body text equivalent: 42 px at 1080×1920.
- Never rely on color alone to distinguish A/B/C; always retain the letter labels.
- Avoid flashing faster than 3 times per second.
