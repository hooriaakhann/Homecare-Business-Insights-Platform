"""Versioned visit-history helpers."""
from __future__ import annotations

from typing import Any

from shared.utils import deduplicate


def append_visit_versions(previous: list[dict[str, Any]], incoming: list[dict[str, Any]]) -> list[dict[str, Any]]:
    keys = ["schedule_id", "component_id", "last_updated"]
    return deduplicate([*previous, *incoming], keys)


def latest_visit_state(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return deduplicate(rows, ["schedule_id", "component_id"], "last_updated")
