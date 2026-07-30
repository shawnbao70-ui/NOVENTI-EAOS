"""Foundation harden — Package-authoritative Terminal preview + closed DTOs."""

from __future__ import annotations

from uuid import UUID, uuid4

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from api.gateway import create_app
from eaos_platform.package.service import PackageService
from kernel.permission.service import PermissionService
from kernel.shared.context import ExecutionContext, SubjectType
from kernel.workflow.service import WorkflowService
from smart_terminal.service import SmartTerminalService

ADMIN = uuid4()
OPERATOR = uuid4()
TENANT = uuid4()


class _AllowAll:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


def _headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(OPERATOR),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": str(uuid4()),
    }


def _admin() -> ExecutionContext:
    return ExecutionContext(
        subject_id=ADMIN,
        subject_type=SubjectType.HUMAN,
        tenant_id=TENANT,
        correlation_id=str(uuid4()),
        request_time=ExecutionContext.utc_now(),
    )


@pytest.fixture()
def gateway() -> TestClient:
    permission = PermissionService(
        grant_administrators={ADMIN},
        principal_eligibility=_AllowAll(),
    )
    workflow = WorkflowService(permission, definition_administrators={ADMIN})
    terminal = SmartTerminalService(permission, workflow)
    packages = PackageService(permission)
    admin = _admin()
    for resource_type, actions in (
        ("terminal_session", {"open", "read", "close"}),
        ("terminal_intent", {"compose", "read"}),
        ("terminal_preview", {"build", "read"}),
        ("terminal_approval", {"present", "request"}),
        ("terminal_commit", {"execute"}),
        ("package_manifest", {"register", "publish", "read"}),
        ("package_installation", {"install", "disable", "read"}),
        ("package_surface", {"read"}),
        ("package_action", {"resolve"}),
        ("pkg.ops.brief", {"compose", "publish"}),
    ):
        assert permission.grant(
            admin,
            principal_subject_id=OPERATOR,
            resource_type=resource_type,
            actions=actions,
        ).ok
    operator = ExecutionContext(
        subject_id=OPERATOR,
        subject_type=SubjectType.HUMAN,
        tenant_id=TENANT,
        correlation_id=str(uuid4()),
        request_time=ExecutionContext.utc_now(),
    )
    registered = packages.register_manifest(
        operator,
        package_key="noventi.sample.ops",
        version="1.0.0",
        package_type="industry",
        surfaces=[
            {"surface_key": "ops.workbench", "title": "Operations Workbench"},
        ],
        actions=[
            {
                "action_key": "ops.brief.publish",
                "resource_type": "pkg.ops.brief",
                "permission_action": "publish",
                "high_impact": True,
                "surface_key": "ops.workbench",
            }
        ],
        required_permissions=[
            {"resource_type": "pkg.ops.brief", "actions": ["publish"]},
        ],
        declared_events=["pkg.ops.brief.published"],
    )
    assert registered.data is not None
    assert packages.publish_manifest(operator, manifest_id=registered.data).ok
    assert packages.install_package(operator, manifest_id=registered.data).ok
    return TestClient(
        create_app(
            permission_service=permission,
            workflow_service=workflow,
            terminal_service=terminal,
            package_service=packages,
        )
    )


def test_preview_high_impact_cannot_be_downgraded_by_client(gateway: TestClient) -> None:
    opened = gateway.post(
        "/v1/terminal/sessions",
        headers=_headers(),
        json={"device_trust": "trusted"},
    )
    assert opened.status_code == 201
    session_id = opened.json()["data"]
    intent = gateway.post(
        "/v1/terminal/intents",
        headers=_headers(),
        json={"terminal_session_id": session_id, "text": "Publish brief"},
    )
    assert intent.status_code == 201
    preview = gateway.post(
        "/v1/terminal/previews",
        headers=_headers(),
        json={
            "intent_id": intent.json()["data"],
            "action": "ops.brief.publish",
            "resource_ref": "brief:1",
            "plan_version": "v1",
            "scope": "tenant",
            "impact_summary": "Publish ops brief",
            "high_impact": False,
        },
    )
    assert preview.status_code == 201
    loaded = gateway.get(
        f"/v1/terminal/previews/{preview.json()['data']}",
        headers=_headers(),
    )
    assert loaded.status_code == 200
    assert loaded.json()["high_impact"] is True


def test_closed_preview_dto_rejects_unknown_fields(gateway: TestClient) -> None:
    opened = gateway.post(
        "/v1/terminal/sessions",
        headers=_headers(),
        json={"device_trust": "trusted"},
    )
    intent = gateway.post(
        "/v1/terminal/intents",
        headers=_headers(),
        json={"terminal_session_id": opened.json()["data"], "text": "x"},
    )
    response = gateway.post(
        "/v1/terminal/previews",
        headers=_headers(),
        json={
            "intent_id": intent.json()["data"],
            "action": "ops.brief.publish",
            "resource_ref": "brief:1",
            "plan_version": "v1",
            "scope": "tenant",
            "impact_summary": "Publish ops brief",
            "extra_field": "nope",
        },
    )
    assert response.status_code == 422


def test_sql_store_requires_database_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EAOS_GATEWAY_STORE", "sql")
    monkeypatch.delenv("EAOS_DATABASE_URL", raising=False)
    with pytest.raises(RuntimeError, match="EAOS_DATABASE_URL"):
        create_app()


def test_sql_store_health_exposes_gateway_store(monkeypatch: pytest.MonkeyPatch) -> None:
    """Positive composition smoke: valid URL + sql mode → health.gateway_store=sql.

    Engine is constructed lazily; no live PostgreSQL required for /v1/health.
    """

    monkeypatch.setenv("EAOS_GATEWAY_STORE", "sql")
    monkeypatch.setenv(
        "EAOS_DATABASE_URL",
        "postgresql+psycopg://eaos:eaos@127.0.0.1:5432/eaos_foundation_smoke",
    )
    client = TestClient(create_app())
    response = client.get("/v1/health")
    assert response.status_code == 200
    assert response.json()["data"]["gateway_store"] == "sql"


def test_sql_composition_wires_all_domain_slots(monkeypatch: pytest.MonkeyPatch) -> None:
    from api.gateway.sql_composition import SqlGatewayServices, compose_sql_gateway_services

    monkeypatch.setenv("EAOS_GATEWAY_STORE", "sql")
    monkeypatch.setenv(
        "EAOS_DATABASE_URL",
        "postgresql+psycopg://eaos:eaos@127.0.0.1:5432/eaos_foundation_smoke",
    )
    services = compose_sql_gateway_services()
    assert isinstance(services, SqlGatewayServices)
    for field in SqlGatewayServices.__dataclass_fields__:
        assert getattr(services, field) is not None, field


def test_permission_status_lists_role_grant_auto_write_surface() -> None:
    client = TestClient(create_app())
    surfaces = client.get("/v1/permission/status").json()["data"]["supported_surfaces"]
    assert "role_catalog" in surfaces
    assert "role_grant_auto_write" in surfaces
