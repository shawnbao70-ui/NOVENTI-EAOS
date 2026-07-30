"""Ops / probe DTOs — runtime parity with docs/api/ops.openapi.yaml."""

from __future__ import annotations

from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class _ClosedModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ContextEchoRequest(BaseModel):
    """Free-form echo body; elevation keys rejected by reject_body_elevation (PHX-G288)."""

    model_config = ConfigDict(extra="allow")


class HealthPayload(_ClosedModel):
    status: Literal["ok"] = "ok"
    service: str = Field(min_length=1)
    gateway_store: Literal["memory", "sql"] = "memory"


class HealthEnvelope(_ClosedModel):
    data: HealthPayload


class ReleasePosture(_ClosedModel):
    baseline_name: str
    version: str
    alembic_head: str
    sdk_version: str
    deploy_region: str | None = None


class ReleaseEnvelope(_ClosedModel):
    data: ReleasePosture


class AdapterItem(_ClosedModel):
    name: str
    openapi_path: str
    transport: str
    status: str


class OpenApiInventoryProductPosture(_ClosedModel):
    surface: Literal["foundation_openapi_inventory_product"] = (
        "foundation_openapi_inventory_product"
    )
    milestone: Literal["PHX-G288"] = "PHX-G288"
    openapi_contract_count: int = Field(ge=0)
    adapter_count: int = Field(ge=0)
    adapter_registry_status: Literal["aligned", "drift"]
    adapter_registry_aligned: bool
    thin_probe_domains: list[str]
    deferred_domains: list[str]
    route_mount_parity_complete: Literal[True] = True
    known_defer_fences: list[str]
    full_openapi_http_complete: Literal[False] = False
    semantic_remainder_honest: Literal[True] = True
    t0188_status: Literal[
        "mount_parity_complete_outer_close_regression_guard_honest"
    ] = "mount_parity_complete_outer_close_regression_guard_honest"
    fail_closed_reasons: list[str]


class SampleKnowledgePackProductPosture(_ClosedModel):
    surface: Literal["foundation_sample_knowledge_pack"] = (
        "foundation_sample_knowledge_pack"
    )
    milestone: Literal["PHX-G293"] = "PHX-G293"
    pack_path: str = Field(min_length=1)
    assembles: list[str] = Field(min_length=1)
    crud: Literal[False] = False
    brain_execute: Literal["fail_closed"] = "fail_closed"
    twin_authorize: Literal["fail_closed"] = "fail_closed"
    usage: list[str] = Field(min_length=1)
    discovery_routes: list[str] = Field(min_length=1)
    fail_closed_reasons: list[str] = Field(min_length=1)


class AdaptersMeta(_ClosedModel):
    count: int = Field(ge=0)
    openapi_inventory_product: OpenApiInventoryProductPosture
    sample_knowledge_pack_product: SampleKnowledgePackProductPosture


class AdaptersEnvelope(_ClosedModel):
    data: list[AdapterItem]
    meta: AdaptersMeta


class ExecutionContextView(_ClosedModel):
    subject_id: UUID
    subject_type: str
    tenant_id: UUID | None = None
    platform_scope: bool
    correlation_id: str
    roles: list[str]


class ContextEnvelope(_ClosedModel):
    data: ExecutionContextView


class ContextEchoPayload(_ClosedModel):
    context: ExecutionContextView
    echo: dict[str, Any] = Field(default_factory=dict)


class ContextEchoEnvelope(_ClosedModel):
    data: ContextEchoPayload
