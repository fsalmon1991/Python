"""RustChain bounty #398 Step 2: focused reproduction of the inline-pubkey hijack class.

This is a minimal cryptographic model of the known-fixed enrollment bug described
by RustChain's current regression test `node/tests/test_enroll_signature_verification.py`.
It does NOT contact production and does NOT move funds.

Vulnerable pattern: the server verifies an enrollment signature using whatever
public key arrived inline in the same request. An attacker can therefore sign a
victim's enrollment tuple with the attacker's own key and have it verify.

Fixed pattern: compare the inline key with the signing key persisted from the
victim's prior attestation, then verify the signature. The attacker's key is
rejected before signature verification with the equivalent of PUBKEY_MISMATCH.
"""

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat


def raw_public_key(private_key: Ed25519PrivateKey) -> bytes:
    return private_key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)


def vulnerable_enroll(inline_pubkey: bytes, signature: bytes, message: bytes) -> bool:
    """Model the pre-fix trust mistake: request-supplied key is the authority."""
    try:
        Ed25519PublicKey.from_public_bytes(inline_pubkey).verify(signature, message)
        return True
    except InvalidSignature:
        return False


def fixed_enroll(
    stored_attestation_pubkey: bytes,
    inline_pubkey: bytes,
    signature: bytes,
    message: bytes,
) -> tuple[bool, str]:
    """Model current fix: enrollment key must equal prior attestation key."""
    if inline_pubkey != stored_attestation_pubkey:
        return False, "PUBKEY_MISMATCH"
    try:
        Ed25519PublicKey.from_public_bytes(inline_pubkey).verify(signature, message)
        return True, "OK"
    except InvalidSignature:
        return False, "INVALID_ENROLLMENT_SIGNATURE"


def main() -> None:
    victim_wallet = "RTC_VICTIM"
    victim_miner_id = "victim-miner"
    epoch = 4242

    victim_key = Ed25519PrivateKey.generate()
    attacker_key = Ed25519PrivateKey.generate()
    victim_pub = raw_public_key(victim_key)
    attacker_pub = raw_public_key(attacker_key)

    enrollment_message = f"{victim_wallet}|{victim_miner_id}|{epoch}".encode()
    attacker_signature = attacker_key.sign(enrollment_message)

    vulnerable_accepts = vulnerable_enroll(
        attacker_pub, attacker_signature, enrollment_message
    )
    fixed_accepts, fixed_code = fixed_enroll(
        victim_pub, attacker_pub, attacker_signature, enrollment_message
    )

    print("victim_pub == attacker_pub:", victim_pub == attacker_pub)
    print("vulnerable_inline_key_path_accepts_attacker:", vulnerable_accepts)
    print("fixed_attestation_key_binding_accepts_attacker:", fixed_accepts)
    print("fixed_result:", fixed_code)

    assert vulnerable_accepts is True
    assert fixed_accepts is False
    assert fixed_code == "PUBKEY_MISMATCH"
    print("RESULT: reproduction passed")


if __name__ == "__main__":
    main()
