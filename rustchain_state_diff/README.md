# RustChain State Diff

`rustchain_state_diff` is a dependency-free, **read-only** operator tool that records a compact RustChain public-state snapshot and compares it with a later snapshot.

It answers a different question from an API schema smoke test: not “does the endpoint still have the expected shape?”, but **“what actually changed since the last observation?”**

## What it reads

The capture command performs exactly three public `GET` requests:

- `/health`
- `/epoch`
- `/api/miners`

It does not attest, mine, transfer RTC, create jobs, mutate settings, or call any write endpoint.

## Capture

```bash
python3 rustchain_state_diff/state_diff.py capture \
  --node https://rustchain.org \
  --output before.json
```

Later:

```bash
python3 rustchain_state_diff/state_diff.py capture \
  --node https://rustchain.org \
  --output after.json
```

For a node using a self-signed certificate, add `--insecure` explicitly.

## Diff

Human-readable:

```bash
python3 rustchain_state_diff/state_diff.py diff before.json after.json
```

Machine-readable:

```bash
python3 rustchain_state_diff/state_diff.py diff before.json after.json --json
```

CI/cron health regression gate:

```bash
python3 rustchain_state_diff/state_diff.py diff before.json after.json \
  --json --fail-on-regression
```

With `--fail-on-regression`, exit code `2` is reserved for an observed `health.ok: true -> non-true` transition. Ordinary epoch advancement, version changes, and miner churn remain visible without being mislabeled as protocol failures.

## What is compared

The normalized snapshot records:

- node health and node version
- epoch, slot, blocks-per-epoch, and enrolled-miner values when returned
- miner counts and pagination totals
- stable miner identity plus selected operational fields such as architecture/family, last attestation, fingerprint result, and status

The diff reports:

- scalar health/epoch/count changes
- miners added since the earlier snapshot
- miners removed from the returned set
- per-miner operational field changes

A removed miner is **not automatically labeled a regression**, because pagination or normal epoch churn can explain disappearance from a returned set.

## Tests

```bash
cd rustchain_state_diff
python3 -m unittest -v test_state_diff.py
```

The tests cover normalization of the currently observed public response shapes, miner add/remove/change detection, regression classification, version changes, and malformed miner payloads.

## Safety

This is monitoring support, not a miner, scanner, or attack tool. Capture traffic is bounded to three documented public reads per invocation. No credentials or wallet keys are accepted by the program.
