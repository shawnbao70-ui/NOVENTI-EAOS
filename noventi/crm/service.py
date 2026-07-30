"""Permissioned Customer + Contact application service (PHX-G294)."""

from __future__ import annotations

import base64
import binascii
import json
from dataclasses import replace
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Protocol
from uuid import UUID, uuid4

from kernel.event_bus.domain_emit import DomainEventEmitter
from kernel.permission.models import PermissionEffect, Resource
from kernel.shared.audit import AuditLog
from kernel.shared.context import ExecutionContext, require_context
from kernel.shared.errors import ErrorCode, KernelError
from kernel.shared.results import KernelResult
from noventi.crm.approval import (
    ConfirmApprovalDecision,
    ConfirmApprovalGate,
    DeliveryOrderReleaseApprovalGate,
    QuoteConvertApprovalGate,
    QuoteIssueApprovalGate,
    SalesOrderConfirmApprovalGate,
)
from noventi.crm.credit_note import CreditNoteCreatePort
from noventi.crm.restock import ReturnRestockPort
from noventi.crm.models import (
    ARInvoice,
    ARInvoiceStatus,
    Contact,
    ContactStatus,
    ConversionStatus,
    Customer,
    CustomerStatus,
    DeliveryOrder,
    DeliveryOrderLine,
    DeliveryOrderLineStatus,
    DeliveryOrderStatus,
    Opportunity,
    OpportunityStatus,
    Page,
    Quote,
    QuoteConversion,
    QuoteLine,
    QuoteLineStatus,
    QuoteStatus,
    Requirement,
    RequirementStatus,
    ReturnAuthorization,
    ReturnAuthorizationStatus,
    SalesOrder,
    SalesOrderLine,
    SalesOrderStatus,
    TenantConfirmPolicy,
)
from noventi.crm.repository import CRMRepository

CUSTOMER_RESOURCE = "pkg.crm.customer"
CONTACT_RESOURCE = "pkg.crm.contact"
OPPORTUNITY_RESOURCE = "pkg.crm.opportunity"
REQUIREMENT_RESOURCE = "pkg.crm.requirement"
QUOTE_RESOURCE = "pkg.crm.quote"
CONVERSION_RESOURCE = "pkg.crm.quote_conversion"
SALES_ORDER_RESOURCE = "pkg.crm.sales_order"
QUOTE_LINE_RESOURCE = "pkg.crm.quote_line"
DELIVERY_ORDER_RESOURCE = "pkg.crm.delivery_order"
AR_INVOICE_RESOURCE = "pkg.crm.ar_invoice"
RETURN_AUTHORIZATION_RESOURCE = "pkg.crm.return_authorization"
POLICY_RESOURCE = "pkg.crm.policy"


def _encode_page_cursor(updated_at: datetime, item_id: UUID) -> str:
    payload = json.dumps(
        {"v": 1, "updated_at": updated_at.isoformat(), "id": str(item_id)},
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return base64.urlsafe_b64encode(payload).rstrip(b"=").decode("ascii")


def _decode_page_cursor(cursor: str | None) -> tuple[datetime, UUID] | None:
    if cursor is None:
        return None
    try:
        padding = "=" * (-len(cursor) % 4)
        payload = json.loads(
            base64.urlsafe_b64decode((cursor + padding).encode("ascii")).decode("utf-8")
        )
        if payload.get("v") != 1:
            raise ValueError("unsupported cursor version")
        updated_at = datetime.fromisoformat(payload["updated_at"])
        if updated_at.tzinfo is None:
            raise ValueError("cursor timestamp must include timezone")
        return updated_at, UUID(payload["id"])
    except (
        binascii.Error,
        json.JSONDecodeError,
        KeyError,
        TypeError,
        UnicodeDecodeError,
        ValueError,
    ) as exc:
        raise KernelError(
            ErrorCode.COMMON_VALIDATION_FAILED, "invalid CRM page cursor"
        ) from exc


class PermissionEvaluator(Protocol):
    def evaluate(
        self,
        ctx: ExecutionContext,
        *,
        principal_subject_id: UUID,
        action: str,
        resource: Resource,
    ) -> KernelResult: ...


class CRMService:
    """C1 use cases; owner references never participate in authorization."""

    def __init__(
        self,
        permission: PermissionEvaluator,
        *,
        repository: CRMRepository,
        audit_log: AuditLog,
        confirm_approval_gate: ConfirmApprovalGate | None = None,
        quote_issue_approval_gate: QuoteIssueApprovalGate | None = None,
        quote_convert_approval_gate: QuoteConvertApprovalGate | None = None,
        sales_order_confirm_approval_gate: SalesOrderConfirmApprovalGate | None = None,
        delivery_order_release_approval_gate: (
            DeliveryOrderReleaseApprovalGate | None
        ) = None,
        return_restock_port: ReturnRestockPort | None = None,
        credit_note_create_port: CreditNoteCreatePort | None = None,
        domain_events: DomainEventEmitter | None = None,
    ) -> None:
        self._permission = permission
        self._repository = repository
        self._audit = audit_log
        self._confirm_approval_gate = confirm_approval_gate
        self._quote_issue_approval_gate = quote_issue_approval_gate
        self._quote_convert_approval_gate = quote_convert_approval_gate
        self._sales_order_confirm_approval_gate = sales_order_confirm_approval_gate
        self._delivery_order_release_approval_gate = (
            delivery_order_release_approval_gate
        )
        self._return_restock_port = return_restock_port
        self._credit_note_create_port = credit_note_create_port
        self._domain_events = domain_events

    def set_quote_issue_approval_gate(
        self, gate: QuoteIssueApprovalGate | None
    ) -> None:
        self._quote_issue_approval_gate = gate

    def set_quote_convert_approval_gate(
        self, gate: QuoteConvertApprovalGate | None
    ) -> None:
        self._quote_convert_approval_gate = gate

    def set_sales_order_confirm_approval_gate(
        self, gate: SalesOrderConfirmApprovalGate | None
    ) -> None:
        self._sales_order_confirm_approval_gate = gate

    def set_delivery_order_release_approval_gate(
        self, gate: DeliveryOrderReleaseApprovalGate | None
    ) -> None:
        self._delivery_order_release_approval_gate = gate

    def create_customer(
        self,
        ctx: ExecutionContext,
        *,
        code: str,
        display_name: str,
        owner_subject_id: UUID | None = None,
    ) -> KernelResult[Customer]:
        customer_id = uuid4()
        try:
            self._write_intent(ctx, "CRM.Customer.Create", CUSTOMER_RESOURCE, customer_id)
            denied = self._authorize(ctx, "create", CUSTOMER_RESOURCE)
            if denied is not None:
                return self._write_denied(ctx, "CRM.Customer.Create", customer_id, denied)
            normalized_code = self._required(code, "code", 64)
            normalized_name = self._required(display_name, "display_name", 255)
            now = datetime.now(timezone.utc)
            customer = Customer(
                id=customer_id,
                tenant_id=self._tenant_id(ctx),
                code=normalized_code,
                display_name=normalized_name,
                owner_subject_id=owner_subject_id,
                status=CustomerStatus.ACTIVE,
                commercial_hold=False,
                created_at=now,
                updated_at=now,
            )
            self._repository.add_customer(customer)
            audit = self._write_result(
                ctx, "CRM.Customer.Create", CUSTOMER_RESOURCE, customer.id, "ok"
            )
            return KernelResult.success(customer, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT, "customer code already exists"
            )

    def get_customer(
        self,
        ctx: ExecutionContext,
        *,
        customer_id: UUID,
    ) -> KernelResult[Customer]:
        try:
            denied = self._authorize(ctx, "read", CUSTOMER_RESOURCE, customer_id)
            if denied is not None:
                return denied
            customer = self._repository.get_customer(customer_id)
            if customer is None:
                raise KernelError(ErrorCode.COMMON_NOT_FOUND, "customer not found")
            return KernelResult.success(customer)
        except KernelError as err:
            return KernelResult.from_error(err)

    def list_customers(
        self,
        ctx: ExecutionContext,
        *,
        limit: int = 50,
        cursor: str | None = None,
    ) -> KernelResult[Page[Customer]]:
        try:
            if limit < 1 or limit > 100:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "limit must be between 1 and 100",
                )
            denied = self._authorize(ctx, "read", CUSTOMER_RESOURCE)
            if denied is not None:
                return denied
            records = self._repository.list_customers(
                limit=limit + 1,
                after=_decode_page_cursor(cursor),
            )
            items = records[:limit]
            next_cursor = (
                _encode_page_cursor(items[-1].updated_at, items[-1].id)
                if len(records) > limit and items
                else None
            )
            return KernelResult.success(Page(items=items, next_cursor=next_cursor))
        except KernelError as err:
            return KernelResult.from_error(err)

    def update_customer(
        self,
        ctx: ExecutionContext,
        *,
        customer_id: UUID,
        display_name: str,
        owner_subject_id: UUID | None,
        expected_version: int,
    ) -> KernelResult[Customer]:
        try:
            self._write_intent(ctx, "CRM.Customer.Update", CUSTOMER_RESOURCE, customer_id)
            denied = self._authorize(ctx, "update", CUSTOMER_RESOURCE, customer_id)
            if denied is not None:
                return self._write_denied(ctx, "CRM.Customer.Update", customer_id, denied)
            customer = self._active_customer(customer_id)
            self._expected_version(customer.version, expected_version)
            updated = replace(
                customer,
                display_name=self._required(display_name, "display_name", 255),
                owner_subject_id=owner_subject_id,
                updated_at=datetime.now(timezone.utc),
                version=customer.version + 1,
            )
            self._repository.save_customer(updated, expected_version=expected_version)
            audit = self._write_result(
                ctx, "CRM.Customer.Update", CUSTOMER_RESOURCE, customer_id, "ok"
            )
            return KernelResult.success(updated, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(ErrorCode.COMMON_CONFLICT, "customer version conflict")

    def archive_customer(
        self,
        ctx: ExecutionContext,
        *,
        customer_id: UUID,
        reason: str,
        expected_version: int,
    ) -> KernelResult[Customer]:
        try:
            self._write_intent(ctx, "CRM.Customer.Archive", CUSTOMER_RESOURCE, customer_id)
            denied = self._authorize(ctx, "archive", CUSTOMER_RESOURCE, customer_id)
            if denied is not None:
                return self._write_denied(ctx, "CRM.Customer.Archive", customer_id, denied)
            self._required(reason, "reason", 500)
            customer = self._active_customer(customer_id)
            self._expected_version(customer.version, expected_version)
            now = datetime.now(timezone.utc)
            archived = replace(
                customer,
                status=CustomerStatus.ARCHIVED,
                archived_at=now,
                updated_at=now,
                version=customer.version + 1,
            )
            self._repository.save_customer(archived, expected_version=expected_version)
            audit = self._write_result(
                ctx, "CRM.Customer.Archive", CUSTOMER_RESOURCE, customer_id, "ok"
            )
            return KernelResult.success(archived, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(ErrorCode.COMMON_CONFLICT, "customer version conflict")

    def set_customer_commercial_hold(
        self,
        ctx: ExecutionContext,
        *,
        customer_id: UUID,
        commercial_hold: bool,
        expected_version: int,
    ) -> KernelResult[Customer]:
        try:
            self._write_intent(
                ctx,
                "CRM.Customer.CommercialHold.Set",
                CUSTOMER_RESOURCE,
                customer_id,
            )
            denied = self._authorize(ctx, "update", CUSTOMER_RESOURCE, customer_id)
            if denied is not None:
                return self._write_denied(
                    ctx,
                    "CRM.Customer.CommercialHold.Set",
                    customer_id,
                    denied,
                )
            customer = self._active_customer(customer_id)
            self._expected_version(customer.version, expected_version)
            updated = replace(
                customer,
                commercial_hold=bool(commercial_hold),
                updated_at=datetime.now(timezone.utc),
                version=customer.version + 1,
            )
            self._repository.save_customer(updated, expected_version=expected_version)
            audit = self._write_result(
                ctx,
                "CRM.Customer.CommercialHold.Set",
                CUSTOMER_RESOURCE,
                customer_id,
                "ok",
            )
            return KernelResult.success(updated, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(ErrorCode.COMMON_CONFLICT, "customer version conflict")

    def create_contact(
        self,
        ctx: ExecutionContext,
        *,
        customer_id: UUID,
        display_name: str,
        title: str | None = None,
        email: str | None = None,
        phone: str | None = None,
    ) -> KernelResult[Contact]:
        contact_id = uuid4()
        try:
            self._write_intent(ctx, "CRM.Contact.Create", CONTACT_RESOURCE, contact_id)
            denied = self._authorize(ctx, "create", CONTACT_RESOURCE)
            if denied is not None:
                return self._write_denied(ctx, "CRM.Contact.Create", contact_id, denied)
            self._active_customer(customer_id)
            now = datetime.now(timezone.utc)
            contact = Contact(
                id=contact_id,
                tenant_id=self._tenant_id(ctx),
                customer_id=customer_id,
                display_name=self._required(display_name, "display_name", 255),
                title=self._optional(title, 128),
                email=self._optional(email, 320),
                phone=self._optional(phone, 64),
                status=ContactStatus.ACTIVE,
                created_at=now,
                updated_at=now,
            )
            self._repository.add_contact(contact)
            audit = self._write_result(
                ctx, "CRM.Contact.Create", CONTACT_RESOURCE, contact.id, "ok"
            )
            return KernelResult.success(contact, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)

    def get_contact(
        self,
        ctx: ExecutionContext,
        *,
        customer_id: UUID,
        contact_id: UUID,
    ) -> KernelResult[Contact]:
        try:
            denied = self._authorize(ctx, "read", CONTACT_RESOURCE, contact_id)
            if denied is not None:
                return denied
            contact = self._repository.get_contact(customer_id, contact_id)
            if contact is None:
                raise KernelError(ErrorCode.COMMON_NOT_FOUND, "contact not found")
            return KernelResult.success(contact)
        except KernelError as err:
            return KernelResult.from_error(err)

    def list_contacts(
        self,
        ctx: ExecutionContext,
        *,
        customer_id: UUID,
        limit: int = 50,
        cursor: str | None = None,
    ) -> KernelResult[Page[Contact]]:
        try:
            if limit < 1 or limit > 100:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "limit must be between 1 and 100",
                )
            denied = self._authorize(ctx, "read", CUSTOMER_RESOURCE, customer_id)
            if denied is not None:
                return denied
            denied = self._authorize(ctx, "read", CONTACT_RESOURCE)
            if denied is not None:
                return denied
            if self._repository.get_customer(customer_id) is None:
                raise KernelError(ErrorCode.COMMON_NOT_FOUND, "customer not found")
            records = self._repository.list_contacts(
                customer_id,
                limit=limit + 1,
                after=_decode_page_cursor(cursor),
            )
            items = records[:limit]
            next_cursor = (
                _encode_page_cursor(items[-1].updated_at, items[-1].id)
                if len(records) > limit and items
                else None
            )
            return KernelResult.success(Page(items=items, next_cursor=next_cursor))
        except KernelError as err:
            return KernelResult.from_error(err)

    def update_contact(
        self,
        ctx: ExecutionContext,
        *,
        customer_id: UUID,
        contact_id: UUID,
        display_name: str,
        title: str | None,
        email: str | None,
        phone: str | None,
        expected_version: int,
    ) -> KernelResult[Contact]:
        try:
            self._write_intent(ctx, "CRM.Contact.Update", CONTACT_RESOURCE, contact_id)
            denied = self._authorize(ctx, "update", CONTACT_RESOURCE, contact_id)
            if denied is not None:
                return self._write_denied(ctx, "CRM.Contact.Update", contact_id, denied)
            contact = self._active_contact(customer_id, contact_id)
            self._expected_version(contact.version, expected_version)
            updated = replace(
                contact,
                display_name=self._required(display_name, "display_name", 255),
                title=self._optional(title, 128),
                email=self._optional(email, 320),
                phone=self._optional(phone, 64),
                updated_at=datetime.now(timezone.utc),
                version=contact.version + 1,
            )
            self._repository.save_contact(updated, expected_version=expected_version)
            audit = self._write_result(
                ctx, "CRM.Contact.Update", CONTACT_RESOURCE, contact_id, "ok"
            )
            return KernelResult.success(updated, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(ErrorCode.COMMON_CONFLICT, "contact version conflict")

    def archive_contact(
        self,
        ctx: ExecutionContext,
        *,
        customer_id: UUID,
        contact_id: UUID,
        reason: str,
        expected_version: int,
    ) -> KernelResult[Contact]:
        try:
            self._write_intent(ctx, "CRM.Contact.Archive", CONTACT_RESOURCE, contact_id)
            denied = self._authorize(ctx, "archive", CONTACT_RESOURCE, contact_id)
            if denied is not None:
                return self._write_denied(ctx, "CRM.Contact.Archive", contact_id, denied)
            self._required(reason, "reason", 500)
            contact = self._active_contact(customer_id, contact_id)
            self._expected_version(contact.version, expected_version)
            now = datetime.now(timezone.utc)
            archived = replace(
                contact,
                status=ContactStatus.ARCHIVED,
                archived_at=now,
                updated_at=now,
                version=contact.version + 1,
            )
            self._repository.save_contact(archived, expected_version=expected_version)
            audit = self._write_result(
                ctx, "CRM.Contact.Archive", CONTACT_RESOURCE, contact_id, "ok"
            )
            return KernelResult.success(archived, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(ErrorCode.COMMON_CONFLICT, "contact version conflict")

    def create_opportunity(
        self,
        ctx: ExecutionContext,
        *,
        customer_id: UUID,
        title: str,
        owner_subject_id: UUID | None = None,
    ) -> KernelResult[Opportunity]:
        opportunity_id = uuid4()
        try:
            self._write_intent(
                ctx,
                "CRM.Opportunity.Create",
                OPPORTUNITY_RESOURCE,
                opportunity_id,
            )
            denied = self._authorize(ctx, "create", OPPORTUNITY_RESOURCE)
            if denied is not None:
                return self._write_denied(
                    ctx, "CRM.Opportunity.Create", opportunity_id, denied
                )
            self._active_customer(customer_id)
            now = datetime.now(timezone.utc)
            opportunity = Opportunity(
                id=opportunity_id,
                tenant_id=self._tenant_id(ctx),
                customer_id=customer_id,
                code=f"OPP-{opportunity_id.hex[:12].upper()}",
                title=self._required(title, "title", 255),
                owner_subject_id=owner_subject_id,
                status=OpportunityStatus.ACTIVE,
                created_at=now,
                updated_at=now,
            )
            self._repository.add_opportunity(opportunity)
            audit = self._write_result(
                ctx,
                "CRM.Opportunity.Create",
                OPPORTUNITY_RESOURCE,
                opportunity.id,
                "ok",
            )
            return KernelResult.success(opportunity, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT, "opportunity code already exists"
            )

    def get_opportunity(
        self,
        ctx: ExecutionContext,
        *,
        opportunity_id: UUID,
    ) -> KernelResult[Opportunity]:
        try:
            denied = self._authorize(
                ctx, "read", OPPORTUNITY_RESOURCE, opportunity_id
            )
            if denied is not None:
                return denied
            opportunity = self._repository.get_opportunity(opportunity_id)
            if opportunity is None:
                raise KernelError(ErrorCode.COMMON_NOT_FOUND, "opportunity not found")
            return KernelResult.success(opportunity)
        except KernelError as err:
            return KernelResult.from_error(err)

    def list_opportunities(
        self,
        ctx: ExecutionContext,
        *,
        limit: int = 50,
        cursor: str | None = None,
    ) -> KernelResult[Page[Opportunity]]:
        try:
            if limit < 1 or limit > 100:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "limit must be between 1 and 100",
                )
            denied = self._authorize(ctx, "read", OPPORTUNITY_RESOURCE)
            if denied is not None:
                return denied
            records = self._repository.list_opportunities(
                limit=limit + 1,
                after=_decode_page_cursor(cursor),
            )
            items = records[:limit]
            next_cursor = (
                _encode_page_cursor(items[-1].updated_at, items[-1].id)
                if len(records) > limit and items
                else None
            )
            return KernelResult.success(Page(items=items, next_cursor=next_cursor))
        except KernelError as err:
            return KernelResult.from_error(err)

    def update_opportunity(
        self,
        ctx: ExecutionContext,
        *,
        opportunity_id: UUID,
        title: str,
        owner_subject_id: UUID | None,
        expected_version: int,
    ) -> KernelResult[Opportunity]:
        try:
            self._write_intent(
                ctx,
                "CRM.Opportunity.Update",
                OPPORTUNITY_RESOURCE,
                opportunity_id,
            )
            denied = self._authorize(
                ctx, "update", OPPORTUNITY_RESOURCE, opportunity_id
            )
            if denied is not None:
                return self._write_denied(
                    ctx, "CRM.Opportunity.Update", opportunity_id, denied
                )
            opportunity = self._active_opportunity(opportunity_id)
            self._expected_version(opportunity.version, expected_version)
            updated = replace(
                opportunity,
                title=self._required(title, "title", 255),
                owner_subject_id=owner_subject_id,
                updated_at=datetime.now(timezone.utc),
                version=opportunity.version + 1,
            )
            self._repository.save_opportunity(
                updated, expected_version=expected_version
            )
            audit = self._write_result(
                ctx,
                "CRM.Opportunity.Update",
                OPPORTUNITY_RESOURCE,
                opportunity_id,
                "ok",
            )
            return KernelResult.success(updated, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT, "opportunity version conflict"
            )

    def archive_opportunity(
        self,
        ctx: ExecutionContext,
        *,
        opportunity_id: UUID,
        reason: str,
        expected_version: int,
    ) -> KernelResult[Opportunity]:
        try:
            self._write_intent(
                ctx,
                "CRM.Opportunity.Archive",
                OPPORTUNITY_RESOURCE,
                opportunity_id,
            )
            denied = self._authorize(
                ctx, "archive", OPPORTUNITY_RESOURCE, opportunity_id
            )
            if denied is not None:
                return self._write_denied(
                    ctx, "CRM.Opportunity.Archive", opportunity_id, denied
                )
            self._required(reason, "reason", 500)
            opportunity = self._active_opportunity(opportunity_id)
            self._expected_version(opportunity.version, expected_version)
            now = datetime.now(timezone.utc)
            archived = replace(
                opportunity,
                status=OpportunityStatus.ARCHIVED,
                archived_at=now,
                updated_at=now,
                version=opportunity.version + 1,
            )
            self._repository.save_opportunity(
                archived, expected_version=expected_version
            )
            audit = self._write_result(
                ctx,
                "CRM.Opportunity.Archive",
                OPPORTUNITY_RESOURCE,
                opportunity_id,
                "ok",
            )
            return KernelResult.success(archived, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT, "opportunity version conflict"
            )

    def create_requirement(
        self,
        ctx: ExecutionContext,
        *,
        opportunity_id: UUID,
        title: str,
        description: str | None = None,
    ) -> KernelResult[Requirement]:
        requirement_id = uuid4()
        try:
            self._write_intent(
                ctx,
                "CRM.Requirement.Create",
                REQUIREMENT_RESOURCE,
                requirement_id,
            )
            denied = self._authorize(ctx, "create", REQUIREMENT_RESOURCE)
            if denied is not None:
                return self._write_denied(
                    ctx, "CRM.Requirement.Create", requirement_id, denied
                )
            self._active_opportunity(opportunity_id)
            now = datetime.now(timezone.utc)
            requirement = Requirement(
                id=requirement_id,
                tenant_id=self._tenant_id(ctx),
                opportunity_id=opportunity_id,
                code=f"REQ-{requirement_id.hex[:12].upper()}",
                title=self._required(title, "title", 255),
                description=self._optional(description, 4000),
                status=RequirementStatus.ACTIVE,
                created_at=now,
                updated_at=now,
            )
            self._repository.add_requirement(requirement)
            audit = self._write_result(
                ctx,
                "CRM.Requirement.Create",
                REQUIREMENT_RESOURCE,
                requirement.id,
                "ok",
            )
            return KernelResult.success(requirement, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT, "requirement code already exists"
            )

    def get_requirement(
        self,
        ctx: ExecutionContext,
        *,
        requirement_id: UUID,
    ) -> KernelResult[Requirement]:
        try:
            denied = self._authorize(
                ctx, "read", REQUIREMENT_RESOURCE, requirement_id
            )
            if denied is not None:
                return denied
            requirement = self._repository.get_requirement(requirement_id)
            if requirement is None:
                raise KernelError(ErrorCode.COMMON_NOT_FOUND, "requirement not found")
            return KernelResult.success(requirement)
        except KernelError as err:
            return KernelResult.from_error(err)

    def list_requirements(
        self,
        ctx: ExecutionContext,
        *,
        limit: int = 50,
        cursor: str | None = None,
    ) -> KernelResult[Page[Requirement]]:
        try:
            if limit < 1 or limit > 100:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "limit must be between 1 and 100",
                )
            denied = self._authorize(ctx, "read", REQUIREMENT_RESOURCE)
            if denied is not None:
                return denied
            records = self._repository.list_requirements(
                limit=limit + 1,
                after=_decode_page_cursor(cursor),
            )
            items = records[:limit]
            next_cursor = (
                _encode_page_cursor(items[-1].updated_at, items[-1].id)
                if len(records) > limit and items
                else None
            )
            return KernelResult.success(Page(items=items, next_cursor=next_cursor))
        except KernelError as err:
            return KernelResult.from_error(err)

    def update_requirement(
        self,
        ctx: ExecutionContext,
        *,
        requirement_id: UUID,
        title: str,
        description: str | None,
        expected_version: int,
    ) -> KernelResult[Requirement]:
        try:
            self._write_intent(
                ctx,
                "CRM.Requirement.Update",
                REQUIREMENT_RESOURCE,
                requirement_id,
            )
            denied = self._authorize(
                ctx, "update", REQUIREMENT_RESOURCE, requirement_id
            )
            if denied is not None:
                return self._write_denied(
                    ctx, "CRM.Requirement.Update", requirement_id, denied
                )
            requirement = self._active_requirement(requirement_id)
            self._expected_version(requirement.version, expected_version)
            updated = replace(
                requirement,
                title=self._required(title, "title", 255),
                description=self._optional(description, 4000),
                updated_at=datetime.now(timezone.utc),
                version=requirement.version + 1,
            )
            self._repository.save_requirement(
                updated, expected_version=expected_version
            )
            audit = self._write_result(
                ctx,
                "CRM.Requirement.Update",
                REQUIREMENT_RESOURCE,
                requirement_id,
                "ok",
            )
            return KernelResult.success(updated, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT, "requirement version conflict"
            )

    def archive_requirement(
        self,
        ctx: ExecutionContext,
        *,
        requirement_id: UUID,
        reason: str,
        expected_version: int,
    ) -> KernelResult[Requirement]:
        try:
            self._write_intent(
                ctx,
                "CRM.Requirement.Archive",
                REQUIREMENT_RESOURCE,
                requirement_id,
            )
            denied = self._authorize(
                ctx, "archive", REQUIREMENT_RESOURCE, requirement_id
            )
            if denied is not None:
                return self._write_denied(
                    ctx, "CRM.Requirement.Archive", requirement_id, denied
                )
            self._required(reason, "reason", 500)
            requirement = self._active_requirement(requirement_id)
            self._expected_version(requirement.version, expected_version)
            now = datetime.now(timezone.utc)
            archived = replace(
                requirement,
                status=RequirementStatus.ARCHIVED,
                archived_at=now,
                updated_at=now,
                version=requirement.version + 1,
            )
            self._repository.save_requirement(
                archived, expected_version=expected_version
            )
            audit = self._write_result(
                ctx,
                "CRM.Requirement.Archive",
                REQUIREMENT_RESOURCE,
                requirement_id,
                "ok",
            )
            return KernelResult.success(archived, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT, "requirement version conflict"
            )

    def create_quote(
        self,
        ctx: ExecutionContext,
        *,
        requirement_id: UUID,
        currency: str = "USD",
        notes: str | None = None,
        functional_currency: str | None = None,
        fx_rate: Decimal | None = None,
    ) -> KernelResult[Quote]:
        quote_id = uuid4()
        try:
            self._write_intent(ctx, "CRM.Quote.Create", QUOTE_RESOURCE, quote_id)
            denied = self._authorize(ctx, "create", QUOTE_RESOURCE)
            if denied is not None:
                return self._write_denied(ctx, "CRM.Quote.Create", quote_id, denied)
            self._active_requirement(requirement_id)
            now = datetime.now(timezone.utc)
            normalized_currency = self._currency(currency)
            quote_functional_currency, quote_fx_rate = self._quote_fx(
                currency=normalized_currency,
                functional_currency=functional_currency,
                fx_rate=fx_rate,
            )
            quote = Quote(
                id=quote_id,
                tenant_id=self._tenant_id(ctx),
                requirement_id=requirement_id,
                code=f"QTE-{quote_id.hex[:12].upper()}",
                currency=normalized_currency,
                notes=self._optional(notes, 4000),
                status=QuoteStatus.DRAFT,
                created_at=now,
                updated_at=now,
                functional_currency=quote_functional_currency,
                fx_rate=quote_fx_rate,
            )
            self._repository.add_quote(quote)
            audit = self._write_result(
                ctx, "CRM.Quote.Create", QUOTE_RESOURCE, quote.id, "ok"
            )
            return KernelResult.success(quote, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT, "quote code already exists"
            )

    def get_quote(
        self, ctx: ExecutionContext, *, quote_id: UUID
    ) -> KernelResult[Quote]:
        try:
            denied = self._authorize(ctx, "read", QUOTE_RESOURCE, quote_id)
            if denied is not None:
                return denied
            quote = self._repository.get_quote(quote_id)
            if quote is None:
                raise KernelError(ErrorCode.COMMON_NOT_FOUND, "quote not found")
            return KernelResult.success(quote)
        except KernelError as err:
            return KernelResult.from_error(err)

    def list_quotes(
        self,
        ctx: ExecutionContext,
        *,
        limit: int = 50,
        cursor: str | None = None,
    ) -> KernelResult[Page[Quote]]:
        try:
            if limit < 1 or limit > 100:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "limit must be between 1 and 100",
                )
            denied = self._authorize(ctx, "read", QUOTE_RESOURCE)
            if denied is not None:
                return denied
            records = self._repository.list_quotes(
                limit=limit + 1,
                after=_decode_page_cursor(cursor),
            )
            items = records[:limit]
            next_cursor = (
                _encode_page_cursor(items[-1].updated_at, items[-1].id)
                if len(records) > limit and items
                else None
            )
            return KernelResult.success(Page(items=items, next_cursor=next_cursor))
        except KernelError as err:
            return KernelResult.from_error(err)

    def update_quote(
        self,
        ctx: ExecutionContext,
        *,
        quote_id: UUID,
        currency: str,
        notes: str | None,
        expected_version: int,
        functional_currency: str | None = None,
        fx_rate: Decimal | None = None,
    ) -> KernelResult[Quote]:
        try:
            self._write_intent(ctx, "CRM.Quote.Update", QUOTE_RESOURCE, quote_id)
            denied = self._authorize(ctx, "update", QUOTE_RESOURCE, quote_id)
            if denied is not None:
                return self._write_denied(ctx, "CRM.Quote.Update", quote_id, denied)
            quote = self._draft_quote(quote_id)
            self._expected_version(quote.version, expected_version)
            normalized_currency = self._currency(currency)
            quote_functional_currency, quote_fx_rate = self._quote_fx(
                currency=normalized_currency,
                functional_currency=(
                    functional_currency
                    if functional_currency is not None
                    else quote.functional_currency
                ),
                fx_rate=(
                    fx_rate
                    if fx_rate is not None
                    else quote.fx_rate if functional_currency is None else None
                ),
            )
            updated = replace(
                quote,
                currency=normalized_currency,
                notes=self._optional(notes, 4000),
                updated_at=datetime.now(timezone.utc),
                version=quote.version + 1,
                functional_currency=quote_functional_currency,
                fx_rate=quote_fx_rate,
            )
            self._repository.save_quote(updated, expected_version=expected_version)
            audit = self._write_result(
                ctx, "CRM.Quote.Update", QUOTE_RESOURCE, quote_id, "ok"
            )
            return KernelResult.success(updated, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT, "quote version conflict"
            )

    def archive_quote(
        self,
        ctx: ExecutionContext,
        *,
        quote_id: UUID,
        reason: str,
        expected_version: int,
    ) -> KernelResult[Quote]:
        try:
            self._write_intent(ctx, "CRM.Quote.Archive", QUOTE_RESOURCE, quote_id)
            denied = self._authorize(ctx, "archive", QUOTE_RESOURCE, quote_id)
            if denied is not None:
                return self._write_denied(ctx, "CRM.Quote.Archive", quote_id, denied)
            self._required(reason, "reason", 500)
            quote = self._archivable_quote(quote_id)
            self._expected_version(quote.version, expected_version)
            now = datetime.now(timezone.utc)
            archived = replace(
                quote,
                status=QuoteStatus.ARCHIVED,
                archived_at=now,
                updated_at=now,
                version=quote.version + 1,
            )
            self._repository.save_quote(archived, expected_version=expected_version)
            audit = self._write_result(
                ctx, "CRM.Quote.Archive", QUOTE_RESOURCE, quote_id, "ok"
            )
            return KernelResult.success(archived, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT, "quote version conflict"
            )

    def issue_quote(
        self,
        ctx: ExecutionContext,
        *,
        quote_id: UUID,
        idempotency_key: UUID,
        human_confirm: bool,
        approval_ref: str | None = None,
    ) -> KernelResult[Quote]:
        try:
            self._write_intent(ctx, "CRM.Quote.Issue", QUOTE_RESOURCE, quote_id)
            denied = self._authorize(ctx, "issue", QUOTE_RESOURCE, quote_id)
            if denied is not None:
                return self._write_denied(ctx, "CRM.Quote.Issue", quote_id, denied)
            quote = self._repository.get_quote(quote_id)
            if quote is None:
                raise KernelError(ErrorCode.COMMON_NOT_FOUND, "quote not found")
            if quote.status == QuoteStatus.ISSUED:
                if quote.issue_key != idempotency_key:
                    raise KernelError(
                        ErrorCode.COMMON_CONFLICT,
                        "quote is already issued",
                    )
                audit = self._write_result(
                    ctx, "CRM.Quote.Issue", QUOTE_RESOURCE, quote.id, "ok"
                )
                return KernelResult.success(quote, audit_id=audit.id)
            if quote.status != QuoteStatus.DRAFT:
                raise KernelError(ErrorCode.COMMON_CONFLICT, "quote is archived")
            if self._confirm_policy_or_default(ctx).quote_issue_approval_required:
                if self._quote_issue_approval_gate is None:
                    raise KernelError(
                        ErrorCode.COMMON_CONFLICT,
                        "quote issue approval gate is unavailable",
                    )
                approved = self._quote_issue_approval_gate.evaluate(
                    ctx, quote_id=quote_id, approval_ref=approval_ref
                )
                if not approved.ok:
                    return KernelResult(
                        ok=False,
                        data=None,
                        error_code=approved.error_code,
                        error_message=approved.error_message,
                        details=approved.details,
                    )
            if not human_confirm:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "human confirmation is required",
                )
            active_lines = [
                item
                for item in self._repository.list_quote_lines(quote.id)
                if item.status == QuoteLineStatus.ACTIVE
            ]
            if not active_lines:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "at least one active quote line is required",
                )
            now = datetime.now(timezone.utc)
            issued = replace(
                quote,
                status=QuoteStatus.ISSUED,
                issued_at=now,
                issue_key=idempotency_key,
                updated_at=now,
                version=quote.version + 1,
            )
            self._repository.save_quote(issued, expected_version=quote.version)
            audit = self._write_result(
                ctx, "CRM.Quote.Issue", QUOTE_RESOURCE, quote_id, "ok"
            )
            return KernelResult.success(issued, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT, "quote issue conflict"
            )

    def convert_quote(
        self,
        ctx: ExecutionContext,
        *,
        quote_id: UUID,
        idempotency_key: UUID,
        functional_currency: str | None = None,
        fx_rate: Decimal | None = None,
        approval_ref: str | None = None,
    ) -> KernelResult[QuoteConversion]:
        conversion_id = uuid4()
        try:
            self._write_intent(
                ctx,
                "CRM.QuoteConversion.Create",
                CONVERSION_RESOURCE,
                conversion_id,
            )
            denied = self._authorize(ctx, "convert", CONVERSION_RESOURCE, quote_id)
            if denied is not None:
                return self._write_denied(
                    ctx, "CRM.QuoteConversion.Create", conversion_id, denied
                )
            quote = self._issued_quote(quote_id)
            if self._confirm_policy_or_default(ctx).quote_convert_approval_required:
                if self._quote_convert_approval_gate is None:
                    raise KernelError(
                        ErrorCode.COMMON_CONFLICT,
                        "quote convert approval gate is unavailable",
                    )
                approved = self._quote_convert_approval_gate.evaluate(
                    ctx, quote_id=quote_id, approval_ref=approval_ref
                )
                if not approved.ok:
                    return KernelResult(
                        ok=False,
                        data=None,
                        error_code=approved.error_code,
                        error_message=approved.error_message,
                        details=approved.details,
                    )
            existing = self._repository.get_conversion_by_quote(quote_id)
            if existing is not None:
                if existing.idempotency_key != idempotency_key:
                    raise KernelError(
                        ErrorCode.COMMON_CONFLICT,
                        "quote already has a conversion instruction",
                    )
                audit = self._write_result(
                    ctx,
                    "CRM.QuoteConversion.Create",
                    CONVERSION_RESOURCE,
                    existing.id,
                    "ok",
                )
                return KernelResult.success(existing, audit_id=audit.id)
            snapshot_currency, snapshot_rate = self._quote_fx(
                currency=quote.currency,
                functional_currency=(
                    functional_currency
                    if functional_currency is not None
                    else quote.functional_currency
                ),
                fx_rate=(
                    fx_rate
                    if fx_rate is not None
                    else quote.fx_rate if functional_currency is None else None
                ),
            )
            total_amount = sum(
                (
                    line.amount
                    for line in self._repository.list_quote_lines(quote.id)
                    if line.status == QuoteLineStatus.ACTIVE
                ),
                Decimal("0.00"),
            ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            now = datetime.now(timezone.utc)
            conversion = QuoteConversion(
                id=conversion_id,
                tenant_id=self._tenant_id(ctx),
                quote_id=quote.id,
                requirement_id=quote.requirement_id,
                quote_version=quote.version,
                currency=quote.currency,
                idempotency_key=idempotency_key,
                status=ConversionStatus.READY,
                created_at=now,
                updated_at=now,
                functional_currency=snapshot_currency,
                fx_rate=snapshot_rate,
                functional_total=(total_amount * snapshot_rate).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                ),
            )
            self._repository.add_conversion(conversion)
            audit = self._write_result(
                ctx,
                "CRM.QuoteConversion.Create",
                CONVERSION_RESOURCE,
                conversion.id,
                "ok",
            )
            self._emit(
                ctx,
                event_name="crm.quote.converted",
                payload={
                    "quote_id": str(conversion.quote_id),
                    "conversion_id": str(conversion.id),
                    "tenant_id": str(conversion.tenant_id),
                },
                tenant_id=conversion.tenant_id,
            )
            return KernelResult.success(conversion, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT,
                "quote conversion already exists",
            )

    def get_conversion(
        self,
        ctx: ExecutionContext,
        *,
        conversion_id: UUID,
    ) -> KernelResult[QuoteConversion]:
        try:
            denied = self._authorize(
                ctx, "read", CONVERSION_RESOURCE, conversion_id
            )
            if denied is not None:
                return denied
            conversion = self._repository.get_conversion(conversion_id)
            if conversion is None:
                raise KernelError(ErrorCode.COMMON_NOT_FOUND, "conversion not found")
            return KernelResult.success(conversion)
        except KernelError as err:
            return KernelResult.from_error(err)

    def create_sales_order(
        self,
        ctx: ExecutionContext,
        *,
        conversion_id: UUID,
        idempotency_key: UUID,
    ) -> KernelResult[SalesOrder]:
        sales_order_id = uuid4()
        try:
            self._write_intent(
                ctx,
                "CRM.SalesOrder.Create",
                SALES_ORDER_RESOURCE,
                sales_order_id,
            )
            denied = self._authorize(
                ctx, "create", SALES_ORDER_RESOURCE, conversion_id
            )
            if denied is not None:
                return self._write_denied(
                    ctx, "CRM.SalesOrder.Create", sales_order_id, denied
                )
            conversion = self._repository.get_conversion(conversion_id)
            if conversion is None:
                raise KernelError(ErrorCode.COMMON_NOT_FOUND, "conversion not found")
            existing = self._repository.get_sales_order_by_conversion(conversion_id)
            if existing is not None:
                if existing.idempotency_key != idempotency_key:
                    raise KernelError(
                        ErrorCode.COMMON_CONFLICT,
                        "conversion already has a sales order",
                    )
                audit = self._write_result(
                    ctx,
                    "CRM.SalesOrder.Create",
                    SALES_ORDER_RESOURCE,
                    existing.id,
                    "ok",
                )
                return KernelResult.success(existing, audit_id=audit.id)
            if conversion.status != ConversionStatus.READY:
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT, "conversion is not ready"
                )
            quote = self._readable_quote(conversion.quote_id)
            if quote.version != conversion.quote_version:
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "quote changed after conversion instruction",
                )
            now = datetime.now(timezone.utc)
            sales_order = SalesOrder(
                id=sales_order_id,
                tenant_id=self._tenant_id(ctx),
                conversion_id=conversion.id,
                quote_id=conversion.quote_id,
                requirement_id=conversion.requirement_id,
                code=f"SO-{sales_order_id.hex[:12].upper()}",
                currency=conversion.currency,
                idempotency_key=idempotency_key,
                status=SalesOrderStatus.CREATED,
                created_at=now,
                functional_currency=conversion.functional_currency,
                fx_rate=conversion.fx_rate,
                functional_total=conversion.functional_total,
            )
            self._repository.add_sales_order(sales_order)
            consumed = replace(
                conversion,
                status=ConversionStatus.CONSUMED,
                consumed_at=now,
                updated_at=now,
                version=conversion.version + 1,
            )
            self._repository.save_conversion(
                consumed, expected_version=conversion.version
            )
            audit = self._write_result(
                ctx,
                "CRM.SalesOrder.Create",
                SALES_ORDER_RESOURCE,
                sales_order.id,
                "ok",
            )
            return KernelResult.success(sales_order, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT, "sales order persistence conflict"
            )

    def get_sales_order(
        self,
        ctx: ExecutionContext,
        *,
        sales_order_id: UUID,
    ) -> KernelResult[SalesOrder]:
        try:
            denied = self._authorize(
                ctx, "read", SALES_ORDER_RESOURCE, sales_order_id
            )
            if denied is not None:
                return denied
            sales_order = self._repository.get_sales_order(sales_order_id)
            if sales_order is None:
                raise KernelError(ErrorCode.COMMON_NOT_FOUND, "sales order not found")
            return KernelResult.success(sales_order)
        except KernelError as err:
            return KernelResult.from_error(err)

    def list_sales_orders(
        self,
        ctx: ExecutionContext,
        *,
        limit: int = 50,
        cursor: str | None = None,
    ) -> KernelResult[Page[SalesOrder]]:
        try:
            if limit < 1 or limit > 100:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "limit must be between 1 and 100",
                )
            denied = self._authorize(ctx, "read", SALES_ORDER_RESOURCE)
            if denied is not None:
                return denied
            records = self._repository.list_sales_orders(
                limit=limit + 1,
                after=_decode_page_cursor(cursor),
            )
            items = records[:limit]
            next_cursor = (
                _encode_page_cursor(items[-1].created_at, items[-1].id)
                if len(records) > limit and items
                else None
            )
            return KernelResult.success(Page(items=items, next_cursor=next_cursor))
        except KernelError as err:
            return KernelResult.from_error(err)

    def create_quote_line(
        self,
        ctx: ExecutionContext,
        *,
        quote_id: UUID,
        description: str,
        quantity: Decimal,
        unit_price: Decimal,
    ) -> KernelResult[QuoteLine]:
        quote_line_id = uuid4()
        try:
            self._write_intent(
                ctx,
                "CRM.QuoteLine.Create",
                QUOTE_LINE_RESOURCE,
                quote_line_id,
            )
            denied = self._authorize(ctx, "create", QUOTE_LINE_RESOURCE, quote_id)
            if denied is not None:
                return self._write_denied(
                    ctx, "CRM.QuoteLine.Create", quote_line_id, denied
                )
            quote = self._draft_quote(quote_id)
            normalized_quantity, normalized_price, amount = self._line_values(
                quantity, unit_price
            )
            now = datetime.now(timezone.utc)
            quote_line = QuoteLine(
                id=quote_line_id,
                tenant_id=self._tenant_id(ctx),
                quote_id=quote_id,
                line_number=self._repository.next_quote_line_number(quote_id),
                description=self._required(description, "description", 500),
                quantity=normalized_quantity,
                unit_price=normalized_price,
                amount=amount,
                status=QuoteLineStatus.ACTIVE,
                created_at=now,
                updated_at=now,
            )
            self._repository.add_quote_line(quote_line)
            self._touch_quote(quote, now)
            audit = self._write_result(
                ctx,
                "CRM.QuoteLine.Create",
                QUOTE_LINE_RESOURCE,
                quote_line.id,
                "ok",
            )
            return KernelResult.success(quote_line, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT, "quote line persistence conflict"
            )

    def get_quote_line(
        self,
        ctx: ExecutionContext,
        *,
        quote_id: UUID,
        quote_line_id: UUID,
    ) -> KernelResult[QuoteLine]:
        try:
            denied = self._authorize(
                ctx, "read", QUOTE_LINE_RESOURCE, quote_line_id
            )
            if denied is not None:
                return denied
            self._readable_quote(quote_id)
            quote_line = self._repository.get_quote_line(quote_id, quote_line_id)
            if quote_line is None:
                raise KernelError(ErrorCode.COMMON_NOT_FOUND, "quote line not found")
            return KernelResult.success(quote_line)
        except KernelError as err:
            return KernelResult.from_error(err)

    def list_quote_lines(
        self,
        ctx: ExecutionContext,
        *,
        quote_id: UUID,
    ) -> KernelResult[list[QuoteLine]]:
        try:
            denied = self._authorize(ctx, "read", QUOTE_LINE_RESOURCE, quote_id)
            if denied is not None:
                return denied
            self._readable_quote(quote_id)
            return KernelResult.success(self._repository.list_quote_lines(quote_id))
        except KernelError as err:
            return KernelResult.from_error(err)

    def update_quote_line(
        self,
        ctx: ExecutionContext,
        *,
        quote_id: UUID,
        quote_line_id: UUID,
        description: str,
        quantity: Decimal,
        unit_price: Decimal,
        expected_version: int,
    ) -> KernelResult[QuoteLine]:
        try:
            self._write_intent(
                ctx,
                "CRM.QuoteLine.Update",
                QUOTE_LINE_RESOURCE,
                quote_line_id,
            )
            denied = self._authorize(
                ctx, "update", QUOTE_LINE_RESOURCE, quote_line_id
            )
            if denied is not None:
                return self._write_denied(
                    ctx, "CRM.QuoteLine.Update", quote_line_id, denied
                )
            quote = self._draft_quote(quote_id)
            quote_line = self._active_quote_line(quote_id, quote_line_id)
            self._expected_version(quote_line.version, expected_version)
            normalized_quantity, normalized_price, amount = self._line_values(
                quantity, unit_price
            )
            now = datetime.now(timezone.utc)
            updated = replace(
                quote_line,
                description=self._required(description, "description", 500),
                quantity=normalized_quantity,
                unit_price=normalized_price,
                amount=amount,
                updated_at=now,
                version=quote_line.version + 1,
            )
            self._repository.save_quote_line(
                updated, expected_version=expected_version
            )
            self._touch_quote(quote, now)
            audit = self._write_result(
                ctx,
                "CRM.QuoteLine.Update",
                QUOTE_LINE_RESOURCE,
                quote_line_id,
                "ok",
            )
            return KernelResult.success(updated, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT, "quote line version conflict"
            )

    def archive_quote_line(
        self,
        ctx: ExecutionContext,
        *,
        quote_id: UUID,
        quote_line_id: UUID,
        reason: str,
        expected_version: int,
    ) -> KernelResult[QuoteLine]:
        try:
            self._write_intent(
                ctx,
                "CRM.QuoteLine.Archive",
                QUOTE_LINE_RESOURCE,
                quote_line_id,
            )
            denied = self._authorize(
                ctx, "archive", QUOTE_LINE_RESOURCE, quote_line_id
            )
            if denied is not None:
                return self._write_denied(
                    ctx, "CRM.QuoteLine.Archive", quote_line_id, denied
                )
            self._required(reason, "reason", 500)
            quote = self._draft_quote(quote_id)
            quote_line = self._active_quote_line(quote_id, quote_line_id)
            self._expected_version(quote_line.version, expected_version)
            now = datetime.now(timezone.utc)
            archived = replace(
                quote_line,
                status=QuoteLineStatus.ARCHIVED,
                archived_at=now,
                updated_at=now,
                version=quote_line.version + 1,
            )
            self._repository.save_quote_line(
                archived, expected_version=expected_version
            )
            self._touch_quote(quote, now)
            audit = self._write_result(
                ctx,
                "CRM.QuoteLine.Archive",
                QUOTE_LINE_RESOURCE,
                quote_line_id,
                "ok",
            )
            return KernelResult.success(archived, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT, "quote line version conflict"
            )

    def confirm_sales_order(
        self,
        ctx: ExecutionContext,
        *,
        sales_order_id: UUID,
        idempotency_key: UUID,
        human_confirm: bool,
        approval_ref: str | None = None,
    ) -> KernelResult[SalesOrder]:
        try:
            self._write_intent(
                ctx,
                "CRM.SalesOrder.Confirm",
                SALES_ORDER_RESOURCE,
                sales_order_id,
            )
            denied = self._authorize(
                ctx, "confirm", SALES_ORDER_RESOURCE, sales_order_id
            )
            if denied is not None:
                return self._write_denied(
                    ctx, "CRM.SalesOrder.Confirm", sales_order_id, denied
                )
            sales_order = self._repository.get_sales_order(sales_order_id)
            if sales_order is None:
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND, "sales order not found"
                )
            if sales_order.status == SalesOrderStatus.CONFIRMED:
                if sales_order.confirmation_key != idempotency_key:
                    raise KernelError(
                        ErrorCode.COMMON_CONFLICT,
                        "sales order is already confirmed",
                    )
                audit = self._write_result(
                    ctx,
                    "CRM.SalesOrder.Confirm",
                    SALES_ORDER_RESOURCE,
                    sales_order.id,
                    "ok",
                )
                return KernelResult.success(sales_order, audit_id=audit.id)
            if not human_confirm:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "human confirmation is required",
                )
            self._assert_commercially_clear_for_requirement(
                sales_order.requirement_id
            )
            conversion = self._repository.get_conversion(
                sales_order.conversion_id
            )
            if conversion is None or conversion.status != ConversionStatus.CONSUMED:
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "sales order conversion trace is not consumed",
                )
            quote = self._readable_quote(sales_order.quote_id)
            if quote.version != conversion.quote_version:
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "quote changed after conversion instruction",
                )
            quote_lines = [
                item
                for item in self._repository.list_quote_lines(quote.id)
                if item.status == QuoteLineStatus.ACTIVE
            ]
            if not quote_lines:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "at least one active quote line is required",
                )
            now = datetime.now(timezone.utc)
            snapshots = [
                SalesOrderLine(
                    id=uuid4(),
                    tenant_id=self._tenant_id(ctx),
                    sales_order_id=sales_order.id,
                    line_number=item.line_number,
                    description=item.description,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    amount=item.amount,
                    created_at=now,
                )
                for item in quote_lines
            ]
            total_amount = sum(
                (item.amount for item in snapshots), Decimal("0.00")
            ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            blocked = self._assert_confirm_approval(
                ctx,
                sales_order_id=sales_order.id,
                requirement_id=sales_order.requirement_id,
                total_amount=total_amount,
            )
            if blocked is not None:
                return blocked
            workflow_blocked = self._assert_sales_order_confirm_workflow_approval(
                ctx,
                sales_order_id=sales_order.id,
                approval_ref=approval_ref,
            )
            if workflow_blocked is not None:
                return workflow_blocked
            self._repository.add_sales_order_lines(snapshots)
            confirmed = replace(
                sales_order,
                status=SalesOrderStatus.CONFIRMED,
                total_amount=total_amount,
                ordered_quantity=sum(
                    (item.quantity for item in snapshots), Decimal("0.000")
                ),
                confirmed_at=now,
                confirmation_key=idempotency_key,
                version=sales_order.version + 1,
            )
            self._repository.save_sales_order(
                confirmed, expected_version=sales_order.version
            )
            audit = self._write_result(
                ctx,
                "CRM.SalesOrder.Confirm",
                SALES_ORDER_RESOURCE,
                sales_order.id,
                "ok",
            )
            self._emit(
                ctx,
                event_name="crm.sales_order.confirmed",
                payload={
                    "sales_order_id": str(confirmed.id),
                    "tenant_id": str(confirmed.tenant_id),
                },
                tenant_id=confirmed.tenant_id,
            )
            return KernelResult.success(confirmed, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT,
                "sales order confirmation conflict",
            )

    def get_confirm_approval_policy(
        self,
        ctx: ExecutionContext,
    ) -> KernelResult[TenantConfirmPolicy]:
        try:
            denied = self._authorize(ctx, "read", POLICY_RESOURCE)
            if denied is not None:
                return denied
            return KernelResult.success(self._confirm_policy_or_default(ctx))
        except KernelError as err:
            return KernelResult.from_error(err)

    def set_confirm_approval_policy(
        self,
        ctx: ExecutionContext,
        *,
        confirm_approval_required: bool,
        expected_version: int,
    ) -> KernelResult[TenantConfirmPolicy]:
        try:
            self._write_intent(
                ctx,
                "CRM.Policy.ConfirmApproval.Set",
                POLICY_RESOURCE,
                self._tenant_id(ctx),
            )
            denied = self._authorize(ctx, "update", POLICY_RESOURCE)
            if denied is not None:
                return self._write_denied(
                    ctx,
                    "CRM.Policy.ConfirmApproval.Set",
                    self._tenant_id(ctx),
                    denied,
                )
            current = self._repository.get_confirm_policy()
            if current is None:
                if expected_version != 0:
                    raise KernelError(
                        ErrorCode.COMMON_CONFLICT,
                        "confirm policy version conflict",
                    )
                version = 1
            else:
                self._expected_version(current.version, expected_version)
                version = current.version + 1
            policy = TenantConfirmPolicy(
                tenant_id=self._tenant_id(ctx),
                confirm_approval_required=bool(confirm_approval_required),
                quote_issue_approval_required=(
                    current.quote_issue_approval_required
                    if current is not None
                    else False
                ),
                quote_convert_approval_required=(
                    current.quote_convert_approval_required
                    if current is not None
                    else False
                ),
                so_confirm_workflow_approval_required=(
                    current.so_confirm_workflow_approval_required
                    if current is not None
                    else False
                ),
                do_ship_approval_required=(
                    current.do_ship_approval_required if current is not None else False
                ),
                do_release_approval_required=(
                    current.do_release_approval_required
                    if current is not None
                    else False
                ),
                updated_at=datetime.now(timezone.utc),
                version=version,
            )
            self._repository.save_confirm_policy(
                policy, expected_version=expected_version
            )
            audit = self._write_result(
                ctx,
                "CRM.Policy.ConfirmApproval.Set",
                POLICY_RESOURCE,
                policy.tenant_id,
                "ok",
            )
            return KernelResult.success(policy, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT,
                "confirm policy version conflict",
            )

    def get_quote_issue_approval_policy(
        self,
        ctx: ExecutionContext,
    ) -> KernelResult[TenantConfirmPolicy]:
        return self.get_confirm_approval_policy(ctx)

    def set_quote_issue_approval_policy(
        self,
        ctx: ExecutionContext,
        *,
        quote_issue_approval_required: bool,
        expected_version: int,
    ) -> KernelResult[TenantConfirmPolicy]:
        try:
            self._write_intent(
                ctx,
                "CRM.Policy.QuoteIssueApproval.Set",
                POLICY_RESOURCE,
                self._tenant_id(ctx),
            )
            denied = self._authorize(ctx, "update", POLICY_RESOURCE)
            if denied is not None:
                return self._write_denied(
                    ctx,
                    "CRM.Policy.QuoteIssueApproval.Set",
                    self._tenant_id(ctx),
                    denied,
                )
            current = self._repository.get_confirm_policy()
            if current is None:
                if expected_version != 0:
                    raise KernelError(
                        ErrorCode.COMMON_CONFLICT,
                        "quote issue approval policy version conflict",
                    )
                version = 1
            else:
                self._expected_version(current.version, expected_version)
                version = current.version + 1
            policy = TenantConfirmPolicy(
                tenant_id=self._tenant_id(ctx),
                confirm_approval_required=(
                    current.confirm_approval_required if current is not None else False
                ),
                quote_issue_approval_required=bool(quote_issue_approval_required),
                quote_convert_approval_required=(
                    current.quote_convert_approval_required
                    if current is not None
                    else False
                ),
                so_confirm_workflow_approval_required=(
                    current.so_confirm_workflow_approval_required
                    if current is not None
                    else False
                ),
                do_ship_approval_required=(
                    current.do_ship_approval_required if current is not None else False
                ),
                do_release_approval_required=(
                    current.do_release_approval_required
                    if current is not None
                    else False
                ),
                updated_at=datetime.now(timezone.utc),
                version=version,
            )
            self._repository.save_confirm_policy(
                policy, expected_version=expected_version
            )
            audit = self._write_result(
                ctx,
                "CRM.Policy.QuoteIssueApproval.Set",
                POLICY_RESOURCE,
                policy.tenant_id,
                "ok",
            )
            return KernelResult.success(policy, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT,
                "quote issue approval policy version conflict",
            )

    def get_quote_convert_approval_policy(
        self,
        ctx: ExecutionContext,
    ) -> KernelResult[TenantConfirmPolicy]:
        return self.get_confirm_approval_policy(ctx)

    def set_quote_convert_approval_policy(
        self,
        ctx: ExecutionContext,
        *,
        quote_convert_approval_required: bool,
        expected_version: int,
    ) -> KernelResult[TenantConfirmPolicy]:
        try:
            self._write_intent(
                ctx,
                "CRM.Policy.QuoteConvertApproval.Set",
                POLICY_RESOURCE,
                self._tenant_id(ctx),
            )
            denied = self._authorize(ctx, "update", POLICY_RESOURCE)
            if denied is not None:
                return self._write_denied(
                    ctx,
                    "CRM.Policy.QuoteConvertApproval.Set",
                    self._tenant_id(ctx),
                    denied,
                )
            current = self._repository.get_confirm_policy()
            if current is None:
                if expected_version != 0:
                    raise KernelError(
                        ErrorCode.COMMON_CONFLICT,
                        "quote convert approval policy version conflict",
                    )
                version = 1
            else:
                self._expected_version(current.version, expected_version)
                version = current.version + 1
            policy = TenantConfirmPolicy(
                tenant_id=self._tenant_id(ctx),
                confirm_approval_required=(
                    current.confirm_approval_required if current is not None else False
                ),
                quote_issue_approval_required=(
                    current.quote_issue_approval_required
                    if current is not None
                    else False
                ),
                quote_convert_approval_required=bool(
                    quote_convert_approval_required
                ),
                so_confirm_workflow_approval_required=(
                    current.so_confirm_workflow_approval_required
                    if current is not None
                    else False
                ),
                do_ship_approval_required=(
                    current.do_ship_approval_required if current is not None else False
                ),
                do_release_approval_required=(
                    current.do_release_approval_required
                    if current is not None
                    else False
                ),
                updated_at=datetime.now(timezone.utc),
                version=version,
            )
            self._repository.save_confirm_policy(
                policy, expected_version=expected_version
            )
            audit = self._write_result(
                ctx,
                "CRM.Policy.QuoteConvertApproval.Set",
                POLICY_RESOURCE,
                policy.tenant_id,
                "ok",
            )
            return KernelResult.success(policy, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT,
                "quote convert approval policy version conflict",
            )

    def get_so_confirm_workflow_approval_policy(
        self,
        ctx: ExecutionContext,
    ) -> KernelResult[TenantConfirmPolicy]:
        return self.get_confirm_approval_policy(ctx)

    def set_so_confirm_workflow_approval_policy(
        self,
        ctx: ExecutionContext,
        *,
        so_confirm_workflow_approval_required: bool,
        expected_version: int,
    ) -> KernelResult[TenantConfirmPolicy]:
        try:
            self._write_intent(
                ctx,
                "CRM.Policy.SalesOrderConfirmWorkflowApproval.Set",
                POLICY_RESOURCE,
                self._tenant_id(ctx),
            )
            denied = self._authorize(ctx, "update", POLICY_RESOURCE)
            if denied is not None:
                return self._write_denied(
                    ctx,
                    "CRM.Policy.SalesOrderConfirmWorkflowApproval.Set",
                    self._tenant_id(ctx),
                    denied,
                )
            current = self._repository.get_confirm_policy()
            if current is None:
                if expected_version != 0:
                    raise KernelError(
                        ErrorCode.COMMON_CONFLICT,
                        "SO confirm workflow approval policy version conflict",
                    )
                version = 1
            else:
                self._expected_version(current.version, expected_version)
                version = current.version + 1
            policy = TenantConfirmPolicy(
                tenant_id=self._tenant_id(ctx),
                confirm_approval_required=(
                    current.confirm_approval_required if current is not None else False
                ),
                quote_issue_approval_required=(
                    current.quote_issue_approval_required
                    if current is not None
                    else False
                ),
                quote_convert_approval_required=(
                    current.quote_convert_approval_required
                    if current is not None
                    else False
                ),
                so_confirm_workflow_approval_required=bool(
                    so_confirm_workflow_approval_required
                ),
                do_ship_approval_required=(
                    current.do_ship_approval_required if current is not None else False
                ),
                do_release_approval_required=(
                    current.do_release_approval_required
                    if current is not None
                    else False
                ),
                updated_at=datetime.now(timezone.utc),
                version=version,
            )
            self._repository.save_confirm_policy(
                policy, expected_version=expected_version
            )
            audit = self._write_result(
                ctx,
                "CRM.Policy.SalesOrderConfirmWorkflowApproval.Set",
                POLICY_RESOURCE,
                policy.tenant_id,
                "ok",
            )
            return KernelResult.success(policy, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT,
                "SO confirm workflow approval policy version conflict",
            )

    def get_do_ship_approval_policy(
        self,
        ctx: ExecutionContext,
    ) -> KernelResult[TenantConfirmPolicy]:
        return self.get_confirm_approval_policy(ctx)

    def set_do_ship_approval_policy(
        self,
        ctx: ExecutionContext,
        *,
        do_ship_approval_required: bool,
        expected_version: int,
    ) -> KernelResult[TenantConfirmPolicy]:
        try:
            self._write_intent(
                ctx,
                "CRM.Policy.DeliveryOrderShipApproval.Set",
                POLICY_RESOURCE,
                self._tenant_id(ctx),
            )
            denied = self._authorize(ctx, "update", POLICY_RESOURCE)
            if denied is not None:
                return self._write_denied(
                    ctx,
                    "CRM.Policy.DeliveryOrderShipApproval.Set",
                    self._tenant_id(ctx),
                    denied,
                )
            current = self._repository.get_confirm_policy()
            if current is None:
                if expected_version != 0:
                    raise KernelError(
                        ErrorCode.COMMON_CONFLICT,
                        "DO ship approval policy version conflict",
                    )
                version = 1
            else:
                self._expected_version(current.version, expected_version)
                version = current.version + 1
            policy = TenantConfirmPolicy(
                tenant_id=self._tenant_id(ctx),
                confirm_approval_required=(
                    current.confirm_approval_required if current is not None else False
                ),
                quote_issue_approval_required=(
                    current.quote_issue_approval_required
                    if current is not None
                    else False
                ),
                quote_convert_approval_required=(
                    current.quote_convert_approval_required
                    if current is not None
                    else False
                ),
                so_confirm_workflow_approval_required=(
                    current.so_confirm_workflow_approval_required
                    if current is not None
                    else False
                ),
                do_ship_approval_required=bool(do_ship_approval_required),
                do_release_approval_required=(
                    current.do_release_approval_required
                    if current is not None
                    else False
                ),
                updated_at=datetime.now(timezone.utc),
                version=version,
            )
            self._repository.save_confirm_policy(
                policy, expected_version=expected_version
            )
            audit = self._write_result(
                ctx,
                "CRM.Policy.DeliveryOrderShipApproval.Set",
                POLICY_RESOURCE,
                policy.tenant_id,
                "ok",
            )
            return KernelResult.success(policy, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT,
                "DO ship approval policy version conflict",
            )

    def get_do_release_approval_policy(
        self,
        ctx: ExecutionContext,
    ) -> KernelResult[TenantConfirmPolicy]:
        return self.get_confirm_approval_policy(ctx)

    def set_do_release_approval_policy(
        self,
        ctx: ExecutionContext,
        *,
        do_release_approval_required: bool,
        expected_version: int,
    ) -> KernelResult[TenantConfirmPolicy]:
        try:
            self._write_intent(
                ctx,
                "CRM.Policy.DeliveryOrderReleaseApproval.Set",
                POLICY_RESOURCE,
                self._tenant_id(ctx),
            )
            denied = self._authorize(ctx, "update", POLICY_RESOURCE)
            if denied is not None:
                return self._write_denied(
                    ctx,
                    "CRM.Policy.DeliveryOrderReleaseApproval.Set",
                    self._tenant_id(ctx),
                    denied,
                )
            current = self._repository.get_confirm_policy()
            if current is None:
                if expected_version != 0:
                    raise KernelError(
                        ErrorCode.COMMON_CONFLICT,
                        "DO release approval policy version conflict",
                    )
                version = 1
            else:
                self._expected_version(current.version, expected_version)
                version = current.version + 1
            policy = TenantConfirmPolicy(
                tenant_id=self._tenant_id(ctx),
                confirm_approval_required=(
                    current.confirm_approval_required if current is not None else False
                ),
                quote_issue_approval_required=(
                    current.quote_issue_approval_required
                    if current is not None
                    else False
                ),
                quote_convert_approval_required=(
                    current.quote_convert_approval_required
                    if current is not None
                    else False
                ),
                so_confirm_workflow_approval_required=(
                    current.so_confirm_workflow_approval_required
                    if current is not None
                    else False
                ),
                do_ship_approval_required=(
                    current.do_ship_approval_required if current is not None else False
                ),
                do_release_approval_required=bool(do_release_approval_required),
                updated_at=datetime.now(timezone.utc),
                version=version,
            )
            self._repository.save_confirm_policy(
                policy, expected_version=expected_version
            )
            audit = self._write_result(
                ctx,
                "CRM.Policy.DeliveryOrderReleaseApproval.Set",
                POLICY_RESOURCE,
                policy.tenant_id,
                "ok",
            )
            return KernelResult.success(policy, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT,
                "DO release approval policy version conflict",
            )

    def list_sales_order_lines(
        self,
        ctx: ExecutionContext,
        *,
        sales_order_id: UUID,
    ) -> KernelResult[list[SalesOrderLine]]:
        try:
            denied = self._authorize(
                ctx, "read", SALES_ORDER_RESOURCE, sales_order_id
            )
            if denied is not None:
                return denied
            sales_order = self._repository.get_sales_order(sales_order_id)
            if sales_order is None:
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND, "sales order not found"
                )
            return KernelResult.success(
                self._repository.list_sales_order_lines(sales_order.id)
            )
        except KernelError as err:
            return KernelResult.from_error(err)

    def create_delivery_order(
        self,
        ctx: ExecutionContext,
        *,
        sales_order_id: UUID,
        idempotency_key: UUID,
        line_quantities: list[tuple[UUID, Decimal]] | None = None,
    ) -> KernelResult[DeliveryOrder]:
        delivery_order_id = uuid4()
        try:
            self._write_intent(
                ctx,
                "CRM.DeliveryOrder.Create",
                DELIVERY_ORDER_RESOURCE,
                delivery_order_id,
            )
            denied = self._authorize(
                ctx, "create", DELIVERY_ORDER_RESOURCE, sales_order_id
            )
            if denied is not None:
                return self._write_denied(
                    ctx, "CRM.DeliveryOrder.Create", delivery_order_id, denied
                )
            sales_order = self._repository.get_sales_order(sales_order_id)
            if sales_order is None:
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND, "sales order not found"
                )
            existing = self._repository.get_delivery_order_by_idempotency_key(
                idempotency_key
            )
            if existing is not None:
                if existing.sales_order_id != sales_order.id:
                    raise KernelError(
                        ErrorCode.COMMON_CONFLICT,
                        "delivery order idempotency key was used for another order",
                    )
                audit = self._write_result(
                    ctx,
                    "CRM.DeliveryOrder.Create",
                    DELIVERY_ORDER_RESOURCE,
                    existing.id,
                    "ok",
                )
                return KernelResult.success(existing, audit_id=audit.id)
            if sales_order.status not in (
                SalesOrderStatus.CONFIRMED,
                SalesOrderStatus.PARTIALLY_SHIPPED,
            ):
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "sales order must have remaining confirmed quantity",
                )
            self._assert_commercially_clear_for_requirement(
                sales_order.requirement_id
            )
            sales_order_lines = self._repository.list_sales_order_lines(
                sales_order.id
            )
            requested = dict(line_quantities or [])
            if line_quantities is not None and len(requested) != len(line_quantities):
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "delivery order lines must not repeat sales order lines",
                )
            if not requested:
                requested = {line.id: line.quantity for line in sales_order_lines}
            if not requested:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "sales order has no shippable lines",
                )
            order_lines = {line.id: line for line in sales_order_lines}
            shipped_by_line: dict[UUID, Decimal] = {}
            for existing_do in self._repository.list_delivery_orders_by_sales_order(
                sales_order.id
            ):
                if existing_do.status != DeliveryOrderStatus.SHIPPED:
                    continue
                for line in self._repository.list_delivery_order_lines(existing_do.id):
                    shipped_by_line[line.sales_order_line_id] = (
                        shipped_by_line.get(line.sales_order_line_id, Decimal("0"))
                        + line.quantity
                    )
            delivery_lines: list[DeliveryOrderLine] = []
            for line_id, quantity in requested.items():
                order_line = order_lines.get(line_id)
                if order_line is None:
                    raise KernelError(
                        ErrorCode.COMMON_VALIDATION_FAILED,
                        "delivery order line is not on the sales order",
                    )
                normalized = self._line_quantity(quantity)
                remaining = order_line.quantity - shipped_by_line.get(
                    line_id, Decimal("0")
                )
                if normalized > remaining:
                    raise KernelError(
                        ErrorCode.COMMON_VALIDATION_FAILED,
                        "delivery order quantity exceeds remaining quantity",
                    )
                delivery_lines.append(
                    DeliveryOrderLine(
                        id=uuid4(),
                        tenant_id=self._tenant_id(ctx),
                        delivery_order_id=delivery_order_id,
                        sales_order_line_id=line_id,
                        quantity=normalized,
                        status=DeliveryOrderLineStatus.OPEN,
                        created_at=datetime.now(timezone.utc),
                    )
                )
            total_amount = sum(
                (
                    (order_lines[line.sales_order_line_id].unit_price * line.quantity)
                    for line in delivery_lines
                ),
                Decimal("0.00"),
            ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            delivery_order = DeliveryOrder(
                id=delivery_order_id,
                tenant_id=self._tenant_id(ctx),
                sales_order_id=sales_order.id,
                sales_order_version=sales_order.version,
                quote_id=sales_order.quote_id,
                requirement_id=sales_order.requirement_id,
                code=f"DO-{delivery_order_id.hex[:12].upper()}",
                currency=sales_order.currency,
                total_amount=total_amount,
                idempotency_key=idempotency_key,
                status=DeliveryOrderStatus.DRAFT,
                created_at=datetime.now(timezone.utc),
            )
            self._repository.add_delivery_order(delivery_order)
            self._repository.add_delivery_order_lines(delivery_lines)
            audit = self._write_result(
                ctx,
                "CRM.DeliveryOrder.Create",
                DELIVERY_ORDER_RESOURCE,
                delivery_order.id,
                "ok",
            )
            return KernelResult.success(delivery_order, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT,
                "delivery order persistence conflict",
            )

    def get_delivery_order(
        self,
        ctx: ExecutionContext,
        *,
        delivery_order_id: UUID,
    ) -> KernelResult[DeliveryOrder]:
        try:
            denied = self._authorize(
                ctx, "read", DELIVERY_ORDER_RESOURCE, delivery_order_id
            )
            if denied is not None:
                return denied
            delivery_order = self._repository.get_delivery_order(
                delivery_order_id
            )
            if delivery_order is None:
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND, "delivery order not found"
                )
            return KernelResult.success(delivery_order)
        except KernelError as err:
            return KernelResult.from_error(err)

    def release_delivery_order(
        self,
        ctx: ExecutionContext,
        *,
        delivery_order_id: UUID,
        idempotency_key: UUID,
        human_confirm: bool,
        approval_ref: str | None = None,
    ) -> KernelResult[DeliveryOrder]:
        try:
            self._write_intent(
                ctx,
                "CRM.DeliveryOrder.Release",
                DELIVERY_ORDER_RESOURCE,
                delivery_order_id,
            )
            denied = self._authorize(
                ctx, "release", DELIVERY_ORDER_RESOURCE, delivery_order_id
            )
            if denied is not None:
                return self._write_denied(
                    ctx, "CRM.DeliveryOrder.Release", delivery_order_id, denied
                )
            delivery_order = self._repository.get_delivery_order(
                delivery_order_id
            )
            if delivery_order is None:
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND, "delivery order not found"
                )
            if delivery_order.status == DeliveryOrderStatus.RELEASED:
                if delivery_order.release_key != idempotency_key:
                    raise KernelError(
                        ErrorCode.COMMON_CONFLICT,
                        "delivery order is already released",
                    )
                audit = self._write_result(
                    ctx,
                    "CRM.DeliveryOrder.Release",
                    DELIVERY_ORDER_RESOURCE,
                    delivery_order.id,
                    "ok",
                )
                return KernelResult.success(delivery_order, audit_id=audit.id)
            if delivery_order.status != DeliveryOrderStatus.DRAFT:
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "delivery order cannot be released",
                )
            if not human_confirm:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "human confirmation is required",
                )
            sales_order = self._repository.get_sales_order(
                delivery_order.sales_order_id
            )
            if (
                sales_order is None
                or sales_order.status
                not in (
                    SalesOrderStatus.CONFIRMED,
                    SalesOrderStatus.PARTIALLY_SHIPPED,
                )
            ):
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "sales order must be confirmed",
                )
            self._assert_commercially_clear_for_requirement(
                delivery_order.requirement_id
            )
            workflow_blocked = self._assert_delivery_order_release_workflow_approval(
                ctx,
                delivery_order_id=delivery_order.id,
                approval_ref=approval_ref,
            )
            if workflow_blocked is not None:
                return workflow_blocked
            now = datetime.now(timezone.utc)
            released = replace(
                delivery_order,
                status=DeliveryOrderStatus.RELEASED,
                released_at=now,
                release_key=idempotency_key,
                version=delivery_order.version + 1,
            )
            self._repository.save_delivery_order(
                released, expected_version=delivery_order.version
            )
            audit = self._write_result(
                ctx,
                "CRM.DeliveryOrder.Release",
                DELIVERY_ORDER_RESOURCE,
                delivery_order_id,
                "ok",
            )
            self._emit(
                ctx,
                event_name="crm.delivery_order.released",
                payload={
                    "delivery_order_id": str(released.id),
                    "sales_order_id": str(released.sales_order_id),
                    "tenant_id": str(released.tenant_id),
                },
                tenant_id=released.tenant_id,
            )
            return KernelResult.success(released, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT, "delivery order release conflict"
            )

    def create_ar_invoice(
        self,
        ctx: ExecutionContext,
        *,
        delivery_order_id: UUID,
        idempotency_key: UUID,
    ) -> KernelResult[ARInvoice]:
        invoice_id = uuid4()
        try:
            self._write_intent(
                ctx,
                "CRM.ARInvoice.Create",
                AR_INVOICE_RESOURCE,
                invoice_id,
            )
            denied = self._authorize(
                ctx, "create", AR_INVOICE_RESOURCE, delivery_order_id
            )
            if denied is not None:
                return self._write_denied(
                    ctx, "CRM.ARInvoice.Create", invoice_id, denied
                )
            delivery_order = self._repository.get_delivery_order(
                delivery_order_id
            )
            if delivery_order is None:
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND, "delivery order not found"
                )
            existing = self._repository.get_ar_invoice_by_delivery_order(
                delivery_order.id
            )
            if existing is not None:
                if existing.idempotency_key != idempotency_key:
                    raise KernelError(
                        ErrorCode.COMMON_CONFLICT,
                        "delivery order already has an AR invoice shell",
                    )
                audit = self._write_result(
                    ctx,
                    "CRM.ARInvoice.Create",
                    AR_INVOICE_RESOURCE,
                    existing.id,
                    "ok",
                )
                return KernelResult.success(existing, audit_id=audit.id)
            if delivery_order.status not in (
                DeliveryOrderStatus.RELEASED,
                DeliveryOrderStatus.SHIPPED,
            ):
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "delivery order must be released",
                )
            sales_order = self._repository.get_sales_order(
                delivery_order.sales_order_id
            )
            if (
                sales_order is None
                or sales_order.status != SalesOrderStatus.CONFIRMED
            ):
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "delivery order must trace a confirmed sales order",
                )
            requirement = self._repository.get_requirement(
                delivery_order.requirement_id
            )
            opportunity = (
                self._repository.get_opportunity(requirement.opportunity_id)
                if requirement is not None
                else None
            )
            if requirement is None or opportunity is None:
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "invoice source trace is incomplete",
                )
            functional_currency = sales_order.functional_currency or sales_order.currency
            fx_rate = sales_order.fx_rate
            if fx_rate is None and functional_currency == sales_order.currency:
                fx_rate = Decimal("1")
            if fx_rate is None:
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "sales order FX snapshot is missing",
                )
            invoice = ARInvoice(
                id=invoice_id,
                tenant_id=self._tenant_id(ctx),
                delivery_order_id=delivery_order.id,
                delivery_order_version=delivery_order.version,
                sales_order_id=sales_order.id,
                sales_order_version=sales_order.version,
                customer_id=opportunity.customer_id,
                code=f"ARI-{invoice_id.hex[:12].upper()}",
                currency=delivery_order.currency,
                total_amount=delivery_order.total_amount,
                idempotency_key=idempotency_key,
                status=ARInvoiceStatus.DRAFT,
                created_at=datetime.now(timezone.utc),
                functional_currency=functional_currency,
                fx_rate=fx_rate,
                functional_total=(delivery_order.total_amount * fx_rate).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                ),
            )
            self._repository.add_ar_invoice(invoice)
            audit = self._write_result(
                ctx,
                "CRM.ARInvoice.Create",
                AR_INVOICE_RESOURCE,
                invoice.id,
                "ok",
            )
            return KernelResult.success(invoice, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT,
                "AR invoice persistence conflict",
            )

    def issue_ar_invoice(
        self,
        ctx: ExecutionContext,
        *,
        invoice_id: UUID,
        idempotency_key: UUID,
        human_confirm: bool,
    ) -> KernelResult[ARInvoice]:
        try:
            self._write_intent(
                ctx,
                "CRM.ARInvoice.Issue",
                AR_INVOICE_RESOURCE,
                invoice_id,
            )
            denied = self._authorize(
                ctx, "issue", AR_INVOICE_RESOURCE, invoice_id
            )
            if denied is not None:
                return self._write_denied(
                    ctx, "CRM.ARInvoice.Issue", invoice_id, denied
                )
            invoice = self._repository.get_ar_invoice(invoice_id)
            if invoice is None:
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND, "AR invoice not found"
                )
            if invoice.status == ARInvoiceStatus.ISSUED:
                if invoice.issue_key != idempotency_key:
                    raise KernelError(
                        ErrorCode.COMMON_CONFLICT,
                        "AR invoice is already issued",
                    )
                audit = self._write_result(
                    ctx,
                    "CRM.ARInvoice.Issue",
                    AR_INVOICE_RESOURCE,
                    invoice.id,
                    "ok",
                )
                return KernelResult.success(invoice, audit_id=audit.id)
            if invoice.status != ARInvoiceStatus.DRAFT:
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "AR invoice cannot be issued",
                )
            if not human_confirm:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "human confirmation is required",
                )
            delivery_order = self._repository.get_delivery_order(
                invoice.delivery_order_id
            )
            if delivery_order is None or delivery_order.status not in (
                DeliveryOrderStatus.RELEASED,
                DeliveryOrderStatus.SHIPPED,
            ):
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "delivery order must be released",
                )
            sales_order = self._repository.get_sales_order(
                invoice.sales_order_id
            )
            if (
                sales_order is None
                or sales_order.status != SalesOrderStatus.CONFIRMED
            ):
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "sales order must be confirmed",
                )
            self._assert_commercially_clear_for_requirement(
                delivery_order.requirement_id
            )
            now = datetime.now(timezone.utc)
            issued = replace(
                invoice,
                status=ARInvoiceStatus.ISSUED,
                issued_at=now,
                issue_key=idempotency_key,
                version=invoice.version + 1,
            )
            self._repository.save_ar_invoice(
                issued, expected_version=invoice.version
            )
            audit = self._write_result(
                ctx,
                "CRM.ARInvoice.Issue",
                AR_INVOICE_RESOURCE,
                invoice_id,
                "ok",
            )
            return KernelResult.success(issued, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT, "AR invoice issue conflict"
            )

    def void_ar_invoice(
        self,
        ctx: ExecutionContext,
        *,
        invoice_id: UUID,
        idempotency_key: UUID,
        human_confirm: bool,
        reason: str,
    ) -> KernelResult[ARInvoice]:
        try:
            self._write_intent(
                ctx,
                "CRM.ARInvoice.Void",
                AR_INVOICE_RESOURCE,
                invoice_id,
            )
            denied = self._authorize(
                ctx, "void", AR_INVOICE_RESOURCE, invoice_id
            )
            if denied is not None:
                return self._write_denied(
                    ctx, "CRM.ARInvoice.Void", invoice_id, denied
                )
            invoice = self._repository.get_ar_invoice(invoice_id)
            if invoice is None:
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND, "AR invoice not found"
                )
            if invoice.status == ARInvoiceStatus.VOIDED:
                if invoice.void_key != idempotency_key:
                    raise KernelError(
                        ErrorCode.COMMON_CONFLICT,
                        "AR invoice is already voided",
                    )
                audit = self._write_result(
                    ctx,
                    "CRM.ARInvoice.Void",
                    AR_INVOICE_RESOURCE,
                    invoice.id,
                    "ok",
                )
                return KernelResult.success(invoice, audit_id=audit.id)
            if invoice.status != ARInvoiceStatus.ISSUED:
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "only issued invoices can be voided",
                )
            if not human_confirm:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "human confirmation is required",
                )
            normalized_reason = reason.strip() if isinstance(reason, str) else ""
            if not normalized_reason or len(normalized_reason) > 500:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "void reason is required",
                )
            now = datetime.now(timezone.utc)
            voided = replace(
                invoice,
                status=ARInvoiceStatus.VOIDED,
                voided_at=now,
                void_key=idempotency_key,
                void_reason=normalized_reason,
                version=invoice.version + 1,
            )
            self._repository.save_ar_invoice(
                voided, expected_version=invoice.version
            )
            audit = self._write_result(
                ctx,
                "CRM.ARInvoice.Void",
                AR_INVOICE_RESOURCE,
                invoice_id,
                "ok",
            )
            return KernelResult.success(voided, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT, "AR invoice void conflict"
            )

    def get_ar_invoice(
        self,
        ctx: ExecutionContext,
        *,
        invoice_id: UUID,
    ) -> KernelResult[ARInvoice]:
        try:
            denied = self._authorize(
                ctx, "read", AR_INVOICE_RESOURCE, invoice_id
            )
            if denied is not None:
                return denied
            invoice = self._repository.get_ar_invoice(invoice_id)
            if invoice is None:
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND, "AR invoice not found"
                )
            return KernelResult.success(invoice)
        except KernelError as err:
            return KernelResult.from_error(err)

    def create_return_authorization(
        self,
        ctx: ExecutionContext,
        *,
        delivery_order_id: UUID,
        reason: str,
        idempotency_key: UUID,
        human_confirm: bool,
        invoice_id: UUID | None = None,
    ) -> KernelResult[ReturnAuthorization]:
        authorization_id = uuid4()
        try:
            self._write_intent(
                ctx,
                "CRM.ReturnAuthorization.Create",
                RETURN_AUTHORIZATION_RESOURCE,
                authorization_id,
            )
            denied = self._authorize(
                ctx,
                "create",
                RETURN_AUTHORIZATION_RESOURCE,
                delivery_order_id,
            )
            if denied is not None:
                return self._write_denied(
                    ctx,
                    "CRM.ReturnAuthorization.Create",
                    authorization_id,
                    denied,
                )
            if not human_confirm:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "human confirmation is required",
                )
            normalized_reason = self._required(reason, "reason", 500)
            delivery_order = self._repository.get_delivery_order(
                delivery_order_id
            )
            if delivery_order is None:
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND, "delivery order not found"
                )
            if delivery_order.status != DeliveryOrderStatus.SHIPPED:
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "delivery order must be shipped",
                )
            if invoice_id is not None:
                invoice = self._repository.get_ar_invoice(invoice_id)
                if invoice is None:
                    raise KernelError(
                        ErrorCode.COMMON_NOT_FOUND, "AR invoice not found"
                    )
                if invoice.status not in (
                    ARInvoiceStatus.ISSUED,
                    ARInvoiceStatus.VOIDED,
                ):
                    raise KernelError(
                        ErrorCode.COMMON_CONFLICT,
                        "AR invoice must be issued or voided",
                    )
                if (
                    invoice.delivery_order_id != delivery_order.id
                    or invoice.sales_order_id != delivery_order.sales_order_id
                ):
                    raise KernelError(
                        ErrorCode.COMMON_CONFLICT,
                        "AR invoice is not on the same commercial lineage",
                    )
            existing = self._repository.get_return_authorization_by_delivery_order(
                delivery_order.id
            )
            if existing is not None:
                if (
                    existing.idempotency_key != idempotency_key
                    or existing.reason != normalized_reason
                    or existing.invoice_id != invoice_id
                ):
                    raise KernelError(
                        ErrorCode.COMMON_CONFLICT,
                        "delivery order already has a return authorization",
                    )
                audit = self._write_result(
                    ctx,
                    "CRM.ReturnAuthorization.Create",
                    RETURN_AUTHORIZATION_RESOURCE,
                    existing.id,
                    "ok",
                )
                return KernelResult.success(existing, audit_id=audit.id)
            existing_key = (
                self._repository.get_return_authorization_by_idempotency_key(
                    idempotency_key
                )
            )
            if existing_key is not None:
                if (
                    existing_key.delivery_order_id != delivery_order.id
                    or existing_key.reason != normalized_reason
                    or existing_key.invoice_id != invoice_id
                ):
                    raise KernelError(
                        ErrorCode.COMMON_CONFLICT,
                        "return authorization idempotency key was used "
                        "for another request",
                    )
                audit = self._write_result(
                    ctx,
                    "CRM.ReturnAuthorization.Create",
                    RETURN_AUTHORIZATION_RESOURCE,
                    existing_key.id,
                    "ok",
                )
                return KernelResult.success(existing_key, audit_id=audit.id)
            authorization = ReturnAuthorization(
                id=authorization_id,
                tenant_id=self._tenant_id(ctx),
                delivery_order_id=delivery_order.id,
                invoice_id=invoice_id,
                code=f"RA-{authorization_id.hex[:12].upper()}",
                reason=normalized_reason,
                idempotency_key=idempotency_key,
                status=ReturnAuthorizationStatus.DRAFT,
                created_at=datetime.now(timezone.utc),
            )
            self._repository.add_return_authorization(authorization)
            audit = self._write_result(
                ctx,
                "CRM.ReturnAuthorization.Create",
                RETURN_AUTHORIZATION_RESOURCE,
                authorization.id,
                "ok",
            )
            return KernelResult.success(authorization, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT,
                "return authorization persistence conflict",
            )

    def get_return_authorization(
        self,
        ctx: ExecutionContext,
        *,
        return_authorization_id: UUID,
    ) -> KernelResult[ReturnAuthorization]:
        try:
            denied = self._authorize(
                ctx,
                "read",
                RETURN_AUTHORIZATION_RESOURCE,
                return_authorization_id,
            )
            if denied is not None:
                return denied
            authorization = self._repository.get_return_authorization(
                return_authorization_id
            )
            if authorization is None:
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND,
                    "return authorization not found",
                )
            return KernelResult.success(authorization)
        except KernelError as err:
            return KernelResult.from_error(err)

    def create_credit_note_from_return_authorization(
        self,
        ctx: ExecutionContext,
        *,
        return_authorization_id: UUID,
        amount: Decimal,
        idempotency_key: UUID,
        human_confirm: bool = True,
    ) -> KernelResult[ReturnAuthorization]:
        try:
            self._write_intent(
                ctx,
                "Crm.ReturnAuthorization.CreateCreditNote",
                RETURN_AUTHORIZATION_RESOURCE,
                return_authorization_id,
            )
            denied = self._authorize(
                ctx,
                "create_credit_note",
                RETURN_AUTHORIZATION_RESOURCE,
                return_authorization_id,
            )
            if denied is not None:
                return self._write_denied(
                    ctx,
                    "Crm.ReturnAuthorization.CreateCreditNote",
                    return_authorization_id,
                    denied,
                )
            if not human_confirm:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "human confirmation is required",
                )
            if self._credit_note_create_port is None:
                raise KernelError(
                    ErrorCode.COMMON_INTERNAL,
                    "credit note create port is not configured",
                )
            authorization = self._repository.get_return_authorization(
                return_authorization_id
            )
            if authorization is None:
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND, "return authorization not found"
                )
            if authorization.credit_note_id is not None:
                audit = self._write_result(
                    ctx,
                    "Crm.ReturnAuthorization.CreateCreditNote",
                    RETURN_AUTHORIZATION_RESOURCE,
                    authorization.id,
                    "ok",
                )
                return KernelResult.success(authorization, audit_id=audit.id)
            if authorization.status != ReturnAuthorizationStatus.RESTOCKED:
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "return authorization must be restocked",
                )
            if authorization.invoice_id is None:
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "return authorization must reference an AR invoice",
                )
            invoice = self._repository.get_ar_invoice(authorization.invoice_id)
            if invoice is None:
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND, "AR invoice not found"
                )
            normalized_amount = self._credit_amount(amount)
            if normalized_amount > invoice.total_amount:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "credit note amount exceeds AR invoice total",
                )
            credit_note = self._credit_note_create_port.create_credit_note(
                ctx,
                invoice_id=invoice.id,
                amount=normalized_amount,
                idempotency_key=idempotency_key,
            )
            if not credit_note.ok:
                return KernelResult.failure(
                    credit_note.error_code or ErrorCode.COMMON_INTERNAL,
                    credit_note.error_message or "credit note creation failed",
                    details=credit_note.details,
                )
            if credit_note.data is None:
                raise KernelError(
                    ErrorCode.COMMON_INTERNAL,
                    "credit note create port returned no credit note",
                )
            linked = replace(
                authorization,
                credit_note_id=credit_note.data,
                credit_note_key=idempotency_key,
                version=authorization.version + 1,
            )
            self._repository.save_return_authorization(
                linked, expected_version=authorization.version
            )
            audit = self._write_result(
                ctx,
                "Crm.ReturnAuthorization.CreateCreditNote",
                RETURN_AUTHORIZATION_RESOURCE,
                linked.id,
                "ok",
            )
            return KernelResult.success(linked, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT,
                "return authorization credit note link conflict",
            )

    def restock_return_authorization(
        self,
        ctx: ExecutionContext,
        *,
        return_authorization_id: UUID,
        human_confirm: bool,
        idempotency_key: UUID,
        quantity: Decimal | None = None,
    ) -> KernelResult[ReturnAuthorization]:
        try:
            self._write_intent(
                ctx,
                "CRM.ReturnAuthorization.Restock",
                RETURN_AUTHORIZATION_RESOURCE,
                return_authorization_id,
            )
            denied = self._authorize(
                ctx,
                "restock",
                RETURN_AUTHORIZATION_RESOURCE,
                return_authorization_id,
            )
            if denied is not None:
                return self._write_denied(
                    ctx,
                    "CRM.ReturnAuthorization.Restock",
                    return_authorization_id,
                    denied,
                )
            if not human_confirm:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "human confirmation is required",
                )
            if self._return_restock_port is None:
                raise KernelError(
                    ErrorCode.COMMON_INTERNAL,
                    "return restock port is not configured",
                )
            authorization = self._repository.get_return_authorization(
                return_authorization_id
            )
            if authorization is None:
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND,
                    "return authorization not found",
                )
            if authorization.status == ReturnAuthorizationStatus.RESTOCKED:
                if authorization.restock_key != idempotency_key:
                    raise KernelError(
                        ErrorCode.COMMON_CONFLICT,
                        "return authorization is already restocked",
                    )
                audit = self._write_result(
                    ctx,
                    "CRM.ReturnAuthorization.Restock",
                    RETURN_AUTHORIZATION_RESOURCE,
                    authorization.id,
                    "ok",
                )
                return KernelResult.success(authorization, audit_id=audit.id)
            if authorization.status != ReturnAuthorizationStatus.DRAFT:
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "return authorization is not draft",
                )
            shipped = self._return_restock_port.shipped_line_quantities(
                authorization.delivery_order_id
            )
            if not shipped:
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "delivery order has no ship ledger quantity",
                )
            if quantity is not None:
                if len(shipped) != 1:
                    raise KernelError(
                        ErrorCode.COMMON_VALIDATION_FAILED,
                        "quantity is only valid for single-line shipments",
                    )
                normalized = self._restock_quantity(quantity)
                shipped_qty = shipped[0][1]
                if normalized > shipped_qty:
                    raise KernelError(
                        ErrorCode.COMMON_VALIDATION_FAILED,
                        "restock quantity exceeds shipped quantity",
                    )
                if normalized != shipped_qty:
                    raise KernelError(
                        ErrorCode.COMMON_VALIDATION_FAILED,
                        "partial restock is not allowed",
                    )
            now = datetime.now(timezone.utc)
            self._return_restock_port.atomic_rma_restock(
                return_authorization_id=authorization.id,
                delivery_order_id=authorization.delivery_order_id,
                line_quantities=shipped,
                idempotency_key=idempotency_key,
                restocked_at=now,
            )
            restocked = replace(
                authorization,
                status=ReturnAuthorizationStatus.RESTOCKED,
                restocked_at=now,
                restock_key=idempotency_key,
                version=authorization.version + 1,
            )
            self._repository.save_return_authorization(
                restocked, expected_version=authorization.version
            )
            audit = self._write_result(
                ctx,
                "CRM.ReturnAuthorization.Restock",
                RETURN_AUTHORIZATION_RESOURCE,
                authorization.id,
                "ok",
            )
            return KernelResult.success(restocked, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT,
                "return authorization restock conflict",
            )

    def _authorize(
        self,
        ctx: ExecutionContext,
        action: str,
        resource_type: str,
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
                "CRM action is denied by Permission",
                details={
                    "reason_code": (
                        decision.reason_code if decision is not None else "PERMISSION_DENIED"
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
        resource_id: UUID,
        denied: KernelResult,
    ) -> KernelResult:
        if ".Customer." in action:
            resource_type = CUSTOMER_RESOURCE
        elif ".Contact." in action:
            resource_type = CONTACT_RESOURCE
        elif ".Opportunity." in action:
            resource_type = OPPORTUNITY_RESOURCE
        elif ".Requirement." in action:
            resource_type = REQUIREMENT_RESOURCE
        elif ".Quote." in action:
            resource_type = QUOTE_RESOURCE
        elif ".QuoteConversion." in action:
            resource_type = CONVERSION_RESOURCE
        elif ".QuoteLine." in action:
            resource_type = QUOTE_LINE_RESOURCE
        elif ".DeliveryOrder." in action:
            resource_type = DELIVERY_ORDER_RESOURCE
        elif ".ARInvoice." in action:
            resource_type = AR_INVOICE_RESOURCE
        elif ".ReturnAuthorization." in action:
            resource_type = RETURN_AUTHORIZATION_RESOURCE
        elif ".Policy." in action:
            resource_type = POLICY_RESOURCE
        else:
            resource_type = SALES_ORDER_RESOURCE
        audit = self._write_result(
            ctx, action, resource_type, resource_id, "denied"
        )
        return KernelResult.failure(
            denied.error_code or ErrorCode.PERMISSION_DENIED,
            denied.error_message or "CRM action is denied",
            details=denied.details,
            audit_id=audit.id,
        )

    def _active_customer(self, customer_id: UUID) -> Customer:
        customer = self._repository.get_customer(customer_id)
        if customer is None:
            raise KernelError(ErrorCode.COMMON_NOT_FOUND, "customer not found")
        if customer.status != CustomerStatus.ACTIVE:
            raise KernelError(ErrorCode.COMMON_CONFLICT, "customer is archived")
        return customer

    def _assert_commercially_clear_for_requirement(
        self, requirement_id: UUID
    ) -> None:
        customer = self._customer_for_requirement(requirement_id)
        if customer.status != CustomerStatus.ACTIVE:
            raise KernelError(ErrorCode.COMMON_CONFLICT, "customer is archived")
        if customer.commercial_hold:
            raise KernelError(
                ErrorCode.COMMON_CONFLICT,
                "customer is on commercial hold",
            )

    def _confirm_policy_or_default(
        self, ctx: ExecutionContext
    ) -> TenantConfirmPolicy:
        current = self._repository.get_confirm_policy()
        if current is not None:
            return current
        return TenantConfirmPolicy(
            tenant_id=self._tenant_id(ctx),
            confirm_approval_required=False,
            quote_issue_approval_required=False,
            quote_convert_approval_required=False,
            so_confirm_workflow_approval_required=False,
            do_ship_approval_required=False,
            do_release_approval_required=False,
            updated_at=datetime.now(timezone.utc),
            version=0,
        )

    def _customer_for_requirement(self, requirement_id: UUID) -> Customer:
        requirement = self._repository.get_requirement(requirement_id)
        opportunity = (
            self._repository.get_opportunity(requirement.opportunity_id)
            if requirement is not None
            else None
        )
        if requirement is None or opportunity is None:
            raise KernelError(
                ErrorCode.COMMON_CONFLICT,
                "commercial hold source trace is incomplete",
            )
        customer = self._repository.get_customer(opportunity.customer_id)
        if customer is None:
            raise KernelError(
                ErrorCode.COMMON_CONFLICT,
                "commercial hold source trace is incomplete",
            )
        return customer

    def _assert_confirm_approval(
        self,
        ctx: ExecutionContext,
        *,
        sales_order_id: UUID,
        requirement_id: UUID,
        total_amount: Decimal,
    ) -> KernelResult[SalesOrder] | None:
        policy = self._confirm_policy_or_default(ctx)
        if not policy.confirm_approval_required:
            return None
        customer = self._customer_for_requirement(requirement_id)
        gate = self._confirm_approval_gate
        if gate is None:
            decision = ConfirmApprovalDecision.UNAVAILABLE
        else:
            decision = gate.evaluate(
                ctx,
                sales_order_id=sales_order_id,
                customer_id=customer.id,
                total_amount=total_amount,
            )
        if decision == ConfirmApprovalDecision.APPROVED:
            return None
        if decision == ConfirmApprovalDecision.DENIED:
            message = "confirm approval is required"
        else:
            message = "confirm approval gate is unavailable"
        audit = self._write_result(
            ctx,
            "CRM.SalesOrder.Confirm",
            SALES_ORDER_RESOURCE,
            sales_order_id,
            "blocked",
        )
        return KernelResult.failure(
            ErrorCode.COMMON_CONFLICT,
            message,
            audit_id=audit.id,
        )

    def _assert_sales_order_confirm_workflow_approval(
        self,
        ctx: ExecutionContext,
        *,
        sales_order_id: UUID,
        approval_ref: str | None,
    ) -> KernelResult[SalesOrder] | None:
        policy = self._confirm_policy_or_default(ctx)
        if not policy.so_confirm_workflow_approval_required:
            return None
        gate = self._sales_order_confirm_approval_gate
        if gate is None:
            raise KernelError(
                ErrorCode.COMMON_CONFLICT,
                "sales order confirm workflow approval gate is unavailable",
            )
        approved = gate.evaluate(
            ctx,
            sales_order_id=sales_order_id,
            approval_ref=approval_ref,
        )
        if approved.ok:
            return None
        return KernelResult(
            ok=False,
            data=None,
            error_code=approved.error_code,
            error_message=approved.error_message,
            details=approved.details,
        )

    def _assert_delivery_order_release_workflow_approval(
        self,
        ctx: ExecutionContext,
        *,
        delivery_order_id: UUID,
        approval_ref: str | None,
    ) -> KernelResult[DeliveryOrder] | None:
        policy = self._confirm_policy_or_default(ctx)
        if not policy.do_release_approval_required:
            return None
        gate = self._delivery_order_release_approval_gate
        if gate is None:
            raise KernelError(
                ErrorCode.COMMON_CONFLICT,
                "delivery order release workflow approval gate is unavailable",
            )
        approved = gate.evaluate(
            ctx,
            delivery_order_id=delivery_order_id,
            approval_ref=approval_ref,
        )
        if approved.ok:
            return None
        return KernelResult(
            ok=False,
            data=None,
            error_code=approved.error_code,
            error_message=approved.error_message,
            details=approved.details,
        )

    def _active_contact(self, customer_id: UUID, contact_id: UUID) -> Contact:
        contact = self._repository.get_contact(customer_id, contact_id)
        if contact is None:
            raise KernelError(ErrorCode.COMMON_NOT_FOUND, "contact not found")
        if contact.status != ContactStatus.ACTIVE:
            raise KernelError(ErrorCode.COMMON_CONFLICT, "contact is archived")
        return contact

    def _active_opportunity(self, opportunity_id: UUID) -> Opportunity:
        opportunity = self._repository.get_opportunity(opportunity_id)
        if opportunity is None:
            raise KernelError(ErrorCode.COMMON_NOT_FOUND, "opportunity not found")
        if opportunity.status != OpportunityStatus.ACTIVE:
            raise KernelError(ErrorCode.COMMON_CONFLICT, "opportunity is archived")
        return opportunity

    def _active_requirement(self, requirement_id: UUID) -> Requirement:
        requirement = self._repository.get_requirement(requirement_id)
        if requirement is None:
            raise KernelError(ErrorCode.COMMON_NOT_FOUND, "requirement not found")
        if requirement.status != RequirementStatus.ACTIVE:
            raise KernelError(ErrorCode.COMMON_CONFLICT, "requirement is archived")
        return requirement

    def _require_quote(self, quote_id: UUID) -> Quote:
        quote = self._repository.get_quote(quote_id)
        if quote is None:
            raise KernelError(ErrorCode.COMMON_NOT_FOUND, "quote not found")
        return quote

    def _draft_quote(self, quote_id: UUID) -> Quote:
        quote = self._require_quote(quote_id)
        if quote.status == QuoteStatus.ISSUED:
            raise KernelError(ErrorCode.COMMON_CONFLICT, "quote is issued")
        if quote.status != QuoteStatus.DRAFT:
            raise KernelError(ErrorCode.COMMON_CONFLICT, "quote is archived")
        return quote

    def _readable_quote(self, quote_id: UUID) -> Quote:
        quote = self._require_quote(quote_id)
        if quote.status == QuoteStatus.ARCHIVED:
            raise KernelError(ErrorCode.COMMON_CONFLICT, "quote is archived")
        return quote

    def _issued_quote(self, quote_id: UUID) -> Quote:
        quote = self._require_quote(quote_id)
        if quote.status == QuoteStatus.ARCHIVED:
            raise KernelError(ErrorCode.COMMON_CONFLICT, "quote is archived")
        if quote.status != QuoteStatus.ISSUED:
            raise KernelError(ErrorCode.COMMON_CONFLICT, "quote must be issued")
        return quote

    def _archivable_quote(self, quote_id: UUID) -> Quote:
        quote = self._require_quote(quote_id)
        if quote.status == QuoteStatus.ARCHIVED:
            raise KernelError(ErrorCode.COMMON_CONFLICT, "quote is archived")
        return quote

    def _active_quote_line(
        self, quote_id: UUID, quote_line_id: UUID
    ) -> QuoteLine:
        quote_line = self._repository.get_quote_line(quote_id, quote_line_id)
        if quote_line is None:
            raise KernelError(ErrorCode.COMMON_NOT_FOUND, "quote line not found")
        if quote_line.status != QuoteLineStatus.ACTIVE:
            raise KernelError(ErrorCode.COMMON_CONFLICT, "quote line is archived")
        return quote_line

    def _touch_quote(self, quote: Quote, now: datetime) -> None:
        touched = replace(
            quote,
            updated_at=now,
            version=quote.version + 1,
        )
        self._repository.save_quote(touched, expected_version=quote.version)

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
            producer="crm.package",
            payload=payload,
            tenant_id=tenant_id,
        )

    @staticmethod
    def _tenant_id(ctx: ExecutionContext) -> UUID:
        require_context(ctx, tenant_data_plane=True)
        assert ctx.tenant_id is not None
        return ctx.tenant_id

    @staticmethod
    def _expected_version(current: int, expected: int) -> None:
        if expected < 1 or current != expected:
            raise KernelError(ErrorCode.COMMON_CONFLICT, "resource version conflict")

    @staticmethod
    def _required(value: str, field: str, max_length: int) -> str:
        normalized = value.strip()
        if not normalized or len(normalized) > max_length:
            raise KernelError(
                ErrorCode.COMMON_VALIDATION_FAILED,
                f"{field} is required and must be at most {max_length} characters",
            )
        return normalized

    @staticmethod
    def _optional(value: str | None, max_length: int) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            return None
        if len(normalized) > max_length:
            raise KernelError(
                ErrorCode.COMMON_VALIDATION_FAILED,
                f"value must be at most {max_length} characters",
            )
        return normalized

    @staticmethod
    def _currency(value: str) -> str:
        normalized = value.strip().upper()
        if len(normalized) != 3 or not normalized.isascii() or not normalized.isalpha():
            raise KernelError(
                ErrorCode.COMMON_VALIDATION_FAILED,
                "currency must be a three-letter ASCII code",
            )
        return normalized

    @staticmethod
    def _quote_fx(
        *,
        currency: str,
        functional_currency: str | None,
        fx_rate: Decimal | None,
    ) -> tuple[str, Decimal]:
        normalized_functional_currency = CRMService._currency(
            functional_currency or currency
        )
        if normalized_functional_currency == currency:
            if fx_rate is None:
                return normalized_functional_currency, Decimal("1.00000000")
            normalized_rate = CRMService._fx_rate(fx_rate)
            if normalized_rate != Decimal("1.00000000"):
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "same-currency quote must use fx_rate 1",
                )
            return normalized_functional_currency, normalized_rate
        if fx_rate is None:
            raise KernelError(
                ErrorCode.COMMON_VALIDATION_FAILED,
                "fx_rate is required when currencies differ",
            )
        return normalized_functional_currency, CRMService._fx_rate(fx_rate)

    @staticmethod
    def _fx_rate(rate: Decimal) -> Decimal:
        try:
            normalized = Decimal(str(rate)).quantize(
                Decimal("0.00000001"), rounding=ROUND_HALF_UP
            )
        except (InvalidOperation, TypeError, ValueError):
            raise KernelError(
                ErrorCode.COMMON_VALIDATION_FAILED, "fx rate is invalid"
            ) from None
        if not normalized.is_finite() or normalized <= 0:
            raise KernelError(
                ErrorCode.COMMON_VALIDATION_FAILED, "fx rate is invalid"
            )
        return normalized

    @staticmethod
    def _credit_amount(amount: Decimal) -> Decimal:
        try:
            normalized = Decimal(str(amount)).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
        except (InvalidOperation, ValueError) as exc:
            raise KernelError(
                ErrorCode.COMMON_VALIDATION_FAILED,
                "credit note amount is invalid",
            ) from exc
        if normalized <= 0:
            raise KernelError(
                ErrorCode.COMMON_VALIDATION_FAILED,
                "credit note amount must be positive",
            )
        return normalized

    @staticmethod
    def _restock_quantity(quantity: Decimal) -> Decimal:
        try:
            normalized = Decimal(str(quantity)).quantize(
                Decimal("0.001"), rounding=ROUND_HALF_UP
            )
        except (InvalidOperation, ValueError):
            raise KernelError(
                ErrorCode.COMMON_VALIDATION_FAILED,
                "restock quantity must be a finite decimal",
            ) from None
        if not normalized.is_finite() or normalized <= 0:
            raise KernelError(
                ErrorCode.COMMON_VALIDATION_FAILED,
                "restock quantity must be positive",
            )
        return normalized

    @staticmethod
    def _line_quantity(quantity: Decimal) -> Decimal:
        return CRMService._restock_quantity(quantity)

    @staticmethod
    def _line_values(
        quantity: Decimal, unit_price: Decimal
    ) -> tuple[Decimal, Decimal, Decimal]:
        try:
            normalized_quantity = Decimal(str(quantity)).quantize(
                Decimal("0.001"), rounding=ROUND_HALF_UP
            )
            normalized_price = Decimal(str(unit_price)).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            amount = (normalized_quantity * normalized_price).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
        except (InvalidOperation, ValueError):
            raise KernelError(
                ErrorCode.COMMON_VALIDATION_FAILED,
                "quote line quantity and price must be finite decimals",
            ) from None
        if (
            not normalized_quantity.is_finite()
            or not normalized_price.is_finite()
            or not amount.is_finite()
            or normalized_quantity <= 0
            or normalized_price < 0
            or normalized_quantity > Decimal("999999999999999.999")
            or normalized_price > Decimal("9999999999999999.99")
            or amount > Decimal("9999999999999999.99")
        ):
            raise KernelError(
                ErrorCode.COMMON_VALIDATION_FAILED,
                "quote line quantity or price is outside the supported range",
            )
        return normalized_quantity, normalized_price, amount
