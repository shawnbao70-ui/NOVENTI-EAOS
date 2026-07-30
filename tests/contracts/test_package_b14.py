"""PHX-B14 Package Platform manifest, install and resolve contracts."""

from __future__ import annotations

import json
from pathlib import Path
from uuid import UUID, uuid4

from eaos_platform.package.service import PackageService
from kernel.permission.service import PermissionService
from kernel.shared.context import ExecutionContext, SubjectType
from kernel.shared.errors import ErrorCode

ADMIN_ID = uuid4()
OPERATOR_ID = uuid4()
ROOT = Path(__file__).resolve().parents[2]
SAMPLE_MANIFEST = ROOT / "packages" / "sample_ops" / "manifest.json"


class _AllowAll:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


def _ctx(tenant_id: UUID, subject_id: UUID) -> ExecutionContext:
    return ExecutionContext(
        subject_id=subject_id,
        subject_type=SubjectType.HUMAN,
        correlation_id=str(uuid4()),
        request_time=ExecutionContext.utc_now(),
        tenant_id=tenant_id,
    )


def _services() -> tuple[PermissionService, PackageService]:
    permission = PermissionService(
        grant_administrators={ADMIN_ID},
        principal_eligibility=_AllowAll(),
    )
    return permission, PackageService(permission)


def _grant_package(permission: PermissionService, tenant_id: UUID, subject_id: UUID) -> None:
    admin = _ctx(tenant_id, ADMIN_ID)
    for resource_type, actions in (
        ("package_manifest", {"register", "publish", "read"}),
        ("package_installation", {"install", "disable", "read"}),
        ("package_surface", {"read"}),
        ("package_action", {"resolve"}),
        ("pkg.ops.brief", {"compose", "publish"}),
    ):
        assert permission.grant(
            admin,
            principal_subject_id=subject_id,
            resource_type=resource_type,
            actions=actions,
        ).ok


def _sample_payload() -> dict:
    return json.loads(SAMPLE_MANIFEST.read_text(encoding="utf-8"))


def test_kernel_package_key_rejected() -> None:
    tenant_id = uuid4()
    permission, packages = _services()
    _grant_package(permission, tenant_id, OPERATOR_ID)
    denied = packages.register_manifest(
        _ctx(tenant_id, OPERATOR_ID),
        package_key="kernel.identity.fork",
        version="1.0.0",
        package_type="business",
        surfaces=[{"surface_key": "x", "title": "X"}],
        actions=[
            {
                "action_key": "x.run",
                "resource_type": "pkg.x",
                "permission_action": "run",
            }
        ],
    )
    assert denied.error_code == ErrorCode.PACKAGE_KERNEL_FORK_DENIED
    register_denied = [
        event
        for event in packages.audit_log.list_events()
        if event.action == "Package.RegisterManifest" and event.result == "denied"
    ]
    assert register_denied
    assert register_denied[-1].details.get("error_code") == str(
        ErrorCode.PACKAGE_KERNEL_FORK_DENIED
    )


def test_reserved_resource_type_rejected() -> None:
    tenant_id = uuid4()
    permission, packages = _services()
    _grant_package(permission, tenant_id, OPERATOR_ID)
    denied = packages.register_manifest(
        _ctx(tenant_id, OPERATOR_ID),
        package_key="noventi.bad",
        version="1.0.0",
        package_type="business",
        actions=[
            {
                "action_key": "steal.grant",
                "resource_type": "grant",
                "permission_action": "create",
            }
        ],
    )
    assert denied.error_code == ErrorCode.PACKAGE_KERNEL_FORK_DENIED


def test_sample_ops_register_publish_install_resolve() -> None:
    tenant_id = uuid4()
    permission, packages = _services()
    _grant_package(permission, tenant_id, OPERATOR_ID)
    operator = _ctx(tenant_id, OPERATOR_ID)
    payload = _sample_payload()
    registered = packages.register_manifest(
        operator,
        package_key=payload["package_key"],
        version=payload["version"],
        package_type=payload["package_type"],
        surfaces=payload["surfaces"],
        actions=payload["actions"],
        required_permissions=payload["required_permissions"],
        declared_events=payload["declared_events"],
    )
    assert registered.ok and registered.data is not None
    assert packages.publish_manifest(operator, manifest_id=registered.data).ok
    installed = packages.install_package(operator, manifest_id=registered.data)
    assert installed.ok and installed.data is not None
    surfaces = packages.list_surfaces(operator)
    assert surfaces.ok and surfaces.data is not None
    assert any(item.surface_key == "ops.workbench" for item in surfaces.data)
    resolved = packages.resolve_action(operator, action_key="ops.brief.compose")
    assert resolved.ok and resolved.data is not None
    assert resolved.data.package_key == "noventi.sample.ops"
    assert resolved.data.source == "package_manifest"


def test_unpublished_cannot_install() -> None:
    tenant_id = uuid4()
    permission, packages = _services()
    _grant_package(permission, tenant_id, OPERATOR_ID)
    operator = _ctx(tenant_id, OPERATOR_ID)
    registered = packages.register_manifest(
        operator,
        package_key="noventi.draft",
        version="0.1.0",
        package_type="business",
        surfaces=[{"surface_key": "draft.surface", "title": "Draft"}],
        actions=[
            {
                "action_key": "draft.run",
                "resource_type": "pkg.draft",
                "permission_action": "run",
            }
        ],
    )
    assert registered.data is not None
    denied = packages.install_package(operator, manifest_id=registered.data)
    assert denied.error_code == ErrorCode.PACKAGE_NOT_PUBLISHED


def test_resolve_action_permission_denied_is_audited() -> None:
    tenant_id = uuid4()
    permission, packages = _services()
    admin = _ctx(tenant_id, ADMIN_ID)
    # Resolve catalog only — omit pkg.ops.brief publish (default-deny on action grant).
    for resource_type, actions in (
        ("package_manifest", {"register", "publish", "read"}),
        ("package_installation", {"install", "disable", "read"}),
        ("package_surface", {"read"}),
        ("package_action", {"resolve"}),
        ("pkg.ops.brief", {"compose"}),
        ("pkg.order.flow", {"compose", "create"}),
    ):
        assert permission.grant(
            admin,
            principal_subject_id=OPERATOR_ID,
            resource_type=resource_type,
            actions=actions,
        ).ok
    operator = _ctx(tenant_id, OPERATOR_ID)
    payload = _sample_payload()
    registered = packages.register_manifest(
        operator,
        package_key=payload["package_key"],
        version=payload["version"],
        package_type=payload["package_type"],
        surfaces=payload["surfaces"],
        actions=payload["actions"],
        required_permissions=payload["required_permissions"],
        declared_events=payload["declared_events"],
    )
    assert registered.data is not None
    assert packages.publish_manifest(operator, manifest_id=registered.data).ok
    assert packages.install_package(operator, manifest_id=registered.data).ok

    denied = packages.resolve_action(operator, action_key="ops.brief.publish")
    assert denied.error_code == ErrorCode.PERMISSION_DENIED
    events = [
        event
        for event in packages.audit_log.list_events()
        if event.action == "Package.ResolveAction" and event.result == "denied"
    ]
    assert events
    assert events[-1].details.get("error_code") == ErrorCode.PERMISSION_DENIED


def test_undeclared_action_not_resolvable() -> None:
    tenant_id = uuid4()
    permission, packages = _services()
    _grant_package(permission, tenant_id, OPERATOR_ID)
    operator = _ctx(tenant_id, OPERATOR_ID)
    payload = _sample_payload()
    registered = packages.register_manifest(
        operator,
        package_key=payload["package_key"],
        version=payload["version"],
        package_type=payload["package_type"],
        surfaces=payload["surfaces"],
        actions=payload["actions"],
        required_permissions=payload["required_permissions"],
        declared_events=payload["declared_events"],
    )
    assert registered.data is not None
    assert packages.publish_manifest(operator, manifest_id=registered.data).ok
    assert packages.install_package(operator, manifest_id=registered.data).ok
    missing = packages.resolve_action(operator, action_key="ops.unknown")
    assert missing.error_code == ErrorCode.PACKAGE_ACTION_UNDECLARED


def test_ambiguous_action_key_across_installations_is_denied() -> None:
    tenant_id = uuid4()
    permission, packages = _services()
    _grant_package(permission, tenant_id, OPERATOR_ID)
    operator = _ctx(tenant_id, OPERATOR_ID)
    for package_key in ("noventi.sample.ops.a", "noventi.sample.ops.b"):
        registered = packages.register_manifest(
            operator,
            package_key=package_key,
            version="1.0.0",
            package_type="industry",
            surfaces=[
                {
                    "surface_key": "ops.workbench",
                    "title": "Operations Workbench",
                }
            ],
            actions=[
                {
                    "action_key": "ops.brief.compose",
                    "resource_type": "pkg.ops.brief",
                    "permission_action": "compose",
                    "surface_key": "ops.workbench",
                }
            ],
            required_permissions=[
                {"resource_type": "pkg.ops.brief", "actions": ["compose"]},
            ],
            declared_events=["pkg.ops.brief.composed"],
        )
        assert registered.data is not None
        assert packages.publish_manifest(operator, manifest_id=registered.data).ok
        assert packages.install_package(operator, manifest_id=registered.data).ok
    ambiguous = packages.resolve_action(operator, action_key="ops.brief.compose")
    assert ambiguous.error_code == ErrorCode.PACKAGE_ACTION_AMBIGUOUS


def test_disabled_installation_hides_actions() -> None:
    tenant_id = uuid4()
    permission, packages = _services()
    _grant_package(permission, tenant_id, OPERATOR_ID)
    operator = _ctx(tenant_id, OPERATOR_ID)
    payload = _sample_payload()
    registered = packages.register_manifest(
        operator,
        package_key=payload["package_key"],
        version=payload["version"],
        package_type=payload["package_type"],
        surfaces=payload["surfaces"],
        actions=payload["actions"],
        required_permissions=payload["required_permissions"],
        declared_events=payload["declared_events"],
    )
    assert registered.data is not None
    assert packages.publish_manifest(operator, manifest_id=registered.data).ok
    installed = packages.install_package(operator, manifest_id=registered.data)
    assert installed.data is not None
    assert packages.disable_installation(
        operator,
        installation_id=installed.data,
    ).ok
    missing = packages.resolve_action(operator, action_key="ops.brief.compose")
    assert missing.error_code == ErrorCode.PACKAGE_ACTION_UNDECLARED
