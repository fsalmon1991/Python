# RustChain #16471 audit finding: docstring weekly cap is keyed to issue creation time, not earnings time

**Bounty:** Scottcjn/rustchain-bounties#16471  
**Claimant:** @fsalmon1991  
**Requested assessment:** 35 RTC audit base for one concrete silent-success defect, subject to maintainer confirmation  
**Payout wallet:** `RTC7f216de84caae4f0fb1bddf3f22e08f76e06bd63`  
**AI disclosure:** This audit was performed with AI assistance and manually constrained to current public source and duplicate checks.

## Finding

`scripts/docstring_gate.py::docstring_rtc_this_week()` says it computes how much RTC an author has **already been granted for docstrings in 7 days**, but the search selects claims by the **claim issue's creation date**:

```python
since = (datetime.datetime.now(datetime.timezone.utc)
         - datetime.timedelta(days=7)).strftime("%Y-%m-%d")
q = (f"repo:{REPO} is:issue author:{author} label:docstring-verified "
     f"created:>{since}")
```

After that, the function fetches comments from the selected issues and sums each gate-generated `<!-- rtc-payout-amount: ... -->` marker. The marker is written when the gate verifies the claim and queues it for payout.

Those two clocks are not equivalent. A claim can be created, wait for its PR to merge or for the gate to retry, and then be verified more than seven days later. Once verified, its RTC is current weekly earnings, but `created:>{since}` excludes it solely because the issue itself is old.

## Concrete silent-success path

Assume the rolling cap is the current 40 RTC/week:

1. Contributor opens docstring claim A on day 0.
2. Claim A remains pending for more than seven days (for example, its PR is not yet merged).
3. On day 10, the PR merges. The gate verifies A, writes `<!-- rtc-payout-amount: 38 -->`, labels it `docstring-verified`, and queues 38 RTC.
4. On day 11, a new claim B is adjudicated for 5 RTC.
5. `docstring_rtc_this_week()` searches only issues with `created:>` day 4. Claim A was created on day 0, so it is absent from the search even though its 38 RTC marker was written only one day ago.
6. The function reports 0 RTC (or otherwise understates the true rolling-week total), so `already + amount > MAX_RTC_PER_WEEK` evaluates as `0 + 5 > 40 == False`.
7. Claim B is approved and queued. The contributor has now been granted 43 RTC inside the intended seven-day window, while the gate exits successfully and reports no error.

This is the #16471 failure class: the workflow is green, but the monetary policy effect is wrong without surfacing an error.

## Why this is distinct from existing #16471 reports

I duplicate-checked the public tracker before submitting. In particular:

- #16711 reports repeated weekly-cap comments because `weekly-cap-reached` is missing from the idempotency skip set. That is a retry/comment-spam defect, not time-window accounting.
- #16662 reports ignored label-write failures in the docstring gate.
- #16660 reports malformed GitHub JSON being converted into an empty payout candidate set.
- #16710 reports premature `gate-processed` persistence in the PR-review gate.

I found no existing report centered on the weekly earnings query using **issue creation time instead of the time the RTC grant marker was created / the claim was verified**.

## Expected behavior

The rolling seven-day cap should count RTC grants whose **verification/grant event** occurred in the last seven days, regardless of when the claim issue was originally opened.

## Suggested fix

Do not pre-filter docstring earnings by issue `created_at`. Instead, enumerate the contributor's relevant `docstring-verified` claims and sum only trusted gate markers whose **comment `created_at`** is within the exact seven-day cutoff. The marker comment timestamp is aligned with the event the function claims to measure: when RTC was granted/queued.

If querying all historical claims is too expensive, persist a trusted grant timestamp/amount in a dedicated ledger or label-backed record and query that source by grant time. The comparison should use an exact UTC timestamp rather than a date-only boundary.

## Regression test

Create an issue fixture whose `created_at` is older than seven days but whose trusted gate comment containing `<!-- rtc-payout-amount: 38 -->` is one day old. With a new 5 RTC claim, the gate must calculate `already == 38` and hold the new claim because 43 RTC exceeds the 40 RTC rolling cap.

A complementary fixture with both the issue and grant marker older than seven days should not contribute to the total.
