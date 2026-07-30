"""PHX-G39 Terminal Extension Host contracts."""

from __future__ import annotations

from uuid import UUID, uuid4

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from api.gateway import create_app
from kernel.permission.service import PermissionService
from kernel.shared.context import ExecutionContext, SubjectType
from kernel.shared.errors import ErrorCode
from kernel.workflow.service import WorkflowService
from smart_terminal.service import SmartTerminalService

ADMIN = uuid4()
ACTOR = uuid4()
TENANT = uuid4()


class _AllowAll:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


def _ctx() -> ExecutionContext:
    return ExecutionContext(
        subject_id=ACTOR,
        subject_type=SubjectType.HUMAN,
        tenant_id=TENANT,
        correlation_id=str(uuid4()),
        request_time=ExecutionContext.utc_now(),
    )


def _services() -> SmartTerminalService:
    permission = PermissionService(
        grant_administrators={ADMIN},
        principal_eligibility=_AllowAll(),
    )
    admin = ExecutionContext(
        subject_id=ADMIN,
        subject_type=SubjectType.HUMAN,
        tenant_id=TENANT,
        correlation_id=str(uuid4()),
        request_time=ExecutionContext.utc_now(),
    )
    assert permission.grant(
        admin,
        principal_subject_id=ACTOR,
        resource_type="terminal_extension",
        actions={"register", "activate", "revoke", "read", "invoke"},
    ).ok
    workflow = WorkflowService(permission)
    return SmartTerminalService(permission, workflow)


def test_unsigned_cannot_activate_and_forbidden_caps() -> None:
    terminal = _services()
    ctx = _ctx()
    denied = terminal.register_extension(
        ctx,
        extension_key="noventi.bad",
        version="1.0.0",
        declared_capabilities=["hide_approval"],
        declared_actions=["panel.render"],
        allowed_surfaces=["extensions"],
        data_scope="tenant.demo",
    )
    assert denied.error_code == ErrorCode.TERMINAL_EXTENSION_SANDBOX_DENIED
    register_denied = [
        event
        for event in terminal.audit_log.list_events()
        if event.action == "Terminal.RegisterExtension" and event.result == "denied"
    ]
    assert register_denied
    assert register_denied[-1].details.get("error_code") == str(
        ErrorCode.TERMINAL_EXTENSION_SANDBOX_DENIED
    )

    stranger = ExecutionContext(
        subject_id=uuid4(),
        subject_type=SubjectType.HUMAN,
        tenant_id=TENANT,
        correlation_id=str(uuid4()),
        request_time=ExecutionContext.utc_now(),
    )
    listed = terminal.list_extensions(stranger)
    assert listed.error_code == ErrorCode.PERMISSION_DENIED
    list_denied = [
        event
        for event in terminal.audit_log.list_events()
        if event.action == "Terminal.ListExtensions" and event.result == "denied"
    ]
    assert list_denied
    assert list_denied[-1].details.get("error_code") == str(ErrorCode.PERMISSION_DENIED)

    created = terminal.register_extension(
        ctx,
        extension_key="noventi.unsigned",
        version="1.0.0",
        declared_actions=["panel.render"],
        allowed_surfaces=["extensions"],
        data_scope="tenant.demo",
    )
    assert created.data is not None
    unsigned = terminal.activate_extension(ctx, extension_id=created.data)
    assert unsigned.error_code == ErrorCode.TERMINAL_EXTENSION_UNSIGNED
    activate_denied = [
        event
        for event in terminal.audit_log.list_events()
        if event.action == "Terminal.ActivateExtension" and event.result == "denied"
    ]
    assert activate_denied
    assert activate_denied[-1].details.get("error_code") == str(
        ErrorCode.TERMINAL_EXTENSION_UNSIGNED
    )


def test_activate_invoke_revoke_lifecycle() -> None:
    terminal = _services()
    ctx = _ctx()
    created = terminal.register_extension(
        ctx,
        extension_key="noventi.panel",
        version="1.0.0",
        signature_ref="sig:ext:1",
        declared_actions=["panel.render"],
        allowed_surfaces=["extensions"],
        data_scope="tenant.demo",
    )
    assert created.data is not None
    assert terminal.activate_extension(ctx, extension_id=created.data).ok
    invoked = terminal.invoke_extension_action(
        ctx,
        extension_id=created.data,
        action="panel.render",
        surface="extensions",
    )
    assert invoked.ok and invoked.data is not None
    assert invoked.data["executed"] is False
    undeclared = terminal.invoke_extension_action(
        ctx,
        extension_id=created.data,
        action="shell.hide_approval",
        surface="extensions",
    )
    assert undeclared.error_code == ErrorCode.TERMINAL_EXTENSION_SANDBOX_DENIED
    assert terminal.revoke_extension(ctx, extension_id=created.data).ok


def test_gateway_extension_routes() -> None:
    permission = PermissionService(
        grant_administrators={ADMIN},
        principal_eligibility=_AllowAll(),
    )
    admin = ExecutionContext(
        subject_id=ADMIN,
        subject_type=SubjectType.HUMAN,
        tenant_id=TENANT,
        correlation_id=str(uuid4()),
        request_time=ExecutionContext.utc_now(),
    )
    assert permission.grant(
        admin,
        principal_subject_id=ACTOR,
        resource_type="terminal_extension",
        actions={"register", "activate", "revoke", "read", "invoke"},
    ).ok
    terminal = SmartTerminalService(permission, WorkflowService(permission))
    client = TestClient(
        create_app(permission_service=permission, terminal_service=terminal)
    )
    headers = {
        "X-EAOS-Subject-Id": str(ACTOR),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": str(uuid4()),
    }
    created = client.post(
        "/v1/terminal/extensions",
        headers=headers,
        json={
            "extension_key": "noventi.http.ext",
            "version": "1.0.0",
            "signature_ref": "sig:http",
            "declared_actions": ["panel.render"],
            "allowed_surfaces": ["extensions"],
            "data_scope": "tenant.demo",
        },
    )
    assert created.status_code == 201
    extension_id = created.json()["data"]
    assert (
        client.post(
            f"/v1/terminal/extensions/{extension_id}/activate",
            headers=headers,
        ).status_code
        == 200
    )
    listed = client.get("/v1/terminal/extensions", headers=headers)
    assert listed.status_code == 200
    assert len(listed.json()["data"]) == 1
