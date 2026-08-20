"""Watermark persistence for incremental API loads."""
from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

from azure.data.tables import TableServiceClient
from azure.identity import DefaultAzureCredential

TABLE_NAME = os.getenv("WATERMARK_TABLE", "PipelineWatermarks")
PARTITION_KEY = "care-platform"


def _table():
    account_name = os.getenv("ADLS_ACCOUNT_NAME")
    if not account_name:
        raise RuntimeError("ADLS_ACCOUNT_NAME is required.")
    url = f"https://{account_name}.table.core.windows.net"
    service = TableServiceClient(url, credential=DefaultAzureCredential())
    service.create_table_if_not_exists(TABLE_NAME)
    return service.get_table_client(TABLE_NAME)


def get_watermark(endpoint: str, *, default_days_back: int = 30, overlap_minutes: int = 15) -> datetime:
    try:
        entity = _table().get_entity(PARTITION_KEY, endpoint)
        value = datetime.fromisoformat(entity["watermark"])
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
    except Exception:
        value = datetime.now(timezone.utc) - timedelta(days=default_days_back)
    return value - timedelta(minutes=overlap_minutes)


def set_watermark(endpoint: str, value: datetime) -> None:
    value = value.astimezone(timezone.utc)
    _table().upsert_entity({
        "PartitionKey": PARTITION_KEY,
        "RowKey": endpoint,
        "watermark": value.isoformat(),
    })
