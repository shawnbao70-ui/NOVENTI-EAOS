"""EAOS Python SDK — Phoenix Foundation release surface (PHX-R17)."""

from eaos_sdk.catalog import list_openapi_contracts, load_release_manifest
from eaos_sdk.context import build_tenant_context
from eaos_sdk.results import require_ok, unwrap

__all__ = [
    "build_tenant_context",
    "list_openapi_contracts",
    "load_release_manifest",
    "require_ok",
    "unwrap",
]

__version__ = "0.2.5"
