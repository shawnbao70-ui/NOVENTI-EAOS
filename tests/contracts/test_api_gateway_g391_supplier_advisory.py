"""PHX-G391 Supplier advisory expand — Supplier360 read source, authority none."""

from __future__ import annotations

from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.schemas.purchase import SupplierAdvisoryEnvelope
from kernel.permission.models import ScopeLevel
from kernel.permission.service import PermissionService
from kernel.shared.audit import InMemoryAuditLog
from kernel.shared.context import ExecutionContext, SubjectType
from noventi.purchase.repository import InMemoryPurchaseRepository
from noventi.purchase.service import SUPPLIER_RESOURCE, PurchaseService
from noventi.purchase.supplier360 import (
    SUPPLIER360_RESOURCE,
    AssembledSupplier360Repository,
    Supplier360Service,
)

SUBJECT, TENANT = uuid4(), uuid4()


class _Eligibility:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


def _ctx() -> ExecutionContext:
    return ExecutionContext(
        subject_id=SUBJECT,
        subject_type=SubjectType.HUMAN,
        tenant_id=TENANT,
        correlation_id="corr-g391",
        request_time=ExecutionContext.utc_now(),
    )


def _headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(SUBJECT),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": "corr-g391-http",
    }


def _client(*, grant_360: bool = True) -> TestClient:
    audit = InMemoryAuditLog()
    permission = PermissionService(
        audit_log=audit,
        grant_administrators={SUBJECT},
        principal_eligibility=_Eligibility(),
    )
    assert permission.grant(
        _ctx(),
        principal_subject_id=SUBJECT,
        resource_type=SUPPLIER_RESOURCE,
        actions={"create", "read"},
        scope_level=ScopeLevel.TENANT,
    ).ok
    if grant_360:
        assert permission.grant(
            _ctx(),
            principal_subject_id=SUBJECT,
            resource_type=SUPPLIER360_RESOURCE,
            actions={"read"},
            scope_level=ScopeLevel.TENANT,
        ).ok
    purchase_repo = InMemoryPurchaseRepository(tenant_id=TENANT)
    return TestClient(
        create_app(
            purchase_service=PurchaseService(
                permission,
                repository=purchase_repo,
                audit_log=audit,
            ),
            supplier360_service=Supplier360Service(
                permission,
                repository=AssembledSupplier360Repository(purchase_repo),
                audit_log=audit,
            ),
        )
    )


def test_g391_supplier_advisory_reads_supplier360_fail_closed_authority() -> None:
    client = _client()
    supplier = client.post(
        "/v1/purchase/suppliers",
        headers=_headers(),
        json={"code": f"G391-{uuid4().hex[:8]}", "display_name": "G391 Supplier"},
    ).json()["data"]
    response = client.get(
        f"/v1/purchase/suppliers/{supplier['id']}/advisory",
        headers=_headers(),
    )
    assert response.status_code == 200, response.text
    SupplierAdvisoryEnvelope.model_validate(response.json())
    data = response.json()["data"]
    assert data["supplier_id"] == supplier["id"]
    assert data["read_source"] == "supplier360"
    assert data["execution_authority"] == "none"
    assert data["commercial_auto_write"] is False
    assert data["supplier360"]["supplier_id"] == supplier["id"]
    assert data["supplier360"]["supplier_code"] == supplier["code"]


def test_g391_supplier_advisory_denied_without_360_grant() -> None:
    client = _client(grant_360=False)
    supplier = client.post(
        "/v1/purchase/suppliers",
        headers=_headers(),
        json={"code": f"G391-{uuid4().hex[:8]}", "display_name": "G391 Denied"},
    ).json()["data"]
    response = client.get(
        f"/v1/purchase/suppliers/{supplier['id']}/advisory",
        headers=_headers(),
    )
    assert response.status_code == 403


def test_g391_no_advisory_write_invent() -> None:
    paths = _client().get("/openapi.json").json()["paths"]
    path = "/v1/purchase/suppliers/{supplier_id}/advisory"
    assert path in paths
    assert list(paths[path].keys()) == ["get"]
