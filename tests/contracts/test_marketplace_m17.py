"""PHX-M17 Marketplace Foundation commercial policy contracts."""

from __future__ import annotations

from uuid import UUID, uuid4

from eaos_platform.marketplace.service import MarketplaceService
from kernel.permission.service import PermissionService
from kernel.shared.context import ExecutionContext, SubjectType
from kernel.shared.errors import ErrorCode

ADMIN_ID = uuid4()
ACTOR = uuid4()


class _AllowAll:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


def _ctx(tenant_id: UUID, subject_id: UUID = ACTOR) -> ExecutionContext:
    return ExecutionContext(
        subject_id=subject_id,
        subject_type=SubjectType.HUMAN,
        correlation_id=str(uuid4()),
        request_time=ExecutionContext.utc_now(),
        tenant_id=tenant_id,
    )


def _market() -> tuple[PermissionService, MarketplaceService, UUID]:
    tenant_id = uuid4()
    permission = PermissionService(
        grant_administrators={ADMIN_ID},
        principal_eligibility=_AllowAll(),
    )
    admin = _ctx(tenant_id, ADMIN_ID)
    assert permission.grant(
        admin,
        principal_subject_id=ACTOR,
        resource_type="marketplace_listing",
        actions={
            "create",
            "submit",
            "review",
            "publish",
            "revoke",
            "read",
            "price",
            "invoice",
            "dispute",
            "revenue_share",
        },
    ).ok
    return permission, MarketplaceService(permission), tenant_id


def test_pricing_validation_and_invoice_requires_price() -> None:
    _, market, tenant_id = _market()
    ctx = _ctx(tenant_id)
    created = market.create_listing(
        ctx,
        package_key="noventi.commerce.demo",
        package_version="1.0.0",
        required_permissions=["pkg.demo:read"],
        declared_events=[],
        data_scope="tenant.demo",
    )
    assert created.data is not None
    bad = market.set_pricing(ctx, listing_id=created.data, price="-1")
    assert bad.error_code == ErrorCode.COMMON_VALIDATION_FAILED
    missing = market.create_invoice(ctx, listing_id=created.data)
    assert missing.error_code == ErrorCode.COMMON_VALIDATION_FAILED
    assert market.set_pricing(ctx, listing_id=created.data, price="10.50", currency="usd").ok
    invoice = market.create_invoice(ctx, listing_id=created.data)
    assert invoice.ok


def test_revenue_share_bounds() -> None:
    _, market, tenant_id = _market()
    ctx = _ctx(tenant_id)
    created = market.create_listing(
        ctx,
        package_key="noventi.commerce.share",
        package_version="1.0.0",
        required_permissions=["pkg.demo:read"],
        declared_events=[],
        data_scope="tenant.demo",
    )
    assert created.data is not None
    over = market.set_revenue_share(
        ctx,
        listing_id=created.data,
        platform_share_bps=5001,
    )
    assert over.error_code == ErrorCode.COMMON_VALIDATION_FAILED
    assert market.set_revenue_share(
        ctx,
        listing_id=created.data,
        share_ratio=0.2,
    ).ok
