# Decision Summary — CRM Sales Order Read-only UI

> **Only Product Owner approval entry**  
> Approved in conversation on 2026-07-29.

## Package

CRM — Sales Order Read-only UI

## Purpose

Provide governed Sales Order list, detail, and line read workflows after Quote
Convert.

## Scope

Second CRM Business UI serial AC→AJ slice; candidate PHX-G519. Read-only Sales
Order projection only; no Confirm, Delivery, Invoice, or Return Authorization.

## Architecture Boundary

CRM-owned Smart Terminal UI over existing Sales Order get/line APIs and any
accepted list-query prerequisite. Trusted context supplies Tenant and actor;
server Permission remains authoritative. No write controls in this slice.

## In Scope

- Sales Order collection list/detail (after list prerequisite if required)
- Sales Order line read for the selected Sales Order
- Permission-projected fail-closed read states
- Frontend contracts and browser evidence after Coding Authorization

## Out of Scope

- Sales Order Confirm, Delivery, AR Invoice, Return Authorization
- Quote Convert expansion or Quote Issue UI
- Database, Alembic, Kernel, Runtime Manifest unless separately authorized as
  a list-query prerequisite
- Finance GL, Brain, Twin, production, automatic writes
- G520+

## Open Decisions

1. Existing get/line APIs are the initial dependency.
2. Missing Sales Order collection capability places G519 on HOLD.
3. Confirm remains an independent G520 Coding Authorization.
4. PII and commercial fields remain minimized to existing closed DTOs.
5. No automatic writes or confirmation affordances are exposed.

## Risks

Collection gaps, cross-tenant association, authorization confusion, and
accidental Confirm/Delivery scope expansion.

## Recommendation

Approve this design boundary and retain `Coding Authorization: None`.
