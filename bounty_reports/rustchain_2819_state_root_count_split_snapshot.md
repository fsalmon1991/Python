# RustChain #2819 — `/utxo/state_root` can return a root and count from different snapshots

**Claimant:** `@fsalmon1991`  
**RTC wallet:** `RTC7f216de84caae4f0fb1bddf3f22e08f76e06bd63`  
**Suggested severity:** Low  
**Requested bounty:** 25 RTC under rustchain-bounties #2819

## Summary

The `/utxo/state_root` endpoint intends to report a Merkle `state_root` and `unspent_count` for the same UTXO set. It even carries a comment saying the two values must describe the same set. However, the endpoint only reuses one SQLite connection; it never opens a read transaction before the two separate SELECTs.

`UtxoDB.compute_state_root(conn=conn)` performs the root query on the caller-supplied connection and returns. `UtxoDB.count_unspent(conn=conn)` then performs a second SELECT. With no explicit `BEGIN`, SQLite does not pin a snapshot across those statements. A writer that commits between them can therefore make the response internally inconsistent: the root describes state A while `unspent_count` describes state B.

This is the same database-snapshot class that RustChain already fixed in `integrity_check()`, where the implementation explicitly starts a read transaction when it owns the connection so totals and the root cannot straddle a concurrent settlement.

## Current code path

`node/utxo_endpoints.py`:

```python
@utxo_bp.route('/state_root')
def utxo_state_root():
    # One connection: the root and the count it is reported beside must describe
    # the same UTXO set (#2819, robin1121).
    conn = sqlite3.connect(_db_path)
    try:
        root = _utxo_db.compute_state_root(conn=conn)
        count = _utxo_db.count_unspent(conn=conn)
    finally:
        conn.close()
```

`node/utxo_db.py::compute_state_root()` does not begin a transaction for a caller-supplied connection; it executes one SELECT and returns. Therefore the subsequent count query is not guaranteed to use the root query's snapshot.

## Focused reproduction

A minimal SQLite reproduction is included beside this report as `rustchain_2819_state_root_count_split_snapshot_repro.py`.

Observed output:

```text
no_explicit_begin: 1 2
explicit_begin_snapshot: 1 1
after_snapshot_ends: 2
```

The first pair demonstrates the endpoint's current transaction shape: one connection, two SELECT statements, no explicit transaction. The second SELECT observes a writer's commit that occurred between the reads.

The second pair demonstrates the required behavior: an explicit read transaction pins both reads to the same snapshot, even while another connection commits a new box under WAL mode.

## Deterministic endpoint-level regression test

A focused upstream regression can make the interleaving deterministic:

1. Seed one unspent box.
2. Wrap/patch `compute_state_root()` so that, after computing the root but before returning to the endpoint, another SQLite connection inserts and commits a second box.
3. Call `/utxo/state_root`.
4. Before the fix, the response can pair the one-box root with `unspent_count == 2`.
5. After the fix, the endpoint should return the one-box root with `unspent_count == 1`; once the request's read transaction ends, a fresh query sees two boxes.

This mirrors the existing `IntegrityRaceTest` strategy already used for the related integrity-report snapshot bug.

## Impact

This does **not** create RTC, spend funds, or directly alter consensus. The impact is integrity/observability:

- API clients can receive an impossible `(state_root, unspent_count)` pair that never existed at one database snapshot.
- Indexers/monitors can emit false state-integrity alarms during ordinary concurrent writes.
- Any external verifier treating the count as metadata for the returned root can record or compare inconsistent state.

Because the effect is an inconsistent read/report rather than fund loss or consensus bypass, I classify it as **Low** and request the #2819 Low tier rather than inflating severity.

## Suggested fix

Pin one read transaction around both reads:

```python
conn = sqlite3.connect(_db_path)
try:
    conn.execute("BEGIN")
    root = _utxo_db.compute_state_root(conn=conn)
    count = _utxo_db.count_unspent(conn=conn)
finally:
    try:
        conn.rollback()
    finally:
        conn.close()
```

An even cleaner option is a `UtxoDB.state_root_with_count()` helper that owns the read transaction and returns both values from one snapshot, which avoids future callers repeating the same mistake.

## Duplicate check

I searched current RustChain issues for `/utxo/state_root`, `unspent_count`, snapshot/concurrency language, and state-root reports. The closest items I found were:

- RustChain #2075 — block producer commits the wrong *model's* root in UTXO mode (different code path/bug).
- RustChain #8177 — state-root count-prefix endianness concern (different root construction issue).
- Existing `IntegrityRaceTest` / #2819 robin1121 regression — the related integrity-report split-snapshot bug, already fixed there; this report identifies the same missing transaction boundary in the separate `/utxo/state_root` route.

I did not find an existing issue covering the root/count pair returned by `/utxo/state_root`.

## Validation limits

I did not attack or mutate production. Validation is source review plus a local focused SQLite concurrency reproduction. I am not claiming the full upstream RustChain test suite was run in this environment.
