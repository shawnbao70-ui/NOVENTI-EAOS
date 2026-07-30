"""Organization request DTOs — runtime parity with docs/api/organization.openapi.yaml."""

from __future__ import annotations

from typing import Literal, Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class _ClosedModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class CreateTenantRequest(_ClosedModel):
    legal_name: str = Field(min_length=1, max_length=255)
    region_policy_ref: str | None = Field(default=None, max_length=255)


class CreateEnterpriseRequest(_ClosedModel):
    legal_name: str = Field(min_length=1, max_length=255)


class UpsertUnitRequest(_ClosedModel):
    unit_type: Literal["hq", "group", "branch", "department", "other"]
    name: str = Field(min_length=1, max_length=255)
    unit_id: UUID | None = None
    enterprise_id: UUID | None = None
    parent_unit_id: UUID | None = None
    status: Literal["active", "inactive"] = "active"
    expected_version: int | None = Field(default=None, ge=1)

    @model_validator(mode="after")
    def _require_version_on_update(self) -> Self:
        if self.unit_id is not None and self.expected_version is None:
            raise ValueError("expected_version is required when unit_id is set")
        return self


class SetUnitStatusRequest(_ClosedModel):
    status: Literal["active", "inactive", "closed"]
    reason: str = Field(min_length=1)
    expected_version: int = Field(ge=1)


class AddMembershipRequest(_ClosedModel):
    subject_id: UUID
    enterprise_id: UUID | None = None
    org_unit_id: UUID | None = None
    membership_role_label: str | None = Field(default=None, max_length=128)


class TransferMembershipUnitRequest(_ClosedModel):
    to_org_unit_id: UUID
    expected_version: int = Field(ge=1)


OrgLifecycleStatus = Literal["active", "suspended", "closed"]
UnitStatusLiteral = Literal["active", "inactive", "closed"]
MembershipStatusLiteral = Literal["active", "suspended", "ended"]
UnitTypeLiteral = Literal["hq", "group", "branch", "department", "other"]


class TenantResponse(_ClosedModel):
    id: UUID
    legal_name: str
    status: OrgLifecycleStatus
    region_policy_ref: str | None = None
    version: int = Field(ge=0)


class EnterpriseResponse(_ClosedModel):
    id: UUID
    tenant_id: UUID
    legal_name: str
    status: OrgLifecycleStatus
    is_primary: bool
    version: int = Field(ge=0)


class OrganizationUnitResponse(_ClosedModel):
    id: UUID
    tenant_id: UUID
    enterprise_id: UUID
    unit_type: UnitTypeLiteral
    name: str
    status: UnitStatusLiteral
    version: int = Field(ge=0)
    parent_unit_id: UUID | None = None


class MembershipResponse(_ClosedModel):
    id: UUID
    tenant_id: UUID
    enterprise_id: UUID
    subject_id: UUID
    status: MembershipStatusLiteral
    version: int = Field(ge=0)
    org_unit_id: UUID | None = None
    membership_role_label: str | None = None
    ended_at: str | None = None
