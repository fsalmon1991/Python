#!/usr/bin/env python3
"""Reproduce a low-severity RustChain UTXO validation gap.

Target reviewed: Scottcjn/Rustchain node/utxo_db.py @
217ba85ef9cab3daac0da7b822c79437693444df

The current apply_transaction() rejects empty outputs only for non-minting
transactions. An internally-authorized mining_reward with outputs=[] therefore
records a confirmed mining_reward row. The one-mining_reward-per-block guard
then rejects the legitimate reward for the same block height.

This is intentionally an offline test. It does not touch a live node or wallet.
Run from a Rustchain checkout, or set RUSTCHAIN_NODE to its node/ directory.
"""

import os
import sys
import tempfile
from pathlib import Path

node_dir = os.environ.get("RUSTCHAIN_NODE")
if node_dir:
    sys.path.insert(0, node_dir)
else:
    # Convenient when this file is copied into / run from a Rustchain checkout.
    candidates = [Path.cwd() / "node", Path.cwd()]
    for candidate in candidates:
        if (candidate / "utxo_db.py").exists():
            sys.path.insert(0, str(candidate))
            break

try:
    from utxo_db import UtxoDB, UNIT
except ImportError as exc:
    raise SystemExit(
        "Could not import utxo_db.py. Run from a Rustchain checkout or set "
        "RUSTCHAIN_NODE=/path/to/Rustchain/node"
    ) from exc


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        db_path = os.path.join(td, "utxo.db")
        db = UtxoDB(db_path)
        db.init_tables()

        height = 424242

        empty_mint = {
            "tx_type": "mining_reward",
            "inputs": [],
            "outputs": [],
            "fee_nrtc": 0,
            "_allow_minting": True,
        }
        empty_ok = db.apply_transaction(empty_mint, height)

        legitimate_mint = {
            "tx_type": "mining_reward",
            "inputs": [],
            "outputs": [{"address": "RTC_TEST_MINER", "value_nrtc": UNIT}],
            "fee_nrtc": 0,
            "_allow_minting": True,
        }
        legit_ok = db.apply_transaction(legitimate_mint, height)

        conn = db._conn()
        try:
            rows = conn.execute(
                "SELECT tx_id, tx_type, outputs_json, block_height "
                "FROM utxo_transactions WHERE block_height = ?",
                (height,),
            ).fetchall()
        finally:
            conn.close()

        print(f"empty authorized mint accepted: {empty_ok}")
        print(f"legitimate same-height mint accepted: {legit_ok}")
        print(f"recorded transactions at height: {len(rows)}")
        for row in rows:
            print(dict(row))

        reproduced = empty_ok is True and legit_ok is False and len(rows) == 1
        print("REPRODUCED" if reproduced else "NOT REPRODUCED")
        return 0 if reproduced else 1


if __name__ == "__main__":
    raise SystemExit(main())
