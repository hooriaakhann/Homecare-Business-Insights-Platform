"""Silver layer: normalize, type and deduplicate Bronze batches."""
from __future__ import annotations

import logging
from io import BytesIO
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq

from shared.adls import download_bytes, path_exists, upload_bytes
from shared.config_loader import endpoint_config, load_config
from shared.utils import deduplicate, normalize_record

log = logging.getLogger(__name__)


def _read_parquet(data: bytes) -> list[dict[str, Any]]:
    return pq.read_table(BytesIO(data)).to_pylist()


def _write_parquet(records: list[dict[str, Any]]) -> bytes:
    table = pa.Table.from_pylist(records) if records else pa.table({})
    buffer = BytesIO()
    pq.write_table(table, buffer, compression="snappy")
    return buffer.getvalue()


def curate_endpoint(bronze_result: dict[str, Any]) -> dict[str, Any]:
    config = load_config()
    endpoint = bronze_result["endpoint"]
    ep = endpoint_config(endpoint)
    bronze_container = config["storage"]["bronze"]
    silver_container = config["storage"]["silver"]

    incoming = _read_parquet(download_bytes(bronze_container, bronze_result["main_path"]))
    incoming = [normalize_record(row) for row in incoming]

    silver_path = f"{endpoint}/{endpoint}.parquet"
    existing: list[dict[str, Any]] = []
    if path_exists(silver_container, silver_path):
        existing = _read_parquet(download_bytes(silver_container, silver_path))

    keys = ep.get("business_keys", ["id"])
    order_field = ep.get("order_field", "updated_at")
    merged = deduplicate([*existing, *incoming], keys, order_field)
    upload_bytes(silver_container, silver_path, _write_parquet(merged))

    log.info("Silver dataset curated", extra={"endpoint": endpoint, "incoming": len(incoming), "rows": len(merged)})
    return {**bronze_result, "silver_path": silver_path, "silver_rows": len(merged)}
