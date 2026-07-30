# Decision Summary — CRM Quote Lines Managed UI

> **Only Product Owner approval entry**  
> Approved in conversation on 2026-07-29.

## Package

CRM — Quote Lines Managed UI

## Purpose

Provide governed Quote Line list, detail, create, edit, and archive workflows.

## Scope

Fourth CRM Business UI serial slice; candidate PHX-G517. Quote Line management
within the selected Quote Header only.

## Architecture Boundary

CRM-owned Smart Terminal UI over existing Quote Line APIs. Trusted context
supplies Tenant and actor; server Permission remains authoritative. The
selected Quote Header is the governed parent resource. Updates and archives use
`expected_version`; archive replaces hard delete.

## In Scope

- Quote Line list/detail/create/edit/archive
- Selected Quote Header parent association
- Description, quantity, unit price, calculated amount, and line status
- Permission-projected controls
- Loading, denied, missing, conflict, and validation states
- Frontend contracts and browser evidence after Coding Authorization

## Out of Scope

- Quote Issue, Convert, approvals, automatic pricing, discounts, or taxes
- Quote Header expansion or ungated backend changes
- Database, Alembic, Kernel, Runtime Manifest
- Finance, Brain, Twin, production, or automatic writes
- G518+

## Open Decisions

1. Existing Quote Line APIs are the implementation dependency.
2. Lines load only for the selected governed Quote Header.
3. Quantity uses the existing three-decimal contract.
4. Unit price uses the existing two-decimal contract.
5. Amount is server-calculated and read-only in the UI.
6. A 409 stops and refreshes without overwrite.

## Risks

Decimal precision, stale parent selection, cross-tenant association,
authorization confusion, and stale versions.

## Recommendation

Approve this design boundary and retain `Coding Authorization: None`.
