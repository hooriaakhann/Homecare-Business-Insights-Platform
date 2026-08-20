"""Small ADLS Gen2 helper used by the public pipeline example."""
from __future__ import annotations

import os
from typing import Iterable

from azure.identity import DefaultAzureCredential
from azure.storage.filedatalake import DataLakeServiceClient


def _service() -> DataLakeServiceClient:
    account_name = os.getenv("ADLS_ACCOUNT_NAME")
    if not account_name:
        raise RuntimeError("ADLS_ACCOUNT_NAME is required.")
    account_url = f"https://{account_name}.dfs.core.windows.net"
    return DataLakeServiceClient(account_url, credential=DefaultAzureCredential())


def upload_bytes(file_system: str, path: str, data: bytes, *, overwrite: bool = True) -> None:
    fs = _service().get_file_system_client(file_system)
    fs.get_file_client(path).upload_data(data, overwrite=overwrite)


def download_bytes(file_system: str, path: str) -> bytes:
    fs = _service().get_file_system_client(file_system)
    return fs.get_file_client(path).download_file().readall()


def path_exists(file_system: str, path: str) -> bool:
    fs = _service().get_file_system_client(file_system)
    try:
        fs.get_file_client(path).get_file_properties()
        return True
    except Exception:
        return False


def list_paths(file_system: str, prefix: str) -> Iterable[str]:
    fs = _service().get_file_system_client(file_system)
    for item in fs.get_paths(path=prefix):
        if not item.is_directory:
            yield item.name
