# ADR-0331 — CRM Commercial Hold Gate Boundary

**状态：** Accepted（design boundary only）  
**日期：** 2026-07-24  
**上位边界：** ADR-0315  
**里程碑（coding）：** PHX-G304（独立 Coding Authorization）

## Decision

C11 adds a tenant-scoped Customer boolean `commercial_hold` (default false).
While true, CRM must fail closed on Sales Order confirm and Delivery Order
create after resolving Customer through Requirement→Opportunity lineage.

This is an operational gate hook, not a credit-limit, aging, or override
engine. Hold mutation is an audited customer update surface.

## Out

Numeric credit limits, AR balance comparison, overdue aging, override/bypass
entities, Approval Center / Workflow hooks (C12), PSP, GL, Brain/Twin.
