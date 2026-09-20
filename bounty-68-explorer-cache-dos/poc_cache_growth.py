#!/usr/bin/env python3
"""Safe local PoC for RustChain explorer_server.py cache lifecycle.

This script makes no network requests and intentionally uses only a small number
of entries. It mirrors the current cache-key and TTL logic closely enough to
show the defect: TTL expiry stops a cache hit but does not evict the entry.
"""

from dataclasses import dataclass


@dataclass
class Clock:
    now: float = 0.0

    def time(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


CACHE_TTL = 10
cache: dict[str, dict] = {}
clock = Clock()


def current_explorer_cache_behavior(endpoint: str, raw_query: str) -> None:
    """Mirror the cache-key + stale-check + successful-insert logic."""
    cache_key = f"{endpoint}:{raw_query}"
    cached = cache.get(cache_key)
    if cached and (clock.time() - cached["time"]) < CACHE_TTL:
        return

    # Model a successful JSON response from an allow-listed upstream endpoint.
    # The real handler performs requests.get(...), response.json(), then stores
    # exactly this cache-key shape without any size bound or expiry sweep.
    data = {"status": "ok"}
    cache[cache_key] = {"data": data, "time": clock.time()}


def main() -> None:
    count = 32  # deliberately tiny/safe; enough to prove lifecycle behavior

    for i in range(count):
        current_explorer_cache_behavior("health", f"nonce={i}")

    assert len(cache) == count
    print(f"resident entries after {count} unique queries: {len(cache)}")

    clock.advance(CACHE_TTL + 1)

    # Touch a new unique key after every old entry is stale. The current design
    # does not sweep the 32 expired entries before inserting this one.
    current_explorer_cache_behavior("health", "nonce=after-expiry")

    print(f"resident entries after TTL expiry + one insert: {len(cache)}")
    assert len(cache) == count + 1

    expired = sum(
        1 for row in cache.values()
        if (clock.time() - row["time"]) >= CACHE_TTL
    )
    print(f"expired entries still resident: {expired}")
    assert expired == count

    print("PASS: TTL expiry does not bound or evict resident cache entries.")


if __name__ == "__main__":
    main()
