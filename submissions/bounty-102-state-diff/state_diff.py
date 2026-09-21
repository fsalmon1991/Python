#!/usr/bin/env python3
"""Capture canonical JSON endpoint snapshots and diff them offline.

Read-only by design: only HTTP GET requests are issued.
Standard-library only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, Iterable, List

Json = Any


@dataclass
class EndpointSnapshot:
    path: str
    url: str
    status: int
    elapsed_ms: int
    sha256: str
    data: Json


def canonical_json(value: Json) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_json(value: Json) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def normalize_path(path: str) -> str:
    path = path.strip()
    if not path:
        raise ValueError("endpoint path cannot be empty")
    return path if path.startswith("/") else "/" + path


def endpoint_url(base_url: str, path: str) -> str:
    return base_url.rstrip("/") + normalize_path(path)


def capture_endpoint(base_url: str, path: str, timeout: float = 10.0) -> EndpointSnapshot:
    """GET one JSON endpoint and return a canonical snapshot."""
    url = endpoint_url(base_url, path)
    request = urllib.request.Request(
        url,
        method="GET",
        headers={
            "Accept": "application/json",
            "User-Agent": "rustchain-state-diff/1.0",
        },
    )
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read()
            status = int(getattr(response, "status", response.getcode()))
    except urllib.error.HTTPError as exc:
        raw = exc.read()
        status = int(exc.code)
        elapsed_ms = int((time.perf_counter() - started) * 1000)
        raise RuntimeError(f"GET {url} returned HTTP {status} after {elapsed_ms} ms") from exc
    except urllib.error.URLError as exc:
        elapsed_ms = int((time.perf_counter() - started) * 1000)
        raise RuntimeError(f"GET {url} failed after {elapsed_ms} ms: {exc.reason}") from exc

    elapsed_ms = int((time.perf_counter() - started) * 1000)
    if status < 200 or status >= 300:
        raise RuntimeError(f"GET {url} returned HTTP {status} after {elapsed_ms} ms")
    try:
        data = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"GET {url} did not return valid UTF-8 JSON") from exc
    return EndpointSnapshot(
        path=normalize_path(path),
        url=url,
        status=status,
        elapsed_ms=elapsed_ms,
        sha256=sha256_json(data),
        data=data,
    )


def capture(base_url: str, paths: Iterable[str], timeout: float = 10.0) -> Dict[str, Any]:
    endpoints = [asdict(capture_endpoint(base_url, path, timeout)) for path in paths]
    return {
        "format": "rustchain-state-diff/v1",
        "base_url": base_url.rstrip("/"),
        "endpoints": endpoints,
    }


def json_type(value: Json) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, dict):
        return "object"
    if isinstance(value, list):
        return "array"
    if isinstance(value, str):
        return "string"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    return type(value).__name__


def _join(path: str, part: str) -> str:
    if not path:
        return part
    if part.startswith("["):
        return path + part
    return path + "." + part


def diff_json(before: Json, after: Json, path: str = "") -> List[Dict[str, Any]]:
    """Return deterministic structural/value differences between JSON values."""
    changes: List[Dict[str, Any]] = []
    before_type, after_type = json_type(before), json_type(after)
    if before_type != after_type:
        return [{
            "path": path or "$",
            "change": "type_changed",
            "before_type": before_type,
            "after_type": after_type,
        }]

    if isinstance(before, dict):
        b_keys, a_keys = set(before), set(after)
        for key in sorted(b_keys - a_keys):
            changes.append({"path": _join(path, key), "change": "removed"})
        for key in sorted(a_keys - b_keys):
            changes.append({"path": _join(path, key), "change": "added"})
        for key in sorted(b_keys & a_keys):
            changes.extend(diff_json(before[key], after[key], _join(path, key)))
        return changes

    if isinstance(before, list):
        if len(before) != len(after):
            changes.append({
                "path": path or "$",
                "change": "length_changed",
                "before": len(before),
                "after": len(after),
            })
        for index, (b_item, a_item) in enumerate(zip(before, after)):
            changes.extend(diff_json(b_item, a_item, _join(path, f"[{index}]")))
        return changes

    if before != after:
        changes.append({
            "path": path or "$",
            "change": "value_changed",
            "before": before,
            "after": after,
        })
    return changes


def endpoint_map(snapshot: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {item["path"]: item for item in snapshot.get("endpoints", [])}


def diff_snapshots(before: Dict[str, Any], after: Dict[str, Any]) -> Dict[str, Any]:
    old, new = endpoint_map(before), endpoint_map(after)
    result: Dict[str, Any] = {
        "format": "rustchain-state-diff-report/v1",
        "endpoints_added": sorted(set(new) - set(old)),
        "endpoints_removed": sorted(set(old) - set(new)),
        "endpoint_diffs": [],
    }
    for path in sorted(set(old) & set(new)):
        changes = diff_json(old[path].get("data"), new[path].get("data"))
        if old[path].get("status") != new[path].get("status"):
            changes.insert(0, {
                "path": "$status",
                "change": "value_changed",
                "before": old[path].get("status"),
                "after": new[path].get("status"),
            })
        if changes:
            result["endpoint_diffs"].append({"path": path, "changes": changes})
    result["changed"] = bool(
        result["endpoints_added"] or result["endpoints_removed"] or result["endpoint_diffs"]
    )
    return result


def read_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: str, value: Dict[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Read-only JSON endpoint snapshot + offline state/schema diff tool."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    snap = sub.add_parser("snapshot", help="Capture JSON endpoints with HTTP GET.")
    snap.add_argument("--base-url", required=True)
    snap.add_argument(
        "--endpoint",
        action="append",
        dest="endpoints",
        required=True,
        help="Endpoint path; repeat for multiple endpoints.",
    )
    snap.add_argument("--out", required=True)
    snap.add_argument("--timeout", type=float, default=10.0)

    diff = sub.add_parser("diff", help="Compare two previously captured snapshots offline.")
    diff.add_argument("before")
    diff.add_argument("after")
    diff.add_argument("--out", help="Optional JSON report path.")
    diff.add_argument(
        "--fail-on-change",
        action="store_true",
        help="Exit 2 when any endpoint/state/schema change is detected.",
    )
    return parser


def main(argv: List[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "snapshot":
        try:
            result = capture(args.base_url, args.endpoints, args.timeout)
            write_json(args.out, result)
        except (ValueError, RuntimeError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        print(args.out)
        return 0

    report = diff_snapshots(read_json(args.before), read_json(args.after))
    rendered = json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False)
    if args.out:
        write_json(args.out, report)
    else:
        print(rendered)
    if args.fail_on_change and report["changed"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
