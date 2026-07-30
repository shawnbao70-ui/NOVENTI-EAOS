# Decision Summary — Finance AR Receipt Shell (F1 / Wave R)

> ADR-0321 decision surface; ADR-0337 boundary applies.
> System-generated governance artifact from PO conversation authorization.

## Package

`noventi.finance` — `pkg.finance.receipt` (not Kernel)

## Purpose

Create an auditable Receipt header that may apply to one issued (non-voided)
AR Invoice. Allocation is single-invoice apply only.

## Scope

### Gate In

- Receipt status `draft` | `applied` (no bank settle / posted-local apply only)
- `create_receipt` + `apply_receipt_to_invoice(invoice_id)` requiring
  `invoice.status == issued`
- Amount ≤ invoice total; currency match; tenant isolation; idempotency keys
- Permission default-deny on `pkg.finance.receipt`
- Audit without PAN / PSP secrets
- Alembic `0046_finance_ar_receipt_g310`
- HTTP under `/v1/finance/receipts`

### Gate Out

Live PSP/card/ACH, webhooks, clearing house; multi-invoice allocation;
write-off; refunds; FX revaluation; GL journal; bank reconciliation;
statement engine; AP; tax filing; Brain/Twin; Inventory ship; Customer360
product surface.

## Major architectural decisions

- Finance package owns Receipt; CRM AR Invoice is read via `ARInvoiceReadPort`
  (no CRMService call from Finance).
- Status vocabulary is `draft`/`applied` only in this slice.
- Single-invoice apply; no remaining-balance allocation engine.

## Open decisions requiring Product Owner input

None for F1 — locked by Wave R instruction.

## Risks

- Multiple receipts may each pass `amount <= invoice total` without a
  remaining-balance engine (accepted Out until a later allocation slice).
- Cross-package FK to `crm.ar_invoices` / `crm.customers` couples migrate order
  (0046 after 0045).

## Recommendation

Approve design boundary and authorize coding as PHX-G310.

## Product Owner response

**Approve — 2026-07-25 conversation authorization (design + coding PHX-G310).**
