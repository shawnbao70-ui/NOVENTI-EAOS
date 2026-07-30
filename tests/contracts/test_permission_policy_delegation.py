"""PHX-K08 Policy, Scope and Delegation contract tests."""

from __future__ import annotations

from uuid import UUID, uuid4

from kernel.permission.models import (
    PermissionEffect,
    PolicyRule,
    Resource,
    ScopeLevel,
)
from kernel.permission.service import PermissionService
from kernel.shared.context import ExecutionContext, SubjectType
from kernel.shared.errors import ErrorCode

GRANT_ADMIN_ID = uuid4()


class _AllowPrincipalEligibility:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


def _service(**kwargs) -> PermissionService:
    return PermissionService(
        principal_eligibility=_AllowPrincipalEligibility(),
        grant_administrators={GRANT_ADMIN_ID},
        **kwargs,
    )


def _ctx(tenant_id: UUID, *, subject_id: UUID = GRANT_ADMIN_ID) -> ExecutionContext:
    return ExecutionContext(
        subject_id=subject_id,
        subject_type=SubjectType.SERVICE,
        correlation_id=str(uuid4()),
        request_time=ExecutionContext.utc_now(),
        tenant_id=tenant_id,
    )


def test_explicit_deny_policy_overrides_allow_grant() -> None:
    tenant_id = uuid4()
    principal_id = uuid4()
    service = _service()
    ctx = _ctx(tenant_id)
    assert service.grant(
        ctx,
        principal_subject_id=principal_id,
        resource_type="document",
        actions={"read"},
        scope_level=ScopeLevel.TENANT,
    ).ok
    created = service.create_policy(
        ctx,
        name="deny-read",
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
    assert created.data is not None
    assert service.activate_policy(
        ctx,
        policy_id=created.data,
        expected_version=1,
    ).ok

    decision = service.evaluate(
        ctx,
        principal_subject_id=principal_id,
        action="read",
        resource=Resource(tenant_id=tenant_id, resource_type="document"),
    )

    assert decision.data is not None
    assert decision.data.effect == PermissionEffect.DENY
    assert decision.data.reason_code == ErrorCode.PERMISSION_DENIED.value
    assert created.data in (decision.data.evidence.matched_policy_ids if decision.data.evidence else [])


def test_draft_policy_does_not_authorize() -> None:
    tenant_id = uuid4()
    principal_id = uuid4()
    service = _service()
    ctx = _ctx(tenant_id)
    created = service.create_policy(
        ctx,
        name="allow-write",
        policy_version="1",
        rules=[
            PolicyRule(
                id=uuid4(),
                effect=PermissionEffect.ALLOW,
                resource_type="document",
                actions=frozenset({"write"}),
                scope_level=ScopeLevel.TENANT,
            )
        ],
    )
    assert created.ok

    decision = service.evaluate(
        ctx,
        principal_subject_id=principal_id,
        action="write",
        resource=Resource(tenant_id=tenant_id, resource_type="document"),
    )

    assert decision.data is not None
    assert decision.data.effect == PermissionEffect.DENY


def test_delegation_narrows_and_follows_parent_chain() -> None:
    tenant_id = uuid4()
    parent_principal = uuid4()
    child_principal = uuid4()
    service = _service()
    admin_ctx = _ctx(tenant_id)
    parent = service.grant(
        admin_ctx,
        principal_subject_id=parent_principal,
        resource_type="document",
        actions={"read", "write"},
        scope_level=ScopeLevel.TENANT,
        delegable=True,
        remaining_depth=2,
    )
    assert parent.data is not None

    delegated = service.delegate(
        _ctx(tenant_id, subject_id=parent_principal),
        parent_grant_id=parent.data,
        to_principal_subject_id=child_principal,
        actions={"read"},
        remaining_depth=1,
        delegable=True,
    )
    assert delegated.ok and delegated.data is not None

    allowed = service.evaluate(
        admin_ctx,
        principal_subject_id=child_principal,
        action="read",
        resource=Resource(tenant_id=tenant_id, resource_type="document"),
    )
    denied_write = service.evaluate(
        admin_ctx,
        principal_subject_id=child_principal,
        action="write",
        resource=Resource(tenant_id=tenant_id, resource_type="document"),
    )
    assert allowed.data is not None
    assert allowed.data.effect == PermissionEffect.ALLOW
    assert denied_write.data is not None
    assert denied_write.data.effect == PermissionEffect.DENY

    assert service.revoke(
        admin_ctx,
        grant_id=parent.data,
        reason="parent revoked",
        expected_version=1,
    ).ok
    after_revoke = service.evaluate(
        admin_ctx,
        principal_subject_id=child_principal,
        action="read",
        resource=Resource(tenant_id=tenant_id, resource_type="document"),
    )
    assert after_revoke.data is not None
    assert after_revoke.data.effect == PermissionEffect.DENY


def test_delegation_cannot_expand_actions_or_scope() -> None:
    tenant_id = uuid4()
    parent_principal = uuid4()
    service = _service()
    parent = service.grant(
        _ctx(tenant_id),
        principal_subject_id=parent_principal,
        resource_type="document",
        actions={"read"},
        scope_level=ScopeLevel.RESOURCE,
        resource_id=uuid4(),
        delegable=True,
        remaining_depth=1,
    )
    assert parent.data is not None

    expanded = service.delegate(
        _ctx(tenant_id, subject_id=parent_principal),
        parent_grant_id=parent.data,
        to_principal_subject_id=uuid4(),
        actions={"read", "write"},
    )
    broader_scope = service.delegate(
        _ctx(tenant_id, subject_id=parent_principal),
        parent_grant_id=parent.data,
        to_principal_subject_id=uuid4(),
        scope_level=ScopeLevel.TENANT,
    )

    assert expanded.error_code == ErrorCode.PERMISSION_DELEGATION_FORBIDDEN
    assert broader_scope.error_code == ErrorCode.PERMISSION_DELEGATION_FORBIDDEN
