# Coding Authorization Summary — Finance Tax Invoice Shell (Tax1)

## Milestone

**PHX-G316** — Tax1, following PHX-G315 / F2.

## Alembic

**`0051_finance_tax_invoice_shell_g316`** revising
`0050_finance_receipt_psp_port_g315`.

## Authorized

Package `noventi.finance`: tenant-scoped Tax Invoice shell document + lifecycle
`draft → issued → voided`, create/get/issue/void against linked issued AR invoice
context, irreversible void (no reopen), Alembic `0051`, gateway
`/v1/finance/tax-invoices` create/get/issue/void, Permission/audit, contracts +
gateway G316 tests. OpenAPI must not expose tax-filing, tax-authority, rate-port,
GL/journal, or network surfaces on this slice.

## Out

Tax2 rate/authority port, Tax3 authority adapter, live tax authority filing,
`ENABLE_*_NETWORK`, GL/CoA/journal/period, Brain/Twin, Tax2+.

## Prerequisites

- TRACK-F2 COMPLETE; Alembic tip `0050_finance_receipt_psp_port_g315`
- ADR-0316 rewrite boundary (tax invoice ≠ AR ≠ receipt ≠ print)
- Design inventory from Post-CRM queue (this conversation)

## Product Owner response

**Approve — 2026-07-26 explicit “Execute ONLY Tax1 Tax Invoice shell
(PHX-G316 / Alembic 0051)” authorization.**  
Milestone: **PHX-G316**. Auto-stop at TRACK-TAX1 COMPLETE; await Tax2.
