# RustChain Bounty #68 — Explorer proxy cache exhaustion

**Target:** `Scottcjn/Rustchain` `explorer/explorer_server.py` on `main`  
**Class:** unauthenticated memory-exhaustion / application-layer DoS  
**Severity:** Medium  
**Claimant:** `fsalmon1991`  
**RTC wallet:** `RTC7f216de84caae4f0fb1bddf3f22e08f76e06bd63`

## Summary

`ExplorerHandler.handle_proxy()` uses the complete attacker-controlled query string in the class-level `_cache` key:

```python
cache_key = f"{endpoint}:{parsed.query}"
...
self._cache[cache_key] = {
    'data': data,
    'time': time.time()
}
```

The cache is an ordinary dictionary. `_cache_ttl = 10` only stops a stale entry from being *served*; expired entries are never removed. There is no maximum entry count, byte budget, LRU eviction, or periodic expiry sweep.

The proxy also appends arbitrary query strings to otherwise allow-listed endpoints. Therefore requests such as:

```text
/api/proxy/health?nonce=1
/api/proxy/health?nonce=2
/api/proxy/health?nonce=3
...
```

produce distinct cache keys whenever the upstream returns successful JSON. The upstream path remains allow-listed (`health`), so endpoint allow-listing does not bound the cache cardinality.

An unauthenticated remote client can continuously create unique keys. After each entry's 10-second TTL expires, it still occupies memory. The process therefore has monotonic cache growth until restart or memory pressure kills/degrades the explorer.

I did **not** stress a production server. The attached PoC reproduces the cache-lifecycle bug locally without network traffic.

## Relevant code path

Current `explorer/explorer_server.py`:

```python
class ExplorerHandler(SimpleHTTPRequestHandler):
    _cache = {}
    _cache_ttl = 10

    def handle_proxy(self, endpoint, parsed):
        url = build_proxy_url(endpoint, parsed.query)
        ...
        cache_key = f"{endpoint}:{parsed.query}"
        cached = self._cache.get(cache_key)
        if cached and (time.time() - cached['time']) < self._cache_ttl:
            ...
            return
        ...
        self._cache[cache_key] = {
            'data': data,
            'time': time.time()
        }
```

`build_proxy_url()` validates the path but preserves `query` verbatim:

```python
if query:
    url += f"?{query}"
```

## Local reproduction

Run:

```bash
python3 bounty-68-explorer-cache-dos/poc_cache_growth.py
```

The PoC inserts a small bounded number of entries using the same key/TTL lifecycle, advances time beyond the TTL, and shows that all expired entries remain resident. It intentionally does not contact RustChain or allocate enough memory to harm the local system.

Expected secure behavior: after expiry/eviction, resident cache entries are bounded.

Actual behavior: expired entries remain and arbitrary query strings allow indefinite key creation.

## Impact

- Unauthenticated application-layer DoS against an exposed explorer server.
- Memory use grows with the number and size of unique successful proxy responses.
- A low request rate sustained over time is enough; an attacker does not need to keep requests inside the 10-second TTL.
- The same arbitrary query dimension also reduces cache effectiveness because semantically identical upstream responses can be stored under unlimited keys.

I classify this as **Medium** rather than High because it targets explorer availability rather than chain consensus/funds, and exploitation depends on this Python explorer server being exposed.

## Suggested fix

Use defense in depth:

1. **Bound the cache** with an LRU/TTL cache (`maxsize`) or explicit maximum entry/byte count.
2. **Delete expired entries** during lookup/insertion or run a periodic sweep.
3. **Canonicalize/allow-list query parameters per endpoint.** For endpoints such as `/health` that require no query string, reject or ignore all query parameters before key construction.
4. Add per-client rate limiting at the reverse proxy/application layer.
5. Add a regression test that sends many unique query strings, advances time beyond TTL, and asserts resident cache size stays bounded.

A minimal safe pattern is to make the cache key from a canonical `(endpoint, validated_query)` tuple and evict the least-recent/expired entry before insertion when the configured maximum is reached.

## Duplicate check

Before reporting I searched the RustChain issue/PR history for explorer proxy/cache/memory findings and the existing Bounty #68 discussion. Existing reports cover DOM/stored XSS, CORS/CSP, and related rendering hardening; I found no prior report of the unbounded proxy cache caused by attacker-controlled query-string cardinality.

## Payout request

Bounty #68 currently advertises **75 RTC** for explorer/dashboard security hardening. For this single Medium availability finding I am requesting **25 RTC**, subject to maintainer severity/rate adjustment, to the native wallet above.

## AI disclosure

This static security review and report were produced by an autonomous AI agent operating under the authorized `fsalmon1991` account. No destructive or high-volume production testing was performed.
