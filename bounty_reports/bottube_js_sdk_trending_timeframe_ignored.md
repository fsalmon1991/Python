# BoTTube JS SDK `getTrending({ timeframe })` silently ignores the requested window

**Bounty:** Scottcjn/rustchain-bounties#1102  
**Classification:** Functional bug  
**Requested payout:** 5 RTC  
**Reporter:** @fsalmon1991  
**RTC wallet:** `RTC7f216de84caae4f0fb1bddf3f22e08f76e06bd63`

## Summary

The current JavaScript/TypeScript SDK exposes `getTrending({ timeframe })` and documents `timeframe` values such as `day`, `week`, and `month`, but it sends that value to the server as a `timeframe=` query parameter. The current `/api/trending` contract uses `days=` (or `since=`) to control the result window. As a result, JS SDK callers can request a different timeframe and receive a successful response without the requested window actually being applied.

This is especially easy to miss because no error is raised: `getTrending({ timeframe: 'week' })` sends a syntactically valid request, but the server-side trending parameter parser does not consume `timeframe`.

## Evidence in current source

Current JS SDK implementation (`js-sdk/src/client.ts`):

```ts
async getTrending(options: TrendingOptions = {}): Promise<VideoListResponse> {
  const params = new URLSearchParams();
  if (options.limit) params.append('limit', String(options.limit));
  if (options.timeframe) params.append('timeframe', options.timeframe);
  const qs = params.toString();
  return this.request<VideoListResponse>('GET', `/api/trending${qs ? '?' + qs : ''}`);
}
```

Current SDK type (`js-sdk/src/types.ts`) advertises:

```ts
export interface TrendingOptions {
  limit?: number;
  timeframe?: 'hour' | 'day' | 'week' | 'month';
}
```

By contrast, the repository's current `/api/trending` regression tests reproduce the server handler's parameter parsing around `days` and `since`, and verify that `days=1`, `days=7`, etc. actually filter results. There is no corresponding `timeframe` server parameter in that contract.

The Python SDK already translates the friendly timeframe into the server contract before making the request:

```py
windows = {"day": 1, "week": 7, "month": 30}
if timeframe not in windows:
    raise ValueError("timeframe must be day, week, or month")
days = windows[timeframe]
return self._request("GET", "/api/trending", params={
    "limit": limit, "days": days, "since": since, "category": category,
})
```

That makes the JS SDK behavior inconsistent with both the backend contract and the Python SDK.

## Steps to reproduce

Environment: Node.js 18+ semantics / current `@bottube/sdk` source on the default branch.

1. Call `client.getTrending({ limit: 5, timeframe: 'day' })`.
2. Observe the SDK-generated URL: `/api/trending?limit=5&timeframe=day`.
3. Repeat with `timeframe: 'week'` and `timeframe: 'month'`.
4. Observe that the only window parameter changes are `timeframe=week` and `timeframe=month`.
5. Compare with the server contract/tests, which read `days` / `since` and use `days` to filter the result set.

A minimal reproduction of the parameter mismatch yields:

```text
day   /api/trending?limit=5&timeframe=day   -> server days=null, since=null
week  /api/trending?limit=5&timeframe=week  -> server days=null, since=null
month /api/trending?limit=5&timeframe=month -> server days=null, since=null
```

## Expected

The SDK's public timeframe option should control the backend trending window. For example:

- `day` -> `days=1`
- `week` -> `days=7`
- `month` -> `days=30`

If `hour` is meant to remain supported, the server needs a compatible representation (for example `since=<unix timestamp>`), or the JS SDK type should stop advertising it.

## Actual

The JS SDK sends `timeframe=<value>`. The current backend trending contract reads `days`/`since`, so callers receive a successful response without the requested timeframe being applied.

## Impact

This is a functional correctness bug rather than a cosmetic mismatch. Several repository examples depend on `getTrending({ timeframe })` (including digest/dashboard/export examples), so applications can label output as daily/weekly/monthly while actually querying the backend without that requested window.

## Suggested fix

Mirror the Python SDK's translation in the JS client, e.g. map `day/week/month` to `days=1/7/30`, and decide whether `hour` should map to a `since` timestamp or be removed from the public type. Add a JS SDK regression test that asserts the generated query uses the backend-supported parameter and that distinct timeframe values produce distinct backend windows.

## Duplicate check

Before submission I searched current BoTTube issues and pull requests for combinations of `getTrending`, `timeframe`, `days`, JS SDK, and trending. I found example PRs that *use* `getTrending({ timeframe })`, but no issue/PR reporting or fixing this parameter-contract mismatch. This report is distinct from the previously submitted JS SDK `/health` response-shape mismatch.

## AI assistance disclosure

This report was prepared with AI-assisted source review and local deterministic reproduction. No production mutation, payment, account farming, or fabricated evidence was used.
