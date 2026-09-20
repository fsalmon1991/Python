# SOURCES — Claim-by-Claim Map

This file maps the narration's factual claims to public sources. Interpretive workflow advice is labeled as such and is not presented as a RustChain protocol fact.

## S1 — Distribution Packages bounty #16601

URL: https://github.com/Scottcjn/rustchain-bounties/issues/16601

Supports these claims:
- #16601 is a distribution-package bounty designed so agents can build publication-ready packages while humans handle external publishing.
- Type B is a YouTube script + storyboard kit.
- Type B base reward is 15 RTC.
- Type C base reward is 15 RTC.
- Type B requires the full production-kit written components except voiceover/visuals, replacing those with a precise storyboard.
- Submission is by public GitHub package plus comment; the machine-readable bounty spec also lists email as a submission route.
- The issue says accepted packages are normally published within 14 days and that base reward still pays if an accepted package is not published within 30 days.
- The issue describes accepted rewards as entering a queued phase before confirmation.

Used in script sections: 0:25–1:10, 3:55–4:35.

## S2 — How to Submit a Bounty PR That Actually Gets Paid

URL: https://github.com/Scottcjn/rustchain-bounties/blob/main/docs/HOW_TO_SUBMIT_A_BOUNTY.md

Supports these claims:
- The guide explicitly addresses AI agents and human contributors.
- Contributors are told to verify the real API before writing code.
- Contributors are told to verify real file paths and not invent filenames.
- The guide documents previous rejected work that referenced nonexistent files and endpoints.
- End-to-end testing before submission is required/recommended.
- The guide explains the `403 Resource not accessible by integration` failure for GitHub App-based agent harnesses.
- Documented recovery options include using a user token, escalating to the human operator, publishing in a repository the contributor controls, opening a PR where appropriate, and emailing `sophia.eagent@gmail.com` as an accepted fallback.
- Email submissions need the bounty number/issue URL, the deliverable or public URL, an RTC wallet, and AI disclosure when agent-produced.
- The guide says being blocked by the 403 does not reduce payout if the work is otherwise valid, and that claims are still verified against bounty requirements.

Used in script sections: 0:00–0:25, 1:10–3:55.

## S3 — Announcement #16470: GitHub App 403, private reporting, and contact route

URL: https://github.com/Scottcjn/rustchain-bounties/issues/16470

Supports these claims:
- The project publicly documented the GitHub App 403 problem after contributors reported it.
- A GitHub App can only write to repositories where that app is installed.
- `sophia.eagent@gmail.com` is the monitored project contact when GitHub cannot be reached by the contributor's tooling.
- The project says agents should not fail silently when blocked.
- For engagement bounties where the GitHub action itself is the deliverable, email alone does not substitute for the required public action.

Used in script section: 2:10–3:05.

## S4 — Interpretive accounting/workflow statements

The following narration statements are workflow design conclusions rather than claims that RustChain itself defines a universal accounting standard:
- “the work failed” and “the submission channel failed” should be separate states;
- duplicate messages should not multiply the value of one underlying piece of work;
- requested, accepted, pending-settlement, and paid amounts should be tracked separately;
- confirmed payment, rather than requested reward, is the conservative point to recognize realized revenue.

These conclusions are consistent with the public review/queue/payment stages in S1 and the evidence/submission guidance in S2, but are presented as recommendations for autonomous worker design.