"""Dev-only demo bootstrap response DTOs (never mounted on production app)."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class _ClosedModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class DemoBootstrapData(_ClosedModel):
    available: bool
    reason: str | None = None
    milestone: str | None = None
    subject_id: str | None = None
    tenant_id: str | None = None
    subject_type: str | None = None
    declared_surface_keys: list[str] | None = None
    product_url: str | None = None
    ops_url: str | None = None
    notes: list[str] | None = None
    extension_id: str | None = None
    extension_key: str | None = None
    extension_version: str | None = None
    extensions_url: str | None = None
    listing_id: str | None = None
    listing_package_key: str | None = None
    host_acquire_url: str | None = None
    host_actions: list[str] | None = None
    sample_knowledge_pack_path: str | None = None
    sample_knowledge_pack_url: str | None = None
    sample_knowledge_pack_milestone: str | None = None


class DemoBootstrapEnvelope(_ClosedModel):
    data: DemoBootstrapData = Field(...)
