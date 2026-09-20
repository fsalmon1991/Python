# Publication Metadata

## Primary title
When an AI Agent Earns a Bounty: The Verifiable Work Pipeline

## Alternate titles
1. AI Agents Can Do Bounty Work — But Can They Prove It?
2. From GitHub Issue to Payout: An Auditable AI-Agent Bounty Workflow

## One-line hook
The hard part is not getting an AI agent to produce work — it is proving the task, sources, submission, and payment are all real.

## Description

What does a legitimate autonomous bounty workflow look like when the worker has to survive real maintainer review?

This explainer uses RustChain's public bounty tracker and submission guide as a concrete case study. It walks through five stages: selecting an explicit paid task, verifying real APIs and files before producing work, recovering safely from a GitHub App authorization block, preserving submission evidence and attribution, and separating requested/accepted rewards from confirmed payment.

Public sources:
- https://github.com/Scottcjn/rustchain-bounties/issues/16601
- https://github.com/Scottcjn/rustchain-bounties/blob/main/docs/HOW_TO_SUBMIT_A_BOUNTY.md
- https://github.com/Scottcjn/rustchain-bounties/issues/16470

Author/claimant: @fsalmon1991  
AI disclosure: produced with AI assistance; factual claims mapped to public sources in `SOURCES.md`.

## Chapters

00:00 The real problem with autonomous bounty work  
00:25 Start with explicit acceptance criteria  
01:10 Verify before generating  
02:10 GitHub App 403: channel failure vs work failure  
03:05 Preserve evidence and attribution  
03:55 Requested is not paid  
04:35 The auditable loop

## Tags

AI agents, autonomous agents, GitHub bounties, open source, software agents, AI coding, bounty workflow, verification, human in the loop, RustChain

## Thumbnail concept

Split-screen graphic. Left: a stylized terminal/agent card labeled `WORK COMPLETE`. Right: a GitHub-style red `403` card. Between them: a bold arrow rerouting to a green `VERIFIED SUBMISSION` box. Small footer: `AUTONOMY NEEDS EVIDENCE`.

No coin imagery, price chart, or earnings promise.

## Suggested thumbnail text

**AI DID THE WORK. NOW PROVE IT.**

## Attribution line

Created by `@fsalmon1991` with AI assistance. Public-source verification links are included in the package.