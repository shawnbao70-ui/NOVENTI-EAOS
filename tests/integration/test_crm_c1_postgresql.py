"""Destructive PostgreSQL acceptance for PHX-G294 CRM C1."""

from __future__ import annotations

from tests.contracts._baseline import EXPECTED_TIP
from tests.integration._db_reset import reset_eaos_test_database

import os
from collections.abc import Iterator
from decimal import Decimal
from uuid import UUID, uuid4

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import Engine, create_engine, inspect, text
from sqlalchemy.engine import make_url

from kernel.identity.models import SubjectKind
from kernel.infrastructure.persistence import (
    TransactionalIdentityService,
    TransactionalOrganizationService,
    TransactionalPermissionService,
)
from kernel.infrastructure.persistence.session import create_session_factory
from kernel.permission.models import ScopeLevel
from kernel.shared.context import ExecutionContext, SubjectType
from kernel.shared.errors import ErrorCode
from noventi.crm.persistence import TransactionalCRMService
from noventi.crm.approval import AllowConfirmApprovalGate, DenyConfirmApprovalGate
from noventi.crm.service import (
    AR_INVOICE_RESOURCE,
    CONTACT_RESOURCE,
    CONVERSION_RESOURCE,
    CUSTOMER_RESOURCE,
    DELIVERY_ORDER_RESOURCE,
    OPPORTUNITY_RESOURCE,
    POLICY_RESOURCE,
    QUOTE_RESOURCE,
    QUOTE_LINE_RESOURCE,
    REQUIREMENT_RESOURCE,
    SALES_ORDER_RESOURCE,
)

TEST_DATABASE_URL = os.getenv("EAOS_TEST_DATABASE_URL", "").strip()
if not TEST_DATABASE_URL:
    pytest.skip("EAOS_TEST_DATABASE_URL is not configured", allow_module_level=True)

pytestmark = pytest.mark.postgresql


def _validated_url() -> str:
    url = make_url(TEST_DATABASE_URL)
    if url.drivername != "postgresql+psycopg":
        raise RuntimeError("integration database must use postgresql+psycopg")
    if url.database is None or not url.database.startswith("eaos_test"):
        raise RuntimeError("integration database name must start with eaos_test")
    return TEST_DATABASE_URL


@pytest.fixture(scope="module")
def postgres_engine() -> Iterator[Engine]:
    previous_url = os.environ.get("EAOS_DATABASE_URL")
    os.environ["EAOS_DATABASE_URL"] = _validated_url()
    engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)
    config = Config("alembic.ini")
    try:
        with engine.begin() as connection:
            reset_eaos_test_database(connection)
        command.upgrade(config, "head")
        yield engine
    finally:
        with engine.begin() as connection:
            reset_eaos_test_database(connection)
        engine.dispose()
        if previous_url is None:
            os.environ.pop("EAOS_DATABASE_URL", None)
        else:
            os.environ["EAOS_DATABASE_URL"] = previous_url


def _platform_context() -> ExecutionContext:
    return ExecutionContext(
        subject_id=uuid4(),
        subject_type=SubjectType.SERVICE,
        tenant_id=None,
        platform_scope=True,
        correlation_id=f"crm-platform-{uuid4()}",
        request_time=ExecutionContext.utc_now(),
    )


def _tenant_context(tenant_id: UUID, subject_id: UUID | None = None) -> ExecutionContext:
    return ExecutionContext(
        subject_id=subject_id or uuid4(),
        subject_type=SubjectType.HUMAN,
        tenant_id=tenant_id,
        correlation_id=f"crm-tenant-{uuid4()}",
        request_time=ExecutionContext.utc_now(),
    )


def _tenant_actor(factory, name: str) -> tuple[UUID, ExecutionContext]:
    governor = _platform_context()
    organization = TransactionalOrganizationService(
        factory,
        platform_governors={governor.subject_id},
    )
    tenant = organization.create_tenant(governor, legal_name=name)
    assert tenant.ok and tenant.data is not None
    provisional = _tenant_context(tenant.data)
    identity = TransactionalIdentityService(factory)
    actor = identity.register_subject(
        provisional,
        subject_type=SubjectKind.HUMAN,
        display_name=f"{name} CRM Operator",
    )
    assert actor.ok and actor.data is not None
    return tenant.data, _tenant_context(tenant.data, actor.data)


def _grant_crm(factory, ctx: ExecutionContext) -> None:
    permission = TransactionalPermissionService(
        factory,
        grant_administrators={ctx.subject_id},
    )
    for resource_type in (
        CUSTOMER_RESOURCE,
        DELIVERY_ORDER_RESOURCE,
        AR_INVOICE_RESOURCE,
        CONTACT_RESOURCE,
        CONVERSION_RESOURCE,
        OPPORTUNITY_RESOURCE,
        POLICY_RESOURCE,
        QUOTE_RESOURCE,
        QUOTE_LINE_RESOURCE,
        REQUIREMENT_RESOURCE,
        SALES_ORDER_RESOURCE,
    ):
        granted = permission.grant(
            ctx,
            principal_subject_id=ctx.subject_id,
            resource_type=resource_type,
            actions={
                "create",
                "read",
                "update",
                "archive",
                "convert",
                "issue",
                "confirm",
                "release",
                "void",
            },
            scope_level=ScopeLevel.TENANT,
        )
        assert granted.ok


def test_g294_migration_creates_package_owned_schema(
    postgres_engine: Engine,
) -> None:
    inspector = inspect(postgres_engine)
    tables = set(inspector.get_table_names(schema="crm"))
    # Core C1 tables must exist; later RET/line tables may add members (PHX-G419).
    assert {
        "ar_invoices",
        "customers",
        "delivery_orders",
        "contacts",
        "opportunities",
        "quotes",
        "quote_conversions",
        "quote_lines",
        "requirements",
        "sales_orders",
        "sales_order_lines",
        "tenant_confirm_policies",
    } <= tables
    with postgres_engine.connect() as connection:
        assert (
            connection.scalar(text("SELECT version_num FROM alembic_version"))
            == EXPECTED_TIP
        )


def test_g294_customer_contact_round_trip_audit_and_no_cascade(
    postgres_engine: Engine,
) -> None:
    factory = create_session_factory(postgres_engine)
    _, ctx = _tenant_actor(factory, "CRM C1 Tenant")
    _grant_crm(factory, ctx)
    crm = TransactionalCRMService(factory)

    customer = crm.create_customer(
        ctx,
        code="CRM-001",
        display_name="C1 Customer",
        owner_subject_id=uuid4(),
    )
    assert customer.ok and customer.data is not None
    contact = crm.create_contact(
        ctx,
        customer_id=customer.data.id,
        display_name="Private Contact",
        email="private@example.test",
        phone="+1-555-0294",
    )
    assert contact.ok and contact.data is not None
    archived = crm.archive_customer(
        ctx,
        customer_id=customer.data.id,
        reason="C1 retention proof",
        expected_version=1,
    )
    assert archived.ok
    retained = crm.get_contact(
        ctx,
        customer_id=customer.data.id,
        contact_id=contact.data.id,
    )
    assert retained.ok

    with postgres_engine.connect() as connection:
        assert connection.scalar(text("SELECT count(*) FROM crm.contacts")) == 1
        audit_details = connection.scalar(
            text(
                """
                SELECT string_agg(details::text, ' ')
                FROM kernel.audit_events
                WHERE action LIKE 'CRM.%'
                """
            )
        )
    assert "private@example.test" not in (audit_details or "")
    assert "+1-555-0294" not in (audit_details or "")


def test_g294_owner_does_not_bypass_default_deny_and_tenants_are_isolated(
    postgres_engine: Engine,
) -> None:
    factory = create_session_factory(postgres_engine)
    _, denied_ctx = _tenant_actor(factory, "CRM Denied Tenant")
    crm = TransactionalCRMService(factory)
    denied = crm.create_customer(
        denied_ctx,
        code="DENIED-001",
        display_name="Owner Is Not Permission",
        owner_subject_id=denied_ctx.subject_id,
    )
    assert denied.error_code == ErrorCode.PERMISSION_DENIED

    _, tenant_a_ctx = _tenant_actor(factory, "CRM Tenant A")
    _grant_crm(factory, tenant_a_ctx)
    allowed = TransactionalCRMService(factory)
    tenant_a_customer = allowed.create_customer(
        tenant_a_ctx,
        code="TENANT-A-001",
        display_name="Tenant A Customer",
    )
    assert tenant_a_customer.ok and tenant_a_customer.data is not None

    _, tenant_b_ctx = _tenant_actor(factory, "CRM Tenant B")
    _grant_crm(factory, tenant_b_ctx)
    hidden = allowed.get_customer(
        tenant_b_ctx,
        customer_id=tenant_a_customer.data.id,
    )
    assert hidden.error_code == ErrorCode.COMMON_NOT_FOUND

    with postgres_engine.connect() as connection:
        assert (
            connection.scalar(
                text("SELECT count(*) FROM crm.customers WHERE code = 'DENIED-001'")
            )
            == 0
        )
        assert (
            connection.scalar(
                text(
                    """
                    SELECT count(*) FROM kernel.audit_events
                    WHERE action = 'CRM.Customer.Create' AND result = 'denied'
                    """
                )
            )
            >= 1
        )


def test_g295_opportunity_round_trip_customer_boundary_and_audit(
    postgres_engine: Engine,
) -> None:
    factory = create_session_factory(postgres_engine)
    _, tenant_a_ctx = _tenant_actor(factory, "CRM C2 Tenant A")
    _grant_crm(factory, tenant_a_ctx)
    crm = TransactionalCRMService(factory)
    customer = crm.create_customer(
        tenant_a_ctx,
        code="C2-PG-CUSTOMER",
        display_name="C2 PostgreSQL Customer",
    )
    assert customer.ok and customer.data is not None
    opportunity = crm.create_opportunity(
        tenant_a_ctx,
        customer_id=customer.data.id,
        title="Sensitive C2 pipeline title",
        owner_subject_id=uuid4(),
    )
    assert opportunity.ok and opportunity.data is not None
    assert opportunity.data.code.startswith("OPP-")
    updated = crm.update_opportunity(
        tenant_a_ctx,
        opportunity_id=opportunity.data.id,
        title="C2 updated title",
        owner_subject_id=None,
        expected_version=1,
    )
    assert updated.ok and updated.data is not None and updated.data.version == 2
    archived = crm.archive_opportunity(
        tenant_a_ctx,
        opportunity_id=opportunity.data.id,
        reason="C2 archive proof",
        expected_version=2,
    )
    assert archived.ok

    _, tenant_b_ctx = _tenant_actor(factory, "CRM C2 Tenant B")
    _grant_crm(factory, tenant_b_ctx)
    cross_tenant = crm.create_opportunity(
        tenant_b_ctx,
        customer_id=customer.data.id,
        title="Must not attach",
    )
    assert cross_tenant.error_code == ErrorCode.COMMON_NOT_FOUND

    with postgres_engine.connect() as connection:
        assert connection.scalar(text("SELECT count(*) FROM crm.opportunities")) == 1
        audit_details = connection.scalar(
            text(
                """
                SELECT string_agg(details::text, ' ')
                FROM kernel.audit_events
                WHERE action LIKE 'CRM.Opportunity.%'
                """
            )
        )
    assert "Sensitive C2 pipeline title" not in (audit_details or "")


def test_g296_requirement_round_trip_opportunity_boundary_and_audit(
    postgres_engine: Engine,
) -> None:
    factory = create_session_factory(postgres_engine)
    _, tenant_a_ctx = _tenant_actor(factory, "CRM C3 Tenant A")
    _grant_crm(factory, tenant_a_ctx)
    crm = TransactionalCRMService(factory)
    customer = crm.create_customer(
        tenant_a_ctx, code="C3-PG-CUSTOMER", display_name="C3 PostgreSQL Customer"
    )
    assert customer.data is not None
    opportunity = crm.create_opportunity(
        tenant_a_ctx,
        customer_id=customer.data.id,
        title="C3 PostgreSQL Opportunity",
    )
    assert opportunity.data is not None
    requirement = crm.create_requirement(
        tenant_a_ctx,
        opportunity_id=opportunity.data.id,
        title="Sensitive C3 requirement",
        description="Secret C3 application data",
    )
    assert requirement.ok and requirement.data is not None
    assert requirement.data.code.startswith("REQ-")
    updated = crm.update_requirement(
        tenant_a_ctx,
        requirement_id=requirement.data.id,
        title="C3 updated requirement",
        description=None,
        expected_version=1,
    )
    assert updated.ok and updated.data is not None and updated.data.version == 2
    archived = crm.archive_requirement(
        tenant_a_ctx,
        requirement_id=requirement.data.id,
        reason="C3 archive proof",
        expected_version=2,
    )
    assert archived.ok

    _, tenant_b_ctx = _tenant_actor(factory, "CRM C3 Tenant B")
    _grant_crm(factory, tenant_b_ctx)
    cross_tenant = crm.create_requirement(
        tenant_b_ctx,
        opportunity_id=opportunity.data.id,
        title="Must not attach",
    )
    assert cross_tenant.error_code == ErrorCode.COMMON_NOT_FOUND

    with postgres_engine.connect() as connection:
        assert connection.scalar(text("SELECT count(*) FROM crm.requirements")) == 1
        audit_details = connection.scalar(
            text(
                """
                SELECT string_agg(details::text, ' ')
                FROM kernel.audit_events
                WHERE action LIKE 'CRM.Requirement.%'
                """
            )
        )
    assert "Sensitive C3 requirement" not in (audit_details or "")
    assert "Secret C3 application data" not in (audit_details or "")


def test_g297_quote_round_trip_requirement_boundary_and_audit(
    postgres_engine: Engine,
) -> None:
    factory = create_session_factory(postgres_engine)
    _, tenant_a_ctx = _tenant_actor(factory, "CRM C4 Tenant A")
    _grant_crm(factory, tenant_a_ctx)
    crm = TransactionalCRMService(factory)
    customer = crm.create_customer(
        tenant_a_ctx, code="C4-PG-CUSTOMER", display_name="C4 PostgreSQL Customer"
    )
    assert customer.data is not None
    opportunity = crm.create_opportunity(
        tenant_a_ctx,
        customer_id=customer.data.id,
        title="C4 PostgreSQL Opportunity",
    )
    assert opportunity.data is not None
    requirement = crm.create_requirement(
        tenant_a_ctx,
        opportunity_id=opportunity.data.id,
        title="C4 PostgreSQL Requirement",
    )
    assert requirement.data is not None
    quote = crm.create_quote(
        tenant_a_ctx,
        requirement_id=requirement.data.id,
        currency="eur",
        notes="Sensitive C4 commercial notes",
    )
    assert quote.ok and quote.data is not None and quote.data.currency == "EUR"
    updated = crm.update_quote(
        tenant_a_ctx,
        quote_id=quote.data.id,
        currency="USD",
        notes=None,
        expected_version=1,
    )
    assert updated.ok and updated.data is not None and updated.data.version == 2
    archived = crm.archive_quote(
        tenant_a_ctx,
        quote_id=quote.data.id,
        reason="C4 archive proof",
        expected_version=2,
    )
    assert archived.ok

    _, tenant_b_ctx = _tenant_actor(factory, "CRM C4 Tenant B")
    _grant_crm(factory, tenant_b_ctx)
    cross_tenant = crm.create_quote(
        tenant_b_ctx,
        requirement_id=requirement.data.id,
    )
    assert cross_tenant.error_code == ErrorCode.COMMON_NOT_FOUND

    with postgres_engine.connect() as connection:
        assert connection.scalar(text("SELECT count(*) FROM crm.quotes")) == 1
        audit_details = connection.scalar(
            text(
                """
                SELECT string_agg(details::text, ' ')
                FROM kernel.audit_events
                WHERE action LIKE 'CRM.Quote.%'
                """
            )
        )
    assert "Sensitive C4 commercial notes" not in (audit_details or "")


def test_g298_convert_is_transactionally_unique_and_tenant_bound(
    postgres_engine: Engine,
) -> None:
    factory = create_session_factory(postgres_engine)
    _, ctx = _tenant_actor(factory, "CRM C5 Tenant")
    _grant_crm(factory, ctx)
    crm = TransactionalCRMService(factory)
    customer = crm.create_customer(
        ctx, code="C5-PG", display_name="C5 PostgreSQL Customer"
    ).data
    assert customer is not None
    opportunity = crm.create_opportunity(
        ctx, customer_id=customer.id, title="C5 PostgreSQL Opportunity"
    ).data
    assert opportunity is not None
    requirement = crm.create_requirement(
        ctx, opportunity_id=opportunity.id, title="C5 PostgreSQL Requirement"
    ).data
    assert requirement is not None
    quote = crm.create_quote(ctx, requirement_id=requirement.id).data
    assert quote is not None
    assert crm.create_quote_line(
        ctx,
        quote_id=quote.id,
        description="C13 commercial line",
        quantity=Decimal("1"),
        unit_price=Decimal("10.00"),
    ).ok
    assert crm.issue_quote(
        ctx,
        quote_id=quote.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    ).ok
    key = uuid4()
    first = crm.convert_quote(ctx, quote_id=quote.id, idempotency_key=key)
    retry = crm.convert_quote(ctx, quote_id=quote.id, idempotency_key=key)
    assert first.ok and first.data is not None
    assert retry.ok and retry.data is not None and retry.data.id == first.data.id

    _, other_ctx = _tenant_actor(factory, "CRM C5 Other Tenant")
    _grant_crm(factory, other_ctx)
    hidden = crm.convert_quote(
        other_ctx, quote_id=quote.id, idempotency_key=uuid4()
    )
    assert hidden.error_code == ErrorCode.COMMON_NOT_FOUND
    with postgres_engine.connect() as connection:
        assert connection.scalar(
            text("SELECT count(*) FROM crm.quote_conversions")
        ) == 1


def test_g299_sales_order_creation_consumes_conversion_atomically(
    postgres_engine: Engine,
) -> None:
    factory = create_session_factory(postgres_engine)
    _, ctx = _tenant_actor(factory, "CRM C6 Tenant")
    _grant_crm(factory, ctx)
    crm = TransactionalCRMService(factory)
    customer = crm.create_customer(
        ctx, code="C6-PG", display_name="C6 PostgreSQL Customer"
    ).data
    assert customer is not None
    opportunity = crm.create_opportunity(
        ctx, customer_id=customer.id, title="C6 PostgreSQL Opportunity"
    ).data
    assert opportunity is not None
    requirement = crm.create_requirement(
        ctx, opportunity_id=opportunity.id, title="C6 PostgreSQL Requirement"
    ).data
    assert requirement is not None
    quote = crm.create_quote(ctx, requirement_id=requirement.id).data
    assert quote is not None
    assert crm.create_quote_line(
        ctx,
        quote_id=quote.id,
        description="C13 commercial line",
        quantity=Decimal("1"),
        unit_price=Decimal("10.00"),
    ).ok
    assert crm.issue_quote(
        ctx,
        quote_id=quote.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    ).ok
    conversion = crm.convert_quote(
        ctx, quote_id=quote.id, idempotency_key=uuid4()
    ).data
    assert conversion is not None
    key = uuid4()
    created = crm.create_sales_order(
        ctx, conversion_id=conversion.id, idempotency_key=key
    )
    retry = crm.create_sales_order(
        ctx, conversion_id=conversion.id, idempotency_key=key
    )
    assert created.ok and created.data is not None
    assert retry.ok and retry.data is not None and retry.data.id == created.data.id
    consumed = crm.get_conversion(ctx, conversion_id=conversion.id)
    assert consumed.data is not None and consumed.data.status.value == "consumed"
    with postgres_engine.connect() as connection:
        assert connection.scalar(text("SELECT count(*) FROM crm.sales_orders")) == 1
        status_value = connection.scalar(
            text(
                "SELECT status FROM crm.quote_conversions WHERE id = :id"
            ),
            {"id": conversion.id},
        )
    assert status_value == "consumed"


def test_g300_quote_line_amount_and_conversion_invalidation(
    postgres_engine: Engine,
) -> None:
    factory = create_session_factory(postgres_engine)
    _, ctx = _tenant_actor(factory, "CRM C7 Tenant")
    _grant_crm(factory, ctx)
    crm = TransactionalCRMService(factory)
    customer = crm.create_customer(
        ctx, code="C7-PG", display_name="C7 PostgreSQL Customer"
    ).data
    assert customer is not None
    opportunity = crm.create_opportunity(
        ctx, customer_id=customer.id, title="C7 PostgreSQL Opportunity"
    ).data
    assert opportunity is not None
    requirement = crm.create_requirement(
        ctx, opportunity_id=opportunity.id, title="C7 PostgreSQL Requirement"
    ).data
    assert requirement is not None
    quote = crm.create_quote(ctx, requirement_id=requirement.id).data
    assert quote is not None
    line = crm.create_quote_line(
        ctx,
        quote_id=quote.id,
        description="C7 manual line",
        quantity=Decimal("2.500"),
        unit_price=Decimal("12.34"),
    ).data
    assert line is not None and line.amount == Decimal("30.85")
    assert crm.issue_quote(
        ctx,
        quote_id=quote.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    ).ok
    conversion = crm.convert_quote(
        ctx, quote_id=quote.id, idempotency_key=uuid4()
    ).data
    assert conversion is not None
    blocked = crm.update_quote_line(
        ctx,
        quote_id=quote.id,
        quote_line_id=line.id,
        description="C7 changed line",
        quantity=Decimal("3"),
        unit_price=Decimal("12.34"),
        expected_version=1,
    )
    assert blocked.error_code == ErrorCode.COMMON_CONFLICT
    assert blocked.error_message == "quote is issued"
    created = crm.create_sales_order(
        ctx, conversion_id=conversion.id, idempotency_key=uuid4()
    )
    assert created.ok and created.data is not None
    with postgres_engine.connect() as connection:
        amount = connection.scalar(
            text("SELECT amount FROM crm.quote_lines WHERE id = :id"),
            {"id": line.id},
        )
        status = connection.scalar(
            text("SELECT status FROM crm.quotes WHERE id = :id"),
            {"id": quote.id},
        )
    assert amount == Decimal("30.85")
    assert status == "issued"


def test_g301_sales_order_confirmation_freezes_lines_and_total(
    postgres_engine: Engine,
) -> None:
    factory = create_session_factory(postgres_engine)
    _, ctx = _tenant_actor(factory, "CRM C8 Tenant")
    _grant_crm(factory, ctx)
    crm = TransactionalCRMService(factory)
    customer = crm.create_customer(
        ctx, code="C8-PG", display_name="C8 PostgreSQL Customer"
    ).data
    assert customer is not None
    opportunity = crm.create_opportunity(
        ctx, customer_id=customer.id, title="C8 PostgreSQL Opportunity"
    ).data
    assert opportunity is not None
    requirement = crm.create_requirement(
        ctx, opportunity_id=opportunity.id, title="C8 PostgreSQL Requirement"
    ).data
    assert requirement is not None
    quote = crm.create_quote(ctx, requirement_id=requirement.id).data
    assert quote is not None
    line = crm.create_quote_line(
        ctx,
        quote_id=quote.id,
        description="C8 sensitive commercial line",
        quantity=Decimal("2"),
        unit_price=Decimal("15.25"),
    ).data
    assert line is not None
    assert crm.issue_quote(
        ctx,
        quote_id=quote.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    ).ok
    conversion = crm.convert_quote(
        ctx, quote_id=quote.id, idempotency_key=uuid4()
    ).data
    assert conversion is not None
    sales_order = crm.create_sales_order(
        ctx, conversion_id=conversion.id, idempotency_key=uuid4()
    ).data
    assert sales_order is not None
    key = uuid4()
    confirmed = crm.confirm_sales_order(
        ctx,
        sales_order_id=sales_order.id,
        idempotency_key=key,
        human_confirm=True,
    )
    retry = crm.confirm_sales_order(
        ctx,
        sales_order_id=sales_order.id,
        idempotency_key=key,
        human_confirm=True,
    )
    assert confirmed.ok and confirmed.data is not None
    assert confirmed.data.status.value == "confirmed"
    assert confirmed.data.total_amount == Decimal("30.50")
    assert retry.data is not None and retry.data.id == confirmed.data.id
    with postgres_engine.connect() as connection:
        line_count = connection.scalar(
            text(
                "SELECT count(*) FROM crm.sales_order_lines "
                "WHERE sales_order_id = :id"
            ),
            {"id": sales_order.id},
        )
        audit_details = connection.scalar(
            text(
                """
                SELECT string_agg(details::text, ' ')
                FROM kernel.audit_events
                WHERE action = 'CRM.SalesOrder.Confirm'
                """
            )
        )
    assert line_count == 1
    assert "C8 sensitive commercial line" not in (audit_details or "")
    assert "30.50" not in (audit_details or "")


def test_g302_g303_delivery_to_ar_invoice_trace_is_unique(
    postgres_engine: Engine,
) -> None:
    factory = create_session_factory(postgres_engine)
    _, ctx = _tenant_actor(factory, "CRM C9 Tenant")
    _grant_crm(factory, ctx)
    crm = TransactionalCRMService(factory)
    customer = crm.create_customer(
        ctx, code="C9-PG", display_name="C9 PostgreSQL Customer"
    ).data
    assert customer is not None
    opportunity = crm.create_opportunity(
        ctx, customer_id=customer.id, title="C9 PostgreSQL Opportunity"
    ).data
    assert opportunity is not None
    requirement = crm.create_requirement(
        ctx, opportunity_id=opportunity.id, title="C9 PostgreSQL Requirement"
    ).data
    assert requirement is not None
    quote = crm.create_quote(ctx, requirement_id=requirement.id).data
    assert quote is not None
    assert crm.create_quote_line(
        ctx,
        quote_id=quote.id,
        description="C9 delivery source",
        quantity=Decimal("2"),
        unit_price=Decimal("10"),
    ).ok
    assert crm.issue_quote(
        ctx,
        quote_id=quote.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    ).ok
    conversion = crm.convert_quote(
        ctx, quote_id=quote.id, idempotency_key=uuid4()
    ).data
    assert conversion is not None
    sales_order = crm.create_sales_order(
        ctx, conversion_id=conversion.id, idempotency_key=uuid4()
    ).data
    assert sales_order is not None
    confirmed = crm.confirm_sales_order(
        ctx,
        sales_order_id=sales_order.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    ).data
    assert confirmed is not None
    key = uuid4()
    created = crm.create_delivery_order(
        ctx, sales_order_id=confirmed.id, idempotency_key=key
    )
    retry = crm.create_delivery_order(
        ctx, sales_order_id=confirmed.id, idempotency_key=key
    )
    assert created.ok and created.data is not None
    assert retry.data is not None and retry.data.id == created.data.id
    _, other_ctx = _tenant_actor(factory, "CRM C9 Other Tenant")
    _grant_crm(factory, other_ctx)
    hidden = crm.create_delivery_order(
        other_ctx, sales_order_id=confirmed.id, idempotency_key=uuid4()
    )
    assert hidden.error_code == ErrorCode.COMMON_NOT_FOUND
    with postgres_engine.connect() as connection:
        count = connection.scalar(text("SELECT count(*) FROM crm.delivery_orders"))
    assert count == 1
    assert crm.release_delivery_order(
        ctx,
        delivery_order_id=created.data.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    ).ok
    invoice_key = uuid4()
    invoice = crm.create_ar_invoice(
        ctx,
        delivery_order_id=created.data.id,
        idempotency_key=invoice_key,
    )
    invoice_retry = crm.create_ar_invoice(
        ctx,
        delivery_order_id=created.data.id,
        idempotency_key=invoice_key,
    )
    assert invoice.ok and invoice.data is not None
    assert invoice_retry.data is not None
    assert invoice_retry.data.id == invoice.data.id
    assert invoice.data.sales_order_id == confirmed.id
    assert invoice.data.customer_id == customer.id
    assert invoice.data.total_amount == Decimal("20.00")
    hidden_invoice = crm.create_ar_invoice(
        other_ctx,
        delivery_order_id=created.data.id,
        idempotency_key=uuid4(),
    )
    assert hidden_invoice.error_code == ErrorCode.COMMON_NOT_FOUND
    with postgres_engine.connect() as connection:
        invoice_count = connection.scalar(
            text("SELECT count(*) FROM crm.ar_invoices")
        )
    assert invoice_count == 1


def test_g304_commercial_hold_blocks_confirm_until_cleared(
    postgres_engine: Engine,
) -> None:
    factory = create_session_factory(postgres_engine)
    _, ctx = _tenant_actor(factory, "CRM C11 Tenant")
    _grant_crm(factory, ctx)
    crm = TransactionalCRMService(factory)
    customer = crm.create_customer(
        ctx, code="C11-PG", display_name="C11 PostgreSQL Customer"
    ).data
    assert customer is not None
    assert customer.commercial_hold is False
    opportunity = crm.create_opportunity(
        ctx, customer_id=customer.id, title="C11 PostgreSQL Opportunity"
    ).data
    assert opportunity is not None
    requirement = crm.create_requirement(
        ctx, opportunity_id=opportunity.id, title="C11 PostgreSQL Requirement"
    ).data
    assert requirement is not None
    quote = crm.create_quote(ctx, requirement_id=requirement.id).data
    assert quote is not None
    assert crm.create_quote_line(
        ctx,
        quote_id=quote.id,
        description="C11 hold source",
        quantity=Decimal("2"),
        unit_price=Decimal("10"),
    ).ok
    assert crm.issue_quote(
        ctx,
        quote_id=quote.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    ).ok
    conversion = crm.convert_quote(
        ctx, quote_id=quote.id, idempotency_key=uuid4()
    ).data
    assert conversion is not None
    sales_order = crm.create_sales_order(
        ctx, conversion_id=conversion.id, idempotency_key=uuid4()
    ).data
    assert sales_order is not None
    held = crm.set_customer_commercial_hold(
        ctx,
        customer_id=customer.id,
        commercial_hold=True,
        expected_version=customer.version,
    ).data
    assert held is not None and held.commercial_hold is True
    blocked = crm.confirm_sales_order(
        ctx,
        sales_order_id=sales_order.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    )
    assert blocked.error_code == ErrorCode.COMMON_CONFLICT
    assert blocked.error_message == "customer is on commercial hold"
    cleared = crm.set_customer_commercial_hold(
        ctx,
        customer_id=held.id,
        commercial_hold=False,
        expected_version=held.version,
    ).data
    assert cleared is not None and cleared.commercial_hold is False
    confirmed = crm.confirm_sales_order(
        ctx,
        sales_order_id=sales_order.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    )
    assert confirmed.ok and confirmed.data is not None
    delivery = crm.create_delivery_order(
        ctx,
        sales_order_id=confirmed.data.id,
        idempotency_key=uuid4(),
    )
    assert delivery.ok and delivery.data is not None
    with postgres_engine.connect() as connection:
        hold_flag = connection.scalar(
            text(
                "SELECT commercial_hold FROM crm.customers WHERE id = :id"
            ),
            {"id": customer.id},
        )
    assert hold_flag is False


def test_g305_confirm_approval_policy_fail_closed_and_allow(
    postgres_engine: Engine,
) -> None:
    factory = create_session_factory(postgres_engine)
    _, ctx = _tenant_actor(factory, "CRM C12 Tenant")
    _grant_crm(factory, ctx)
    deny_crm = TransactionalCRMService(
        factory, confirm_approval_gate=DenyConfirmApprovalGate()
    )
    customer = deny_crm.create_customer(
        ctx, code="C12-PG", display_name="C12 PostgreSQL Customer"
    ).data
    assert customer is not None
    opportunity = deny_crm.create_opportunity(
        ctx, customer_id=customer.id, title="C12 PostgreSQL Opportunity"
    ).data
    assert opportunity is not None
    requirement = deny_crm.create_requirement(
        ctx, opportunity_id=opportunity.id, title="C12 PostgreSQL Requirement"
    ).data
    assert requirement is not None
    quote = deny_crm.create_quote(ctx, requirement_id=requirement.id).data
    assert quote is not None
    assert deny_crm.create_quote_line(
        ctx,
        quote_id=quote.id,
        description="C12 approval source",
        quantity=Decimal("2"),
        unit_price=Decimal("10"),
    ).ok
    assert deny_crm.issue_quote(
        ctx,
        quote_id=quote.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    ).ok
    conversion = deny_crm.convert_quote(
        ctx, quote_id=quote.id, idempotency_key=uuid4()
    ).data
    assert conversion is not None
    sales_order = deny_crm.create_sales_order(
        ctx, conversion_id=conversion.id, idempotency_key=uuid4()
    ).data
    assert sales_order is not None
    default_policy = deny_crm.get_confirm_approval_policy(ctx).data
    assert default_policy is not None
    assert default_policy.confirm_approval_required is False
    required = deny_crm.set_confirm_approval_policy(
        ctx, confirm_approval_required=True, expected_version=0
    ).data
    assert required is not None and required.confirm_approval_required is True
    blocked = deny_crm.confirm_sales_order(
        ctx,
        sales_order_id=sales_order.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    )
    assert blocked.error_code == ErrorCode.COMMON_CONFLICT
    assert blocked.error_message == "confirm approval is required"
    allow_crm = TransactionalCRMService(
        factory, confirm_approval_gate=AllowConfirmApprovalGate()
    )
    confirmed = allow_crm.confirm_sales_order(
        ctx,
        sales_order_id=sales_order.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    )
    assert confirmed.ok and confirmed.data is not None
    with postgres_engine.connect() as connection:
        flag = connection.scalar(
            text(
                """
                SELECT confirm_approval_required
                FROM crm.tenant_confirm_policies
                WHERE tenant_id = :tenant_id
                """
            ),
            {"tenant_id": ctx.tenant_id},
        )
    assert flag is True


def test_g306_quote_issue_is_idempotent_and_gates_convert(
    postgres_engine: Engine,
) -> None:
    factory = create_session_factory(postgres_engine)
    _, ctx = _tenant_actor(factory, "CRM C13 Tenant")
    _grant_crm(factory, ctx)
    crm = TransactionalCRMService(factory)
    customer = crm.create_customer(
        ctx, code="C13-PG", display_name="C13 PostgreSQL Customer"
    ).data
    assert customer is not None
    opportunity = crm.create_opportunity(
        ctx, customer_id=customer.id, title="C13 PostgreSQL Opportunity"
    ).data
    assert opportunity is not None
    requirement = crm.create_requirement(
        ctx, opportunity_id=opportunity.id, title="C13 PostgreSQL Requirement"
    ).data
    assert requirement is not None
    quote = crm.create_quote(ctx, requirement_id=requirement.id).data
    assert quote is not None
    draft_convert = crm.convert_quote(
        ctx, quote_id=quote.id, idempotency_key=uuid4()
    )
    assert draft_convert.error_code == ErrorCode.COMMON_CONFLICT
    assert crm.create_quote_line(
        ctx,
        quote_id=quote.id,
        description="C13 issued line",
        quantity=Decimal("2"),
        unit_price=Decimal("12.50"),
    ).ok
    key = uuid4()
    first = crm.issue_quote(
        ctx, quote_id=quote.id, idempotency_key=key, human_confirm=True
    )
    retry = crm.issue_quote(
        ctx, quote_id=quote.id, idempotency_key=key, human_confirm=True
    )
    assert first.ok and first.data is not None
    assert first.data.status.value == "issued"
    assert retry.ok and retry.data is not None and retry.data.id == first.data.id
    conflict = crm.issue_quote(
        ctx, quote_id=quote.id, idempotency_key=uuid4(), human_confirm=True
    )
    assert conflict.error_code == ErrorCode.COMMON_CONFLICT
    conversion = crm.convert_quote(
        ctx, quote_id=quote.id, idempotency_key=uuid4()
    )
    assert conversion.ok and conversion.data is not None
    with postgres_engine.connect() as connection:
        status = connection.scalar(
            text("SELECT status FROM crm.quotes WHERE id = :id"),
            {"id": quote.id},
        )
        assert status == "issued"
        assert (
            connection.scalar(text("SELECT version_num FROM alembic_version"))
            == EXPECTED_TIP
        )


def test_g307_delivery_order_release_gates_ar_invoice(
    postgres_engine: Engine,
) -> None:
    factory = create_session_factory(postgres_engine)
    _, ctx = _tenant_actor(factory, "CRM C14 Tenant")
    _grant_crm(factory, ctx)
    crm = TransactionalCRMService(factory)
    customer = crm.create_customer(
        ctx, code="C14-PG", display_name="C14 PostgreSQL Customer"
    ).data
    assert customer is not None
    opportunity = crm.create_opportunity(
        ctx, customer_id=customer.id, title="C14 PostgreSQL Opportunity"
    ).data
    assert opportunity is not None
    requirement = crm.create_requirement(
        ctx, opportunity_id=opportunity.id, title="C14 PostgreSQL Requirement"
    ).data
    assert requirement is not None
    quote = crm.create_quote(ctx, requirement_id=requirement.id).data
    assert quote is not None
    assert crm.create_quote_line(
        ctx,
        quote_id=quote.id,
        description="C14 release line",
        quantity=Decimal("1"),
        unit_price=Decimal("25.00"),
    ).ok
    assert crm.issue_quote(
        ctx,
        quote_id=quote.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    ).ok
    conversion = crm.convert_quote(
        ctx, quote_id=quote.id, idempotency_key=uuid4()
    ).data
    assert conversion is not None
    sales_order = crm.create_sales_order(
        ctx, conversion_id=conversion.id, idempotency_key=uuid4()
    ).data
    assert sales_order is not None
    sales_order = crm.confirm_sales_order(
        ctx,
        sales_order_id=sales_order.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    ).data
    assert sales_order is not None
    delivery_order = crm.create_delivery_order(
        ctx, sales_order_id=sales_order.id, idempotency_key=uuid4()
    ).data
    assert delivery_order is not None
    draft_invoice = crm.create_ar_invoice(
        ctx, delivery_order_id=delivery_order.id, idempotency_key=uuid4()
    )
    assert draft_invoice.error_code == ErrorCode.COMMON_CONFLICT
    key = uuid4()
    first = crm.release_delivery_order(
        ctx,
        delivery_order_id=delivery_order.id,
        idempotency_key=key,
        human_confirm=True,
    )
    retry = crm.release_delivery_order(
        ctx,
        delivery_order_id=delivery_order.id,
        idempotency_key=key,
        human_confirm=True,
    )
    assert first.ok and first.data is not None
    assert first.data.status.value == "released"
    assert retry.ok and retry.data is not None and retry.data.id == first.data.id
    invoice = crm.create_ar_invoice(
        ctx, delivery_order_id=delivery_order.id, idempotency_key=uuid4()
    )
    assert invoice.ok and invoice.data is not None
    with postgres_engine.connect() as connection:
        status = connection.scalar(
            text("SELECT status FROM crm.delivery_orders WHERE id = :id"),
            {"id": delivery_order.id},
        )
        assert status == "released"
        assert (
            connection.scalar(text("SELECT version_num FROM alembic_version"))
            == EXPECTED_TIP
        )


def test_g308_ar_invoice_issue_is_idempotent_and_tenant_head(
    postgres_engine: Engine,
) -> None:
    factory = create_session_factory(postgres_engine)
    _, ctx = _tenant_actor(factory, "CRM C15 Tenant")
    _grant_crm(factory, ctx)
    crm = TransactionalCRMService(factory)
    customer = crm.create_customer(
        ctx, code="C15-PG", display_name="C15 PostgreSQL Customer"
    ).data
    assert customer is not None
    opportunity = crm.create_opportunity(
        ctx, customer_id=customer.id, title="C15 PostgreSQL Opportunity"
    ).data
    assert opportunity is not None
    requirement = crm.create_requirement(
        ctx, opportunity_id=opportunity.id, title="C15 PostgreSQL Requirement"
    ).data
    assert requirement is not None
    quote = crm.create_quote(ctx, requirement_id=requirement.id).data
    assert quote is not None
    assert crm.create_quote_line(
        ctx,
        quote_id=quote.id,
        description="C15 issue line",
        quantity=Decimal("1"),
        unit_price=Decimal("40.00"),
    ).ok
    assert crm.issue_quote(
        ctx,
        quote_id=quote.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    ).ok
    conversion = crm.convert_quote(
        ctx, quote_id=quote.id, idempotency_key=uuid4()
    ).data
    assert conversion is not None
    sales_order = crm.create_sales_order(
        ctx, conversion_id=conversion.id, idempotency_key=uuid4()
    ).data
    assert sales_order is not None
    sales_order = crm.confirm_sales_order(
        ctx,
        sales_order_id=sales_order.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    ).data
    assert sales_order is not None
    delivery_order = crm.create_delivery_order(
        ctx, sales_order_id=sales_order.id, idempotency_key=uuid4()
    ).data
    assert delivery_order is not None
    assert crm.release_delivery_order(
        ctx,
        delivery_order_id=delivery_order.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    ).ok
    invoice = crm.create_ar_invoice(
        ctx, delivery_order_id=delivery_order.id, idempotency_key=uuid4()
    ).data
    assert invoice is not None and invoice.status.value == "draft"
    key = uuid4()
    first = crm.issue_ar_invoice(
        ctx, invoice_id=invoice.id, idempotency_key=key, human_confirm=True
    )
    retry = crm.issue_ar_invoice(
        ctx, invoice_id=invoice.id, idempotency_key=key, human_confirm=True
    )
    assert first.ok and first.data is not None
    assert first.data.status.value == "issued"
    assert retry.ok and retry.data is not None and retry.data.id == first.data.id
    conflict = crm.issue_ar_invoice(
        ctx, invoice_id=invoice.id, idempotency_key=uuid4(), human_confirm=True
    )
    assert conflict.error_code == ErrorCode.COMMON_CONFLICT
    with postgres_engine.connect() as connection:
        status = connection.scalar(
            text("SELECT status FROM crm.ar_invoices WHERE id = :id"),
            {"id": invoice.id},
        )
        assert status == "issued"
        assert (
            connection.scalar(text("SELECT version_num FROM alembic_version"))
            == EXPECTED_TIP
        )


def test_g309_ar_invoice_void_is_idempotent_and_blocks_reissue(
    postgres_engine: Engine,
) -> None:
    factory = create_session_factory(postgres_engine)
    _, ctx = _tenant_actor(factory, "CRM C16 Tenant")
    _grant_crm(factory, ctx)
    crm = TransactionalCRMService(factory)
    customer = crm.create_customer(
        ctx, code="C16-PG", display_name="C16 PostgreSQL Customer"
    ).data
    assert customer is not None
    opportunity = crm.create_opportunity(
        ctx, customer_id=customer.id, title="C16 PostgreSQL Opportunity"
    ).data
    assert opportunity is not None
    requirement = crm.create_requirement(
        ctx, opportunity_id=opportunity.id, title="C16 PostgreSQL Requirement"
    ).data
    assert requirement is not None
    quote = crm.create_quote(ctx, requirement_id=requirement.id).data
    assert quote is not None
    assert crm.create_quote_line(
        ctx,
        quote_id=quote.id,
        description="C16 void line",
        quantity=Decimal("1"),
        unit_price=Decimal("50.00"),
    ).ok
    assert crm.issue_quote(
        ctx,
        quote_id=quote.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    ).ok
    conversion = crm.convert_quote(
        ctx, quote_id=quote.id, idempotency_key=uuid4()
    ).data
    assert conversion is not None
    sales_order = crm.create_sales_order(
        ctx, conversion_id=conversion.id, idempotency_key=uuid4()
    ).data
    assert sales_order is not None
    sales_order = crm.confirm_sales_order(
        ctx,
        sales_order_id=sales_order.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    ).data
    assert sales_order is not None
    delivery_order = crm.create_delivery_order(
        ctx, sales_order_id=sales_order.id, idempotency_key=uuid4()
    ).data
    assert delivery_order is not None
    assert crm.release_delivery_order(
        ctx,
        delivery_order_id=delivery_order.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    ).ok
    invoice = crm.create_ar_invoice(
        ctx, delivery_order_id=delivery_order.id, idempotency_key=uuid4()
    ).data
    assert invoice is not None
    assert crm.issue_ar_invoice(
        ctx,
        invoice_id=invoice.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    ).ok
    key = uuid4()
    first = crm.void_ar_invoice(
        ctx,
        invoice_id=invoice.id,
        idempotency_key=key,
        human_confirm=True,
        reason="Operator retract",
    )
    retry = crm.void_ar_invoice(
        ctx,
        invoice_id=invoice.id,
        idempotency_key=key,
        human_confirm=True,
        reason="Operator retract",
    )
    assert first.ok and first.data is not None
    assert first.data.status.value == "voided"
    assert first.data.void_reason == "Operator retract"
    assert retry.ok and retry.data is not None and retry.data.id == first.data.id
    reissue = crm.issue_ar_invoice(
        ctx,
        invoice_id=invoice.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    )
    assert reissue.error_code == ErrorCode.COMMON_CONFLICT
    with postgres_engine.connect() as connection:
        status = connection.scalar(
            text("SELECT status FROM crm.ar_invoices WHERE id = :id"),
            {"id": invoice.id},
        )
        assert status == "voided"
        assert (
            connection.scalar(text("SELECT version_num FROM alembic_version"))
            == EXPECTED_TIP
        )
