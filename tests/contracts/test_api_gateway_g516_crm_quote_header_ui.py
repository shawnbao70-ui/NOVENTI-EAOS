"""PHX-G516 CRM Quote Header list-query and managed UI contracts."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
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
from noventi.crm.models import Quote, QuoteStatus
from noventi.crm.persistence import (
    CustomerRecord,
    OpportunityRecord,
    QuoteRecord,
    RequirementRecord,
    SQLAlchemyCRMRepository,
)
from noventi.crm.repository import InMemoryCRMRepository
from noventi.crm.service import (
    CUSTOMER_RESOURCE,
    OPPORTUNITY_RESOURCE,
    QUOTE_RESOURCE,
    REQUIREMENT_RESOURCE,
    CRMService,
)

ROOT = Path(__file__).resolve().parents[2]
SUBJECT, TENANT = uuid4(), uuid4()


class _Eligibility:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


def _context() -> ExecutionContext:
    return ExecutionContext(
        subject_id=SUBJECT,
        subject_type=SubjectType.HUMAN,
        tenant_id=TENANT,
        correlation_id="corr-g516-grant",
        request_time=ExecutionContext.utc_now(),
    )


def _headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(SUBJECT),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": "corr-g516-http",
    }


def _client(*, grant: bool = True) -> TestClient:
    audit = InMemoryAuditLog()
    permission = PermissionService(
        audit_log=audit,
        grant_administrators={SUBJECT},
        principal_eligibility=_Eligibility(),
    )
    if grant:
        for resource in (
            CUSTOMER_RESOURCE,
            OPPORTUNITY_RESOURCE,
            REQUIREMENT_RESOURCE,
            QUOTE_RESOURCE,
        ):
            assert permission.grant(
                _context(),
                principal_subject_id=SUBJECT,
                resource_type=resource,
                actions={"create", "read", "update", "archive"},
                scope_level=ScopeLevel.TENANT,
            ).ok
    crm = CRMService(
        permission,
        repository=InMemoryCRMRepository(tenant_id=TENANT),
        audit_log=audit,
    )
    return TestClient(create_app(crm_service=crm, permission_service=permission))


def _requirement(client: TestClient) -> dict:
    customer = client.post(
        "/v1/crm/customers",
        headers=_headers(),
        json={"code": "C-G516", "display_name": "G516 Customer"},
    ).json()["data"]
    opportunity = client.post(
        "/v1/crm/opportunities",
        headers=_headers(),
        json={"customer_id": customer["id"], "title": "G516 Opportunity"},
    ).json()["data"]
    return client.post(
        "/v1/crm/requirements",
        headers=_headers(),
        json={
            "opportunity_id": opportunity["id"],
            "title": "G516 Requirement",
            "description": None,
        },
    ).json()["data"]


def _quote(client: TestClient, requirement_id: str, notes: str) -> dict:
    response = client.post(
        "/v1/crm/quotes",
        headers=_headers(),
        json={"requirement_id": requirement_id, "currency": "USD", "notes": notes},
    )
    assert response.status_code == 201
    return response.json()["data"]


def test_g516_quote_list_is_bounded_minimal_and_excludes_archived() -> None:
    client = _client()
    requirement = _requirement(client)
    first = _quote(client, requirement["id"], "private note one")
    second = _quote(client, requirement["id"], "private note two")
    page = client.get(
        "/v1/crm/quotes", headers=_headers(), params={"limit": 1}
    ).json()["data"]
    assert page["next_cursor"]
    assert set(page["items"][0]) == {
        "id",
        "requirement_id",
        "code",
        "currency",
        "status",
        "updated_at",
        "version",
    }
    assert "notes" not in page["items"][0]
    next_page = client.get(
        "/v1/crm/quotes",
        headers=_headers(),
        params={"limit": 1, "cursor": page["next_cursor"]},
    ).json()["data"]
    assert {page["items"][0]["id"], next_page["items"][0]["id"]} == {
        first["id"],
        second["id"],
    }
    assert client.post(
        f"/v1/crm/quotes/{first['id']}/archive",
        headers=_headers(),
        json={"reason": "G516 active collection", "expected_version": 1},
    ).status_code == 200
    visible = client.get("/v1/crm/quotes", headers=_headers()).json()["data"]["items"]
    assert [item["id"] for item in visible] == [second["id"]]


def test_g516_list_fails_closed_and_validates_pagination() -> None:
    assert _client(grant=False).get(
        "/v1/crm/quotes", headers=_headers()
    ).status_code == 403
    client = _client()
    assert client.get("/v1/crm/quotes?limit=101", headers=_headers()).status_code == 422
    assert client.get(
        "/v1/crm/quotes", headers=_headers(), params={"cursor": "invalid"}
    ).status_code == 400


def test_g516_stale_update_never_overwrites_quote() -> None:
    client = _client()
    quote = _quote(client, _requirement(client)["id"], "original")
    assert client.patch(
        f"/v1/crm/quotes/{quote['id']}",
        headers=_headers(),
        json={"currency": "EUR", "notes": "current", "expected_version": 1},
    ).status_code == 200
    assert client.patch(
        f"/v1/crm/quotes/{quote['id']}",
        headers=_headers(),
        json={"currency": "USD", "notes": "stale", "expected_version": 1},
    ).status_code == 409
    detail = client.get(f"/v1/crm/quotes/{quote['id']}", headers=_headers())
    assert detail.json()["data"]["currency"] == "EUR"


def test_g516_openapi_and_ui_keep_lines_issue_convert_outside() -> None:
    spec = _client().get("/openapi.json").json()
    for name in ("QuoteListItemView", "QuoteListData", "QuoteListEnvelope"):
        assert spec["components"]["schemas"][name]["additionalProperties"] is False
    html = (ROOT / "smart_terminal" / "ui" / "index.html").read_text(encoding="utf-8")
    app = (ROOT / "smart_terminal" / "ui" / "app.js").read_text(encoding="utf-8")
    for control in (
        "btnCrmNewQuote",
        "btnCrmEditQuote",
        "btnCrmArchiveQuote",
        "crmQuoteRequirement",
        "crmQuoteForm",
    ):
        assert f'id="{control}"' in html
    chunk = app[
        app.index("function openCrmQuoteEditor") :
        app.index("function openCrmQuoteLineEditor")
    ]
    assert "tenant_id" not in chunk
    assert "issue_quote" not in chunk
    assert "convert_quote" not in chunk
    assert "quote_line" not in chunk


def test_g516_sql_repository_lists_without_schema_change() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    with engine.begin() as connection:
        connection.exec_driver_sql("ATTACH DATABASE ':memory:' AS crm")
        CustomerRecord.__table__.create(connection)
        OpportunityRecord.__table__.create(connection)
        RequirementRecord.__table__.create(connection)
        QuoteRecord.__table__.create(connection)
    now, requirement_id, quote_id = datetime.now(timezone.utc), uuid4(), uuid4()
    with Session(engine) as session:
        repository = SQLAlchemyCRMRepository(session, tenant_id=TENANT)
        repository.add_quote(
            Quote(
                id=quote_id,
                tenant_id=TENANT,
                requirement_id=requirement_id,
                code="Q-SQL-G516",
                currency="USD",
                functional_currency="USD",
                fx_rate=Decimal("1"),
                notes=None,
                status=QuoteStatus.DRAFT,
                created_at=now,
                updated_at=now,
            )
        )
        session.commit()
        assert [item.id for item in repository.list_quotes(limit=10)] == [quote_id]


def test_g516_closeout_preserves_release_and_production_boundaries() -> None:
    roadmap = (ROOT / "docs" / "project" / "POST_CRM_VERTICAL_ROADMAP.md").read_text(
        encoding="utf-8"
    )
    acceptance = (
        ROOT / "docs" / "project" / "CRM_QUOTE_HEADER_UI_G516_ACCEPTANCE.md"
    ).read_text(encoding="utf-8")
    hold = (
        ROOT / "docs" / "project" / "CRM_QUOTE_HEADER_UI_G516_HOLD.md"
    ).read_text(encoding="utf-8")
    manifest = (
        ROOT / "docs" / "release" / "RELEASE_MANIFEST.yaml"
    ).read_text(encoding="utf-8")
    authorization = (
        ROOT
        / "docs"
        / "project"
        / "CRM_QUOTE_HEADER_G516_CODING_AUTHORIZATION_SUMMARY.md"
    ).read_text(encoding="utf-8")
    assert "FINAL STOP TRACK-G516" in roadmap
    assert "G517–G521 remain closed" in roadmap
    assert "PHX-G516 COMPLETE" in acceptance
    assert "Further Coding / Runtime / Production: **None**" in acceptance
    assert "Queue: **RESOLVED**" in hold
    assert "id: PHX-G516" in manifest
    assert "Database/Alembic/Runtime/Production: **None**" in authorization
