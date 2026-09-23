"""Read-only Grazer-style client for RustChain RIP-302 Agent Economy.

This integration intentionally exposes only public browsing endpoints. It never
posts jobs, claims work, moves escrow, or signs wallet actions.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, Optional
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode, urljoin
from urllib.request import Request, urlopen


DEFAULT_BASE_URL = "https://50.28.86.131"
VALID_CATEGORIES = frozenset(
    {
        "research",
        "code",
        "video",
        "audio",
        "writing",
        "translation",
        "data",
        "design",
        "testing",
        "other",
    }
)
VALID_STATUSES = frozenset(
    {"open", "claimed", "delivered", "completed", "disputed", "expired", "cancelled"}
)


class AgentEconomyError(RuntimeError):
    """Raised when the RIP-302 API cannot satisfy a read request."""


@dataclass(frozen=True)
class SearchResult:
    """Compact, normalized search result for agent marketplace discovery."""

    job_id: str
    title: str
    description: str
    category: str
    status: str
    reward_rtc: float
    poster_wallet: str
    worker_wallet: Optional[str]
    created_at: Optional[int]
    raw: Mapping[str, Any]

    @classmethod
    def from_job(cls, job: Mapping[str, Any]) -> "SearchResult":
        reward_raw = job.get("reward_rtc", 0)
        try:
            reward = float(reward_raw)
        except (TypeError, ValueError):
            reward = 0.0
        created_raw = job.get("created_at")
        try:
            created_at = int(created_raw) if created_raw is not None else None
        except (TypeError, ValueError):
            created_at = None
        worker = job.get("worker_wallet")
        return cls(
            job_id=str(job.get("job_id", "")),
            title=str(job.get("title", "")),
            description=str(job.get("description", "")),
            category=str(job.get("category", "")),
            status=str(job.get("status", "")),
            reward_rtc=reward,
            poster_wallet=str(job.get("poster_wallet", "")),
            worker_wallet=None if worker in (None, "") else str(worker),
            created_at=created_at,
            raw=dict(job),
        )

    def as_dict(self) -> Dict[str, Any]:
        return {
            "job_id": self.job_id,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "status": self.status,
            "reward_rtc": self.reward_rtc,
            "poster_wallet": self.poster_wallet,
            "worker_wallet": self.worker_wallet,
            "created_at": self.created_at,
        }


class AgentEconomyGrazer:
    """Discover RIP-302 jobs and agent reputation without wallet-side effects.

    The server's current GET `/agent/jobs` route is public/read-only. This class
    deliberately does not wrap POST/claim/deliver/accept/dispute/cancel actions.
    """

    def __init__(self, base_url: str = DEFAULT_BASE_URL, timeout: float = 10.0):
        base_url = str(base_url).strip().rstrip("/")
        if not base_url.startswith(("http://", "https://")):
            raise ValueError("base_url must use http:// or https://")
        if timeout <= 0:
            raise ValueError("timeout must be > 0")
        self.base_url = base_url
        self.timeout = float(timeout)

    def browse(
        self,
        *,
        category: Optional[str] = None,
        status: str = "open",
        limit: int = 50,
        offset: int = 0,
        min_reward: float = 0.0,
    ) -> Dict[str, Any]:
        """Browse jobs with server-side RIP-302 filters.

        Returns the API metadata plus both raw `jobs` and normalized `results`.
        """
        status = self._validate_status(status)
        category = self._validate_category(category)
        limit = self._validate_limit(limit)
        offset = self._validate_offset(offset)
        min_reward = self._validate_min_reward(min_reward)

        params: Dict[str, Any] = {
            "status": status,
            "limit": limit,
            "offset": offset,
            "min_reward": min_reward,
        }
        if category:
            params["category"] = category

        payload = self._get("/agent/jobs", params=params)
        jobs = payload.get("jobs", []) if isinstance(payload, Mapping) else []
        if not isinstance(jobs, list):
            raise AgentEconomyError("Malformed /agent/jobs response: jobs must be a list")
        results = [SearchResult.from_job(j).as_dict() for j in jobs if isinstance(j, Mapping)]

        return {
            "jobs": jobs,
            "results": results,
            "total": payload.get("total", len(jobs)) if isinstance(payload, Mapping) else len(jobs),
            "limit": payload.get("limit", limit) if isinstance(payload, Mapping) else limit,
            "offset": payload.get("offset", offset) if isinstance(payload, Mapping) else offset,
            "categories": payload.get("categories", sorted(VALID_CATEGORIES))
            if isinstance(payload, Mapping)
            else sorted(VALID_CATEGORIES),
        }

    def search(
        self,
        query: str,
        *,
        category: Optional[str] = None,
        status: str = "open",
        limit: int = 50,
        offset: int = 0,
        min_reward: float = 0.0,
    ) -> List[Dict[str, Any]]:
        """Grazer-style keyword discovery over title, description, category and tags."""
        needle = str(query).strip().casefold()
        if not needle:
            raise ValueError("query must not be empty")
        page = self.browse(
            category=category,
            status=status,
            limit=limit,
            offset=offset,
            min_reward=min_reward,
        )
        matches: List[Dict[str, Any]] = []
        for raw, normalized in zip(page["jobs"], page["results"]):
            tags = raw.get("tags", []) if isinstance(raw, Mapping) else []
            if isinstance(tags, str):
                try:
                    decoded = json.loads(tags)
                    tags = decoded if isinstance(decoded, list) else [tags]
                except json.JSONDecodeError:
                    tags = [tags]
            haystack = " ".join(
                [
                    normalized.get("title", ""),
                    normalized.get("description", ""),
                    normalized.get("category", ""),
                    " ".join(str(tag) for tag in tags if tag is not None),
                ]
            ).casefold()
            if needle in haystack:
                matches.append(normalized)
        return matches

    def job(self, job_id: str) -> Dict[str, Any]:
        """Return one job's detail/activity/rating document."""
        job_id = self._validate_identifier(job_id, "job_id")
        payload = self._get(f"/agent/jobs/{quote(job_id, safe='')}")
        if not isinstance(payload, Mapping):
            raise AgentEconomyError("Malformed job detail response")
        return dict(payload)

    def reputation(self, wallet: str) -> Dict[str, Any]:
        """Return the public reputation document for a wallet."""
        wallet = self._validate_identifier(wallet, "wallet")
        payload = self._get(f"/agent/reputation/{quote(wallet, safe='')}")
        if not isinstance(payload, Mapping):
            raise AgentEconomyError("Malformed reputation response")
        return dict(payload)

    def stats(self) -> Dict[str, Any]:
        """Return marketplace-wide public statistics."""
        payload = self._get("/agent/stats")
        if not isinstance(payload, Mapping):
            raise AgentEconomyError("Malformed stats response")
        return dict(payload)

    def _get(self, path: str, params: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
        query = urlencode(params or {})
        url = urljoin(self.base_url + "/", path.lstrip("/"))
        if query:
            url += "?" + query
        request = Request(url, headers={"Accept": "application/json", "User-Agent": "grazer-rip302/1.0"})
        try:
            with urlopen(request, timeout=self.timeout) as response:
                body = response.read().decode("utf-8")
                status = getattr(response, "status", 200)
        except HTTPError as exc:
            detail = self._decode_error_body(exc)
            raise AgentEconomyError(f"RIP-302 HTTP {exc.code}: {detail}") from exc
        except URLError as exc:
            raise AgentEconomyError(f"RIP-302 network error: {exc.reason}") from exc

        if not (200 <= int(status) < 300):
            raise AgentEconomyError(f"RIP-302 HTTP {status}")
        try:
            payload = json.loads(body)
        except json.JSONDecodeError as exc:
            raise AgentEconomyError("RIP-302 returned non-JSON data") from exc
        if not isinstance(payload, dict):
            raise AgentEconomyError("RIP-302 returned a non-object JSON document")
        if payload.get("error") and payload.get("ok") is not True:
            raise AgentEconomyError(str(payload["error"]))
        return payload

    @staticmethod
    def _decode_error_body(exc: HTTPError) -> str:
        try:
            raw = exc.read().decode("utf-8")
            payload = json.loads(raw)
            if isinstance(payload, Mapping):
                return str(payload.get("error") or payload)
            return str(payload)
        except Exception:
            return exc.reason or "request failed"

    @staticmethod
    def _validate_limit(limit: int) -> int:
        if isinstance(limit, bool):
            raise ValueError("limit must be an integer from 1 to 100")
        try:
            value = int(limit)
        except (TypeError, ValueError) as exc:
            raise ValueError("limit must be an integer from 1 to 100") from exc
        if value < 1 or value > 100:
            raise ValueError("limit must be between 1 and 100")
        return value

    @staticmethod
    def _validate_offset(offset: int) -> int:
        if isinstance(offset, bool):
            raise ValueError("offset must be a non-negative integer")
        try:
            value = int(offset)
        except (TypeError, ValueError) as exc:
            raise ValueError("offset must be a non-negative integer") from exc
        if value < 0:
            raise ValueError("offset must be non-negative")
        return value

    @staticmethod
    def _validate_min_reward(min_reward: float) -> float:
        try:
            value = float(min_reward)
        except (TypeError, ValueError) as exc:
            raise ValueError("min_reward must be a non-negative number") from exc
        if value < 0 or value != value or value in (float("inf"), float("-inf")):
            raise ValueError("min_reward must be a finite non-negative number")
        return value

    @staticmethod
    def _validate_category(category: Optional[str]) -> Optional[str]:
        if category is None or str(category).strip() == "":
            return None
        value = str(category).strip().lower()
        if value not in VALID_CATEGORIES:
            raise ValueError(f"category must be one of: {', '.join(sorted(VALID_CATEGORIES))}")
        return value

    @staticmethod
    def _validate_status(status: str) -> str:
        value = str(status).strip().lower()
        if value not in VALID_STATUSES:
            raise ValueError(f"status must be one of: {', '.join(sorted(VALID_STATUSES))}")
        return value

    @staticmethod
    def _validate_identifier(value: str, name: str) -> str:
        cleaned = str(value).strip()
        if not cleaned:
            raise ValueError(f"{name} must not be empty")
        if len(cleaned) > 256:
            raise ValueError(f"{name} is too long")
        return cleaned
