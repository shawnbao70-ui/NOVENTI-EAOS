"""PHX-G335 Brain execute / Twin authorize Permission-gated open (service)."""

from __future__ import annotations

from uuid import UUID, uuid4

from eaos_platform.brain.service import BrainService
from eaos_platform.twin.service import TwinService
from kernel.permission.service import PermissionService
from kernel.shared.context import ExecutionContext, SubjectType
from kernel.shared.errors import ErrorCode

ADMIN = uuid4()
OPERATOR = uuid4()
TENANT = uuid4()


class _AllowAll:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


def _ctx(subject_id: UUID = OPERATOR) -> ExecutionContext:
    return ExecutionContext(
        subject_id=subject_id,
        subject_type=SubjectType.HUMAN,
        tenant_id=TENANT,
        correlation_id=str(uuid4()),
        request_time=ExecutionContext.utc_now(),
    )


def _stack(*, with_execute: bool = False, with_authorize: bool = False):
    permission = PermissionService(
        grant_administrators={ADMIN},
        principal_eligibility=_AllowAll(),
    )
    twin = TwinService(permission)
    brain = BrainService(permission, twin_reader=twin)
    twin_actions = {"write", "read"}
    brain_actions = {"publish", "read"}
    if with_authorize:
        twin_actions = twin_actions | {"authorize"}
    if with_execute:
        brain_actions = brain_actions | {"execute"}
    assert permission.grant(
        _ctx(ADMIN),
        principal_subject_id=OPERATOR,
        resource_type="twin_snapshot",
        actions=twin_actions,
    ).ok
    assert permission.grant(
        _ctx(ADMIN),
        principal_subject_id=OPERATOR,
        resource_type="brain_insight",
        actions=brain_actions,
    ).ok
    return permission, twin, brain


def test_g335_deny_without_execute_or_authorize_grant() -> None:
    _permission, twin, brain = _stack()
    operator = _ctx()
    snap = twin.upsert_snapshot(
        operator,
        entity_ref="plant:g335-deny",
        state={"load": 1},
        source_ref="sensor:g335",
        reason="baseline",
        confidence=0.7,
    )
    assert snap.ok and snap.data is not None
    denied_twin = twin.authorize_from_twin(operator, snapshot_id=snap.data)
    assert not denied_twin.ok
    assert denied_twin.error_code == ErrorCode.TWIN_EXECUTION_FORBIDDEN

    published = brain.publish_insight(
        operator,
        kind="insight",
        summary="advisory",
        confidence=0.6,
        source_ref="model:g335",
        reason="deny path",
    )
    assert published.ok and published.data is not None
    denied_brain = brain.request_execution(operator, insight_id=published.data)
    assert not denied_brain.ok
    assert denied_brain.error_code == ErrorCode.BRAIN_EXECUTION_FORBIDDEN


def test_g335_allow_with_execute_and_authorize_grant() -> None:
    _permission, twin, brain = _stack(with_execute=True, with_authorize=True)
    operator = _ctx()
    snap = twin.upsert_snapshot(
        operator,
        entity_ref="plant:g335-allow",
        state={"load": 2},
        source_ref="sensor:g335",
        reason="baseline",
        confidence=0.8,
    )
    assert snap.ok and snap.data is not None
    allowed_twin = twin.authorize_from_twin(operator, snapshot_id=snap.data)
    assert allowed_twin.ok
    assert allowed_twin.data is True

    published = brain.publish_insight(
        operator,
        kind="recommendation",
        summary="governed",
        confidence=0.7,
        source_ref="model:g335",
        reason="allow path",
        twin_ref=snap.data,
    )
    assert published.ok and published.data is not None
    allowed_brain = brain.request_execution(operator, insight_id=published.data)
    assert allowed_brain.ok
    assert allowed_brain.data is True


def test_g335_missing_resource_not_found() -> None:
    _permission, twin, brain = _stack(with_execute=True, with_authorize=True)
    operator = _ctx()
    missing = uuid4()
    assert brain.request_execution(operator, insight_id=missing).error_code == (
        ErrorCode.BRAIN_NOT_FOUND
    )
    assert twin.authorize_from_twin(operator, snapshot_id=missing).error_code == (
        ErrorCode.TWIN_NOT_FOUND
    )
