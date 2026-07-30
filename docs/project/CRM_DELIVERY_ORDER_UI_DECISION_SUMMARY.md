# Decision Summary — CRM Delivery Order Read / Release UI

> **Only Product Owner approval entry**  
> Approved in conversation on 2026-07-29 (AK→AR fourth slice).

## Package

CRM — Delivery Order Read / Release UI

## Purpose

Provide governed Delivery Order create/read and Release workflows for
confirmed Sales Orders.

## Scope

Fourth CRM Business UI serial AK→AR slice; candidate PHX-G523. Delivery Order
read plus Release (and create shell from Sales Order); no Invoice, Return
Authorization, ship-ledger deepen, or Quote Issue changes.

## Architecture Boundary

CRM-owned Smart Terminal UI over existing
`POST /v1/crm/sales-orders/{id}/delivery-order`,
`GET /v1/crm/delivery-orders/{id}`, and
`POST /v1/crm/delivery-orders/{id}/release`. Trusted context supplies Tenant
and actor; server Permission remains authoritative. Release requires
`human_confirm: true`, idempotency_key, and optional approval_ref. Without a
tenant-scoped Delivery Order collection, selection is Sales-Order-scoped
create/get, or HOLD for a list prerequisite.

## In Scope

- Create Delivery Order shell from a selected confirmed Sales Order
- Read-only Delivery Order detail
- Release with explicit confirmation and post-release refresh
- Permission-projected controls and fail-closed states
- Frontend contracts and browser evidence after Coding Authorization
- HOLD if a missing list prerequisite is required

## Out of Scope

- AR Invoice, Return Authorization, inventory ship deepen
- Quote Issue behavior changes
- Database, Alembic, Kernel, Runtime Manifest unless this slice’s Coding
  Authorization explicitly allows a list prerequisite
- Finance GL, Brain, Twin, production, automatic writes
- G524+

## Open Decisions

1. Existing create/get/release APIs are the dependencies.
2. No `GET /v1/crm/delivery-orders` collection exists; selection is
   SO-scoped create+get, or HOLD for a list prerequisite.
3. Only releasable statuses expose Release.
4. Idempotent Release returns the existing released order without overwrite.
5. Missing prerequisite places G523 on HOLD.

## Risks

Missing list forcing HOLD, duplicate Release, accidental Invoice/Ship
expansion, and cross-tenant association.

## Recommendation

Approve this design boundary and retain `Coding Authorization: None`.
