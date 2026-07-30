# CRM Requirement Product Architecture Gate

**状态：** Gate Accepted（design boundary only）  
**规范源：** ADR-0323  
**授权源：** Approved CRM Requirement Decision Summary

## Gate In

- `noventi.crm` Requirement aggregate
- Mandatory active same-tenant Opportunity
- Opaque ID, system code, title and optional description
- `active` / `archived`, versioning, Permission and audit boundaries

## Gate Out

- Analysis/matching, Sample, Quote/Convert/SO/Finance
- Requirement360, trace links, requirement_count, AI/mining
- Brain/Twin, events, Legacy implementation inheritance, hard delete

## Invariants

1. Package ownership; no Kernel CRM entity.
2. Missing/cross-tenant Opportunity fails closed.
3. Permission default-deny; C3 has no owner field and future owner never authorizes.
4. Audit contains intent/result but no requirement text.
5. This Gate does not open C4.

## Decision

Accepted from Product Owner conversation preauthorization on 2026-07-24.
Coding authorization remains a separate record.
