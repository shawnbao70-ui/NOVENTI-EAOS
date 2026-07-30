"""Closed HTTP DTOs for the PHX-G294 CRM C1 slice."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class _ClosedModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class CreateCustomerRequest(_ClosedModel):
    code: str = Field(min_length=1, max_length=64)
    display_name: str = Field(min_length=1, max_length=255)
    owner_subject_id: UUID | None = None


class UpdateCustomerRequest(_ClosedModel):
    display_name: str = Field(min_length=1, max_length=255)
    owner_subject_id: UUID | None = None
    expected_version: int = Field(ge=1)


class ArchiveRequest(_ClosedModel):
    reason: str = Field(min_length=1, max_length=500)
    expected_version: int = Field(ge=1)


class SetCommercialHoldRequest(_ClosedModel):
    commercial_hold: bool
    expected_version: int = Field(ge=1)


class SetConfirmApprovalPolicyRequest(_ClosedModel):
    confirm_approval_required: bool
    expected_version: int = Field(ge=0)


class SetQuoteIssueApprovalPolicyRequest(_ClosedModel):
    quote_issue_approval_required: bool
    expected_version: int = Field(ge=0)


class SetQuoteConvertApprovalPolicyRequest(_ClosedModel):
    quote_convert_approval_required: bool
    expected_version: int = Field(ge=0)


class SetSOConfirmWorkflowApprovalPolicyRequest(_ClosedModel):
    so_confirm_workflow_approval_required: bool
    expected_version: int = Field(ge=0)


class SetDoShipApprovalPolicyRequest(_ClosedModel):
    do_ship_approval_required: bool
    expected_version: int = Field(ge=0)


class SetDoReleaseApprovalPolicyRequest(_ClosedModel):
    do_release_approval_required: bool
    expected_version: int = Field(ge=0)


class CreateContactRequest(_ClosedModel):
    display_name: str = Field(min_length=1, max_length=255)
    title: str | None = Field(default=None, max_length=128)
    email: str | None = Field(default=None, max_length=320)
    phone: str | None = Field(default=None, max_length=64)


class UpdateContactRequest(CreateContactRequest):
    expected_version: int = Field(ge=1)


class CreateOpportunityRequest(_ClosedModel):
    customer_id: UUID
    title: str = Field(min_length=1, max_length=255)
    owner_subject_id: UUID | None = None


class UpdateOpportunityRequest(_ClosedModel):
    title: str = Field(min_length=1, max_length=255)
    owner_subject_id: UUID | None = None
    expected_version: int = Field(ge=1)


class CreateRequirementRequest(_ClosedModel):
    opportunity_id: UUID
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=4000)


class UpdateRequirementRequest(_ClosedModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=4000)
    expected_version: int = Field(ge=1)


class CreateQuoteRequest(_ClosedModel):
    requirement_id: UUID
    currency: str = Field(default="USD", min_length=3, max_length=3)
    notes: str | None = Field(default=None, max_length=4000)
    functional_currency: str | None = Field(default=None, min_length=3, max_length=3)
    fx_rate: Decimal | None = Field(
        default=None, gt=0, max_digits=18, decimal_places=8
    )


class UpdateQuoteRequest(_ClosedModel):
    currency: str = Field(min_length=3, max_length=3)
    notes: str | None = Field(default=None, max_length=4000)
    expected_version: int = Field(ge=1)
    functional_currency: str | None = Field(default=None, min_length=3, max_length=3)
    fx_rate: Decimal | None = Field(
        default=None, gt=0, max_digits=18, decimal_places=8
    )


class ConvertQuoteRequest(_ClosedModel):
    idempotency_key: UUID
    functional_currency: str | None = Field(default=None, min_length=3, max_length=3)
    fx_rate: Decimal | None = Field(
        default=None, gt=0, max_digits=18, decimal_places=8
    )
    approval_ref: str | None = Field(default=None, min_length=1, max_length=64)


class CreateSalesOrderRequest(_ClosedModel):
    idempotency_key: UUID


class CreateQuoteLineRequest(_ClosedModel):
    description: str = Field(min_length=1, max_length=500)
    quantity: Decimal = Field(gt=0, max_digits=18, decimal_places=3)
    unit_price: Decimal = Field(ge=0, max_digits=18, decimal_places=2)


class UpdateQuoteLineRequest(_ClosedModel):
    description: str = Field(min_length=1, max_length=500)
    quantity: Decimal = Field(gt=0, max_digits=18, decimal_places=3)
    unit_price: Decimal = Field(ge=0, max_digits=18, decimal_places=2)
    expected_version: int = Field(ge=1)


class ConfirmSalesOrderRequest(_ClosedModel):
    idempotency_key: UUID
    human_confirm: Literal[True]
    approval_ref: str | None = Field(default=None, min_length=1, max_length=64)


class CreateDeliveryOrderRequest(_ClosedModel):
    idempotency_key: UUID
    lines: list["CreateDeliveryOrderLineRequest"] | None = None


class CreateDeliveryOrderLineRequest(_ClosedModel):
    sales_order_line_id: UUID
    quantity: Decimal = Field(gt=0, max_digits=18, decimal_places=3)


class ReleaseDeliveryOrderRequest(_ClosedModel):
    idempotency_key: UUID
    human_confirm: Literal[True]
    approval_ref: str | None = Field(default=None, min_length=1, max_length=64)


class CreateARInvoiceRequest(_ClosedModel):
    idempotency_key: UUID


class IssueARInvoiceRequest(_ClosedModel):
    idempotency_key: UUID
    human_confirm: Literal[True]


class VoidARInvoiceRequest(_ClosedModel):
    idempotency_key: UUID
    human_confirm: Literal[True]
    reason: str = Field(min_length=1, max_length=500)


class CreateReturnAuthorizationRequest(_ClosedModel):
    reason: str = Field(min_length=1, max_length=500)
    idempotency_key: UUID
    human_confirm: Literal[True]
    invoice_id: UUID | None = None


class RestockReturnAuthorizationRequest(_ClosedModel):
    idempotency_key: UUID
    human_confirm: Literal[True]
    quantity: Decimal | None = Field(
        default=None, gt=0, max_digits=18, decimal_places=3
    )


class CreateReturnAuthorizationCreditNoteRequest(_ClosedModel):
    amount: Decimal = Field(gt=0, max_digits=18, decimal_places=2)
    idempotency_key: UUID
    human_confirm: Literal[True]


class CustomerView(_ClosedModel):
    id: UUID
    code: str
    display_name: str
    owner_subject_id: UUID | None
    status: Literal["active", "archived"]
    commercial_hold: bool
    created_at: datetime
    updated_at: datetime
    archived_at: datetime | None
    version: int


class ContactView(_ClosedModel):
    id: UUID
    customer_id: UUID
    display_name: str
    title: str | None
    email: str | None
    phone: str | None
    status: Literal["active", "archived"]
    created_at: datetime
    updated_at: datetime
    archived_at: datetime | None
    version: int


class CustomerListItemView(_ClosedModel):
    id: UUID
    code: str
    display_name: str
    status: Literal["active"]
    updated_at: datetime


class ContactListItemView(_ClosedModel):
    id: UUID
    customer_id: UUID
    display_name: str
    title: str | None
    status: Literal["active"]
    updated_at: datetime


class CustomerListData(_ClosedModel):
    items: list[CustomerListItemView]
    next_cursor: str | None


class ContactListData(_ClosedModel):
    items: list[ContactListItemView]
    next_cursor: str | None


class OpportunityListItemView(_ClosedModel):
    id: UUID
    customer_id: UUID
    code: str
    title: str
    owner_subject_id: UUID | None
    status: Literal["active"]
    updated_at: datetime
    version: int


class OpportunityListData(_ClosedModel):
    items: list[OpportunityListItemView]
    next_cursor: str | None


class RequirementListItemView(_ClosedModel):
    id: UUID
    opportunity_id: UUID
    code: str
    title: str
    status: Literal["active"]
    updated_at: datetime
    version: int


class RequirementListData(_ClosedModel):
    items: list[RequirementListItemView]
    next_cursor: str | None


class QuoteListItemView(_ClosedModel):
    id: UUID
    requirement_id: UUID
    code: str
    currency: str
    status: Literal["draft", "issued"]
    updated_at: datetime
    version: int


class QuoteListData(_ClosedModel):
    items: list[QuoteListItemView]
    next_cursor: str | None


class OpportunityView(_ClosedModel):
    id: UUID
    customer_id: UUID
    code: str
    title: str
    owner_subject_id: UUID | None
    status: Literal["active", "archived"]
    created_at: datetime
    updated_at: datetime
    archived_at: datetime | None
    version: int


class RequirementView(_ClosedModel):
    id: UUID
    opportunity_id: UUID
    code: str
    title: str
    description: str | None
    status: Literal["active", "archived"]
    created_at: datetime
    updated_at: datetime
    archived_at: datetime | None
    version: int


class IssueQuoteRequest(_ClosedModel):
    idempotency_key: UUID
    human_confirm: Literal[True]
    approval_ref: str | None = Field(default=None, min_length=1, max_length=64)


class QuoteView(_ClosedModel):
    id: UUID
    requirement_id: UUID
    code: str
    currency: str
    functional_currency: str
    fx_rate: Decimal
    notes: str | None
    status: Literal["draft", "issued", "archived"]
    created_at: datetime
    updated_at: datetime
    archived_at: datetime | None
    issued_at: datetime | None = None
    version: int


class QuoteConversionView(_ClosedModel):
    id: UUID
    quote_id: UUID
    requirement_id: UUID
    quote_version: int
    currency: str
    functional_currency: str
    fx_rate: Decimal
    functional_total: Decimal
    status: Literal["ready", "consumed"]
    created_at: datetime
    updated_at: datetime
    consumed_at: datetime | None
    version: int


class SalesOrderListItemView(_ClosedModel):
    id: UUID
    conversion_id: UUID
    quote_id: UUID
    requirement_id: UUID
    code: str
    currency: str
    status: Literal["created", "confirmed", "partially_shipped", "shipped"]
    total_amount: Decimal
    created_at: datetime
    version: int


class SalesOrderListData(_ClosedModel):
    items: list[SalesOrderListItemView]
    next_cursor: str | None


class SalesOrderView(_ClosedModel):
    id: UUID
    conversion_id: UUID
    quote_id: UUID
    requirement_id: UUID
    code: str
    currency: str
    functional_currency: str
    fx_rate: Decimal
    functional_total: Decimal
    status: Literal["created", "confirmed", "partially_shipped", "shipped"]
    created_at: datetime
    total_amount: Decimal
    confirmed_at: datetime | None
    shipped_quantity: Decimal
    remaining_quantity: Decimal
    version: int


class SalesOrderLineView(_ClosedModel):
    id: UUID
    sales_order_id: UUID
    line_number: int
    description: str
    quantity: Decimal
    unit_price: Decimal
    amount: Decimal
    created_at: datetime


class DeliveryOrderView(_ClosedModel):
    id: UUID
    sales_order_id: UUID
    sales_order_version: int
    quote_id: UUID
    requirement_id: UUID
    code: str
    currency: str
    total_amount: Decimal
    status: Literal["draft", "released", "shipped"]
    created_at: datetime
    released_at: datetime | None = None
    fulfillment_status: Literal["draft", "released", "shipped"]
    version: int


class ARInvoiceView(_ClosedModel):
    id: UUID
    delivery_order_id: UUID
    delivery_order_version: int
    sales_order_id: UUID
    sales_order_version: int
    customer_id: UUID
    code: str
    currency: str
    functional_currency: str
    fx_rate: Decimal
    total_amount: Decimal
    functional_total: Decimal
    status: Literal["draft", "issued", "closed", "voided"]
    created_at: datetime
    issued_at: datetime | None = None
    voided_at: datetime | None = None
    void_reason: str | None = None
    version: int


class ReturnAuthorizationView(_ClosedModel):
    id: UUID
    delivery_order_id: UUID
    invoice_id: UUID | None
    credit_note_id: UUID | None = None
    code: str
    reason: str
    status: Literal["draft", "restocked"]
    created_at: datetime
    restocked_at: datetime | None = None
    credit_note_issued_at: datetime | None = None
    version: int


class QuoteLineView(_ClosedModel):
    id: UUID
    quote_id: UUID
    line_number: int
    description: str
    quantity: Decimal
    unit_price: Decimal
    amount: Decimal
    status: Literal["active", "archived"]
    created_at: datetime
    updated_at: datetime
    archived_at: datetime | None
    version: int


class CustomerEnvelope(_ClosedModel):
    data: CustomerView
    audit_id: UUID | None = None


class ContactEnvelope(_ClosedModel):
    data: ContactView
    audit_id: UUID | None = None


class CustomerListEnvelope(_ClosedModel):
    data: CustomerListData


class ContactListEnvelope(_ClosedModel):
    data: ContactListData


class OpportunityListEnvelope(_ClosedModel):
    data: OpportunityListData


class RequirementListEnvelope(_ClosedModel):
    data: RequirementListData


class QuoteListEnvelope(_ClosedModel):
    data: QuoteListData


class OpportunityEnvelope(_ClosedModel):
    data: OpportunityView
    audit_id: UUID | None = None


class RequirementEnvelope(_ClosedModel):
    data: RequirementView
    audit_id: UUID | None = None


class QuoteEnvelope(_ClosedModel):
    data: QuoteView
    audit_id: UUID | None = None


class QuoteConversionEnvelope(_ClosedModel):
    data: QuoteConversionView
    audit_id: UUID | None = None


class SalesOrderEnvelope(_ClosedModel):
    data: SalesOrderView
    audit_id: UUID | None = None


class SalesOrderListEnvelope(_ClosedModel):
    data: SalesOrderListData


class QuoteLineEnvelope(_ClosedModel):
    data: QuoteLineView
    audit_id: UUID | None = None


class QuoteLineListEnvelope(_ClosedModel):
    data: list[QuoteLineView]


class SalesOrderLineListEnvelope(_ClosedModel):
    data: list[SalesOrderLineView]


class DeliveryOrderEnvelope(_ClosedModel):
    data: DeliveryOrderView
    audit_id: UUID | None = None


class ARInvoiceEnvelope(_ClosedModel):
    data: ARInvoiceView
    audit_id: UUID | None = None


class ReturnAuthorizationEnvelope(_ClosedModel):
    data: ReturnAuthorizationView
    audit_id: UUID | None = None


class ConfirmApprovalPolicyView(_ClosedModel):
    confirm_approval_required: bool
    updated_at: datetime
    version: int


class ConfirmApprovalPolicyEnvelope(_ClosedModel):
    data: ConfirmApprovalPolicyView
    audit_id: UUID | None = None


class QuoteIssueApprovalPolicyView(_ClosedModel):
    quote_issue_approval_required: bool
    updated_at: datetime
    version: int


class QuoteIssueApprovalPolicyEnvelope(_ClosedModel):
    data: QuoteIssueApprovalPolicyView
    audit_id: UUID | None = None


class QuoteConvertApprovalPolicyView(_ClosedModel):
    quote_convert_approval_required: bool
    updated_at: datetime
    version: int


class QuoteConvertApprovalPolicyEnvelope(_ClosedModel):
    data: QuoteConvertApprovalPolicyView
    audit_id: UUID | None = None


class SOConfirmWorkflowApprovalPolicyView(_ClosedModel):
    so_confirm_workflow_approval_required: bool
    updated_at: datetime
    version: int


class SOConfirmWorkflowApprovalPolicyEnvelope(_ClosedModel):
    data: SOConfirmWorkflowApprovalPolicyView
    audit_id: UUID | None = None


class DoShipApprovalPolicyView(_ClosedModel):
    do_ship_approval_required: bool
    updated_at: datetime
    version: int


class DoShipApprovalPolicyEnvelope(_ClosedModel):
    data: DoShipApprovalPolicyView
    audit_id: UUID | None = None


class DoReleaseApprovalPolicyView(_ClosedModel):
    do_release_approval_required: bool
    updated_at: datetime
    version: int


class DoReleaseApprovalPolicyEnvelope(_ClosedModel):
    data: DoReleaseApprovalPolicyView
    audit_id: UUID | None = None


class Customer360InvoiceTraceView(_ClosedModel):
    id: UUID
    code: str
    status: Literal["draft", "issued", "closed", "voided"]
    currency: str
    total_amount: Decimal


class Customer360AppliedReceiptTraceView(_ClosedModel):
    id: UUID
    code: str
    status: Literal["draft", "applied"]
    currency: str
    amount: Decimal
    ar_invoice_id: UUID


class Customer360CreditNoteTraceView(_ClosedModel):
    id: UUID
    code: str
    status: Literal["draft", "issued"]
    currency: str
    amount: Decimal
    ar_invoice_id: UUID


class Customer360View(_ClosedModel):
    customer_id: UUID
    customer_code: str
    display_name: str
    commercial_hold: bool
    opportunities_count: int
    open_sales_orders_count: int
    open_delivery_orders_count: int
    invoice_traces: list[Customer360InvoiceTraceView]
    applied_receipt_traces: list[Customer360AppliedReceiptTraceView]
    credit_note_traces: list[Customer360CreditNoteTraceView]


class Customer360Envelope(_ClosedModel):
    data: Customer360View


class TwinAdvisoryRefView(_ClosedModel):
    id: UUID
    entity_ref: str
    status: Literal["active", "superseded", "archived"]
    source_ref: str
    updated_at: datetime


class BrainAdvisoryRefView(_ClosedModel):
    id: UUID
    kind: Literal["insight", "recommendation", "simulation"]
    summary: str
    advisory: bool
    twin_ref: UUID | None
    updated_at: datetime


class CustomerAdvisoryView(_ClosedModel):
    customer_id: UUID
    twin_snapshot_refs: list[TwinAdvisoryRefView]
    brain_insight_refs: list[BrainAdvisoryRefView]
    execution_authority: Literal["none"]


class CustomerAdvisoryEnvelope(_ClosedModel):
    data: CustomerAdvisoryView
