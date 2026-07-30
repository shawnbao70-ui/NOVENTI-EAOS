# Gate Acceptance — CRM Opportunity Minimal List Query

> **System-generated governance artifact**  
> Product Owner editing is neither required nor permitted.

## References

- Framework ADR: [ADR-0321](../decisions/ADR-0321-phoenix-gate-framework.md)
- Approved Decision Summary:
  [CRM_OPPORTUNITY_LIST_QUERY_DECISION_SUMMARY.md](CRM_OPPORTUNITY_LIST_QUERY_DECISION_SUMMARY.md)
- Architecture Gate:
  [CRM_OPPORTUNITY_LIST_QUERY_ARCHITECTURE_GATE.md](CRM_OPPORTUNITY_LIST_QUERY_ARCHITECTURE_GATE.md)
- Approval Record:
  [CRM_OPPORTUNITY_LIST_QUERY_APPROVAL_RECORD.md](CRM_OPPORTUNITY_LIST_QUERY_APPROVAL_RECORD.md)
- Evidence:
  [G514 HOLD](CRM_OPPORTUNITY_UI_G514_HOLD.md)

## Independent states

- Accepted Knowledge: **Independent / unchanged**
- Architecture Gate Accepted: **Yes — design boundary only**
- Coding Authorization: **None**
- G514 implementation: **HOLD**
- G515–G521: **Closed**

No state above automatically changes another.

## Acceptance assertions

| ID | Assertion | Result | Evidence |
|---|---|---|---|
| AC-01 | Exact nine-field Summary | Pass | approved Summary |
| AC-02 | Explicit Product Owner Approve | Pass | Approval Record |
| AC-03 | Query is tenant-scoped and default-deny | Pass | Gate |
| AC-04 | Pagination and active-only defaults are bounded | Pass | Gate |
| AC-05 | Collection projection is fixed and minimal | Pass | Gate |
| AC-06 | No Database or Alembic expansion | Pass | Gate |
| AC-07 | Gate does not resume G514 | Pass | Approval Record / HOLD |

## OD dispositions

OD-01 through OD-05 are accepted exactly as generated in the Architecture
Gate.

## RC attestations

RC-01 through RC-08 pass against governance evidence. Implementation and
runtime evidence remain absent and are not inferred.

## Approval Record

- Product Owner decision: **Approve**
- Decision date: 2026-07-28
- Approval meaning: Opportunity list-query design only
- Coding Authorization: **None**

## Signature

System-generated projection of the explicit Product Owner `Approve` response.
No manual signature is required.

## Evidence

- ADR-0321: available
- Opportunity detail/write routes and G514 HOLD: available
- List-query implementation evidence: not applicable

## Result

**Gate Accepted (design boundary only). Coding Authorization: None.**

G514 remains HOLD. This Acceptance grants no API, Service, Repository,
frontend, Database, Alembic, Runtime Manifest, production, or business-write
authority.
