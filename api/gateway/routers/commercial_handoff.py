"""Explicit Brain/Twin commercial handoff HTTP surface (PHX-G339 / G390)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from api.gateway.context import derive_tenant_context, reject_context_override
from api.gateway.deps import (
    CommercialHandoffGatewayService,
    get_commercial_handoff_service,
)
from api.gateway.errors import raise_for_result
from api.gateway.schemas.commercial_handoff import (
    RmaCreditNoteHandoffEnvelope,
    RmaCreditNoteHandoffRequest,
    SoConfirmHandoffEnvelope,
    SoConfirmHandoffRequest,
)
from kernel.shared.context import ExecutionContext

router = APIRouter(
    prefix="/v1/platform/commercial-handoffs",
    tags=["Commercial Handoffs"],
)


@router.post(
    "/rma-credit-note",
    response_model=RmaCreditNoteHandoffEnvelope,
    status_code=status.HTTP_201_CREATED,
)
def handoff_rma_credit_note(
    body: RmaCreditNoteHandoffRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    handoff: CommercialHandoffGatewayService = Depends(get_commercial_handoff_service),
) -> RmaCreditNoteHandoffEnvelope:
    reject_context_override(body.model_dump(exclude_none=True))
    result = handoff.handoff_rma_credit_note(
        ctx,
        authorization_source=body.authorization_source,
        insight_id=body.insight_id,
        snapshot_id=body.snapshot_id,
        return_authorization_id=body.return_authorization_id,
        amount=body.amount,
        idempotency_key=body.idempotency_key,
        human_confirm=body.human_confirm,
    )
    raise_for_result(result)
    assert result.data is not None
    return RmaCreditNoteHandoffEnvelope.model_validate(
        {
            "data": {
                "authorization_source": result.data.authorization_source,
                "authorization_id": result.data.authorization_id,
                "return_authorization_id": result.data.return_authorization_id,
                "credit_note_id": result.data.credit_note_id,
                "authorization_audit_id": result.data.authorization_audit_id,
            },
            "audit_id": result.audit_id,
        }
    )


@router.post(
    "/so-confirm",
    response_model=SoConfirmHandoffEnvelope,
    status_code=status.HTTP_200_OK,
)
def handoff_so_confirm(
    body: SoConfirmHandoffRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    handoff: CommercialHandoffGatewayService = Depends(get_commercial_handoff_service),
) -> SoConfirmHandoffEnvelope:
    """Authorize SO.confirm intent only — never auto-confirm (PHX-G390)."""

    reject_context_override(body.model_dump(exclude_none=True))
    result = handoff.handoff_so_confirm(
        ctx,
        authorization_source=body.authorization_source,
        insight_id=body.insight_id,
        snapshot_id=body.snapshot_id,
        sales_order_id=body.sales_order_id,
        human_confirm=body.human_confirm,
    )
    raise_for_result(result)
    assert result.data is not None
    return SoConfirmHandoffEnvelope.model_validate(
        {
            "data": {
                "authorization_source": result.data.authorization_source,
                "authorization_id": result.data.authorization_id,
                "sales_order_id": result.data.sales_order_id,
                "sales_order_status": result.data.sales_order_status,
                "auto_confirm": result.data.auto_confirm,
                "approval_ref": result.data.approval_ref,
                "authorization_audit_id": result.data.authorization_audit_id,
            },
            "audit_id": result.audit_id,
        }
    )
