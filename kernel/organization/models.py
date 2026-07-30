"""Organization domain models (DM-KERNEL-001)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Optional
from uuid import UUID


class OrganizationStatus(StrEnum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CLOSED = "closed"
    INACTIVE = "inactive"
    ENDED = "ended"


class UnitType(StrEnum):
    HEADQUARTERS = "hq"
    GROUP = "group"
    BRANCH = "branch"
    DEPARTMENT = "department"
    OTHER = "other"


@dataclass(slots=True)
class Tenant:
    id: UUID
    legal_name: str
    status: OrganizationStatus
    created_at: datetime
    updated_at: datetime
    region_policy_ref: Optional[str] = None
    version: int = 1


@dataclass(slots=True)
class Enterprise:
    id: UUID
    tenant_id: UUID
    legal_name: str
    status: OrganizationStatus
    is_primary: bool
    created_at: datetime
    updated_at: datetime
    version: int = 1


@dataclass(slots=True)
class OrganizationUnit:
    id: UUID
    tenant_id: UUID
    enterprise_id: UUID
    unit_type: UnitType
    name: str
    status: OrganizationStatus
    created_at: datetime
    updated_at: datetime
    parent_unit_id: Optional[UUID] = None
    version: int = 1


@dataclass(slots=True)
class Membership:
    id: UUID
    tenant_id: UUID
    enterprise_id: UUID
    subject_id: UUID
    status: OrganizationStatus
    created_at: datetime
    updated_at: datetime
    org_unit_id: Optional[UUID] = None
    membership_role_label: Optional[str] = None
    ended_at: Optional[datetime] = None
    version: int = 1
