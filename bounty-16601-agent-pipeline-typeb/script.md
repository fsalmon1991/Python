# Script — When an AI Agent Earns a Bounty

**Target runtime:** ~5 minutes  
**Tone:** factual, practical, non-promotional

---

## 0:00–0:25 — Hook

An AI agent finds a paid GitHub issue. That sounds like the easy part. The harder question is: how do you prove the agent did real work, used the real codebase, followed the project's rules, and submitted through a channel the maintainer can actually verify?

RustChain's bounty documentation is unusually explicit about that pipeline. It welcomes AI-assisted work, but it also documents the exact failure modes that make agent submissions useless: invented APIs, imaginary files, untested code, duplicate claims, and silent authorization failures.

## 0:25–1:10 — Step 1: start with a real paid issue

The process begins with an actual bounty issue, not a vague promise of future payment. For example, RustChain bounty round #16601 defines four publication-package types, their RTC rewards, caps, required files, and accepted submission routes. Type B pays 15 RTC for a complete script-and-storyboard kit. Type C pays 15 RTC for a Shorts kit. The issue also states that agents can build the package while a human publisher handles external platforms.

That matters because the acceptance criteria exist before the work begins. The agent can turn them into a checklist instead of guessing what “good enough” means.

## 1:10–2:10 — Step 2: verify before creating

RustChain's submission guide tells contributors to verify the real API, real file paths, and actual behavior before writing integration code or making technical claims. It gives a blunt reason: earlier submissions referenced files and endpoints that did not exist.

For an autonomous worker, that becomes a simple discipline: every factual claim needs a source, every referenced path needs to be fetched, and executable work needs a test or reproduction step. If the agent cannot independently verify a fact, it should leave it out or label it as an open question.

This is the difference between generating text and completing a bounty. The deliverable has to survive somebody else checking it.

## 2:10–3:05 — Step 3: treat authorization failure as a workflow state

There is another failure mode that has nothing to do with the quality of the work. Many agent harnesses operate through a GitHub App. A GitHub App can only write where that app is installed, so an agent may be able to read a public repository while receiving “403 Resource not accessible by integration” when it tries to comment.

RustChain documents this case directly. The project says not to fail silently. Preferred routes include using a real user token, escalating to the human operator, publishing the deliverable in a repository the contributor controls, opening a pull request when appropriate, or using the monitored project email fallback when GitHub write access is unavailable.

The important design lesson is broader than RustChain: an autonomous worker should distinguish “the work failed” from “the submission channel failed.” Those are different states and need different recovery paths.

## 3:05–3:55 — Step 4: preserve evidence and attribution

The email fallback is not a shortcut around review. The project's guide says the message still needs the bounty number, the actual deliverable or public URL, the payout wallet, and an AI disclosure when an agent produced the work.

That creates a clean evidence chain: bounty issue, public artifact, claimant identity, payout destination, submission timestamp, and review outcome. The same structure also makes duplicate detection possible. If a later message corrects or overlaps an earlier claim, the ledger can keep both messages while counting the underlying work once.

For autonomous systems, this is crucial. A worker that can produce ten emails is not ten times more productive if nine are duplicate claims.

## 3:55–4:35 — Step 5: payment is a separate state

A submitted bounty is not revenue. A requested reward is not revenue. Even an accepted deliverable should remain separate from a confirmed payment.

RustChain's #16601 issue describes a review-and-payout process for accepted packages, including a queued phase before confirmation. A reliable worker should therefore track at least four separate states: submitted, accepted, pending settlement, and paid.

That accounting rule prevents an agent from turning optimistic pipeline value into fake earnings.

## 4:35–5:05 — Close

The interesting part of autonomous bounty work is not that an AI can write a script or patch. It is that the entire job can be made auditable: a real task, objective criteria, verified sources, a reproducible deliverable, an authorized submission route, and a payment state that is never invented.

That is the useful pattern: automate the work, not the evidence away.

---

## On-screen disclosure

`Built with AI assistance for @fsalmon1991. Facts checked against the public RustChain bounty tracker and submission documentation. No payout is claimed until confirmed by the maintainer.`