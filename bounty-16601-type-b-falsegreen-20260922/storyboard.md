# Storyboard — “When Green CI Lies”

**Target:** 16:9 YouTube, ~5 minutes.  
**Rule:** every terminal result shown must be either a real local run or clearly labeled as an illustrative reconstruction based on the cited README/source. Do not invent a successful scan.

| Time | Visual | Exact capture / build instruction | Narration anchor |
|---|---|---|---|
| 0:00–0:12 | Thumbnail-style cold open | Full-screen `thumbnail.png`; animate a slow push into the peeled green-check area. | “A green checkmark is supposed to mean your system worked.” |
| 0:12–0:25 | Green pipeline → hidden red layer | Build a simple editor graphic with “CI: PASS” on top and “failure swallowed” underneath. Use only original shapes/text. | “What if the check itself is lying?” |
| 0:25–0:55 | Source README | Screen-record `tools/falsegreen/README.md` at the section defining “reports success while doing nothing.” Highlight the line explaining identical success/failure shapes. | Explain the pattern. |
| 0:55–1:15 | Four failure examples | Show four original cards: settlement, payout cap, pagination, health check. Put “documented examples” in a corner. | “The examples are not cosmetic.” |
| 1:15–1:35 | Confidence/uncertainty animation | Three boxes: `verified`, `failed`, `unknown`; animate `unknown` incorrectly collapsing into `verified empty`, then cross it out. | “It can convert uncertainty into confidence.” |
| 1:35–1:55 | FG001 | Capture `falsegreen.py` around the rule header/exception-handler logic; overlay `except → success-shaped return`. | Define FG001. |
| 1:55–2:08 | FG002 | Capture the source comment describing status-code-only health checks. Add 200 OK bubble next to a red body reading `{"ok": false}` as an illustrative example. | Define FG002. |
| 2:08–2:22 | FG003 | Show original CI snippets `continue-on-error: true` and `command || true`, stamped “evidence cannot fail.” | Define FG003. |
| 2:22–2:38 | FG005 | Show an original code card `claims = api(...) or []`; animate an API error turning into `[]`, then a wrong “0 claims” decision. | Define FG005. |
| 2:38–3:05 | Precision principle | Capture README paragraph explaining optional dependency exceptions and precision-over-recall. | “A noisy linter eventually gets ignored.” |
| 3:05–3:35 | Diff-only deployment | Terminal capture: `python3 tools/falsegreen/falsegreen.py . --diff origin/main --min-sev HIGH`; next to it show a split lane “legacy baseline” vs “new PR lines.” Only show actual command output if run locally. | Explain delta gating. |
| 3:35–4:10 | Implementation anatomy | Screen-record source imports (`ast`, `re`, `argparse`, `Path`) and the README’s stdlib / exit-code description. | Explain lightweight implementation. |
| 4:10–4:50 | Broader lesson | Original diagram: `SUCCESS / FAILURE / UNKNOWN`. Then return to the green-check thumbnail and replace the green check with a question mark. | “Could failure return the same shape as success?” |
| 4:50–end | End card | Project path, source commit, bounty disclosure, @fsalmon1991 attribution. | “Green is useful only when it still means something.” |

## Capture checklist

1. Checkout or browse upstream commit `217ba85ef9cab3daac0da7b822c79437693444df`.
2. Use the public source files linked in `SOURCES.md`.
3. If executing FalseGreen, preserve the raw output in the editor project for verification.
4. Do not claim that the linter found a specific current defect unless the exact run produced it.
5. Blur no secrets because the planned captures use only public repository content.
