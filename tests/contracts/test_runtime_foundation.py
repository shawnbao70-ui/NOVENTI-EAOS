"""PHX-005 Runtime Foundation contracts R-01 through R-10."""

from __future__ import annotations

import json
from dataclasses import replace
from datetime import timezone
from uuid import UUID, uuid4

import pytest

from kernel.identity.models import SubjectKind
from kernel.identity.service import IdentityService
from kernel.permission.models import PermissionEffect, Resource
from kernel.permission.service import PermissionService
from kernel.shared.context import ExecutionContext, SubjectType
from kernel.shared.errors import ErrorCode, KernelError
from runtime import (
    ContextPropagator,
    ContextSnapshot,
    InboundContextBuilder,
    InboundContextSpec,
    ObservabilityBinding,
    PropagationOverrides,
    RuntimeExecutor,
)


class _AllowAllPrincipalEligibility:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


def _context(**changes) -> ExecutionContext:
    context = ExecutionContext(
        subject_id=uuid4(),
        subject_type=SubjectType.SERVICE,
        correlation_id=str(uuid4()),
        request_time=ExecutionContext.utc_now(),
        tenant_id=uuid4(),
    )
    return replace(context, **changes)


def _inbound(**changes) -> InboundContextSpec:
    values = {
        "subject_id": str(uuid4()),
        "subject_type": "service",
        "correlation_id": str(uuid4()),
        "request_time": ExecutionContext.utc_now().isoformat(),
        "tenant_id": str(uuid4()),
    }
    values.update(changes)
    return InboundContextSpec(**values)


def test_r01_inbound_tenant_data_plane_requires_tenant() -> None:
    with pytest.raises(KernelError) as captured:
        InboundContextBuilder.build(_inbound(tenant_id=None))
    assert captured.value.code == ErrorCode.CTX_MISSING_TENANT


def test_inbound_missing_subject_uses_stable_context_error() -> None:
    with pytest.raises(KernelError) as captured:
        InboundContextBuilder.build(_inbound(subject_id=None))
    assert captured.value.code == ErrorCode.CTX_MISSING_SUBJECT


def test_r02_inbound_platform_governance_allows_no_tenant() -> None:
    context = InboundContextBuilder.build(
        _inbound(tenant_id=None, platform_scope=True),
        tenant_data_plane=False,
    )
    assert context.platform_scope
    assert context.tenant_id is None


@pytest.mark.parametrize(
    "overrides",
    [
        PropagationOverrides(correlation_id="replacement"),
        PropagationOverrides(tenant_id=uuid4()),
        PropagationOverrides(subject_id=uuid4()),
        PropagationOverrides(subject_type=SubjectType.HUMAN),
        PropagationOverrides(platform_scope=True),
    ],
)
def test_r03_propagation_rejects_security_context_changes(
    overrides: PropagationOverrides,
) -> None:
    with pytest.raises(KernelError) as captured:
        ContextPropagator.propagate(_context(), overrides=overrides)
    assert captured.value.code == ErrorCode.RT_PROPAGATION_VIOLATION


def test_r04_propagation_supplements_non_security_fields() -> None:
    parent = _context()
    propagated = ContextPropagator.propagate(
        parent,
        overrides=PropagationOverrides(
            package_id="finance",
            locale="zh-CN",
            trace_id="trace-1",
            approval_ref="approval-1",
        ),
    )
    assert propagated.subject_id == parent.subject_id
    assert propagated.tenant_id == parent.tenant_id
    assert propagated.correlation_id == parent.correlation_id
    assert propagated.package_id == "finance"
    assert propagated.trace_id == "trace-1"


def test_r05_snapshot_json_round_trip_preserves_all_fields() -> None:
    context = _context(
        session_id=uuid4(),
        package_id="finance",
        locale="zh-CN",
        trace_id="trace-1",
        approval_ref="approval-1",
    )
    snapshot = ContextSnapshot.capture(context)
    json.loads(snapshot.serialized_json)
    restored = snapshot.restore()
    assert restored == context
    assert restored.request_time.utcoffset() == timezone.utc.utcoffset(None)


def test_r06_snapshot_rejects_unknown_version_and_fields() -> None:
    payload = ContextSnapshot.capture(_context()).to_dict()
    payload["version"] = 2
    payload["unexpected"] = "value"
    with pytest.raises(KernelError) as captured:
        ContextSnapshot(json.dumps(payload)).restore()
    assert captured.value.code == ErrorCode.RT_SNAPSHOT_INVALID


def test_r07_executor_rejects_before_operation_side_effect() -> None:
    calls = 0

    def operation(_: ExecutionContext) -> None:
        nonlocal calls
        calls += 1

    with pytest.raises(KernelError) as captured:
        RuntimeExecutor.execute(_context(tenant_id=None), operation)
    assert captured.value.code == ErrorCode.CTX_MISSING_TENANT
    assert calls == 0


def test_r08_executor_calls_operation_once_with_original_context() -> None:
    context = _context()
    received: list[ExecutionContext] = []
    result = RuntimeExecutor.execute(
        context,
        lambda current: received.append(current) or "ok",
    )
    assert result == "ok"
    assert received == [context]


def test_r09_observability_binding_is_allowlisted() -> None:
    context = _context(
        package_id="finance",
        trace_id="trace-1",
        approval_ref="sensitive-approval-ref",
    )
    binding = ObservabilityBinding.from_context(context).as_dict()
    assert set(binding) == {
        "correlation_id",
        "subject_id",
        "subject_type",
        "tenant_id",
        "trace_id",
        "package_id",
    }
    assert "approval_ref" not in binding


def test_r10_runtime_preserves_context_into_permission_kernel() -> None:
    context = _context(subject_type=SubjectType.HUMAN)
    permission = PermissionService(
        grant_administrators={context.subject_id},
        principal_eligibility=_AllowAllPrincipalEligibility(),
    )
    assert permission.grant(
        context,
        principal_subject_id=context.subject_id,
        resource_type="runtime_probe",
        actions={"execute"},
    ).ok
    decision = RuntimeExecutor.execute(
        context,
        lambda current: permission.evaluate(
            current,
            principal_subject_id=current.subject_id,
            action="execute",
            resource=Resource(
                tenant_id=current.tenant_id,
                resource_type="runtime_probe",
            ),
        ),
    )
    assert decision.data is not None
    assert decision.data.effect == PermissionEffect.ALLOW
    assert decision.data.correlation_id == context.correlation_id
    assert decision.data.tenant_id == context.tenant_id
    assert isinstance(decision.data.principal_subject_id, UUID)


def test_r11_runtime_requires_and_enforces_identity_session_validator() -> None:
    identity = IdentityService()
    registration_context = _context(subject_type=SubjectType.HUMAN)
    registered = identity.register_subject(
        registration_context,
        subject_type=SubjectKind.HUMAN,
        display_name="Runtime Session User",
    )
    assert registered.data is not None
    subject_context = replace(registration_context, subject_id=registered.data)
    credential = identity.bind_credential(
        subject_context,
        subject_id=registered.data,
        credential_kind="password_hash",
        secret_handle="vault:runtime-session",
    )
    assert credential.data is not None
    created = identity.create_session(
        subject_context,
        credential_id=credential.data,
    )
    assert created.data is not None
    session_context = replace(
        subject_context,
        session_id=created.data["session_id"],
    )
    calls = 0

    def operation(_: ExecutionContext) -> str:
        nonlocal calls
        calls += 1
        return "ok"

    with pytest.raises(KernelError) as missing_validator:
        RuntimeExecutor.execute(session_context, operation)
    assert missing_validator.value.code == ErrorCode.CTX_INVALID
    assert calls == 0
    assert (
        RuntimeExecutor.execute(
            session_context,
            operation,
            session_validator=identity,
        )
        == "ok"
    )
    assert calls == 1
    assert session_context.session_id is not None
    assert identity.revoke_session(
        subject_context,
        session_id=session_context.session_id,
        reason="logout",
    ).ok
    with pytest.raises(KernelError) as revoked:
        RuntimeExecutor.execute(
            session_context,
            operation,
            session_validator=identity,
        )
    assert revoked.value.code == ErrorCode.CTX_INVALID
    assert calls == 1
