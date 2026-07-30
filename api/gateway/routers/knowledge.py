"""Knowledge HTTP surface — thin transport adapter (PHX-G24)."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from api.gateway.context import derive_tenant_context, reject_context_override
from api.gateway.deps import KnowledgeGatewayService, get_knowledge_service
from api.gateway.errors import raise_for_result
from api.gateway.sample_knowledge_pack import sample_knowledge_pack_product_posture
from api.gateway.schemas.common import OkResponse, UuidResult
from api.gateway.schemas.knowledge import (
    CreateLinkRequest,
    KnowledgeEntityListEnvelope,
    KnowledgeEntityResponse,
    KnowledgeStatusEnvelope,
    ProvenanceListEnvelope,
    ShareEntityRequest,
    UpsertEntityRequest,
    VersionedProvenanceRequest,
)
from api.gateway.serializers.knowledge import (
    list_envelope,
    ok_response,
    serialize_entity,
    serialize_provenance,
    uuid_result,
)
from eaos_platform.knowledge.models import KnowledgeLayer
from kernel.shared.context import ExecutionContext

router = APIRouter(prefix="/v1/knowledge", tags=["Knowledge"])


@router.get("/status", response_model=KnowledgeStatusEnvelope)
def get_knowledge_status() -> KnowledgeStatusEnvelope:
    """Read-only Knowledge posture (G110/G293) + G377 governance honesty."""

    return KnowledgeStatusEnvelope.model_validate(
        {
            "data": {
                "writable": False,
                "supported_surfaces": [
                    "entity_upsert",
                    "entity_get",
                    "entity_query",
                    "entity_archive",
                    "entity_share",
                    "link_create",
                    "search",
                    "provenance_get",
                ],
                "sample_knowledge_pack_product": sample_knowledge_pack_product_posture(),
                "graph_write_engine": False,
                "constitution_rewrite": "never",
                "sample_pack_is_not_runtime_graph": True,
                "sample_pack_not_complete_evidence": True,
                "execution_authority": "none",
            }
        }
    )


@router.post("/entities", response_model=UuidResult)
def upsert_entity(
    body: UpsertEntityRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    knowledge: KnowledgeGatewayService = Depends(get_knowledge_service),
) -> UuidResult:
    reject_context_override(body.model_dump(exclude_none=True))
    result = knowledge.upsert_entity(
        ctx,
        entity_type=body.entity_type,
        name=body.name,
        layer=KnowledgeLayer(body.layer),
        attributes=body.attributes,
        labels=set(body.labels),
        source_ref=body.source_ref,
        reason=body.reason,
        retain_until=body.retain_until,
        entity_id=body.entity_id,
        expected_version=body.expected_version,
    )
    raise_for_result(result)
    assert result.data is not None
    return UuidResult.model_validate(
        uuid_result(result.data, audit_id=result.audit_id)
    )


@router.get("/entities", response_model=KnowledgeEntityListEnvelope)
def query_entities(
    ctx: ExecutionContext = Depends(derive_tenant_context),
    knowledge: KnowledgeGatewayService = Depends(get_knowledge_service),
    entity_type: str | None = Query(default=None, alias="entityType"),
    layer: str | None = Query(default=None),
    include_archived: bool = Query(default=False, alias="includeArchived"),
) -> KnowledgeEntityListEnvelope:
    parsed_layer: KnowledgeLayer | None = None
    if layer is not None:
        try:
            parsed_layer = KnowledgeLayer(layer)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "COMMON_VALIDATION_FAILED",
                    "message": "layer is invalid",
                },
            ) from exc
    result = knowledge.query(
        ctx,
        entity_type=entity_type,
        layer=parsed_layer,
        include_archived=include_archived,
    )
    raise_for_result(result)
    assert result.data is not None
    return KnowledgeEntityListEnvelope.model_validate(
        list_envelope([serialize_entity(item) for item in result.data])
    )


@router.get("/entities/{entity_id}", response_model=KnowledgeEntityResponse)
def get_entity(
    entity_id: UUID,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    knowledge: KnowledgeGatewayService = Depends(get_knowledge_service),
) -> KnowledgeEntityResponse:
    result = knowledge.get_entity(ctx, entity_id=entity_id)
    raise_for_result(result)
    assert result.data is not None
    return KnowledgeEntityResponse.model_validate(serialize_entity(result.data))


@router.post("/entities/{entity_id}/archive", response_model=OkResponse)
def archive_entity(
    entity_id: UUID,
    body: VersionedProvenanceRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    knowledge: KnowledgeGatewayService = Depends(get_knowledge_service),
) -> OkResponse:
    reject_context_override(body.model_dump(exclude_none=True))
    result = knowledge.archive_entity(
        ctx,
        entity_id=entity_id,
        reason=body.reason,
        source_ref=body.source_ref,
        expected_version=body.expected_version,
    )
    raise_for_result(result)
    return OkResponse.model_validate(ok_response(audit_id=result.audit_id))


@router.post("/entities/{entity_id}/share", response_model=OkResponse)
def share_entity(
    entity_id: UUID,
    body: ShareEntityRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    knowledge: KnowledgeGatewayService = Depends(get_knowledge_service),
) -> OkResponse:
    reject_context_override(body.model_dump(exclude_none=True))
    result = knowledge.share(
        ctx,
        entity_id=entity_id,
        share_with_subject_id=body.share_with_subject_id,
        source_ref=body.source_ref,
        reason=body.reason,
        expected_version=body.expected_version,
    )
    raise_for_result(result)
    return OkResponse.model_validate(ok_response(audit_id=result.audit_id))


@router.post("/links", response_model=UuidResult, status_code=status.HTTP_201_CREATED)
def create_link(
    body: CreateLinkRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    knowledge: KnowledgeGatewayService = Depends(get_knowledge_service),
) -> UuidResult:
    reject_context_override(body.model_dump())
    result = knowledge.link(
        ctx,
        from_entity_id=body.from_entity_id,
        to_entity_id=body.to_entity_id,
        relation_type=body.relation_type,
        source_ref=body.source_ref,
        reason=body.reason,
        attributes=body.attributes,
    )
    raise_for_result(result)
    assert result.data is not None
    return UuidResult.model_validate(
        uuid_result(result.data, audit_id=result.audit_id)
    )


@router.get("/search", response_model=KnowledgeEntityListEnvelope)
def search_knowledge(
    ctx: ExecutionContext = Depends(derive_tenant_context),
    knowledge: KnowledgeGatewayService = Depends(get_knowledge_service),
    text: str = Query(min_length=1),
) -> KnowledgeEntityListEnvelope:
    result = knowledge.search(ctx, text=text)
    raise_for_result(result)
    assert result.data is not None
    return KnowledgeEntityListEnvelope.model_validate(
        list_envelope([serialize_entity(item) for item in result.data])
    )


@router.get(
    "/provenance/{subject_kind}/{subject_id}",
    response_model=ProvenanceListEnvelope,
)
def get_provenance(
    subject_kind: str,
    subject_id: UUID,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    knowledge: KnowledgeGatewayService = Depends(get_knowledge_service),
) -> ProvenanceListEnvelope:
    result = knowledge.get_provenance(
        ctx,
        subject_kind=subject_kind,
        subject_id=subject_id,
    )
    raise_for_result(result)
    assert result.data is not None
    return ProvenanceListEnvelope.model_validate(
        list_envelope([serialize_provenance(item) for item in result.data])
    )
