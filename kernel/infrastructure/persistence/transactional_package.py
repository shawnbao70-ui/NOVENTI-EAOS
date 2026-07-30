"""Transactional SQLAlchemy composition for Package Platform commands."""

from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar
from uuid import UUID

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from eaos_platform.package.models import (
    PackageManifest,
    ResolvedAction,
    SurfaceDeclaration,
)
from eaos_platform.package.service import PackageService
from kernel.infrastructure.persistence.audit_log import SQLAlchemyAuditLog
from kernel.infrastructure.persistence.identity_permission import (
    SQLAlchemyPrincipalEligibility,
)
from kernel.infrastructure.persistence.package_repository import (
    SQLAlchemyPackageRepository,
)
from kernel.infrastructure.persistence.permission_repository import (
    SQLAlchemyPermissionRepository,
)
from kernel.infrastructure.persistence.unit_of_work import SQLAlchemyUnitOfWork
from kernel.permission.service import PermissionService
from kernel.shared.context import ExecutionContext
from kernel.shared.errors import ErrorCode
from kernel.shared.results import KernelResult

T = TypeVar("T")


class TransactionalPackageService:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

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
        return self._execute(
            ctx,
            lambda service: service.register_manifest(
                ctx,
                package_key=package_key,
                version=version,
                package_type=package_type,
                surfaces=surfaces,
                actions=actions,
                required_permissions=required_permissions,
                declared_events=declared_events,
            ),
            conflict_code=ErrorCode.PACKAGE_VERSION_CONFLICT,
        )

    def publish_manifest(
        self,
        ctx: ExecutionContext,
        *,
        manifest_id: UUID,
    ) -> KernelResult[bool]:
        return self._execute(
            ctx,
            lambda service: service.publish_manifest(ctx, manifest_id=manifest_id),
        )

    def get_manifest(
        self,
        ctx: ExecutionContext,
        *,
        manifest_id: UUID,
    ) -> KernelResult[PackageManifest]:
        return self._execute(
            ctx,
            lambda service: service.get_manifest(ctx, manifest_id=manifest_id),
        )

    def install_package(
        self,
        ctx: ExecutionContext,
        *,
        manifest_id: UUID,
    ) -> KernelResult[UUID]:
        return self._execute(
            ctx,
            lambda service: service.install_package(ctx, manifest_id=manifest_id),
        )

    def disable_installation(
        self,
        ctx: ExecutionContext,
        *,
        installation_id: UUID,
    ) -> KernelResult[bool]:
        return self._execute(
            ctx,
            lambda service: service.disable_installation(
                ctx,
                installation_id=installation_id,
            ),
        )

    def list_surfaces(
        self,
        ctx: ExecutionContext,
    ) -> KernelResult[list[SurfaceDeclaration]]:
        return self._execute(ctx, lambda service: service.list_surfaces(ctx))

    def resolve_action(
        self,
        ctx: ExecutionContext,
        *,
        action_key: str,
    ) -> KernelResult[ResolvedAction]:
        return self._execute(
            ctx,
            lambda service: service.resolve_action(ctx, action_key=action_key),
        )

    def _execute(
        self,
        ctx: ExecutionContext,
        operation: Callable[[PackageService], KernelResult[T]],
        *,
        conflict_code: ErrorCode = ErrorCode.COMMON_CONFLICT,
    ) -> KernelResult[T]:
        if ctx.tenant_id is None or ctx.platform_scope:
            return KernelResult.failure(
                ErrorCode.CTX_INVALID,
                "Package Platform requires tenant data-plane context",
            )
        try:
            with SQLAlchemyUnitOfWork(self._session_factory) as unit_of_work:
                audit_log = SQLAlchemyAuditLog(
                    unit_of_work.session,
                    tenant_id=ctx.tenant_id,
                )
                permission = PermissionService(
                    repository=SQLAlchemyPermissionRepository(
                        unit_of_work.session,
                        tenant_id=ctx.tenant_id,
                    ),
                    audit_log=audit_log,
                    principal_eligibility=SQLAlchemyPrincipalEligibility(
                        unit_of_work.session
                    ),
                )
                result = operation(
                    PackageService(
                        permission,
                        repository=SQLAlchemyPackageRepository(
                            unit_of_work.session,
                            tenant_id=ctx.tenant_id,
                        ),
                        audit_log=audit_log,
                    )
                )
                if not result.ok:
                    if result.error_code in {
                        ErrorCode.PERMISSION_DENIED,
                        ErrorCode.PACKAGE_KERNEL_FORK_DENIED,
                        ErrorCode.PACKAGE_MANIFEST_INVALID,
                        ErrorCode.PACKAGE_NOT_FOUND,
                        ErrorCode.PACKAGE_NOT_PUBLISHED,
                        ErrorCode.PACKAGE_NOT_INSTALLED,
                        ErrorCode.PACKAGE_ALREADY_INSTALLED,
                        ErrorCode.PACKAGE_ACTION_UNDECLARED,
                        ErrorCode.PACKAGE_SURFACE_UNDECLARED,
                        ErrorCode.PACKAGE_VERSION_CONFLICT,
                    }:
                        unit_of_work.commit()
                    return result
                unit_of_work.commit()
                return result
        except IntegrityError:
            return KernelResult.failure(
                conflict_code,
                "Package Platform persistence conflict",
            )
        except SQLAlchemyError:
            return KernelResult.failure(
                ErrorCode.COMMON_INTERNAL,
                "Package Platform persistence operation failed",
            )
