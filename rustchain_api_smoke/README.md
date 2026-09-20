# RustChain API Smoke Checker

A small, dependency-free, **read-only** contract checker for RustChain's public API. It is designed for operators, SDK authors, and agents that need a quick answer to two questions before doing real work:

1. Is the public node reachable?
2. Do the core endpoint response shapes still match what downstream automation expects?

The checker only performs HTTP `GET` requests. It does **not** submit attestations, transfer RTC, create jobs, or mutate node state.

## Checks

By default it validates:

- `GET /health` — HTTP success plus `ok` and `version`
- `GET /epoch` — epoch/slot/enrollment contract
- `GET /api/miners` — top-level pagination plus a representative miner schema

It also records request latency and emits either concise terminal output or machine-readable JSON.

## Run

```bash
python3 rustchain_api_smoke/smoke.py
```

For a node with a self-signed certificate:

```bash
python3 rustchain_api_smoke/smoke.py \
  --node https://50.28.86.131 \
  --insecure
```

Machine-readable output for CI or an agent:

```bash
python3 rustchain_api_smoke/smoke.py --json > rustchain-smoke.json
```

Exit status is `0` only if every endpoint contract passes; otherwise it is `1`.

## Tests

```bash
cd rustchain_api_smoke
python3 -m unittest -v test_smoke.py
```

The fixtures mirror the public node's observed response structure. As of 2026-09-20 the public node reported version `2.2.1-rip200`; `/epoch` exposed epoch/slot/enrollment fields; and `/api/miners` returned a paginated `miners` list.

## Why this is useful

API drift can leave SDKs and autonomous agents silently calling stale routes or parsing obsolete response shapes. A cheap read-only smoke step catches that mismatch before a wallet, miner, or higher-level agent workflow depends on the result. The script is deliberately small enough to run in CI, cron, a health probe, or an agent's preflight sequence without installing a client library.

## Scope and safety

This is a compatibility/availability smoke checker, not a miner and not a security scanner. It performs three public reads per run and does not fuzz, brute-force, or modify anything.
