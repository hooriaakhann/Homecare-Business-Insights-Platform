"""Generic SCD2 history helper for client-style dimensions."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def build_scd2(
    previous: list[dict[str, Any]],
    current: list[dict[str, Any]],
    *,
    key: str = "client_id",
    tracked_fields: tuple[str, ...] = ("status", "service_region", "funding_type"),
) -> list[dict[str, Any]]:
    now = datetime.now(timezone.utc).isoformat()
    active = {row[key]: row.copy() for row in previous if row.get("is_current") is True}
    history = [row.copy() for row in previous if row.get("is_current") is not True]

    for row in current:
        entity_id = row.get(key)
        prior = active.get(entity_id)
        changed = prior is None or any(prior.get(field) != row.get(field) for field in tracked_fields)

        if not changed:
            history.append(prior)
            active.pop(entity_id, None)
            continue

        if prior is not None:
            prior["is_current"] = False
            prior["valid_to"] = now
            history.append(prior)

        new_row = row.copy()
        new_row["valid_from"] = now
        new_row["valid_to"] = None
        new_row["is_current"] = True
        history.append(new_row)
        active.pop(entity_id, None)

    history.extend(active.values())
    return history
