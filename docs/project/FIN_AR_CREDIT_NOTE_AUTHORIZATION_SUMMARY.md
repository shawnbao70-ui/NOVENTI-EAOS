# Decision Summary — Finance AR Credit Note Shell (N1 / Wave N)

> ADR-0321 decision surface; ADR-0339 boundary applies.
> System-generated governance artifact from PO conversation authorization.

## Package

`noventi.finance` — `pkg.finance.credit_note` (not Kernel)

## Purpose

Create an auditable AR Credit Note document traced to one AR Invoice. Local
draft/issue only — not a GL journal and not a PSP refund.

## Scope

### Gate In

- Credit note status `draft` | `issued` (local issue ≠ GL post)
- Create against invoice with status `issued` OR `voided`
- Amount ≤ invoice total; currency/customer from invoice; tenant isolation;
  idempotent create
- Optional local `issue_credit_note` (human_confirm + issue key)
- Permission default-deny; audit details empty
- Alembic `0048_finance_ar_credit_note_g312`
- HTTP under `/v1/finance/credit-notes`

### Gate Out

Full GL/CoA/journal/period close; tax authority credit; PSP refund execution;
multi-invoice credit application; bad-debt write-off automation; Brain/Twin.

## Major architectural decisions

- Accept target invoice statuses: **issued | voided** only.
- Amount bound is invoice `total_amount` (no open-balance allocation engine).
- Invoice observed via existing `ARInvoiceReadPort`.

## Open decisions requiring Product Owner input

None for N1 — locked by Wave N instruction (Accept proposed).

## Risks

- Multiple credit notes may each pass `amount <= total` without remaining-credit
  tracking (accepted until a later application slice).

## Recommendation

Approve design boundary and authorize coding as PHX-G312.

## Product Owner response

**Approve — 2026-07-25 conversation authorization (design + coding PHX-G312).**
