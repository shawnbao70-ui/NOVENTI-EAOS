"""PHX-G518 CRM Quote Convert UI contracts."""

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
    CONVERSION_RESOURCE,
    CUSTOMER_RESOURCE,
    OPPORTUNITY_RESOURCE,
    QUOTE_LINE_RESOURCE,
    QUOTE_RESOURCE,
    REQUIREMENT_RESOURCE,
    SALES_ORDER_RESOURCE,
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
        correlation_id="corr-g518-grant",
        request_time=ExecutionContext.utc_now(),
    )


def _headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(SUBJECT),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": "corr-g518-http",
    }


def _client(*, grant: bool = True) -> TestClient:
    audit = InMemoryAuditLog()
    permission = PermissionService(
        audit_log=audit,
        grant_administrators={SUBJECT},
        principal_eligibility=_Eligibility(),
    )
    if grant:
        for resource, actions in (
            (CUSTOMER_RESOURCE, {"create", "read", "update", "archive"}),
            (OPPORTUNITY_RESOURCE, {"create", "read", "update", "archive"}),
            (REQUIREMENT_RESOURCE, {"create", "read", "update", "archive"}),
            (QUOTE_RESOURCE, {"create", "read", "update", "archive", "issue"}),
            (QUOTE_LINE_RESOURCE, {"create", "read", "update", "archive"}),
            (CONVERSION_RESOURCE, {"create", "read", "convert"}),
            (SALES_ORDER_RESOURCE, {"create", "read"}),
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


def _issued_quote(client: TestClient) -> dict:
    customer = client.post(
        "/v1/crm/customers",
        headers=_headers(),
        json={"code": "C-G518", "display_name": "G518 Customer"},
    ).json()["data"]
    opportunity = client.post(
        "/v1/crm/opportunities",
        headers=_headers(),
        json={"customer_id": customer["id"], "title": "G518 Opportunity"},
    ).json()["data"]
    requirement = client.post(
        "/v1/crm/requirements",
        headers=_headers(),
        json={
            "opportunity_id": opportunity["id"],
            "title": "G518 Requirement",
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
                "description": "G518 line",
                "quantity": "2.000",
                "unit_price": "15.50",
            },
        ).status_code
        == 201
    )
    issued = client.post(
        f"/v1/crm/quotes/{quote['id']}/issue",
        headers=_headers(),
        json={"idempotency_key": str(uuid4()), "human_confirm": True},
    )
    assert issued.status_code == 200
    return issued.json()["data"]


def test_g518_convert_is_idempotent_and_creates_sales_order_shell() -> None:
    client = _client()
    quote = _issued_quote(client)
    key = str(uuid4())
    first = client.post(
        f"/v1/crm/quotes/{quote['id']}/convert",
        headers=_headers(),
        json={"idempotency_key": key},
    )
    assert first.status_code == 201
    conversion = first.json()["data"]
    assert conversion["status"] == "ready"
    assert conversion["functional_total"] == "31.00"
    retry = client.post(
        f"/v1/crm/quotes/{quote['id']}/convert",
        headers=_headers(),
        json={"idempotency_key": key},
    )
    assert retry.status_code == 201
    assert retry.json()["data"]["id"] == conversion["id"]
    conflict = client.post(
        f"/v1/crm/quotes/{quote['id']}/convert",
        headers=_headers(),
        json={"idempotency_key": str(uuid4())},
    )
    assert conflict.status_code == 409
    sales_order = client.post(
        f"/v1/crm/conversions/{conversion['id']}/sales-order",
        headers=_headers(),
        json={"idempotency_key": str(uuid4())},
    )
    assert sales_order.status_code == 201
    assert sales_order.json()["data"]["status"] == "created"
    assert sales_order.json()["data"]["conversion_id"] == conversion["id"]


def test_g518_draft_quote_cannot_convert() -> None:
    client = _client()
    customer = client.post(
        "/v1/crm/customers",
        headers=_headers(),
        json={"code": "C-G518-D", "display_name": "Draft"},
    ).json()["data"]
    opportunity = client.post(
        "/v1/crm/opportunities",
        headers=_headers(),
        json={"customer_id": customer["id"], "title": "Draft Opp"},
    ).json()["data"]
    requirement = client.post(
        "/v1/crm/requirements",
        headers=_headers(),
        json={
            "opportunity_id": opportunity["id"],
            "title": "Draft Req",
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
            f"/v1/crm/quotes/{quote['id']}/convert",
            headers=_headers(),
            json={"idempotency_key": str(uuid4())},
        ).status_code
        == 409
    )


def test_g518_convert_fails_closed_without_permission() -> None:
    client = _client(grant=False)
    assert (
        client.post(
            f"/v1/crm/quotes/{uuid4()}/convert",
            headers=_headers(),
            json={"idempotency_key": str(uuid4())},
        ).status_code
        == 403
    )


def test_g518_terminal_exposes_convert_without_confirm_or_issue() -> None:
    html = (ROOT / "smart_terminal" / "ui" / "index.html").read_text(encoding="utf-8")
    app = (ROOT / "smart_terminal" / "ui" / "app.js").read_text(encoding="utf-8")
    for control in (
        "btnCrmConvertQuote",
        "crmConvertForm",
        "crmConvertConfirmed",
        "btnCrmCreateSalesOrder",
        "crmCreateSoForm",
        "crmConversionDetail",
        "crmConvertSoDetail",
    ):
        assert f'id="{control}"' in html
    chunk = app[
        app.index("function openCrmConvertEditor") :
        app.index("async function submitCrmArchive")
    ]
    assert "confirm_sales_order" not in chunk
    assert "/issue" not in chunk
    assert "delivery-order" not in chunk
    assert "ar-invoice" not in chunk
    assert "tenant_id" not in chunk


def test_g518_closeout_preserves_successor_boundaries() -> None:
    roadmap = (ROOT / "docs" / "project" / "POST_CRM_VERTICAL_ROADMAP.md").read_text(
        encoding="utf-8"
    )
    acceptance = (
        ROOT / "docs" / "project" / "CRM_QUOTE_CONVERT_UI_G518_ACCEPTANCE.md"
    ).read_text(encoding="utf-8")
    authorization = (
        ROOT
        / "docs"
        / "project"
        / "CRM_QUOTE_CONVERT_G518_CODING_AUTHORIZATION_SUMMARY.md"
    ).read_text(encoding="utf-8")
    manifest = (ROOT / "docs" / "release" / "RELEASE_MANIFEST.yaml").read_text(
        encoding="utf-8"
    )
    assert "FINAL STOP TRACK-G518" in roadmap
    assert "G519–G525 remain closed" in roadmap
    assert "PHX-G518 COMPLETE" in acceptance
    assert "Further Coding / Runtime / Production: **None**" in acceptance
    assert "Backend/Database/Alembic/Runtime/Production: **None**" in authorization
    assert "id: PHX-G518" in manifest
