# CRM Customer360 Read Projection Architecture Gate

**状态：** Gate Accepted（design boundary only）  
**规范源：** ADR-0340  
**证据：** `CRM_CUSTOMER360_AUTHORIZATION_SUMMARY.md` (PO Approve 2026-07-25)

## Invariants

1. Read-only projection; no commercial writes from 360.
2. Permission default-deny on `pkg.crm.customer360` action `read`.
3. Live assemble from CRM (+ Finance traces, Inventory ship presence for open DO).
4. Zero-migration for Z1; fail-closed to live read (no cache authority).
5. No Brain/Twin/commission/payout surfaces.

## Decision

Accepted through Product Owner conversation authorization (Wave Z / Z1).
