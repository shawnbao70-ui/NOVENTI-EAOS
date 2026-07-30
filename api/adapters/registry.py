"""OpenAPI-backed adapter registry for EAOS release train."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from eaos_sdk.catalog import list_openapi_contracts

_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True, slots=True)
class AdapterDescriptor:
    name: str
    openapi_path: str
    transport: str = "openapi-3.1"
    status: str = "contract-ready"


def list_adapters() -> list[AdapterDescriptor]:
    adapters: list[AdapterDescriptor] = []
    for relative in list_openapi_contracts():
        path = Path(relative)
        name = path.stem.replace(".openapi", "")
        adapters.append(
            AdapterDescriptor(
                name=name,
                openapi_path=relative.replace("\\", "/"),
            )
        )
    return adapters


def require_adapter(name: str) -> AdapterDescriptor:
    for adapter in list_adapters():
        if adapter.name == name:
            full = _ROOT / adapter.openapi_path
            if not full.is_file():
                raise FileNotFoundError(adapter.openapi_path)
            return adapter
    raise KeyError(name)
