# Metadata

## Primary title
**How RustChain Changes Its Ledger Without Duplicating the Money**

## Alternate titles
1. **Account Balances → UTXOs: A Safe Ledger Migration, Explained**
2. **Dual-Write Without Double Spend: Inside RustChain’s UTXO Migration**

## Description
RustChain is migrating from an account-style balance model toward UTXOs. The risky part is not creating boxes — it is preserving ownership while two representations overlap.

This technical explainer walks through genesis snapshot construction, `account_mirror_boxes` provenance, atomic UTXO state transitions, deterministic state roots, integrity checks, and administrator-gated rollback.

Source revision reviewed: `217ba85ef9cab3daac0da7b822c79437693444df`

RustChain: https://github.com/Scottcjn/Rustchain

Author: @fsalmon1991  
AI-assisted production; eSpeak TTS; original diagrams.

## Tags
RustChain, UTXO, blockchain, ledger migration, SQLite, Merkle root, double spend, software engineering, distributed systems, Python

## Thumbnail text options
- HOW DO YOU CHANGE A LEDGER WITHOUT DUPLICATING MONEY?
- ACCOUNT BALANCES → UTXOs — SAME VALUE. NEW MODEL.
- DUAL-WRITE WITHOUT DOUBLE SPEND

## Chapters
- 0:00 — Hook — migration is a state-conservation problem
- 0:53 — Deterministic genesis snapshot
- 2:03 — Dual-write provenance
- 3:00 — Atomic UTXO state transition
- 4:13 — Deterministic state root
- 4:56 — Guarded rollback
