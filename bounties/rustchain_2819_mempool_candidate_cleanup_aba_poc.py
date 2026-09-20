#!/usr/bin/env python3
"""PoC for RustChain bounty #2819: stale-candidate cleanup ABA race.

This is an isolated SQLite reproduction of the cleanup sequence currently used
by UtxoDB.mempool_get_block_candidates(). It does not contact a RustChain node,
move funds, or modify any third-party system.

Current sequence under review:
1. Read mempool rows and collect stale tx_ids.
2. No encompassing BEGIN IMMEDIATE transaction is held for that scan.
3. Later, delete utxo_mempool_inputs and utxo_mempool rows by tx_id only.

If the same tx_id is removed and re-added with a valid transaction between
steps 1 and 3, the stale scanner deletes the replacement transaction (ABA).
"""

import json
import os
import sqlite3
import tempfile
import time


def connection(path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(path, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def main() -> None:
    handle = tempfile.NamedTemporaryFile(delete=False)
    path = handle.name
    handle.close()

    try:
        setup = connection(path)
        setup.executescript(
            """
            CREATE TABLE utxo_mempool (
                tx_id TEXT PRIMARY KEY,
                tx_data_json TEXT NOT NULL,
                fee_nrtc INTEGER DEFAULT 0,
                submitted_at INTEGER NOT NULL,
                expires_at INTEGER NOT NULL
            );
            CREATE TABLE utxo_mempool_inputs (
                box_id TEXT NOT NULL PRIMARY KEY,
                tx_id TEXT NOT NULL,
                FOREIGN KEY (tx_id) REFERENCES utxo_mempool(tx_id)
            );
            """
        )
        now = int(time.time())
        stale_tx = {
            "tx_id": "A",
            "inputs": [{"box_id": "spent_box"}],
            "outputs": [{"address": "x", "value_nrtc": 1000}],
        }
        setup.execute(
            "INSERT INTO utxo_mempool VALUES (?,?,?,?,?)",
            ("A", json.dumps(stale_tx), 0, now, now + 3600),
        )
        setup.execute(
            "INSERT INTO utxo_mempool_inputs VALUES (?,?)", ("spent_box", "A")
        )
        setup.commit()
        setup.close()

        # Scanner reads A and decides it is stale, matching the first phase of
        # mempool_get_block_candidates(). There is no write transaction spanning
        # this decision and the later cleanup DELETEs.
        scanner = connection(path)
        assert scanner.execute(
            "SELECT tx_id FROM utxo_mempool WHERE tx_id='A'"
        ).fetchone()
        stale_tx_ids = ["A"]

        # Concurrent legitimate lifecycle: A is removed and then the same tx_id
        # is re-added with different, currently valid content/input.
        writer = connection(path)
        writer.execute("BEGIN IMMEDIATE")
        writer.execute("DELETE FROM utxo_mempool_inputs WHERE tx_id='A'")
        writer.execute("DELETE FROM utxo_mempool WHERE tx_id='A'")
        writer.commit()

        valid_tx = {
            "tx_id": "A",
            "inputs": [{"box_id": "valid_box"}],
            "outputs": [{"address": "y", "value_nrtc": 1000}],
        }
        writer.execute("BEGIN IMMEDIATE")
        writer.execute(
            "INSERT INTO utxo_mempool VALUES (?,?,?,?,?)",
            ("A", json.dumps(valid_tx), 10, now + 1, now + 3601),
        )
        writer.execute(
            "INSERT INTO utxo_mempool_inputs VALUES (?,?)", ("valid_box", "A")
        )
        writer.commit()
        replacement_before_cleanup = writer.execute(
            "SELECT tx_data_json FROM utxo_mempool WHERE tx_id='A'"
        ).fetchone()
        writer.close()
        assert replacement_before_cleanup is not None

        # Current stale cleanup deletes solely by tx_id. It cannot distinguish
        # the old stale incarnation of A from the replacement incarnation.
        for tx_id in stale_tx_ids:
            scanner.execute(
                "DELETE FROM utxo_mempool_inputs WHERE tx_id = ?", (tx_id,)
            )
            scanner.execute("DELETE FROM utxo_mempool WHERE tx_id = ?", (tx_id,))
        scanner.commit()

        replacement_after_cleanup = scanner.execute(
            "SELECT tx_data_json FROM utxo_mempool WHERE tx_id='A'"
        ).fetchone()
        replacement_claim_after_cleanup = scanner.execute(
            "SELECT box_id FROM utxo_mempool_inputs WHERE tx_id='A'"
        ).fetchone()
        scanner.close()

        print("replacement existed before stale cleanup:", True)
        print(
            "replacement survives stale cleanup:",
            replacement_after_cleanup is not None,
        )
        print(
            "replacement input claim survives:",
            replacement_claim_after_cleanup is not None,
        )

        assert replacement_after_cleanup is None
        assert replacement_claim_after_cleanup is None
        print("REPRODUCED: stale candidate cleanup deleted a valid replacement tx")
    finally:
        try:
            os.unlink(path)
        except FileNotFoundError:
            pass


if __name__ == "__main__":
    main()
