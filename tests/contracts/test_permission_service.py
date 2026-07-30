"""Permission Kernel contract tests — P-01..P-06."""

from __future__ import annotations

from datetime import timedelta
from uuid import UUID, uuid4

from kernel.permission.models import PermissionEffect, Resource
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


def test_p01_default_deny_without_grant() -> None:
    tenant_id = uuid4()
    service = _service(grant_administrators={GRANT_ADMIN_ID})
    decision = service.evaluate(
        _ctx(tenant_id),
        principal_subject_id=uuid4(),
        action="read",
        resource=Resource(tenant_id=tenant_id, resource_type="document"),
    )
    assert decision.ok and decision.data is not None
    assert decision.data.effect == PermissionEffect.DENY
    assert decision.data.reason_code == ErrorCode.PERMISSION_DENIED


def test_p02_grant_allows_matching_action() -> None:
    tenant_id = uuid4()
    principal_id = uuid4()
    service = _service(grant_administrators={GRANT_ADMIN_ID})
    ctx = _ctx(tenant_id)
    grant = service.grant(
        ctx,
        principal_subject_id=principal_id,
        resource_type="document",
        actions={"read", "write"},
    )
    assert grant.ok and grant.audit_id is not None

    decision = service.evaluate(
        ctx,
        principal_subject_id=principal_id,
        action="read",
        resource=Resource(tenant_id=tenant_id, resource_type="document"),
    )
    assert decision.ok and decision.data is not None
    assert decision.data.effect == PermissionEffect.ALLOW
    assert decision.data.policy_version == service.POLICY_VERSION


def test_p03_revoke_restores_default_deny() -> None:
    tenant_id = uuid4()
    principal_id = uuid4()
    service = _service(grant_administrators={GRANT_ADMIN_ID})
    ctx = _ctx(tenant_id)
    grant = service.grant(
        ctx,
        principal_subject_id=principal_id,
        resource_type="record",
        actions={"read"},
    )
    assert grant.data is not None
    assert service.revoke(
        ctx,
        grant_id=grant.data,
        reason="removed",
        expected_version=1,
    ).ok

    decision = service.evaluate(
        ctx,
        principal_subject_id=principal_id,
        action="read",
        resource=Resource(tenant_id=tenant_id, resource_type="record"),
    )
    assert decision.data is not None
    assert decision.data.effect == PermissionEffect.DENY


def test_p04_explain_returns_reason_without_secret() -> None:
    tenant_id = uuid4()
    service = _service(
        grant_administrators={GRANT_ADMIN_ID},
        decision_auditors={GRANT_ADMIN_ID},
    )
    ctx = _ctx(tenant_id)
    decision = service.evaluate(
        ctx,
        principal_subject_id=uuid4(),
        action="approve",
        resource=Resource(tenant_id=tenant_id, resource_type="invoice"),
    )
    assert decision.data is not None
    explanation = service.explain(ctx, decision_id=decision.data.id)
    assert explanation.ok and explanation.data is not None
    assert explanation.data["reason_code"] == ErrorCode.PERMISSION_DENIED
    assert set(explanation.data) == {"effect", "reason_code", "policy_version"}


def test_p05_ai_tool_call_requires_explicit_grant() -> None:
    tenant_id = uuid4()
    ai_subject_id = uuid4()
    service = _service(grant_administrators={GRANT_ADMIN_ID})
    ctx = _ctx(tenant_id)
    denied = service.evaluate(
        ctx,
        principal_subject_id=ai_subject_id,
        action="invoke_tool",
        resource=Resource(tenant_id=tenant_id, resource_type="tool"),
    )
    assert denied.data is not None
    assert denied.data.effect == PermissionEffect.DENY

    assert service.grant(
        ctx,
        principal_subject_id=ai_subject_id,
        resource_type="tool",
        actions={"invoke_tool"},
    ).ok
    allowed = service.evaluate(
        ctx,
        principal_subject_id=ai_subject_id,
        action="invoke_tool",
        resource=Resource(tenant_id=tenant_id, resource_type="tool"),
    )
    assert allowed.data is not None
    assert allowed.data.effect == PermissionEffect.ALLOW


def test_p06_decision_is_recorded_and_audited() -> None:
    tenant_id = uuid4()
    service = _service(grant_administrators={GRANT_ADMIN_ID})
    result = service.evaluate(
        _ctx(tenant_id),
        principal_subject_id=uuid4(),
        action="read",
        resource=Resource(tenant_id=tenant_id, resource_type="document"),
    )
    assert result.ok and result.data is not None
    assert service._repo.get_decision(result.data.id) is not None
    assert result.audit_id is not None


def test_cross_tenant_evaluation_fails_closed() -> None:
    service = _service(grant_administrators={GRANT_ADMIN_ID})
    tenant_a = uuid4()
    result = service.evaluate(
        _ctx(tenant_a),
        principal_subject_id=uuid4(),
        action="read",
        resource=Resource(tenant_id=uuid4(), resource_type="document"),
    )
    assert not result.ok
    assert result.error_code == ErrorCode.PERMISSION_CROSS_TENANT_FORBIDDEN


def test_expired_grant_is_rejected_at_creation() -> None:
    tenant_id = uuid4()
    result = _service(grant_administrators={GRANT_ADMIN_ID}).grant(
        _ctx(tenant_id),
        principal_subject_id=uuid4(),
        resource_type="document",
        actions={"read"},
        expires_at=ExecutionContext.utc_now() - timedelta(seconds=1),
    )
    assert not result.ok
    assert result.error_code == ErrorCode.PERMISSION_GRANT_EXPIRED


def test_untrusted_subject_cannot_self_grant() -> None:
    tenant_id = uuid4()
    service = _service(grant_administrators={GRANT_ADMIN_ID})
    untrusted_subject = uuid4()
    result = service.grant(
        _ctx(tenant_id, subject_id=untrusted_subject),
        principal_subject_id=untrusted_subject,
        resource_type="document",
        actions={"write"},
    )
    assert not result.ok
    assert result.error_code == ErrorCode.PERMISSION_DENIED


def test_unresolved_grant_condition_fails_closed() -> None:
    tenant_id = uuid4()
    principal_id = uuid4()
    service = _service(grant_administrators={GRANT_ADMIN_ID})
    ctx = _ctx(tenant_id)
    assert service.grant(
        ctx,
        principal_subject_id=principal_id,
        resource_type="document",
        actions={"read"},
        conditions_ref="conditions/business-hours",
    ).ok

    decision = service.evaluate(
        ctx,
        principal_subject_id=principal_id,
        action="read",
        resource=Resource(tenant_id=tenant_id, resource_type="document"),
    )

    assert decision.data is not None
    assert decision.data.effect == PermissionEffect.DENY
    assert (
        decision.data.reason_code
        == ErrorCode.PERMISSION_CONDITION_UNRESOLVED.value
    )


def test_revoke_requires_current_version() -> None:
    tenant_id = uuid4()
    service = _service(grant_administrators={GRANT_ADMIN_ID})
    granted = service.grant(
        _ctx(tenant_id),
        principal_subject_id=uuid4(),
        resource_type="document",
        actions={"read"},
    )
    assert granted.data is not None

    stale = service.revoke(
        _ctx(tenant_id),
        grant_id=granted.data,
        reason="stale",
        expected_version=2,
    )

    assert stale.error_code == ErrorCode.PERMISSION_VERSION_CONFLICT


def test_explain_is_self_or_auditor_only() -> None:
    tenant_id = uuid4()
    principal_id = uuid4()
    stranger = uuid4()
    service = _service(grant_administrators={GRANT_ADMIN_ID})
    decision = service.evaluate(
        _ctx(tenant_id),
        principal_subject_id=principal_id,
        action="read",
        resource=Resource(tenant_id=tenant_id, resource_type="document"),
    )
    assert decision.data is not None

    denied = service.explain(
        _ctx(tenant_id, subject_id=stranger),
        decision_id=decision.data.id,
    )
    allowed = service.explain(
        _ctx(tenant_id, subject_id=principal_id),
        decision_id=decision.data.id,
    )

    assert denied.error_code == ErrorCode.PERMISSION_DENIED
    assert allowed.ok


def test_list_effective_is_self_or_auditor_only() -> None:
    tenant_id = uuid4()
    principal_id = uuid4()
    stranger = uuid4()
    service = _service(grant_administrators={GRANT_ADMIN_ID})
    assert service.grant(
        _ctx(tenant_id),
        principal_subject_id=principal_id,
        resource_type="document",
        actions={"read"},
    ).ok

    denied = service.list_effective(
        _ctx(tenant_id, subject_id=stranger),
        principal_subject_id=principal_id,
    )
    allowed = service.list_effective(
        _ctx(tenant_id, subject_id=principal_id),
        principal_subject_id=principal_id,
    )

    assert denied.error_code == ErrorCode.PERMISSION_DENIED
    assert allowed.ok and allowed.data is not None
    assert len(allowed.data) == 1


def test_ineligible_principal_fails_closed_on_grant_and_evaluate() -> None:
    tenant_id = uuid4()
    service = PermissionService(grant_administrators={GRANT_ADMIN_ID})
    grant = service.grant(
        _ctx(tenant_id),
        principal_subject_id=uuid4(),
        resource_type="document",
        actions={"read"},
    )
    decision = service.evaluate(
        _ctx(tenant_id),
        principal_subject_id=uuid4(),
        action="read",
        resource=Resource(tenant_id=tenant_id, resource_type="document"),
    )

    assert grant.error_code == ErrorCode.PERMISSION_PRINCIPAL_INELIGIBLE
    assert decision.error_code == ErrorCode.PERMISSION_PRINCIPAL_INELIGIBLE
