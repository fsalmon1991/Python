# Sources and claim map

All source links are pinned to RustChain commit `217ba85ef9cab3daac0da7b822c79437693444df`.

## Primary sources

1. `node/utxo_db.py`  
   https://github.com/Scottcjn/Rustchain/blob/217ba85ef9cab3daac0da7b822c79437693444df/node/utxo_db.py

2. `node/utxo_genesis_migration.py`  
   https://github.com/Scottcjn/Rustchain/blob/217ba85ef9cab3daac0da7b822c79437693444df/node/utxo_genesis_migration.py

## Claim → source

| Claim in narration | Source |
|---|---|
| Phase 1 runs beside the account model in dual-write mode | `utxo_db.py` module docstring |
| Atomic application, spent-state double-spend prevention, deterministic root, mempool claim tracking | `utxo_db.py` module docstring and transaction/mempool methods |
| 1 RTC = 100,000,000 nanoRTC in the UTXO model | `utxo_db.py` constant `UNIT` |
| Migration reads non-zero balances ordered by miner ID | `utxo_genesis_migration.py::load_account_balances` |
| Genesis tx ID is SHA-256 of `rustchain_genesis:` + miner ID | `utxo_genesis_migration.py::compute_genesis_tx_id` |
| One deterministic genesis box per non-zero account balance | migration rules and `migrate()` loop |
| Migration refuses existing genesis and non-genesis UTXO state | `check_existing_genesis`, `check_existing_non_genesis_utxo_state`, `migrate` |
| Dry run opens read-only and computes preview boxes | `_open_readonly`, `_has_complete_utxo_schema`, `migrate(dry_run=True)` |
| `account_mirror_boxes` records account↔UTXO provenance | `utxo_db.py` schema and migration insert |
| Integrity checking includes a per-wallet mirror-provenance assertion | `utxo_db.py::_check_mirror_provenance` |
| Normal transfers reject duplicate/spent/missing inputs and non-conserving value | `utxo_db.py::apply_transaction` |
| Owned transactions use `BEGIN IMMEDIATE`, rollback on abort, commit on success | `utxo_db.py::apply_transaction` |
| Mempool input claims prevent pending double-spend reservations | `utxo_db.py::mempool_add`, `utxo_mempool_inputs` schema |
| State root sorts unspent boxes and binds count/content; odd layers use domain-separated padding | `utxo_db.py::compute_state_root` |
| Rollback requires `RC_ADMIN_KEY`, refuses non-genesis live state, evicts dependencies, cleans provenance | `utxo_genesis_migration.py::_require_rollback_authorization`, `rollback_genesis` |

## Deliberate exclusions

No mining-profit, ROI, price, benchmark, throughput, or current wallet-count claims are made. No claim is made that the UTXO database module alone authenticates spenders; its module documentation places Ed25519 proof verification at the endpoint layer.
