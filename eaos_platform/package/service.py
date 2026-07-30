"""Package Platform service — PHX-B14 manifest / install / resolve."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from eaos_platform.package.models import (
    ActionDeclaration,
    DeclaredPermission,
    InstallationStatus,
    ManifestStatus,
    PackageInstallation,
    PackageManifest,
    PackageType,
    ResolvedAction,
    SurfaceDeclaration,
)
from eaos_platform.package.repository import (
    InMemoryPackageRepository,
    PackageRepository,
)
from kernel.permission.models import PermissionEffect, Resource
from kernel.permission.service import PermissionService
from kernel.shared.audit import AuditLog, InMemoryAuditLog
from kernel.shared.context import ExecutionContext, require_context
from kernel.shared.errors import ErrorCode, KernelError
from kernel.shared.results import KernelResult

_RESERVED_RESOURCE_TYPES = frozenset(
    {
        "subject",
        "tenant",
        "enterprise",
        "org_unit",
        "membership",
        "grant",
        "policy",
        "policy_rule",
        "permission_decision",
        "workflow_definition",
        "workflow_instance",
        "workflow_task",
        "event_stream",
        "knowledge_entity",
        "knowledge_link",
        "ai_run",
        "ai_memory",
        "tool",
        "terminal_session",
        "terminal_intent",
        "terminal_preview",
        "terminal_approval",
        "terminal_commit",
        "package_manifest",
        "package_installation",
        "package_surface",
        "package_action",
    }
)

_FORBIDDEN_KEY_PREFIXES = ("kernel.", "eaos.kernel.")


class PackageService:
    """Governed package catalog: manifests, tenant installs, contract resolve."""

    def __init__(
        self,
        permission_service: PermissionService,
        repository: PackageRepository | None = None,
        audit_log: AuditLog | None = None,
    ) -> None:
        self._permission = permission_service
        self._repo = repository or InMemoryPackageRepository()
        self._audit = audit_log or InMemoryAuditLog()

    @property
    def audit_log(self) -> AuditLog:
        return self._audit

    def register_manifest(
        self,
        ctx: ExecutionContext,
        *,
        package_key: str,
        version: str,
        package_type: str,
        surfaces: list[dict[str, str]] | None = None,
        actions: list[dict[str, object]] | None = None,
        required_permissions: list[dict[str, object]] | None = None,
        declared_events: list[str] | None = None,
    ) -> KernelResult[UUID]:
        try:
            require_context(ctx, tenant_data_plane=True)
            assert ctx.tenant_id is not None
            cleaned_key = package_key.strip()
            cleaned_version = version.strip()
            if not cleaned_key or not cleaned_version:
                raise KernelError(
                    ErrorCode.PACKAGE_MANIFEST_INVALID,
                    "package_key and version are required",
                )
            self._reject_kernel_fork_key(cleaned_key)
            try:
                ptype = PackageType(package_type.strip().casefold())
            except ValueError as exc:
                raise KernelError(
                    ErrorCode.PACKAGE_MANIFEST_INVALID,
                    "package_type is invalid",
                ) from exc

            surface_decls = self._parse_surfaces(surfaces or [])
            action_decls = self._parse_actions(actions or [], surfaces=surface_decls)
            perm_decls = self._parse_required_permissions(required_permissions or [])
            events = [item.strip() for item in (declared_events or []) if item.strip()]

            self._require_permission(
                ctx,
                action="register",
                resource=Resource(
                    tenant_id=ctx.tenant_id,
                    resource_type="package_manifest",
                ),
            )
            existing = self._repo.get_manifest_by_key_version(
                tenant_id=ctx.tenant_id,
                package_key=cleaned_key,
                version=cleaned_version,
            )
            if existing is not None:
                raise KernelError(
                    ErrorCode.PACKAGE_VERSION_CONFLICT,
                    "package_key and version already registered",
                )

            now = datetime.now(timezone.utc)
            manifest = PackageManifest(
                id=uuid4(),
                tenant_id=ctx.tenant_id,
                package_key=cleaned_key,
                version=cleaned_version,
                package_type=ptype,
                status=ManifestStatus.DRAFT,
                surfaces=surface_decls,
                actions=action_decls,
                required_permissions=perm_decls,
                declared_events=events,
                created_at=now,
                updated_at=now,
            )
            self._repo.add_manifest(manifest)
            audit = self._audit.record(
                ctx,
                action="Package.RegisterManifest",
                resource=f"package_manifest:{manifest.id}",
                result="ok",
                details={
                    "package_key": cleaned_key,
                    "version": cleaned_version,
                    "package_type": ptype.value,
                },
            )
            return KernelResult.success(manifest.id, audit_id=audit.id)
        except KernelError as err:
            return self._package_denied(
                ctx,
                action="Package.RegisterManifest",
                resource=f"package_manifest:{package_key.strip() or 'register'}",
                err=err,
            )

    def publish_manifest(
        self,
        ctx: ExecutionContext,
        *,
        manifest_id: UUID,
    ) -> KernelResult[bool]:
        try:
            manifest = self._require_manifest(ctx, manifest_id, writable=True)
            self._require_permission(
                ctx,
                action="publish",
                resource=Resource(
                    tenant_id=manifest.tenant_id,
                    resource_type="package_manifest",
                    resource_id=manifest.id,
                ),
            )
            if not manifest.actions and not manifest.surfaces:
                raise KernelError(
                    ErrorCode.PACKAGE_MANIFEST_INVALID,
                    "published manifest requires at least one surface or action",
                )
            expected = manifest.version_number
            manifest.status = ManifestStatus.PUBLISHED
            manifest.updated_at = datetime.now(timezone.utc)
            manifest.version_number = expected + 1
            self._repo.save_manifest(manifest, expected_version=expected)
            audit = self._audit.record(
                ctx,
                action="Package.PublishManifest",
                resource=f"package_manifest:{manifest.id}",
                result="ok",
            )
            return KernelResult.success(True, audit_id=audit.id)
        except KernelError as err:
            return self._package_denied(
                ctx,
                action="Package.PublishManifest",
                resource=f"package_manifest:{manifest_id}",
                err=err,
            )

    def get_manifest(
        self,
        ctx: ExecutionContext,
        *,
        manifest_id: UUID,
    ) -> KernelResult[PackageManifest]:
        try:
            manifest = self._require_manifest(ctx, manifest_id)
            self._require_permission(
                ctx,
                action="read",
                resource=Resource(
                    tenant_id=manifest.tenant_id,
                    resource_type="package_manifest",
                    resource_id=manifest.id,
                ),
            )
            return KernelResult.success(manifest)
        except KernelError as err:
            return KernelResult.from_error(err)

    def install_package(
        self,
        ctx: ExecutionContext,
        *,
        manifest_id: UUID,
    ) -> KernelResult[UUID]:
        try:
            require_context(ctx, tenant_data_plane=True)
            assert ctx.tenant_id is not None
            manifest = self._require_manifest(ctx, manifest_id)
            if manifest.status != ManifestStatus.PUBLISHED:
                raise KernelError(
                    ErrorCode.PACKAGE_NOT_PUBLISHED,
                    "only published manifests can be installed",
                )
            self._require_permission(
                ctx,
                action="install",
                resource=Resource(
                    tenant_id=ctx.tenant_id,
                    resource_type="package_installation",
                ),
            )
            existing = self._repo.get_installation_by_package_key(
                tenant_id=ctx.tenant_id,
                package_key=manifest.package_key,
            )
            if existing is not None:
                raise KernelError(
                    ErrorCode.PACKAGE_ALREADY_INSTALLED,
                    "package is already installed for this tenant",
                )
            now = datetime.now(timezone.utc)
            installation = PackageInstallation(
                id=uuid4(),
                tenant_id=ctx.tenant_id,
                manifest_id=manifest.id,
                package_key=manifest.package_key,
                manifest_version=manifest.version,
                status=InstallationStatus.INSTALLED,
                created_at=now,
                updated_at=now,
            )
            self._repo.add_installation(installation)
            audit = self._audit.record(
                ctx,
                action="Package.Install",
                resource=f"package_installation:{installation.id}",
                result="ok",
                details={
                    "package_key": manifest.package_key,
                    "manifest_version": manifest.version,
                },
            )
            return KernelResult.success(installation.id, audit_id=audit.id)
        except KernelError as err:
            return self._package_denied(
                ctx,
                action="Package.Install",
                resource=f"package_installation:{manifest_id}",
                err=err,
            )

    def disable_installation(
        self,
        ctx: ExecutionContext,
        *,
        installation_id: UUID,
    ) -> KernelResult[bool]:
        try:
            installation = self._require_installation(ctx, installation_id, writable=True)
            self._require_permission(
                ctx,
                action="disable",
                resource=Resource(
                    tenant_id=installation.tenant_id,
                    resource_type="package_installation",
                    resource_id=installation.id,
                ),
            )
            expected = installation.version_number
            installation.status = InstallationStatus.DISABLED
            installation.updated_at = datetime.now(timezone.utc)
            installation.version_number = expected + 1
            self._repo.save_installation(installation, expected_version=expected)
            audit = self._audit.record(
                ctx,
                action="Package.DisableInstallation",
                resource=f"package_installation:{installation.id}",
                result="ok",
            )
            return KernelResult.success(True, audit_id=audit.id)
        except KernelError as err:
            return self._package_denied(
                ctx,
                action="Package.DisableInstallation",
                resource=f"package_installation:{installation_id}",
                err=err,
            )

    def list_surfaces(
        self,
        ctx: ExecutionContext,
    ) -> KernelResult[list[SurfaceDeclaration]]:
        try:
            require_context(ctx, tenant_data_plane=True)
            assert ctx.tenant_id is not None
            self._require_permission(
                ctx,
                action="read",
                resource=Resource(
                    tenant_id=ctx.tenant_id,
                    resource_type="package_surface",
                ),
            )
            surfaces: list[SurfaceDeclaration] = []
            for installation in self._repo.list_installations(tenant_id=ctx.tenant_id):
                if installation.status != InstallationStatus.INSTALLED:
                    continue
                manifest = self._repo.get_manifest(installation.manifest_id)
                if manifest is None or manifest.tenant_id != ctx.tenant_id:
                    continue
                surfaces.extend(manifest.surfaces)
            return KernelResult.success(surfaces)
        except KernelError as err:
            return KernelResult.from_error(err)

    def resolve_action(
        self,
        ctx: ExecutionContext,
        *,
        action_key: str,
    ) -> KernelResult[ResolvedAction]:
        cleaned = action_key.strip()
        try:
            require_context(ctx, tenant_data_plane=True)
            assert ctx.tenant_id is not None
            if not cleaned:
                raise KernelError(
                    ErrorCode.PACKAGE_ACTION_UNDECLARED,
                    "action_key is required",
                )
            self._require_permission(
                ctx,
                action="resolve",
                resource=Resource(
                    tenant_id=ctx.tenant_id,
                    resource_type="package_action",
                ),
            )
            matches: list[tuple[PackageInstallation, PackageManifest, ActionDeclaration]] = []
            for installation in self._repo.list_installations(tenant_id=ctx.tenant_id):
                if installation.status != InstallationStatus.INSTALLED:
                    continue
                manifest = self._repo.get_manifest(installation.manifest_id)
                if manifest is None or manifest.tenant_id != ctx.tenant_id:
                    continue
                for action in manifest.actions:
                    if action.action_key.casefold() != cleaned.casefold():
                        continue
                    matches.append((installation, manifest, action))
            if len(matches) > 1:
                raise KernelError(
                    ErrorCode.PACKAGE_ACTION_AMBIGUOUS,
                    "action_key is declared by multiple installed packages",
                    details={
                        "action_key": cleaned,
                        "package_keys": sorted(
                            {manifest.package_key for _, manifest, _ in matches}
                        ),
                        "installation_ids": [
                            str(installation.id) for installation, _, _ in matches
                        ],
                    },
                )
            if not matches:
                raise KernelError(
                    ErrorCode.PACKAGE_ACTION_UNDECLARED,
                    "action is not declared by any installed package",
                )
            installation, manifest, action = matches[0]
            self._require_permission(
                ctx,
                action=action.permission_action,
                resource=Resource(
                    tenant_id=ctx.tenant_id,
                    resource_type=action.resource_type,
                ),
            )
            resolved = ResolvedAction(
                package_key=manifest.package_key,
                manifest_version=manifest.version,
                action_key=action.action_key,
                resource_type=action.resource_type,
                permission_action=action.permission_action,
                high_impact=action.high_impact,
                surface_key=action.surface_key,
                installation_id=installation.id,
            )
            audit = self._audit.record(
                ctx,
                action="Package.ResolveAction",
                resource=f"package_action:{action.action_key}",
                result="ok",
                details={
                    "package_key": manifest.package_key,
                    "installation_id": str(installation.id),
                    "high_impact": action.high_impact,
                    "permission_action": action.permission_action,
                },
            )
            return KernelResult.success(resolved, audit_id=audit.id)
        except KernelError as err:
            return self._package_denied(
                ctx,
                action="Package.ResolveAction",
                resource=f"package_action:{cleaned or action_key}",
                err=err,
            )

    def _package_denied(
        self,
        ctx: ExecutionContext,
        *,
        action: str,
        resource: str,
        err: KernelError,
    ) -> KernelResult[Any]:
        """Audit fail-closed denial (parity with Terminal extension denials)."""

        self._audit.record(
            ctx,
            action=action,
            resource=resource,
            result="denied",
            details={
                "error_code": str(err.code),
                "error_message": err.message,
            },
        )
        return KernelResult.from_error(err)

    def _reject_kernel_fork_key(self, package_key: str) -> None:
        lowered = package_key.casefold()
        if any(lowered.startswith(prefix) for prefix in _FORBIDDEN_KEY_PREFIXES):
            raise KernelError(
                ErrorCode.PACKAGE_KERNEL_FORK_DENIED,
                "package_key must not claim kernel ownership",
            )

    def _parse_surfaces(
        self,
        surfaces: list[dict[str, str]],
    ) -> list[SurfaceDeclaration]:
        result: list[SurfaceDeclaration] = []
        seen: set[str] = set()
        for item in surfaces:
            key = str(item.get("surface_key", "")).strip()
            title = str(item.get("title", "")).strip()
            description = str(item.get("description", "")).strip()
            if not key or not title:
                raise KernelError(
                    ErrorCode.PACKAGE_MANIFEST_INVALID,
                    "surface_key and title are required",
                )
            if key.casefold() in seen:
                raise KernelError(
                    ErrorCode.PACKAGE_MANIFEST_INVALID,
                    f"duplicate surface_key: {key}",
                )
            seen.add(key.casefold())
            result.append(
                SurfaceDeclaration(
                    surface_key=key,
                    title=title,
                    description=description,
                )
            )
        return result

    def _parse_actions(
        self,
        actions: list[dict[str, object]],
        *,
        surfaces: list[SurfaceDeclaration],
    ) -> list[ActionDeclaration]:
        surface_keys = {item.surface_key.casefold() for item in surfaces}
        result: list[ActionDeclaration] = []
        seen: set[str] = set()
        for item in actions:
            action_key = str(item.get("action_key", "")).strip()
            resource_type = str(item.get("resource_type", "")).strip()
            permission_action = str(item.get("permission_action", "")).strip()
            description = str(item.get("description", "")).strip()
            high_impact = bool(item.get("high_impact", False))
            surface_key_raw = item.get("surface_key")
            surface_key = (
                str(surface_key_raw).strip() if surface_key_raw is not None else None
            )
            if not action_key or not resource_type or not permission_action:
                raise KernelError(
                    ErrorCode.PACKAGE_MANIFEST_INVALID,
                    "action_key, resource_type, and permission_action are required",
                )
            if action_key.casefold() in seen:
                raise KernelError(
                    ErrorCode.PACKAGE_MANIFEST_INVALID,
                    f"duplicate action_key: {action_key}",
                )
            seen.add(action_key.casefold())
            if not resource_type.casefold().startswith("pkg."):
                raise KernelError(
                    ErrorCode.PACKAGE_KERNEL_FORK_DENIED,
                    "package actions must use pkg.* resource_type",
                )
            if resource_type.casefold() in _RESERVED_RESOURCE_TYPES:
                raise KernelError(
                    ErrorCode.PACKAGE_KERNEL_FORK_DENIED,
                    "package actions cannot own reserved resource types",
                )
            if surface_key and surface_key.casefold() not in surface_keys:
                raise KernelError(
                    ErrorCode.PACKAGE_SURFACE_UNDECLARED,
                    f"action references undeclared surface: {surface_key}",
                )
            result.append(
                ActionDeclaration(
                    action_key=action_key,
                    resource_type=resource_type,
                    permission_action=permission_action,
                    high_impact=high_impact,
                    surface_key=surface_key or None,
                    description=description,
                )
            )
        return result

    def _parse_required_permissions(
        self,
        items: list[dict[str, object]],
    ) -> list[DeclaredPermission]:
        result: list[DeclaredPermission] = []
        for item in items:
            resource_type = str(item.get("resource_type", "")).strip()
            actions_raw = item.get("actions", [])
            if not resource_type or not isinstance(actions_raw, (list, set, frozenset)):
                raise KernelError(
                    ErrorCode.PACKAGE_MANIFEST_INVALID,
                    "required_permissions entries need resource_type and actions",
                )
            actions = frozenset(str(action).strip() for action in actions_raw if str(action).strip())
            if not actions:
                raise KernelError(
                    ErrorCode.PACKAGE_MANIFEST_INVALID,
                    "required_permissions actions must be non-empty",
                )
            if resource_type.casefold() in _RESERVED_RESOURCE_TYPES and not resource_type.casefold().startswith(
                "pkg."
            ):
                # Declaring *need* for platform resources is allowed (e.g. workflow start),
                # but owning reserved types as package resources is not — required_permissions
                # may reference platform types for dependency declaration only.
                pass
            result.append(
                DeclaredPermission(resource_type=resource_type, actions=actions)
            )
        return result

    def _require_manifest(
        self,
        ctx: ExecutionContext,
        manifest_id: UUID,
        *,
        writable: bool = False,
    ) -> PackageManifest:
        require_context(ctx, tenant_data_plane=True)
        manifest = self._repo.get_manifest(manifest_id)
        if manifest is None or manifest.tenant_id != ctx.tenant_id:
            raise KernelError(ErrorCode.PACKAGE_NOT_FOUND, "package manifest not found")
        if writable and manifest.status == ManifestStatus.DEPRECATED:
            raise KernelError(
                ErrorCode.PACKAGE_MANIFEST_INVALID,
                "deprecated manifest cannot be modified",
            )
        return manifest

    def _require_installation(
        self,
        ctx: ExecutionContext,
        installation_id: UUID,
        *,
        writable: bool = False,
    ) -> PackageInstallation:
        require_context(ctx, tenant_data_plane=True)
        installation = self._repo.get_installation(installation_id)
        if installation is None or installation.tenant_id != ctx.tenant_id:
            raise KernelError(
                ErrorCode.PACKAGE_NOT_INSTALLED,
                "package installation not found",
            )
        if writable and installation.status == InstallationStatus.DISABLED:
            raise KernelError(
                ErrorCode.PACKAGE_NOT_INSTALLED,
                "package installation is already disabled",
            )
        return installation

    def _require_permission(
        self,
        ctx: ExecutionContext,
        *,
        action: str,
        resource: Resource,
    ) -> None:
        result = self._permission.evaluate(
            ctx,
            principal_subject_id=ctx.subject_id,
            action=action,
            resource=resource,
        )
        if not result.ok:
            raise KernelError(
                result.error_code or ErrorCode.PERMISSION_DENIED,
                result.error_message or "permission evaluation failed",
            )
        if result.data is None or result.data.effect != PermissionEffect.ALLOW:
            raise KernelError(ErrorCode.PERMISSION_DENIED, "permission denied")
