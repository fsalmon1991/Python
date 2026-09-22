# RustChain #16471 — pending payout is marked confirmed and claim is closed before settlement

**Bounty:** `Scottcjn/rustchain-bounties#16471` — Audit the payout pipeline for silent-success failures  
**Reporter:** `@fsalmon1991`  
**Canonical RTC payout wallet:** `RTC7f216de84caae4f0fb1bddf3f22e08f76e06bd63`  
**Requested assessment:** 35 RTC base audit if this is the first valid non-duplicate finding from this claimant; otherwise apply the bounty's applicable increment.  
**Testing:** source/state-machine analysis only. No production transfer was attempted.

## Summary

Current `scripts/bounty_payout.py` correctly distinguishes a two-phase transfer response with `phase == "pending"` from an already-settled transfer in its human-readable text, but it still writes the terminal idempotency marker `RTC-AutoPay-Confirmed` and immediately closes the claim **before the pending transfer has settled**.

On the next payout run, the script skips any claim containing `RTC-AutoPay-Confirmed`. Therefore, if the 24-hour confirmer later fails, stalls, rejects, or never settles the pending transfer, the bounty issue is already closed and the payout runner will never retry or reconcile it. The workflow can appear complete while the recipient balance never moves.

That is the exact silent-success shape #16471 asks for: code completes successfully and records a terminal success state while the intended money movement has not happened.

## Current control flow

In current `scripts/bounty_payout.py`:

1. A claim is skipped if **any** comment contains `RTC-AutoPay-Confirmed`.
2. `transfer(...)` treats an HTTP/application response with `ok: true` as success and returns the response to the caller.
3. The caller recognizes `phase == "pending"` and correctly constructs text saying the payment is only **queued** and that the balance moves later.
4. Despite that non-terminal phase, the script posts a comment beginning with:

   ```text
   💸 **RTC-AutoPay-Confirmed** — payout **queued** ...
   ```

5. It then immediately closes the claim issue as completed.
6. On a future run, the marker check short-circuits the claim before any settlement/balance verification.

The relevant current source is:

- `scripts/bounty_payout.py` in `Scottcjn/rustchain-bounties`
- candidate skip: `if any("RTC-AutoPay-Confirmed" in ...): continue`
- pending branch: `if phase == "pending": state = "**queued** ... Pending ... balance moves when it clears."`
- terminal marker and close happen immediately after that branch.

## Deterministic state-machine reproduction

No live funds are necessary to reproduce the logic:

```text
Initial claim:
  eligible = true
  terminal_marker = false
  issue = open

Transfer response:
  {"ok": true, "phase": "pending", "confirms_in_hours": 24}

Current payout runner then does:
  post "RTC-AutoPay-Confirmed — payout queued ..."
  close issue

Suppose settlement later does not complete:
  balance moved = false
  pending transfer = expired/rejected/stuck

Next payout run:
  sees RTC-AutoPay-Confirmed
  => continue
  => no retry
  => no reconciliation
  => claim remains closed
```

The failure does not require a speculative transport error. #16471 itself documents that the pending confirmer previously failed to run for an extended period; this payout-side state machine has no settlement check before recording the terminal marker and closing the claim.

## Impact

- A contributor can receive a public terminal-looking confirmation and a closed claim while their wallet was never credited.
- The payout runner's own idempotency guard prevents later retry because it trusts the premature terminal marker.
- Maintainers may read a closed issue / `RTC-AutoPay-Confirmed` marker as proof of settlement even though the source explicitly says `phase="pending"` means the balance has not moved yet.
- Recovery becomes manual because the normal runner has removed the claim from its own retry path.

This is not a fund-theft claim and does not require exploiting production. It is a payout-liveness/accounting defect.

## Why this is distinct from already-reported findings

I duplicate-checked the public tracker before submitting.

- **#16390 / the original #16471 example:** `transfer()` treated HTTP 200 with `{"ok": false}` as success. That defect was fixed by checking `resp.get("ok")`. This report starts **after a legitimate `ok: true, phase: pending` response** and concerns premature terminalization before settlement.
- **#10590:** concerns spoofable idempotency comments / duplicate-transfer ordering in a different auto-pay path. This report is about the current `bounty_payout.py` state transition from `pending` to a terminal marker/closed issue without confirmation.
- **#16660:** malformed `gh` JSON becomes an empty payout set. Different failure path.
- **#16662:** docstring gate can ignore failed label writes. Different failure path.
- Searches for `pending + RTC-AutoPay-Confirmed + close/settlement` did not return an exact prior report.

## Suggested fix

Use separate states and only close on settlement:

1. When `phase == "pending"`, post a non-terminal marker such as `RTC-AutoPay-Queued` containing the pending/transaction identifier.
2. Keep the issue open, or use an explicit `payout-pending` label.
3. Have the confirmation/reconciliation path verify the pending transfer reached a settled ledger state.
4. Only then post `RTC-AutoPay-Confirmed` and close the issue.
5. If the pending transfer expires/rejects, remove/transition the pending marker and return the claim to a retry or human-review state. Reuse the same idempotency key so retry cannot double-debit an already-accepted transfer.

A regression test should assert that an `ok: true, phase: pending` response **does not** create the terminal confirmed marker and **does not** close the issue, while a truly settled response does both.

## Scope and disclosure

This report is based on public source and a deterministic control-flow analysis. I did not call production payout endpoints, use admin credentials, move funds, or fabricate settlement evidence. AI assistance was used to inspect the public code and prepare the report.