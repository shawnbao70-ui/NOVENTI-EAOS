"""Narrow confirm-approval gate port for CRM C12 (PHX-G305)."""

from __future__ import annotations

from decimal import Decimal
from enum import StrEnum
from dataclasses import replace
from typing import Protocol
from uuid import UUID

from kernel.shared.context import ExecutionContext
from kernel.shared.results import KernelResult


class ConfirmApprovalDecision(StrEnum):
    APPROVED = "approved"
    DENIED = "denied"
    UNAVAILABLE = "unavailable"


class ConfirmApprovalGate(Protocol):
    def evaluate(
        self,
        ctx: ExecutionContext,
        *,
        sales_order_id: UUID,
        customer_id: UUID,
        total_amount: Decimal,
    ) -> ConfirmApprovalDecision: ...


class AllowConfirmApprovalGate:
    def evaluate(
        self,
        ctx: ExecutionContext,
        *,
        sales_order_id: UUID,
        customer_id: UUID,
        total_amount: Decimal,
    ) -> ConfirmApprovalDecision:
        return ConfirmApprovalDecision.APPROVED


class DenyConfirmApprovalGate:
    def evaluate(
        self,
        ctx: ExecutionContext,
        *,
        sales_order_id: UUID,
        customer_id: UUID,
        total_amount: Decimal,
    ) -> ConfirmApprovalDecision:
        return ConfirmApprovalDecision.DENIED


class UnavailableConfirmApprovalGate:
    def evaluate(
        self,
        ctx: ExecutionContext,
        *,
        sales_order_id: UUID,
        customer_id: UUID,
        total_amount: Decimal,
    ) -> ConfirmApprovalDecision:
        return ConfirmApprovalDecision.UNAVAILABLE


class ApprovedActionVerifier(Protocol):
    def verify_approved_action(
        self,
        ctx: ExecutionContext,
        *,
        action: str,
        resource_ref: str,
        plan_version: str | None = None,
        scope: str | None = None,
    ) -> KernelResult[bool]: ...


class QuoteIssueApprovalGate(Protocol):
    def evaluate(
        self,
        ctx: ExecutionContext,
        *,
        quote_id: UUID,
        approval_ref: str | None,
    ) -> KernelResult[bool]: ...


class WorkflowQuoteIssueApprovalGate:
    """Binds Quote.issue to an approved Workflow action without issuing it."""

    def __init__(self, workflow: ApprovedActionVerifier) -> None:
        self._workflow = workflow

    def evaluate(
        self,
        ctx: ExecutionContext,
        *,
        quote_id: UUID,
        approval_ref: str | None,
    ) -> KernelResult[bool]:
        return self._workflow.verify_approved_action(
            replace(ctx, approval_ref=approval_ref),
            action="crm.quote.issue",
            resource_ref=str(quote_id),
        )


class QuoteConvertApprovalGate(Protocol):
    def evaluate(
        self,
        ctx: ExecutionContext,
        *,
        quote_id: UUID,
        approval_ref: str | None,
    ) -> KernelResult[bool]: ...


class WorkflowQuoteConvertApprovalGate:
    """Binds Quote.convert to an approved Workflow action without converting it."""

    def __init__(self, workflow: ApprovedActionVerifier) -> None:
        self._workflow = workflow

    def evaluate(
        self,
        ctx: ExecutionContext,
        *,
        quote_id: UUID,
        approval_ref: str | None,
    ) -> KernelResult[bool]:
        return self._workflow.verify_approved_action(
            replace(ctx, approval_ref=approval_ref),
            action="crm.quote.convert",
            resource_ref=str(quote_id),
        )


class SalesOrderConfirmApprovalGate(Protocol):
    def evaluate(
        self,
        ctx: ExecutionContext,
        *,
        sales_order_id: UUID,
        approval_ref: str | None,
    ) -> KernelResult[bool]: ...


class WorkflowSalesOrderConfirmApprovalGate:
    """Binds SO.confirm to an approved Workflow action without confirming it."""

    def __init__(self, workflow: ApprovedActionVerifier) -> None:
        self._workflow = workflow

    def evaluate(
        self,
        ctx: ExecutionContext,
        *,
        sales_order_id: UUID,
        approval_ref: str | None,
    ) -> KernelResult[bool]:
        return self._workflow.verify_approved_action(
            replace(ctx, approval_ref=approval_ref),
            action="crm.sales_order.confirm",
            resource_ref=str(sales_order_id),
        )


class DeliveryOrderReleaseApprovalGate(Protocol):
    def evaluate(
        self,
        ctx: ExecutionContext,
        *,
        delivery_order_id: UUID,
        approval_ref: str | None,
    ) -> KernelResult[bool]: ...


class WorkflowDeliveryOrderReleaseApprovalGate:
    """Binds DO.release to an approved Workflow action without releasing it."""

    def __init__(self, workflow: ApprovedActionVerifier) -> None:
        self._workflow = workflow

    def evaluate(
        self,
        ctx: ExecutionContext,
        *,
        delivery_order_id: UUID,
        approval_ref: str | None,
    ) -> KernelResult[bool]:
        return self._workflow.verify_approved_action(
            replace(ctx, approval_ref=approval_ref),
            action="crm.delivery_order.release",
            resource_ref=str(delivery_order_id),
        )
