"""PHX-G517 CRM Quote Lines managed UI contracts."""

from __future__ import annotations

from pathlib import Path
from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from api.gateway import create_app
from kernel.permission.models import ScopeLevel
from kernel.permission.service import PermissionService
from kernel.shared.audit import InMemoryAuditLog
from kernel.shared.context import ExecutionContext, SubjectType
from noventi.crm.repository import InMemoryCRMRepository
from noventi.crm.service import (
    CUSTOMER_RESOURCE,
    OPPORTUNITY_RESOURCE,
    QUOTE_LINE_RESOURCE,
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
        correlation_id="corr-g517-grant",
        request_time=ExecutionContext.utc_now(),
    )


def _headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(SUBJECT),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": "corr-g517-http",
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
            QUOTE_LINE_RESOURCE,
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


def _quote(client: TestClient) -> dict:
    customer = client.post(
        "/v1/crm/customers",
        headers=_headers(),
        json={"code": "C-G517", "display_name": "G517 Customer"},
    ).json()["data"]
    opportunity = client.post(
        "/v1/crm/opportunities",
        headers=_headers(),
        json={"customer_id": customer["id"], "title": "G517 Opportunity"},
    ).json()["data"]
    requirement = client.post(
        "/v1/crm/requirements",
        headers=_headers(),
        json={
            "opportunity_id": opportunity["id"],
            "title": "G517 Requirement",
            "description": None,
        },
    ).json()["data"]
    return client.post(
        "/v1/crm/quotes",
        headers=_headers(),
        json={
            "requirement_id": requirement["id"],
            "currency": "USD",
            "notes": None,
        },
    ).json()["data"]


def test_g517_line_crud_uses_server_amount_and_archive_lifecycle() -> None:
    client = _client()
    quote = _quote(client)
    created = client.post(
        f"/v1/crm/quotes/{quote['id']}/lines",
        headers=_headers(),
        json={"description": "Analysis", "quantity": "2.500", "unit_price": "12.34"},
    )
    assert created.status_code == 201
    line = created.json()["data"]
    assert line["amount"] == "30.85"
    listed = client.get(
        f"/v1/crm/quotes/{quote['id']}/lines", headers=_headers()
    ).json()["data"]
    assert [item["id"] for item in listed] == [line["id"]]
    archived = client.post(
        f"/v1/crm/quotes/{quote['id']}/lines/{line['id']}/archive",
        headers=_headers(),
        json={"reason": "G517 lifecycle", "expected_version": 1},
    )
    assert archived.status_code == 200
    archived_history = client.get(
        f"/v1/crm/quotes/{quote['id']}/lines", headers=_headers()
    ).json()["data"]
    assert archived_history[0]["status"] == "archived"


def test_g517_stale_line_update_never_overwrites() -> None:
    client = _client()
    quote = _quote(client)
    line = client.post(
        f"/v1/crm/quotes/{quote['id']}/lines",
        headers=_headers(),
        json={"description": "Original", "quantity": "1.000", "unit_price": "10.00"},
    ).json()["data"]
    path = f"/v1/crm/quotes/{quote['id']}/lines/{line['id']}"
    assert client.patch(
        path,
        headers=_headers(),
        json={
            "description": "Current",
            "quantity": "2.000",
            "unit_price": "11.00",
            "expected_version": 1,
        },
    ).status_code == 200
    assert client.patch(
        path,
        headers=_headers(),
        json={
            "description": "Stale",
            "quantity": "1.000",
            "unit_price": "1.00",
            "expected_version": 1,
        },
    ).status_code == 409
    assert client.get(path, headers=_headers()).json()["data"]["description"] == "Current"


def test_g517_quote_lines_fail_closed_without_permission() -> None:
    client = _client(grant=False)
    assert client.get(
        f"/v1/crm/quotes/{uuid4()}/lines", headers=_headers()
    ).status_code == 403


def test_g517_terminal_exposes_only_authorized_line_workflow() -> None:
    html = (ROOT / "smart_terminal" / "ui" / "index.html").read_text(encoding="utf-8")
    app = (ROOT / "smart_terminal" / "ui" / "app.js").read_text(encoding="utf-8")
    for control in (
        "btnCrmNewQuoteLine",
        "btnCrmEditQuoteLine",
        "btnCrmArchiveQuoteLine",
        "crmQuoteLineDescription",
        "crmQuoteLineQuantity",
        "crmQuoteLineUnitPrice",
        "crmQuoteLineForm",
    ):
        assert f'id="{control}"' in html
    chunk = app[
        app.index("function openCrmQuoteLineEditor") :
        app.index("function openCrmIssueQuoteEditor")
    ]
    assert "amount:" not in chunk
    assert "tenant_id" not in chunk
    assert "issue_quote" not in chunk
    assert "convert_quote" not in chunk
    assert "crmQuoteIssue" not in chunk


def test_g517_closeout_preserves_backend_and_successor_boundaries() -> None:
    roadmap = (ROOT / "docs" / "project" / "POST_CRM_VERTICAL_ROADMAP.md").read_text(
        encoding="utf-8"
    )
    acceptance = (
        ROOT / "docs" / "project" / "CRM_QUOTE_LINES_UI_G517_ACCEPTANCE.md"
    ).read_text(encoding="utf-8")
    authorization = (
        ROOT
        / "docs"
        / "project"
        / "CRM_QUOTE_LINES_G517_CODING_AUTHORIZATION_SUMMARY.md"
    ).read_text(encoding="utf-8")
    manifest = (
        ROOT / "docs" / "release" / "RELEASE_MANIFEST.yaml"
    ).read_text(encoding="utf-8")
    assert "FINAL STOP TRACK-G517" in roadmap
    assert "G518–G521 remain closed" in roadmap
    assert "PHX-G517 COMPLETE" in acceptance
    assert "35 passed" in acceptance
    assert "Further Coding / Runtime / Production: **None**" in acceptance
    assert "Backend/Database/Alembic/Runtime/Production: **None**" in authorization
    assert "id: PHX-G517" in manifest
