# RustChain `/attest/submit` Live Fuzzing Report

Bounty: Scottcjn/rustchain-bounties#1112  
Researcher: `fsalmon1991`  
Run date: 2026-09-19  
Target: `POST https://50.28.86.131/attest/submit`  
Requests: **100**  
Cost: **$0**

## Executive summary

I executed a bounded, non-destructive live-production fuzz pass against the endpoint explicitly authorized by bounty #1112. The run sent exactly 100 malformed/adversarial JSON payloads across four equal categories:

- 25 missing/partial-field payloads
- 25 wrong-type payloads
- 25 oversized-but-bounded field payloads (1 KiB–16 KiB)
- 25 basic injection/path/template/control-character strings

**Observed result:** every request returned **HTTP 400**. There were **0 HTTP 5xx responses** and **0 transport errors**. In this test set, the production endpoint failed closed at validation and did not expose a crash or obvious server-side failure.

This is a negative security result, not a vulnerability claim.

## Reproducible evidence

Successful GitHub Actions run:

- Workflow run: https://github.com/fsalmon1991/Python/actions/runs/35432974783
- Workflow source: https://github.com/fsalmon1991/Python/blob/main/.github/workflows/rustchain-attest-fuzz.yml
- Fixed workflow commit: `b53445a4e0b42454bde43dbd78f38cf72a3d30dd`

The first workflow attempt failed locally at Python parse time because one quoted injection string was malformed. No requests were sent by that failed attempt. I corrected the string and reran; run #2 completed successfully.

## Outcome counts

### Overall

| Result | Count |
|---|---:|
| HTTP 400 | 100 |
| HTTP 401 | 0 |
| HTTP 409 | 0 |
| HTTP 413 | 0 |
| HTTP 422 | 0 |
| HTTP 429 | 0 |
| HTTP 5xx | 0 |
| Transport errors | 0 |

### By category

| Category | Requests | 400 | 5xx | Transport error |
|---|---:|---:|---:|---:|
| Missing fields | 25 | 25 | 0 | 0 |
| Wrong types | 25 | 25 | 0 | 0 |
| Oversized inputs | 25 | 25 | 0 | 0 |
| Injection-style strings | 25 | 25 | 0 | 0 |

## Payload design

The harness used the following nominal field set and then mutated/removes individual fields:

```text
miner_id
nonce
timestamp
fingerprint
signature
```

Wrong-type values included `null`, booleans, integers, negative integers, floats, arrays, and objects.

Oversized values were bounded to 1,024 / 2,048 / 4,096 / 8,192 / 16,384 characters so the test remained intentionally non-destructive.

Injection-style values included simple SQL-looking strings, HTML/script-looking strings, template expressions, traversal strings, null/control representations, command-substitution-looking text, Unicode, and long numeric/alphanumeric strings. These were strings only; the harness did not attempt command execution or destructive SQL.

A 250 ms pause was used between requests. Each request had a 10-second timeout and a descriptive user agent: `fsalmon1991-authorized-bounty-fuzzer/1.0`.

## Representative responses

The first twenty requests all returned structured 400 JSON errors. Two recurring examples were:

```json
{"code":"INVALID_FINGERPRINT","error":"invalid_fingerprint","message":"Field 'fingerprint' must be a JSON object","ok":false}
```

and:

```json
{"code":"MISSING_MINER","error":"missing_miner","message":"Field 'miner' or 'miner_id' must be a non-empty identifier using only letters, numbers, '.', '_', ':' or '-'","ok":false}
```

This indicates early schema/shape validation is active on the live endpoint.

## Interpretation

### What passed

- All 100 malformed requests were rejected with a 4xx status.
- No case produced a 500-class response.
- No request caused a transport failure during the run.
- Responses were structured JSON rather than HTML tracebacks.
- Obvious string-based injection content was treated as invalid input rather than producing an observable server crash.

### Important limitation

This run intentionally used malformed payloads and therefore many cases stopped at the endpoint's earliest validation layer, especially fingerprint/miner shape checks. It **does not prove** deeper signature, replay, hardware-binding, challenge, or persistence paths are bug-free. It specifically verifies that these four classes of malformed requests did not bypass the early production validation path or crash the endpoint during this run.

## Overlap / prior-art check

Before interpreting the result, I checked the current RustChain repository and found that the project already contains local malformed-input regression coverage, including:

- `tests/test_attestation_fuzz.py`
- `tests/fuzz_attest_submit.py`
- `docs/attestation_fuzzing.md`
- prior fixes such as `docs/FIX_1147_ATTEST_SUBMIT_CRASH.md`

So I am **not** claiming the 400 behavior as a novel bug/fix. The value of this bounty run is live-production verification against the currently deployed endpoint, with a reproducible 100-request run and categorized response counts.

## Security finding status

- New exploitable vulnerability found: **No**
- 500-class bug found: **No**
- Private vulnerability report required: **No**
- Destructive testing performed: **No**

## Suggested follow-up

A future deeper pass could start from a schema-valid but unauthenticated attestation fixture and mutate nested `device`, `signals`, `report`, and `fingerprint.checks` members one at a time. That would map validation beyond the earliest shape gates while still avoiding any valid signature or unauthorized state-changing behavior.

## AI assistance disclosure

The fuzz harness and report were produced with AI assistance under the account owner's authorization. Results above are copied from the successful GitHub Actions execution, not estimated or fabricated.