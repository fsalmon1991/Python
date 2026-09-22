#!/usr/bin/env python3
"""Focused local reproduction of RustChain #398 Step 2: Inline PubKey Hijack.

This harness isolates the ownership check documented in the current RustChain
/epoch/enroll implementation. It does not contact production or mutate RustChain.
"""
import sqlite3
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives import serialization

VICTIM = "RTC_VICTIM"
VICTIM_ID = "victim_001"
EPOCH = 4242


def raw_pub(key):
    return key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    ).hex()


def sign(key, message):
    return key.sign(message.encode()).hex()


def verify(pub_hex, message, sig_hex):
    try:
        Ed25519PublicKey.from_public_bytes(bytes.fromhex(pub_hex)).verify(
            bytes.fromhex(sig_hex), message.encode()
        )
        return True
    except Exception:
        return False


def setup_db():
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE miner_attest_recent (miner TEXT PRIMARY KEY, signing_pubkey TEXT)")
    db.execute("CREATE TABLE miner_header_keys (miner_id TEXT PRIMARY KEY, pubkey_hex TEXT NOT NULL)")
    return db


def vulnerable_enroll(db, miner_pk, miner_id, pubkey_hex, sig_hex):
    """Pre-fix model: inline key proves only possession of itself, not victim ownership."""
    message = f"{miner_pk}|{miner_id}|{EPOCH}"
    if not verify(pubkey_hex, message, sig_hex):
        return 400, "INVALID_SIGNATURE"
    db.execute(
        "INSERT OR REPLACE INTO miner_header_keys (miner_id, pubkey_hex) VALUES (?, ?)",
        (miner_id, pubkey_hex),
    )
    return 200, "OK"


def fixed_enroll(db, miner_pk, miner_id, pubkey_hex, sig_hex):
    """Current model: enrollment key must equal key persisted by attestation."""
    row = db.execute(
        "SELECT signing_pubkey FROM miner_attest_recent WHERE miner = ?", (miner_pk,)
    ).fetchone()
    if not row or not row[0]:
        return 412, "ENROLLMENT_SIGNING_KEY_REQUIRED"
    stored_pubkey = row[0]
    if pubkey_hex != stored_pubkey:
        return 400, "PUBKEY_MISMATCH"
    message = f"{miner_pk}|{miner_id}|{EPOCH}"
    if not verify(pubkey_hex, message, sig_hex):
        return 400, "INVALID_ENROLLMENT_SIGNATURE"
    db.execute(
        "INSERT OR REPLACE INTO miner_header_keys (miner_id, pubkey_hex) VALUES (?, ?)",
        (miner_id, pubkey_hex),
    )
    return 200, "OK"


def main():
    victim_key = Ed25519PrivateKey.generate()
    attacker_key = Ed25519PrivateKey.generate()
    victim_pub = raw_pub(victim_key)
    attacker_pub = raw_pub(attacker_key)
    message = f"{VICTIM}|{VICTIM_ID}|{EPOCH}"
    attacker_sig = sign(attacker_key, message)

    db = setup_db()
    db.execute(
        "INSERT INTO miner_attest_recent (miner, signing_pubkey) VALUES (?, ?)",
        (VICTIM, victim_pub),
    )
    db.execute(
        "INSERT INTO miner_header_keys (miner_id, pubkey_hex) VALUES (?, ?)",
        (VICTIM_ID, victim_pub),
    )

    old_status, old_code = vulnerable_enroll(
        db, VICTIM, VICTIM_ID, attacker_pub, attacker_sig
    )
    old_mapping = db.execute(
        "SELECT pubkey_hex FROM miner_header_keys WHERE miner_id = ?", (VICTIM_ID,)
    ).fetchone()[0]
    assert old_status == 200
    assert old_mapping == attacker_pub

    db.execute(
        "UPDATE miner_header_keys SET pubkey_hex = ? WHERE miner_id = ?",
        (victim_pub, VICTIM_ID),
    )
    new_status, new_code = fixed_enroll(
        db, VICTIM, VICTIM_ID, attacker_pub, attacker_sig
    )
    new_mapping = db.execute(
        "SELECT pubkey_hex FROM miner_header_keys WHERE miner_id = ?", (VICTIM_ID,)
    ).fetchone()[0]
    assert new_status == 400
    assert new_code == "PUBKEY_MISMATCH"
    assert new_mapping == victim_pub

    victim_sig = sign(victim_key, message)
    ok_status, ok_code = fixed_enroll(db, VICTIM, VICTIM_ID, victim_pub, victim_sig)
    assert (ok_status, ok_code) == (200, "OK")

    print("pre_fix_attacker_request:", old_status, old_code)
    print("pre_fix_mapping_hijacked:", old_mapping == attacker_pub)
    print("post_fix_attacker_request:", new_status, new_code)
    print("post_fix_mapping_preserved:", new_mapping == victim_pub)
    print("post_fix_legitimate_request:", ok_status, ok_code)
    print("RESULT: PASS")


if __name__ == "__main__":
    main()
