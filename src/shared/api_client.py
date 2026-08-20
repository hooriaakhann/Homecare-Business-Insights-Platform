"""Generic care-management API client with pagination, retries and throttling."""
from __future__ import annotations

import os
import random
import time
from dataclasses import dataclass
from typing import Any, Iterator

import requests


@dataclass(frozen=True)
class ApiSettings:
    base_url: str
    timeout_seconds: int = 45
    max_retries: int = 5
    page_size: int = 500


class CareApiClient:
    def __init__(self, settings: ApiSettings):
        self.settings = settings
        token = os.getenv("CARE_API_TOKEN")
        company_id = os.getenv("CARE_COMPANY_ID")
        if not token or not company_id:
            raise RuntimeError("CARE_API_TOKEN and CARE_COMPANY_ID must be supplied through the environment.")

        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {token}",
            "X-Company-Id": company_id,
            "Accept": "application/json",
            "User-Agent": "homecare-analytics-public-example/1.0",
        })

    def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        url = f"{self.settings.base_url.rstrip('/')}/{path.lstrip('/')}"
        last_error: Exception | None = None

        for attempt in range(self.settings.max_retries):
            try:
                response = self.session.get(url, params=params, timeout=self.settings.timeout_seconds)
                if response.status_code == 429:
                    retry_after = float(response.headers.get("Retry-After", "1"))
                    time.sleep(retry_after + random.random())
                    continue
                response.raise_for_status()
                return response.json()
            except requests.RequestException as exc:
                last_error = exc
                if attempt == self.settings.max_retries - 1:
                    break
                time.sleep(min(2**attempt, 20) + random.random())

        raise RuntimeError(f"API request failed after retries: {path}") from last_error

    def iter_records(self, endpoint: str, *, updated_since: str | None = None, extra_params: dict[str, Any] | None = None) -> Iterator[dict[str, Any]]:
        page = 1
        while True:
            params: dict[str, Any] = {"page": page, "page_size": self.settings.page_size}
            if updated_since:
                params["updated_since"] = updated_since
            if extra_params:
                params.update(extra_params)

            payload = self._get(endpoint, params=params)
            if isinstance(payload, dict):
                records = payload.get("data") or payload.get("items") or payload.get("results") or []
            elif isinstance(payload, list):
                records = payload
            else:
                raise TypeError(f"Unexpected payload type for {endpoint}: {type(payload)!r}")

            if not records:
                return
            for record in records:
                if isinstance(record, dict):
                    yield record
            if len(records) < self.settings.page_size:
                return
            page += 1
