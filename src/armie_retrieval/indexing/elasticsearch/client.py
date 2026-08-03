"""Small requests-based Elasticsearch adapter with explicit prerequisite errors."""

from __future__ import annotations

import json
import os
from typing import Any, Iterable

import requests


class ElasticsearchPrerequisiteError(RuntimeError):
    """Raised when local Elasticsearch is unavailable or incompatible."""


class ElasticsearchClient:
    def __init__(self, base_url: str | None = None, *, username: str | None = None, password: str | None = None, timeout: float = 10.0) -> None:
        self.base_url = (base_url or os.getenv("ARMIE_ELASTICSEARCH_URL", "http://127.0.0.1:9200")).rstrip("/")
        self.auth = (username or os.getenv("ARMIE_ELASTICSEARCH_USERNAME"), password or os.getenv("ARMIE_ELASTICSEARCH_PASSWORD"))
        self.timeout = timeout

    def request(self, method: str, path: str, **kwargs: Any) -> requests.Response:
        try:
            response = requests.request(method, f"{self.base_url}/{path.lstrip('/')}", auth=self.auth if all(self.auth) else None, timeout=self.timeout, **kwargs)
        except requests.RequestException as exc:
            raise ElasticsearchPrerequisiteError(f"Elasticsearch is unreachable at {self.base_url}; start docker compose and retry") from exc
        if response.status_code >= 400:
            raise ElasticsearchPrerequisiteError(f"Elasticsearch {method} {path} failed with HTTP {response.status_code}: {response.text[:300]}")
        return response

    def health(self) -> dict[str, Any]:
        info = self.request("GET", "/").json()
        cluster = self.request("GET", "/_cluster/health").json()
        return {"reachable": True, "version": info.get("version", {}).get("number"), "cluster": cluster}

    def create_index(self, index: str, mapping: dict[str, Any]) -> None:
        self.request("PUT", index, json=mapping)

    def bulk_index(self, index: str, documents: Iterable[dict[str, Any]], *, batch_size: int = 250) -> dict[str, Any]:
        records = list(documents)
        failures: list[dict[str, Any]] = []
        indexed = 0
        for offset in range(0, len(records), batch_size):
            batch = records[offset : offset + batch_size]
            lines: list[str] = []
            for document in batch:
                lines.append(json.dumps({"index": {"_index": index, "_id": document["expert_id"]}}))
                lines.append(json.dumps(document))
            response = self.request("POST", "_bulk", data="\n".join(lines) + "\n", headers={"Content-Type": "application/x-ndjson"}).json()
            for item in response.get("items", []):
                result = item.get("index", {})
                if result.get("status", 500) >= 300:
                    failures.append(result)
                else:
                    indexed += 1
        if failures:
            raise ElasticsearchPrerequisiteError(f"bulk indexing had {len(failures)} permanent failures: {failures[:2]}")
        return {"indexed": indexed, "rejected": 0, "index": index}

    def alias(self, alias: str, index: str, *, write: bool = False) -> None:
        # Versioned builds must move aliases atomically.  Leaving the prior
        # write alias in place makes Elasticsearch reject the update because
        # an alias may have only one write index.
        actions = []
        try:
            existing = self.request("GET", f"_alias/{alias}").json()
        except ElasticsearchPrerequisiteError as exc:
            if "HTTP 404" not in str(exc):
                raise
            existing = {}
        actions.extend({"remove": {"index": existing_index, "alias": alias}} for existing_index in existing)
        actions.append({"add": {"index": index, "alias": alias, **({"is_write_index": True} if write else {})}})
        self.request("POST", "_aliases", json={"actions": actions})
