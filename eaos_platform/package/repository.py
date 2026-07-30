"""In-memory repository for Package Platform."""

from __future__ import annotations

from copy import deepcopy
from typing import Protocol
from uuid import UUID

from eaos_platform.package.models import PackageInstallation, PackageManifest
from kernel.shared.errors import ErrorCode, KernelError


class PackageRepository(Protocol):
    def add_manifest(self, manifest: PackageManifest) -> None: ...

    def get_manifest(self, manifest_id: UUID) -> PackageManifest | None: ...

    def get_manifest_by_key_version(
        self,
        *,
        tenant_id: UUID,
        package_key: str,
        version: str,
    ) -> PackageManifest | None: ...

    def save_manifest(
        self,
        manifest: PackageManifest,
        *,
        expected_version: int,
    ) -> None: ...

    def add_installation(self, installation: PackageInstallation) -> None: ...

    def get_installation(self, installation_id: UUID) -> PackageInstallation | None: ...

    def get_installation_by_package_key(
        self,
        *,
        tenant_id: UUID,
        package_key: str,
    ) -> PackageInstallation | None: ...

    def save_installation(
        self,
        installation: PackageInstallation,
        *,
        expected_version: int,
    ) -> None: ...

    def list_installations(
        self,
        *,
        tenant_id: UUID,
    ) -> list[PackageInstallation]: ...


class InMemoryPackageRepository:
    def __init__(self) -> None:
        self._manifests: dict[UUID, PackageManifest] = {}
        self._installations: dict[UUID, PackageInstallation] = {}

    def add_manifest(self, manifest: PackageManifest) -> None:
        self._manifests[manifest.id] = deepcopy(manifest)

    def get_manifest(self, manifest_id: UUID) -> PackageManifest | None:
        item = self._manifests.get(manifest_id)
        return deepcopy(item) if item is not None else None

    def get_manifest_by_key_version(
        self,
        *,
        tenant_id: UUID,
        package_key: str,
        version: str,
    ) -> PackageManifest | None:
        for item in self._manifests.values():
            if (
                item.tenant_id == tenant_id
                and item.package_key.casefold() == package_key.casefold()
                and item.version == version
            ):
                return deepcopy(item)
        return None

    def save_manifest(
        self,
        manifest: PackageManifest,
        *,
        expected_version: int,
    ) -> None:
        current = self._manifests.get(manifest.id)
        if current is None or current.version_number != expected_version:
            raise KernelError(
                ErrorCode.PACKAGE_VERSION_CONFLICT,
                "package manifest version conflict",
            )
        self._manifests[manifest.id] = deepcopy(manifest)

    def add_installation(self, installation: PackageInstallation) -> None:
        self._installations[installation.id] = deepcopy(installation)

    def get_installation(self, installation_id: UUID) -> PackageInstallation | None:
        item = self._installations.get(installation_id)
        return deepcopy(item) if item is not None else None

    def get_installation_by_package_key(
        self,
        *,
        tenant_id: UUID,
        package_key: str,
    ) -> PackageInstallation | None:
        for item in self._installations.values():
            if (
                item.tenant_id == tenant_id
                and item.package_key.casefold() == package_key.casefold()
                and item.status.value == "installed"
            ):
                return deepcopy(item)
        return None

    def save_installation(
        self,
        installation: PackageInstallation,
        *,
        expected_version: int,
    ) -> None:
        current = self._installations.get(installation.id)
        if current is None or current.version_number != expected_version:
            raise KernelError(
                ErrorCode.PACKAGE_VERSION_CONFLICT,
                "package installation version conflict",
            )
        self._installations[installation.id] = deepcopy(installation)

    def list_installations(self, *, tenant_id: UUID) -> list[PackageInstallation]:
        return [
            deepcopy(item)
            for item in self._installations.values()
            if item.tenant_id == tenant_id
        ]
