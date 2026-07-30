# Workflow Quote.convert Approval G353 Summary

**Status:** System-generated governance artifact — COMPLETE  
**Milestone:** PHX-G353  
**Authorization:** `WF_QUOTE_CONVERT_APPROVAL_CODING_AUTHORIZATION_SUMMARY.md`

- Added Alembic revision `0077_crm_quote_convert_approval_g353`.
- Added tenant-scoped `quote_convert_approval_required` policy and its protected
  GET/PUT API at `/v1/crm/policies/quote-convert-approval`.
- When enabled, `Quote.convert` requires approved Workflow action
  `crm.quote.convert` bound to the target quote ID. Workflow approval never
  performs a conversion itself.
- Contract coverage verifies unchanged policy-off behavior, fail-closed denial,
  and explicit conversion after approval.

**TRACK-QUOTE-CONVERT-APPROVAL COMPLETE / TRACK-G353 COMPLETE**
