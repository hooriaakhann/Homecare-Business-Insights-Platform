"""Simplified public example of an incremental-load watermark pattern."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone


@dataclass(frozen=True)
class WatermarkWindow:
    start: datetime
    end: datetime


def build_incremental_window(
    last_successful_watermark: datetime,
    *,
    overlap_minutes: int = 60,
    now: datetime | None = None,
) -> WatermarkWindow:
    """Return a safe incremental extraction window with overlap."""
    if last_successful_watermark.tzinfo is None:
        raise ValueError("watermark must be timezone-aware")

    end = now or datetime.now(timezone.utc)
    start = last_successful_watermark - timedelta(minutes=overlap_minutes)

    if start >= end:
        raise ValueError("watermark window is invalid")

    return WatermarkWindow(start=start, end=end)


def should_advance_watermark(*, extract_ok: bool, curate_ok: bool) -> bool:
    """Advance state only after all required processing stages succeed."""
    return extract_ok and curate_ok
