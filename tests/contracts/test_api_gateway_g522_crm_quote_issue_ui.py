"""PHX-G522 CRM Quote Issue UI contracts."""

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
        correlation_id="corr-g522-grant",
        request_time=ExecutionContext.utc_now(),
    )


def _headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(SUBJECT),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": "corr-g522-http",
    }


def _client(*, grant: bool = True, issue: bool = True) -> TestClient:
    audit = InMemoryAuditLog()
    permission = PermissionService(
        audit_log=audit,
        grant_administrators={SUBJECT},
        principal_eligibility=_Eligibility(),
    )
    if grant:
        quote_actions = {"create", "read", "update", "archive"}
        if issue:
            quote_actions.add("issue")
        for resource, actions in (
            (CUSTOMER_RESOURCE, {"create", "read", "update", "archive"}),
            (OPPORTUNITY_RESOURCE, {"create", "read", "update", "archive"}),
            (REQUIREMENT_RESOURCE, {"create", "read", "update", "archive"}),
            (QUOTE_RESOURCE, quote_actions),
            (QUOTE_LINE_RESOURCE, {"create", "read", "update", "archive"}),
        ):
            assert permission.grant(
                _context(),
                principal_subject_id=SUBJECT,
                resource_type=resource,
                actions=actions,
                scope_level=ScopeLevel.TENANT,
            ).ok
    crm = CRMService(
        permission,
        repository=InMemoryCRMRepository(tenant_id=TENANT),
        audit_log=audit,
    )
    return TestClient(create_app(crm_service=crm, permission_service=permission))


def _draft_quote(client: TestClient, suffix: str = "A") -> dict:
    customer = client.post(
        "/v1/crm/customers",
        headers=_headers(),
        json={"code": f"C-G522-{suffix}", "display_name": f"G522 {suffix}"},
    ).json()["data"]
    opportunity = client.post(
        "/v1/crm/opportunities",
        headers=_headers(),
        json={"customer_id": customer["id"], "title": f"G522 Opp {suffix}"},
    ).json()["data"]
    requirement = client.post(
        "/v1/crm/requirements",
        headers=_headers(),
        json={
            "opportunity_id": opportunity["id"],
            "title": f"G522 Req {suffix}",
            "description": None,
        },
    ).json()["data"]
    quote = client.post(
        "/v1/crm/quotes",
        headers=_headers(),
        json={
            "requirement_id": requirement["id"],
            "currency": "USD",
            "notes": None,
        },
    ).json()["data"]
    assert (
        client.post(
            f"/v1/crm/quotes/{quote['id']}/lines",
            headers=_headers(),
            json={
                "description": f"Line {suffix}",
                "quantity": "1.000",
                "unit_price": "20.00",
            },
        ).status_code
        == 201
    )
    return quote


def test_g522_issue_is_idempotent_and_publishes_draft() -> None:
    client = _client()
    quote = _draft_quote(client)
    assert quote["status"] == "draft"
    key = str(uuid4())
    first = client.post(
        f"/v1/crm/quotes/{quote['id']}/issue",
        headers=_headers(),
        json={"idempotency_key": key, "human_confirm": True},
    )
    assert first.status_code == 200
    issued = first.json()["data"]
    assert issued["status"] == "issued"
    assert issued["id"] == quote["id"]
    retry = client.post(
        f"/v1/crm/quotes/{quote['id']}/issue",
        headers=_headers(),
        json={"idempotency_key": key, "human_confirm": True},
    )
    assert retry.status_code == 200
    assert retry.json()["data"]["id"] == quote["id"]
    assert retry.json()["data"]["status"] == "issued"


def test_g522_issue_requires_human_confirm_and_fails_closed() -> None:
    no_issue = _client(issue=False)
    quote = _draft_quote(no_issue, "B")
    assert (
        no_issue.post(
            f"/v1/crm/quotes/{quote['id']}/issue",
            headers=_headers(),
            json={"idempotency_key": str(uuid4()), "human_confirm": True},
        ).status_code
        == 403
    )
    denied = _client(grant=False)
    assert (
        denied.post(
            f"/v1/crm/quotes/{uuid4()}/issue",
            headers=_headers(),
            json={"idempotency_key": str(uuid4()), "human_confirm": True},
        ).status_code
        == 403
    )
    granted = _client()
    quote2 = _draft_quote(granted, "C")
    assert (
        granted.post(
            f"/v1/crm/quotes/{quote2['id']}/issue",
            headers=_headers(),
            json={"idempotency_key": str(uuid4()), "human_confirm": False},
        ).status_code
        == 422
    )


def test_g522_terminal_exposes_issue_without_delivery_or_invoice() -> None:
    html = (ROOT / "smart_terminal" / "ui" / "index.html").read_text(encoding="utf-8")
    app = (ROOT / "smart_terminal" / "ui" / "app.js").read_text(encoding="utf-8")
    for control in (
        "btnCrmIssueQuote",
        "crmIssueQuoteForm",
        "crmIssueQuoteConfirmed",
        "crmIssueQuoteApprovalRef",
        "btnCrmSubmitIssueQuote",
    ):
        assert f'id="{control}"' in html
    chunk = app[
        app.index("function openCrmIssueQuoteEditor") :
        app.index("async function submitCrmConvert")
    ]
    assert "human_confirm: true" in chunk
    assert "crmQuoteIssue" in chunk
    assert "delivery-order" not in chunk
    assert "ar-invoice" not in chunk
    assert "commercial-hold" not in chunk
    assert "tenant_id" not in chunk
    assert "openCrmIssueQuoteEditor" in app
    assert "submitCrmIssueQuote" in app


def test_g522_closeout_preserves_successor_boundaries() -> None:
    roadmap = (ROOT / "docs" / "project" / "POST_CRM_VERTICAL_ROADMAP.md").read_text(
        encoding="utf-8"
    )
    acceptance = (
        ROOT / "docs" / "project" / "CRM_QUOTE_ISSUE_UI_G522_ACCEPTANCE.md"
    ).read_text(encoding="utf-8")
    authorization = (
        ROOT
        / "docs"
        / "project"
        / "CRM_QUOTE_ISSUE_G522_CODING_AUTHORIZATION_SUMMARY.md"
    ).read_text(encoding="utf-8")
    manifest = (ROOT / "docs" / "release" / "RELEASE_MANIFEST.yaml").read_text(
        encoding="utf-8"
    )
    assert "FINAL STOP TRACK-G522" in roadmap
    assert "G523–G527 remain closed" in roadmap
    assert "PHX-G522 COMPLETE" in acceptance
    assert "57 passed" in acceptance
    assert "Further Coding / Runtime / Production: **None**" in acceptance
    assert "Backend/Database/Alembic/Runtime/Production: **None**" in authorization
    assert "id: PHX-G522" in manifest
