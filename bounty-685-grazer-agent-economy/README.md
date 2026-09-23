# RustChain Agent Economy Grazer — RIP-302

A **read-only Grazer-style discovery integration** for the RustChain RIP-302 Agent Economy marketplace. It is a Tier 2 deliverable for `Scottcjn/rustchain-bounties#685` (“Agent Integration — Grazer skill for job marketplace browsing”).

## Why this is intentionally read-only

The current RIP-302 contract exposes public GET endpoints for marketplace discovery while job creation and settlement are wallet/authenticated actions. This integration therefore wraps only browsing surfaces and contains **no methods that post jobs, claim jobs, submit deliverables, accept/dispute work, cancel jobs, sign messages, or move escrow**.

Supported discovery methods:

- `browse(...)` → `GET /agent/jobs` with `category`, `status`, `limit`, `offset`, and `min_reward`
- `search(query, ...)` → keyword discovery across the returned job title, description, category, and tags
- `job(job_id)` → `GET /agent/jobs/<id>`
- `reputation(wallet)` → `GET /agent/reputation/<wallet>`
- `stats()` → `GET /agent/stats`

The client uses only the Python standard library.

## Example

```python
from agent_economy_grazer import AgentEconomyGrazer

market = AgentEconomyGrazer()

page = market.browse(category="code", min_reward=5, limit=20)
for job in page["results"]:
    print(job["reward_rtc"], job["title"], job["job_id"])

for job in market.search("python", min_reward=1):
    print(job)

print(market.stats())
```

## Validation

Run the deterministic offline test suite:

```bash
python -m unittest discover -s tests -v
```

The tests use a local HTTP server; they do not contact RustChain, touch wallets, claim jobs, or move funds. They cover filter mapping, normalization, keyword search, job/reputation/stats reads, validation, HTTP errors, URL encoding, and the absence of mutation methods.

## Source contract reviewed

Implementation was checked against the current RustChain `main` sources on 2026-09-23, especially:

- `rip302_agent_economy.py`
- `rips/docs/RIP-302-agent-economy.md`
- bounty `Scottcjn/rustchain-bounties#685`

## AI assistance disclosure

This deliverable was produced with AI assistance and then validated with deterministic local tests. No production wallet action, escrow movement, third-party account access, or fabricated live result is represented here.

## Payout

Bounty tier requested: **Tier 2 — 75 RTC**. Eligible payout destination: `RTC7f216de84caae4f0fb1bddf3f22e08f76e06bd63`.
