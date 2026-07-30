"""Digital Twin HTTP surface — thin transport adapter (PHX-G28 / G335)."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Response, status

from api.gateway.context import derive_tenant_context, reject_context_override
from api.gateway.deps import TwinGatewayService, get_twin_service
from api.gateway.errors import raise_for_result
from api.gateway.schemas.common import AuthorizedResult, UuidResult
from api.gateway.schemas.foundation_status import TwinStatusEnvelope
from api.gateway.schemas.twin import TwinSnapshotResponse, UpsertTwinSnapshotRequest
from api.gateway.serializers.twin import serialize_snapshot, uuid_result
from kernel.shared.context import ExecutionContext

router = APIRouter(prefix="/v1/twin", tags=["Twin"])


@router.get("/status", response_model=TwinStatusEnvelope)
def get_twin_status() -> TwinStatusEnvelope:
    """Read-only Twin posture (G335) + sync thin honesty (PHX-G388)."""

    return TwinStatusEnvelope.model_validate(
        {
            "data": {
                "writable": False,
                "authorize_execution": "permission_gated",
                "supported_surfaces": [
                    "snapshot_upsert",
                    "snapshot_get",
                    "authorize_from_twin",
                ],
                "continuous_sync_daemon": False,
                "sync_mode": "snapshot_upsert",
                "commercial_auto_write": False,
            }
        }
    )


@router.post(
    "/snapshots",
    response_model=UuidResult,
    status_code=status.HTTP_201_CREATED,
)
def upsert_snapshot(
    body: UpsertTwinSnapshotRequest,
    response: Response,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    twin: TwinGatewayService = Depends(get_twin_service),
) -> UuidResult:
    reject_context_override(body.model_dump(exclude_none=True))
    result = twin.upsert_snapshot(
        ctx,
        entity_ref=body.entity_ref,
        state=body.state,
        source_ref=body.source_ref,
        reason=body.reason,
        confidence=body.confidence,
        valid_from=body.valid_from,
        valid_until=body.valid_until,
    )
    raise_for_result(result)
    assert result.data is not None
    response.status_code = status.HTTP_201_CREATED
    return UuidResult.model_validate(
        uuid_result(result.data, audit_id=result.audit_id)
    )


@router.get("/snapshots/{snapshot_id}", response_model=TwinSnapshotResponse)
def get_snapshot(
    snapshot_id: UUID,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    twin: TwinGatewayService = Depends(get_twin_service),
) -> TwinSnapshotResponse:
    result = twin.get_snapshot(ctx, snapshot_id=snapshot_id)
    raise_for_result(result)
    assert result.data is not None
    return TwinSnapshotResponse.model_validate(serialize_snapshot(result.data))


@router.post(
    "/snapshots/{snapshot_id}/authorize",
    response_model=AuthorizedResult,
)
def authorize_from_twin(
    snapshot_id: UUID,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    twin: TwinGatewayService = Depends(get_twin_service),
) -> AuthorizedResult:
    result = twin.authorize_from_twin(ctx, snapshot_id=snapshot_id)
    raise_for_result(result)
    payload: dict[str, object] = {"data": {"authorized": True}}
    if result.audit_id is not None:
        payload["audit_id"] = str(result.audit_id)
    return AuthorizedResult.model_validate(payload)
