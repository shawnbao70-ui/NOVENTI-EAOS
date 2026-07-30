"""PHX-E19 domain event catalog wiring contracts."""

from __future__ import annotations

import re
from pathlib import Path
from uuid import UUID, uuid4

from eaos_platform.knowledge.models import KnowledgeLayer
from eaos_platform.knowledge.service import KnowledgeService
from kernel.event_bus.bus import EventBus
from kernel.event_bus.domain_emit import DomainEventEmitter
from kernel.event_bus.models import EVENT_NAME_PATTERN
from kernel.event_bus.outbox import OutboxStatus
from kernel.event_bus.repository import InMemoryEventRepository
from kernel.organization.eligibility import RejectAllMembershipEligibility
from kernel.organization.models import UnitType
from kernel.organization.service import OrganizationService
from kernel.permission.models import Resource
from kernel.permission.service import PermissionService
from kernel.shared.context import ExecutionContext, SubjectType
from kernel.workflow.service import WorkflowService

ROOT = Path(__file__).resolve().parents[2]
EVENT_DOCS = (
    ROOT / "docs" / "architecture" / "ORGANIZATION_EVENTS.md",
    ROOT / "docs" / "architecture" / "PERMISSION_EVENTS.md",
    ROOT / "docs" / "architecture" / "WORKFLOW_EVENTS.md",
    ROOT / "docs" / "architecture" / "KNOWLEDGE_EVENTS.md",
    ROOT / "docs" / "architecture" / "COMMERCIAL_EVENTS.md",
)

WIRED_E19_EVENTS = frozenset(
    {
        "organization.tenant.created",
        "organization.tenant.suspended",
        "organization.tenant.reactivated",
        "organization.enterprise.created",
        "organization.unit.created",
        "organization.unit.updated",
        "organization.membership.added",
        "organization.membership.suspended",
        "organization.membership.reactivated",
        "organization.membership.transferred",
        "organization.membership.ended",
        "permission.policy.activated",
        "permission.policy.deprecated",
        "permission.grant.created",
        "permission.grant.revoked",
        "permission.grant.delegated",
        "permission.decision.recorded",
        "workflow.instance.started",
        "workflow.task.approved",
        "workflow.task.rejected",
        "workflow.task.escalated",
        "workflow.instance.cancelled",
        "workflow.instance.completed",
        "workflow.instance.compensated",
        "knowledge.entity.upserted",
        "knowledge.link.created",
        "knowledge.entity.archived",
        "knowledge.entity.shared",
        "knowledge.provenance.recorded",
        "crm.sales_order.confirmed",
        "inventory.delivery_order.shipped",
        "crm.quote.converted",
        "crm.delivery_order.released",
    }
)

GOVERNOR_ID = uuid4()
ADMIN_ID = uuid4()
INITIATOR_ID = uuid4()
AUTHOR_ID = uuid4()
WORKER_ID = uuid4()
SUBSCRIBER_ID = uuid4()


class _AllowAllMembership:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


class _AllowAllPrincipal:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


def _platform_ctx() -> ExecutionContext:
    return ExecutionContext(
        subject_id=GOVERNOR_ID,
        subject_type=SubjectType.SERVICE,
        correlation_id=str(uuid4()),
        request_time=ExecutionContext.utc_now(),
        platform_scope=True,
    )


def _tenant_ctx(tenant_id: UUID, *, subject_id: UUID | None = None) -> ExecutionContext:
    return ExecutionContext(
        subject_id=subject_id or uuid4(),
        subject_type=SubjectType.HUMAN,
        correlation_id=str(uuid4()),
        request_time=ExecutionContext.utc_now(),
        tenant_id=tenant_id,
    )


def _parse_catalog_event_names(path: Path) -> set[str]:
    names: set[str] = set()
    for match in re.finditer(
        r"`([a-z][a-z0-9_]*\.[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*)`",
        path.read_text(encoding="utf-8"),
    ):
        name = match.group(1)
        if name == "domain.entity.action":
            continue
        names.add(name)
    return names


def test_wired_catalog_names_match_event_name_pattern() -> None:
    catalog_names: set[str] = set()
    for doc in EVENT_DOCS:
        catalog_names.update(_parse_catalog_event_names(doc))
    assert catalog_names == WIRED_E19_EVENTS
    for event_name in WIRED_E19_EVENTS:
        assert EVENT_NAME_PATTERN.fullmatch(event_name)


def test_create_tenant_enqueues_tenant_and_primary_enterprise_events() -> None:
    repo = InMemoryEventRepository()
    service = OrganizationService(
        platform_governors={GOVERNOR_ID},
        domain_events=DomainEventEmitter(repo),
    )
    created = service.create_tenant(_platform_ctx(), legal_name="Acme")
    assert created.ok and created.data is not None
    pending = [
        entry
        for entry in repo.outbox.values()
        if entry.status == OutboxStatus.PENDING
    ]
    assert len(pending) == 2
    assert {entry.event_name for entry in pending} == {
        "organization.tenant.created",
        "organization.enterprise.created",
    }
    assert all(entry.producer == "organization.kernel" for entry in pending)
    assert all(entry.tenant_id == created.data for entry in pending)


def test_create_enterprise_and_add_membership_emit_catalog_events() -> None:
    repo = InMemoryEventRepository()
    service = OrganizationService(
        platform_governors={GOVERNOR_ID},
        membership_eligibility=_AllowAllMembership(),
        domain_events=DomainEventEmitter(repo),
    )
    tenant_id = service.create_tenant(_platform_ctx(), legal_name="Tenant A").data
    assert tenant_id is not None
    repo.outbox.clear()

    enterprise = service.create_enterprise(
        _tenant_ctx(tenant_id),
        legal_name="Secondary Co",
    )
    assert enterprise.ok and enterprise.data is not None
    enterprise_events = [entry.event_name for entry in repo.outbox.values()]
    assert enterprise_events == ["organization.enterprise.created"]

    subject_id = uuid4()
    membership = service.add_membership(
        _tenant_ctx(tenant_id),
        subject_id=subject_id,
    )
    assert membership.ok
    membership_events = [
        entry.event_name
        for entry in repo.outbox.values()
        if entry.event_name.startswith("organization.membership")
    ]
    assert membership_events == ["organization.membership.added"]


def test_permission_grant_emits_created_event() -> None:
    tenant_id = uuid4()
    repo = InMemoryEventRepository()
    permission = PermissionService(
        grant_administrators={ADMIN_ID},
        principal_eligibility=_AllowAllPrincipal(),
        domain_events=DomainEventEmitter(repo),
    )
    principal_id = uuid4()
    granted = permission.grant(
        _tenant_ctx(tenant_id, subject_id=ADMIN_ID),
        principal_subject_id=principal_id,
        resource_type="event_stream",
        actions={"publish"},
    )
    assert granted.ok
    assert len(repo.outbox) == 1
    entry = next(iter(repo.outbox.values()))
    assert entry.event_name == "permission.grant.created"
    assert entry.producer == "permission.kernel"


def test_permission_evaluate_emits_decision_recorded() -> None:
    tenant_id = uuid4()
    repo = InMemoryEventRepository()
    permission = PermissionService(
        grant_administrators={ADMIN_ID},
        principal_eligibility=_AllowAllPrincipal(),
        domain_events=DomainEventEmitter(repo),
    )
    principal_id = uuid4()
    admin = _tenant_ctx(tenant_id, subject_id=ADMIN_ID)
    assert permission.grant(
        admin,
        principal_subject_id=principal_id,
        resource_type="event_stream",
        actions={"publish"},
    ).ok
    repo.outbox.clear()

    decision = permission.evaluate(
        _tenant_ctx(tenant_id, subject_id=principal_id),
        principal_subject_id=principal_id,
        action="publish",
        resource=Resource(tenant_id=tenant_id, resource_type="event_stream"),
    )
    assert decision.ok and decision.data is not None
    assert len(repo.outbox) == 1
    entry = next(iter(repo.outbox.values()))
    assert entry.event_name == "permission.decision.recorded"
    assert entry.producer == "permission.kernel"
    assert entry.payload["decision_id"] == str(decision.data.id)
    assert entry.payload["effect"] == decision.data.effect.value
    assert entry.payload["action"] == "publish"
    assert "matched_grant_ids" in entry.payload
    assert "policy_document" not in entry.payload


def test_workflow_start_emits_instance_started() -> None:
    tenant_id = uuid4()
    repo = InMemoryEventRepository()
    permission = PermissionService(
        grant_administrators={ADMIN_ID},
        principal_eligibility=_AllowAllPrincipal(),
    )
    workflow = WorkflowService(
        permission,
        definition_administrators={ADMIN_ID},
        domain_events=DomainEventEmitter(repo),
    )
    admin = _tenant_ctx(tenant_id, subject_id=ADMIN_ID)
    definition = workflow.register_definition(
        admin,
        name=f"flow-{uuid4()}",
        definition_document_ref="docs/workflows/e19",
        version="1.0",
    )
    assert definition.data is not None
    assert permission.grant(
        admin,
        principal_subject_id=INITIATOR_ID,
        resource_type="workflow_definition",
        resource_id=definition.data,
        actions={"start"},
    ).ok
    started = workflow.start(
        _tenant_ctx(tenant_id, subject_id=INITIATOR_ID),
        definition_id=definition.data,
        payload={"case": "e19"},
    )
    assert started.ok
    entry = next(iter(repo.outbox.values()))
    assert entry.event_name == "workflow.instance.started"
    assert entry.producer == "workflow.kernel"


def test_knowledge_upsert_emits_entity_upserted() -> None:
    tenant_id = uuid4()
    repo = InMemoryEventRepository()
    permission = PermissionService(
        grant_administrators={ADMIN_ID},
        principal_eligibility=_AllowAllPrincipal(),
    )
    knowledge = KnowledgeService(
        permission,
        domain_events=DomainEventEmitter(repo),
    )
    admin = _tenant_ctx(tenant_id, subject_id=ADMIN_ID)
    assert permission.grant(
        admin,
        principal_subject_id=AUTHOR_ID,
        resource_type="knowledge_entity",
        actions={"upsert", "read"},
    ).ok
    assert permission.grant(
        admin,
        principal_subject_id=AUTHOR_ID,
        resource_type="knowledge_provenance",
        actions={"read"},
    ).ok
    upserted = knowledge.upsert_entity(
        _tenant_ctx(tenant_id, subject_id=AUTHOR_ID),
        entity_type="policy",
        name="Retention Rule",
        layer=KnowledgeLayer.CANONICAL,
        source_ref="manual://e19",
        reason="contract test",
    )
    assert upserted.ok
    upsert_events = [
        entry.event_name
        for entry in repo.outbox.values()
        if entry.event_name == "knowledge.entity.upserted"
    ]
    assert upsert_events == ["knowledge.entity.upserted"]


def test_domain_enqueue_then_dispatch_delivers_org_event() -> None:
    repo = InMemoryEventRepository()
    permission = PermissionService(
        grant_administrators={ADMIN_ID},
        principal_eligibility=_AllowAllPrincipal(),
    )
    bus = EventBus(permission, repository=repo)
    organization = OrganizationService(
        platform_governors={GOVERNOR_ID},
        domain_events=DomainEventEmitter(repo),
    )

    created = organization.create_tenant(_platform_ctx(), legal_name="Dispatch Tenant")
    assert created.ok and created.data is not None
    tenant_id = created.data
    admin_ctx = _tenant_ctx(tenant_id, subject_id=ADMIN_ID)
    worker_ctx = _tenant_ctx(tenant_id, subject_id=WORKER_ID)
    assert permission.grant(
        admin_ctx,
        principal_subject_id=WORKER_ID,
        resource_type="event_stream",
        actions={"dispatch", "read"},
    ).ok
    assert permission.grant(
        admin_ctx,
        principal_subject_id=SUBSCRIBER_ID,
        resource_type="event_stream",
        actions={"subscribe"},
    ).ok
    received: list[str] = []
    assert bus.subscribe(
        _tenant_ctx(tenant_id, subject_id=SUBSCRIBER_ID),
        subscriber_id="projection.org.tenant",
        event_name="organization.tenant.created",
        handler=lambda event: received.append(event.event_name),
    ).ok

    pending = [
        entry
        for entry in repo.outbox.values()
        if entry.event_name == "organization.tenant.created"
    ]
    assert len(pending) == 1
    assert pending[0].tenant_id == tenant_id

    dispatched = bus.dispatch_due(worker_ctx, worker_id="worker-e19")
    assert dispatched.ok and dispatched.data is not None
    assert dispatched.data.outbox_dispatched >= 1
    assert received == ["organization.tenant.created"]
