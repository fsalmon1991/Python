# BoTTube JS SDK health contract mismatch

**Bounty:** Scottcjn/rustchain-bounties #1102  
**Target:** Scottcjn/bottube  
**Source reviewed:** `0b25f2bed262746a653c86ef2a1b8b0f5b2794a1`  
**Reporter:** `@fsalmon1991`  
**Payout wallet:** `RTC7f216de84caae4f0fb1bddf3f22e08f76e06bd63`

## Summary

The current JavaScript SDK models `GET /health` as returning `{ status, timestamp }`, while the current BoTTube server regression test and API documentation define the response with `ok`, `service`, `version`, `uptime_s`, and counters. `bottube-dashboard` then treats `result.status === 'healthy'` as its health decision.

A valid healthy server response therefore leaves `result.status` undefined and makes the dashboard report the API as unhealthy even though the HTTP request succeeded.

## Current SDK contract

`js-sdk/src/client.ts`:

```ts
async health(): Promise<{ status: string; timestamp: number }> {
  return this.request<{ status: string; timestamp: number }>('GET', '/health');
}
```

The JS SDK test reinforces the wrong shape by mocking:

```ts
{ status: 'healthy', timestamp: 123 }
```

## Dashboard behavior

`bottube-dashboard/src/index.ts`:

```ts
const result = await this.client.health();
spinner.succeed(kleur.green(`API Status: ${result.status}`));
return result.status === 'healthy';
```

## Server contract

The current server regression test calls `/health` and asserts:

```py
resp = client.get('/health')
assert resp.status_code == 200
data = resp.get_json()
assert data['ok'] is True
assert data['service'] == 'bottube'
```

`docs/API.md` documents a response shaped like:

```json
{
  "ok": true,
  "service": "bottube",
  "version": "1.2.0",
  "uptime_s": 86400
}
```

with additional counters.

## Deterministic reproduction

No production mutation is required. Apply the documented/server-tested response shape to the dashboard's decision logic:

```js
const result = {
  ok: true,
  service: 'bottube',
  version: '1.2.0',
  uptime_s: 86400,
};

console.log(result.status);               // undefined
console.log(result.status === 'healthy'); // false
```

## Expected

The SDK should model the actual server health response, and callers should use the canonical health signal (`ok`) rather than a nonexistent `status` field.

## Actual

The request can succeed with a healthy response, but the dashboard prints an undefined status and returns `false`.

## Suggested fix

1. Add a `HealthResponse` type matching the real `/health` contract.
2. Return `HealthResponse` from `BoTTubeClient.health()`.
3. Update the JS SDK health unit test to mock the real server response.
4. Update `bottube-dashboard` to use `result.ok === true` for the health decision and render meaningful fields from the real response.

## Duplicate check

Searched current BoTTube issues for combinations of `js-sdk`, `health`, `API Status`, `result.status`, `health response`, and `dashboard health`; no matching report was found before submission.

## Submission note

Direct issue creation and bounty commenting through the connected GitHub integration returned `403 Resource not accessible by integration`. The complete claim was therefore submitted through the bounty's allowed email fallback for maintainer filing.

AI assistance was used for source review and report preparation.
