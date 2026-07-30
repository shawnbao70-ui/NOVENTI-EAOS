# Workflow DO.release Approval G365 Summary

**Status:** System-generated governance artifact — COMPLETE  
**Milestone:** PHX-G365  
**Authorization:** `WF_DO_RELEASE_APPROVAL_CODING_AUTHORIZATION_SUMMARY.md`

- Added Alembic revision `0087_crm_do_release_approval_g365`.
- Added the tenant-scoped `do_release_approval_required` policy and
  protected GET/PUT API at `/v1/crm/policies/do-release-approval`.
- When enabled, `DO.release` requires an approved Workflow action
  `crm.delivery_order.release` bound to the target delivery-order ID.
  Human Confirm remains a separate local gate; Workflow approval never
  releases an order.
- Contract coverage verifies unchanged policy-off behavior, fail-closed
  denial, and explicit release after approval.

**TRACK-DO-RELEASE-APPROVAL COMPLETE / TRACK-G365 COMPLETE**
