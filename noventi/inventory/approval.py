"""Workflow approval adapter for Inventory DO.ship (PHX-G354)."""

from __future__ import annotations

from dataclasses import replace
from typing import Protocol
from uuid import UUID

from kernel.shared.context import ExecutionContext
from kernel.shared.results import KernelResult


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


class WorkflowDeliveryOrderShipApprovalGate:
    """Binds DO.ship to an approved Workflow action without shipping it."""

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
            action="inventory.delivery_order.ship",
            resource_ref=str(delivery_order_id),
        )
