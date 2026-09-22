# RustChain #398 — Step 2: Inline PubKey Hijack Reproduction

**Claimant:** @fsalmon1991  
**Bounty:** Scottcjn/rustchain-bounties #398, Step 2 — Reproduce a Known Fix  
**Selected BuilderFred audit item:** Inline PubKey Hijack  
**Requested reward:** 15 RTC  
**RTC wallet:** `RTC7f216de84caae4f0fb1bddf3f22e08f76e06bd63`  
**AI assistance:** Yes. This write-up and local reproduction were prepared with AI assistance. No production exploitation was performed.

## What the attack looked like before the fix

The vulnerable trust boundary was `/epoch/enroll`. An enrollment request could carry an inline Ed25519 public key and signature. Cryptographically, a signature only proves that the caller controls the private key corresponding to the **supplied** public key. It does not by itself prove that this key belongs to the miner identity named in the request.

That distinction matters because enrollment also controls the mapping used later for miner/block-header identity. RustChain's own regression test documents the original defect directly: without ownership verification, a caller who knew a victim miner ID could enroll using an attacker-controlled inline public key, including replacing the victim's `miner_header_keys` mapping. See `node/tests/test_enroll_signature_verification.py`, whose module header describes the exact hijack and whose `test_enrollment_pubkey_mismatch_with_attacker_key` constructs an attacker keypair, signs a victim enrollment message, and expects `PUBKEY_MISMATCH` from the fixed implementation.

A pre-fix attack therefore did not require breaking Ed25519. The attacker could generate a completely valid Ed25519 keypair, sign the canonical `miner_pubkey|miner_id|epoch` text using the attacker's private key, submit the attacker's public key inline while naming the victim miner, and rely on the server accepting that self-consistent key/signature pair. If the server then used `INSERT OR REPLACE` for the miner-to-header-key mapping, the request could replace the victim's identity mapping with the attacker's key.

## What the current fix does

At current RustChain commit `217ba85ef9cab3daac0da7b822c79437693444df`, the enrollment route no longer treats the inline key as self-authenticating identity evidence.

In `node/rustchain_v2_integrated_v2.2.1_rip200.py` around lines 6960–7050, the route:

1. validates that `signature` and `public_key` are strings;
2. loads `miner_attest_recent.signing_pubkey` for the `miner_pubkey` being enrolled;
3. rejects the request with `PUBKEY_MISMATCH` when the inline `public_key` differs from the key stored during that miner's latest attestation;
4. only then verifies the Ed25519 signature over `miner_pubkey|miner_id|epoch`;
5. rejects a signed enrollment with no stored attestation signing key unless the explicit legacy escape hatch is enabled;
6. rejects unsigned enrollment by default unless `ENROLL_ALLOW_UNSIGNED_LEGACY=1` is deliberately configured.

The critical change is step 3: possession of *some* valid private key is no longer enough. The request key must be the same key that was bound to the miner during attestation.

RustChain's regression suite reinforces that contract. `node/tests/test_enroll_signature_verification.py` checks that a signed request without a stored attestation key receives `ENROLLMENT_SIGNING_KEY_REQUIRED`, incomplete signature material receives `INCOMPLETE_SIGNATURE`, and an attacker-signed victim enrollment receives HTTP 400 / `PUBKEY_MISMATCH`.

## Local reproduction

The full upstream repository could not be cloned inside this execution environment because outbound git traffic failed at the environment proxy. I did not pretend that a full upstream test suite ran. Instead, I built and executed a focused local reproduction of the exact ownership boundary using SQLite plus Ed25519 from Python's `cryptography` package.

Artifacts:

- Harness: `bounty_reports/rustchain_398_step2_inline_pubkey_repro.py`
- Captured output: `bounty_reports/rustchain_398_step2_inline_pubkey_repro_output.txt`

The harness creates the two relevant tables (`miner_attest_recent` and `miner_header_keys`), stores a victim attestation public key, creates an independent attacker keypair, and has the attacker sign the victim's canonical enrollment message.

It then evaluates two models:

**Pre-fix model:** verify the signature against the caller-supplied inline key and then `INSERT OR REPLACE` the header-key mapping. Result: the attacker request returns success and the victim mapping changes to the attacker's public key.

**Fixed model:** load the victim's attestation key first, compare it to the inline key, and reject before changing state when they differ. Result: the attacker request returns `PUBKEY_MISMATCH`, the victim mapping remains unchanged, and a legitimate request signed by the victim's attested key still succeeds.

Actual local output:

```text
pre_fix_attacker_request: 200 OK
pre_fix_mapping_hijacked: True
post_fix_attacker_request: 400 PUBKEY_MISMATCH
post_fix_mapping_preserved: True
post_fix_legitimate_request: 200 OK
RESULT: PASS
```

Harness SHA-256: `22096773e459c3f14e19df911b150ac952eb46d82f7af939399f31bb486f2f77`  
Output SHA-256: `41940b20940e7bde79dd099a89a83cc8fc1c70f8021e7eaaa185ae1e30e09a3c`

## Why the fix is sufficient for this vulnerability

For the specific Inline PubKey Hijack, the fix is sufficient because it changes the proof from "the caller owns the key it just supplied" to "the caller owns the same key already bound to this miner through attestation." An attacker-generated key can still produce a perfectly valid Ed25519 signature, but it fails the identity-binding check before it can replace the miner's header key.

The fail-closed cases also matter. Missing stored key material does not silently downgrade to accepting any signed request, and partial signature data does not fall into an unsigned path. These close common compatibility-path bypasses around an otherwise-correct signature check.

There is one deliberate residual risk: operators can enable `ENROLL_ALLOW_UNSIGNED_LEGACY=1`. That is an explicit migration compatibility mode, not a cryptographic bypass of the default path, but it weakens the ownership guarantee and therefore should stay disabled in public production deployments, be loudly logged/monitored, and ideally have a removal deadline.

This fix does **not** prove that the underlying hardware attestation itself is impossible to spoof; it solves a narrower identity-binding bug. Hardware authenticity, replay resistance, and attestation-key integrity remain separate controls. For the named BuilderFred issue, however, binding enrollment to the stored attestation signing key directly removes the attacker-controlled inline-key substitution that enabled the hijack.

## Source references

- Current enrollment implementation: https://github.com/Scottcjn/Rustchain/blob/217ba85ef9cab3daac0da7b822c79437693444df/node/rustchain_v2_integrated_v2.2.1_rip200.py
- Regression tests: https://github.com/Scottcjn/Rustchain/blob/217ba85ef9cab3daac0da7b822c79437693444df/node/tests/test_enroll_signature_verification.py
- Quest requirements: https://github.com/Scottcjn/rustchain-bounties/issues/398
