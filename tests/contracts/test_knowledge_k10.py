"""PHX-K10 Knowledge provenance, derived, retention and retrieval contracts."""

from __future__ import annotations

from datetime import timedelta
from uuid import UUID, uuid4

from eaos_platform.knowledge.models import KnowledgeLayer, KnowledgeStatus
from eaos_platform.knowledge.service import KnowledgeService
from kernel.permission.service import PermissionService
from kernel.shared.context import ExecutionContext, SubjectType
from kernel.shared.errors import ErrorCode

ADMIN_ID = uuid4()
AUTHOR_ID = uuid4()
READER_ID = uuid4()
PEER_ID = uuid4()


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


def _services() -> tuple[PermissionService, KnowledgeService]:
    permission = PermissionService(
        grant_administrators={ADMIN_ID},
        principal_eligibility=_AllowAll(),
    )
    knowledge = KnowledgeService(permission)
    return permission, knowledge


def _grant_author(permission: PermissionService, tenant_id: UUID) -> None:
    admin = _ctx(tenant_id, ADMIN_ID)
    assert permission.grant(
        admin,
        principal_subject_id=AUTHOR_ID,
        resource_type="knowledge_entity",
        resource_id=None,
        actions={"upsert", "archive", "share", "read"},
    ).ok
    assert permission.grant(
        admin,
        principal_subject_id=AUTHOR_ID,
        resource_type="knowledge_link",
        resource_id=None,
        actions={"create", "read"},
    ).ok
    assert permission.grant(
        admin,
        principal_subject_id=AUTHOR_ID,
        resource_type="knowledge_graph",
        resource_id=tenant_id,
        actions={"query", "search"},
    ).ok
    assert permission.grant(
        admin,
        principal_subject_id=AUTHOR_ID,
        resource_type="knowledge_provenance",
        resource_id=None,
        actions={"read"},
    ).ok


def test_upsert_requires_provenance_and_records_it() -> None:
    tenant_id = uuid4()
    permission, knowledge = _services()
    _grant_author(permission, tenant_id)
    author = _ctx(tenant_id, AUTHOR_ID)

    missing = knowledge.upsert_entity(
        author,
        entity_type="Capability",
        name="Billing",
        layer=KnowledgeLayer.CANONICAL,
        source_ref="",
        reason="seed",
    )
    assert not missing.ok
    assert missing.error_code == ErrorCode.KNOWLEDGE_PROVENANCE_REQUIRED

    created = knowledge.upsert_entity(
        author,
        entity_type="Capability",
        name="Billing",
        layer=KnowledgeLayer.CANONICAL,
        source_ref="docs/billing.md",
        reason="initial seed",
        labels={"finance"},
    )
    assert created.ok and created.data is not None
    provenance = knowledge.get_provenance(
        author,
        subject_kind="entity",
        subject_id=created.data,
    )
    assert provenance.ok and provenance.data is not None
    assert len(provenance.data) == 1
    assert provenance.data[0].source_ref == "docs/billing.md"
    assert provenance.data[0].derived is False


def test_derived_cannot_be_relabelled_as_canonical() -> None:
    tenant_id = uuid4()
    permission, knowledge = _services()
    _grant_author(permission, tenant_id)
    author = _ctx(tenant_id, AUTHOR_ID)

    created = knowledge.upsert_entity(
        author,
        entity_type="Insight",
        name="Forecast",
        layer=KnowledgeLayer.DERIVED,
        source_ref="model:v1",
        reason="model output",
    )
    assert created.data is not None
    entity = knowledge.get_entity(author, entity_id=created.data)
    assert entity.data is not None

    disguised = knowledge.upsert_entity(
        author,
        entity_id=created.data,
        entity_type="Insight",
        name="Forecast",
        layer=KnowledgeLayer.CANONICAL,
        source_ref="model:v1",
        reason="promote",
        expected_version=entity.data.version,
    )
    assert not disguised.ok
    assert disguised.error_code == ErrorCode.KNOWLEDGE_DERIVED_MISLABELLED


def test_secrets_are_rejected_in_attributes() -> None:
    tenant_id = uuid4()
    permission, knowledge = _services()
    _grant_author(permission, tenant_id)
    result = knowledge.upsert_entity(
        _ctx(tenant_id, AUTHOR_ID),
        entity_type="System",
        name="ERP",
        layer=KnowledgeLayer.OPERATIONAL,
        attributes={"api_key": "secret"},
        source_ref="ops",
        reason="seed",
    )
    assert not result.ok
    assert result.error_code == ErrorCode.KNOWLEDGE_SECRET_FORBIDDEN


def test_archive_and_retention_fail_closed_on_read() -> None:
    tenant_id = uuid4()
    permission, knowledge = _services()
    _grant_author(permission, tenant_id)
    author = _ctx(tenant_id, AUTHOR_ID)
    created = knowledge.upsert_entity(
        author,
        entity_type="Policy",
        name="Retention",
        layer=KnowledgeLayer.DOCUMENTARY,
        source_ref="policy:1",
        reason="seed",
    )
    assert created.data is not None
    entity = knowledge.get_entity(author, entity_id=created.data)
    assert entity.data is not None

    archived = knowledge.archive_entity(
        author,
        entity_id=created.data,
        reason="retired",
        source_ref="policy:1",
        expected_version=entity.data.version,
    )
    assert archived.ok
    denied = knowledge.get_entity(author, entity_id=created.data)
    assert not denied.ok
    assert denied.error_code == ErrorCode.KNOWLEDGE_ARCHIVED

    expired = knowledge.upsert_entity(
        author,
        entity_type="Policy",
        name="Expired",
        layer=KnowledgeLayer.DOCUMENTARY,
        source_ref="policy:2",
        reason="seed",
        retain_until=ExecutionContext.utc_now() - timedelta(seconds=1),
    )
    assert not expired.ok
    assert expired.error_code == ErrorCode.COMMON_VALIDATION_FAILED


def test_query_search_and_share_are_permission_gated() -> None:
    tenant_id = uuid4()
    permission, knowledge = _services()
    _grant_author(permission, tenant_id)
    author = _ctx(tenant_id, AUTHOR_ID)
    created = knowledge.upsert_entity(
        author,
        entity_type="Product",
        name="EAOS Core",
        layer=KnowledgeLayer.CANONICAL,
        source_ref="catalog",
        reason="seed",
        labels={"platform"},
    )
    assert created.data is not None

    reader = _ctx(tenant_id, READER_ID)
    denied = knowledge.search(reader, text="EAOS")
    assert not denied.ok
    assert denied.error_code == ErrorCode.PERMISSION_DENIED

    admin = _ctx(tenant_id, ADMIN_ID)
    assert permission.grant(
        admin,
        principal_subject_id=READER_ID,
        resource_type="knowledge_graph",
        resource_id=tenant_id,
        actions={"query", "search"},
    ).ok
    assert permission.grant(
        admin,
        principal_subject_id=READER_ID,
        resource_type="knowledge_entity",
        resource_id=created.data,
        actions={"read"},
    ).ok

    hits = knowledge.search(reader, text="platform")
    assert hits.ok and hits.data is not None
    assert [item.id for item in hits.data] == [created.data]

    entity = knowledge.get_entity(author, entity_id=created.data)
    assert entity.data is not None
    shared = knowledge.share(
        author,
        entity_id=created.data,
        share_with_subject_id=PEER_ID,
        source_ref="catalog",
        reason="peer review",
        expected_version=entity.data.version,
    )
    assert shared.ok
    after = knowledge.get_entity(author, entity_id=created.data)
    assert after.data is not None
    assert PEER_ID in after.data.shared_with_subject_ids
    assert after.data.status == KnowledgeStatus.ACTIVE


def test_link_rejects_self_loop_and_cross_tenant() -> None:
    tenant_id = uuid4()
    other_tenant = uuid4()
    permission, knowledge = _services()
    _grant_author(permission, tenant_id)
    author = _ctx(tenant_id, AUTHOR_ID)
    created = knowledge.upsert_entity(
        author,
        entity_type="Node",
        name="A",
        layer=KnowledgeLayer.OPERATIONAL,
        source_ref="graph",
        reason="seed",
    )
    assert created.data is not None
    self_link = knowledge.link(
        author,
        from_entity_id=created.data,
        to_entity_id=created.data,
        relation_type="depends_on",
        source_ref="graph",
        reason="invalid",
    )
    assert not self_link.ok
    assert self_link.error_code == ErrorCode.KNOWLEDGE_LINK_INVALID

    foreign = knowledge.get_entity(_ctx(other_tenant, AUTHOR_ID), entity_id=created.data)
    assert not foreign.ok
    assert foreign.error_code == ErrorCode.KNOWLEDGE_ENTITY_NOT_FOUND


def test_version_conflict_on_concurrent_archive() -> None:
    tenant_id = uuid4()
    permission, knowledge = _services()
    _grant_author(permission, tenant_id)
    author = _ctx(tenant_id, AUTHOR_ID)
    created = knowledge.upsert_entity(
        author,
        entity_type="Doc",
        name="Manual",
        layer=KnowledgeLayer.DOCUMENTARY,
        source_ref="docs",
        reason="seed",
    )
    assert created.data is not None
    first = knowledge.archive_entity(
        author,
        entity_id=created.data,
        reason="v1",
        source_ref="docs",
        expected_version=1,
    )
    assert first.ok
    second = knowledge.archive_entity(
        author,
        entity_id=created.data,
        reason="v2",
        source_ref="docs",
        expected_version=1,
    )
    assert not second.ok
    assert second.error_code in {
        ErrorCode.KNOWLEDGE_VERSION_CONFLICT,
        ErrorCode.KNOWLEDGE_ARCHIVED,
    }
