"""Transactional SQLAlchemy composition for Marketplace commands."""

from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar
from uuid import UUID

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from eaos_platform.marketplace.models import MarketplaceListing
from eaos_platform.marketplace.service import MarketplaceService
from kernel.infrastructure.persistence.audit_log import SQLAlchemyAuditLog
from kernel.infrastructure.persistence.identity_permission import (
    SQLAlchemyPrincipalEligibility,
)
from kernel.infrastructure.persistence.marketplace_repository import (
    SQLAlchemyMarketplaceRepository,
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


class TransactionalMarketplaceService:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def create_listing(
        self,
        ctx: ExecutionContext,
        *,
        package_key: str,
        package_version: str,
        required_permissions: list[str],
        declared_events: list[str],
        data_scope: str,
    ) -> KernelResult[UUID]:
        return self._execute(
            ctx,
            lambda service: service.create_listing(
                ctx,
                package_key=package_key,
                package_version=package_version,
                required_permissions=required_permissions,
                declared_events=declared_events,
                data_scope=data_scope,
            ),
        )

    def attach_signature(
        self,
        ctx: ExecutionContext,
        *,
        listing_id: UUID,
        signature_ref: str,
    ) -> KernelResult[bool]:
        return self._execute(
            ctx,
            lambda service: service.attach_signature(
                ctx,
                listing_id=listing_id,
                signature_ref=signature_ref,
            ),
        )

    def submit_for_review(
        self,
        ctx: ExecutionContext,
        *,
        listing_id: UUID,
    ) -> KernelResult[bool]:
        return self._execute(
            ctx,
            lambda service: service.submit_for_review(ctx, listing_id=listing_id),
        )

    def review_listing(
        self,
        ctx: ExecutionContext,
        *,
        listing_id: UUID,
        approve: bool,
        notes: str = "",
    ) -> KernelResult[bool]:
        return self._execute(
            ctx,
            lambda service: service.review_listing(
                ctx,
                listing_id=listing_id,
                approve=approve,
                notes=notes,
            ),
        )

    def publish_listing(
        self,
        ctx: ExecutionContext,
        *,
        listing_id: UUID,
    ) -> KernelResult[bool]:
        return self._execute(
            ctx,
            lambda service: service.publish_listing(ctx, listing_id=listing_id),
        )

    def revoke_listing(
        self,
        ctx: ExecutionContext,
        *,
        listing_id: UUID,
    ) -> KernelResult[bool]:
        return self._execute(
            ctx,
            lambda service: service.revoke_listing(ctx, listing_id=listing_id),
        )

    def get_listing(
        self,
        ctx: ExecutionContext,
        *,
        listing_id: UUID,
    ) -> KernelResult[MarketplaceListing]:
        return self._execute(
            ctx,
            lambda service: service.get_listing(ctx, listing_id=listing_id),
        )

    def acquire_listing(
        self,
        ctx: ExecutionContext,
        *,
        listing_id: UUID,
    ) -> KernelResult[UUID]:
        return self._execute(
            ctx,
            lambda service: service.acquire_listing(ctx, listing_id=listing_id),
        )

    def set_pricing(
        self,
        ctx: ExecutionContext,
        *,
        listing_id: UUID,
        price: str,
        currency: str | None = None,
    ) -> KernelResult[bool]:
        return self._execute(
            ctx,
            lambda service: service.set_pricing(
                ctx,
                listing_id=listing_id,
                price=price,
                currency=currency,
            ),
        )

    def create_invoice(
        self,
        ctx: ExecutionContext,
        *,
        listing_id: UUID,
    ) -> KernelResult[UUID]:
        return self._execute(
            ctx,
            lambda service: service.create_invoice(ctx, listing_id=listing_id),
        )

    def open_dispute(
        self,
        ctx: ExecutionContext,
        *,
        listing_id: UUID,
        reason: str,
    ) -> KernelResult[UUID]:
        return self._execute(
            ctx,
            lambda service: service.open_dispute(
                ctx,
                listing_id=listing_id,
                reason=reason,
            ),
        )

    def resolve_dispute(
        self,
        ctx: ExecutionContext,
        *,
        dispute_id: UUID,
        resolution: str,
    ) -> KernelResult[bool]:
        return self._execute(
            ctx,
            lambda service: service.resolve_dispute(
                ctx,
                dispute_id=dispute_id,
                resolution=resolution,
            ),
        )

    def set_revenue_share(
        self,
        ctx: ExecutionContext,
        *,
        listing_id: UUID,
        platform_share_bps: int | None = None,
        share_ratio: float | None = None,
    ) -> KernelResult[bool]:
        return self._execute(
            ctx,
            lambda service: service.set_revenue_share(
                ctx,
                listing_id=listing_id,
                platform_share_bps=platform_share_bps,
                share_ratio=share_ratio,
            ),
        )

    def _execute(
        self,
        ctx: ExecutionContext,
        operation: Callable[[MarketplaceService], KernelResult[T]],
    ) -> KernelResult[T]:
        if ctx.tenant_id is None or ctx.platform_scope:
            return KernelResult.failure(
                ErrorCode.CTX_INVALID,
                "Marketplace requires tenant data-plane context",
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
                    MarketplaceService(
                        permission,
                        repository=SQLAlchemyMarketplaceRepository(
                            unit_of_work.session,
                            tenant_id=ctx.tenant_id,
                        ),
                        audit_log=audit_log,
                    )
                )
                if not result.ok:
                    if result.error_code in {
                        ErrorCode.PERMISSION_DENIED,
                        ErrorCode.MARKETPLACE_NOT_FOUND,
                        ErrorCode.MARKETPLACE_SIGNATURE_REQUIRED,
                        ErrorCode.MARKETPLACE_SIGNATURE_INVALID,
                        ErrorCode.MARKETPLACE_SIGNING_UNCONFIGURED,
                        ErrorCode.MARKETPLACE_NOT_APPROVED,
                        ErrorCode.MARKETPLACE_NOT_PUBLISHED,
                        ErrorCode.MARKETPLACE_REVOKED,
                        ErrorCode.MARKETPLACE_CAPABILITY_REQUIRED,
                        ErrorCode.MARKETPLACE_ALREADY_ACQUIRED,
                        ErrorCode.MARKETPLACE_COMMERCIAL_POLICY_REQUIRED,
                        ErrorCode.PACKAGE_KERNEL_FORK_DENIED,
                        ErrorCode.COMMON_VALIDATION_FAILED,
                        ErrorCode.COMMON_CONFLICT,
                    }:
                        unit_of_work.commit()
                    return result
                unit_of_work.commit()
                return result
        except IntegrityError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT,
                "Marketplace persistence conflict",
            )
        except SQLAlchemyError:
            return KernelResult.failure(
                ErrorCode.COMMON_INTERNAL,
                "Marketplace persistence operation failed",
            )
