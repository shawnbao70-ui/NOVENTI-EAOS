"""PHX-G515 CRM Requirement list-query and managed Terminal UI contracts."""

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
from noventi.crm.models import (
    Customer,
    CustomerStatus,
    Opportunity,
    OpportunityStatus,
    Requirement,
    RequirementStatus,
)
from noventi.crm.persistence import (
    CustomerRecord,
    OpportunityRecord,
    RequirementRecord,
    SQLAlchemyCRMRepository,
)
from noventi.crm.repository import InMemoryCRMRepository
from noventi.crm.service import (
    CUSTOMER_RESOURCE,
    OPPORTUNITY_RESOURCE,
    REQUIREMENT_RESOURCE,
    CRMService,
)

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
        correlation_id="corr-g515-grant",
        request_time=ExecutionContext.utc_now(),
    )


def _headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(SUBJECT),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": "corr-g515-http",
    }


def _client(*, grant: bool = True) -> TestClient:
    audit = InMemoryAuditLog()
    permission = PermissionService(
        audit_log=audit,
        grant_administrators={SUBJECT},
        principal_eligibility=_AllowPrincipalEligibility(),
    )
    if grant:
        for resource_type in (
            CUSTOMER_RESOURCE,
            OPPORTUNITY_RESOURCE,
            REQUIREMENT_RESOURCE,
        ):
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


def _parents(client: TestClient) -> tuple[dict, dict]:
    customer = client.post(
        "/v1/crm/customers",
        headers=_headers(),
        json={"code": "C-G515", "display_name": "G515 Customer"},
    ).json()["data"]
    opportunity = client.post(
        "/v1/crm/opportunities",
        headers=_headers(),
        json={"customer_id": customer["id"], "title": "G515 Opportunity"},
    ).json()["data"]
    return customer, opportunity


def _create_requirement(client: TestClient, opportunity_id: str, title: str) -> dict:
    response = client.post(
        "/v1/crm/requirements",
        headers=_headers(),
        json={
            "opportunity_id": opportunity_id,
            "title": title,
            "description": None,
        },
    )
    assert response.status_code == 201
    return response.json()["data"]


def test_g515_requirement_list_is_bounded_paginated_and_active_only() -> None:
    client = _client()
    _, opportunity = _parents(client)
    first = _create_requirement(client, opportunity["id"], "First")
    second = _create_requirement(client, opportunity["id"], "Second")
    page_one = client.get(
        "/v1/crm/requirements", headers=_headers(), params={"limit": 1}
    )
    assert page_one.status_code == 200
    data = page_one.json()["data"]
    assert data["next_cursor"]
    assert set(data["items"][0]) == {
        "id",
        "opportunity_id",
        "code",
        "title",
        "status",
        "updated_at",
        "version",
    }
    page_two = client.get(
        "/v1/crm/requirements",
        headers=_headers(),
        params={"limit": 1, "cursor": data["next_cursor"]},
    )
    assert {data["items"][0]["id"], page_two.json()["data"]["items"][0]["id"]} == {
        first["id"],
        second["id"],
    }
    assert client.post(
        f"/v1/crm/requirements/{first['id']}/archive",
        headers=_headers(),
        json={"reason": "G515 active-only", "expected_version": 1},
    ).status_code == 200
    visible = client.get(
        "/v1/crm/requirements", headers=_headers()
    ).json()["data"]["items"]
    assert [item["id"] for item in visible] == [second["id"]]


def test_g515_list_fails_closed_and_validates_cursor() -> None:
    denied = _client(grant=False).get(
        "/v1/crm/requirements", headers=_headers()
    )
    assert denied.status_code == 403
    assert _client().get(
        "/v1/crm/requirements?limit=101", headers=_headers()
    ).status_code == 422
    invalid = _client().get(
        "/v1/crm/requirements",
        headers=_headers(),
        params={"cursor": "invalid"},
    )
    assert invalid.status_code == 400


def test_g515_conflict_never_overwrites_current_requirement() -> None:
    client = _client()
    _, opportunity = _parents(client)
    requirement = _create_requirement(client, opportunity["id"], "Original")
    assert client.patch(
        f"/v1/crm/requirements/{requirement['id']}",
        headers=_headers(),
        json={
            "title": "Current",
            "description": "current",
            "expected_version": 1,
        },
    ).status_code == 200
    stale = client.patch(
        f"/v1/crm/requirements/{requirement['id']}",
        headers=_headers(),
        json={
            "title": "Stale overwrite",
            "description": None,
            "expected_version": 1,
        },
    )
    assert stale.status_code == 409
    detail = client.get(
        f"/v1/crm/requirements/{requirement['id']}", headers=_headers()
    )
    assert detail.json()["data"]["title"] == "Current"


def test_g515_openapi_and_terminal_expose_closed_managed_contract() -> None:
    spec = _client().get("/openapi.json").json()
    assert spec["paths"]["/v1/crm/requirements"]["get"]
    schemas = spec["components"]["schemas"]
    for name in (
        "RequirementListItemView",
        "RequirementListData",
        "RequirementListEnvelope",
    ):
        assert schemas[name]["additionalProperties"] is False
    html = (ROOT / "smart_terminal" / "ui" / "index.html").read_text(encoding="utf-8")
    app = (ROOT / "smart_terminal" / "ui" / "app.js").read_text(encoding="utf-8")
    for control in (
        "btnCrmNewRequirement",
        "btnCrmEditRequirement",
        "btnCrmArchiveRequirement",
        "crmRequirementOpportunity",
        "crmRequirementForm",
    ):
        assert f'id="{control}"' in html
    for symbol in (
        "loadCrmRequirements",
        "selectCrmRequirement",
        "submitCrmRequirement",
        "pkg.crm.requirement",
    ):
        assert symbol in app
    managed = app[
        app.index("function openCrmRequirementEditor") :
        app.index("async function submitCrmArchive")
    ]
    assert "tenant_id" not in managed


def test_g515_sql_repository_lists_without_schema_change() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    with engine.begin() as connection:
        connection.exec_driver_sql("ATTACH DATABASE ':memory:' AS crm")
        CustomerRecord.__table__.create(connection)
        OpportunityRecord.__table__.create(connection)
        RequirementRecord.__table__.create(connection)
    now = datetime.now(timezone.utc)
    customer_id, opportunity_id, requirement_id = uuid4(), uuid4(), uuid4()
    with Session(engine) as session:
        repository = SQLAlchemyCRMRepository(session, tenant_id=TENANT)
        repository.add_customer(
            Customer(
                id=customer_id,
                tenant_id=TENANT,
                code="C-SQL-G515",
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
                code="OPP-SQL-G515",
                title="SQL Opportunity",
                owner_subject_id=None,
                status=OpportunityStatus.ACTIVE,
                created_at=now,
                updated_at=now,
            )
        )
        repository.add_requirement(
            Requirement(
                id=requirement_id,
                tenant_id=TENANT,
                opportunity_id=opportunity_id,
                code="REQ-SQL-G515",
                title="SQL Requirement",
                description=None,
                status=RequirementStatus.ACTIVE,
                created_at=now,
                updated_at=now,
            )
        )
        session.commit()
        assert [item.id for item in repository.list_requirements(limit=10)] == [
            requirement_id
        ]


def test_g515_closeout_resolves_hold_and_keeps_g516_closed() -> None:
    acceptance = (
        ROOT / "docs" / "project" / "CRM_REQUIREMENT_UI_G515_ACCEPTANCE.md"
    ).read_text(encoding="utf-8")
    hold = (
        ROOT / "docs" / "project" / "CRM_REQUIREMENT_UI_G515_HOLD.md"
    ).read_text(encoding="utf-8")
    roadmap = (
        ROOT / "docs" / "project" / "POST_CRM_VERTICAL_ROADMAP.md"
    ).read_text(encoding="utf-8")
    manifest = (
        ROOT / "docs" / "release" / "RELEASE_MANIFEST.yaml"
    ).read_text(encoding="utf-8")
    assert "24 passed" in acceptance
    assert "Production: **None**" in acceptance
    assert "HOLD RESOLVED" in hold
    assert "TRACK-G515 COMPLETE" in roadmap
    assert "FINAL STOP TRACK-G515" in roadmap
    assert "G516–G521" in roadmap
    assert "PHX-G515" in manifest
    assert "crm_requirement_managed_ui_and_list_query" in manifest
