# Self-Audit: node/utxo_db.py

## Wallet
RTC7f216de84caae4f0fb1bddf3f22e08f76e06bd63

## Module reviewed
- Path: node/utxo_db.py
- Commit: 217ba85
- Lines reviewed: whole file, with focus on transaction application and mempool paths
- Source commit: https://github.com/Scottcjn/Rustchain/commit/217ba85ef9cab3daac0da7b822c79437693444df

## Deliverable: 3 specific findings

### 1. Expired mempool claims can remain visible to the direct double-spend query
- Severity: low
- Location: node/utxo_db.py — mempool_check_double_spend()
- Description: mempool_check_double_spend() directly queries utxo_mempool_inputs but does not call mempool_clear_expired() first and does not join against utxo_mempool.expires_at. An expired transaction therefore remains reported as an active pending claim until some other code path happens to run cleanup. This makes the method's name/contract stronger than what it actually guarantees and can create false-positive “already claimed” results for callers that use this helper directly.
- Reproduction:
  1. Add a valid mempool transaction that claims box A.
  2. Set the corresponding utxo_mempool.expires_at to a timestamp in the past without calling mempool_clear_expired().
  3. Call mempool_check_double_spend(A).
  4. Observe True even though the claim has expired.
  5. Call mempool_clear_expired(), then call mempool_check_double_spend(A) again; observe False.
- Suggested fix: either call mempool_clear_expired() at the start of mempool_check_double_spend(), or query through utxo_mempool with expires_at > now so the helper is correct without requiring a cleanup side effect.

### 2. Block-candidate max_count is not type-validated at the public method boundary
- Severity: low
- Location: node/utxo_db.py — mempool_get_block_candidates(max_count=100)
- Description: the method immediately evaluates `max_count <= 0` and later multiplies max_count by MAX_MEMPOOL_CANDIDATE_SCAN_FACTOR. Non-integer caller values such as None or strings raise TypeError instead of producing a bounded validation failure. Other public methods in this module explicitly reject booleans/non-integers, so this is inconsistent with the module's defensive-input pattern.
- Reproduction:
  1. Initialize the UTXO tables.
  2. Call `db.mempool_get_block_candidates(None)` and observe TypeError on the comparison.
  3. Call `db.mempool_get_block_candidates("10")` and observe TypeError on the comparison.
  4. Compare with get_unspent_for_address(limit=...) and get_coin_select_candidates(max_inputs=...), which validate type/range explicitly.
- Suggested fix: require `type(max_count) is int` (or equivalent int-but-not-bool validation) and reject values below 1 or above an explicit caller cap.

### 3. Public compute_tx_id() helper does not accept the normal pre-application output shape
- Severity: informational
- Location: node/utxo_db.py — compute_tx_id()
- Description: compute_tx_id() sorts each output by `x['box_id']`, but normal transaction outputs supplied to apply_transaction() contain address/value/metadata and do not yet have box_id values; box IDs are generated only after the production transaction identity is computed. The helper is also documented as a public API while production intentionally uses a different canonical identity algorithm. External consumers following the transaction shape documented by apply_transaction() therefore cannot use compute_tx_id() without first inventing fields that do not exist yet.
- Reproduction:
  1. Build the documented transfer output: `{"address": "bob", "value_nrtc": 1000}`.
  2. Call compute_tx_id(inputs, [that_output], timestamp).
  3. Observe KeyError: 'box_id'.
  4. Pass an artificial box_id and compare the resulting algorithm to apply_transaction(), which hashes tx_type, sorted input IDs, data_inputs, output intent, fee, timestamp/block height and then derives output box IDs afterward.
- Suggested fix: either deprecate/rename the helper as a legacy box-id-based utility, or make it consume the same normalized output intent and canonical fields as apply_transaction() so there is one transaction-ID definition.

## Known failures of this audit
- I did not execute the complete RustChain test suite or a live node; this was a source-level audit of the current main commit.
- I did not review endpoint-layer Ed25519 verification, so this audit makes no claim about authorization bypasses.
- I did not inspect every historical issue/PR for semantic duplicates; I searched the bounty tracker for the exact helper/function names before filing.
- Finding 1 is an availability/correctness issue, not a demonstrated fund-loss path.
- Finding 2 depends on whether untrusted or loosely typed callers can reach this method; its severity is therefore intentionally low.
- Finding 3 is an API-consistency defect, not a consensus vulnerability.

## Confidence
- Overall confidence: 0.79
- Per-finding confidence: [0.90, 0.83, 0.72]

## What I would test next
- Add a focused test proving an expired mempool claim cannot make mempool_check_double_spend() return True.
- Trace every caller of mempool_get_block_candidates() to determine whether malformed max_count values can cross an API boundary.
- Add a property test asserting public transaction-ID helpers and apply_transaction() share one canonical intent definition, or explicitly document why they differ.

## AI disclosure
This audit was produced with AI assistance under the direction of @fsalmon1991 and was checked against the current source before submission.
