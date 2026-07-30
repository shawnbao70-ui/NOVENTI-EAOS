# Decision Summary — CRM Confirm Approval Hook (C12)

> ADR-0321 decision surface; ADR-0332 boundary applies.

## Purpose

Add a minimal, fail-closed optional Workflow/Approval hook on Sales Order
confirm without opening a full Approval Center product.

## Gate In

- Attach only to `confirm_sales_order`
- Tenant policy `confirm_approval_required` (default false)
- Narrow `ConfirmApprovalGate` port: approved | denied | unavailable
- Required + missing/unavailable/denied → fail closed
- Keep `human_confirm` and C11 commercial hold
- Audited policy mutation and blocked/successful confirm (no commercial PII)

## Gate Out

Approval Center CRUD, workflow authoring, DO/AR invoice hooks, Invoice
issue/post, PSP, GL, credit engine, Brain/Twin, silent/AI auto-approve.

## Decisions

- Default policy false preserves current green path: Accept.
- Hook order: authorize → human_confirm → commercial hold → approval → mutate: Accept.
- No SO mutation from external approval callbacks in this slice: Accept.

## Product Owner response

**Approve — 2026-07-25 conversation authorization (design only).**
