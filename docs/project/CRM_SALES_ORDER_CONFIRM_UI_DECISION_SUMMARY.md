# Decision Summary — CRM Sales Order Confirm UI

> **Only Product Owner approval entry**  
> Approved in conversation on 2026-07-29 (AK→AR first slice).

## Package

CRM — Sales Order Confirm UI

## Purpose

Provide governed Sales Order Confirm workflows for created Sales Order shells.

## Scope

First CRM Business UI serial AK→AR slice; candidate PHX-G520. Confirm path
only; no Delivery, Invoice, Return Authorization, or Quote Issue UI.

## Architecture Boundary

CRM-owned Smart Terminal UI over the existing Confirm API. Trusted context
supplies Tenant and actor; server Permission remains authoritative. Confirm
requires `human_confirm: true`, idempotency_key, and optional approval_ref
per existing contracts. High-impact Confirm requires explicit UI confirmation.
Selected Sales Order comes from the governed G519 collection.

## In Scope

- Confirm action for selected `created` Sales Orders
- Idempotency key generation and optional approval_ref
- Post-confirm detail and line refresh (lines materialize on Confirm)
- Permission-projected controls and fail-closed states
- Frontend contracts and browser evidence after Coding Authorization

## Out of Scope

- Delivery Order, AR Invoice, Return Authorization, Quote Issue
- Confirm-policy administration beyond existing optional approval_ref
- Database, Alembic, Kernel, Runtime Manifest
- Finance GL, Brain, Twin, production, automatic writes
- G521+

## Open Decisions

1. Existing `POST /v1/crm/sales-orders/{id}/confirm` is the dependency.
2. Only `created` Sales Orders expose Confirm; already confirmed stay read-only.
3. Idempotent Confirm returns the existing confirmed order without overwrite.
4. Optional approval_ref is required only when server policy demands it.
5. Missing prerequisite places G520 on HOLD.

## Risks

Duplicate Confirm conflicts, approval-gate unavailability, commercial-hold
blocks, cross-tenant association, and accidental Delivery/Invoice scope.

## Recommendation

Approve this design boundary and retain `Coding Authorization: None`.
