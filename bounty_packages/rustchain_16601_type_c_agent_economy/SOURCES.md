# Claim-by-claim sources

Primary source pinned to RustChain commit `217ba85ef9cab3daac0da7b822c79437693444df`:

https://github.com/Scottcjn/Rustchain/blob/217ba85ef9cab3daac0da7b822c79437693444df/agent-economy-demo/autonomous_pipeline.py

| Claim in package | Public evidence |
|---|---|
| The demo has three agents hiring each other | File module docstring: Researcher posts/pays Writer; Writer delivers then posts/pays Publisher; Publisher delivers final article. |
| Lifecycle is `post -> claim -> deliver -> accept -> repeat` | File module docstring states that exact lifecycle. |
| Transactions are described as using RIP-302 escrow | File module docstring states: “All transactions on-chain via RIP-302 escrow.” |
| Agent A posts a 2 RTC research job | `run_pipeline()` Phase 1 calls `post_job(... reward_rtc=2.0 ...)`. |
| Agent B posts a 1.5 RTC writing job for Agent C | `run_pipeline()` Phase 2 calls `post_job(... reward_rtc=1.5 ...)`. |
| Agent C later posts a 1 RTC review/publishing job for Agent A | `run_pipeline()` docstring describes the third leg as a 1 RTC review/publishing job, completing A → B → C → A. |
| The workflow tracks poster and worker wallets | `post_job()` sends `poster_wallet`; `claim_job()` sends `worker_wallet`; job receipts print both fields. |
| Acceptance releases/pays the reward to the worker | `accept_delivery()` posts to the accept endpoint and logs `reward_paid_rtc` and `platform_fee_rtc` on success. |
| Jobs use the Agent Economy API | The class calls `/agent/jobs`, `/agent/jobs/{job_id}/claim`, `/deliver`, `/accept`, plus marketplace stats/reputation endpoints. |

## Deliberately excluded claims

This package does **not** claim that the demo proves real-world adoption, throughput, profitability, decentralization, production uptime, or security. It explains only behavior explicitly represented by the public demo source.
