"""Bronze layer: source API -> immutable Parquet batches in ADLS Gen2."""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from io import BytesIO

import pyarrow as pa
import pyarrow.parquet as pq

from shared.adls import upload_bytes
from shared.api_client import ApiSettings, CareApiClient
from shared.config_loader import endpoint_config, load_config
from shared.utils import extract_child_rows, normalize_record
from shared.watermark import get_watermark

log = logging.getLogger(__name__)


def _to_parquet_bytes(records: list[dict]) -> bytes:
    table = pa.Table.from_pylist(records) if records else pa.table({})
    buffer = BytesIO()
    pq.write_table(table, buffer, compression="snappy")
    return buffer.getvalue()


def ingest_endpoint(endpoint: str, *, mode: str = "incremental") -> dict:
    config = load_config()
    ep = endpoint_config(endpoint)
    now = datetime.now(timezone.utc)
    batch_id = uuid.uuid4().hex
    run_date = now.date().isoformat()

    updated_since = None
    if mode == "incremental":
        overlap = int(ep.get("overlap_minutes", 15))
        updated_since = get_watermark(endpoint, overlap_minutes=overlap).isoformat()

    client = CareApiClient(
        ApiSettings(
            base_url=config["base_url"],
            timeout_seconds=int(config.get("timeout_seconds", 45)),
            page_size=int(config.get("page_size", 500)),
        )
    )

    records = [normalize_record(r) for r in client.iter_records(endpoint, updated_since=updated_since)]
    raw_container = config["storage"]["bronze"]
    main_path = f"source/{endpoint}/date={run_date}/batch={batch_id}/{endpoint}.parquet"
    upload_bytes(raw_container, main_path, _to_parquet_bytes(records))

    child_outputs: dict[str, str] = {}
    for child in ep.get("child_arrays", []):
        field = child["field"]
        child_name = child["name"]
        parent_key = child["parent_key"]
        rows = extract_child_rows(records, field, parent_key)
        child_path = f"source/{child_name}/date={run_date}/batch={batch_id}/{child_name}.parquet"
        upload_bytes(raw_container, child_path, _to_parquet_bytes(rows))
        child_outputs[child_name] = child_path

    log.info("Bronze batch written", extra={"endpoint": endpoint, "records": len(records), "batch": batch_id})
    return {
        "endpoint": endpoint,
        "batch_id": batch_id,
        "run_date": run_date,
        "records": len(records),
        "main_path": main_path,
        "children": child_outputs,
        "max_seen_at": now.isoformat(),
    }
