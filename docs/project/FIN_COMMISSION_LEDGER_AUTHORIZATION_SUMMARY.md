# APPROVAL REQUEST — Finance Commission Ledger Shell (Z2 / Wave Z)

> Approved Authorization Summary for ADR-0322.  
> Product Owner approved the design boundary only on 2026-07-26.  
> Coding always requires a **separate** explicit Coding Authorization.

## Package name

`noventi.finance` — proposed resource `pkg.finance.commission`  
(CRM supplies issued AR Invoice source trace only; not Kernel.)

## Purpose

Auditable **accrual-only** commission ledger row tied to one commercial
source, without paying anyone and without payroll/PSP/GL closure.

## Scope

### Proposed Gate In

- Entity `CommissionEntry`: tenant_id, source_invoice_id,
  beneficiary_subject_id, currency, amount, status=`accrued` only,
  idempotency_key, created_at, version
- Service `accrue_commission(...)` with **explicit amount** (no pricing engine)
- Fail-closed: source invoice `issued`; currency matches invoice; amount > 0;
  beneficiary known/eligible in tenant
- Uniqueness: tenant+idempotency_key **and**
  tenant+invoice+beneficiary (prevent double accrual)
- Permission default-deny create/read on `pkg.finance.commission`
- HTTP: `POST /v1/finance/commissions`, `GET /v1/finance/commissions/{id}`
- Audit `Finance.Commission.Accrue` (empty details; amount on entity)
- `PHX-G314` is a candidate label only; it is not opened or assigned by this design approval

### Explicit Gate Out

Payroll/payout execution; bank/PSP transfer; partner portal; multi-tier
hierarchy; clawback automation; GL/journal; tax withholding; Brain execute /
Twin authorize; Customer360 write-back; payable/paid/cancelled transitions
(Defer Z2b); Z3.

## Major architectural decisions (proposed — Accept/Amend)

1. **Package ownership:** `noventi.finance` / `pkg.finance.commission`
   (not `noventi.crm`).
2. **Source document:** **issued AR Invoice only** (not confirmed SO).
3. **Status:** `accrued` only in Z2 — no status machine beyond create.
4. **Amount:** explicit in request; currency in request must match invoice
   (or derive currency from invoice — PO may Amend).
5. **Customer360:** optional read enrich later; **not required** for Z2 green.

## Alembic risk evaluation (design-only)

| Fact | Assessment |
|---|---|
| Current tip (verified) | `0048_finance_ar_credit_note_g312` |
| Z1 Customer360 | TRACK-Z1 COMPLETE via **live assemble** — **no** `0049_crm_customer360_projection_g313` was created |
| PO draft revision id | `0050_finance_commission_ledger_g314` (assumed Z1 tip = 0049) |
| Linear-head risk | Using `0050` while `0049` is free **skips a revision id** and breaks contiguous Alembic discipline |
| Recommended if design Approve later authorizes a table | Next free: **`0049_finance_commission_ledger_g314`** |
| Alternative (zero-migration) | In-memory/service-only accrual without table — **not** recommended for an auditable ledger shell; table is the natural Gate In |
| Tip-bump blast radius | Many contract/integration tests + `RELEASE_MANIFEST` / topology / runbook hardcode tip `0048`; any migration requires coordinated tip bump (exclude historical N1 docs that *name* revision 0048) |
| Cross-schema FK risk | FK to `crm.ar_invoices` + `kernel.tenants` (+ optional subject) — same pattern as credit notes; ORM should omit cross-Base FKs (Alembic owns DB FKs) |
| Collision risk | No second parallel milestone; do not invent Customer360 `0049` retroactively |

**Recommendation on Alembic:** If coding is later authorized, use
**`0049_finance_commission_ledger_g314`** (not `0050`) unless PO explicitly
Accepts a skip and documents why.

## Open decisions requiring Product Owner input

1. Confirm package = `noventi.finance` (vs CRM-owned ledger).
2. Confirm source = issued AR Invoice only.
3. Confirm currency: request field + match invoice, or derive-from-invoice only.
4. Confirm Alembic id: accept **`0049_…_g314`** given actual tip `0048`, or
   Amend with explicit skip rationale for `0050`.
5. Confirm uniqueness: both idempotency **and** (invoice, beneficiary).

## Risks

- Accruals without payout may accumulate unread rows (accepted until Z2b).
- Beneficiary eligibility model (Identity eligibility vs HR role) may be
  thinner than sales-ops expect.
- Tip-bump surface is large; migration coding without separate Coding Auth
  is forbidden.

## Recommendation

**Approve design boundary only** with the generated dispositions below.  
Do **not** authorize coding, Alembic, gateway, or tip bumps in this response.
Issue a separate Coding Authorization and milestone assignment before any
implementation.

## Product Owner response

**Approve — 2026-07-26 (explicit conversation authorization).**

Generated dispositions:

1. Package = `noventi.finance`.
2. Source = issued AR Invoice only.
3. Currency = explicit request field; must match invoice currency.
4. If a table is later authorized, next revision recommendation = `0049_finance_commission_ledger_g314`; this approval does not create it.
5. Enforce both tenant+idempotency and tenant+invoice+beneficiary uniqueness in the future design contract.

**Coding Authorization: None. Implementation milestone: None assigned.**
