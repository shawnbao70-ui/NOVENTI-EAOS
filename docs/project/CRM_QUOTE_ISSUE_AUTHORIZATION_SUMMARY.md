# Decision Summary — CRM Quote Issue (C13)

> ADR-0321 decision surface; ADR-0333 boundary applies.

## Purpose

Add a local Draft→Issued publish gate for Quote so conversion only proceeds
from an auditable issued commercial snapshot.

## Gate In

- Quote status `issued` plus `issue_quote` (human_confirm, ≥1 active line)
- Idempotent issue key; Permission action `issue` on `pkg.crm.quote`
- `convert_quote` requires issued
- Freeze header/line mutation after issue
- Audited `CRM.Quote.Issue` without commercial amounts/keys

## Gate Out

Email/PDF/send, Approval Center, Workflow start, Invoice issue/post, PSP, GL,
inventory/ship, Brain/Twin, C14+.

## Decisions

- Convert fail-closed on draft (intentional product change): Accept.
- Issued quotes are not commercially reopened by line/header edit: Accept.
- Archive remains available as terminal path: Accept.

## Product Owner response

**Approve — 2026-07-25 conversation authorization (design only).**
