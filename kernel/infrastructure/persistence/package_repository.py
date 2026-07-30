"""Tenant-bound SQLAlchemy adapter for Package Repository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from eaos_platform.package.models import (
    ActionDeclaration,
    DeclaredPermission,
    InstallationStatus,
    ManifestStatus,
    PackageInstallation,
    PackageManifest,
    PackageType,
    SurfaceDeclaration,
)
from kernel.infrastructure.persistence.package_models import (
    PackageInstallationRecord,
    PackageManifestRecord,
)
from kernel.shared.errors import ErrorCode, KernelError


class SQLAlchemyPackageRepository:
    def __init__(self, session: Session, *, tenant_id: UUID) -> None:
        self._session = session
        self._tenant_id = tenant_id

    def add_manifest(self, manifest: PackageManifest) -> None:
        self._require_tenant(manifest.tenant_id)
        self._session.add(
            PackageManifestRecord(
                id=manifest.id,
                tenant_id=manifest.tenant_id,
                package_key=manifest.package_key,
                version=manifest.version,
                package_type=manifest.package_type.value,
                status=manifest.status.value,
                surfaces_json=[
                    {
                        "surface_key": item.surface_key,
                        "title": item.title,
                        "description": item.description,
                    }
                    for item in manifest.surfaces
                ],
                actions_json=[
                    {
                        "action_key": item.action_key,
                        "resource_type": item.resource_type,
                        "permission_action": item.permission_action,
                        "high_impact": item.high_impact,
                        "surface_key": item.surface_key,
                        "description": item.description,
                    }
                    for item in manifest.actions
                ],
                required_permissions_json=[
                    {
                        "resource_type": item.resource_type,
                        "actions": sorted(item.actions),
                    }
                    for item in manifest.required_permissions
                ],
                declared_events_json=list(manifest.declared_events),
                created_at=manifest.created_at,
                updated_at=manifest.updated_at,
                version_number=manifest.version_number,
            )
        )

    def get_manifest(self, manifest_id: UUID) -> PackageManifest | None:
        record = self._session.scalar(
            select(PackageManifestRecord).where(
                PackageManifestRecord.id == manifest_id,
                PackageManifestRecord.tenant_id == self._tenant_id,
            )
        )
        return self._to_manifest(record) if record is not None else None

    def get_manifest_by_key_version(
        self,
        *,
        tenant_id: UUID,
        package_key: str,
        version: str,
    ) -> PackageManifest | None:
        self._require_tenant(tenant_id)
        record = self._session.scalar(
            select(PackageManifestRecord).where(
                PackageManifestRecord.tenant_id == tenant_id,
                func.lower(PackageManifestRecord.package_key) == package_key.casefold(),
                PackageManifestRecord.version == version,
            )
        )
        return self._to_manifest(record) if record is not None else None

    def save_manifest(
        self,
        manifest: PackageManifest,
        *,
        expected_version: int,
    ) -> None:
        self._require_tenant(manifest.tenant_id)
        result = self._session.execute(
            update(PackageManifestRecord)
            .where(
                PackageManifestRecord.id == manifest.id,
                PackageManifestRecord.tenant_id == manifest.tenant_id,
                PackageManifestRecord.version_number == expected_version,
            )
            .values(
                status=manifest.status.value,
                updated_at=manifest.updated_at,
                version_number=manifest.version_number,
            )
        )
        if result.rowcount != 1:
            raise KernelError(
                ErrorCode.PACKAGE_VERSION_CONFLICT,
                "package manifest version conflict",
            )

    def add_installation(self, installation: PackageInstallation) -> None:
        self._require_tenant(installation.tenant_id)
        self._session.add(
            PackageInstallationRecord(
                id=installation.id,
                tenant_id=installation.tenant_id,
                manifest_id=installation.manifest_id,
                package_key=installation.package_key,
                manifest_version=installation.manifest_version,
                status=installation.status.value,
                created_at=installation.created_at,
                updated_at=installation.updated_at,
                version_number=installation.version_number,
            )
        )

    def get_installation(self, installation_id: UUID) -> PackageInstallation | None:
        record = self._session.scalar(
            select(PackageInstallationRecord).where(
                PackageInstallationRecord.id == installation_id,
                PackageInstallationRecord.tenant_id == self._tenant_id,
            )
        )
        return self._to_installation(record) if record is not None else None

    def get_installation_by_package_key(
        self,
        *,
        tenant_id: UUID,
        package_key: str,
    ) -> PackageInstallation | None:
        self._require_tenant(tenant_id)
        record = self._session.scalar(
            select(PackageInstallationRecord).where(
                PackageInstallationRecord.tenant_id == tenant_id,
                func.lower(PackageInstallationRecord.package_key)
                == package_key.casefold(),
                PackageInstallationRecord.status == InstallationStatus.INSTALLED.value,
            )
        )
        return self._to_installation(record) if record is not None else None

    def save_installation(
        self,
        installation: PackageInstallation,
        *,
        expected_version: int,
    ) -> None:
        self._require_tenant(installation.tenant_id)
        result = self._session.execute(
            update(PackageInstallationRecord)
            .where(
                PackageInstallationRecord.id == installation.id,
                PackageInstallationRecord.tenant_id == installation.tenant_id,
                PackageInstallationRecord.version_number == expected_version,
            )
            .values(
                status=installation.status.value,
                updated_at=installation.updated_at,
                version_number=installation.version_number,
            )
        )
        if result.rowcount != 1:
            raise KernelError(
                ErrorCode.PACKAGE_VERSION_CONFLICT,
                "package installation version conflict",
            )

    def list_installations(self, *, tenant_id: UUID) -> list[PackageInstallation]:
        self._require_tenant(tenant_id)
        records = self._session.scalars(
            select(PackageInstallationRecord).where(
                PackageInstallationRecord.tenant_id == tenant_id,
            )
        ).all()
        return [self._to_installation(record) for record in records]

    def _require_tenant(self, tenant_id: UUID) -> None:
        if tenant_id != self._tenant_id:
            raise KernelError(ErrorCode.COMMON_INTERNAL, "tenant boundary violation")

    @staticmethod
    def _to_manifest(record: PackageManifestRecord) -> PackageManifest:
        return PackageManifest(
            id=record.id,
            tenant_id=record.tenant_id,
            package_key=record.package_key,
            version=record.version,
            package_type=PackageType(record.package_type),
            status=ManifestStatus(record.status),
            surfaces=[
                SurfaceDeclaration(
                    surface_key=str(item["surface_key"]),
                    title=str(item["title"]),
                    description=str(item.get("description", "")),
                )
                for item in record.surfaces_json
            ],
            actions=[
                ActionDeclaration(
                    action_key=str(item["action_key"]),
                    resource_type=str(item["resource_type"]),
                    permission_action=str(item["permission_action"]),
                    high_impact=bool(item.get("high_impact", False)),
                    surface_key=(
                        str(item["surface_key"])
                        if item.get("surface_key") is not None
                        else None
                    ),
                    description=str(item.get("description", "")),
                )
                for item in record.actions_json
            ],
            required_permissions=[
                DeclaredPermission(
                    resource_type=str(item["resource_type"]),
                    actions=frozenset(str(action) for action in item.get("actions", [])),
                )
                for item in record.required_permissions_json
            ],
            declared_events=[str(item) for item in record.declared_events_json],
            created_at=record.created_at,
            updated_at=record.updated_at,
            version_number=record.version_number,
        )

    @staticmethod
    def _to_installation(record: PackageInstallationRecord) -> PackageInstallation:
        return PackageInstallation(
            id=record.id,
            tenant_id=record.tenant_id,
            manifest_id=record.manifest_id,
            package_key=record.package_key,
            manifest_version=record.manifest_version,
            status=InstallationStatus(record.status),
            created_at=record.created_at,
            updated_at=record.updated_at,
            version_number=record.version_number,
        )
