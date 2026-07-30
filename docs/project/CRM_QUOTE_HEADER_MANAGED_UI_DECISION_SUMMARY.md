# Decision Summary — CRM Quote Header Managed UI

> **Only Product Owner approval entry**  
> Approved in conversation on 2026-07-29.

## Package

CRM — Quote Header Managed UI

## Purpose

Provide governed Quote header list, detail, create, edit, and archive workflows.

## Scope

Third CRM Business UI serial slice; candidate PHX-G516. Header management only.

## Architecture Boundary

CRM-owned Smart Terminal UI over existing APIs. Trusted context supplies Tenant
and actor; server Permission remains authoritative. Updates/archives use
`expected_version`; archive replaces hard delete.

## In Scope

- Quote header list/detail/create/edit/archive
- Governed Requirement association
- Currency and optional notes fields
- Permission-projected controls
- Loading, denied, missing, conflict, and validation states
- Frontend contracts/browser evidence after Coding Authorization

## Out of Scope

- Quote Lines, Issue, Convert, approval workflows, pricing automation
- Ungated backend expansion
- Database, Alembic, Kernel, Runtime Manifest
- Finance, Brain, Twin, production, automatic writes
- G517+

## Open Decisions

1. Existing APIs are the initial dependency.
2. Missing Quote collection capability places G516 on HOLD.
3. Requirement association must use governed records.
4. Currency remains the existing three-character API contract.
5. 409 stops and refreshes without overwrite.

## Risks

Collection gaps, invalid currency, cross-tenant association, authorization
confusion, and stale versions.

## Recommendation

Approve this design boundary and retain `Coding Authorization: None`.
