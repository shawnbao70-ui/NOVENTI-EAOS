# Workflow SO.confirm Approval G364 Summary

**Status:** System-generated governance artifact — COMPLETE  
**Milestone:** PHX-G364  
**Authorization:** `WF_SO_CONFIRM_APPROVAL_CODING_AUTHORIZATION_SUMMARY.md`

- Added Alembic revision `0086_crm_so_confirm_approval_g364`.
- Added the tenant-scoped `so_confirm_workflow_approval_required` policy and
  protected GET/PUT API at `/v1/crm/policies/so-confirm-workflow-approval`.
- When enabled, `SO.confirm` requires an approved Workflow action
  `crm.sales_order.confirm` bound to the target sales-order ID. The existing
  local `ConfirmApprovalGate` remains separate; when both policies are enabled,
  both must approve.
- Workflow approval never confirms an order. Contract coverage verifies
  unchanged policy-off behavior, fail-closed denial, and explicit confirmation
  after approval.

**TRACK-SO-CONFIRM-APPROVAL COMPLETE / TRACK-G364 COMPLETE**
