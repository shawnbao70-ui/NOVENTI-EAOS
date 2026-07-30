"""PHX-G83 opt-in context roles evaluate grant map (Kernel) contracts."""

from __future__ import annotations

from uuid import UUID, uuid4

from kernel.permission.models import (
    PermissionEffect,
    PolicyRule,
    Resource,
    ScopeLevel,
)
from kernel.permission.role_grant_map import (
    configure_permission_role_grant_map,
    parse_role_grant_map,
    reset_permission_role_grant_map,
)
from kernel.permission.service import PermissionService
from kernel.shared.context import ExecutionContext, SubjectType
from kernel.shared.errors import ErrorCode

GRANT_ADMIN = uuid4()


class _AllowPrincipalEligibility:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


def _service() -> PermissionService:
    return PermissionService(
        grant_administrators={GRANT_ADMIN},
        decision_auditors={GRANT_ADMIN},
        principal_eligibility=_AllowPrincipalEligibility(),
    )


def _ctx(
    tenant_id: UUID,
    *,
    subject_id: UUID,
    roles: tuple[str, ...] = (),
) -> ExecutionContext:
    return ExecutionContext(
        subject_id=subject_id,
        subject_type=SubjectType.HUMAN,
        correlation_id=str(uuid4()),
        request_time=ExecutionContext.utc_now(),
        tenant_id=tenant_id,
        roles=roles,
    )


def setup_function() -> None:
    reset_permission_role_grant_map()


def teardown_function() -> None:
    reset_permission_role_grant_map()


def test_parse_role_grant_map() -> None:
    mapping = parse_role_grant_map(
        "operator=document:read,admin=document:read|document:write"
    )
    assert mapping["operator"] == frozenset({("document", "read")})
    assert mapping["admin"] == frozenset(
        {("document", "read"), ("document", "write")}
    )


def test_map_off_ignores_context_roles() -> None:
    tenant_id = uuid4()
    principal = uuid4()
    service = _service()
    result = service.evaluate(
        _ctx(tenant_id, subject_id=principal, roles=("operator",)),
        principal_subject_id=principal,
        action="read",
        resource=Resource(tenant_id=tenant_id, resource_type="document"),
    )
    assert result.ok and result.data is not None
    assert result.data.effect == PermissionEffect.DENY
    assert result.data.reason_code == ErrorCode.PERMISSION_DENIED.value


def test_role_map_allows_without_grant() -> None:
    configure_permission_role_grant_map(
        {"operator": frozenset({("document", "read")})}
    )
    tenant_id = uuid4()
    principal = uuid4()
    service = _service()
    result = service.evaluate(
        _ctx(tenant_id, subject_id=principal, roles=("operator", "viewer")),
        principal_subject_id=principal,
        action="read",
        resource=Resource(tenant_id=tenant_id, resource_type="document"),
    )
    assert result.ok and result.data is not None
    assert result.data.effect == PermissionEffect.ALLOW
    assert result.data.reason_code == "MATCHED_CONTEXT_ROLE"
    assert result.data.evidence is not None
    assert result.data.evidence.matched_roles == ["operator"]

    explained = service.explain(
        _ctx(tenant_id, subject_id=principal, roles=("operator",)),
        decision_id=result.data.id,
    )
    assert explained.ok and explained.data is not None
    assert explained.data["matched_roles"] == "operator"


def test_deny_policy_overrides_role_allow() -> None:
    configure_permission_role_grant_map(
        {"operator": frozenset({("document", "read")})}
    )
    tenant_id = uuid4()
    principal = uuid4()
    service = _service()
    admin_ctx = _ctx(tenant_id, subject_id=GRANT_ADMIN)
    created = service.create_policy(
        admin_ctx,
        name="deny-doc-read",
        policy_version="1",
        rules=[
            PolicyRule(
                id=uuid4(),
                effect=PermissionEffect.DENY,
                resource_type="document",
                actions=frozenset({"read"}),
                scope_level=ScopeLevel.TENANT,
            )
        ],
    )
    assert created.ok and created.data is not None
    activated = service.activate_policy(
        admin_ctx, policy_id=created.data, expected_version=1
    )
    assert activated.ok

    result = service.evaluate(
        _ctx(tenant_id, subject_id=principal, roles=("operator",)),
        principal_subject_id=principal,
        action="read",
        resource=Resource(tenant_id=tenant_id, resource_type="document"),
    )
    assert result.ok and result.data is not None
    assert result.data.effect == PermissionEffect.DENY
    assert result.data.reason_code == ErrorCode.PERMISSION_DENIED.value


def test_empty_roles_cannot_use_map() -> None:
    configure_permission_role_grant_map(
        {"operator": frozenset({("document", "read")})}
    )
    tenant_id = uuid4()
    principal = uuid4()
    service = _service()
    result = service.evaluate(
        _ctx(tenant_id, subject_id=principal, roles=()),
        principal_subject_id=principal,
        action="read",
        resource=Resource(tenant_id=tenant_id, resource_type="document"),
    )
    assert result.ok and result.data is not None
    assert result.data.effect == PermissionEffect.DENY
