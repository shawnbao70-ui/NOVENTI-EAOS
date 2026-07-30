"""PHX-E15 Enterprise Brain & Digital Twin contracts."""

from __future__ import annotations

from uuid import UUID, uuid4

from eaos_platform.brain.service import BrainService
from eaos_platform.twin.models import TwinSnapshotStatus
from eaos_platform.twin.service import TwinService
from kernel.permission.service import PermissionService
from kernel.shared.context import ExecutionContext, SubjectType
from kernel.shared.errors import ErrorCode

ADMIN_ID = uuid4()
OPERATOR_ID = uuid4()


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


def _services() -> tuple[PermissionService, TwinService, BrainService]:
    permission = PermissionService(
        grant_administrators={ADMIN_ID},
        principal_eligibility=_AllowAll(),
    )
    twin = TwinService(permission)
    brain = BrainService(permission, twin_reader=twin)
    return permission, twin, brain


def _grant(permission: PermissionService, tenant_id: UUID, subject_id: UUID) -> None:
    admin = _ctx(tenant_id, ADMIN_ID)
    for resource_type, actions in (
        ("twin_snapshot", {"write", "read"}),
        ("brain_insight", {"publish", "read"}),
    ):
        assert permission.grant(
            admin,
            principal_subject_id=subject_id,
            resource_type=resource_type,
            actions=actions,
        ).ok


def test_twin_requires_provenance_and_confidence() -> None:
    tenant_id = uuid4()
    permission, twin, _brain = _services()
    _grant(permission, tenant_id, OPERATOR_ID)
    operator = _ctx(tenant_id, OPERATOR_ID)
    missing = twin.upsert_snapshot(
        operator,
        entity_ref="plant:1",
        state={"throughput": 10},
        source_ref="",
        reason="sync",
        confidence=0.8,
    )
    assert missing.error_code == ErrorCode.TWIN_PROVENANCE_REQUIRED
    bad = twin.upsert_snapshot(
        operator,
        entity_ref="plant:1",
        state={"throughput": 10},
        source_ref="sensor:a",
        reason="sync",
        confidence=1.5,
    )
    assert bad.error_code == ErrorCode.TWIN_CONFIDENCE_INVALID


def test_twin_does_not_authorize_execution() -> None:
    tenant_id = uuid4()
    permission, twin, _brain = _services()
    _grant(permission, tenant_id, OPERATOR_ID)
    operator = _ctx(tenant_id, OPERATOR_ID)
    created = twin.upsert_snapshot(
        operator,
        entity_ref="plant:1",
        state={"throughput": 12},
        source_ref="sensor:a",
        reason="hourly sync",
        confidence=0.91,
    )
    assert created.ok and created.data is not None
    denied = twin.authorize_from_twin(operator, snapshot_id=created.data)
    assert denied.error_code == ErrorCode.TWIN_EXECUTION_FORBIDDEN


def test_brain_insight_advisory_with_twin_ref() -> None:
    tenant_id = uuid4()
    permission, twin, brain = _services()
    _grant(permission, tenant_id, OPERATOR_ID)
    operator = _ctx(tenant_id, OPERATOR_ID)
    twin_id = twin.upsert_snapshot(
        operator,
        entity_ref="plant:2",
        state={"utilization": 0.72},
        source_ref="mes:line-2",
        reason="shift close",
        confidence=0.88,
    )
    assert twin_id.data is not None
    published = brain.publish_insight(
        operator,
        kind="recommendation",
        summary="Consider redistributing load to line 3",
        confidence=0.74,
        source_ref="brain:model-v1",
        reason="utilization pattern",
        bias_notes="trained on Q1-Q2 only",
        twin_ref=twin_id.data,
        knowledge_refs=["knowledge:policy-load"],
    )
    assert published.ok and published.data is not None
    insight = brain.get_insight(operator, insight_id=published.data)
    assert insight.data is not None
    assert insight.data.advisory is True
    assert insight.data.twin_ref == twin_id.data


def test_brain_request_execution_forbidden() -> None:
    tenant_id = uuid4()
    permission, _twin, brain = _services()
    _grant(permission, tenant_id, OPERATOR_ID)
    operator = _ctx(tenant_id, OPERATOR_ID)
    published = brain.publish_insight(
        operator,
        kind="simulation",
        summary="Simulated overtime reduction",
        confidence=0.6,
        source_ref="brain:sim-1",
        reason="what-if",
    )
    assert published.data is not None
    denied = brain.request_execution(operator, insight_id=published.data)
    assert denied.error_code == ErrorCode.BRAIN_EXECUTION_FORBIDDEN


def test_non_advisory_insight_rejected() -> None:
    tenant_id = uuid4()
    permission, _twin, brain = _services()
    _grant(permission, tenant_id, OPERATOR_ID)
    denied = brain.publish_insight(
        _ctx(tenant_id, OPERATOR_ID),
        kind="insight",
        summary="Force execute",
        confidence=0.9,
        source_ref="brain:x",
        reason="test",
        advisory=False,
    )
    assert denied.error_code == ErrorCode.BRAIN_ADVISORY_REQUIRED


def test_twin_upsert_supersedes_prior_active() -> None:
    tenant_id = uuid4()
    permission, twin, _brain = _services()
    _grant(permission, tenant_id, OPERATOR_ID)
    operator = _ctx(tenant_id, OPERATOR_ID)
    first = twin.upsert_snapshot(
        operator,
        entity_ref="warehouse:a",
        state={"stock": 100},
        source_ref="wms",
        reason="nightly",
        confidence=0.95,
    )
    assert first.data is not None
    second = twin.upsert_snapshot(
        operator,
        entity_ref="warehouse:a",
        state={"stock": 90},
        source_ref="wms",
        reason="correction",
        confidence=0.97,
    )
    assert second.data is not None
    prior = twin.get_snapshot(operator, snapshot_id=first.data)
    assert prior.data is not None
    assert prior.data.status == TwinSnapshotStatus.SUPERSEDED
