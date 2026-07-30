# Coding Authorization Summary — Purchase Supplier + AP Bill Draft (AP1)

## Milestone

**PHX-G324** — AP1, following PHX-G323 / GL5 (tip `0057`).

## Alembic

**`0058_purchase_supplier_ap_bill_g324`** revising
`0057_finance_gl_bank_recon_g323`.

## Authorized

Package `noventi.purchase` (schema `purchase`): tenant-scoped Supplier master
(`active|archived`) and AP Bill **draft header only** (supplier_id, code,
currency, total_amount, idempotency_key; status=`draft` only), Alembic `0058`,
gateway `/v1/purchase/suppliers` and `/v1/purchase/ap-bills`, Permission/audit,
contracts + gateway G324 tests. OpenAPI must not expose bill lines, PO, GR,
payment, PSP, GL post, tax engine, or Brain/Twin on this slice.

## Out

AP2 bill lines, AP3 PO, AP4 GRN/inventory, AP5 three-way match, payment run,
PSP, GL AP bridge, tax engine, Brain/Twin, RET1/Z3/F3.

## Prerequisites

- TRACK-GL5 COMPLETE; tip `0057_finance_gl_bank_recon_g323`
- ADR-0315 rewrite boundary (AP ≠ payment clearing)
- Design inventory: WAVE AP / AP1 Supplier + AP Bill Draft Shell

## Product Owner response

**Approve — 2026-07-26 explicit “AP1（应付壳）” authorization.**  
Milestone: **PHX-G324**. Auto-stop at TRACK-AP1 COMPLETE; await AP2.
