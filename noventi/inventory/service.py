"""Permissioned Inventory stock and delivery shipment service (PHX-G311)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Protocol
from uuid import UUID

from kernel.event_bus.domain_emit import DomainEventEmitter
from kernel.permission.models import PermissionEffect, Resource
from kernel.shared.audit import AuditLog
from kernel.shared.context import ExecutionContext, require_context
from kernel.shared.errors import ErrorCode, KernelError
from kernel.shared.results import KernelResult
from noventi.inventory.models import (
    DeliveryShipPosting,
    DeliveryShipStatus,
    StockBalance,
    TenantShipPodPolicy,
)
from noventi.inventory.repository import InventoryRepository

STOCK_RESOURCE = "pkg.inventory.stock"
DELIVERY_SHIP_RESOURCE = "pkg.inventory.delivery_ship"
DELIVERY_UNSHIP_RESOURCE = "pkg.inventory.delivery_unship"
SHIP_POD_POLICY_RESOURCE = "pkg.inventory.ship_pod_policy"
DO_SHIP_WORKFLOW_ACTION = "inventory.delivery_order.ship"
QUANTITY_QUANTUM = Decimal("0.0001")
MAX_QUANTITY = Decimal("99999999999999.9999")
MAX_POD_REF_LENGTH = 128


class PermissionEvaluator(Protocol):
    def evaluate(
        self,
        ctx: ExecutionContext,
        *,
        principal_subject_id: UUID,
        action: str,
        resource: Resource,
    ) -> KernelResult: ...


@dataclass(frozen=True, slots=True)
class DeliveryOrderShipLineSnapshot:
    id: UUID
    quantity: Decimal


@dataclass(frozen=True, slots=True)
class DeliveryOrderShipSnapshot:
    id: UUID
    tenant_id: UUID
    status: str
    version: int
    sales_order_id: UUID
    sales_order_status: str
    sales_order_version: int
    customer_id: UUID
    commercial_hold: bool
    lines: tuple[DeliveryOrderShipLineSnapshot, ...]


class DeliveryOrderShipReadPort(Protocol):
    def get_delivery_order_ship_snapshot(
        self, delivery_order_id: UUID
    ) -> DeliveryOrderShipSnapshot | None: ...


class DeliveryOrderShipApprovalPolicyReadPort(Protocol):
    def do_ship_approval_required(self) -> bool: ...


class DeliveryOrderShipApprovalGate(Protocol):
    def evaluate(
        self,
        ctx: ExecutionContext,
        *,
        delivery_order_id: UUID,
        approval_ref: str | None,
    ) -> KernelResult[bool]: ...


class InventoryService:
    def __init__(
        self,
        permission: PermissionEvaluator,
        *,
        repository: InventoryRepository,
        audit_log: AuditLog,
        delivery_order_reader: DeliveryOrderShipReadPort,
        do_ship_approval_policy_reader: (
            DeliveryOrderShipApprovalPolicyReadPort | None
        ) = None,
        do_ship_approval_gate: DeliveryOrderShipApprovalGate | None = None,
        domain_events: DomainEventEmitter | None = None,
    ) -> None:
        self._permission = permission
        self._repository = repository
        self._audit = audit_log
        self._delivery_order_reader = delivery_order_reader
        self._do_ship_approval_policy_reader = do_ship_approval_policy_reader
        self._do_ship_approval_gate = do_ship_approval_gate
        self._domain_events = domain_events

    def set_do_ship_approval_gate(
        self, gate: DeliveryOrderShipApprovalGate | None
    ) -> None:
        self._do_ship_approval_gate = gate

    def adjust_stock(
        self,
        ctx: ExecutionContext,
        *,
        sales_order_line_id: UUID,
        quantity_delta: Decimal,
        idempotency_key: UUID,
    ) -> KernelResult[Decimal]:
        try:
            self._write_intent(
                ctx, "Inventory.Stock.Adjust", STOCK_RESOURCE, sales_order_line_id
            )
            denied = self._authorize(
                ctx,
                "adjust",
                STOCK_RESOURCE,
                resource_id=sales_order_line_id,
            )
            if denied is not None:
                return self._write_denied(
                    ctx,
                    "Inventory.Stock.Adjust",
                    STOCK_RESOURCE,
                    sales_order_line_id,
                    denied,
                )
            delta = self._delta(quantity_delta)
            existing = self._repository.get_adjustment_by_key(idempotency_key)
            if existing is not None:
                if (
                    existing.sales_order_line_id != sales_order_line_id
                    or existing.quantity_delta != delta
                ):
                    raise KernelError(
                        ErrorCode.COMMON_CONFLICT,
                        "adjustment idempotency key was used for another request",
                    )
                audit = self._write_result(
                    ctx,
                    "Inventory.Stock.Adjust",
                    STOCK_RESOURCE,
                    sales_order_line_id,
                    "ok",
                )
                return KernelResult.success(
                    existing.balance_after, audit_id=audit.id
                )
            balance = self._repository.atomic_adjust(
                sales_order_line_id=sales_order_line_id,
                quantity_delta=delta,
                idempotency_key=idempotency_key,
                adjusted_at=datetime.now(timezone.utc),
            )
            audit = self._write_result(
                ctx,
                "Inventory.Stock.Adjust",
                STOCK_RESOURCE,
                sales_order_line_id,
                "ok",
            )
            return KernelResult.success(balance.on_hand, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT, "stock adjustment conflict"
            )

    def get_stock_balance(
        self, ctx: ExecutionContext, *, sales_order_line_id: UUID
    ) -> KernelResult[StockBalance]:
        try:
            denied = self._authorize(
                ctx, "read", STOCK_RESOURCE, resource_id=sales_order_line_id
            )
            if denied is not None:
                return denied
            balance = self._repository.get_stock_balance(sales_order_line_id)
            if balance is None:
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND, "stock balance not found"
                )
            return KernelResult.success(balance)
        except KernelError as err:
            return KernelResult.from_error(err)

    def ship_delivery_order(
        self,
        ctx: ExecutionContext,
        *,
        delivery_order_id: UUID,
        idempotency_key: UUID,
        human_confirm: bool,
        approval_ref: str | None = None,
        pod_ref: str | None = None,
    ) -> KernelResult[DeliveryShipPosting]:
        try:
            self._write_intent(
                ctx,
                "Inventory.DeliveryOrder.Ship",
                DELIVERY_SHIP_RESOURCE,
                delivery_order_id,
            )
            denied = self._authorize(
                ctx,
                "ship",
                DELIVERY_SHIP_RESOURCE,
                resource_id=delivery_order_id,
            )
            if denied is not None:
                return self._write_denied(
                    ctx,
                    "Inventory.DeliveryOrder.Ship",
                    DELIVERY_SHIP_RESOURCE,
                    delivery_order_id,
                    denied,
                )
            existing = self._repository.get_ship_posting(delivery_order_id)
            if (
                existing is not None
                and existing.status == DeliveryShipStatus.SHIPPED
            ):
                if existing.idempotency_key != idempotency_key:
                    raise KernelError(
                        ErrorCode.COMMON_CONFLICT,
                        "delivery order is already shipped",
                    )
                audit = self._write_result(
                    ctx,
                    "Inventory.DeliveryOrder.Ship",
                    DELIVERY_SHIP_RESOURCE,
                    delivery_order_id,
                    "ok",
                )
                return KernelResult.success(existing, audit_id=audit.id)
            prior = self._repository.get_ship_posting_by_key(idempotency_key)
            if prior is not None:
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "ship idempotency key cannot be reused for reship",
                )
            if human_confirm is not True:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "human confirmation is required to ship",
                )
            normalized_pod = self._normalize_pod_ref(pod_ref)
            if self._ship_pod_required() and normalized_pod is None:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "POD evidence is required to ship",
                )
            if self._do_ship_approval_required():
                if self._do_ship_approval_gate is None:
                    raise KernelError(
                        ErrorCode.PERMISSION_DENIED,
                        "DO ship approval gate is unavailable",
                    )
                approved = self._do_ship_approval_gate.evaluate(
                    ctx,
                    delivery_order_id=delivery_order_id,
                    approval_ref=approval_ref,
                )
                if not approved.ok or approved.data is not True:
                    raise KernelError(
                        approved.error_code or ErrorCode.PERMISSION_DENIED,
                        approved.error_message or "DO ship approval is required",
                    )
            snapshot = (
                self._delivery_order_reader.get_delivery_order_ship_snapshot(
                    delivery_order_id
                )
            )
            if snapshot is None or snapshot.tenant_id != self._tenant_id(ctx):
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND, "delivery order not found"
                )
            self._validate_ship_snapshot(snapshot)
            shipped_at = datetime.now(timezone.utc)
            posting = self._repository.atomic_ship(
                delivery_order_id=snapshot.id,
                sales_order_id=snapshot.sales_order_id,
                expected_delivery_order_version=snapshot.version,
                line_quantities=tuple(
                    (line.id, self._ship_quantity(line.quantity))
                    for line in snapshot.lines
                ),
                idempotency_key=idempotency_key,
                shipped_at=shipped_at,
                pod_ref=normalized_pod,
                pod_captured_at=(
                    shipped_at if normalized_pod is not None else None
                ),
            )
            audit = self._write_result(
                ctx,
                "Inventory.DeliveryOrder.Ship",
                DELIVERY_SHIP_RESOURCE,
                delivery_order_id,
                "ok",
            )
            self._emit(
                ctx,
                event_name="inventory.delivery_order.shipped",
                payload={
                    "delivery_order_id": str(posting.delivery_order_id),
                    "sales_order_id": str(posting.sales_order_id),
                    "tenant_id": str(posting.tenant_id),
                },
                tenant_id=posting.tenant_id,
            )
            return KernelResult.success(posting, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT, "delivery shipment conflict"
            )

    def get_ship_pod_policy(
        self, ctx: ExecutionContext
    ) -> KernelResult[TenantShipPodPolicy]:
        try:
            denied = self._authorize(ctx, "read", SHIP_POD_POLICY_RESOURCE)
            if denied is not None:
                return denied
            return KernelResult.success(self._ship_pod_policy_or_default(ctx))
        except KernelError as err:
            return KernelResult.from_error(err)

    def set_ship_pod_policy(
        self,
        ctx: ExecutionContext,
        *,
        ship_pod_required: bool,
        expected_version: int,
    ) -> KernelResult[TenantShipPodPolicy]:
        try:
            tenant_id = self._tenant_id(ctx)
            self._write_intent(
                ctx,
                "Inventory.Policy.ShipPod.Set",
                SHIP_POD_POLICY_RESOURCE,
                tenant_id,
            )
            denied = self._authorize(ctx, "update", SHIP_POD_POLICY_RESOURCE)
            if denied is not None:
                return self._write_denied(
                    ctx,
                    "Inventory.Policy.ShipPod.Set",
                    SHIP_POD_POLICY_RESOURCE,
                    tenant_id,
                    denied,
                )
            current = self._repository.get_ship_pod_policy()
            if current is None:
                if expected_version != 0:
                    raise KernelError(
                        ErrorCode.COMMON_CONFLICT,
                        "ship POD policy version conflict",
                    )
                version = 1
            else:
                if current.version != expected_version:
                    raise KernelError(
                        ErrorCode.COMMON_CONFLICT,
                        "ship POD policy version conflict",
                    )
                version = current.version + 1
            policy = TenantShipPodPolicy(
                tenant_id=tenant_id,
                ship_pod_required=bool(ship_pod_required),
                updated_at=datetime.now(timezone.utc),
                version=version,
            )
            self._repository.save_ship_pod_policy(
                policy, expected_version=expected_version
            )
            audit = self._write_result(
                ctx,
                "Inventory.Policy.ShipPod.Set",
                SHIP_POD_POLICY_RESOURCE,
                tenant_id,
                "ok",
            )
            return KernelResult.success(policy, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT,
                "ship POD policy version conflict",
            )

    def get_ship_posting(
        self, ctx: ExecutionContext, *, delivery_order_id: UUID
    ) -> KernelResult[DeliveryShipPosting]:
        try:
            denied = self._authorize(
                ctx,
                "read",
                DELIVERY_SHIP_RESOURCE,
                resource_id=delivery_order_id,
            )
            if denied is not None:
                return denied
            posting = self._repository.get_ship_posting(delivery_order_id)
            if posting is None:
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND, "ship posting not found"
                )
            return KernelResult.success(posting)
        except KernelError as err:
            return KernelResult.from_error(err)

    def unship_delivery_order(
        self,
        ctx: ExecutionContext,
        *,
        delivery_order_id: UUID,
        human_confirm: bool,
        idempotency_key: UUID,
    ) -> KernelResult[DeliveryShipPosting]:
        try:
            self._write_intent(
                ctx,
                "Inventory.DeliveryOrder.Unship",
                DELIVERY_UNSHIP_RESOURCE,
                delivery_order_id,
            )
            denied = self._authorize(
                ctx,
                "unship",
                DELIVERY_UNSHIP_RESOURCE,
                resource_id=delivery_order_id,
            )
            if denied is not None:
                return self._write_denied(
                    ctx,
                    "Inventory.DeliveryOrder.Unship",
                    DELIVERY_UNSHIP_RESOURCE,
                    delivery_order_id,
                    denied,
                )
            posting = self._repository.get_ship_posting(delivery_order_id)
            if posting is not None and posting.status.value == "unshipped":
                if posting.unship_key != idempotency_key:
                    raise KernelError(
                        ErrorCode.COMMON_CONFLICT,
                        "delivery order is already unshipped",
                    )
                audit = self._write_result(
                    ctx,
                    "Inventory.DeliveryOrder.Unship",
                    DELIVERY_UNSHIP_RESOURCE,
                    delivery_order_id,
                    "ok",
                )
                return KernelResult.success(posting, audit_id=audit.id)
            if human_confirm is not True:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "human confirmation is required to unship",
                )
            snapshot = (
                self._delivery_order_reader.get_delivery_order_ship_snapshot(
                    delivery_order_id
                )
            )
            if snapshot is None or snapshot.tenant_id != self._tenant_id(ctx):
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND, "delivery order not found"
                )
            if snapshot.status != "shipped":
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT, "delivery order must be shipped"
                )
            if posting is None:
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT, "delivery order has no ship posting"
                )
            line_quantities = self._repository.list_do_ship_quantities(
                delivery_order_id
            )
            if not line_quantities:
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT, "delivery order has no ship quantities"
                )
            unshipped = self._repository.atomic_unship(
                delivery_order_id=snapshot.id,
                sales_order_id=snapshot.sales_order_id,
                expected_delivery_order_version=snapshot.version,
                line_quantities=line_quantities,
                idempotency_key=idempotency_key,
                unshipped_at=datetime.now(timezone.utc),
            )
            audit = self._write_result(
                ctx,
                "Inventory.DeliveryOrder.Unship",
                DELIVERY_UNSHIP_RESOURCE,
                delivery_order_id,
                "ok",
            )
            return KernelResult.success(unshipped, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT, "delivery unship conflict"
            )

    def _validate_ship_snapshot(
        self, snapshot: DeliveryOrderShipSnapshot
    ) -> None:
        if snapshot.status != "released":
            raise KernelError(
                ErrorCode.COMMON_CONFLICT,
                "delivery order must be released",
            )
        if snapshot.sales_order_status != "confirmed":
            raise KernelError(
                ErrorCode.COMMON_CONFLICT,
                "sales order must be confirmed",
            )
        if snapshot.commercial_hold:
            raise KernelError(
                ErrorCode.COMMON_CONFLICT,
                "customer is on commercial hold",
            )
        if not snapshot.lines:
            raise KernelError(
                ErrorCode.COMMON_CONFLICT,
                "sales order has no shippable lines",
            )

    def _do_ship_approval_required(self) -> bool:
        return bool(
            self._do_ship_approval_policy_reader is not None
            and self._do_ship_approval_policy_reader.do_ship_approval_required()
        )

    def _ship_pod_required(self) -> bool:
        policy = self._repository.get_ship_pod_policy()
        return bool(policy is not None and policy.ship_pod_required)

    def _ship_pod_policy_or_default(
        self, ctx: ExecutionContext
    ) -> TenantShipPodPolicy:
        return self._repository.get_ship_pod_policy() or TenantShipPodPolicy(
            tenant_id=self._tenant_id(ctx),
            ship_pod_required=False,
            updated_at=datetime.now(timezone.utc),
            version=0,
        )

    @staticmethod
    def _normalize_pod_ref(pod_ref: str | None) -> str | None:
        if pod_ref is None:
            return None
        normalized = pod_ref.strip()
        if not normalized:
            return None
        if len(normalized) > MAX_POD_REF_LENGTH:
            raise KernelError(
                ErrorCode.COMMON_VALIDATION_FAILED,
                "POD reference exceeds maximum length",
            )
        return normalized

    def _authorize(
        self,
        ctx: ExecutionContext,
        action: str,
        resource_type: str,
        *,
        resource_id: UUID | None = None,
    ) -> KernelResult | None:
        tenant_id = self._tenant_id(ctx)
        result = self._permission.evaluate(
            ctx,
            principal_subject_id=ctx.subject_id,
            action=action,
            resource=Resource(
                tenant_id=tenant_id,
                resource_type=resource_type,
                resource_id=resource_id,
            ),
        )
        if not result.ok:
            return result
        decision = result.data
        if decision is None or decision.effect != PermissionEffect.ALLOW:
            return KernelResult.failure(
                ErrorCode.PERMISSION_DENIED,
                "Inventory action is denied by Permission",
                details={
                    "reason_code": (
                        decision.reason_code
                        if decision is not None
                        else "PERMISSION_DENIED"
                    )
                },
            )
        return None

    def _write_intent(
        self,
        ctx: ExecutionContext,
        action: str,
        resource_type: str,
        resource_id: UUID,
    ) -> None:
        self._tenant_id(ctx)
        self._audit.record(
            ctx,
            action=f"{action}.Intent",
            resource=f"{resource_type}:{resource_id}",
            result="attempted",
            details={},
        )

    def _write_result(
        self,
        ctx: ExecutionContext,
        action: str,
        resource_type: str,
        resource_id: UUID,
        result: str,
    ):
        return self._audit.record(
            ctx,
            action=action,
            resource=f"{resource_type}:{resource_id}",
            result=result,
            details={},
        )

    def _write_denied(
        self,
        ctx: ExecutionContext,
        action: str,
        resource_type: str,
        resource_id: UUID,
        denied: KernelResult,
    ) -> KernelResult:
        audit = self._write_result(
            ctx, action, resource_type, resource_id, "denied"
        )
        return KernelResult.failure(
            denied.error_code or ErrorCode.PERMISSION_DENIED,
            denied.error_message or "Inventory action is denied",
            details=denied.details,
            audit_id=audit.id,
        )

    def _emit(
        self,
        ctx: ExecutionContext,
        *,
        event_name: str,
        payload: dict[str, object],
        tenant_id: UUID | None = None,
    ) -> None:
        if self._domain_events is None:
            return
        self._domain_events.enqueue_fact(
            ctx,
            event_name=event_name,
            producer="inventory.package",
            payload=payload,
            tenant_id=tenant_id,
        )

    @staticmethod
    def _tenant_id(ctx: ExecutionContext) -> UUID:
        require_context(ctx, tenant_data_plane=True)
        assert ctx.tenant_id is not None
        return ctx.tenant_id

    @staticmethod
    def _decimal(value: Decimal, message: str) -> Decimal:
        try:
            quantity = Decimal(str(value))
            four_decimal = quantity.quantize(QUANTITY_QUANTUM)
        except (InvalidOperation, ValueError):
            raise KernelError(
                ErrorCode.COMMON_VALIDATION_FAILED, message
            ) from None
        if (
            not quantity.is_finite()
            or quantity.copy_abs() > MAX_QUANTITY
            or quantity != four_decimal
        ):
            raise KernelError(ErrorCode.COMMON_VALIDATION_FAILED, message)
        return four_decimal

    @classmethod
    def _delta(cls, value: Decimal) -> Decimal:
        delta = cls._decimal(
            value, "quantity delta must be a nonzero finite 4-decimal value"
        )
        if delta == 0:
            raise KernelError(
                ErrorCode.COMMON_VALIDATION_FAILED,
                "quantity delta must be a nonzero finite 4-decimal value",
            )
        return delta

    @classmethod
    def _ship_quantity(cls, value: Decimal) -> Decimal:
        quantity = cls._decimal(
            value, "each shipment quantity must be positive"
        )
        if quantity <= 0:
            raise KernelError(
                ErrorCode.COMMON_CONFLICT,
                "each shipment quantity must be positive",
            )
        return quantity
