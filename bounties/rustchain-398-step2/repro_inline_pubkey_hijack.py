#!/usr/bin/env python3
"""Standalone reproduction of RustChain's pre-fix inline public-key pinning bug.

This intentionally models only the pin-decision state machine. It does not
contact a RustChain node, submit an attestation, or mutate production state.
"""


def vulnerable_pin(existing_pin, supplied_pubkey):
    """Pre-fix behavior: first supplied key becomes authority."""
    return existing_pin or supplied_pubkey or None


def hardened_pin(*, stored_pin, supplied_pubkey, is_rtc_hex,
                 derives_to_addr, is_grandfathered, is_pin_frozen):
    """Model the current pin decision in rustchain_v2...rip200.py."""
    if stored_pin:
        return None                 # keep existing via DB COALESCE
    if is_pin_frozen:
        return None                 # admin must set a replacement
    if is_rtc_hex:
        return supplied_pubkey if derives_to_addr else None
    if not is_grandfathered:
        return supplied_pubkey      # TOFU is allowed only for a brand-new id
    return None                     # legacy symbolic id: admin enrollment required


def main():
    victim = "dual-g4-125"          # symbolic, pre-existing identity
    attacker_key = "aa" * 32
    real_operator_key = "bb" * 32

    # BEFORE: attacker is first to send a signed attestation for victim.
    captured = vulnerable_pin(None, attacker_key)
    assert captured == attacker_key
    real_operator_blocked = real_operator_key != captured
    assert real_operator_blocked

    # AFTER: same first-signer attempt cannot pin a grandfathered symbolic id.
    decided = hardened_pin(
        stored_pin=None,
        supplied_pubkey=attacker_key,
        is_rtc_hex=False,
        derives_to_addr=False,
        is_grandfathered=True,
        is_pin_frozen=False,
    )
    assert decided is None

    # Self-certifying RTC address also fails closed if key does not derive to it.
    rtc_mismatch = hardened_pin(
        stored_pin=None,
        supplied_pubkey=attacker_key,
        is_rtc_hex=True,
        derives_to_addr=False,
        is_grandfathered=False,
        is_pin_frozen=False,
    )
    assert rtc_mismatch is None

    # A genuinely new non-grandfathered identity can still be born key-bound.
    new_identity = hardened_pin(
        stored_pin=None,
        supplied_pubkey=real_operator_key,
        is_rtc_hex=False,
        derives_to_addr=False,
        is_grandfathered=False,
        is_pin_frozen=False,
    )
    assert new_identity == real_operator_key

    print("PRE_FIX_CAPTURE_REPRODUCED: True")
    print(f"victim={victim}")
    print("attacker_became_authority_before_fix: True")
    print("real_operator_locked_out_before_fix: True")
    print("grandfathered_symbolic_first_signer_pinned_after_fix: False")
    print("rtc_address_mismatched_key_pinned_after_fix: False")
    print("brand_new_identity_can_be_key_bound_after_fix: True")
    print("RESULT: hardened pin decision blocks the inline pubkey hijack without disabling safe new-identity enrollment")


if __name__ == "__main__":
    main()
