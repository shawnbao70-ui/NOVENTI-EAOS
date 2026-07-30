"""Transactional Marketplace contracts."""

from __future__ import annotations

from uuid import UUID, uuid4

from sqlalchemy import Engine, create_engine, select
from sqlalchemy.pool import StaticPool

from kernel.identity.models import SubjectKind
from kernel.infrastructure.persistence import (
    MarketplaceAcquisitionRecord,
    MarketplaceListingRecord,
    TransactionalIdentityService,
    TransactionalMarketplaceService,
    TransactionalOrganizationService,
    TransactionalPermissionService,
    create_session_factory,
    metadata,
)
from kernel.shared.context import ExecutionContext, SubjectType
from kernel.shared.errors import ErrorCode


def _engine() -> Engine:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        poolclass=StaticPool,
    )
    with engine.begin() as connection:
        connection.exec_driver_sql("ATTACH DATABASE ':memory:' AS kernel")
        metadata.create_all(connection)
    return engine


def _context(
    tenant_id=None,
    *,
    subject_id=None,
    subject_type=SubjectType.SERVICE,
    platform=False,
) -> ExecutionContext:
    return ExecutionContext(
        subject_id=subject_id or uuid4(),
        subject_type=subject_type,
        tenant_id=None if platform else (tenant_id or uuid4()),
        platform_scope=platform,
        correlation_id=str(uuid4()),
        request_time=ExecutionContext.utc_now(),
    )


def _foundation(engine: Engine) -> tuple[UUID, ExecutionContext]:
    governor = _context(platform=True)
    organization = TransactionalOrganizationService(
        create_session_factory(engine),
        platform_governors={governor.subject_id},
    )
    tenant = organization.create_tenant(governor, legal_name=str(uuid4()))
    assert tenant.data is not None
    identity = TransactionalIdentityService(
        create_session_factory(engine),
        platform_governors={governor.subject_id},
    )
    assert identity.grant_platform_governor(
        governor,
        subject_id=governor.subject_id,
    ).ok
    initial = _context(tenant.data)
    admin = identity.register_subject(
        initial,
        subject_type=SubjectKind.HUMAN,
        display_name="Market Admin",
    )
    assert admin.data is not None
    return (
        tenant.data,
        _context(tenant.data, subject_id=admin.data, subject_type=SubjectType.HUMAN),
    )


def test_transactional_marketplace_lifecycle() -> None:
    engine = _engine()
    _tenant_id, admin = _foundation(engine)
    factory = create_session_factory(engine)
    permission = TransactionalPermissionService(
        factory,
        grant_administrators={admin.subject_id},
    )
    market = TransactionalMarketplaceService(factory)
    assert permission.grant(
        admin,
        principal_subject_id=admin.subject_id,
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
        principal_subject_id=admin.subject_id,
        resource_type="marketplace_acquisition",
        actions={"acquire", "read"},
    ).ok

    created = market.create_listing(
        admin,
        package_key="noventi.sample.ops",
        package_version="1.0.0",
        required_permissions=["pkg.ops.brief:compose"],
        declared_events=["pkg.ops.brief.composed"],
        data_scope="tenant.ops",
    )
    assert created.ok and created.data is not None
    assert market.attach_signature(
        admin,
        listing_id=created.data,
        signature_ref="sig:pg",
    ).ok
    assert market.submit_for_review(admin, listing_id=created.data).ok
    assert market.review_listing(admin, listing_id=created.data, approve=True).ok
    assert market.publish_listing(admin, listing_id=created.data).ok
    acquired = market.acquire_listing(admin, listing_id=created.data)
    assert acquired.ok and acquired.data is not None
    assert market.set_pricing(admin, listing_id=created.data, price="1").ok
    invoice = market.create_invoice(admin, listing_id=created.data)
    assert invoice.ok and invoice.data is not None

    with factory() as session:
        assert session.scalar(
            select(MarketplaceListingRecord).where(
                MarketplaceListingRecord.id == created.data
            )
        ) is not None
        assert session.scalar(
            select(MarketplaceAcquisitionRecord).where(
                MarketplaceAcquisitionRecord.id == acquired.data
            )
        ) is not None
