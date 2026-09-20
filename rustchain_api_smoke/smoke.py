#!/usr/bin/env python3
"""Read-only RustChain public API contract smoke checker.

Checks a small set of public GET endpoints for reachability and response shape.
It never submits attestations, transfers tokens, or mutates node state.
"""
from __future__ import annotations

import argparse
import json
import ssl
import time
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple


@dataclass(frozen=True)
class EndpointSpec:
    path: str
    required_keys: Tuple[str, ...]
    nested_list: Optional[str] = None
    nested_required_keys: Tuple[str, ...] = ()


SPECS: Tuple[EndpointSpec, ...] = (
    EndpointSpec("/health", ("ok", "version")),
    EndpointSpec("/epoch", ("epoch", "slot", "blocks_per_epoch", "enrolled_miners")),
    EndpointSpec(
        "/api/miners",
        ("miners", "pagination"),
        nested_list="miners",
        nested_required_keys=("miner", "device_arch", "last_attest"),
    ),
)


@dataclass
class CheckResult:
    path: str
    url: str
    ok: bool
    http_status: Optional[int]
    latency_ms: Optional[float]
    errors: List[str]
    summary: Dict[str, Any]


Fetcher = Callable[[str, float, bool], Tuple[int, Mapping[str, Any], float]]


def _default_fetch_json(url: str, timeout: float, insecure: bool) -> Tuple[int, Mapping[str, Any], float]:
    context = ssl._create_unverified_context() if insecure else ssl.create_default_context()
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "rustchain-api-smoke/1.0",
        },
        method="GET",
    )
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=timeout, context=context) as response:
            status = int(getattr(response, "status", response.getcode()))
            raw = response.read()
    except urllib.error.HTTPError as exc:
        latency = (time.perf_counter() - started) * 1000.0
        raw = exc.read()
        try:
            payload = json.loads(raw.decode("utf-8", errors="replace"))
        except Exception:
            payload = {"_raw": raw.decode("utf-8", errors="replace")[:500]}
        return int(exc.code), payload, latency

    latency = (time.perf_counter() - started) * 1000.0
    payload = json.loads(raw.decode("utf-8"))
    if not isinstance(payload, Mapping):
        raise ValueError(f"expected JSON object, got {type(payload).__name__}")
    return status, payload, latency


def _missing_keys(payload: Mapping[str, Any], keys: Iterable[str]) -> List[str]:
    return [key for key in keys if key not in payload]


def _summarize(spec: EndpointSpec, payload: Mapping[str, Any]) -> Dict[str, Any]:
    if spec.path == "/health":
        return {"node_ok": payload.get("ok"), "version": payload.get("version")}
    if spec.path == "/epoch":
        return {
            "epoch": payload.get("epoch"),
            "slot": payload.get("slot"),
            "enrolled_miners": payload.get("enrolled_miners"),
        }
    if spec.path == "/api/miners":
        miners = payload.get("miners")
        pagination = payload.get("pagination")
        return {
            "returned_miners": len(miners) if isinstance(miners, list) else None,
            "reported_total": pagination.get("total") if isinstance(pagination, Mapping) else None,
            "total_enrolled": pagination.get("total_enrolled") if isinstance(pagination, Mapping) else None,
        }
    return {}


def check_endpoint(
    base_url: str,
    spec: EndpointSpec,
    timeout: float,
    insecure: bool,
    fetcher: Fetcher = _default_fetch_json,
) -> CheckResult:
    url = base_url.rstrip("/") + spec.path
    errors: List[str] = []
    status: Optional[int] = None
    latency: Optional[float] = None
    payload: Mapping[str, Any] = {}

    try:
        status, payload, latency = fetcher(url, timeout, insecure)
    except Exception as exc:
        errors.append(f"request failed: {type(exc).__name__}: {exc}")
        return CheckResult(spec.path, url, False, status, latency, errors, {})

    if status < 200 or status >= 300:
        errors.append(f"HTTP {status}")

    missing = _missing_keys(payload, spec.required_keys)
    if missing:
        errors.append("missing top-level keys: " + ", ".join(missing))

    if spec.nested_list and spec.nested_list in payload:
        items = payload.get(spec.nested_list)
        if not isinstance(items, list):
            errors.append(f"{spec.nested_list} must be a list")
        else:
            for idx, item in enumerate(items[:25]):
                if not isinstance(item, Mapping):
                    errors.append(f"{spec.nested_list}[{idx}] must be an object")
                    continue
                nested_missing = _missing_keys(item, spec.nested_required_keys)
                if nested_missing:
                    errors.append(
                        f"{spec.nested_list}[{idx}] missing keys: " + ", ".join(nested_missing)
                    )
                    break

    return CheckResult(
        path=spec.path,
        url=url,
        ok=not errors,
        http_status=status,
        latency_ms=round(latency, 2) if latency is not None else None,
        errors=errors,
        summary=_summarize(spec, payload),
    )


def run_checks(
    base_url: str,
    timeout: float = 8.0,
    insecure: bool = False,
    specs: Sequence[EndpointSpec] = SPECS,
    fetcher: Fetcher = _default_fetch_json,
) -> List[CheckResult]:
    return [check_endpoint(base_url, spec, timeout, insecure, fetcher) for spec in specs]


def _human_output(results: Sequence[CheckResult]) -> str:
    lines: List[str] = []
    for result in results:
        marker = "PASS" if result.ok else "FAIL"
        latency = f"{result.latency_ms:.2f} ms" if result.latency_ms is not None else "n/a"
        lines.append(f"[{marker}] {result.path} HTTP={result.http_status} latency={latency}")
        if result.summary:
            lines.append("       " + json.dumps(result.summary, sort_keys=True))
        for err in result.errors:
            lines.append(f"       error: {err}")
    lines.append(f"summary: {sum(r.ok for r in results)}/{len(results)} endpoint contracts passed")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Read-only RustChain public API smoke checker")
    parser.add_argument("--node", default="https://rustchain.org", help="RustChain node base URL")
    parser.add_argument("--timeout", type=float, default=8.0, help="per-request timeout in seconds")
    parser.add_argument("--insecure", action="store_true", help="disable TLS verification for self-signed nodes")
    parser.add_argument("--json", action="store_true", dest="json_output", help="emit machine-readable JSON")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    results = run_checks(args.node, args.timeout, args.insecure)
    if args.json_output:
        print(json.dumps([asdict(result) for result in results], indent=2, sort_keys=True))
    else:
        print(_human_output(results))
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
