#!/usr/bin/env python3
"""Offline reproduction for RustChain Quest #398 Step 2.

Demonstrates the historical balance-schema mismatch failure and the current
schema-dispatch behavior using only Python's sqlite3 standard library.

This does not touch production or any live RustChain node.
"""

import sqlite3

ACCOUNT_UNIT = 1_000_000
DELTA_I64 = 1_440_000
WALLET = "miner-demo"


def balance_columns(cursor):
    return {row[1] for row in cursor.execute("PRAGMA table_info(balances)").fetchall()}


def fixed_apply(cursor, wallet_id, delta_i64, balance_cols):
    """Mirror current _apply_wallet_balance_delta schema dispatch."""
    if {"miner_id", "amount_i64"}.issubset(balance_cols):
        cursor.execute(
            "UPDATE balances SET amount_i64 = amount_i64 + ? WHERE miner_id = ?",
            (delta_i64, wallet_id),
        )
        return

    delta_rtc = delta_i64 / ACCOUNT_UNIT
    if {"miner_pk", "balance_rtc"}.issubset(balance_cols):
        cursor.execute(
            "UPDATE balances SET balance_rtc = balance_rtc + ? WHERE miner_pk = ?",
            (delta_rtc, wallet_id),
        )
        return

    raise RuntimeError("unsupported balances schema for wallet transfer")


def legacy_case():
    db = sqlite3.connect(":memory:")
    db.execute(
        "CREATE TABLE balances(miner_pk TEXT PRIMARY KEY, balance_rtc REAL NOT NULL DEFAULT 0)"
    )
    db.execute(
        "CREATE TABLE epoch_state(epoch INTEGER PRIMARY KEY, settled INTEGER NOT NULL DEFAULT 0)"
    )
    db.execute("INSERT INTO balances VALUES (?, 0)", (WALLET,))
    db.execute("INSERT INTO epoch_state VALUES (1, 0)")
    db.commit()

    try:
        db.execute("BEGIN IMMEDIATE")
        # Historical failure mode: a migrated-schema statement used against a
        # legacy balances table.
        db.execute(
            "UPDATE balances SET amount_i64 = amount_i64 + ? WHERE miner_id = ?",
            (DELTA_I64, WALLET),
        )
        db.execute("UPDATE epoch_state SET settled = 1 WHERE epoch = 1")
        db.commit()
        old_result = "UNEXPECTED_SUCCESS"
    except sqlite3.OperationalError as exc:
        old_result = f"{type(exc).__name__}: {exc}"
        db.rollback()

    after_rollback = (
        db.execute(
            "SELECT balance_rtc FROM balances WHERE miner_pk = ?", (WALLET,)
        ).fetchone()[0],
        db.execute("SELECT settled FROM epoch_state WHERE epoch = 1").fetchone()[0],
    )

    db.execute("BEGIN IMMEDIATE")
    fixed_apply(db.cursor(), WALLET, DELTA_I64, balance_columns(db.cursor()))
    db.execute("UPDATE epoch_state SET settled = 1 WHERE epoch = 1")
    db.commit()

    fixed_result = (
        db.execute(
            "SELECT balance_rtc FROM balances WHERE miner_pk = ?", (WALLET,)
        ).fetchone()[0],
        db.execute("SELECT settled FROM epoch_state WHERE epoch = 1").fetchone()[0],
    )
    return old_result, after_rollback, fixed_result


def canonical_case():
    db = sqlite3.connect(":memory:")
    db.execute(
        "CREATE TABLE balances(miner_id TEXT PRIMARY KEY, amount_i64 INTEGER NOT NULL DEFAULT 0)"
    )
    db.execute("INSERT INTO balances VALUES (?, 0)", (WALLET,))
    db.commit()
    fixed_apply(db.cursor(), WALLET, DELTA_I64, balance_columns(db.cursor()))
    db.commit()
    return db.execute(
        "SELECT amount_i64 FROM balances WHERE miner_id = ?", (WALLET,)
    ).fetchone()[0]


def unknown_schema_case():
    db = sqlite3.connect(":memory:")
    db.execute(
        "CREATE TABLE balances(wallet TEXT PRIMARY KEY, balance REAL NOT NULL DEFAULT 0)"
    )
    db.execute("INSERT INTO balances VALUES (?, 0)", (WALLET,))
    db.commit()
    try:
        fixed_apply(db.cursor(), WALLET, DELTA_I64, balance_columns(db.cursor()))
    except Exception as exc:
        return f"{type(exc).__name__}: {exc}"
    return "UNEXPECTED_SUCCESS"


if __name__ == "__main__":
    old, rollback, fixed = legacy_case()
    print("legacy_pre_fix_error=", old)
    print("legacy_after_rollback(balance_rtc, settled)=", rollback)
    print("legacy_fixed(balance_rtc, settled)=", fixed)
    print("canonical_fixed_amount_i64=", canonical_case())
    print("unknown_schema=", unknown_schema_case())
