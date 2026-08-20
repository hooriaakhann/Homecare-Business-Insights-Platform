"""Configuration loader for the public homecare data-platform example."""
from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

DEFAULT_CONFIG = Path(__file__).resolve().parents[2] / "config" / "config.example.json"


@lru_cache(maxsize=1)
def load_config(path: str | None = None) -> dict[str, Any]:
    config_path = Path(path or os.getenv("PIPELINE_CONFIG", DEFAULT_CONFIG))
    with config_path.open("r", encoding="utf-8") as handle:
        config = json.load(handle)

    required = {"base_url", "endpoints", "storage"}
    missing = required.difference(config)
    if missing:
        raise ValueError(f"Missing configuration keys: {sorted(missing)}")

    if not isinstance(config["endpoints"], dict) or not config["endpoints"]:
        raise ValueError("At least one endpoint must be configured.")

    return config


def endpoint_config(endpoint: str) -> dict[str, Any]:
    config = load_config()
    try:
        return config["endpoints"][endpoint]
    except KeyError as exc:
        raise KeyError(f"Unknown endpoint: {endpoint}") from exc
