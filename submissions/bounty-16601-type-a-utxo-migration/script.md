# Narration Script — Changing the Ledger Without Duplicating the Money

**Package:** RustChain bounty #16601, Type A full production kit  
**Author credit:** @fsalmon1991  
**Target length:** 3–8 minutes

## 01 — Hook: the dangerous part of a ledger migration

A blockchain can change its code. The hard part is changing its accounting model without accidentally changing who owns what.

RustChain is moving from an account-style balance system toward a UTXO model. That sounds like a database refactor, but it is actually a state-conservation problem. If old balances and new UTXO boxes are both spendable at the same time, one unit of value can exist in two spend paths. If migration output depends on local timing or row order, different nodes can build different state roots from the same balances.

The interesting part of RustChain’s migration code is not that it creates UTXOs. It is the set of rules around creation: deterministic snapshotting, explicit provenance, atomic state transitions, and integrity checks that make the old and new representations agree.

## 02 — A deterministic genesis snapshot

The migration starts from non-zero account balances. Those balances are read in miner-ID order, and the code converts the account model’s micro-RTC units into the UTXO model’s nano-RTC units. In the UTXO layer, one RTC is represented as one hundred million nano-RTC.

For every non-zero wallet, the migration creates one genesis box. Its transaction ID is deterministic: SHA-256 of the fixed prefix `rustchain_genesis:` plus the miner ID. The box ID is also derived deterministically from value, proposition, creation height, transaction ID, and output index.

That matters because the migration is not supposed to invent a different genesis state on each machine. Given the same balance snapshot, nodes should derive the same boxes and the same state root.

The migration also refuses to run over an already-migrated genesis or over existing non-genesis UTXO state. A dry run is observational: it opens the database read-only and computes the boxes it would create instead of quietly initializing or modifying the target.

## 03 — Dual-write needs provenance, not just matching totals

During the transition, RustChain’s UTXO layer can run beside the account-based system in dual-write mode. That creates a subtle risk: matching global totals are not enough to prove that the same value cannot be spent through both models.

RustChain records account-backed UTXO boxes in an `account_mirror_boxes` table. Each entry links a box ID to the account wallet, its value, and the epoch when the mirrored value was created.

This provenance is more useful than a loose metadata tag. It gives later reconciliation code an explicit answer to the question: which UTXO boxes represent value that also exists in the account model?

The integrity checker goes further than comparing one network-wide sum. It checks mirror provenance per wallet and fails if a wallet’s unspent mirrored UTXO value exceeds the corresponding account balance. That catches a class of divergence that a total-only comparison could hide.

## 04 — Spending is an atomic state transition

Once value is in the UTXO set, a transfer is handled as a state transition, not as a sequence of independent balance edits.

`apply_transaction` validates the input shape, rejects duplicate input box IDs, verifies that regular inputs exist and are still unspent, validates read-only data inputs, and enforces conservation for normal transfers: outputs plus fee must equal the consumed input value.

The code then derives the transaction identity from the normalized transaction intent, computes deterministic output box IDs, marks inputs spent, creates outputs, and records the transaction.

When the UTXO database owns the transaction, it opens a SQLite `BEGIN IMMEDIATE` transaction. If validation fails, it aborts. If the state transition succeeds, it commits. The layer also tracks mempool input claims so two pending transactions cannot casually reserve the same box.

This is the key migration idea: the new model is not safe because it has UTXOs. It is safe only if consuming old state and creating new state happens as one coherent transition.

## 05 — State roots make divergence visible

RustChain computes a deterministic Merkle-style state root over unspent boxes. Boxes are ordered by box ID. The leaf hash commits to the box contents and the number of leaves, and odd tree layers use a domain-separated padding hash instead of blindly duplicating the last leaf.

The result is a compact fingerprint of the current unspent set. If two nodes believe they have the same state but produce different roots, the difference is observable.

The migration uses the same idea in dry-run mode: it hashes the preview boxes in memory. After a real migration, the integrity check compares the UTXO total with the account snapshot and also runs the per-wallet mirror-provenance check.

## 06 — Rollback is part of migration safety

A migration path also needs a safe way back. RustChain’s genesis rollback is deliberately fail-closed. It requires an administrator key configured through `RC_ADMIN_KEY`, uses a constant-time key comparison, and refuses rollback if non-genesis UTXO state exists.

Before deleting genesis state, it identifies dependent boxes and evicts mempool transactions that rely on them. It also cleans mirror provenance that no longer backs a live box.

That is the broader lesson in this code: a ledger migration is not just a converter. It is a protocol for preserving ownership while two representations overlap. Deterministic construction tells every node what the new state should be. Provenance says where mirrored value came from. Atomic application controls how state changes. Integrity checks expose divergence. And rollback rules prevent “undo” from becoming a second corruption path.

The implementation reviewed for this production kit is pinned in the sources, so every technical claim can be checked against the exact code revision used here.
