"""PHX-G512 CRM collection-query and read-only Terminal UI contracts."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID, uuid4

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from api.gateway import create_app
from kernel.permission.models import ScopeLevel
from kernel.permission.service import PermissionService
from kernel.shared.audit import InMemoryAuditLog
from kernel.shared.context import ExecutionContext, SubjectType
from noventi.crm.models import Contact, ContactStatus, Customer, CustomerStatus
from noventi.crm.persistence import (
    ContactRecord,
    CustomerRecord,
    SQLAlchemyCRMRepository,
)
from noventi.crm.repository import InMemoryCRMRepository
from noventi.crm.service import CONTACT_RESOURCE, CUSTOMER_RESOURCE, CRMService

ROOT = Path(__file__).resolve().parents[2]
SUBJECT = uuid4()
TENANT = uuid4()


class _AllowPrincipalEligibility:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


def _context() -> ExecutionContext:
    return ExecutionContext(
        subject_id=SUBJECT,
        subject_type=SubjectType.HUMAN,
        tenant_id=TENANT,
        correlation_id="corr-g512-grant",
        request_time=ExecutionContext.utc_now(),
    )


def _headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(SUBJECT),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": "corr-g512-http",
    }


def _client(*, grant: bool = True) -> TestClient:
    audit = InMemoryAuditLog()
    permission = PermissionService(
        audit_log=audit,
        grant_administrators={SUBJECT},
        principal_eligibility=_AllowPrincipalEligibility(),
    )
    if grant:
        for resource_type in (CUSTOMER_RESOURCE, CONTACT_RESOURCE):
            assert permission.grant(
                _context(),
                principal_subject_id=SUBJECT,
                resource_type=resource_type,
                actions={"create", "read", "update", "archive"},
                scope_level=ScopeLevel.TENANT,
            ).ok
    crm = CRMService(
        permission,
        repository=InMemoryCRMRepository(tenant_id=TENANT),
        audit_log=audit,
    )
    return TestClient(create_app(crm_service=crm, permission_service=permission))


def _create_customer(client: TestClient, code: str) -> dict:
    response = client.post(
        "/v1/crm/customers",
        headers=_headers(),
        json={"code": code, "display_name": f"Customer {code}"},
    )
    assert response.status_code == 201
    return response.json()["data"]


def test_g512_customer_list_is_bounded_cursor_paginated_and_active_only() -> None:
    client = _client()
    first = _create_customer(client, "C-512-A")
    second = _create_customer(client, "C-512-B")

    page_one = client.get(
        "/v1/crm/customers?limit=1",
        headers=_headers(),
    )
    assert page_one.status_code == 200
    page_one_data = page_one.json()["data"]
    assert len(page_one_data["items"]) == 1
    assert page_one_data["next_cursor"]

    page_two = client.get(
        "/v1/crm/customers",
        headers=_headers(),
        params={"limit": 1, "cursor": page_one_data["next_cursor"]},
    )
    assert page_two.status_code == 200
    assert len(page_two.json()["data"]["items"]) == 1
    assert {
        page_one_data["items"][0]["id"],
        page_two.json()["data"]["items"][0]["id"],
    } == {first["id"], second["id"]}

    archived = client.post(
        f"/v1/crm/customers/{first['id']}/archive",
        headers=_headers(),
        json={"reason": "G512 active-only check", "expected_version": 1},
    )
    assert archived.status_code == 200
    visible = client.get("/v1/crm/customers", headers=_headers()).json()["data"]["items"]
    assert [item["id"] for item in visible] == [second["id"]]


def test_g512_contact_list_minimizes_pii_and_detail_remains_governed() -> None:
    client = _client()
    customer = _create_customer(client, "C-512-PII")
    created = client.post(
        f"/v1/crm/customers/{customer['id']}/contacts",
        headers=_headers(),
        json={
            "display_name": "Ada Example",
            "title": "Operations",
            "email": "ada@example.test",
            "phone": "+1-555-0512",
        },
    )
    assert created.status_code == 201
    contact = created.json()["data"]

    listed = client.get(
        f"/v1/crm/customers/{customer['id']}/contacts",
        headers=_headers(),
    )
    assert listed.status_code == 200
    item = listed.json()["data"]["items"][0]
    assert item["id"] == contact["id"]
    assert item["title"] == "Operations"
    assert "email" not in item
    assert "phone" not in item
    assert "tenant_id" not in item

    detail = client.get(
        f"/v1/crm/customers/{customer['id']}/contacts/{contact['id']}",
        headers=_headers(),
    )
    assert detail.status_code == 200
    assert detail.json()["data"]["email"] == "ada@example.test"


def test_g512_lists_fail_closed_and_reject_invalid_pagination() -> None:
    denied = _client(grant=False).get("/v1/crm/customers", headers=_headers())
    assert denied.status_code == 403
    assert denied.json()["detail"]["code"] == "PERMISSION_DENIED"

    client = _client()
    assert client.get(
        "/v1/crm/customers?limit=101", headers=_headers()
    ).status_code == 422
    invalid_cursor = client.get(
        "/v1/crm/customers",
        headers=_headers(),
        params={"cursor": "not-a-valid-cursor"},
    )
    assert invalid_cursor.status_code == 400
    assert invalid_cursor.json()["detail"]["code"] == "COMMON_VALIDATION_FAILED"


def test_g512_openapi_closes_list_contracts_and_minimizes_contact_pii() -> None:
    spec = _client().get("/openapi.json").json()
    assert spec["paths"]["/v1/crm/customers"]["get"]
    assert spec["paths"]["/v1/crm/customers/{customer_id}/contacts"]["get"]
    schemas = spec["components"]["schemas"]
    for name in (
        "CustomerListItemView",
        "ContactListItemView",
        "CustomerListData",
        "ContactListData",
        "CustomerListEnvelope",
        "ContactListEnvelope",
    ):
        assert schemas[name]["additionalProperties"] is False
    contact_properties = schemas["ContactListItemView"]["properties"]
    assert "email" not in contact_properties
    assert "phone" not in contact_properties
    assert "tenant_id" not in contact_properties


def test_g512_sql_repository_lists_without_schema_change() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    with engine.begin() as connection:
        connection.exec_driver_sql("ATTACH DATABASE ':memory:' AS crm")
        CustomerRecord.__table__.create(connection)
        ContactRecord.__table__.create(connection)
    now = datetime.now(timezone.utc)
    customer_id = uuid4()
    contact_id = uuid4()
    with Session(engine) as session:
        repository = SQLAlchemyCRMRepository(session, tenant_id=TENANT)
        repository.add_customer(
            Customer(
                id=customer_id,
                tenant_id=TENANT,
                code="C-SQL-512",
                display_name="SQL Customer",
                owner_subject_id=None,
                status=CustomerStatus.ACTIVE,
                created_at=now,
                updated_at=now,
            )
        )
        repository.add_contact(
            Contact(
                id=contact_id,
                tenant_id=TENANT,
                customer_id=customer_id,
                display_name="SQL Contact",
                title="Reader",
                email="private@example.test",
                phone="+1-555-0000",
                status=ContactStatus.ACTIVE,
                created_at=now,
                updated_at=now,
            )
        )
        session.commit()

        assert [item.id for item in repository.list_customers(limit=10)] == [
            customer_id
        ]
        assert [
            item.id for item in repository.list_contacts(customer_id, limit=10)
        ] == [contact_id]


def test_g512_terminal_exposes_read_only_crm_states_and_routes() -> None:
    html = (ROOT / "smart_terminal" / "ui" / "index.html").read_text(encoding="utf-8")
    app = (ROOT / "smart_terminal" / "ui" / "app.js").read_text(encoding="utf-8")

    assert 'data-surface="crm"' in html
    assert 'data-surface-panel="crm"' in html
    for state in ("loading", "empty", "denied", "error"):
        assert state in app
    for symbol in (
        "crmCustomers",
        "crmContacts",
        "loadCrmCustomers",
        "loadCrmContacts",
        "selectCrmCustomer",
        "selectCrmContact",
    ):
        assert symbol in app
    for forbidden in ("btnCrmImport", "btnCrmMerge"):
        assert forbidden not in html

    served = _client().get("/terminal/")
    assert served.status_code == 200
    assert 'data-surface-panel="crm"' in served.text


def test_g512_closeout_preserves_release_and_production_boundaries() -> None:
    roadmap = (
        ROOT / "docs" / "project" / "POST_CRM_VERTICAL_ROADMAP.md"
    ).read_text(encoding="utf-8")
    acceptance = (
        ROOT / "docs" / "project" / "CRM_CUSTOMER_CONTACT_UI_G512_ACCEPTANCE.md"
    ).read_text(encoding="utf-8")
    manifest = (
        ROOT / "docs" / "release" / "RELEASE_MANIFEST.yaml"
    ).read_text(encoding="utf-8")

    assert "TRACK-G512 COMPLETE" in roadmap
    assert "FINAL STOP TRACK-G512" in roadmap
    assert "16 passed" in acceptance
    assert "Production Authorization:** None" in acceptance
    assert "PHX-G512" in manifest
    assert "crm_customer_contact_readonly_ui_and_list_queries" in manifest
