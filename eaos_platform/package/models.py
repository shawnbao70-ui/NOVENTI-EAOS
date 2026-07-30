"""Business Package Platform domain models (PHX-B14)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Optional
from uuid import UUID


class PackageType(StrEnum):
    INDUSTRY = "industry"
    BUSINESS = "business"
    AI = "ai"
    INTEGRATION = "integration"


class ManifestStatus(StrEnum):
    DRAFT = "draft"
    PUBLISHED = "published"
    DEPRECATED = "deprecated"


class InstallationStatus(StrEnum):
    INSTALLED = "installed"
    DISABLED = "disabled"


@dataclass(frozen=True, slots=True)
class DeclaredPermission:
    resource_type: str
    actions: frozenset[str]


@dataclass(frozen=True, slots=True)
class SurfaceDeclaration:
    surface_key: str
    title: str
    description: str = ""


@dataclass(frozen=True, slots=True)
class ActionDeclaration:
    action_key: str
    resource_type: str
    permission_action: str
    high_impact: bool = False
    surface_key: Optional[str] = None
    description: str = ""


@dataclass(slots=True)
class PackageManifest:
    id: UUID
    tenant_id: UUID
    package_key: str
    version: str
    package_type: PackageType
    status: ManifestStatus
    surfaces: list[SurfaceDeclaration]
    actions: list[ActionDeclaration]
    required_permissions: list[DeclaredPermission]
    declared_events: list[str]
    created_at: datetime
    updated_at: datetime
    version_number: int = 1


@dataclass(slots=True)
class PackageInstallation:
    id: UUID
    tenant_id: UUID
    manifest_id: UUID
    package_key: str
    manifest_version: str
    status: InstallationStatus
    created_at: datetime
    updated_at: datetime
    version_number: int = 1


@dataclass(frozen=True, slots=True)
class ResolvedAction:
    package_key: str
    manifest_version: str
    action_key: str
    resource_type: str
    permission_action: str
    high_impact: bool
    surface_key: Optional[str]
    installation_id: UUID
    source: str = "package_manifest"
