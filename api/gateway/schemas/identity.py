"""Identity request DTOs — runtime parity with docs/api/identity.openapi.yaml."""

from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class _ClosedModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ExternalRefBody(_ClosedModel):
    system: str = Field(min_length=1)
    external_id: str = Field(min_length=1)


class RegisterSubjectRequest(_ClosedModel):
    subject_type: Literal["human", "service", "device", "application", "plugin"]
    display_name: str = Field(min_length=1, max_length=255)
    external_refs: list[ExternalRefBody] | None = None


class BindCredentialRequest(_ClosedModel):
    subject_id: UUID
    credential_kind: str = Field(min_length=1, max_length=64)
    secret_handle: str = Field(min_length=1)
    expires_at: datetime | None = None


class ReasonRequest(_ClosedModel):
    reason: str = Field(min_length=1, max_length=1000)


class CreateSessionRequest(_ClosedModel):
    credential_id: UUID
    ttl_minutes: int = Field(default=60, ge=1, le=1440)


class GovernorGrantRequest(_ClosedModel):
    subject_id: UUID


class RegisterAIEmployeeRequest(_ClosedModel):
    display_name: str = Field(min_length=1, max_length=255)
    capabilities_profile: str = Field(min_length=1, max_length=255)
    owner_policy: str = Field(min_length=1, max_length=255)


class UpdateAIProfileRequest(_ClosedModel):
    expected_version: int = Field(ge=1)
    capabilities_profile: str = Field(min_length=1, max_length=255)
    owner_policy: str = Field(min_length=1, max_length=255)


class AssignAIRequest(_ClosedModel):
    management_policy: str = Field(default="tenant_managed", max_length=255)


class ReassignAIRequest(_ClosedModel):
    mode: Literal["reassign", "inherit", "archive"]
    to_tenant_id: UUID | None = None
    management_policy: str = Field(default="tenant_managed", max_length=255)


class SubjectResponse(_ClosedModel):
    id: UUID
    subject_type: str = Field(min_length=1)
    display_name: str
    status: Literal["active", "archived", "revoked", "ended"]
    version: int = Field(ge=1)


class CredentialValidationResponse(_ClosedModel):
    credential_id: UUID
    valid: Literal[True] = True
    status: Literal["active"] = "active"
    expires_at: str | None = None


class SessionCreatedResponse(_ClosedModel):
    session_id: UUID
    expires_at: str
    audit_id: UUID | str | None = None


class SessionValidationResponse(_ClosedModel):
    session_id: UUID
    valid: Literal[True] = True
    status: Literal["active"] = "active"
    expires_at: str


class AIEmployeeProfileResponse(_ClosedModel):
    ai_subject_id: UUID
    capabilities_profile_ref: str
    owner_policy_ref: str
    version: int = Field(ge=1)
