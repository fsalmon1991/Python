# RustChain Quest #398 — Step 2: SQL Schema Mismatch Fix Reproduction

**Claimant:** `fsalmon1991`  
**Requested reward:** 15 RTC  
**Wallet:** `RTC7f216de84caae4f0fb1bddf3f22e08f76e06bd63`  
**AI-assisted:** yes; source inspection, test drafting, and documentation used AI assistance.  
**Production impact:** none — this reproduction uses only in-memory SQLite databases.

## Vulnerability / failure before the fix

The historical SQL-schema mismatch occurred because RustChain has had more than one legitimate `balances` table shape. A legacy database can expose a floating-point RTC balance keyed as:

```text
balances(miner_pk, balance_rtc)
```

while the newer canonical shape stores micro-RTC integers keyed as:

```text
balances(miner_id, amount_i64)
```

A settlement implementation that hard-codes the newer statement:

```sql
UPDATE balances
SET amount_i64 = amount_i64 + ?
WHERE miner_id = ?
```

fails immediately when it is pointed at the older schema. SQLite raises `no such column: amount_i64`. If that update is inside the epoch settlement transaction, the credit and the settlement marker roll back together. The bug is therefore primarily an availability / reward-delivery failure: a valid miner can remain unpaid because the code guessed the wrong schema family.

## Current fix

Current RustChain code no longer blindly assumes one schema. In `node/rustchain_v2_integrated_v2.2.1_rip200.py`:

- `_balance_columns()` reads `PRAGMA table_info(balances)`.
- `_supports_wallet_balance_updates()` checks for known supported column families rather than inferring from unrelated state.
- `_apply_wallet_balance_delta()` dispatches to the integer `miner_id/amount_i64` update when that shape exists.
- For the legacy `miner_pk/balance_rtc` shape, it converts the micro-RTC delta to RTC and updates the floating-point column instead.
- Unknown table shapes fail closed with `RuntimeError("unsupported balances schema for wallet transfer")` rather than silently guessing.

The settlement path also uses transactional locking (`BEGIN IMMEDIATE`) so the schema-aware balance write remains part of the same atomic settlement decision.

## Local reproduction

I reproduced the failure and the fixed behavior with Python 3.13.5 and the standard-library `sqlite3` module. The harness is committed here:

- `bounty_reports/repro_sql_schema_mismatch.py`

It builds three in-memory databases:

1. **Legacy schema** — proves the pre-fix migrated-schema update raises an SQLite error and that rollback leaves both balance and `epoch_state.settled` unchanged.
2. **Canonical schema** — proves the fixed dispatch credits the exact micro-RTC integer.
3. **Unknown schema** — proves the fixed dispatch refuses to guess.

Executed output:

```text
legacy_pre_fix_error= OperationalError: no such column: amount_i64
legacy_after_rollback(balance_rtc, settled)= (0.0, 0)
legacy_fixed(balance_rtc, settled)= (1.44, 1)
canonical_fixed_amount_i64= 1440000
unknown_schema= RuntimeError: unsupported balances schema for wallet transfer
```

The 1.44 RTC / 1,440,000 micro-RTC test delta is intentional: it makes the unit conversion visible instead of hiding it behind an integer-looking amount.

## Why the fix is sufficient for this known failure class

For the SQL-schema mismatch itself, the fix addresses the root problem: the settlement code no longer assumes that every valid database has the same balance column names or units. It first identifies a supported schema family and then executes the corresponding update. This prevents a legacy database from reaching an SQL statement that references columns it does not contain.

Failing closed on an unrecognized shape is equally important. Automatically selecting a “closest-looking” column would turn a clean availability bug into possible accounting corruption. A hard failure leaves the settlement retryable after migration or operator correction.

The fix does not mean arbitrary historical schemas are supported forever. Its security property is narrower and stronger: **known schemas are handled explicitly; unknown schemas are rejected.** That is the right behavior for money-moving code.

## Residual considerations

Schema compatibility should continue to be covered by migration tests because future migrations can introduce a third valid representation or temporarily leave both old and new columns present. Tests should verify not only that settlement succeeds, but that units are not double-converted and that a rollback leaves the epoch unsettled when any balance write fails.

## Source basis

Current source reviewed at RustChain commit:

`217ba85ef9cab3daac0da7b822c79437693444df`

Relevant current symbols:

- `node/rustchain_v2_integrated_v2.2.1_rip200.py::_balance_columns`
- `node/rustchain_v2_integrated_v2.2.1_rip200.py::_supports_wallet_balance_updates`
- `node/rustchain_v2_integrated_v2.2.1_rip200.py::_apply_wallet_balance_delta`
- `node/rewards_implementation_rip200.py::settle_epoch_rip200`

This is a reproduction of a **known fixed issue** for Quest #398 Step 2. It is not presented as a new vulnerability and it does not touch a production node.