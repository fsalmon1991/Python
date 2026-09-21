# RustChain State Diff

A small **read-only, Python-standard-library-only** utility for RustChain bounty #102 Track A.

It captures canonical JSON snapshots from REST endpoints using HTTP `GET`, then compares two saved snapshots **offline**. The diff flags:

- endpoint additions/removals;
- object field additions/removals;
- JSON type changes;
- list length changes;
- scalar value changes.

This is intended for agent/CI smoke checks where a response can remain HTTP 200 while its shape or state drifts.

## Safety

`state_diff.py` only performs `GET` requests during `snapshot`. `diff` performs no network I/O. It contains no wallet, transaction, mutation, authentication, or trading code.

## Usage

Capture a baseline:

```bash
python state_diff.py snapshot \
  --base-url https://example-rustchain-node.invalid \
  --endpoint /health \
  --endpoint /epoch \
  --endpoint /api/miners \
  --out baseline.json
```

Capture another snapshot later:

```bash
python state_diff.py snapshot \
  --base-url https://example-rustchain-node.invalid \
  --endpoint /health \
  --endpoint /epoch \
  --endpoint /api/miners \
  --out current.json
```

Diff offline:

```bash
python state_diff.py diff baseline.json current.json
```

CI mode:

```bash
python state_diff.py diff baseline.json current.json --fail-on-change
```

Exit codes: `0` success/no fail condition, `1` capture/input error, `2` drift found with `--fail-on-change`.

## Tests

```bash
python -m unittest -v test_state_diff.py
```

The tests use a local in-process HTTP server; they do not contact RustChain or any external service. Current test suite: 5 tests, all passing.
