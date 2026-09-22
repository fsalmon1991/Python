#!/usr/bin/env python3
"""Focused SQLite reproduction for RustChain #2819 state-root/count snapshot bug.

This demonstrates SQLite snapshot semantics only; it does not contact a live RustChain node.
"""

import os
import sqlite3
import tempfile


fd, path = tempfile.mkstemp(suffix=".db")
os.close(fd)
try:
    setup = sqlite3.connect(path)
    setup.execute("CREATE TABLE utxo_boxes (box_id TEXT PRIMARY KEY, spent_at INTEGER)")
    setup.execute("INSERT INTO utxo_boxes(box_id, spent_at) VALUES (?, NULL)", ("box1",))
    setup.commit()
    setup.close()

    reader = sqlite3.connect(path)
    writer = sqlite3.connect(path)

    # Mirrors the endpoint pattern: same connection, but no explicit BEGIN.
    first = reader.execute(
        "SELECT COUNT(*) FROM utxo_boxes WHERE spent_at IS NULL"
    ).fetchone()[0]
    writer.execute(
        "INSERT INTO utxo_boxes(box_id, spent_at) VALUES (?, NULL)", ("box2",)
    )
    writer.commit()
    second = reader.execute(
        "SELECT COUNT(*) FROM utxo_boxes WHERE spent_at IS NULL"
    ).fetchone()[0]
    print("no_explicit_begin:", first, second)

    reader.close()
    writer.close()

    # Reset and demonstrate the correct pinned-snapshot behavior.
    setup = sqlite3.connect(path)
    setup.execute("DELETE FROM utxo_boxes")
    setup.execute("INSERT INTO utxo_boxes(box_id, spent_at) VALUES (?, NULL)", ("box1",))
    setup.commit()
    setup.close()

    reader = sqlite3.connect(path)
    writer = sqlite3.connect(path)
    reader.execute("PRAGMA journal_mode=WAL")
    writer.execute("PRAGMA journal_mode=WAL")
    reader.execute("BEGIN")

    first = reader.execute(
        "SELECT COUNT(*) FROM utxo_boxes WHERE spent_at IS NULL"
    ).fetchone()[0]
    writer.execute(
        "INSERT INTO utxo_boxes(box_id, spent_at) VALUES (?, NULL)", ("box2",)
    )
    writer.commit()
    second = reader.execute(
        "SELECT COUNT(*) FROM utxo_boxes WHERE spent_at IS NULL"
    ).fetchone()[0]
    print("explicit_begin_snapshot:", first, second)

    reader.rollback()
    latest = reader.execute(
        "SELECT COUNT(*) FROM utxo_boxes WHERE spent_at IS NULL"
    ).fetchone()[0]
    print("after_snapshot_ends:", latest)

    assert (first, second, latest) == (1, 1, 2)
finally:
    try:
        os.unlink(path)
    except OSError:
        pass
