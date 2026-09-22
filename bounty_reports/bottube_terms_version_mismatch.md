# BoTTube agent onboarding: documented TOS version 1.0 rejected by production 1.1

## Summary

A new BoTTube agent following the published agent quick-start examples was instructed to send `{"version":"1.0"}` to `POST /api/agents/me/accept-terms`. Production had already moved to TOS version 1.1, so the documented request returned HTTP 400 `version_mismatch` and blocked the first upload.

This was encountered while completing the open Agent Resume Reel bounty with the single agent `fsalmon-paidtaskworker`. No alternate account was created after the failure.

## Reproduction

1. Register one agent through the documented BoTTube agent flow.
2. Use the API key returned for that same agent.
3. Follow the documented terms-acceptance example that posts `{"version":"1.0"}` to `/api/agents/me/accept-terms`.
4. Observe HTTP 400 `version_mismatch` while production reports current TOS version 1.1.
5. The failed terms acknowledgement blocks the authenticated upload path.

## Expected

The public quick-start should either:

- submit the live current TOS version, or
- omit the explicit version and let the server record the current version when that behavior is supported.

Documentation and the server-side version constant should match production.

## Actual

The published example pinned version 1.0 while production required 1.1.

## Impact

Low-severity functional/documentation bug with a real onboarding failure: a correctly implemented autonomous client can follow the official instructions exactly and still be unable to finish account onboarding or upload its first video.

## Maintainer confirmation

Maintainer PR `Scottcjn/bottube#2296`, created after this report, states that `@fsalmon1991` followed `AGENT_QUICKSTART.md` exactly, received HTTP 400 `version_mismatch`, and that production had served TOS 1.1 since 2026-07-09 while the repo constant and examples still said 1.0.

PR: https://github.com/Scottcjn/bottube/pull/2296

The proposed fix changes the examples to submit `{}` so they cannot drift, documents how to query the live version, and synchronizes the server constant to 1.1 / 2026-07-09.

## Suggested fix

The maintainer's PR implements the right durable approach:

- avoid pinning a stale version in quick-start snippets when the endpoint can accept the current version implicitly;
- document `GET /api/tos` and the registration response `terms` block for clients that want explicit versioning;
- keep the repository's `TOS_VERSION` and effective date synchronized with production;
- retain regression coverage for invalid explicit versions.

## Duplicate check

Before filing the bounty claim, searches of current BoTTube issues for `version_mismatch`, `accept-terms`, and the 1.0/1.1 mismatch found no earlier report of this exact stale-version failure. Issue #1299 concerns a different bug: the quick-start omitted the terms-acceptance step entirely.

## Bounty claim

- Program: `Scottcjn/rustchain-bounties#71` ongoing bug bounty.
- Severity requested: Low.
- Requested payout: **5 RTC**, the minimum advertised Low-tier amount.
- Claimant: `@fsalmon1991`.
- RTC wallet: `RTC7f216de84caae4f0fb1bddf3f22e08f76e06bd63`.
- AI disclosure: the report and validation were prepared with AI assistance under the account owner's authorization; all evidence above is tied to the actual observed failure and maintainer-confirmed fix.
