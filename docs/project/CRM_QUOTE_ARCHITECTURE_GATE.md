# CRM Quote Product Architecture Gate

**状态：** Gate Accepted（design boundary only）  
**规范源：** ADR-0324

## Gate In

- `noventi.crm` Quote draft shell
- Mandatory active same-tenant Requirement
- Opaque ID, system code, currency label, optional notes
- `draft` / `archived`, versioning, Permission and audit

## Gate Out

Lines/pricing/amounts/tax/discount/FX/margin, issue/approve/status pipeline,
Convert/SO/Finance/PSP, documents/templates, Sample/AI/Brain/Twin/events.

## Invariants

1. Quote is package data, not Kernel data.
2. Missing/cross-tenant Requirement fails closed.
3. Permission is default-deny; no owner shortcut exists.
4. Audit details exclude notes.
5. `currency` is a label only; C4 makes no monetary calculation.
6. No Convert or Sales Order boundary is opened.

## Decision

Accepted from Product Owner conversation preauthorization on 2026-07-24.
