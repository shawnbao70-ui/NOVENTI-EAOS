# CRM Quote Product Gate Acceptance

**状态：** Gate Accepted（design boundary only；system-generated）  
**日期：** 2026-07-24  
**规范源：** ADR-0324

## Product Owner authorization

Approve design boundary through the C4 conversation preauthorization.

## Accepted

Quote is a tenant-scoped draft shell below an active same-tenant Requirement,
with opaque ID, system code, currency label, notes, default-deny Permission,
audited writes and archive-first lifecycle.

## Deferred / Out

All commercial line and pricing behavior, issuance/approval, Convert/SO,
Finance/PSP, document rendering, AI and runtime events.

## Outcome

**ACCEPTED — DESIGN BOUNDARY ONLY.**
