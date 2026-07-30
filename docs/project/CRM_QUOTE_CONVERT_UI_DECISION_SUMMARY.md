# Decision Summary — CRM Quote Convert UI

> **Only Product Owner approval entry**  
> Approved in conversation on 2026-07-29.

## Package

CRM — Quote Convert UI

## Purpose

Provide governed Quote Convert workflows for issued Quotes, including
conversion result display and Sales Order shell creation from a ready
conversion.

## Scope

First CRM Business UI serial AC→AJ slice; candidate PHX-G518. Convert path
only; no Confirm, Issue, Delivery, Invoice, or Return Authorization UI.

## Architecture Boundary

CRM-owned Smart Terminal UI over existing Convert, Conversion, and Sales Order
create APIs. Trusted context supplies Tenant and actor; server Permission
remains authoritative. Convert requires an issued Quote. Idempotency keys and
optional approval_ref follow existing contracts. High-impact convert and SO
shell creation require explicit UI confirmation.

## In Scope

- Issued Quote selection from the governed Quote collection
- Convert action with idempotency_key and optional FX / approval_ref
- Conversion detail / status display
- Create Sales Order shell from a ready conversion
- Permission-projected controls and fail-closed states
- Frontend contracts and browser evidence after Coding Authorization

## Out of Scope

- Quote Issue UI, Sales Order Confirm, Delivery, AR Invoice, Return Auth
- Sales Order collection/list expansion beyond get-after-create
- Database, Alembic, Kernel, Runtime Manifest
- Finance GL, Brain, Twin, production, automatic writes
- G519+

## Open Decisions

1. Existing Convert / Conversion / create-SO APIs are the dependency.
2. Only issued Quotes are convertible; draft Quotes remain non-actionable.
3. Idempotent convert returns the existing conversion without overwrite.
4. Optional approval_ref is required only when server policy demands it.
5. SO create from conversion is included; SO confirm remains G520.
6. Missing prerequisite places G518 on HOLD.

## Risks

Duplicate convert conflicts, approval-gate unavailability, FX validation,
cross-tenant association, and accidental opening of Confirm/Issue UI.

## Recommendation

Approve this design boundary and retain `Coding Authorization: None`.
