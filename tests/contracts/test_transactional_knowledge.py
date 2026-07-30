"""Knowledge SQLAlchemy transactional contracts."""

from __future__ import annotations

from uuid import UUID, uuid4

from sqlalchemy import Engine, create_engine, select
from sqlalchemy.pool import StaticPool

from eaos_platform.knowledge.models import KnowledgeLayer
from kernel.identity.models import SubjectKind
from kernel.infrastructure.persistence import (
    KnowledgeEntityRecord,
    KnowledgeProvenanceRecord,
    TransactionalIdentityService,
    TransactionalKnowledgeService,
    TransactionalOrganizationService,
    TransactionalPermissionService,
    create_session_factory,
    metadata,
)
from kernel.shared.context import ExecutionContext, SubjectType
from kernel.shared.errors import ErrorCode


def _engine() -> Engine:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        poolclass=StaticPool,
    )
    with engine.begin() as connection:
        connection.exec_driver_sql("ATTACH DATABASE ':memory:' AS kernel")
        metadata.create_all(connection)
    return engine


def _context(
    tenant_id=None,
    *,
    subject_id=None,
    subject_type=SubjectType.SERVICE,
    platform=False,
) -> ExecutionContext:
    return ExecutionContext(
        subject_id=subject_id or uuid4(),
        subject_type=subject_type,
        tenant_id=None if platform else (tenant_id or uuid4()),
        platform_scope=platform,
        correlation_id=str(uuid4()),
        request_time=ExecutionContext.utc_now(),
    )


def _foundation(engine: Engine) -> tuple[UUID, ExecutionContext]:
    governor = _context(platform=True)
    organization = TransactionalOrganizationService(
        create_session_factory(engine),
        platform_governors={governor.subject_id},
    )
    tenant = organization.create_tenant(governor, legal_name=str(uuid4()))
    assert tenant.data is not None
    identity = TransactionalIdentityService(create_session_factory(engine))
    initial = _context(tenant.data)
    author = identity.register_subject(
        initial,
        subject_type=SubjectKind.HUMAN,
        display_name="Author",
    )
    assert author.data is not None
    return tenant.data, _context(tenant.data, subject_id=author.data)


def _grant_author(
    engine: Engine,
    tenant_id: UUID,
    author: ExecutionContext,
) -> TransactionalKnowledgeService:
    permission = TransactionalPermissionService(
        create_session_factory(engine),
        grant_administrators={author.subject_id},
    )
    assert permission.grant(
        author,
        principal_subject_id=author.subject_id,
        resource_type="knowledge_entity",
        resource_id=None,
        actions={"upsert", "archive", "share", "read"},
    ).ok
    assert permission.grant(
        author,
        principal_subject_id=author.subject_id,
        resource_type="knowledge_link",
        resource_id=None,
        actions={"create", "read"},
    ).ok
    assert permission.grant(
        author,
        principal_subject_id=author.subject_id,
        resource_type="knowledge_graph",
        resource_id=tenant_id,
        actions={"query", "search"},
    ).ok
    assert permission.grant(
        author,
        principal_subject_id=author.subject_id,
        resource_type="knowledge_provenance",
        resource_id=None,
        actions={"read"},
    ).ok
    return TransactionalKnowledgeService(create_session_factory(engine))


def test_transactional_upsert_persists_entity_and_provenance() -> None:
    engine = _engine()
    tenant_id, author = _foundation(engine)
    knowledge = _grant_author(engine, tenant_id, author)

    created = knowledge.upsert_entity(
        author,
        entity_type="Capability",
        name="Billing",
        layer=KnowledgeLayer.CANONICAL,
        source_ref="docs/billing.md",
        reason="seed",
        labels={"finance"},
    )
    assert created.ok and created.data is not None

    with create_session_factory(engine)() as session:
        entity = session.scalar(
            select(KnowledgeEntityRecord).where(
                KnowledgeEntityRecord.id == created.data
            )
        )
        assert entity is not None
        assert entity.name == "Billing"
        assert entity.layer == "canonical"
        provenance = list(
            session.scalars(
                select(KnowledgeProvenanceRecord).where(
                    KnowledgeProvenanceRecord.subject_id == created.data
                )
            )
        )
        assert len(provenance) == 1
        assert provenance[0].source_ref == "docs/billing.md"

    fetched = knowledge.get_entity(author, entity_id=created.data)
    assert fetched.ok and fetched.data is not None
    assert fetched.data.labels == frozenset({"finance"})


def test_transactional_link_and_query_round_trip() -> None:
    engine = _engine()
    tenant_id, author = _foundation(engine)
    knowledge = _grant_author(engine, tenant_id, author)

    source = knowledge.upsert_entity(
        author,
        entity_type="Service",
        name="API",
        layer=KnowledgeLayer.OPERATIONAL,
        source_ref="ops",
        reason="seed",
    )
    target = knowledge.upsert_entity(
        author,
        entity_type="Service",
        name="Ledger",
        layer=KnowledgeLayer.OPERATIONAL,
        source_ref="ops",
        reason="seed",
    )
    assert source.data is not None and target.data is not None
    linked = knowledge.link(
        author,
        from_entity_id=source.data,
        to_entity_id=target.data,
        relation_type="depends_on",
        source_ref="ops",
        reason="topology",
    )
    assert linked.ok

    queried = knowledge.query(
        author,
        entity_type="Service",
        layer=KnowledgeLayer.OPERATIONAL,
    )
    assert queried.ok and queried.data is not None
    assert {item.name for item in queried.data} == {"API", "Ledger"}

    hits = knowledge.search(author, text="Ledger")
    assert hits.ok and hits.data is not None
    assert [item.id for item in hits.data] == [target.data]


def test_transactional_denies_without_permission() -> None:
    engine = _engine()
    tenant_id, author = _foundation(engine)
    knowledge = TransactionalKnowledgeService(create_session_factory(engine))
    result = knowledge.upsert_entity(
        author,
        entity_type="Capability",
        name="Denied",
        layer=KnowledgeLayer.CANONICAL,
        source_ref="docs",
        reason="seed",
    )
    assert not result.ok
    assert result.error_code == ErrorCode.PERMISSION_DENIED
    assert tenant_id == author.tenant_id
