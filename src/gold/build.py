"""Gold layer: curated entities -> analytical dimensions, facts and cross-references."""
from __future__ import annotations

import logging
from io import BytesIO
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq

from shared.adls import download_bytes, path_exists, upload_bytes
from shared.config_loader import load_config

log = logging.getLogger(__name__)

TABLE_MAP = {
    "clients": "dim_client",
    "employees": "dim_employee",
    "services": "dim_service",
    "visits": "fact_visit",
    "care_summaries": "fact_care_summary",
}


def _read(container: str, path: str) -> list[dict[str, Any]]:
    if not path_exists(container, path):
        return []
    return pq.read_table(BytesIO(download_bytes(container, path))).to_pylist()


def _write(container: str, path: str, rows: list[dict[str, Any]]) -> None:
    table = pa.Table.from_pylist(rows) if rows else pa.table({})
    buffer = BytesIO()
    pq.write_table(table, buffer, compression="snappy")
    upload_bytes(container, path, buffer.getvalue())


def _select_fields(row: dict[str, Any], fields: list[str]) -> dict[str, Any]:
    return {field: row.get(field) for field in fields}


def build_gold(endpoint: str) -> dict[str, Any]:
    config = load_config()
    silver = config["storage"]["silver"]
    gold = config["storage"]["gold"]
    rows = _read(silver, f"{endpoint}/{endpoint}.parquet")

    table_name = TABLE_MAP.get(endpoint, f"fact_{endpoint}")
    projection = config["endpoints"][endpoint].get("gold_fields")
    if projection:
        rows = [_select_fields(row, projection) for row in rows]

    if endpoint == "visits":
        by_partition: dict[tuple[str, str], list[dict[str, Any]]] = {}
        for row in rows:
            start = str(row.get("start_at") or row.get("scheduled_start") or "")
            year = start[:4] if len(start) >= 4 else "unknown"
            month = start[5:7] if len(start) >= 7 else "unknown"
            by_partition.setdefault((year, month), []).append(row)

        for (year, month), partition_rows in by_partition.items():
            _write(gold, f"{table_name}/year={year}/month={month}/{table_name}.parquet", partition_rows)
    else:
        _write(gold, f"{table_name}/{table_name}.parquet", rows)

    log.info("Gold table built", extra={"table": table_name, "rows": len(rows)})
    return {"endpoint": endpoint, "table": table_name, "rows": len(rows)}
