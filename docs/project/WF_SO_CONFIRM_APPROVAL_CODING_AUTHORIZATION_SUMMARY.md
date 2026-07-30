# Coding Authorization Summary — Workflow Approval SO.confirm (G364)

## Milestone

**PHX-G364** — ADR-0318; **unique command: SO.confirm only**.

## Alembic

**`0086_crm_so_confirm_approval_g364`** revising
`0085_purchase_ap_writeoff_close_g362`.

## Authorized

1. Tenant policy `so_confirm_workflow_approval_required` (separate from local
   ConfirmApprovalGate / `confirm_approval_required`).
2. Gate action `crm.sales_order.confirm`; resource_ref=sales_order_id.
3. When Workflow policy on: require approved Workflow; approve ≠ auto confirm.
4. Local ConfirmApprovalGate may still apply when its own policy on (AND both).
5. GET/PUT policy route; contracts.

## Out

DO.release (G365), 3WM, POD, Supplier360.

## Product Owner response

**Approve — Constitution closeout IV.** Auto-continue G365.
