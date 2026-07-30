"""PHX-G514 CRM Opportunity list-query and managed Terminal UI contracts."""

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
from noventi.crm.models import Customer, CustomerStatus, Opportunity, OpportunityStatus
from noventi.crm.persistence import (
    CustomerRecord,
    OpportunityRecord,
    SQLAlchemyCRMRepository,
)
from noventi.crm.repository import InMemoryCRMRepository
from noventi.crm.service import CUSTOMER_RESOURCE, OPPORTUNITY_RESOURCE, CRMService

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
        correlation_id="corr-g514-grant",
        request_time=ExecutionContext.utc_now(),
    )


def _headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(SUBJECT),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": "corr-g514-http",
    }


def _client(*, grant: bool = True) -> TestClient:
    audit = InMemoryAuditLog()
    permission = PermissionService(
        audit_log=audit,
        grant_administrators={SUBJECT},
        principal_eligibility=_AllowPrincipalEligibility(),
    )
    if grant:
        for resource_type in (CUSTOMER_RESOURCE, OPPORTUNITY_RESOURCE):
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


def _create_customer(client: TestClient) -> dict:
    response = client.post(
        "/v1/crm/customers",
        headers=_headers(),
        json={"code": "C-G514", "display_name": "G514 Customer"},
    )
    assert response.status_code == 201
    return response.json()["data"]


def _create_opportunity(client: TestClient, customer_id: str, title: str) -> dict:
    response = client.post(
        "/v1/crm/opportunities",
        headers=_headers(),
        json={"customer_id": customer_id, "title": title},
    )
    assert response.status_code == 201
    return response.json()["data"]


def test_g514_opportunity_list_is_bounded_paginated_and_active_only() -> None:
    client = _client()
    customer = _create_customer(client)
    first = _create_opportunity(client, customer["id"], "First")
    second = _create_opportunity(client, customer["id"], "Second")

    page_one = client.get(
        "/v1/crm/opportunities",
        headers=_headers(),
        params={"limit": 1},
    )
    assert page_one.status_code == 200
    page_one_data = page_one.json()["data"]
    assert len(page_one_data["items"]) == 1
    assert page_one_data["next_cursor"]
    assert set(page_one_data["items"][0]) == {
        "id",
        "customer_id",
        "code",
        "title",
        "owner_subject_id",
        "status",
        "updated_at",
        "version",
    }

    page_two = client.get(
        "/v1/crm/opportunities",
        headers=_headers(),
        params={"limit": 1, "cursor": page_one_data["next_cursor"]},
    )
    assert {
        page_one_data["items"][0]["id"],
        page_two.json()["data"]["items"][0]["id"],
    } == {first["id"], second["id"]}

    archived = client.post(
        f"/v1/crm/opportunities/{first['id']}/archive",
        headers=_headers(),
        json={"reason": "G514 active-only contract", "expected_version": 1},
    )
    assert archived.status_code == 200
    visible = client.get(
        "/v1/crm/opportunities", headers=_headers()
    ).json()["data"]["items"]
    assert [item["id"] for item in visible] == [second["id"]]


def test_g514_list_fails_closed_and_rejects_invalid_pagination() -> None:
    denied = _client(grant=False).get(
        "/v1/crm/opportunities", headers=_headers()
    )
    assert denied.status_code == 403
    assert denied.json()["detail"]["code"] == "PERMISSION_DENIED"

    client = _client()
    assert client.get(
        "/v1/crm/opportunities?limit=101", headers=_headers()
    ).status_code == 422
    invalid = client.get(
        "/v1/crm/opportunities",
        headers=_headers(),
        params={"cursor": "invalid"},
    )
    assert invalid.status_code == 400
    assert invalid.json()["detail"]["code"] == "COMMON_VALIDATION_FAILED"


def test_g514_update_conflict_never_overwrites_current_opportunity() -> None:
    client = _client()
    customer = _create_customer(client)
    opportunity = _create_opportunity(client, customer["id"], "Original")
    current = client.patch(
        f"/v1/crm/opportunities/{opportunity['id']}",
        headers=_headers(),
        json={
            "title": "Current",
            "owner_subject_id": None,
            "expected_version": opportunity["version"],
        },
    )
    assert current.status_code == 200

    stale = client.patch(
        f"/v1/crm/opportunities/{opportunity['id']}",
        headers=_headers(),
        json={
            "title": "Stale overwrite",
            "owner_subject_id": None,
            "expected_version": opportunity["version"],
        },
    )
    assert stale.status_code == 409
    detail = client.get(
        f"/v1/crm/opportunities/{opportunity['id']}",
        headers=_headers(),
    )
    assert detail.json()["data"]["title"] == "Current"


def test_g514_openapi_and_terminal_expose_closed_managed_contract() -> None:
    client = _client()
    spec = client.get("/openapi.json").json()
    assert spec["paths"]["/v1/crm/opportunities"]["get"]
    schemas = spec["components"]["schemas"]
    for name in (
        "OpportunityListItemView",
        "OpportunityListData",
        "OpportunityListEnvelope",
    ):
        assert schemas[name]["additionalProperties"] is False

    html = (ROOT / "smart_terminal" / "ui" / "index.html").read_text(encoding="utf-8")
    app = (ROOT / "smart_terminal" / "ui" / "app.js").read_text(encoding="utf-8")
    for control in (
        "btnCrmNewOpportunity",
        "btnCrmEditOpportunity",
        "btnCrmArchiveOpportunity",
        "crmOpportunityCustomer",
        "crmOpportunityForm",
    ):
        assert f'id="{control}"' in html
    for symbol in (
        "loadCrmOpportunities",
        "selectCrmOpportunity",
        "submitCrmOpportunity",
        "pkg.crm.opportunity",
        "expected_version",
    ):
        assert symbol in app
    managed = app[
        app.index("function openCrmOpportunityEditor") :
        app.index("async function submitCrmArchive")
    ]
    assert "tenant_id" not in managed
    assert "automatic retry" not in managed.lower()


def test_g514_sql_repository_lists_without_schema_change() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    with engine.begin() as connection:
        connection.exec_driver_sql("ATTACH DATABASE ':memory:' AS crm")
        CustomerRecord.__table__.create(connection)
        OpportunityRecord.__table__.create(connection)
    now = datetime.now(timezone.utc)
    customer_id = uuid4()
    opportunity_id = uuid4()
    with Session(engine) as session:
        repository = SQLAlchemyCRMRepository(session, tenant_id=TENANT)
        repository.add_customer(
            Customer(
                id=customer_id,
                tenant_id=TENANT,
                code="C-SQL-G514",
                display_name="SQL Customer",
                owner_subject_id=None,
                status=CustomerStatus.ACTIVE,
                created_at=now,
                updated_at=now,
            )
        )
        repository.add_opportunity(
            Opportunity(
                id=opportunity_id,
                tenant_id=TENANT,
                customer_id=customer_id,
                code="OPP-SQL-G514",
                title="SQL Opportunity",
                owner_subject_id=None,
                status=OpportunityStatus.ACTIVE,
                created_at=now,
                updated_at=now,
            )
        )
        session.commit()
        assert [item.id for item in repository.list_opportunities(limit=10)] == [
            opportunity_id
        ]


def test_g514_closeout_resolves_hold_and_preserves_successor_boundary() -> None:
    acceptance = (
        ROOT / "docs" / "project" / "CRM_OPPORTUNITY_UI_G514_ACCEPTANCE.md"
    ).read_text(encoding="utf-8")
    hold = (
        ROOT / "docs" / "project" / "CRM_OPPORTUNITY_UI_G514_HOLD.md"
    ).read_text(encoding="utf-8")
    roadmap = (
        ROOT / "docs" / "project" / "POST_CRM_VERTICAL_ROADMAP.md"
    ).read_text(encoding="utf-8")
    manifest = (
        ROOT / "docs" / "release" / "RELEASE_MANIFEST.yaml"
    ).read_text(encoding="utf-8")

    assert "18 passed" in acceptance
    assert "Production Authorization: **None**" in acceptance
    assert "HOLD RESOLVED" in hold
    assert "TRACK-G514 COMPLETE" in roadmap
    assert "FINAL STOP TRACK-G514" in roadmap
    assert "G515–G521" in roadmap
    assert "PHX-G514" in manifest
    assert "crm_opportunity_managed_ui_and_list_query" in manifest
