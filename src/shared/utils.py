"""Shared record-normalization helpers."""
from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Iterable

_SNAKE = re.compile(r"[^a-zA-Z0-9]+")


def snake_case(value: str) -> str:
    return _SNAKE.sub("_", value).strip("_").lower()


def normalize_record(record: dict[str, Any]) -> dict[str, Any]:
    normalized: dict[str, Any] = {}
    for key, value in record.items():
        clean_key = snake_case(str(key))
        if isinstance(value, dict):
            normalized[clean_key] = {snake_case(str(k)): v for k, v in value.items()}
        else:
            normalized[clean_key] = value
    return normalized


def parse_datetime(value: Any) -> datetime | None:
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        return value
    text = str(value).strip().replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return None


def deduplicate(records: Iterable[dict[str, Any]], keys: list[str], order_field: str | None = None) -> list[dict[str, Any]]:
    chosen: dict[tuple[Any, ...], dict[str, Any]] = {}
    for record in records:
        key = tuple(record.get(k) for k in keys)
        current = chosen.get(key)
        if current is None:
            chosen[key] = record
            continue

        if order_field:
            new_value = parse_datetime(record.get(order_field))
            old_value = parse_datetime(current.get(order_field))
            if (new_value or datetime.min) >= (old_value or datetime.min):
                chosen[key] = record
        else:
            chosen[key] = record

    return list(chosen.values())


def extract_child_rows(records: Iterable[dict[str, Any]], field: str, parent_key: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for parent in records:
        children = parent.get(field) or []
        if not isinstance(children, list):
            continue
        for child in children:
            if isinstance(child, dict):
                row = normalize_record(child)
                row[parent_key] = parent.get(parent_key)
                rows.append(row)
    return rows
