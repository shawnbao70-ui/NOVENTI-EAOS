"""PHX-G327 Brain/Twin CRM advisory HTTP contracts."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from api.gateway import create_app
from eaos_platform.brain.models import InsightKind
from eaos_platform.brain.service import BrainService
from eaos_platform.twin.models import TwinSnapshotStatus
from eaos_platform.twin.service import TwinService
from kernel.permission.models import ScopeLevel
from kernel.permission.service import PermissionService
from kernel.shared.audit import InMemoryAuditLog
from kernel.shared.context import ExecutionContext, SubjectType
from noventi.crm.customer360 import CUSTOMER360_RESOURCE
from noventi.crm.customer_advisory import (
    BrainAdvisoryRef,
    CustomerAdvisoryProjection,
    CustomerAdvisoryService,
    InMemoryCustomerAdvisoryRepository,
    TwinAdvisoryRef,
)
from noventi.crm.repository import InMemoryCRMRepository
from noventi.crm.service import CUSTOMER_RESOURCE, CRMService

SUBJECT, TENANT = uuid4(), uuid4()
ADMIN = SUBJECT


class _Eligibility:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


def _ctx() -> ExecutionContext:
    return ExecutionContext(
        subject_id=SUBJECT,
        subject_type=SubjectType.HUMAN,
        tenant_id=TENANT,
        correlation_id="corr-g327",
        request_time=ExecutionContext.utc_now(),
    )


def _headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(SUBJECT),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": "corr-g327-http",
    }


def _client(
    *,
    grant_360: bool = True,
    projections: tuple[CustomerAdvisoryProjection, ...] = (),
) -> TestClient:
    audit = InMemoryAuditLog()
    permission = PermissionService(
        audit_log=audit,
        grant_administrators={ADMIN},
        principal_eligibility=_Eligibility(),
    )
    assert permission.grant(
        _ctx(),
        principal_subject_id=SUBJECT,
        resource_type=CUSTOMER_RESOURCE,
        actions={"create", "read", "update", "archive"},
        scope_level=ScopeLevel.TENANT,
    ).ok
    if grant_360:
        assert permission.grant(
            _ctx(),
            principal_subject_id=SUBJECT,
            resource_type=CUSTOMER360_RESOURCE,
            actions={"read"},
            scope_level=ScopeLevel.TENANT,
        ).ok
    for resource_type, actions in (
        ("twin_snapshot", {"write", "read"}),
        ("brain_insight", {"publish", "read"}),
    ):
        assert permission.grant(
            _ctx(),
            principal_subject_id=SUBJECT,
            resource_type=resource_type,
            actions=actions,
            scope_level=ScopeLevel.TENANT,
        ).ok
    twin = TwinService(permission)
    brain = BrainService(permission, twin_reader=twin)
    crm_repo = InMemoryCRMRepository(tenant_id=TENANT)
    return TestClient(
        create_app(
            permission_service=permission,
            twin_service=twin,
            brain_service=brain,
            crm_service=CRMService(
                permission, repository=crm_repo, audit_log=audit
            ),
            customer_advisory_service=CustomerAdvisoryService(
                permission,
                repository=InMemoryCustomerAdvisoryRepository(projections),
            ),
        )
    )


def test_g327_advisory_get_with_permission() -> None:
    customer_id = uuid4()
    now = datetime.now(timezone.utc)
    twin_id = uuid4()
    brain_id = uuid4()
    projection = CustomerAdvisoryProjection(
        customer_id=customer_id,
        twin_snapshot_refs=(
            TwinAdvisoryRef(
                id=twin_id,
                entity_ref=f"pkg.crm.customer:{customer_id}",
                status=TwinSnapshotStatus.ACTIVE,
                source_ref="crm:sync",
                updated_at=now,
            ),
        ),
        brain_insight_refs=(
            BrainAdvisoryRef(
                id=brain_id,
                kind=InsightKind.RECOMMENDATION,
                summary="Advisory only",
                advisory=True,
                twin_ref=twin_id,
                updated_at=now,
            ),
        ),
    )
    client = _client(projections=(projection,))
    response = client.get(
        f"/v1/crm/customers/{customer_id}/advisory", headers=_headers()
    )
    assert response.status_code == 200
    body = response.json()["data"]
    assert body["customer_id"] == str(customer_id)
    assert body["execution_authority"] == "none"
    assert body["twin_snapshot_refs"][0]["id"] == str(twin_id)
    assert body["twin_snapshot_refs"][0]["status"] == "active"
    assert body["brain_insight_refs"][0]["id"] == str(brain_id)
    assert body["brain_insight_refs"][0]["advisory"] is True
    assert body["brain_insight_refs"][0]["kind"] == "recommendation"


def test_g327_advisory_default_deny_without_grant() -> None:
    customer_id = uuid4()
    client = _client(
        grant_360=False,
        projections=(
            CustomerAdvisoryProjection(
                customer_id=customer_id,
                twin_snapshot_refs=(),
                brain_insight_refs=(),
            ),
        ),
    )
    response = client.get(
        f"/v1/crm/customers/{customer_id}/advisory", headers=_headers()
    )
    assert response.status_code == 403


def test_g327_brain_execute_remains_forbidden() -> None:
    client = _client()
    twin = client.post(
        "/v1/twin/snapshots",
        headers=_headers(),
        json={
            "entity_ref": "pkg.crm.customer:probe",
            "state": {"ok": True},
            "source_ref": "sensor:g327",
            "reason": "advisory-probe",
            "confidence": 0.7,
        },
    )
    assert twin.status_code == 201
    twin_id = twin.json()["data"]
    published = client.post(
        "/v1/brain/insights",
        headers=_headers(),
        json={
            "kind": "recommendation",
            "summary": "Stay advisory",
            "confidence": 0.6,
            "source_ref": "model:g327",
            "reason": "advisory",
            "twin_ref": twin_id,
        },
    )
    assert published.status_code == 201
    insight_id = published.json()["data"]
    denied = client.post(
        f"/v1/brain/insights/{insight_id}/execute",
        headers=_headers(),
    )
    assert denied.status_code == 403
    assert denied.json()["detail"]["code"] == "BRAIN_EXECUTION_FORBIDDEN"


def test_g327_twin_authorize_remains_forbidden() -> None:
    client = _client()
    created = client.post(
        "/v1/twin/snapshots",
        headers=_headers(),
        json={
            "entity_ref": "pkg.crm.customer:authz",
            "state": {"ok": True},
            "source_ref": "sensor:g327b",
            "reason": "authorize-probe",
            "confidence": 0.8,
        },
    )
    assert created.status_code == 201
    snapshot_id = created.json()["data"]
    denied = client.post(
        f"/v1/twin/snapshots/{snapshot_id}/authorize",
        headers=_headers(),
    )
    assert denied.status_code == 403
    assert denied.json()["detail"]["code"] == "TWIN_EXECUTION_FORBIDDEN"


def test_g327_advisory_not_embedded_in_360_openapi() -> None:
    spec = _client().get("/openapi.json").json()
    advisory_path = "/v1/crm/customers/{customer_id}/advisory"
    assert advisory_path in spec["paths"]
    assert list(spec["paths"][advisory_path].keys()) == ["get"]
    schemas = spec["components"]["schemas"]
    assert schemas["CustomerAdvisoryView"]["additionalProperties"] is False
    assert schemas["CustomerAdvisoryEnvelope"]["additionalProperties"] is False
    view_props = schemas["CustomerAdvisoryView"]["properties"]
    assert view_props["execution_authority"].get("const") == "none" or (
        view_props["execution_authority"].get("enum") == ["none"]
    )
    assert "advisory" not in schemas["Customer360View"]["properties"]
    assert "twin_snapshot_refs" not in schemas["Customer360View"]["properties"]
    assert "brain_insight_refs" not in schemas["Customer360View"]["properties"]
    assert "execution_authority" not in schemas["Customer360View"]["properties"]
