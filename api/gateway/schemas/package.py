"""Package request DTOs — runtime parity with docs/api/package.openapi.yaml."""

from __future__ import annotations

from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class _ClosedModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class PackageStatusData(_ClosedModel):
    """Package status with Terminal resolve alignment honesty (PHX-G398)."""

    writable: Literal[False] = False
    supported_surfaces: list[str] = Field(min_length=1)
    action_resolve_surface: Literal[True] = True
    surface_list_surface: Literal[True] = True
    terminal_resolve_aligned: Literal[True] = True
    terminal_holds_business_truth: Literal[False] = False


class PackageStatusEnvelope(_ClosedModel):
    data: PackageStatusData


class SurfaceDeclarationBody(_ClosedModel):
    surface_key: str = Field(min_length=1)
    title: str = Field(min_length=1)
    description: str = ""


class ActionDeclarationBody(_ClosedModel):
    action_key: str = Field(min_length=1)
    resource_type: str = Field(min_length=1)
    permission_action: str = Field(min_length=1)
    high_impact: bool = False
    surface_key: str | None = None
    description: str = ""


class DeclaredPermissionBody(_ClosedModel):
    resource_type: str = Field(min_length=1)
    actions: list[str] = Field(min_length=1)


class RegisterManifestRequest(_ClosedModel):
    package_key: str = Field(min_length=1)
    version: str = Field(min_length=1)
    package_type: Literal["industry", "business", "ai", "integration"]
    surfaces: list[SurfaceDeclarationBody] | None = None
    actions: list[ActionDeclarationBody] | None = None
    required_permissions: list[DeclaredPermissionBody] | None = None
    declared_events: list[str] | None = None

    def surfaces_as_dicts(self) -> list[dict[str, str]] | None:
        if self.surfaces is None:
            return None
        return [item.model_dump() for item in self.surfaces]

    def actions_as_dicts(self) -> list[dict[str, Any]] | None:
        if self.actions is None:
            return None
        return [item.model_dump() for item in self.actions]

    def permissions_as_dicts(self) -> list[dict[str, Any]] | None:
        if self.required_permissions is None:
            return None
        return [item.model_dump() for item in self.required_permissions]


class InstallPackageRequest(_ClosedModel):
    manifest_id: UUID


class ResolveActionRequest(_ClosedModel):
    action_key: str = Field(min_length=1)


class PackageSurfaceDeclaration(_ClosedModel):
    surface_key: str = Field(min_length=1)
    title: str = Field(min_length=1)
    description: str = ""


class PackageSurfacesEnvelope(_ClosedModel):
    data: list[PackageSurfaceDeclaration]


class ResolvedActionResponse(_ClosedModel):
    package_key: str = Field(min_length=1)
    manifest_version: str = Field(min_length=1)
    action_key: str = Field(min_length=1)
    resource_type: str = Field(min_length=1)
    permission_action: str = Field(min_length=1)
    high_impact: bool
    surface_key: str | None = None
    installation_id: UUID
    source: Literal["package_manifest"] = "package_manifest"


class PackageActionDeclaration(_ClosedModel):
    action_key: str = Field(min_length=1)
    resource_type: str = Field(min_length=1)
    permission_action: str = Field(min_length=1)
    high_impact: bool
    surface_key: str | None = None
    description: str = ""


class PackageDeclaredPermission(_ClosedModel):
    resource_type: str = Field(min_length=1)
    actions: list[str]


class PackageManifestResponse(_ClosedModel):
    id: UUID
    package_key: str = Field(min_length=1)
    version: str = Field(min_length=1)
    package_type: Literal["industry", "business", "ai", "integration"]
    status: Literal["draft", "published", "deprecated"]
    surfaces: list[PackageSurfaceDeclaration]
    actions: list[PackageActionDeclaration]
    required_permissions: list[PackageDeclaredPermission] = Field(default_factory=list)
    declared_events: list[str] = Field(default_factory=list)
