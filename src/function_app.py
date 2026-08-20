"""Azure Durable Functions orchestration for the public data-platform example."""
from __future__ import annotations

from datetime import datetime, timezone

import azure.durable_functions as df
import azure.functions as func

from bronze.ingest import ingest_endpoint
from gold.build import build_gold
from shared.config_loader import load_config
from shared.logging_config import configure_logging
from shared.watermark import set_watermark
from silver.curate import curate_endpoint

configure_logging()

app = df.DFApp(http_auth_level=func.AuthLevel.FUNCTION)


@app.route(route="pipeline/start")
@app.durable_client_input(client_name="client")
async def start_pipeline(req: func.HttpRequest, client: df.DurableOrchestrationClient):
    payload = req.get_json() if req.get_body() else {}
    instance_id = await client.start_new("pipeline_orchestrator", None, payload)
    return client.create_check_status_response(req, instance_id)


@app.orchestration_trigger(context_name="context")
def pipeline_orchestrator(context: df.DurableOrchestrationContext):
    payload = context.get_input() or {}
    config = load_config()
    endpoints = payload.get("endpoints") or list(config["endpoints"].keys())
    mode = payload.get("mode", "incremental")

    results = []
    for endpoint in endpoints:
        result = yield context.call_activity(
            "run_endpoint",
            {"endpoint": endpoint, "mode": mode},
        )
        results.append(result)
    return results


@app.activity_trigger(input_name="payload")
def run_endpoint(payload: dict):
    endpoint = payload["endpoint"]
    mode = payload.get("mode", "incremental")

    bronze = ingest_endpoint(endpoint, mode=mode)
    silver = curate_endpoint(bronze)
    gold = build_gold(endpoint)

    watermark_value = datetime.fromisoformat(bronze["max_seen_at"])
    set_watermark(endpoint, watermark_value.astimezone(timezone.utc))

    return {
        "endpoint": endpoint,
        "bronze_records": bronze["records"],
        "silver_rows": silver["silver_rows"],
        "gold_table": gold["table"],
        "gold_rows": gold["rows"],
    }
