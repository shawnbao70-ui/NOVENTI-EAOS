# Coding Authorization Summary — Finance Receipt PSP Port (F2)

## Milestone
**PHX-G315** — F2, following PHX-G314 / Z2.

## Alembic
**`0050_finance_receipt_psp_port_g315`** revising
`0049_finance_commission_ledger_g314`.

## Authorized
Package `noventi.finance`: tenant-scoped receipt PSP-required policy, fail-closed
`PspPort`, test-only in-memory fake, PSP receipt reference/status persistence,
permissioned/audited policy HTTP read/write, and contracts.

## Out
No live PSP provider, network transport, webhook, settlement, tax, GL, refund,
or Tax1 implementation.

## Product Owner response
**Approve — 2026-07-26 explicit “Implement Wave R / F2 NOW” authorization.**
