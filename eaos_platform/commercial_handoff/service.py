"""Explicit Brain/Twin-to-commercial handoffs (PHX-G339 / G390 / G392)."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Literal, Protocol
from uuid import UUID

from kernel.permission.models import PermissionEffect, Resource
from kernel.permission.service import PermissionService
from kernel.shared.audit import AuditLog, InMemoryAuditLog
from kernel.shared.context import ExecutionContext, require_context
from kernel.shared.errors import ErrorCode, KernelError
from kernel.shared.results import KernelResult

COMMERCIAL_HANDOFF_RESOURCE = "pkg.platform.commercial_handoff"
RMA_CREDIT_NOTE_ACTION = "handoff_rma_credit_note"
SO_CONFIRM_ACTION = "handoff_so_confirm"


class BrainExecutionPort(Protocol):
    def request_execution(
        self, ctx: ExecutionContext, *, insight_id: UUID
    ) -> KernelResult[bool]: ...


class TwinAuthorizationPort(Protocol):
    def authorize_from_twin(
        self, ctx: ExecutionContext, *, snapshot_id: UUID
    ) -> KernelResult[bool]: ...


class RmaCreditNotePort(Protocol):
    def create_credit_note_from_return_authorization(
        self,
        ctx: ExecutionContext,
        *,
        return_authorization_id: UUID,
        amount: Decimal,
        idempotency_key: UUID,
        human_confirm: bool,
    ) -> KernelResult[object]: ...


class SalesOrderReadPort(Protocol):
    def get_sales_order(
        self, ctx: ExecutionContext, *, sales_order_id: UUID
    ) -> KernelResult[object]: ...


@dataclass(frozen=True, slots=True)
class RmaCreditNoteHandoff:
    authorization_source: Literal["brain", "twin"]
    authorization_id: UUID
    return_authorization_id: UUID
    credit_note_id: UUID
    authorization_audit_id: UUID | str | None = None


@dataclass(frozen=True, slots=True)
class SoConfirmHandoff:
    authorization_source: Literal["brain", "twin"]
    authorization_id: UUID
    sales_order_id: UUID
    sales_order_status: str
    auto_confirm: Literal[False]
    approval_ref: str
    authorization_audit_id: UUID | str | None = None


class CommercialHandoffService:
    """Explicit commercial write/authorize handoffs; no silent Brain writes."""

    def __init__(
        self,
        permission_service: PermissionService,
        *,
        brain: BrainExecutionPort,
        twin: TwinAuthorizationPort,
        crm: RmaCreditNotePort | SalesOrderReadPort | None = None,
        sales_orders: SalesOrderReadPort | None = None,
        audit_log: AuditLog | None = None,
    ) -> None:
        self._permission = permission_service
        self._brain = brain
        self._twin = twin
        self._crm = crm
        self._sales_orders = sales_orders or (
            crm if crm is not None and hasattr(crm, "get_sales_order") else None
        )
        self._audit = audit_log or InMemoryAuditLog()

    def handoff_rma_credit_note(
        self,
        ctx: ExecutionContext,
        *,
        authorization_source: Literal["brain", "twin"],
        insight_id: UUID | None,
        snapshot_id: UUID | None,
        return_authorization_id: UUID,
        amount: Decimal,
        idempotency_key: UUID,
        human_confirm: bool,
    ) -> KernelResult[RmaCreditNoteHandoff]:
        try:
            require_context(ctx, tenant_data_plane=True)
            assert ctx.tenant_id is not None
            if self._crm is None or not hasattr(
                self._crm, "create_credit_note_from_return_authorization"
            ):
                raise KernelError(
                    ErrorCode.COMMON_INTERNAL,
                    "rma credit-note handoff CRM port is unavailable",
                )
            if not human_confirm:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "human confirmation is required",
                )
            authorization_id = self._validate_source(
                authorization_source, insight_id, snapshot_id
            )
            self._require_handoff_permission(
                ctx,
                action=RMA_CREDIT_NOTE_ACTION,
                audit_action="Platform.CommercialHandoff.RmaCreditNote",
            )
            self._audit.record(
                ctx,
                action="Platform.CommercialHandoff.RmaCreditNote",
                resource=f"return_authorization:{return_authorization_id}",
                result="intent",
                details={
                    "authorization_source": authorization_source,
                    "authorization_id": str(authorization_id),
                    "return_authorization_id": str(return_authorization_id),
                    "idempotency_key": str(idempotency_key),
                },
            )
            authorization = self._authorize(
                ctx,
                authorization_source=authorization_source,
                authorization_id=authorization_id,
            )
            if not authorization.ok:
                return KernelResult.failure(
                    authorization.error_code or ErrorCode.COMMON_INTERNAL,
                    authorization.error_message or "execution authorization failed",
                    details=authorization.details,
                )
            credit_note = self._crm.create_credit_note_from_return_authorization(
                ctx,
                return_authorization_id=return_authorization_id,
                amount=amount,
                idempotency_key=idempotency_key,
                human_confirm=True,
            )
            if not credit_note.ok:
                return KernelResult.failure(
                    credit_note.error_code or ErrorCode.COMMON_INTERNAL,
                    credit_note.error_message or "credit note creation failed",
                    details=credit_note.details,
                )
            return_authorization = credit_note.data
            credit_note_id = getattr(return_authorization, "credit_note_id", None)
            if not isinstance(credit_note_id, UUID):
                raise KernelError(
                    ErrorCode.COMMON_INTERNAL,
                    "credit note handoff returned no credit note",
                )
            handoff = RmaCreditNoteHandoff(
                authorization_source=authorization_source,
                authorization_id=authorization_id,
                return_authorization_id=return_authorization_id,
                credit_note_id=credit_note_id,
                authorization_audit_id=authorization.audit_id,
            )
            audit = self._audit.record(
                ctx,
                action="Platform.CommercialHandoff.RmaCreditNote",
                resource=f"return_authorization:{return_authorization_id}",
                result="ok",
                details={
                    "authorization_source": authorization_source,
                    "authorization_id": str(authorization_id),
                    "authorization_audit_id": (
                        str(authorization.audit_id)
                        if authorization.audit_id is not None
                        else None
                    ),
                    "return_authorization_id": str(return_authorization_id),
                    "credit_note_id": str(credit_note_id),
                    "idempotency_key": str(idempotency_key),
                },
            )
            return KernelResult.success(handoff, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)

    def handoff_so_confirm(
        self,
        ctx: ExecutionContext,
        *,
        authorization_source: Literal["brain", "twin"],
        insight_id: UUID | None,
        snapshot_id: UUID | None,
        sales_order_id: UUID,
        human_confirm: bool,
    ) -> KernelResult[SoConfirmHandoff]:
        """Authorize SO.confirm intent only — never auto-confirm (PHX-G390)."""

        try:
            require_context(ctx, tenant_data_plane=True)
            assert ctx.tenant_id is not None
            if self._sales_orders is None:
                raise KernelError(
                    ErrorCode.COMMON_INTERNAL,
                    "so-confirm handoff sales-order port is unavailable",
                )
            if not human_confirm:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "human confirmation is required",
                )
            authorization_id = self._validate_source(
                authorization_source, insight_id, snapshot_id
            )
            self._require_handoff_permission(
                ctx,
                action=SO_CONFIRM_ACTION,
                audit_action="Platform.CommercialHandoff.SoConfirm",
            )
            sales_order = self._sales_orders.get_sales_order(
                ctx, sales_order_id=sales_order_id
            )
            if not sales_order.ok or sales_order.data is None:
                return KernelResult.failure(
                    sales_order.error_code or ErrorCode.COMMON_NOT_FOUND,
                    sales_order.error_message or "sales order not found",
                    details=sales_order.details,
                )
            status_before = getattr(sales_order.data, "status", None)
            status_value = getattr(status_before, "value", status_before)
            if not isinstance(status_value, str):
                raise KernelError(
                    ErrorCode.COMMON_INTERNAL,
                    "sales order status is unavailable",
                )
            self._audit.record(
                ctx,
                action="Platform.CommercialHandoff.SoConfirm",
                resource=f"sales_order:{sales_order_id}",
                result="intent",
                details={
                    "authorization_source": authorization_source,
                    "authorization_id": str(authorization_id),
                    "sales_order_id": str(sales_order_id),
                    "sales_order_status": status_value,
                    "auto_confirm": False,
                },
            )
            authorization = self._authorize(
                ctx,
                authorization_source=authorization_source,
                authorization_id=authorization_id,
            )
            if not authorization.ok:
                return KernelResult.failure(
                    authorization.error_code or ErrorCode.COMMON_INTERNAL,
                    authorization.error_message or "execution authorization failed",
                    details=authorization.details,
                )
            # Re-read to prove status unchanged — never call confirm_sales_order.
            after = self._sales_orders.get_sales_order(
                ctx, sales_order_id=sales_order_id
            )
            if not after.ok or after.data is None:
                return KernelResult.failure(
                    after.error_code or ErrorCode.COMMON_INTERNAL,
                    after.error_message or "sales order re-read failed",
                    details=after.details,
                )
            status_after = getattr(getattr(after.data, "status", None), "value", None)
            if status_after is None:
                status_after = getattr(after.data, "status", None)
            if status_after != status_value:
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "sales order status changed during so-confirm handoff",
                )
            approval_ref = f"commercial-handoff:so-confirm:{authorization_id}"
            handoff = SoConfirmHandoff(
                authorization_source=authorization_source,
                authorization_id=authorization_id,
                sales_order_id=sales_order_id,
                sales_order_status=status_value,
                auto_confirm=False,
                approval_ref=approval_ref,
                authorization_audit_id=authorization.audit_id,
            )
            audit = self._audit.record(
                ctx,
                action="Platform.CommercialHandoff.SoConfirm",
                resource=f"sales_order:{sales_order_id}",
                result="ok",
                details={
                    "authorization_source": authorization_source,
                    "authorization_id": str(authorization_id),
                    "authorization_audit_id": (
                        str(authorization.audit_id)
                        if authorization.audit_id is not None
                        else None
                    ),
                    "sales_order_id": str(sales_order_id),
                    "sales_order_status": status_value,
                    "auto_confirm": False,
                    "approval_ref": approval_ref,
                },
            )
            return KernelResult.success(handoff, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)

    def _authorize(
        self,
        ctx: ExecutionContext,
        *,
        authorization_source: Literal["brain", "twin"],
        authorization_id: UUID,
    ) -> KernelResult[bool]:
        if authorization_source == "brain":
            return self._brain.request_execution(ctx, insight_id=authorization_id)
        return self._twin.authorize_from_twin(ctx, snapshot_id=authorization_id)

    def _require_handoff_permission(
        self,
        ctx: ExecutionContext,
        *,
        action: str,
        audit_action: str,
    ) -> None:
        assert ctx.tenant_id is not None
        decision = self._permission.evaluate(
            ctx,
            principal_subject_id=ctx.subject_id,
            action=action,
            resource=Resource(
                tenant_id=ctx.tenant_id,
                resource_type=COMMERCIAL_HANDOFF_RESOURCE,
            ),
        )
        if (
            not decision.ok
            or decision.data is None
            or decision.data.effect != PermissionEffect.ALLOW
        ):
            self._audit.record(
                ctx,
                action=audit_action,
                resource=COMMERCIAL_HANDOFF_RESOURCE,
                result="denied",
            )
            raise KernelError(
                ErrorCode.COMMERCIAL_HANDOFF_FORBIDDEN,
                "commercial handoff permission is required",
            )

    @staticmethod
    def _validate_source(
        authorization_source: Literal["brain", "twin"],
        insight_id: UUID | None,
        snapshot_id: UUID | None,
    ) -> UUID:
        if authorization_source == "brain" and insight_id is not None and snapshot_id is None:
            return insight_id
        if authorization_source == "twin" and snapshot_id is not None and insight_id is None:
            return snapshot_id
        raise KernelError(
            ErrorCode.COMMON_VALIDATION_FAILED,
            "authorization source must match exactly one source identifier",
        )
