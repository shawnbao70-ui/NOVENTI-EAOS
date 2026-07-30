"""API contract adapter registry (PHX-R17) — no HTTP routers."""

from api.adapters.registry import AdapterDescriptor, list_adapters, require_adapter

__all__ = ["AdapterDescriptor", "list_adapters", "require_adapter"]
