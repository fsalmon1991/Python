# Storyboard — When an AI Agent Earns a Bounty

**Format:** 16:9 YouTube explainer  
**Target runtime:** ~5:05  
**Visual rule:** use only public GitHub pages, terminal-style text recreations, and simple original motion graphics. Do not show private inbox contents, tokens, cookies, or wallet private material.

| Time | Narration beat | Exact visual / capture direction | On-screen text |
|---|---|---|---|
| 0:00–0:10 | “An AI agent finds a paid GitHub issue…” | Screen capture: GitHub search/bounty issue cards scrolling quickly, then stop on RustChain #16601 title and reward table. Crop browser account controls if desired. | `PAID TASK → VERIFIED WORK → SUBMISSION → REVIEW → PAYMENT` |
| 0:10–0:25 | Real problem is proof and verification | Original diagram: five boxes appear one at a time: Real task, Real sources, Tested deliverable, Authorized channel, Confirmed payout. | `Autonomy needs evidence.` |
| 0:25–0:45 | #16601 has explicit package types | Capture #16601 package table. Zoom only the Type B and Type C rows. | `Type B: 15 RTC` / `Type C: 15 RTC` |
| 0:45–1:10 | Acceptance criteria before work | Capture the “What Goes In A Package” Type B section, then animate checklist ticks beside `script.md`, `storyboard.md`, `metadata.md`, `SOURCES.md`. | `Turn the issue into a checklist.` |
| 1:10–1:30 | Verify the real API / paths | Capture `docs/HOW_TO_SUBMIT_A_BOUNTY.md`, scrolling through “Verify the real API” and “Verify the real file paths.” | `VERIFY BEFORE GENERATE` |
| 1:30–1:50 | Hallucinated endpoints/files are rejected | Terminal-style recreation, not a live command: show `curl REAL_ENDPOINT`, `gh api repos/.../contents/REAL_FILE`, then green checkmarks. Beside it, invented path turns red and disappears. | `If you cannot fetch it, do not cite it.` |
| 1:50–2:10 | Deliverable must survive checking | Show a source map animation: claim on left → GitHub URL/file on right → validation check. Three example arrows. | `Claim → Source → Check` |
| 2:10–2:35 | GitHub App 403 | Capture #16470 or the submission-guide 403 section. Highlight only the text `403 Resource not accessible by integration`. Do not show any credential. | `CHANNEL BLOCKED ≠ WORK FAILED` |
| 2:35–3:05 | Documented recovery routes | Original branching diagram: `GitHub App 403` → `user token` / `human operator` / `public artifact` / `PR` / `project email fallback`. Highlight public artifact + email fallback. | `Never fail silently.` |
| 3:05–3:30 | Email is still verified | Capture the submission guide's “What an email submission needs” bullets. Blur/crop unrelated browser chrome. | `Bounty # + Deliverable + Public URL + Wallet + AI disclosure` |
| 3:30–3:55 | Duplicate-aware evidence chain | Original timeline with two submission-envelope icons. Second one gets label `correction / duplicate`, both remain visible, while a single claim counter stays at 1. | `Preserve evidence. Count the work once.` |
| 3:55–4:20 | Submission is not revenue | Four-step state machine appears: Submitted → Accepted → Pending settlement → Paid. Only `Paid` turns into a dollar/RTC ledger icon. | `Requested ≠ Accepted ≠ Paid` |
| 4:20–4:35 | #16601 review/payout language | Capture #16601 ground rules / claim section where review and queued confirmation are described. | `Track state, don't invent earnings.` |
| 4:35–4:55 | Auditable loop | Return to the opening five-box diagram; each box gets a checkmark. | `Real task • Verified sources • Reproducible work • Authorized submission • Confirmed payout` |
| 4:55–5:05 | Final line | Black background, simple centered text. | `Automate the work, not the evidence away.` |

## Capture checklist

1. #16601 issue title, package reward table, Type B requirements, claim/review section.
2. `docs/HOW_TO_SUBMIT_A_BOUNTY.md`: real API rule, real path rule, end-to-end testing rule, 403 section, email requirements.
3. #16470 announcement: 403 explanation and monitored project contact.
4. No private Gmail inbox capture is needed.
5. No live token, PAT, cookie, secret, seed phrase, private key, or account credential should appear in any frame.

## Editor notes

- Keep GitHub source captures on screen long enough for viewers to see the relevant heading, not necessarily read every paragraph.
- Use a small source slug in the lower-right corner on factual scenes, e.g. `rustchain-bounties#16601` or `HOW_TO_SUBMIT_A_BOUNTY.md`.
- Avoid crypto-price imagery, charts, coins spinning, or profit graphics. This video is about verifiable workflow, not investment value.
- If a maintainer changes a reward amount before publication, update the reward overlays to match the current issue title/body and note the capture date.