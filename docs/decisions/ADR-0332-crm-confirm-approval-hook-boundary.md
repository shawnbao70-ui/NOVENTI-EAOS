# ADR-0332 — CRM Confirm Approval Hook Boundary

**状态：** Accepted（design boundary only）  
**日期：** 2026-07-25  
**里程碑（coding）：** PHX-G305

## Decision

C12 adds a tenant-scoped confirm policy (`confirm_approval_required`, default
false) and a package-owned `ConfirmApprovalGate` protocol evaluated only inside
`confirm_sales_order`.

When the policy requires approval:

- missing gate, `unavailable`, or `denied` fail closed
- `approved` is additional to `human_confirm=True` and C11 commercial-hold clear

When the policy does not require approval, confirm behavior is unchanged.

Persistence uses `crm.tenant_confirm_policies` (Alembic
`0045_crm_ar_invoice_void_g309`). Audit covers policy set and
blocked/successful confirm without commercial values or keys.

## Out

Full Approval Center, workflow definition authoring, DO/AR hooks, invoice
issue/post, PSP, GL, Brain/Twin, and silent/AI auto-approve.
