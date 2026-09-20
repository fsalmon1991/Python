# RustChain #398 — Step 2: Reproduce Inline PubKey Hijack Fix

Reviewed RustChain revision: `217ba85ef9cab3daac0da7b822c79437693444df`.

## Vulnerability before the fix

The vulnerable trust decision effectively pinned the public key supplied by the first signed attestation (`signing_pubkey=pubkey_hex or None`). For a pre-existing symbolic miner identity such as `dual-g4-125`, the identifier is not cryptographically derived from a public key. An attacker who reached the attestation endpoint first could therefore sign an attestation with the attacker's own key while claiming the victim's symbolic miner name. If that supplied key was persisted as `signing_pubkey`, `/epoch/enroll` would subsequently treat the attacker's key as the authority for the victim identity and reject the real operator's different key. This is a trust-on-first-use capture of an already-owned identity.

The upstream regression test `tests/test_attest_identity_pinning.py` documents the pre-fix behavior and explicitly asserts that the old `signing_pubkey=pubkey_hex or None` wiring must never return.

## Current fix

The current `/attest/submit` implementation verifies the supplied signature first and then computes a separate `pin_pubkey` decision rather than blindly persisting `pubkey_hex`.

The important branches in `node/rustchain_v2_integrated_v2.2.1_rip200.py` are:

1. If a signing key is already stored, a different supplied key is rejected during enforcing phases, so public requests cannot rotate authority.
2. If the pin is administratively frozen, public requests cannot repin it.
3. For a self-certifying native RTC address, the supplied key is pin-eligible only if `address_from_pubkey(pubkey_hex) == miner`.
4. A genuinely new, non-grandfathered symbolic identity can be TOFU-pinned because there is no previous owner to displace.
5. A grandfathered symbolic identity with no cryptographic derivation is deliberately **not** pinned from a public attestation; administrative enrollment through `/admin/attest/key` is required.
6. `record_attestation_success(...)` receives `signing_pubkey=pin_pubkey`, not the raw caller-supplied public key.

This separates signature validity from identity ownership. A signature proves possession of the submitted key; it does not, by itself, prove that the signer owns an arbitrary pre-existing symbolic name.

## Local reproduction

`repro_inline_pubkey_hijack.py` is a side-effect-free state-machine reproduction. It models the pre-fix and current pin decisions without contacting a live node.

Run:

```bash
python3 repro_inline_pubkey_hijack.py
```

Observed output:

```text
PRE_FIX_CAPTURE_REPRODUCED: True
victim=dual-g4-125
attacker_became_authority_before_fix: True
real_operator_locked_out_before_fix: True
grandfathered_symbolic_first_signer_pinned_after_fix: False
rtc_address_mismatched_key_pinned_after_fix: False
brand_new_identity_can_be_key_bound_after_fix: True
RESULT: hardened pin decision blocks the inline pubkey hijack without disabling safe new-identity enrollment
```

## Why the fix is sufficient for this attack

For the original first-signer capture, the fix closes the ownership gap. An attacker can still generate a valid Ed25519 signature with an attacker-controlled key, but that key is no longer automatically promoted to the authority for a grandfathered symbolic miner. Self-certifying RTC identities have a stronger rule: the key must derive to the address. Existing pins cannot be silently rotated, and a frozen pin requires the admin path. These checks remove every public path used by the original TOFU hijack while preserving onboarding for genuinely new identities.

The phased `log_only` / `enforce_new` / `enforce_all` rollout is operationally important: the identity model is hardened without abruptly disconnecting vintage clients. The security property is strongest once enforcement is enabled; `log_only` intentionally records what would be rejected rather than rejecting the fleet immediately.

## Scope

This reproduction demonstrates understanding of the known **Inline PubKey Hijack** fix requested by Step 2 of `Scottcjn/rustchain-bounties#398`. It does not claim a new vulnerability and does not touch production state.

Payout wallet: `RTC7f216de84caae4f0fb1bddf3f22e08f76e06bd63`

AI assistance was used for code navigation and drafting.