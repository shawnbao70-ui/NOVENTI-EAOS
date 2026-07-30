"""Thin HTTP adapter for the PHX-G294 Customer + Contact C1 slice."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from api.gateway.context import derive_tenant_context, reject_context_override
from api.gateway.deps import (
    CRMGatewayService,
    Customer360GatewayService,
    CustomerAdvisoryGatewayService,
    get_crm_service,
    get_customer360_service,
    get_customer_advisory_service,
)
from api.gateway.errors import raise_for_result
from api.gateway.schemas.crm import (
    ARInvoiceEnvelope,
    ArchiveRequest,
    ConfirmApprovalPolicyEnvelope,
    ContactEnvelope,
    ContactListEnvelope,
    ConfirmSalesOrderRequest,
    CreateARInvoiceRequest,
    CreateReturnAuthorizationRequest,
    CreateReturnAuthorizationCreditNoteRequest,
    RestockReturnAuthorizationRequest,
    ConvertQuoteRequest,
    Customer360Envelope,
    CustomerAdvisoryEnvelope,
    DoReleaseApprovalPolicyEnvelope,
    DoShipApprovalPolicyEnvelope,
    IssueARInvoiceRequest,
    VoidARInvoiceRequest,
    CreateQuoteLineRequest,
    CreateSalesOrderRequest,
    CreateContactRequest,
    CreateCustomerRequest,
    CreateDeliveryOrderRequest,
    CustomerEnvelope,
    CustomerListEnvelope,
    DeliveryOrderEnvelope,
    ReleaseDeliveryOrderRequest,
    CreateOpportunityRequest,
    CreateRequirementRequest,
    CreateQuoteRequest,
    IssueQuoteRequest,
    OpportunityEnvelope,
    OpportunityListEnvelope,
    QuoteEnvelope,
    QuoteListEnvelope,
    QuoteConvertApprovalPolicyEnvelope,
    QuoteIssueApprovalPolicyEnvelope,
    QuoteConversionEnvelope,
    QuoteLineEnvelope,
    QuoteLineListEnvelope,
    RequirementEnvelope,
    RequirementListEnvelope,
    ReturnAuthorizationEnvelope,
    SOConfirmWorkflowApprovalPolicyEnvelope,
    SalesOrderEnvelope,
    SalesOrderListEnvelope,
    SalesOrderLineListEnvelope,
    SetCommercialHoldRequest,
    SetConfirmApprovalPolicyRequest,
    SetDoReleaseApprovalPolicyRequest,
    SetDoShipApprovalPolicyRequest,
    SetQuoteConvertApprovalPolicyRequest,
    SetQuoteIssueApprovalPolicyRequest,
    SetSOConfirmWorkflowApprovalPolicyRequest,
    UpdateContactRequest,
    UpdateCustomerRequest,
    UpdateOpportunityRequest,
    UpdateRequirementRequest,
    UpdateQuoteRequest,
    UpdateQuoteLineRequest,
)
from api.gateway.schemas.finance import CustomerBalanceEnvelope
from noventi.crm.customer360 import Customer360Projection
from noventi.crm.customer_advisory import CustomerAdvisoryProjection
from api.gateway.deps import FinanceGatewayService, get_finance_service
from kernel.shared.context import ExecutionContext
from noventi.crm.models import (
    ARInvoice,
    Contact,
    Customer,
    DeliveryOrder,
    Opportunity,
    Quote,
    QuoteConversion,
    QuoteLine,
    Requirement,
    ReturnAuthorization,
    SalesOrder,
    SalesOrderLine,
    TenantConfirmPolicy,
)

router = APIRouter(prefix="/v1/crm/customers", tags=["CRM"])
opportunity_router = APIRouter(prefix="/v1/crm/opportunities", tags=["CRM"])
requirement_router = APIRouter(prefix="/v1/crm/requirements", tags=["CRM"])
quote_router = APIRouter(prefix="/v1/crm/quotes", tags=["CRM"])
conversion_router = APIRouter(prefix="/v1/crm/conversions", tags=["CRM"])
sales_order_router = APIRouter(prefix="/v1/crm/sales-orders", tags=["CRM"])
delivery_order_router = APIRouter(
    prefix="/v1/crm/delivery-orders", tags=["CRM"]
)
ar_invoice_router = APIRouter(prefix="/v1/crm/ar-invoices", tags=["CRM"])
return_authorization_router = APIRouter(
    prefix="/v1/crm/return-authorizations", tags=["CRM"]
)
policy_router = APIRouter(prefix="/v1/crm/policies", tags=["CRM"])


def _customer(customer: Customer) -> dict:
    return {
        "id": customer.id,
        "code": customer.code,
        "display_name": customer.display_name,
        "owner_subject_id": customer.owner_subject_id,
        "status": customer.status.value,
        "commercial_hold": customer.commercial_hold,
        "created_at": customer.created_at,
        "updated_at": customer.updated_at,
        "archived_at": customer.archived_at,
        "version": customer.version,
    }


def _contact(contact: Contact) -> dict:
    return {
        "id": contact.id,
        "customer_id": contact.customer_id,
        "display_name": contact.display_name,
        "title": contact.title,
        "email": contact.email,
        "phone": contact.phone,
        "status": contact.status.value,
        "created_at": contact.created_at,
        "updated_at": contact.updated_at,
        "archived_at": contact.archived_at,
        "version": contact.version,
    }


def _opportunity(opportunity: Opportunity) -> dict:
    return {
        "id": opportunity.id,
        "customer_id": opportunity.customer_id,
        "code": opportunity.code,
        "title": opportunity.title,
        "owner_subject_id": opportunity.owner_subject_id,
        "status": opportunity.status.value,
        "created_at": opportunity.created_at,
        "updated_at": opportunity.updated_at,
        "archived_at": opportunity.archived_at,
        "version": opportunity.version,
    }


def _requirement(requirement: Requirement) -> dict:
    return {
        "id": requirement.id,
        "opportunity_id": requirement.opportunity_id,
        "code": requirement.code,
        "title": requirement.title,
        "description": requirement.description,
        "status": requirement.status.value,
        "created_at": requirement.created_at,
        "updated_at": requirement.updated_at,
        "archived_at": requirement.archived_at,
        "version": requirement.version,
    }


def _quote(quote: Quote) -> dict:
    return {
        "id": quote.id,
        "requirement_id": quote.requirement_id,
        "code": quote.code,
        "currency": quote.currency,
        "functional_currency": quote.functional_currency,
        "fx_rate": quote.fx_rate,
        "notes": quote.notes,
        "status": quote.status.value,
        "created_at": quote.created_at,
        "updated_at": quote.updated_at,
        "archived_at": quote.archived_at,
        "issued_at": quote.issued_at,
        "version": quote.version,
    }


def _conversion(conversion: QuoteConversion) -> dict:
    return {
        "id": conversion.id,
        "quote_id": conversion.quote_id,
        "requirement_id": conversion.requirement_id,
        "quote_version": conversion.quote_version,
        "currency": conversion.currency,
        "functional_currency": conversion.functional_currency,
        "fx_rate": conversion.fx_rate,
        "functional_total": conversion.functional_total,
        "status": conversion.status.value,
        "created_at": conversion.created_at,
        "updated_at": conversion.updated_at,
        "consumed_at": conversion.consumed_at,
        "version": conversion.version,
    }


def _sales_order(sales_order: SalesOrder) -> dict:
    return {
        "id": sales_order.id,
        "conversion_id": sales_order.conversion_id,
        "quote_id": sales_order.quote_id,
        "requirement_id": sales_order.requirement_id,
        "code": sales_order.code,
        "currency": sales_order.currency,
        "functional_currency": sales_order.functional_currency,
        "fx_rate": sales_order.fx_rate,
        "functional_total": sales_order.functional_total,
        "status": sales_order.status.value,
        "created_at": sales_order.created_at,
        "total_amount": sales_order.total_amount,
        "confirmed_at": sales_order.confirmed_at,
        "shipped_quantity": sales_order.shipped_quantity,
        "remaining_quantity": (
            sales_order.ordered_quantity - sales_order.shipped_quantity
        ),
        "version": sales_order.version,
    }


def _quote_line(quote_line: QuoteLine) -> dict:
    return {
        "id": quote_line.id,
        "quote_id": quote_line.quote_id,
        "line_number": quote_line.line_number,
        "description": quote_line.description,
        "quantity": quote_line.quantity,
        "unit_price": quote_line.unit_price,
        "amount": quote_line.amount,
        "status": quote_line.status.value,
        "created_at": quote_line.created_at,
        "updated_at": quote_line.updated_at,
        "archived_at": quote_line.archived_at,
        "version": quote_line.version,
    }


def _sales_order_line(sales_order_line: SalesOrderLine) -> dict:
    return {
        "id": sales_order_line.id,
        "sales_order_id": sales_order_line.sales_order_id,
        "line_number": sales_order_line.line_number,
        "description": sales_order_line.description,
        "quantity": sales_order_line.quantity,
        "unit_price": sales_order_line.unit_price,
        "amount": sales_order_line.amount,
        "created_at": sales_order_line.created_at,
    }


def _delivery_order(delivery_order: DeliveryOrder) -> dict:
    return {
        "id": delivery_order.id,
        "sales_order_id": delivery_order.sales_order_id,
        "sales_order_version": delivery_order.sales_order_version,
        "quote_id": delivery_order.quote_id,
        "requirement_id": delivery_order.requirement_id,
        "code": delivery_order.code,
        "currency": delivery_order.currency,
        "total_amount": delivery_order.total_amount,
        "status": delivery_order.status.value,
        "created_at": delivery_order.created_at,
        "released_at": delivery_order.released_at,
        "fulfillment_status": delivery_order.status.value,
        "version": delivery_order.version,
    }


def _ar_invoice(invoice: ARInvoice) -> dict:
    return {
        "id": invoice.id,
        "delivery_order_id": invoice.delivery_order_id,
        "delivery_order_version": invoice.delivery_order_version,
        "sales_order_id": invoice.sales_order_id,
        "sales_order_version": invoice.sales_order_version,
        "customer_id": invoice.customer_id,
        "code": invoice.code,
        "currency": invoice.currency,
        "functional_currency": invoice.functional_currency,
        "fx_rate": invoice.fx_rate,
        "total_amount": invoice.total_amount,
        "functional_total": invoice.functional_total,
        "status": invoice.status.value,
        "created_at": invoice.created_at,
        "issued_at": invoice.issued_at,
        "voided_at": invoice.voided_at,
        "void_reason": invoice.void_reason,
        "version": invoice.version,
    }


def _return_authorization(authorization: ReturnAuthorization) -> dict:
    return {
        "id": authorization.id,
        "delivery_order_id": authorization.delivery_order_id,
        "invoice_id": authorization.invoice_id,
        "credit_note_id": authorization.credit_note_id,
        "code": authorization.code,
        "reason": authorization.reason,
        "status": authorization.status.value,
        "created_at": authorization.created_at,
        "restocked_at": authorization.restocked_at,
        "credit_note_issued_at": authorization.credit_note_issued_at,
        "version": authorization.version,
    }


@router.post(
    "",
    response_model=CustomerEnvelope,
    status_code=status.HTTP_201_CREATED,
)
def create_customer(
    body: CreateCustomerRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    crm: CRMGatewayService = Depends(get_crm_service),
) -> CustomerEnvelope:
    reject_context_override(body.model_dump(exclude_none=True))
    result = crm.create_customer(
        ctx,
        code=body.code,
        display_name=body.display_name,
        owner_subject_id=body.owner_subject_id,
    )
    raise_for_result(result)
    assert result.data is not None
    return CustomerEnvelope.model_validate(
        {"data": _customer(result.data), "audit_id": result.audit_id}
    )


@router.get("", response_model=CustomerListEnvelope)
def list_customers(
    limit: int = Query(default=50, ge=1, le=100),
    cursor: str | None = Query(default=None, max_length=2048),
    ctx: ExecutionContext = Depends(derive_tenant_context),
    crm: CRMGatewayService = Depends(get_crm_service),
) -> CustomerListEnvelope:
    result = crm.list_customers(ctx, limit=limit, cursor=cursor)
    raise_for_result(result)
    assert result.data is not None
    return CustomerListEnvelope.model_validate(
        {
            "data": {
                "items": [
                    {
                        "id": customer.id,
                        "code": customer.code,
                        "display_name": customer.display_name,
                        "status": customer.status.value,
                        "updated_at": customer.updated_at,
                    }
                    for customer in result.data.items
                ],
                "next_cursor": result.data.next_cursor,
            }
        }
    )


@router.get("/{customer_id}", response_model=CustomerEnvelope)
def get_customer(
    customer_id: UUID,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    crm: CRMGatewayService = Depends(get_crm_service),
) -> CustomerEnvelope:
    result = crm.get_customer(ctx, customer_id=customer_id)
    raise_for_result(result)
    assert result.data is not None
    return CustomerEnvelope.model_validate({"data": _customer(result.data)})


@router.get("/{customer_id}/balances", response_model=CustomerBalanceEnvelope)
def get_customer_balances(
    customer_id: UUID,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    finance: FinanceGatewayService = Depends(get_finance_service),
) -> CustomerBalanceEnvelope:
    result = finance.get_customer_balance(ctx, customer_id=customer_id)
    raise_for_result(result)
    assert result.data is not None
    return CustomerBalanceEnvelope.model_validate(
        {
            "data": {
                "customer_id": result.data.customer_id,
                "balances": result.data.balances,
                "unallocated_receipts": result.data.unallocated_receipts,
                "unallocated_receipts_note": "NOT part of cleared balance",
            },
            "audit_id": result.audit_id,
        }
    )


def _customer360(projection: Customer360Projection) -> dict:
    return {
        "customer_id": projection.customer_id,
        "customer_code": projection.customer_code,
        "display_name": projection.display_name,
        "commercial_hold": projection.commercial_hold,
        "opportunities_count": projection.opportunities_count,
        "open_sales_orders_count": projection.open_sales_orders_count,
        "open_delivery_orders_count": projection.open_delivery_orders_count,
        "invoice_traces": [
            {
                "id": invoice.id,
                "code": invoice.code,
                "status": invoice.status.value,
                "currency": invoice.currency,
                "total_amount": invoice.total_amount,
            }
            for invoice in projection.invoice_traces
        ],
        "applied_receipt_traces": [
            {
                "id": receipt.id,
                "code": receipt.code,
                "status": receipt.status.value,
                "currency": receipt.currency,
                "amount": receipt.amount,
                "ar_invoice_id": receipt.ar_invoice_id,
            }
            for receipt in projection.applied_receipt_traces
        ],
        "credit_note_traces": [
            {
                "id": credit_note.id,
                "code": credit_note.code,
                "status": credit_note.status.value,
                "currency": credit_note.currency,
                "amount": credit_note.amount,
                "ar_invoice_id": credit_note.ar_invoice_id,
            }
            for credit_note in projection.credit_note_traces
        ],
    }


@router.get("/{customer_id}/360", response_model=Customer360Envelope)
def get_customer360(
    customer_id: UUID,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    customer360: Customer360GatewayService = Depends(get_customer360_service),
) -> Customer360Envelope:
    result = customer360.get_customer360(ctx, customer_id)
    raise_for_result(result)
    assert result.data is not None
    return Customer360Envelope.model_validate(
        {"data": _customer360(result.data)}
    )


def _customer_advisory(projection: CustomerAdvisoryProjection) -> dict:
    return {
        "customer_id": projection.customer_id,
        "twin_snapshot_refs": [
            {
                "id": snapshot.id,
                "entity_ref": snapshot.entity_ref,
                "status": snapshot.status.value,
                "source_ref": snapshot.source_ref,
                "updated_at": snapshot.updated_at,
            }
            for snapshot in projection.twin_snapshot_refs
        ],
        "brain_insight_refs": [
            {
                "id": insight.id,
                "kind": insight.kind.value,
                "summary": insight.summary,
                "advisory": insight.advisory,
                "twin_ref": insight.twin_ref,
                "updated_at": insight.updated_at,
            }
            for insight in projection.brain_insight_refs
        ],
        "execution_authority": projection.execution_authority,
    }


@router.get(
    "/{customer_id}/advisory", response_model=CustomerAdvisoryEnvelope
)
def get_customer_advisory(
    customer_id: UUID,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    advisory: CustomerAdvisoryGatewayService = Depends(
        get_customer_advisory_service
    ),
) -> CustomerAdvisoryEnvelope:
    result = advisory.get_customer_advisory(ctx, customer_id)
    raise_for_result(result)
    assert result.data is not None
    return CustomerAdvisoryEnvelope.model_validate(
        {"data": _customer_advisory(result.data)}
    )


@router.patch("/{customer_id}", response_model=CustomerEnvelope)
def update_customer(
    customer_id: UUID,
    body: UpdateCustomerRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    crm: CRMGatewayService = Depends(get_crm_service),
) -> CustomerEnvelope:
    reject_context_override(body.model_dump(exclude_none=True))
    result = crm.update_customer(
        ctx,
        customer_id=customer_id,
        display_name=body.display_name,
        owner_subject_id=body.owner_subject_id,
        expected_version=body.expected_version,
    )
    raise_for_result(result)
    assert result.data is not None
    return CustomerEnvelope.model_validate(
        {"data": _customer(result.data), "audit_id": result.audit_id}
    )


@router.post("/{customer_id}/commercial-hold", response_model=CustomerEnvelope)
def set_customer_commercial_hold(
    customer_id: UUID,
    body: SetCommercialHoldRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    crm: CRMGatewayService = Depends(get_crm_service),
) -> CustomerEnvelope:
    reject_context_override(body.model_dump())
    result = crm.set_customer_commercial_hold(
        ctx,
        customer_id=customer_id,
        commercial_hold=body.commercial_hold,
        expected_version=body.expected_version,
    )
    raise_for_result(result)
    assert result.data is not None
    return CustomerEnvelope.model_validate(
        {"data": _customer(result.data), "audit_id": result.audit_id}
    )


@router.post("/{customer_id}/archive", response_model=CustomerEnvelope)
def archive_customer(
    customer_id: UUID,
    body: ArchiveRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    crm: CRMGatewayService = Depends(get_crm_service),
) -> CustomerEnvelope:
    reject_context_override(body.model_dump())
    result = crm.archive_customer(
        ctx,
        customer_id=customer_id,
        reason=body.reason,
        expected_version=body.expected_version,
    )
    raise_for_result(result)
    assert result.data is not None
    return CustomerEnvelope.model_validate(
        {"data": _customer(result.data), "audit_id": result.audit_id}
    )


@router.post(
    "/{customer_id}/contacts",
    response_model=ContactEnvelope,
    status_code=status.HTTP_201_CREATED,
)
def create_contact(
    customer_id: UUID,
    body: CreateContactRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    crm: CRMGatewayService = Depends(get_crm_service),
) -> ContactEnvelope:
    reject_context_override(body.model_dump(exclude_none=True))
    result = crm.create_contact(
        ctx,
        customer_id=customer_id,
        display_name=body.display_name,
        title=body.title,
        email=body.email,
        phone=body.phone,
    )
    raise_for_result(result)
    assert result.data is not None
    return ContactEnvelope.model_validate(
        {"data": _contact(result.data), "audit_id": result.audit_id}
    )


@router.get(
    "/{customer_id}/contacts",
    response_model=ContactListEnvelope,
)
def list_contacts(
    customer_id: UUID,
    limit: int = Query(default=50, ge=1, le=100),
    cursor: str | None = Query(default=None, max_length=2048),
    ctx: ExecutionContext = Depends(derive_tenant_context),
    crm: CRMGatewayService = Depends(get_crm_service),
) -> ContactListEnvelope:
    result = crm.list_contacts(
        ctx,
        customer_id=customer_id,
        limit=limit,
        cursor=cursor,
    )
    raise_for_result(result)
    assert result.data is not None
    return ContactListEnvelope.model_validate(
        {
            "data": {
                "items": [
                    {
                        "id": contact.id,
                        "customer_id": contact.customer_id,
                        "display_name": contact.display_name,
                        "title": contact.title,
                        "status": contact.status.value,
                        "updated_at": contact.updated_at,
                    }
                    for contact in result.data.items
                ],
                "next_cursor": result.data.next_cursor,
            }
        }
    )


@router.get(
    "/{customer_id}/contacts/{contact_id}",
    response_model=ContactEnvelope,
)
def get_contact(
    customer_id: UUID,
    contact_id: UUID,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    crm: CRMGatewayService = Depends(get_crm_service),
) -> ContactEnvelope:
    result = crm.get_contact(
        ctx,
        customer_id=customer_id,
        contact_id=contact_id,
    )
    raise_for_result(result)
    assert result.data is not None
    return ContactEnvelope.model_validate({"data": _contact(result.data)})


@router.patch(
    "/{customer_id}/contacts/{contact_id}",
    response_model=ContactEnvelope,
)
def update_contact(
    customer_id: UUID,
    contact_id: UUID,
    body: UpdateContactRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    crm: CRMGatewayService = Depends(get_crm_service),
) -> ContactEnvelope:
    reject_context_override(body.model_dump(exclude_none=True))
    result = crm.update_contact(
        ctx,
        customer_id=customer_id,
        contact_id=contact_id,
        display_name=body.display_name,
        title=body.title,
        email=body.email,
        phone=body.phone,
        expected_version=body.expected_version,
    )
    raise_for_result(result)
    assert result.data is not None
    return ContactEnvelope.model_validate(
        {"data": _contact(result.data), "audit_id": result.audit_id}
    )


@router.post(
    "/{customer_id}/contacts/{contact_id}/archive",
    response_model=ContactEnvelope,
)
def archive_contact(
    customer_id: UUID,
    contact_id: UUID,
    body: ArchiveRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    crm: CRMGatewayService = Depends(get_crm_service),
) -> ContactEnvelope:
    reject_context_override(body.model_dump())
    result = crm.archive_contact(
        ctx,
        customer_id=customer_id,
        contact_id=contact_id,
        reason=body.reason,
        expected_version=body.expected_version,
    )
    raise_for_result(result)
    assert result.data is not None
    return ContactEnvelope.model_validate(
        {"data": _contact(result.data), "audit_id": result.audit_id}
    )


@opportunity_router.post(
    "",
    response_model=OpportunityEnvelope,
    status_code=status.HTTP_201_CREATED,
)
def create_opportunity(
    body: CreateOpportunityRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    crm: CRMGatewayService = Depends(get_crm_service),
) -> OpportunityEnvelope:
    reject_context_override(body.model_dump(exclude_none=True))
    result = crm.create_opportunity(
        ctx,
        customer_id=body.customer_id,
        title=body.title,
        owner_subject_id=body.owner_subject_id,
    )
    raise_for_result(result)
    assert result.data is not None
    return OpportunityEnvelope.model_validate(
        {"data": _opportunity(result.data), "audit_id": result.audit_id}
    )


@opportunity_router.get("", response_model=OpportunityListEnvelope)
def list_opportunities(
    limit: int = Query(default=50, ge=1, le=100),
    cursor: str | None = Query(default=None, max_length=2048),
    ctx: ExecutionContext = Depends(derive_tenant_context),
    crm: CRMGatewayService = Depends(get_crm_service),
) -> OpportunityListEnvelope:
    result = crm.list_opportunities(ctx, limit=limit, cursor=cursor)
    raise_for_result(result)
    assert result.data is not None
    return OpportunityListEnvelope.model_validate(
        {
            "data": {
                "items": [
                    {
                        "id": opportunity.id,
                        "customer_id": opportunity.customer_id,
                        "code": opportunity.code,
                        "title": opportunity.title,
                        "owner_subject_id": opportunity.owner_subject_id,
                        "status": opportunity.status.value,
                        "updated_at": opportunity.updated_at,
                        "version": opportunity.version,
                    }
                    for opportunity in result.data.items
                ],
                "next_cursor": result.data.next_cursor,
            }
        }
    )


@opportunity_router.get(
    "/{opportunity_id}",
    response_model=OpportunityEnvelope,
)
def get_opportunity(
    opportunity_id: UUID,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    crm: CRMGatewayService = Depends(get_crm_service),
) -> OpportunityEnvelope:
    result = crm.get_opportunity(ctx, opportunity_id=opportunity_id)
    raise_for_result(result)
    assert result.data is not None
    return OpportunityEnvelope.model_validate({"data": _opportunity(result.data)})


@opportunity_router.patch(
    "/{opportunity_id}",
    response_model=OpportunityEnvelope,
)
def update_opportunity(
    opportunity_id: UUID,
    body: UpdateOpportunityRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    crm: CRMGatewayService = Depends(get_crm_service),
) -> OpportunityEnvelope:
    reject_context_override(body.model_dump(exclude_none=True))
    result = crm.update_opportunity(
        ctx,
        opportunity_id=opportunity_id,
        title=body.title,
        owner_subject_id=body.owner_subject_id,
        expected_version=body.expected_version,
    )
    raise_for_result(result)
    assert result.data is not None
    return OpportunityEnvelope.model_validate(
        {"data": _opportunity(result.data), "audit_id": result.audit_id}
    )


@opportunity_router.post(
    "/{opportunity_id}/archive",
    response_model=OpportunityEnvelope,
)
def archive_opportunity(
    opportunity_id: UUID,
    body: ArchiveRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    crm: CRMGatewayService = Depends(get_crm_service),
) -> OpportunityEnvelope:
    reject_context_override(body.model_dump())
    result = crm.archive_opportunity(
        ctx,
        opportunity_id=opportunity_id,
        reason=body.reason,
        expected_version=body.expected_version,
    )
    raise_for_result(result)
    assert result.data is not None
    return OpportunityEnvelope.model_validate(
        {"data": _opportunity(result.data), "audit_id": result.audit_id}
    )


@requirement_router.post(
    "",
    response_model=RequirementEnvelope,
    status_code=status.HTTP_201_CREATED,
)
def create_requirement(
    body: CreateRequirementRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    crm: CRMGatewayService = Depends(get_crm_service),
) -> RequirementEnvelope:
    reject_context_override(body.model_dump(exclude_none=True))
    result = crm.create_requirement(
        ctx,
        opportunity_id=body.opportunity_id,
        title=body.title,
        description=body.description,
    )
    raise_for_result(result)
    assert result.data is not None
    return RequirementEnvelope.model_validate(
        {"data": _requirement(result.data), "audit_id": result.audit_id}
    )


@requirement_router.get("", response_model=RequirementListEnvelope)
def list_requirements(
    limit: int = Query(default=50, ge=1, le=100),
    cursor: str | None = Query(default=None, max_length=2048),
    ctx: ExecutionContext = Depends(derive_tenant_context),
    crm: CRMGatewayService = Depends(get_crm_service),
) -> RequirementListEnvelope:
    result = crm.list_requirements(ctx, limit=limit, cursor=cursor)
    raise_for_result(result)
    assert result.data is not None
    return RequirementListEnvelope.model_validate(
        {
            "data": {
                "items": [
                    {
                        "id": requirement.id,
                        "opportunity_id": requirement.opportunity_id,
                        "code": requirement.code,
                        "title": requirement.title,
                        "status": requirement.status.value,
                        "updated_at": requirement.updated_at,
                        "version": requirement.version,
                    }
                    for requirement in result.data.items
                ],
                "next_cursor": result.data.next_cursor,
            }
        }
    )


@requirement_router.get(
    "/{requirement_id}",
    response_model=RequirementEnvelope,
)
def get_requirement(
    requirement_id: UUID,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    crm: CRMGatewayService = Depends(get_crm_service),
) -> RequirementEnvelope:
    result = crm.get_requirement(ctx, requirement_id=requirement_id)
    raise_for_result(result)
    assert result.data is not None
    return RequirementEnvelope.model_validate({"data": _requirement(result.data)})


@requirement_router.patch(
    "/{requirement_id}",
    response_model=RequirementEnvelope,
)
def update_requirement(
    requirement_id: UUID,
    body: UpdateRequirementRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    crm: CRMGatewayService = Depends(get_crm_service),
) -> RequirementEnvelope:
    reject_context_override(body.model_dump(exclude_none=True))
    result = crm.update_requirement(
        ctx,
        requirement_id=requirement_id,
        title=body.title,
        description=body.description,
        expected_version=body.expected_version,
    )
    raise_for_result(result)
    assert result.data is not None
    return RequirementEnvelope.model_validate(
        {"data": _requirement(result.data), "audit_id": result.audit_id}
    )


@requirement_router.post(
    "/{requirement_id}/archive",
    response_model=RequirementEnvelope,
)
def archive_requirement(
    requirement_id: UUID,
    body: ArchiveRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    crm: CRMGatewayService = Depends(get_crm_service),
) -> RequirementEnvelope:
    reject_context_override(body.model_dump())
    result = crm.archive_requirement(
        ctx,
        requirement_id=requirement_id,
        reason=body.reason,
        expected_version=body.expected_version,
    )
    raise_for_result(result)
    assert result.data is not None
    return RequirementEnvelope.model_validate(
        {"data": _requirement(result.data), "audit_id": result.audit_id}
    )


@quote_router.post(
    "",
    response_model=QuoteEnvelope,
    status_code=status.HTTP_201_CREATED,
)
def create_quote(
    body: CreateQuoteRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    crm: CRMGatewayService = Depends(get_crm_service),
) -> QuoteEnvelope:
    reject_context_override(body.model_dump(exclude_none=True))
    result = crm.create_quote(
        ctx,
        requirement_id=body.requirement_id,
        currency=body.currency,
        notes=body.notes,
        functional_currency=body.functional_currency,
        fx_rate=body.fx_rate,
    )
    raise_for_result(result)
    assert result.data is not None
    return QuoteEnvelope.model_validate(
        {"data": _quote(result.data), "audit_id": result.audit_id}
    )


@quote_router.get("", response_model=QuoteListEnvelope)
def list_quotes(
    limit: int = Query(default=50, ge=1, le=100),
    cursor: str | None = Query(default=None, max_length=2048),
    ctx: ExecutionContext = Depends(derive_tenant_context),
    crm: CRMGatewayService = Depends(get_crm_service),
) -> QuoteListEnvelope:
    result = crm.list_quotes(ctx, limit=limit, cursor=cursor)
    raise_for_result(result)
    assert result.data is not None
    return QuoteListEnvelope.model_validate(
        {
            "data": {
                "items": [
                    {
                        "id": quote.id,
                        "requirement_id": quote.requirement_id,
                        "code": quote.code,
                        "currency": quote.currency,
                        "status": quote.status.value,
                        "updated_at": quote.updated_at,
                        "version": quote.version,
                    }
                    for quote in result.data.items
                ],
                "next_cursor": result.data.next_cursor,
            }
        }
    )


@quote_router.get("/{quote_id}", response_model=QuoteEnvelope)
def get_quote(
    quote_id: UUID,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    crm: CRMGatewayService = Depends(get_crm_service),
) -> QuoteEnvelope:
    result = crm.get_quote(ctx, quote_id=quote_id)
    raise_for_result(result)
    assert result.data is not None
    return QuoteEnvelope.model_validate({"data": _quote(result.data)})


@quote_router.patch("/{quote_id}", response_model=QuoteEnvelope)
def update_quote(
    quote_id: UUID,
    body: UpdateQuoteRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    crm: CRMGatewayService = Depends(get_crm_service),
) -> QuoteEnvelope:
    reject_context_override(body.model_dump(exclude_none=True))
    result = crm.update_quote(
        ctx,
        quote_id=quote_id,
        currency=body.currency,
        notes=body.notes,
        expected_version=body.expected_version,
        functional_currency=body.functional_currency,
        fx_rate=body.fx_rate,
    )
    raise_for_result(result)
    assert result.data is not None
    return QuoteEnvelope.model_validate(
        {"data": _quote(result.data), "audit_id": result.audit_id}
    )


@quote_router.post("/{quote_id}/archive", response_model=QuoteEnvelope)
def archive_quote(
    quote_id: UUID,
    body: ArchiveRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    crm: CRMGatewayService = Depends(get_crm_service),
) -> QuoteEnvelope:
    reject_context_override(body.model_dump())
    result = crm.archive_quote(
        ctx,
        quote_id=quote_id,
        reason=body.reason,
        expected_version=body.expected_version,
    )
    raise_for_result(result)
    assert result.data is not None
    return QuoteEnvelope.model_validate(
        {"data": _quote(result.data), "audit_id": result.audit_id}
    )


@quote_router.post("/{quote_id}/issue", response_model=QuoteEnvelope)
def issue_quote(
    quote_id: UUID,
    body: IssueQuoteRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    crm: CRMGatewayService = Depends(get_crm_service),
) -> QuoteEnvelope:
    reject_context_override(body.model_dump())
    result = crm.issue_quote(
        ctx,
        quote_id=quote_id,
        idempotency_key=body.idempotency_key,
        human_confirm=body.human_confirm,
        approval_ref=body.approval_ref,
    )
    raise_for_result(result)
    assert result.data is not None
    return QuoteEnvelope.model_validate(
        {"data": _quote(result.data), "audit_id": result.audit_id}
    )


@quote_router.post(
    "/{quote_id}/convert",
    response_model=QuoteConversionEnvelope,
    status_code=status.HTTP_201_CREATED,
)
def convert_quote(
    quote_id: UUID,
    body: ConvertQuoteRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    crm: CRMGatewayService = Depends(get_crm_service),
) -> QuoteConversionEnvelope:
    reject_context_override(body.model_dump())
    result = crm.convert_quote(
        ctx,
        quote_id=quote_id,
        idempotency_key=body.idempotency_key,
        functional_currency=body.functional_currency,
        fx_rate=body.fx_rate,
        approval_ref=body.approval_ref,
    )
    raise_for_result(result)
    assert result.data is not None
    return QuoteConversionEnvelope.model_validate(
        {"data": _conversion(result.data), "audit_id": result.audit_id}
    )


@conversion_router.get(
    "/{conversion_id}",
    response_model=QuoteConversionEnvelope,
)
def get_conversion(
    conversion_id: UUID,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    crm: CRMGatewayService = Depends(get_crm_service),
) -> QuoteConversionEnvelope:
    result = crm.get_conversion(ctx, conversion_id=conversion_id)
    raise_for_result(result)
    assert result.data is not None
    return QuoteConversionEnvelope.model_validate(
        {"data": _conversion(result.data)}
    )


@conversion_router.post(
    "/{conversion_id}/sales-order",
    response_model=SalesOrderEnvelope,
    status_code=status.HTTP_201_CREATED,
)
def create_sales_order(
    conversion_id: UUID,
    body: CreateSalesOrderRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    crm: CRMGatewayService = Depends(get_crm_service),
) -> SalesOrderEnvelope:
    reject_context_override(body.model_dump())
    result = crm.create_sales_order(
        ctx,
        conversion_id=conversion_id,
        idempotency_key=body.idempotency_key,
    )
    raise_for_result(result)
    assert result.data is not None
    return SalesOrderEnvelope.model_validate(
        {"data": _sales_order(result.data), "audit_id": result.audit_id}
    )


@sales_order_router.get("", response_model=SalesOrderListEnvelope)
def list_sales_orders(
    limit: int = Query(default=50, ge=1, le=100),
    cursor: str | None = Query(default=None, max_length=2048),
    ctx: ExecutionContext = Depends(derive_tenant_context),
    crm: CRMGatewayService = Depends(get_crm_service),
) -> SalesOrderListEnvelope:
    result = crm.list_sales_orders(ctx, limit=limit, cursor=cursor)
    raise_for_result(result)
    assert result.data is not None
    return SalesOrderListEnvelope.model_validate(
        {
            "data": {
                "items": [
                    {
                        "id": order.id,
                        "conversion_id": order.conversion_id,
                        "quote_id": order.quote_id,
                        "requirement_id": order.requirement_id,
                        "code": order.code,
                        "currency": order.currency,
                        "status": order.status.value,
                        "total_amount": order.total_amount,
                        "created_at": order.created_at,
                        "version": order.version,
                    }
                    for order in result.data.items
                ],
                "next_cursor": result.data.next_cursor,
            }
        }
    )


@sales_order_router.get(
    "/{sales_order_id}",
    response_model=SalesOrderEnvelope,
)
def get_sales_order(
    sales_order_id: UUID,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    crm: CRMGatewayService = Depends(get_crm_service),
) -> SalesOrderEnvelope:
    result = crm.get_sales_order(ctx, sales_order_id=sales_order_id)
    raise_for_result(result)
    assert result.data is not None
    return SalesOrderEnvelope.model_validate({"data": _sales_order(result.data)})


@quote_router.post(
    "/{quote_id}/lines",
    response_model=QuoteLineEnvelope,
    status_code=status.HTTP_201_CREATED,
)
def create_quote_line(
    quote_id: UUID,
    body: CreateQuoteLineRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    crm: CRMGatewayService = Depends(get_crm_service),
) -> QuoteLineEnvelope:
    reject_context_override(body.model_dump())
    result = crm.create_quote_line(
        ctx,
        quote_id=quote_id,
        description=body.description,
        quantity=body.quantity,
        unit_price=body.unit_price,
    )
    raise_for_result(result)
    assert result.data is not None
    return QuoteLineEnvelope.model_validate(
        {"data": _quote_line(result.data), "audit_id": result.audit_id}
    )


@quote_router.get(
    "/{quote_id}/lines",
    response_model=QuoteLineListEnvelope,
)
def list_quote_lines(
    quote_id: UUID,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    crm: CRMGatewayService = Depends(get_crm_service),
) -> QuoteLineListEnvelope:
    result = crm.list_quote_lines(ctx, quote_id=quote_id)
    raise_for_result(result)
    assert result.data is not None
    return QuoteLineListEnvelope.model_validate(
        {"data": [_quote_line(item) for item in result.data]}
    )


@quote_router.get(
    "/{quote_id}/lines/{quote_line_id}",
    response_model=QuoteLineEnvelope,
)
def get_quote_line(
    quote_id: UUID,
    quote_line_id: UUID,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    crm: CRMGatewayService = Depends(get_crm_service),
) -> QuoteLineEnvelope:
    result = crm.get_quote_line(
        ctx, quote_id=quote_id, quote_line_id=quote_line_id
    )
    raise_for_result(result)
    assert result.data is not None
    return QuoteLineEnvelope.model_validate({"data": _quote_line(result.data)})


@quote_router.patch(
    "/{quote_id}/lines/{quote_line_id}",
    response_model=QuoteLineEnvelope,
)
def update_quote_line(
    quote_id: UUID,
    quote_line_id: UUID,
    body: UpdateQuoteLineRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    crm: CRMGatewayService = Depends(get_crm_service),
) -> QuoteLineEnvelope:
    reject_context_override(body.model_dump())
    result = crm.update_quote_line(
        ctx,
        quote_id=quote_id,
        quote_line_id=quote_line_id,
        description=body.description,
        quantity=body.quantity,
        unit_price=body.unit_price,
        expected_version=body.expected_version,
    )
    raise_for_result(result)
    assert result.data is not None
    return QuoteLineEnvelope.model_validate(
        {"data": _quote_line(result.data), "audit_id": result.audit_id}
    )


@quote_router.post(
    "/{quote_id}/lines/{quote_line_id}/archive",
    response_model=QuoteLineEnvelope,
)
def archive_quote_line(
    quote_id: UUID,
    quote_line_id: UUID,
    body: ArchiveRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    crm: CRMGatewayService = Depends(get_crm_service),
) -> QuoteLineEnvelope:
    reject_context_override(body.model_dump())
    result = crm.archive_quote_line(
        ctx,
        quote_id=quote_id,
        quote_line_id=quote_line_id,
        reason=body.reason,
        expected_version=body.expected_version,
    )
    raise_for_result(result)
    assert result.data is not None
    return QuoteLineEnvelope.model_validate(
        {"data": _quote_line(result.data), "audit_id": result.audit_id}
    )


@sales_order_router.post(
    "/{sales_order_id}/confirm",
    response_model=SalesOrderEnvelope,
)
def confirm_sales_order(
    sales_order_id: UUID,
    body: ConfirmSalesOrderRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    crm: CRMGatewayService = Depends(get_crm_service),
) -> SalesOrderEnvelope:
    reject_context_override(body.model_dump())
    result = crm.confirm_sales_order(
        ctx,
        sales_order_id=sales_order_id,
        idempotency_key=body.idempotency_key,
        human_confirm=body.human_confirm,
        approval_ref=body.approval_ref,
    )
    raise_for_result(result)
    assert result.data is not None
    return SalesOrderEnvelope.model_validate(
        {"data": _sales_order(result.data), "audit_id": result.audit_id}
    )


@sales_order_router.get(
    "/{sales_order_id}/lines",
    response_model=SalesOrderLineListEnvelope,
)
def list_sales_order_lines(
    sales_order_id: UUID,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    crm: CRMGatewayService = Depends(get_crm_service),
) -> SalesOrderLineListEnvelope:
    result = crm.list_sales_order_lines(
        ctx, sales_order_id=sales_order_id
    )
    raise_for_result(result)
    assert result.data is not None
    return SalesOrderLineListEnvelope.model_validate(
        {"data": [_sales_order_line(item) for item in result.data]}
    )


@sales_order_router.post(
    "/{sales_order_id}/delivery-order",
    response_model=DeliveryOrderEnvelope,
    status_code=status.HTTP_201_CREATED,
)
def create_delivery_order(
    sales_order_id: UUID,
    body: CreateDeliveryOrderRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    crm: CRMGatewayService = Depends(get_crm_service),
) -> DeliveryOrderEnvelope:
    reject_context_override(body.model_dump())
    result = crm.create_delivery_order(
        ctx,
        sales_order_id=sales_order_id,
        idempotency_key=body.idempotency_key,
        line_quantities=(
            [(line.sales_order_line_id, line.quantity) for line in body.lines]
            if body.lines is not None
            else None
        ),
    )
    raise_for_result(result)
    assert result.data is not None
    return DeliveryOrderEnvelope.model_validate(
        {"data": _delivery_order(result.data), "audit_id": result.audit_id}
    )


@delivery_order_router.get(
    "/{delivery_order_id}",
    response_model=DeliveryOrderEnvelope,
)
def get_delivery_order(
    delivery_order_id: UUID,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    crm: CRMGatewayService = Depends(get_crm_service),
) -> DeliveryOrderEnvelope:
    result = crm.get_delivery_order(
        ctx, delivery_order_id=delivery_order_id
    )
    raise_for_result(result)
    assert result.data is not None
    return DeliveryOrderEnvelope.model_validate(
        {"data": _delivery_order(result.data)}
    )


@delivery_order_router.post(
    "/{delivery_order_id}/release",
    response_model=DeliveryOrderEnvelope,
)
def release_delivery_order(
    delivery_order_id: UUID,
    body: ReleaseDeliveryOrderRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    crm: CRMGatewayService = Depends(get_crm_service),
) -> DeliveryOrderEnvelope:
    reject_context_override(body.model_dump())
    result = crm.release_delivery_order(
        ctx,
        delivery_order_id=delivery_order_id,
        idempotency_key=body.idempotency_key,
        human_confirm=body.human_confirm,
        approval_ref=body.approval_ref,
    )
    raise_for_result(result)
    assert result.data is not None
    return DeliveryOrderEnvelope.model_validate(
        {"data": _delivery_order(result.data), "audit_id": result.audit_id}
    )


@delivery_order_router.post(
    "/{delivery_order_id}/ar-invoice",
    response_model=ARInvoiceEnvelope,
    status_code=status.HTTP_201_CREATED,
)
def create_ar_invoice(
    delivery_order_id: UUID,
    body: CreateARInvoiceRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    crm: CRMGatewayService = Depends(get_crm_service),
) -> ARInvoiceEnvelope:
    reject_context_override(body.model_dump())
    result = crm.create_ar_invoice(
        ctx,
        delivery_order_id=delivery_order_id,
        idempotency_key=body.idempotency_key,
    )
    raise_for_result(result)
    assert result.data is not None
    return ARInvoiceEnvelope.model_validate(
        {"data": _ar_invoice(result.data), "audit_id": result.audit_id}
    )


@delivery_order_router.post(
    "/{delivery_order_id}/return-authorizations",
    response_model=ReturnAuthorizationEnvelope,
    status_code=status.HTTP_201_CREATED,
)
def create_return_authorization(
    delivery_order_id: UUID,
    body: CreateReturnAuthorizationRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    crm: CRMGatewayService = Depends(get_crm_service),
) -> ReturnAuthorizationEnvelope:
    reject_context_override(body.model_dump())
    result = crm.create_return_authorization(
        ctx,
        delivery_order_id=delivery_order_id,
        reason=body.reason,
        idempotency_key=body.idempotency_key,
        human_confirm=body.human_confirm,
        invoice_id=body.invoice_id,
    )
    raise_for_result(result)
    assert result.data is not None
    return ReturnAuthorizationEnvelope.model_validate(
        {
            "data": _return_authorization(result.data),
            "audit_id": result.audit_id,
        }
    )


@return_authorization_router.get(
    "/{return_authorization_id}",
    response_model=ReturnAuthorizationEnvelope,
)
def get_return_authorization(
    return_authorization_id: UUID,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    crm: CRMGatewayService = Depends(get_crm_service),
) -> ReturnAuthorizationEnvelope:
    result = crm.get_return_authorization(
        ctx, return_authorization_id=return_authorization_id
    )
    raise_for_result(result)
    assert result.data is not None
    return ReturnAuthorizationEnvelope.model_validate(
        {"data": _return_authorization(result.data)}
    )


@return_authorization_router.post(
    "/{return_authorization_id}/restock",
    response_model=ReturnAuthorizationEnvelope,
)
def restock_return_authorization(
    return_authorization_id: UUID,
    body: RestockReturnAuthorizationRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    crm: CRMGatewayService = Depends(get_crm_service),
) -> ReturnAuthorizationEnvelope:
    reject_context_override(body.model_dump())
    result = crm.restock_return_authorization(
        ctx,
        return_authorization_id=return_authorization_id,
        human_confirm=body.human_confirm,
        idempotency_key=body.idempotency_key,
        quantity=body.quantity,
    )
    raise_for_result(result)
    assert result.data is not None
    return ReturnAuthorizationEnvelope.model_validate(
        {
            "data": _return_authorization(result.data),
            "audit_id": result.audit_id,
        }
    )


@return_authorization_router.post(
    "/{return_authorization_id}/credit-notes",
    response_model=ReturnAuthorizationEnvelope,
    status_code=status.HTTP_201_CREATED,
)
def create_credit_note_from_return_authorization(
    return_authorization_id: UUID,
    body: CreateReturnAuthorizationCreditNoteRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    crm: CRMGatewayService = Depends(get_crm_service),
) -> ReturnAuthorizationEnvelope:
    reject_context_override(body.model_dump())
    result = crm.create_credit_note_from_return_authorization(
        ctx,
        return_authorization_id=return_authorization_id,
        amount=body.amount,
        idempotency_key=body.idempotency_key,
        human_confirm=body.human_confirm,
    )
    raise_for_result(result)
    assert result.data is not None
    return ReturnAuthorizationEnvelope.model_validate(
        {
            "data": _return_authorization(result.data),
            "audit_id": result.audit_id,
        }
    )


@ar_invoice_router.get(
    "/{invoice_id}",
    response_model=ARInvoiceEnvelope,
)
def get_ar_invoice(
    invoice_id: UUID,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    crm: CRMGatewayService = Depends(get_crm_service),
) -> ARInvoiceEnvelope:
    result = crm.get_ar_invoice(ctx, invoice_id=invoice_id)
    raise_for_result(result)
    assert result.data is not None
    return ARInvoiceEnvelope.model_validate(
        {"data": _ar_invoice(result.data)}
    )


@ar_invoice_router.post(
    "/{invoice_id}/issue",
    response_model=ARInvoiceEnvelope,
)
def issue_ar_invoice(
    invoice_id: UUID,
    body: IssueARInvoiceRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    crm: CRMGatewayService = Depends(get_crm_service),
) -> ARInvoiceEnvelope:
    reject_context_override(body.model_dump())
    result = crm.issue_ar_invoice(
        ctx,
        invoice_id=invoice_id,
        idempotency_key=body.idempotency_key,
        human_confirm=body.human_confirm,
    )
    raise_for_result(result)
    assert result.data is not None
    return ARInvoiceEnvelope.model_validate(
        {"data": _ar_invoice(result.data), "audit_id": result.audit_id}
    )


@ar_invoice_router.post(
    "/{invoice_id}/void",
    response_model=ARInvoiceEnvelope,
)
def void_ar_invoice(
    invoice_id: UUID,
    body: VoidARInvoiceRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    crm: CRMGatewayService = Depends(get_crm_service),
) -> ARInvoiceEnvelope:
    reject_context_override(body.model_dump())
    result = crm.void_ar_invoice(
        ctx,
        invoice_id=invoice_id,
        idempotency_key=body.idempotency_key,
        human_confirm=body.human_confirm,
        reason=body.reason,
    )
    raise_for_result(result)
    assert result.data is not None
    return ARInvoiceEnvelope.model_validate(
        {"data": _ar_invoice(result.data), "audit_id": result.audit_id}
    )


def _confirm_approval_policy(policy: TenantConfirmPolicy) -> dict:
    return {
        "confirm_approval_required": policy.confirm_approval_required,
        "updated_at": policy.updated_at,
        "version": policy.version,
    }


@policy_router.get(
    "/confirm-approval",
    response_model=ConfirmApprovalPolicyEnvelope,
)
def get_confirm_approval_policy(
    ctx: ExecutionContext = Depends(derive_tenant_context),
    crm: CRMGatewayService = Depends(get_crm_service),
) -> ConfirmApprovalPolicyEnvelope:
    result = crm.get_confirm_approval_policy(ctx)
    raise_for_result(result)
    assert result.data is not None
    return ConfirmApprovalPolicyEnvelope.model_validate(
        {"data": _confirm_approval_policy(result.data)}
    )


@policy_router.put(
    "/confirm-approval",
    response_model=ConfirmApprovalPolicyEnvelope,
)
def set_confirm_approval_policy(
    body: SetConfirmApprovalPolicyRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    crm: CRMGatewayService = Depends(get_crm_service),
) -> ConfirmApprovalPolicyEnvelope:
    reject_context_override(body.model_dump())
    result = crm.set_confirm_approval_policy(
        ctx,
        confirm_approval_required=body.confirm_approval_required,
        expected_version=body.expected_version,
    )
    raise_for_result(result)
    assert result.data is not None
    return ConfirmApprovalPolicyEnvelope.model_validate(
        {
            "data": _confirm_approval_policy(result.data),
            "audit_id": result.audit_id,
        }
    )


def _quote_issue_approval_policy(policy: TenantConfirmPolicy) -> dict:
    return {
        "quote_issue_approval_required": policy.quote_issue_approval_required,
        "updated_at": policy.updated_at,
        "version": policy.version,
    }


@policy_router.get(
    "/quote-issue-approval",
    response_model=QuoteIssueApprovalPolicyEnvelope,
)
def get_quote_issue_approval_policy(
    ctx: ExecutionContext = Depends(derive_tenant_context),
    crm: CRMGatewayService = Depends(get_crm_service),
) -> QuoteIssueApprovalPolicyEnvelope:
    result = crm.get_quote_issue_approval_policy(ctx)
    raise_for_result(result)
    assert result.data is not None
    return QuoteIssueApprovalPolicyEnvelope.model_validate(
        {"data": _quote_issue_approval_policy(result.data)}
    )


@policy_router.put(
    "/quote-issue-approval",
    response_model=QuoteIssueApprovalPolicyEnvelope,
)
def set_quote_issue_approval_policy(
    body: SetQuoteIssueApprovalPolicyRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    crm: CRMGatewayService = Depends(get_crm_service),
) -> QuoteIssueApprovalPolicyEnvelope:
    reject_context_override(body.model_dump())
    result = crm.set_quote_issue_approval_policy(
        ctx,
        quote_issue_approval_required=body.quote_issue_approval_required,
        expected_version=body.expected_version,
    )
    raise_for_result(result)
    assert result.data is not None
    return QuoteIssueApprovalPolicyEnvelope.model_validate(
        {
            "data": _quote_issue_approval_policy(result.data),
            "audit_id": result.audit_id,
        }
    )


def _quote_convert_approval_policy(policy: TenantConfirmPolicy) -> dict:
    return {
        "quote_convert_approval_required": policy.quote_convert_approval_required,
        "updated_at": policy.updated_at,
        "version": policy.version,
    }


@policy_router.get(
    "/quote-convert-approval",
    response_model=QuoteConvertApprovalPolicyEnvelope,
)
def get_quote_convert_approval_policy(
    ctx: ExecutionContext = Depends(derive_tenant_context),
    crm: CRMGatewayService = Depends(get_crm_service),
) -> QuoteConvertApprovalPolicyEnvelope:
    result = crm.get_quote_convert_approval_policy(ctx)
    raise_for_result(result)
    assert result.data is not None
    return QuoteConvertApprovalPolicyEnvelope.model_validate(
        {"data": _quote_convert_approval_policy(result.data)}
    )


@policy_router.put(
    "/quote-convert-approval",
    response_model=QuoteConvertApprovalPolicyEnvelope,
)
def set_quote_convert_approval_policy(
    body: SetQuoteConvertApprovalPolicyRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    crm: CRMGatewayService = Depends(get_crm_service),
) -> QuoteConvertApprovalPolicyEnvelope:
    reject_context_override(body.model_dump())
    result = crm.set_quote_convert_approval_policy(
        ctx,
        quote_convert_approval_required=body.quote_convert_approval_required,
        expected_version=body.expected_version,
    )
    raise_for_result(result)
    assert result.data is not None
    return QuoteConvertApprovalPolicyEnvelope.model_validate(
        {
            "data": _quote_convert_approval_policy(result.data),
            "audit_id": result.audit_id,
        }
    )


def _so_confirm_workflow_approval_policy(policy: TenantConfirmPolicy) -> dict:
    return {
        "so_confirm_workflow_approval_required": (
            policy.so_confirm_workflow_approval_required
        ),
        "updated_at": policy.updated_at,
        "version": policy.version,
    }


@policy_router.get(
    "/so-confirm-workflow-approval",
    response_model=SOConfirmWorkflowApprovalPolicyEnvelope,
)
def get_so_confirm_workflow_approval_policy(
    ctx: ExecutionContext = Depends(derive_tenant_context),
    crm: CRMGatewayService = Depends(get_crm_service),
) -> SOConfirmWorkflowApprovalPolicyEnvelope:
    result = crm.get_so_confirm_workflow_approval_policy(ctx)
    raise_for_result(result)
    assert result.data is not None
    return SOConfirmWorkflowApprovalPolicyEnvelope.model_validate(
        {"data": _so_confirm_workflow_approval_policy(result.data)}
    )


@policy_router.put(
    "/so-confirm-workflow-approval",
    response_model=SOConfirmWorkflowApprovalPolicyEnvelope,
)
def set_so_confirm_workflow_approval_policy(
    body: SetSOConfirmWorkflowApprovalPolicyRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    crm: CRMGatewayService = Depends(get_crm_service),
) -> SOConfirmWorkflowApprovalPolicyEnvelope:
    reject_context_override(body.model_dump())
    result = crm.set_so_confirm_workflow_approval_policy(
        ctx,
        so_confirm_workflow_approval_required=(
            body.so_confirm_workflow_approval_required
        ),
        expected_version=body.expected_version,
    )
    raise_for_result(result)
    assert result.data is not None
    return SOConfirmWorkflowApprovalPolicyEnvelope.model_validate(
        {
            "data": _so_confirm_workflow_approval_policy(result.data),
            "audit_id": result.audit_id,
        }
    )


def _do_ship_approval_policy(policy: TenantConfirmPolicy) -> dict:
    return {
        "do_ship_approval_required": policy.do_ship_approval_required,
        "updated_at": policy.updated_at,
        "version": policy.version,
    }


@policy_router.get(
    "/do-ship-approval",
    response_model=DoShipApprovalPolicyEnvelope,
)
def get_do_ship_approval_policy(
    ctx: ExecutionContext = Depends(derive_tenant_context),
    crm: CRMGatewayService = Depends(get_crm_service),
) -> DoShipApprovalPolicyEnvelope:
    result = crm.get_do_ship_approval_policy(ctx)
    raise_for_result(result)
    assert result.data is not None
    return DoShipApprovalPolicyEnvelope.model_validate(
        {"data": _do_ship_approval_policy(result.data)}
    )


@policy_router.put(
    "/do-ship-approval",
    response_model=DoShipApprovalPolicyEnvelope,
)
def set_do_ship_approval_policy(
    body: SetDoShipApprovalPolicyRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    crm: CRMGatewayService = Depends(get_crm_service),
) -> DoShipApprovalPolicyEnvelope:
    reject_context_override(body.model_dump())
    result = crm.set_do_ship_approval_policy(
        ctx,
        do_ship_approval_required=body.do_ship_approval_required,
        expected_version=body.expected_version,
    )
    raise_for_result(result)
    assert result.data is not None
    return DoShipApprovalPolicyEnvelope.model_validate(
        {
            "data": _do_ship_approval_policy(result.data),
            "audit_id": result.audit_id,
        }
    )


def _do_release_approval_policy(policy: TenantConfirmPolicy) -> dict:
    return {
        "do_release_approval_required": policy.do_release_approval_required,
        "updated_at": policy.updated_at,
        "version": policy.version,
    }


@policy_router.get(
    "/do-release-approval",
    response_model=DoReleaseApprovalPolicyEnvelope,
)
def get_do_release_approval_policy(
    ctx: ExecutionContext = Depends(derive_tenant_context),
    crm: CRMGatewayService = Depends(get_crm_service),
) -> DoReleaseApprovalPolicyEnvelope:
    result = crm.get_do_release_approval_policy(ctx)
    raise_for_result(result)
    assert result.data is not None
    return DoReleaseApprovalPolicyEnvelope.model_validate(
        {"data": _do_release_approval_policy(result.data)}
    )


@policy_router.put(
    "/do-release-approval",
    response_model=DoReleaseApprovalPolicyEnvelope,
)
def set_do_release_approval_policy(
    body: SetDoReleaseApprovalPolicyRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    crm: CRMGatewayService = Depends(get_crm_service),
) -> DoReleaseApprovalPolicyEnvelope:
    reject_context_override(body.model_dump())
    result = crm.set_do_release_approval_policy(
        ctx,
        do_release_approval_required=body.do_release_approval_required,
        expected_version=body.expected_version,
    )
    raise_for_result(result)
    assert result.data is not None
    return DoReleaseApprovalPolicyEnvelope.model_validate(
        {
            "data": _do_release_approval_policy(result.data),
            "audit_id": result.audit_id,
        }
    )
