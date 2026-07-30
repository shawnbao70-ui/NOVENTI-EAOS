"""Destructive PostgreSQL acceptance for PHX-G312 Finance AR Credit Note N1."""

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
from noventi.crm.persistence import TransactionalCRMService
from noventi.crm.service import (
    AR_INVOICE_RESOURCE,
    CONTACT_RESOURCE,
    CONVERSION_RESOURCE,
    CUSTOMER_RESOURCE,
    DELIVERY_ORDER_RESOURCE,
    OPPORTUNITY_RESOURCE,
    POLICY_RESOURCE,
    QUOTE_LINE_RESOURCE,
    QUOTE_RESOURCE,
    REQUIREMENT_RESOURCE,
    SALES_ORDER_RESOURCE,
)
from noventi.finance.persistence import TransactionalFinanceService
from noventi.finance.service import AR_CREDIT_NOTE_RESOURCE, AR_RECEIPT_RESOURCE

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
        correlation_id=f"cn-platform-{uuid4()}",
        request_time=ExecutionContext.utc_now(),
    )


def _tenant_context(
    tenant_id: UUID, subject_id: UUID | None = None
) -> ExecutionContext:
    return ExecutionContext(
        subject_id=subject_id or uuid4(),
        subject_type=SubjectType.HUMAN,
        tenant_id=tenant_id,
        correlation_id=f"cn-tenant-{uuid4()}",
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
        display_name=f"{name} Finance Operator",
    )
    assert actor.ok and actor.data is not None
    return tenant.data, _tenant_context(tenant.data, actor.data)


def _grant_all(factory, ctx: ExecutionContext) -> None:
    permission = TransactionalPermissionService(
        factory,
        grant_administrators={ctx.subject_id},
    )
    for resource_type, actions in (
        (
            CUSTOMER_RESOURCE,
            {
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
        ),
        (CONTACT_RESOURCE, {"create", "read", "update", "archive"}),
        (OPPORTUNITY_RESOURCE, {"create", "read", "update", "archive"}),
        (REQUIREMENT_RESOURCE, {"create", "read", "update", "archive"}),
        (
            QUOTE_RESOURCE,
            {"create", "read", "update", "archive", "issue", "convert"},
        ),
        (QUOTE_LINE_RESOURCE, {"create", "read", "update", "archive"}),
        (CONVERSION_RESOURCE, {"create", "read", "convert"}),
        (SALES_ORDER_RESOURCE, {"create", "read", "confirm"}),
        (DELIVERY_ORDER_RESOURCE, {"create", "read", "release"}),
        (AR_INVOICE_RESOURCE, {"create", "read", "issue", "void"}),
        (POLICY_RESOURCE, {"read", "update"}),
        (AR_RECEIPT_RESOURCE, {"create", "read", "apply"}),
        (AR_CREDIT_NOTE_RESOURCE, {"create", "read", "issue"}),
    ):
        granted = permission.grant(
            ctx,
            principal_subject_id=ctx.subject_id,
            resource_type=resource_type,
            actions=actions,
            scope_level=ScopeLevel.TENANT,
        )
        assert granted.ok


def test_g312_migration_creates_credit_note_table(
    postgres_engine: Engine,
) -> None:
    inspector = inspect(postgres_engine)
    tables = set(inspector.get_table_names(schema="finance"))
    assert {"ar_credit_notes", "ar_receipts"} <= tables
    with postgres_engine.connect() as connection:
        assert (
            connection.scalar(text("SELECT version_num FROM alembic_version"))
            == EXPECTED_TIP
        )


def test_g312_credit_note_persists(
    postgres_engine: Engine,
) -> None:
    factory = create_session_factory()
    _, ctx = _tenant_actor(factory, "Finance N1 Tenant")
    _grant_all(factory, ctx)
    crm = TransactionalCRMService(factory)
    finance = TransactionalFinanceService(factory)

    customer = crm.create_customer(
        ctx, code=f"N1-{uuid4().hex[:8]}", display_name="N1 PG"
    ).data
    assert customer is not None
    opportunity = crm.create_opportunity(
        ctx, customer_id=customer.id, title="N1 Opp"
    ).data
    assert opportunity is not None
    requirement = crm.create_requirement(
        ctx, opportunity_id=opportunity.id, title="N1 Req"
    ).data
    assert requirement is not None
    quote = crm.create_quote(ctx, requirement_id=requirement.id).data
    assert quote is not None
    assert crm.create_quote_line(
        ctx,
        quote_id=quote.id,
        description="line",
        quantity=Decimal("2"),
        unit_price=Decimal("10"),
    ).ok
    assert crm.issue_quote(
        ctx, quote_id=quote.id, idempotency_key=uuid4(), human_confirm=True
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
    issued = crm.issue_ar_invoice(
        ctx,
        invoice_id=invoice.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    ).data
    assert issued is not None

    created = finance.create_credit_note(
        ctx,
        invoice_id=issued.id,
        amount=Decimal("5.00"),
        idempotency_key=uuid4(),
    )
    assert created.ok and created.data is not None
    issued_note = finance.issue_credit_note(
        ctx,
        credit_note_id=created.data.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    )
    assert issued_note.ok and issued_note.data is not None

    with postgres_engine.connect() as connection:
        row = connection.execute(
            text(
                "SELECT status, ar_invoice_id, amount "
                "FROM finance.ar_credit_notes WHERE id = :id"
            ),
            {"id": created.data.id},
        ).one()
        assert row.status == "issued"
        assert row.ar_invoice_id == issued.id
        assert row.amount == Decimal("5.00")
        assert (
            connection.scalar(text("SELECT version_num FROM alembic_version"))
            == EXPECTED_TIP
        )
