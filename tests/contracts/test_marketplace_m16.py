"""PHX-M16 Marketplace technical foundation contracts."""

from __future__ import annotations

from uuid import UUID, uuid4

from eaos_platform.marketplace.models import ListingStatus
from eaos_platform.marketplace.service import MarketplaceService
from kernel.permission.service import PermissionService
from kernel.shared.context import ExecutionContext, SubjectType
from kernel.shared.errors import ErrorCode

ADMIN_ID = uuid4()
PUBLISHER_ID = uuid4()
REVIEWER_ID = uuid4()


class _AllowAll:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


def _ctx(tenant_id: UUID, subject_id: UUID) -> ExecutionContext:
    return ExecutionContext(
        subject_id=subject_id,
        subject_type=SubjectType.HUMAN,
        correlation_id=str(uuid4()),
        request_time=ExecutionContext.utc_now(),
        tenant_id=tenant_id,
    )


def _services() -> tuple[PermissionService, MarketplaceService]:
    permission = PermissionService(
        grant_administrators={ADMIN_ID},
        principal_eligibility=_AllowAll(),
    )
    return permission, MarketplaceService(permission)


def _grant_all(permission: PermissionService, tenant_id: UUID, subject_id: UUID) -> None:
    admin = _ctx(tenant_id, ADMIN_ID)
    assert permission.grant(
        admin,
        principal_subject_id=subject_id,
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
    assert permission.grant(
        admin,
        principal_subject_id=subject_id,
        resource_type="marketplace_acquisition",
        actions={"acquire", "read"},
    ).ok


def test_publish_requires_signature_and_approval() -> None:
    tenant_id = uuid4()
    permission, market = _services()
    _grant_all(permission, tenant_id, PUBLISHER_ID)
    _grant_all(permission, tenant_id, REVIEWER_ID)
    publisher = _ctx(tenant_id, PUBLISHER_ID)
    created = market.create_listing(
        publisher,
        package_key="noventi.sample.ops",
        package_version="1.0.0",
        required_permissions=["pkg.ops.brief:compose"],
        declared_events=["pkg.ops.brief.composed"],
        data_scope="tenant.ops",
    )
    assert created.data is not None
    no_sig = market.submit_for_review(publisher, listing_id=created.data)
    assert no_sig.error_code == ErrorCode.MARKETPLACE_SIGNATURE_REQUIRED
    assert market.attach_signature(
        publisher,
        listing_id=created.data,
        signature_ref="sig:ed25519:abc",
    ).ok
    assert market.submit_for_review(publisher, listing_id=created.data).ok
    unapproved = market.publish_listing(publisher, listing_id=created.data)
    assert unapproved.error_code == ErrorCode.MARKETPLACE_NOT_APPROVED
    assert market.review_listing(
        _ctx(tenant_id, REVIEWER_ID),
        listing_id=created.data,
        approve=True,
    ).ok
    assert market.publish_listing(publisher, listing_id=created.data).ok
    listing = market.get_listing(publisher, listing_id=created.data)
    assert listing.data is not None
    assert listing.data.status == ListingStatus.PUBLISHED


def test_acquire_and_revoke() -> None:
    tenant_id = uuid4()
    permission, market = _services()
    _grant_all(permission, tenant_id, PUBLISHER_ID)
    publisher = _ctx(tenant_id, PUBLISHER_ID)
    created = market.create_listing(
        publisher,
        package_key="noventi.market.demo",
        package_version="0.1.0",
        required_permissions=["pkg.demo:read"],
        declared_events=[],
        data_scope="tenant.demo",
    )
    assert created.data is not None
    assert market.attach_signature(
        publisher,
        listing_id=created.data,
        signature_ref="sig:demo",
    ).ok
    assert market.submit_for_review(publisher, listing_id=created.data).ok
    assert market.review_listing(publisher, listing_id=created.data, approve=True).ok
    assert market.publish_listing(publisher, listing_id=created.data).ok
    acquired = market.acquire_listing(publisher, listing_id=created.data)
    assert acquired.ok and acquired.data is not None
    assert market.revoke_listing(publisher, listing_id=created.data).ok
    blocked = market.acquire_listing(publisher, listing_id=created.data)
    assert blocked.error_code == ErrorCode.MARKETPLACE_REVOKED


def test_commercial_apis_foundation_policy() -> None:
    tenant_id = uuid4()
    permission, market = _services()
    _grant_all(permission, tenant_id, PUBLISHER_ID)
    publisher = _ctx(tenant_id, PUBLISHER_ID)
    created = market.create_listing(
        publisher,
        package_key="noventi.market.demo",
        package_version="0.2.0",
        required_permissions=["pkg.demo:read"],
        declared_events=[],
        data_scope="tenant.demo",
    )
    assert created.data is not None
    pricing = market.set_pricing(publisher, listing_id=created.data, price="9.99")
    assert pricing.ok
    invoice = market.create_invoice(publisher, listing_id=created.data)
    assert invoice.ok and invoice.data is not None
    dispute = market.open_dispute(
        publisher,
        listing_id=created.data,
        reason="refund",
    )
    assert dispute.ok and dispute.data is not None
    assert market.resolve_dispute(
        publisher,
        dispute_id=dispute.data,
        resolution="credited",
    ).ok
    share = market.set_revenue_share(
        publisher,
        listing_id=created.data,
        platform_share_bps=2000,
    )
    assert share.ok
    deferred = market.deny_unsupported_commercial(
        publisher,
        operation="capture_payment",
        listing_id=created.data,
    )
    assert deferred.error_code == ErrorCode.MARKETPLACE_COMMERCIAL_POLICY_REQUIRED


def test_capability_required() -> None:
    tenant_id = uuid4()
    permission, market = _services()
    _grant_all(permission, tenant_id, PUBLISHER_ID)
    denied = market.create_listing(
        _ctx(tenant_id, PUBLISHER_ID),
        package_key="noventi.empty",
        package_version="1.0.0",
        required_permissions=[],
        declared_events=[],
        data_scope="",
    )
    assert denied.error_code == ErrorCode.MARKETPLACE_CAPABILITY_REQUIRED
