"""Thin HTTP adapter for Finance Receipt, Credit Note, Tax Invoice, Commission."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status

from api.gateway.context import derive_tenant_context, reject_context_override
from api.gateway.deps import FinanceGatewayService, get_finance_service
from api.gateway.errors import raise_for_result
from api.gateway.schemas.finance import (
    FinanceStatusEnvelope,
    AccrueCommissionRequest,
    AllocateARReceiptRequest,
    ApplyARReceiptRequest,
    ARCreditNoteEnvelope,
    ARRefundEnvelope,
    ARReceiptEnvelope,
    ARWriteOffEnvelope,
    TreasuryTransferEnvelope,
    ARReceiptAllocationListEnvelope,
    BankStatementEnvelope,
    BridgeSourceRequest,
    ClearBankStatementRequest,
    CloseARInvoiceEnvelope,
    CloseARInvoiceRequest,
    CloseGlPeriodRequest,
    CommissionEntryEnvelope,
    CreateARCreditNoteRequest,
    CreateARRefundRequest,
    CreateARReceiptRequest,
    CreateARWriteOffRequest,
    CreateTreasuryTransferRequest,
    CreateBankStatementRequest,
    CreateTaxRedCreditRequest,
    CreateTaxCreditLinkRequest,
    CreateGlAccountRequest,
    CreateGlFxRevaluationRequest,
    CreateGlPeriodRequest,
    CreateJournalEntryRequest,
    CreateTaxInvoiceRequest,
    CreateTaxRateRequest,
    GlAccountEnvelope,
    GlBridgeMapEnvelope,
    GlBridgePostingEnvelope,
    GlFxRevaluationEnvelope,
    GlPeriodEnvelope,
    IssueARCreditNoteRequest,
    IssueTaxInvoiceRequest,
    JournalEntryEnvelope,
    MatchBankStatementLineRequest,
    PostGlFxRevaluationRequest,
    PostARRefundRequest,
    PostTreasuryTransferRequest,
    PostJournalEntryRequest,
    PspAdapterStatusEnvelope,
    ReceiptPspPolicyEnvelope,
    SetGlBridgeMapRequest,
    SetReceiptPspPolicyRequest,
    SetTaxAuthorityPolicyRequest,
    TaxAuthorityAdapterStatusEnvelope,
    TaxAuthorityPolicyEnvelope,
    TaxCreditLinkEnvelope,
    TaxInvoiceEnvelope,
    TaxRateEnvelope,
    VoidTaxInvoiceRequest,
)
from kernel.shared.context import ExecutionContext
from noventi.finance.models import (
    ARCreditNote,
    ARRefund,
    ARReceipt,
    ARWriteOff,
    BankStatement,
    CommissionEntry,
    GlAccount,
    GlBridgeMap,
    GlBridgePosting,
    GlFxRevaluation,
    GlPeriod,
    JournalEntry,
    TaxInvoice,
    TaxCreditLink,
    TaxRate,
    TreasuryTransfer,
)
from noventi.finance.psp_provider_adapter import psp_adapter_status
from noventi.finance.tax_authority_adapter import tax_authority_adapter_status

router = APIRouter(prefix="/v1/finance/receipts", tags=["Finance"])
ar_write_off_router = APIRouter(
    prefix="/v1/finance/ar-write-offs", tags=["Finance"]
)
ar_invoice_close_router = APIRouter(
    prefix="/v1/finance/ar-invoices", tags=["Finance"]
)
credit_note_router = APIRouter(
    prefix="/v1/finance/credit-notes", tags=["Finance"]
)
ar_refund_router = APIRouter(
    prefix="/v1/finance/ar-refunds", tags=["Finance"]
)
treasury_transfer_router = APIRouter(
    prefix="/v1/finance/treasury-transfers", tags=["Finance"]
)
tax_invoice_router = APIRouter(
    prefix="/v1/finance/tax-invoices", tags=["Finance"]
)
tax_credit_link_router = APIRouter(
    prefix="/v1/finance/tax-credit-links", tags=["Finance"]
)
tax_rate_router = APIRouter(prefix="/v1/finance/tax-rates", tags=["Finance"])
gl_account_router = APIRouter(
    prefix="/v1/finance/gl-accounts", tags=["Finance"]
)
gl_period_router = APIRouter(
    prefix="/v1/finance/gl-periods", tags=["Finance"]
)
journal_entry_router = APIRouter(
    prefix="/v1/finance/journal-entries", tags=["Finance"]
)
gl_bridge_map_router = APIRouter(
    prefix="/v1/finance/gl-bridge-map", tags=["Finance"]
)
gl_bridge_router = APIRouter(
    prefix="/v1/finance/gl-bridges", tags=["Finance"]
)
gl_fx_revaluation_router = APIRouter(
    prefix="/v1/finance/gl-fx-revaluations", tags=["Finance"]
)
bank_statement_router = APIRouter(
    prefix="/v1/finance/bank-statements", tags=["Finance"]
)
commission_router = APIRouter(
    prefix="/v1/finance/commissions", tags=["Finance"]
)
policy_router = APIRouter(prefix="/v1/finance/policies", tags=["Finance"])
adapter_router = APIRouter(prefix="/v1/finance/adapters", tags=["Finance"])
status_router = APIRouter(prefix="/v1/finance", tags=["Finance"])


@status_router.get("/status", response_model=FinanceStatusEnvelope)
def get_finance_status() -> FinanceStatusEnvelope:
    """Read-only Finance posture for Terminal strip (PHX-G394)."""

    return FinanceStatusEnvelope.model_validate(
        {
            "data": {
                "writable": False,
                "commercial_auto_write": False,
                "holds_business_truth": True,
                "terminal_holds_business_truth": False,
                "bank_file_import": "deferred",
                "external_psp_network_default": "off",
                "gl_period_status_surface": True,
                "party_balance_projection": True,
                "treasury_transfer_surface": True,
                "crm_quote_so_do_state_consistency": True,
                "ar_receipt_credit_boundary": "internal_records_only",
                "commission_settlement_mode": "read_only_status",
                "crm_finance_handoff_audit": True,
                "purchase_order_observability": True,
                "inventory_movement_observability": True,
                "receiving_return_boundary": "kernel_records_only",
                "purchase_inventory_cross_contract": True,
                "supported_surfaces": [
                    "adapter_tax_authority",
                    "adapter_psp",
                    "ar_receipt",
                    "credit_note",
                    "gl_bridge",
                    "party_balance",
                    "treasury_transfer",
                ],
            }
        }
    )


def _receipt(receipt: ARReceipt) -> dict:
    return {
        "id": receipt.id,
        "customer_id": receipt.customer_id,
        "code": receipt.code,
        "currency": receipt.currency,
        "amount": receipt.amount,
        "functional_currency": receipt.functional_currency,
        "fx_rate": receipt.fx_rate,
        "functional_amount": receipt.functional_amount,
        "allocated_amount": receipt.allocated_amount,
        "unallocated_amount": receipt.amount - receipt.allocated_amount,
        "status": receipt.status.value,
        "ar_invoice_id": receipt.ar_invoice_id,
        "ar_invoice_version": receipt.ar_invoice_version,
        "created_at": receipt.created_at,
        "applied_at": receipt.applied_at,
        "psp_ref": receipt.psp_ref,
        "psp_status": receipt.psp_status,
        "version": receipt.version,
    }


def _receipt_allocation(allocation) -> dict:
    return {
        "id": allocation.id,
        "receipt_id": allocation.receipt_id,
        "ar_invoice_id": allocation.ar_invoice_id,
        "amount": allocation.amount,
        "allocation_key": allocation.allocation_key,
        "created_at": allocation.created_at,
        "version": allocation.version,
        "realized_fx_amount": allocation.realized_fx_amount,
        "realized_fx_side": (
            allocation.realized_fx_side.value
            if allocation.realized_fx_side is not None
            else None
        ),
    }


def _write_off(write_off: ARWriteOff) -> dict:
    return {
        "id": write_off.id,
        "ar_invoice_id": write_off.ar_invoice_id,
        "amount": write_off.amount,
        "currency": write_off.currency,
        "reason": write_off.reason,
        "created_at": write_off.created_at,
        "version": write_off.version,
    }


@ar_write_off_router.post(
    "", response_model=ARWriteOffEnvelope, status_code=status.HTTP_201_CREATED
)
def create_ar_write_off(
    body: CreateARWriteOffRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    finance: FinanceGatewayService = Depends(get_finance_service),
) -> ARWriteOffEnvelope:
    reject_context_override(body.model_dump())
    result = finance.create_ar_write_off(
        ctx,
        invoice_id=body.invoice_id,
        amount=body.amount,
        idempotency_key=body.idempotency_key,
        human_confirm=body.human_confirm,
        reason=body.reason,
    )
    raise_for_result(result)
    assert result.data is not None
    return ARWriteOffEnvelope.model_validate(
        {"data": _write_off(result.data), "audit_id": result.audit_id}
    )


@ar_invoice_close_router.post(
    "/{invoice_id}/close", response_model=CloseARInvoiceEnvelope
)
def close_ar_invoice(
    invoice_id: UUID,
    body: CloseARInvoiceRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    finance: FinanceGatewayService = Depends(get_finance_service),
) -> CloseARInvoiceEnvelope:
    reject_context_override(body.model_dump())
    result = finance.close_ar_invoice(
        ctx, invoice_id=invoice_id, human_confirm=body.human_confirm
    )
    raise_for_result(result)
    assert result.data is not None
    return CloseARInvoiceEnvelope.model_validate(
        {
            "data": {
                "id": result.data.id,
                "status": result.data.status,
                "version": result.data.version,
            },
            "audit_id": result.audit_id,
        }
    )


def _credit_note(credit_note: ARCreditNote) -> dict:
    return {
        "id": credit_note.id,
        "customer_id": credit_note.customer_id,
        "ar_invoice_id": credit_note.ar_invoice_id,
        "ar_invoice_version": credit_note.ar_invoice_version,
        "code": credit_note.code,
        "currency": credit_note.currency,
        "amount": credit_note.amount,
        "status": credit_note.status.value,
        "created_at": credit_note.created_at,
        "issued_at": credit_note.issued_at,
        "version": credit_note.version,
    }


def _ar_refund(refund: ARRefund) -> dict:
    return {
        "id": refund.id,
        "credit_note_id": refund.credit_note_id,
        "customer_id": refund.customer_id,
        "currency": refund.currency,
        "amount": refund.amount,
        "status": refund.status.value,
        "created_at": refund.created_at,
        "posted_at": refund.posted_at,
        "version": refund.version,
    }


def _treasury_transfer(transfer: TreasuryTransfer) -> dict:
    return {
        "id": transfer.id,
        "from_account_ref": transfer.from_account_ref,
        "to_account_ref": transfer.to_account_ref,
        "currency": transfer.currency,
        "amount": transfer.amount,
        "functional_currency": transfer.functional_currency,
        "fx_rate": transfer.fx_rate,
        "functional_amount": transfer.functional_amount,
        "status": transfer.status.value,
        "created_at": transfer.created_at,
        "posted_at": transfer.posted_at,
        "version": transfer.version,
    }


def _tax_credit_link(link: TaxCreditLink) -> dict:
    return {
        "id": link.id,
        "tax_invoice_id": link.tax_invoice_id,
        "credit_note_id": link.credit_note_id,
        "status": link.status,
        "created_at": link.created_at,
        "version": link.version,
    }


@router.post(
    "",
    response_model=ARReceiptEnvelope,
    status_code=status.HTTP_201_CREATED,
)
def create_receipt(
    body: CreateARReceiptRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    finance: FinanceGatewayService = Depends(get_finance_service),
) -> ARReceiptEnvelope:
    reject_context_override(body.model_dump())
    result = finance.create_receipt(
        ctx,
        customer_id=body.customer_id,
        amount=body.amount,
        currency=body.currency,
        functional_currency=body.functional_currency,
        fx_rate=body.fx_rate,
        functional_amount=body.functional_amount,
        idempotency_key=body.idempotency_key,
    )
    raise_for_result(result)
    assert result.data is not None
    return ARReceiptEnvelope.model_validate(
        {"data": _receipt(result.data), "audit_id": result.audit_id}
    )


@router.get("/{receipt_id}", response_model=ARReceiptEnvelope)
def get_receipt(
    receipt_id: UUID,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    finance: FinanceGatewayService = Depends(get_finance_service),
) -> ARReceiptEnvelope:
    result = finance.get_receipt(ctx, receipt_id=receipt_id)
    raise_for_result(result)
    assert result.data is not None
    return ARReceiptEnvelope.model_validate({"data": _receipt(result.data)})


@router.post("/{receipt_id}/apply", response_model=ARReceiptEnvelope)
def apply_receipt_to_invoice(
    receipt_id: UUID,
    body: ApplyARReceiptRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    finance: FinanceGatewayService = Depends(get_finance_service),
) -> ARReceiptEnvelope:
    reject_context_override(body.model_dump())
    result = finance.apply_receipt_to_invoice(
        ctx,
        receipt_id=receipt_id,
        invoice_id=body.invoice_id,
        idempotency_key=body.idempotency_key,
    )
    raise_for_result(result)
    assert result.data is not None
    return ARReceiptEnvelope.model_validate(
        {"data": _receipt(result.data), "audit_id": result.audit_id}
    )


@router.post(
    "/{receipt_id}/allocations", response_model=ARReceiptEnvelope
)
def allocate_receipt_to_invoice(
    receipt_id: UUID,
    body: AllocateARReceiptRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    finance: FinanceGatewayService = Depends(get_finance_service),
) -> ARReceiptEnvelope:
    reject_context_override(body.model_dump())
    result = finance.allocate_receipt_to_invoice(
        ctx,
        receipt_id=receipt_id,
        invoice_id=body.invoice_id,
        amount=body.amount,
        allocation_key=body.allocation_key,
    )
    raise_for_result(result)
    assert result.data is not None
    return ARReceiptEnvelope.model_validate(
        {"data": _receipt(result.data), "audit_id": result.audit_id}
    )


@router.get(
    "/{receipt_id}/allocations", response_model=ARReceiptAllocationListEnvelope
)
def list_receipt_allocations(
    receipt_id: UUID,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    finance: FinanceGatewayService = Depends(get_finance_service),
) -> ARReceiptAllocationListEnvelope:
    result = finance.list_receipt_allocations(ctx, receipt_id=receipt_id)
    raise_for_result(result)
    assert result.data is not None
    return ARReceiptAllocationListEnvelope.model_validate(
        {"data": [_receipt_allocation(item) for item in result.data]}
    )


def _receipt_psp_policy(policy) -> dict:
    return {
        "receipt_psp_required": policy.receipt_psp_required,
        "updated_at": policy.updated_at,
        "version": policy.version,
    }


@policy_router.get(
    "/receipt-psp", response_model=ReceiptPspPolicyEnvelope
)
def get_receipt_psp_policy(
    ctx: ExecutionContext = Depends(derive_tenant_context),
    finance: FinanceGatewayService = Depends(get_finance_service),
) -> ReceiptPspPolicyEnvelope:
    result = finance.get_receipt_psp_policy(ctx)
    raise_for_result(result)
    assert result.data is not None
    return ReceiptPspPolicyEnvelope.model_validate(
        {"data": _receipt_psp_policy(result.data)}
    )


@policy_router.put(
    "/receipt-psp", response_model=ReceiptPspPolicyEnvelope
)
def set_receipt_psp_policy(
    body: SetReceiptPspPolicyRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    finance: FinanceGatewayService = Depends(get_finance_service),
) -> ReceiptPspPolicyEnvelope:
    reject_context_override(body.model_dump())
    result = finance.set_receipt_psp_policy(
        ctx,
        receipt_psp_required=body.receipt_psp_required,
        expected_version=body.expected_version,
    )
    raise_for_result(result)
    assert result.data is not None
    return ReceiptPspPolicyEnvelope.model_validate(
        {"data": _receipt_psp_policy(result.data), "audit_id": result.audit_id}
    )


def _tax_authority_policy(policy) -> dict:
    return {
        "tax_authority_required": policy.tax_authority_required,
        "updated_at": policy.updated_at,
        "version": policy.version,
    }


@policy_router.get(
    "/tax-authority", response_model=TaxAuthorityPolicyEnvelope
)
def get_tax_authority_policy(
    ctx: ExecutionContext = Depends(derive_tenant_context),
    finance: FinanceGatewayService = Depends(get_finance_service),
) -> TaxAuthorityPolicyEnvelope:
    result = finance.get_tax_authority_policy(ctx)
    raise_for_result(result)
    assert result.data is not None
    return TaxAuthorityPolicyEnvelope.model_validate(
        {"data": _tax_authority_policy(result.data)}
    )


@policy_router.put(
    "/tax-authority", response_model=TaxAuthorityPolicyEnvelope
)
def set_tax_authority_policy(
    body: SetTaxAuthorityPolicyRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    finance: FinanceGatewayService = Depends(get_finance_service),
) -> TaxAuthorityPolicyEnvelope:
    reject_context_override(body.model_dump())
    result = finance.set_tax_authority_policy(
        ctx,
        tax_authority_required=body.tax_authority_required,
        expected_version=body.expected_version,
    )
    raise_for_result(result)
    assert result.data is not None
    return TaxAuthorityPolicyEnvelope.model_validate(
        {
            "data": _tax_authority_policy(result.data),
            "audit_id": result.audit_id,
        }
    )


@adapter_router.get(
    "/tax-authority", response_model=TaxAuthorityAdapterStatusEnvelope
)
def get_tax_authority_adapter_status(
    _ctx: ExecutionContext = Depends(derive_tenant_context),
) -> TaxAuthorityAdapterStatusEnvelope:
    """Read-only reflection of EAOS_TAX_NETWORK / ENABLE_TAX_NETWORK (env)."""
    status_view = tax_authority_adapter_status()
    return TaxAuthorityAdapterStatusEnvelope.model_validate(
        {
            "data": {
                "network_flag_enabled": status_view.network_flag_enabled,
                "adapter_kind": status_view.adapter_kind,
                "live_transport": status_view.live_transport,
                "endpoint_configured": status_view.endpoint_configured,
            }
        }
    )


@adapter_router.get("/psp", response_model=PspAdapterStatusEnvelope)
def get_psp_adapter_status(
    _ctx: ExecutionContext = Depends(derive_tenant_context),
) -> PspAdapterStatusEnvelope:
    """Read-only reflection of EAOS_PSP_PROVIDER + PSP network flags (env)."""
    status_view = psp_adapter_status()
    return PspAdapterStatusEnvelope.model_validate(
        {
            "data": {
                "provider": status_view.provider,
                "network_flag_enabled": status_view.network_flag_enabled,
                "adapter_kind": status_view.adapter_kind,
                "live_transport": status_view.live_transport,
                "endpoint_configured": status_view.endpoint_configured,
            }
        }
    )


@credit_note_router.post(
    "",
    response_model=ARCreditNoteEnvelope,
    status_code=status.HTTP_201_CREATED,
)
def create_credit_note(
    body: CreateARCreditNoteRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    finance: FinanceGatewayService = Depends(get_finance_service),
) -> ARCreditNoteEnvelope:
    reject_context_override(body.model_dump())
    result = finance.create_credit_note(
        ctx,
        invoice_id=body.invoice_id,
        amount=body.amount,
        idempotency_key=body.idempotency_key,
    )
    raise_for_result(result)
    assert result.data is not None
    return ARCreditNoteEnvelope.model_validate(
        {"data": _credit_note(result.data), "audit_id": result.audit_id}
    )


@credit_note_router.get(
    "/{credit_note_id}", response_model=ARCreditNoteEnvelope
)
def get_credit_note(
    credit_note_id: UUID,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    finance: FinanceGatewayService = Depends(get_finance_service),
) -> ARCreditNoteEnvelope:
    result = finance.get_credit_note(ctx, credit_note_id=credit_note_id)
    raise_for_result(result)
    assert result.data is not None
    return ARCreditNoteEnvelope.model_validate(
        {"data": _credit_note(result.data)}
    )


@credit_note_router.post(
    "/{credit_note_id}/issue", response_model=ARCreditNoteEnvelope
)
def issue_credit_note(
    credit_note_id: UUID,
    body: IssueARCreditNoteRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    finance: FinanceGatewayService = Depends(get_finance_service),
) -> ARCreditNoteEnvelope:
    reject_context_override(body.model_dump())
    result = finance.issue_credit_note(
        ctx,
        credit_note_id=credit_note_id,
        idempotency_key=body.idempotency_key,
        human_confirm=body.human_confirm,
    )
    raise_for_result(result)
    assert result.data is not None
    return ARCreditNoteEnvelope.model_validate(
        {"data": _credit_note(result.data), "audit_id": result.audit_id}
    )


@ar_refund_router.post(
    "", response_model=ARRefundEnvelope, status_code=status.HTTP_201_CREATED
)
def create_ar_refund(
    body: CreateARRefundRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    finance: FinanceGatewayService = Depends(get_finance_service),
) -> ARRefundEnvelope:
    reject_context_override(body.model_dump())
    result = finance.create_ar_refund(
        ctx,
        credit_note_id=body.credit_note_id,
        amount=body.amount,
        currency=body.currency,
        idempotency_key=body.idempotency_key,
    )
    raise_for_result(result)
    assert result.data is not None
    return ARRefundEnvelope.model_validate(
        {"data": _ar_refund(result.data), "audit_id": result.audit_id}
    )


@ar_refund_router.post("/{refund_id}/post", response_model=ARRefundEnvelope)
def post_ar_refund(
    refund_id: UUID,
    body: PostARRefundRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    finance: FinanceGatewayService = Depends(get_finance_service),
) -> ARRefundEnvelope:
    reject_context_override(body.model_dump())
    result = finance.post_ar_refund(
        ctx,
        refund_id=refund_id,
        idempotency_key=body.idempotency_key,
        human_confirm=body.human_confirm,
    )
    raise_for_result(result)
    assert result.data is not None
    return ARRefundEnvelope.model_validate(
        {"data": _ar_refund(result.data), "audit_id": result.audit_id}
    )


@treasury_transfer_router.post(
    "",
    response_model=TreasuryTransferEnvelope,
    status_code=status.HTTP_201_CREATED,
)
def create_treasury_transfer(
    body: CreateTreasuryTransferRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    finance: FinanceGatewayService = Depends(get_finance_service),
) -> TreasuryTransferEnvelope:
    reject_context_override(body.model_dump())
    result = finance.create_treasury_transfer(
        ctx,
        from_account_ref=body.from_account_ref,
        to_account_ref=body.to_account_ref,
        amount=body.amount,
        currency=body.currency,
        functional_currency=body.functional_currency,
        fx_rate=body.fx_rate,
        functional_amount=body.functional_amount,
        idempotency_key=body.idempotency_key,
    )
    raise_for_result(result)
    assert result.data is not None
    return TreasuryTransferEnvelope.model_validate(
        {"data": _treasury_transfer(result.data), "audit_id": result.audit_id}
    )


@treasury_transfer_router.get(
    "/{transfer_id}", response_model=TreasuryTransferEnvelope
)
def get_treasury_transfer(
    transfer_id: UUID,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    finance: FinanceGatewayService = Depends(get_finance_service),
) -> TreasuryTransferEnvelope:
    result = finance.get_treasury_transfer(ctx, transfer_id=transfer_id)
    raise_for_result(result)
    assert result.data is not None
    return TreasuryTransferEnvelope.model_validate(
        {"data": _treasury_transfer(result.data)}
    )


@treasury_transfer_router.post(
    "/{transfer_id}/post", response_model=TreasuryTransferEnvelope
)
def post_treasury_transfer(
    transfer_id: UUID,
    body: PostTreasuryTransferRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    finance: FinanceGatewayService = Depends(get_finance_service),
) -> TreasuryTransferEnvelope:
    reject_context_override(body.model_dump())
    result = finance.post_treasury_transfer(
        ctx,
        transfer_id=transfer_id,
        idempotency_key=body.idempotency_key,
        human_confirm=body.human_confirm,
    )
    raise_for_result(result)
    assert result.data is not None
    return TreasuryTransferEnvelope.model_validate(
        {"data": _treasury_transfer(result.data), "audit_id": result.audit_id}
    )


@tax_credit_link_router.post(
    "",
    response_model=TaxCreditLinkEnvelope,
    status_code=status.HTTP_201_CREATED,
)
def link_tax_invoice_to_credit_note(
    body: CreateTaxCreditLinkRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    finance: FinanceGatewayService = Depends(get_finance_service),
) -> TaxCreditLinkEnvelope:
    reject_context_override(body.model_dump())
    result = finance.link_tax_invoice_to_credit_note(
        ctx,
        tax_invoice_id=body.tax_invoice_id,
        credit_note_id=body.credit_note_id,
        idempotency_key=body.idempotency_key,
    )
    raise_for_result(result)
    assert result.data is not None
    return TaxCreditLinkEnvelope.model_validate(
        {"data": _tax_credit_link(result.data), "audit_id": result.audit_id}
    )


@tax_credit_link_router.get(
    "/{link_id}", response_model=TaxCreditLinkEnvelope
)
def get_tax_credit_link(
    link_id: UUID,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    finance: FinanceGatewayService = Depends(get_finance_service),
) -> TaxCreditLinkEnvelope:
    result = finance.get_tax_credit_link(ctx, link_id=link_id)
    raise_for_result(result)
    assert result.data is not None
    return TaxCreditLinkEnvelope.model_validate({"data": _tax_credit_link(result.data)})


def _tax_invoice(tax_invoice: TaxInvoice) -> dict:
    return {
        "id": tax_invoice.id,
        "customer_id": tax_invoice.customer_id,
        "ar_invoice_id": tax_invoice.ar_invoice_id,
        "ar_invoice_version": tax_invoice.ar_invoice_version,
        "code": tax_invoice.code,
        "currency": tax_invoice.currency,
        "amount": tax_invoice.amount,
        "status": tax_invoice.status.value,
        "created_at": tax_invoice.created_at,
        "issued_at": tax_invoice.issued_at,
        "voided_at": tax_invoice.voided_at,
        "void_reason": tax_invoice.void_reason,
        "tax_code": tax_invoice.tax_code,
        "authority_ref": tax_invoice.authority_ref,
        "authority_status": tax_invoice.authority_status,
        "original_tax_invoice_id": tax_invoice.original_tax_invoice_id,
        "is_red_credit": tax_invoice.is_red_credit,
        "version": tax_invoice.version,
    }


def _tax_rate(tax_rate: TaxRate) -> dict:
    return {
        "id": tax_rate.id,
        "tax_code": tax_rate.tax_code,
        "tax_name": tax_rate.tax_name,
        "rate_percent": tax_rate.rate_percent,
        "status": tax_rate.status.value,
        "created_at": tax_rate.created_at,
        "updated_at": tax_rate.updated_at,
        "version": tax_rate.version,
    }


@tax_invoice_router.post(
    "",
    response_model=TaxInvoiceEnvelope,
    status_code=status.HTTP_201_CREATED,
)
def create_tax_invoice(
    body: CreateTaxInvoiceRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    finance: FinanceGatewayService = Depends(get_finance_service),
) -> TaxInvoiceEnvelope:
    reject_context_override(body.model_dump())
    result = finance.create_tax_invoice(
        ctx,
        invoice_id=body.invoice_id,
        amount=body.amount,
        idempotency_key=body.idempotency_key,
        tax_code=body.tax_code,
    )
    raise_for_result(result)
    assert result.data is not None
    return TaxInvoiceEnvelope.model_validate(
        {"data": _tax_invoice(result.data), "audit_id": result.audit_id}
    )


@tax_invoice_router.get(
    "/{tax_invoice_id}", response_model=TaxInvoiceEnvelope
)
def get_tax_invoice(
    tax_invoice_id: UUID,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    finance: FinanceGatewayService = Depends(get_finance_service),
) -> TaxInvoiceEnvelope:
    result = finance.get_tax_invoice(ctx, tax_invoice_id=tax_invoice_id)
    raise_for_result(result)
    assert result.data is not None
    return TaxInvoiceEnvelope.model_validate(
        {"data": _tax_invoice(result.data)}
    )


@tax_invoice_router.post(
    "/{tax_invoice_id}/red-credits",
    response_model=TaxInvoiceEnvelope,
    status_code=status.HTTP_201_CREATED,
)
def create_tax_red_credit(
    tax_invoice_id: UUID,
    body: CreateTaxRedCreditRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    finance: FinanceGatewayService = Depends(get_finance_service),
) -> TaxInvoiceEnvelope:
    reject_context_override(body.model_dump())
    result = finance.create_tax_red_credit(
        ctx,
        original_id=tax_invoice_id,
        amount=body.amount,
        idempotency_key=body.idempotency_key,
        human_confirm=body.human_confirm,
    )
    raise_for_result(result)
    assert result.data is not None
    return TaxInvoiceEnvelope.model_validate(
        {"data": _tax_invoice(result.data), "audit_id": result.audit_id}
    )


@tax_invoice_router.post(
    "/{tax_invoice_id}/issue", response_model=TaxInvoiceEnvelope
)
def issue_tax_invoice(
    tax_invoice_id: UUID,
    body: IssueTaxInvoiceRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    finance: FinanceGatewayService = Depends(get_finance_service),
) -> TaxInvoiceEnvelope:
    reject_context_override(body.model_dump())
    result = finance.issue_tax_invoice(
        ctx,
        tax_invoice_id=tax_invoice_id,
        idempotency_key=body.idempotency_key,
        human_confirm=body.human_confirm,
        tax_code=body.tax_code,
    )
    raise_for_result(result)
    assert result.data is not None
    return TaxInvoiceEnvelope.model_validate(
        {"data": _tax_invoice(result.data), "audit_id": result.audit_id}
    )


@tax_rate_router.post(
    "",
    response_model=TaxRateEnvelope,
    status_code=status.HTTP_201_CREATED,
)
def create_tax_rate(
    body: CreateTaxRateRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    finance: FinanceGatewayService = Depends(get_finance_service),
) -> TaxRateEnvelope:
    reject_context_override(body.model_dump())
    result = finance.create_tax_rate(
        ctx,
        tax_code=body.tax_code,
        tax_name=body.tax_name,
        rate_percent=body.rate_percent,
    )
    raise_for_result(result)
    assert result.data is not None
    return TaxRateEnvelope.model_validate(
        {"data": _tax_rate(result.data), "audit_id": result.audit_id}
    )


@tax_rate_router.get("/{tax_rate_id}", response_model=TaxRateEnvelope)
def get_tax_rate(
    tax_rate_id: UUID,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    finance: FinanceGatewayService = Depends(get_finance_service),
) -> TaxRateEnvelope:
    result = finance.get_tax_rate(ctx, tax_rate_id=tax_rate_id)
    raise_for_result(result)
    assert result.data is not None
    return TaxRateEnvelope.model_validate({"data": _tax_rate(result.data)})


@tax_invoice_router.post(
    "/{tax_invoice_id}/void", response_model=TaxInvoiceEnvelope
)
def void_tax_invoice(
    tax_invoice_id: UUID,
    body: VoidTaxInvoiceRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    finance: FinanceGatewayService = Depends(get_finance_service),
) -> TaxInvoiceEnvelope:
    reject_context_override(body.model_dump())
    result = finance.void_tax_invoice(
        ctx,
        tax_invoice_id=tax_invoice_id,
        idempotency_key=body.idempotency_key,
        human_confirm=body.human_confirm,
        reason=body.reason,
    )
    raise_for_result(result)
    assert result.data is not None
    return TaxInvoiceEnvelope.model_validate(
        {"data": _tax_invoice(result.data), "audit_id": result.audit_id}
    )


def _commission(entry: CommissionEntry) -> dict:
    return {
        "id": entry.id,
        "source_invoice_id": entry.source_invoice_id,
        "beneficiary_subject_id": entry.beneficiary_subject_id,
        "code": entry.code,
        "currency": entry.currency,
        "amount": entry.amount,
        "status": entry.status.value,
        "created_at": entry.created_at,
        "version": entry.version,
    }


def _gl_account(account: GlAccount) -> dict:
    return {
        "id": account.id,
        "code": account.code,
        "name": account.name,
        "account_type": account.account_type.value,
        "status": account.status.value,
        "created_at": account.created_at,
        "version": account.version,
    }


def _gl_period(period: GlPeriod) -> dict:
    return {
        "id": period.id,
        "code": period.code,
        "name": period.name,
        "start_at": period.start_at,
        "end_at": period.end_at,
        "status": period.status.value,
        "created_at": period.created_at,
        "closed_at": period.closed_at,
        "version": period.version,
    }


def _journal_entry(entry: JournalEntry) -> dict:
    return {
        "id": entry.id,
        "code": entry.code,
        "currency": entry.currency,
        "period_id": entry.period_id,
        "memo": entry.memo,
        "status": entry.status.value,
        "created_at": entry.created_at,
        "posted_at": entry.posted_at,
        "version": entry.version,
        "lines": [
            {
                "id": line.id,
                "account_id": line.account_id,
                "debit": line.debit,
                "credit": line.credit,
            }
            for line in entry.lines
        ],
    }


@gl_account_router.post(
    "",
    response_model=GlAccountEnvelope,
    status_code=status.HTTP_201_CREATED,
)
def create_gl_account(
    body: CreateGlAccountRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    finance: FinanceGatewayService = Depends(get_finance_service),
) -> GlAccountEnvelope:
    reject_context_override(body.model_dump())
    result = finance.create_gl_account(
        ctx,
        code=body.code,
        name=body.name,
        account_type=body.account_type,
    )
    raise_for_result(result)
    assert result.data is not None
    return GlAccountEnvelope.model_validate(
        {"data": _gl_account(result.data), "audit_id": result.audit_id}
    )


@gl_account_router.get("/{account_id}", response_model=GlAccountEnvelope)
def get_gl_account(
    account_id: UUID,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    finance: FinanceGatewayService = Depends(get_finance_service),
) -> GlAccountEnvelope:
    result = finance.get_gl_account(ctx, account_id=account_id)
    raise_for_result(result)
    assert result.data is not None
    return GlAccountEnvelope.model_validate(
        {"data": _gl_account(result.data)}
    )


@gl_period_router.post(
    "",
    response_model=GlPeriodEnvelope,
    status_code=status.HTTP_201_CREATED,
)
def create_gl_period(
    body: CreateGlPeriodRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    finance: FinanceGatewayService = Depends(get_finance_service),
) -> GlPeriodEnvelope:
    reject_context_override(body.model_dump())
    result = finance.create_gl_period(
        ctx,
        code=body.code,
        start_at=body.start_at,
        end_at=body.end_at,
        name=body.name,
    )
    raise_for_result(result)
    assert result.data is not None
    return GlPeriodEnvelope.model_validate(
        {"data": _gl_period(result.data), "audit_id": result.audit_id}
    )


@gl_period_router.get("/{period_id}", response_model=GlPeriodEnvelope)
def get_gl_period(
    period_id: UUID,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    finance: FinanceGatewayService = Depends(get_finance_service),
) -> GlPeriodEnvelope:
    result = finance.get_gl_period(ctx, period_id=period_id)
    raise_for_result(result)
    assert result.data is not None
    return GlPeriodEnvelope.model_validate(
        {"data": _gl_period(result.data)}
    )


@gl_period_router.post(
    "/{period_id}/close", response_model=GlPeriodEnvelope
)
def close_gl_period(
    period_id: UUID,
    body: CloseGlPeriodRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    finance: FinanceGatewayService = Depends(get_finance_service),
) -> GlPeriodEnvelope:
    reject_context_override(body.model_dump())
    result = finance.close_gl_period(
        ctx,
        period_id=period_id,
        idempotency_key=body.idempotency_key,
        human_confirm=body.human_confirm,
    )
    raise_for_result(result)
    assert result.data is not None
    return GlPeriodEnvelope.model_validate(
        {"data": _gl_period(result.data), "audit_id": result.audit_id}
    )


@journal_entry_router.post(
    "",
    response_model=JournalEntryEnvelope,
    status_code=status.HTTP_201_CREATED,
)
def create_journal_entry(
    body: CreateJournalEntryRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    finance: FinanceGatewayService = Depends(get_finance_service),
) -> JournalEntryEnvelope:
    reject_context_override(body.model_dump())
    result = finance.create_journal_entry(
        ctx,
        currency=body.currency,
        period_id=body.period_id,
        lines=[line.model_dump() for line in body.lines],
        idempotency_key=body.idempotency_key,
        memo=body.memo,
    )
    raise_for_result(result)
    assert result.data is not None
    return JournalEntryEnvelope.model_validate(
        {"data": _journal_entry(result.data), "audit_id": result.audit_id}
    )


@journal_entry_router.get(
    "/{entry_id}", response_model=JournalEntryEnvelope
)
def get_journal_entry(
    entry_id: UUID,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    finance: FinanceGatewayService = Depends(get_finance_service),
) -> JournalEntryEnvelope:
    result = finance.get_journal_entry(ctx, entry_id=entry_id)
    raise_for_result(result)
    assert result.data is not None
    return JournalEntryEnvelope.model_validate(
        {"data": _journal_entry(result.data)}
    )


@journal_entry_router.post(
    "/{entry_id}/post", response_model=JournalEntryEnvelope
)
def post_journal_entry(
    entry_id: UUID,
    body: PostJournalEntryRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    finance: FinanceGatewayService = Depends(get_finance_service),
) -> JournalEntryEnvelope:
    reject_context_override(body.model_dump())
    result = finance.post_journal_entry(
        ctx,
        entry_id=entry_id,
        idempotency_key=body.idempotency_key,
        human_confirm=body.human_confirm,
    )
    raise_for_result(result)
    assert result.data is not None
    return JournalEntryEnvelope.model_validate(
        {"data": _journal_entry(result.data), "audit_id": result.audit_id}
    )


def _gl_bridge_map(bridge_map: GlBridgeMap) -> dict:
    return {
        "ar_control": bridge_map.ar_control,
        "cash": bridge_map.cash,
        "revenue": bridge_map.revenue,
        "tax_payable": bridge_map.tax_payable,
        "commission_expense": bridge_map.commission_expense,
        "commission_payable": bridge_map.commission_payable,
        "fx_gain": bridge_map.fx_gain,
        "fx_loss": bridge_map.fx_loss,
        "ap_control": bridge_map.ap_control,
        "ap_expense": bridge_map.ap_expense,
        "updated_at": bridge_map.updated_at,
        "version": bridge_map.version,
    }


def _gl_bridge_posting(posting: GlBridgePosting) -> dict:
    return {
        "id": posting.id,
        "source_type": posting.source_type.value,
        "source_id": posting.source_id,
        "journal_entry_id": posting.journal_entry_id,
        "created_at": posting.created_at,
    }


@gl_bridge_map_router.get("", response_model=GlBridgeMapEnvelope)
def get_gl_bridge_map(
    ctx: ExecutionContext = Depends(derive_tenant_context),
    finance: FinanceGatewayService = Depends(get_finance_service),
) -> GlBridgeMapEnvelope:
    result = finance.get_gl_bridge_map(ctx)
    raise_for_result(result)
    assert result.data is not None
    return GlBridgeMapEnvelope.model_validate(
        {"data": _gl_bridge_map(result.data)}
    )


@gl_bridge_map_router.put("", response_model=GlBridgeMapEnvelope)
def set_gl_bridge_map(
    body: SetGlBridgeMapRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    finance: FinanceGatewayService = Depends(get_finance_service),
) -> GlBridgeMapEnvelope:
    reject_context_override(body.model_dump())
    result = finance.set_gl_bridge_map(
        ctx,
        ar_control=body.ar_control,
        cash=body.cash,
        revenue=body.revenue,
        tax_payable=body.tax_payable,
        commission_expense=body.commission_expense,
        commission_payable=body.commission_payable,
        expected_version=body.expected_version,
        fx_gain=body.fx_gain,
        fx_loss=body.fx_loss,
        ap_control=body.ap_control,
        ap_expense=body.ap_expense,
    )
    raise_for_result(result)
    assert result.data is not None
    return GlBridgeMapEnvelope.model_validate(
        {"data": _gl_bridge_map(result.data), "audit_id": result.audit_id}
    )


@gl_bridge_router.post(
    "/ar-invoice-issue",
    response_model=GlBridgePostingEnvelope,
    status_code=status.HTTP_201_CREATED,
)
def bridge_ar_invoice_issue(
    body: BridgeSourceRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    finance: FinanceGatewayService = Depends(get_finance_service),
) -> GlBridgePostingEnvelope:
    reject_context_override(body.model_dump())
    result = finance.bridge_ar_invoice_issue(
        ctx,
        invoice_id=body.source_id,
        period_id=body.period_id,
        idempotency_key=body.idempotency_key,
        human_confirm=body.human_confirm,
    )
    raise_for_result(result)
    assert result.data is not None
    return GlBridgePostingEnvelope.model_validate(
        {"data": _gl_bridge_posting(result.data), "audit_id": result.audit_id}
    )


@gl_bridge_router.post(
    "/ar-receipt-apply",
    response_model=GlBridgePostingEnvelope,
    status_code=status.HTTP_201_CREATED,
)
def bridge_ar_receipt_apply(
    body: BridgeSourceRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    finance: FinanceGatewayService = Depends(get_finance_service),
) -> GlBridgePostingEnvelope:
    reject_context_override(body.model_dump())
    result = finance.bridge_ar_receipt_apply(
        ctx,
        receipt_id=body.source_id,
        period_id=body.period_id,
        idempotency_key=body.idempotency_key,
        human_confirm=body.human_confirm,
    )
    raise_for_result(result)
    assert result.data is not None
    return GlBridgePostingEnvelope.model_validate(
        {"data": _gl_bridge_posting(result.data), "audit_id": result.audit_id}
    )


@gl_bridge_router.post(
    "/ap-bill-post",
    response_model=GlBridgePostingEnvelope,
    status_code=status.HTTP_201_CREATED,
)
def bridge_ap_bill_post(
    body: BridgeSourceRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    finance: FinanceGatewayService = Depends(get_finance_service),
) -> GlBridgePostingEnvelope:
    reject_context_override(body.model_dump())
    result = finance.bridge_ap_bill_post(
        ctx,
        ap_bill_id=body.source_id,
        period_id=body.period_id,
        idempotency_key=body.idempotency_key,
        human_confirm=body.human_confirm,
    )
    raise_for_result(result)
    assert result.data is not None
    return GlBridgePostingEnvelope.model_validate(
        {"data": _gl_bridge_posting(result.data), "audit_id": result.audit_id}
    )


@gl_bridge_router.post(
    "/ap-payment-apply",
    response_model=GlBridgePostingEnvelope,
    status_code=status.HTTP_201_CREATED,
)
def bridge_ap_payment_apply(
    body: BridgeSourceRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    finance: FinanceGatewayService = Depends(get_finance_service),
) -> GlBridgePostingEnvelope:
    reject_context_override(body.model_dump())
    result = finance.bridge_ap_payment_apply(
        ctx,
        ap_payment_id=body.source_id,
        period_id=body.period_id,
        idempotency_key=body.idempotency_key,
        human_confirm=body.human_confirm,
    )
    raise_for_result(result)
    assert result.data is not None
    return GlBridgePostingEnvelope.model_validate(
        {"data": _gl_bridge_posting(result.data), "audit_id": result.audit_id}
    )


@gl_bridge_router.post(
    "/tax-invoice-issue",
    response_model=GlBridgePostingEnvelope,
    status_code=status.HTTP_201_CREATED,
)
def bridge_tax_invoice_issue(
    body: BridgeSourceRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    finance: FinanceGatewayService = Depends(get_finance_service),
) -> GlBridgePostingEnvelope:
    reject_context_override(body.model_dump())
    result = finance.bridge_tax_invoice_issue(
        ctx,
        tax_invoice_id=body.source_id,
        period_id=body.period_id,
        idempotency_key=body.idempotency_key,
        human_confirm=body.human_confirm,
    )
    raise_for_result(result)
    assert result.data is not None
    return GlBridgePostingEnvelope.model_validate(
        {"data": _gl_bridge_posting(result.data), "audit_id": result.audit_id}
    )


@gl_bridge_router.post(
    "/commission-accrue",
    response_model=GlBridgePostingEnvelope,
    status_code=status.HTTP_201_CREATED,
)
def bridge_commission_accrue(
    body: BridgeSourceRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    finance: FinanceGatewayService = Depends(get_finance_service),
) -> GlBridgePostingEnvelope:
    reject_context_override(body.model_dump())
    result = finance.bridge_commission_accrue(
        ctx,
        commission_id=body.source_id,
        period_id=body.period_id,
        idempotency_key=body.idempotency_key,
        human_confirm=body.human_confirm,
    )
    raise_for_result(result)
    assert result.data is not None
    return GlBridgePostingEnvelope.model_validate(
        {"data": _gl_bridge_posting(result.data), "audit_id": result.audit_id}
    )


@gl_bridge_router.post(
    "/realized-fx",
    response_model=GlBridgePostingEnvelope,
    status_code=status.HTTP_201_CREATED,
)
def bridge_realized_fx(
    body: BridgeSourceRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    finance: FinanceGatewayService = Depends(get_finance_service),
) -> GlBridgePostingEnvelope:
    reject_context_override(body.model_dump())
    result = finance.bridge_realized_fx(
        ctx,
        realized_fx_event_id=body.source_id,
        period_id=body.period_id,
        idempotency_key=body.idempotency_key,
        human_confirm=body.human_confirm,
    )
    raise_for_result(result)
    assert result.data is not None
    return GlBridgePostingEnvelope.model_validate(
        {"data": _gl_bridge_posting(result.data), "audit_id": result.audit_id}
    )


def _gl_fx_revaluation(revaluation: GlFxRevaluation) -> dict:
    return {
        "id": revaluation.id,
        "period_id": revaluation.period_id,
        "from_currency": revaluation.from_currency,
        "to_currency": revaluation.to_currency,
        "rate": revaluation.rate,
        "amount": revaluation.amount,
        "side": revaluation.side.value,
        "status": revaluation.status.value,
        "journal_entry_id": revaluation.journal_entry_id,
        "created_at": revaluation.created_at,
        "posted_at": revaluation.posted_at,
        "version": revaluation.version,
    }


@gl_fx_revaluation_router.post(
    "",
    response_model=GlFxRevaluationEnvelope,
    status_code=status.HTTP_201_CREATED,
)
def create_fx_revaluation(
    body: CreateGlFxRevaluationRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    finance: FinanceGatewayService = Depends(get_finance_service),
) -> GlFxRevaluationEnvelope:
    reject_context_override(body.model_dump())
    result = finance.create_fx_revaluation(
        ctx,
        period_id=body.period_id,
        from_currency=body.from_currency,
        to_currency=body.to_currency,
        amount=body.amount,
        side=body.side,
        idempotency_key=body.idempotency_key,
        rate=body.rate,
    )
    raise_for_result(result)
    assert result.data is not None
    return GlFxRevaluationEnvelope.model_validate(
        {"data": _gl_fx_revaluation(result.data), "audit_id": result.audit_id}
    )


@gl_fx_revaluation_router.get(
    "/{revaluation_id}", response_model=GlFxRevaluationEnvelope
)
def get_fx_revaluation(
    revaluation_id: UUID,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    finance: FinanceGatewayService = Depends(get_finance_service),
) -> GlFxRevaluationEnvelope:
    result = finance.get_fx_revaluation(ctx, revaluation_id=revaluation_id)
    raise_for_result(result)
    assert result.data is not None
    return GlFxRevaluationEnvelope.model_validate(
        {"data": _gl_fx_revaluation(result.data)}
    )


@gl_fx_revaluation_router.post(
    "/{revaluation_id}/post", response_model=GlFxRevaluationEnvelope
)
def post_fx_revaluation(
    revaluation_id: UUID,
    body: PostGlFxRevaluationRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    finance: FinanceGatewayService = Depends(get_finance_service),
) -> GlFxRevaluationEnvelope:
    reject_context_override(body.model_dump())
    result = finance.post_fx_revaluation(
        ctx,
        revaluation_id=revaluation_id,
        idempotency_key=body.idempotency_key,
        human_confirm=body.human_confirm,
    )
    raise_for_result(result)
    assert result.data is not None
    return GlFxRevaluationEnvelope.model_validate(
        {"data": _gl_fx_revaluation(result.data), "audit_id": result.audit_id}
    )


def _bank_statement(statement: BankStatement) -> dict:
    return {
        "id": statement.id,
        "account_ref": statement.account_ref,
        "statement_date": statement.statement_date,
        "currency": statement.currency,
        "status": statement.status.value,
        "created_at": statement.created_at,
        "cleared_at": statement.cleared_at,
        "version": statement.version,
        "lines": [
            {
                "id": line.id,
                "amount": line.amount,
                "description": line.description,
                "status": line.status.value,
                "matched_journal_line_id": line.matched_journal_line_id,
                "matched_receipt_id": line.matched_receipt_id,
            }
            for line in statement.lines
        ],
    }


@bank_statement_router.post(
    "",
    response_model=BankStatementEnvelope,
    status_code=status.HTTP_201_CREATED,
)
def create_bank_statement(
    body: CreateBankStatementRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    finance: FinanceGatewayService = Depends(get_finance_service),
) -> BankStatementEnvelope:
    reject_context_override(body.model_dump())
    result = finance.create_bank_statement(
        ctx,
        account_ref=body.account_ref,
        statement_date=body.statement_date,
        currency=body.currency,
        lines=[line.model_dump() for line in body.lines],
    )
    raise_for_result(result)
    assert result.data is not None
    return BankStatementEnvelope.model_validate(
        {"data": _bank_statement(result.data), "audit_id": result.audit_id}
    )


@bank_statement_router.get(
    "/{statement_id}", response_model=BankStatementEnvelope
)
def get_bank_statement(
    statement_id: UUID,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    finance: FinanceGatewayService = Depends(get_finance_service),
) -> BankStatementEnvelope:
    result = finance.get_bank_statement(ctx, statement_id=statement_id)
    raise_for_result(result)
    assert result.data is not None
    return BankStatementEnvelope.model_validate(
        {"data": _bank_statement(result.data)}
    )


@bank_statement_router.post(
    "/{statement_id}/lines/{line_id}/match",
    response_model=BankStatementEnvelope,
)
def match_bank_statement_line(
    statement_id: UUID,
    line_id: UUID,
    body: MatchBankStatementLineRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    finance: FinanceGatewayService = Depends(get_finance_service),
) -> BankStatementEnvelope:
    reject_context_override(body.model_dump())
    result = finance.match_bank_statement_line(
        ctx,
        statement_id=statement_id,
        line_id=line_id,
        matched_journal_line_id=body.matched_journal_line_id,
        matched_receipt_id=body.matched_receipt_id,
    )
    raise_for_result(result)
    assert result.data is not None
    return BankStatementEnvelope.model_validate(
        {"data": _bank_statement(result.data), "audit_id": result.audit_id}
    )


@bank_statement_router.post(
    "/{statement_id}/clear", response_model=BankStatementEnvelope
)
def clear_bank_statement(
    statement_id: UUID,
    body: ClearBankStatementRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    finance: FinanceGatewayService = Depends(get_finance_service),
) -> BankStatementEnvelope:
    reject_context_override(body.model_dump())
    result = finance.clear_bank_statement(
        ctx,
        statement_id=statement_id,
        human_confirm=body.human_confirm,
    )
    raise_for_result(result)
    assert result.data is not None
    return BankStatementEnvelope.model_validate(
        {"data": _bank_statement(result.data), "audit_id": result.audit_id}
    )


@commission_router.post(
    "",
    response_model=CommissionEntryEnvelope,
    status_code=status.HTTP_201_CREATED,
)
def accrue_commission(
    body: AccrueCommissionRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    finance: FinanceGatewayService = Depends(get_finance_service),
) -> CommissionEntryEnvelope:
    reject_context_override(body.model_dump())
    result = finance.accrue_commission(
        ctx,
        invoice_id=body.invoice_id,
        beneficiary_subject_id=body.beneficiary_subject_id,
        amount=body.amount,
        currency=body.currency,
        idempotency_key=body.idempotency_key,
    )
    raise_for_result(result)
    assert result.data is not None
    return CommissionEntryEnvelope.model_validate(
        {"data": _commission(result.data), "audit_id": result.audit_id}
    )


@commission_router.post(
    "/{commission_id}/payable", response_model=CommissionEntryEnvelope
)
def mark_commission_payable(
    commission_id: UUID,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    finance: FinanceGatewayService = Depends(get_finance_service),
) -> CommissionEntryEnvelope:
    result = finance.mark_commission_payable(ctx, commission_id=commission_id)
    raise_for_result(result)
    assert result.data is not None
    return CommissionEntryEnvelope.model_validate(
        {"data": _commission(result.data), "audit_id": result.audit_id}
    )


@commission_router.post(
    "/{commission_id}/paid", response_model=CommissionEntryEnvelope
)
def mark_commission_paid(
    commission_id: UUID,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    finance: FinanceGatewayService = Depends(get_finance_service),
) -> CommissionEntryEnvelope:
    result = finance.mark_commission_paid(ctx, commission_id=commission_id)
    raise_for_result(result)
    assert result.data is not None
    return CommissionEntryEnvelope.model_validate(
        {"data": _commission(result.data), "audit_id": result.audit_id}
    )


@commission_router.get(
    "/{commission_id}", response_model=CommissionEntryEnvelope
)
def get_commission(
    commission_id: UUID,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    finance: FinanceGatewayService = Depends(get_finance_service),
) -> CommissionEntryEnvelope:
    result = finance.get_commission(ctx, commission_id=commission_id)
    raise_for_result(result)
    assert result.data is not None
    return CommissionEntryEnvelope.model_validate(
        {"data": _commission(result.data)}
    )
