#!/usr/bin/env python3
"""Read-only RustChain state snapshot + diff tool."""

from __future__ import annotations

import argparse
import json
import ssl
import sys
import time
import urllib.request
from pathlib import Path
from typing import Any, Callable

ENDPOINTS = ("/health", "/epoch", "/api/miners")


def fetch_json(url: str, timeout: float = 10.0, insecure: bool = False) -> dict[str, Any]:
    ctx = ssl._create_unverified_context() if insecure else None
    req = urllib.request.Request(url, headers={"User-Agent": "rustchain-state-diff/1.0"})
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
        if resp.status < 200 or resp.status >= 300:
            raise RuntimeError(f"HTTP {resp.status} from {url}")
        raw = resp.read().decode("utf-8")
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object from {url}")
    return data


def _miner_key(row: dict[str, Any], index: int) -> str:
    for key in ("miner", "miner_id", "wallet", "name", "id"):
        value = row.get(key)
        if value not in (None, ""):
            return str(value)
    return f"<anonymous:{index}>"


def summarize_miners(payload: dict[str, Any]) -> dict[str, Any]:
    miners = payload.get("miners", [])
    if not isinstance(miners, list):
        raise ValueError("/api/miners: 'miners' must be a list")
    selected = {}
    fields = (
        "device_arch",
        "device_family",
        "hardware_type",
        "last_attest",
        "last_seen",
        "fingerprint_passed",
        "status",
    )
    for index, row in enumerate(miners):
        if not isinstance(row, dict):
            raise ValueError(f"/api/miners: miners[{index}] must be an object")
        key = _miner_key(row, index)
        selected[key] = {field: row[field] for field in fields if field in row}
    pagination = payload.get("pagination")
    total = None
    total_enrolled = None
    if isinstance(pagination, dict):
        total = pagination.get("total")
        total_enrolled = pagination.get("total_enrolled")
    return {
        "returned": len(miners),
        "total": total,
        "total_enrolled": total_enrolled,
        "miners": selected,
    }


def make_snapshot(
    node: str,
    *,
    fetcher: Callable[[str, float, bool], dict[str, Any]] | None = None,
    timeout: float = 10.0,
    insecure: bool = False,
    captured_at: int | None = None,
) -> dict[str, Any]:
    fetcher = fetcher or (lambda url, timeout, insecure: fetch_json(url, timeout, insecure))
    node = node.rstrip("/")
    data = {}
    for endpoint in ENDPOINTS:
        data[endpoint] = fetcher(node + endpoint, timeout, insecure)

    health = data["/health"]
    epoch = data["/epoch"]
    snapshot = {
        "schema_version": "1.0",
        "captured_at": int(time.time()) if captured_at is None else int(captured_at),
        "node": node,
        "health": {
            "ok": health.get("ok"),
            "version": health.get("version"),
        },
        "epoch": {
            key: epoch.get(key)
            for key in ("epoch", "slot", "blocks_per_epoch", "enrolled_miners")
            if key in epoch
        },
        "miner_summary": summarize_miners(data["/api/miners"]),
    }
    return snapshot


def diff_snapshots(old: dict[str, Any], new: dict[str, Any]) -> dict[str, Any]:
    changes: list[dict[str, Any]] = []
    regressions: list[dict[str, Any]] = []

    def add(path: str, before: Any, after: Any, regression: bool = False) -> None:
        item = {"path": path, "before": before, "after": after}
        changes.append(item)
        if regression:
            regressions.append(item)

    old_health = old.get("health", {})
    new_health = new.get("health", {})
    for field in ("ok", "version"):
        if old_health.get(field) != new_health.get(field):
            add(
                f"health.{field}",
                old_health.get(field),
                new_health.get(field),
                regression=(field == "ok" and old_health.get(field) is True and new_health.get(field) is not True),
            )

    old_epoch = old.get("epoch", {})
    new_epoch = new.get("epoch", {})
    for field in sorted(set(old_epoch) | set(new_epoch)):
        if old_epoch.get(field) != new_epoch.get(field):
            add(f"epoch.{field}", old_epoch.get(field), new_epoch.get(field))

    old_ms = old.get("miner_summary", {})
    new_ms = new.get("miner_summary", {})
    for field in ("returned", "total", "total_enrolled"):
        if old_ms.get(field) != new_ms.get(field):
            add(f"miner_summary.{field}", old_ms.get(field), new_ms.get(field))

    old_miners = old_ms.get("miners", {}) if isinstance(old_ms.get("miners", {}), dict) else {}
    new_miners = new_ms.get("miners", {}) if isinstance(new_ms.get("miners", {}), dict) else {}
    old_ids = set(old_miners)
    new_ids = set(new_miners)

    added = sorted(new_ids - old_ids)
    removed = sorted(old_ids - new_ids)
    changed = {}
    for miner_id in sorted(old_ids & new_ids):
        if old_miners[miner_id] != new_miners[miner_id]:
            changed[miner_id] = {
                "before": old_miners[miner_id],
                "after": new_miners[miner_id],
            }

    return {
        "schema_version": "1.0",
        "old_captured_at": old.get("captured_at"),
        "new_captured_at": new.get("captured_at"),
        "node_changed": old.get("node") != new.get("node"),
        "changes": changes,
        "miner_changes": {
            "added": added,
            "removed": removed,
            "changed": changed,
        },
        "regressions": regressions,
        "changed": bool(changes or added or removed or changed or old.get("node") != new.get("node")),
    }


def _load(path: str) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: snapshot must be a JSON object")
    return data


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Capture read-only RustChain public state or compare two saved snapshots."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    capture = sub.add_parser("capture", help="GET the public endpoints and save a normalized snapshot")
    capture.add_argument("--node", default="https://rustchain.org")
    capture.add_argument("--output", required=True)
    capture.add_argument("--timeout", type=float, default=10.0)
    capture.add_argument("--insecure", action="store_true")

    diff = sub.add_parser("diff", help="Compare two snapshot JSON files")
    diff.add_argument("old")
    diff.add_argument("new")
    diff.add_argument("--json", action="store_true", dest="as_json")
    diff.add_argument(
        "--fail-on-regression",
        action="store_true",
        help="exit 2 only when a health regression is detected",
    )

    args = parser.parse_args(argv)
    try:
        if args.command == "capture":
            snap = make_snapshot(
                args.node,
                timeout=args.timeout,
                insecure=args.insecure,
            )
            Path(args.output).write_text(json.dumps(snap, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            print(f"wrote {args.output}")
            return 0

        old = _load(args.old)
        new = _load(args.new)
        result = diff_snapshots(old, new)
        if args.as_json:
            print(json.dumps(result, indent=2, sort_keys=True))
        else:
            print(f"changed={result['changed']} regressions={len(result['regressions'])}")
            for item in result["changes"]:
                print(f"{item['path']}: {item['before']!r} -> {item['after']!r}")
            mc = result["miner_changes"]
            if mc["added"]:
                print("miners added: " + ", ".join(mc["added"]))
            if mc["removed"]:
                print("miners removed: " + ", ".join(mc["removed"]))
            for miner_id in mc["changed"]:
                print(f"miner changed: {miner_id}")
        if args.fail_on_regression and result["regressions"]:
            return 2
        return 0
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
