# Architecture Gate — CRM Commercial Hold Gate (C11)

**Status:** Gate Accepted（design boundary only）  
**Date:** 2026-07-24  
**Package:** `pkg.crm`  
**Decision Summary:** [CRM_COMMERCIAL_HOLD_AUTHORIZATION_SUMMARY.md](CRM_COMMERCIAL_HOLD_AUTHORIZATION_SUMMARY.md)  
**Coding authorization:** None（until Coding Authorization Summary）  
**Implementation milestone:** None（until Coding Authorization）

## Boundary

C11 introduces a package-owned `commercial_hold` boolean on Customer.
When true, `confirm_sales_order` and `create_delivery_order` must fail closed
after resolving the customer through the commercial lineage. Clearing hold
restores the prior path. This is not a credit engine.

## OD dispositions

| ID | Disposition |
|---|---|
| OD-01 Gate SO confirm and DO create | Accept |
| OD-02 Boolean hold only | Accept |
| OD-03 Reuse customer update permission | Accept |

## RC attestations

| ID | Attestation |
|---|---|
| RC-01 Package ≠ Kernel | Hold field and gate live in `noventi.crm` |
| RC-02 Tenant isolation | Repository tenant binding unchanged |
| RC-03 Default-deny Permission | Hold mutate requires customer update grant |
| RC-04 Fail-closed | Missing lineage or hold=true blocks confirm/DO |
| RC-05 Audit | Hold set/clear audited without inventing credit facts |

## Approval record

Product Owner Approve of Decision Summary — 2026-07-24 conversation
authorization (design only).
