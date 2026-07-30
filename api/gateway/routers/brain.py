"""Enterprise Brain HTTP surface — thin transport adapter (PHX-G28 / G335)."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Response, status

from api.gateway.context import derive_tenant_context, reject_context_override
from api.gateway.deps import BrainGatewayService, get_brain_service
from api.gateway.errors import raise_for_result
from api.gateway.schemas.brain import BrainInsightResponse, PublishInsightRequest
from api.gateway.schemas.common import AuthorizedResult, UuidResult
from api.gateway.schemas.foundation_status import BrainStatusEnvelope
from api.gateway.serializers.brain import serialize_insight, uuid_result
from kernel.shared.context import ExecutionContext

router = APIRouter(prefix="/v1/brain", tags=["Brain"])


@router.get("/status", response_model=BrainStatusEnvelope)
def get_brain_status() -> BrainStatusEnvelope:
    """Read-only Brain posture (G335) + confidence/bias honesty (PHX-G389)."""

    return BrainStatusEnvelope.model_validate(
        {
            "data": {
                "writable": False,
                "execute_execution": "permission_gated",
                "advisory_required": True,
                "supported_surfaces": [
                    "insight_publish",
                    "insight_get",
                    "request_execution",
                ],
                "confidence_field_required": True,
                "bias_notes_surface": "insight_payload",
                "confidence_drives_execution": False,
                "commercial_auto_write": False,
            }
        }
    )


@router.post(
    "/insights",
    response_model=UuidResult,
    status_code=status.HTTP_201_CREATED,
)
def publish_insight(
    body: PublishInsightRequest,
    response: Response,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    brain: BrainGatewayService = Depends(get_brain_service),
) -> UuidResult:
    reject_context_override(body.model_dump(exclude_none=True))
    result = brain.publish_insight(
        ctx,
        kind=body.kind,
        summary=body.summary,
        confidence=body.confidence,
        source_ref=body.source_ref,
        reason=body.reason,
        bias_notes=body.bias_notes,
        twin_ref=body.twin_ref,
        knowledge_refs=body.knowledge_refs,
        details=body.details,
        advisory=body.advisory,
    )
    raise_for_result(result)
    assert result.data is not None
    response.status_code = status.HTTP_201_CREATED
    return UuidResult.model_validate(
        uuid_result(result.data, audit_id=result.audit_id)
    )


@router.get("/insights/{insight_id}", response_model=BrainInsightResponse)
def get_insight(
    insight_id: UUID,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    brain: BrainGatewayService = Depends(get_brain_service),
) -> BrainInsightResponse:
    result = brain.get_insight(ctx, insight_id=insight_id)
    raise_for_result(result)
    assert result.data is not None
    return BrainInsightResponse.model_validate(serialize_insight(result.data))


@router.post(
    "/insights/{insight_id}/execute",
    response_model=AuthorizedResult,
)
def request_execution(
    insight_id: UUID,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    brain: BrainGatewayService = Depends(get_brain_service),
) -> AuthorizedResult:
    result = brain.request_execution(ctx, insight_id=insight_id)
    raise_for_result(result)
    payload: dict[str, object] = {"data": {"authorized": True}}
    if result.audit_id is not None:
        payload["audit_id"] = str(result.audit_id)
    return AuthorizedResult.model_validate(payload)
