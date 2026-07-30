# Decision Summary — CRM Quote Issue UI

> **Only Product Owner approval entry**  
> Approved in conversation on 2026-07-29 (AK→AR third slice).

## Package

CRM — Quote Issue UI

## Purpose

Provide governed Quote Issue (local publish) workflows for draft Quotes.

## Scope

Third CRM Business UI serial AK→AR slice; candidate PHX-G522. Quote Issue
path only; no Convert behavior change, Sales Order Confirm, Delivery,
Invoice, Return Authorization, or Commercial Hold UI.

## Architecture Boundary

CRM-owned Smart Terminal UI over the existing
`POST /v1/crm/quotes/{id}/issue` API. Trusted context supplies Tenant and
actor; server Permission remains authoritative. Issue requires
`human_confirm: true`, idempotency_key, and optional approval_ref per
existing contracts. High-impact Issue requires explicit UI confirmation.
Selected Quote comes from the governed G516 collection.

## In Scope

- Issue action for selected `draft` Quotes
- Idempotency key generation and optional approval_ref
- Post-issue Quote detail refresh
- Permission-projected controls and fail-closed states
- Frontend contracts and browser evidence after Coding Authorization

## Out of Scope

- Convert behavior changes, Sales Order Confirm, Delivery, Invoice, RA
- Commercial Hold write
- Database, Alembic, Kernel, Runtime Manifest
- Finance GL, Brain, Twin, production, automatic writes
- G523+

## Open Decisions

1. Existing Issue API is the dependency.
2. Only `draft` Quotes expose Issue; already issued stay read-only for Issue.
3. Idempotent Issue returns the existing issued Quote without overwrite.
4. Optional approval_ref is required only when server policy demands it.
5. Missing prerequisite places G522 on HOLD.

## Risks

Duplicate Issue conflicts, approval-gate unavailability, commercial-hold
blocks, and accidental Convert/Confirm/Delivery scope.

## Recommendation

Approve this design boundary and retain `Coding Authorization: None`.
