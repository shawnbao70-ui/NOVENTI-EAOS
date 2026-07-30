"""Platform IdP + Roles request/response DTOs — runtime parity with docs/api/platform.openapi.yaml."""

from __future__ import annotations

from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class _ClosedModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class EmptyBody(_ClosedModel):
    """Empty body; context override fields are rejected via extra=forbid."""


class CountMeta(_ClosedModel):
    count: int = Field(ge=0)


class DeclaredRole(_ClosedModel):
    id: UUID
    name: str = Field(min_length=1)
    status: str = Field(min_length=1)
    version: int = Field(ge=0)


class DeclaredRoleListEnvelope(_ClosedModel):
    data: list[DeclaredRole]
    meta: CountMeta


class DeclaredRoleEnvelope(_ClosedModel):
    data: DeclaredRole


class DeclaredRoleActionData(DeclaredRole):
    action: str = Field(min_length=1)


class DeclaredRoleActionEnvelope(_ClosedModel):
    data: DeclaredRoleActionData


class IdpIssuer(_ClosedModel):
    id: UUID
    issuer: str = Field(min_length=1)
    jwks_url: str | None = None
    has_jwks_json: bool
    status: str = Field(min_length=1)
    version: int = Field(ge=0)


class IdpIssuerEnvelope(_ClosedModel):
    data: IdpIssuer


class IdpIssuerListEnvelope(_ClosedModel):
    data: list[IdpIssuer]
    meta: CountMeta


class DiscoveryRegistryWritePosture(_ClosedModel):
    enabled: bool
    action: str = Field(min_length=1)
    issuer: str | None = Field(default=None, min_length=1)
    jwks_url: str | None = Field(default=None, min_length=1)
    id: UUID | None = None
    version: int | None = Field(default=None, ge=0)
    error: str | None = None


class DiscoverySyncEnvelope(_ClosedModel):
    data: DiscoveryRegistryWritePosture


class TenantIdpBinding(_ClosedModel):
    id: UUID
    bound_tenant_id: UUID
    issuer: str = Field(min_length=1)
    status: str = Field(min_length=1)
    priority: int = Field(ge=0)
    version: int = Field(ge=0)


class TenantIdpBindingEnvelope(_ClosedModel):
    data: TenantIdpBinding


class TenantIdpBindingListEnvelope(_ClosedModel):
    data: list[TenantIdpBinding]
    meta: CountMeta


class FederationMatrixCell(_ClosedModel):
    bound_tenant_id: str | None = None
    issuer: str = Field(min_length=1)
    state: Literal["active", "disabled", "unbound"]
    binding_id: UUID | str | None = None
    priority: int | None = None
    registry_status: Literal["absent", "active", "disabled"]


class FederationMatrixPayload(_ClosedModel):
    cells: list[FederationMatrixCell]
    tenants: list[str]
    issuers: list[str]


class FederationMatrixMeta(_ClosedModel):
    cell_count: int = Field(ge=0)
    tenant_count: int = Field(ge=0)
    issuer_count: int = Field(ge=0)
    binding_count: int = Field(ge=0)
    active_count: int = Field(ge=0)
    include_unbound_issuers: bool


class FederationMatrixEnvelope(_ClosedModel):
    data: FederationMatrixPayload
    meta: FederationMatrixMeta


class UpsertDeclaredRoleRequest(_ClosedModel):
    name: str = Field(min_length=1, max_length=128)


class CreateIdpIssuerRequest(_ClosedModel):
    issuer: str = Field(min_length=1)
    jwks_url: str | None = None
    jwks_json: dict[str, Any] | str | None = None


class CreateTenantIdpBindingRequest(_ClosedModel):
    issuer: str = Field(min_length=1)


class SetBindingPriorityRequest(_ClosedModel):
    priority: int = Field(ge=0)

    @field_validator("priority", mode="before")
    @classmethod
    def _reject_bool(cls, value: object) -> object:
        # Before coercion: bool would become 0/1 under lax int parsing.
        if isinstance(value, bool):
            raise ValueError("priority must be an integer >= 0")
        return value
