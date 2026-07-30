# Coding Authorization Summary — PHX-G526 AR Invoice Void UI

> Independent authorization under ADR-0321. Approved 2026-07-29.

## Package

CRM — AR Invoice Void UI

## Purpose

Implement the accepted Void UI over the existing void API for a selected
issued AR Invoice.

## Scope

Void control + editor (reason, confirmation, idempotency); post-void refresh;
frontend contracts, browser evidence, and closeout under PHX-G526 only. No
Database/Alembic.

## Architecture Boundary

Trusted Tenant/actor context; `pkg.crm.ar_invoice` `void` Permission
default-deny; Void body `{ idempotency_key, human_confirm: true, reason }`;
only `issued` invoices expose Void; selection from G524 Invoice surface; no
Receipt/GL/RA Restock/Credit Note/Commercial Hold. Contiguous after
TRACK-G525; no parallel second milestone.

## In Scope

Only the accepted PHX-G526 UI Gate boundary.

## Out of Scope

Tenant Invoice list; Receipt; Finance GL; RA Restock/Credit Note; Commercial
Hold; Database/Alembic/Kernel/Runtime Manifest; production; G527+.

## Open Decisions

Existing void endpoint is authoritative (**no HOLD**); only `issued`
invoices expose Void; idempotent void of already-voided returns existing
without overwrite; selection remains G524 DO-scoped create/get.

## Risks

Accidental GL/Receipt/Hold expansion; void without confirmation;
successor-scope drift.

## Recommendation

**Approved** — implement PHX-G526 only.

## Authorization Record

- Coding Authorization: **Approved**
- Milestone: **PHX-G526**
- Backend/Database/Alembic/Runtime/Production: **None**
- Tenant Invoice list: **None**
- PHX-G527: **None**
