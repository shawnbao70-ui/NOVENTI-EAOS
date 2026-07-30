# PHX-G514 HOLD RESOLVED — Opportunity Managed UI

> **System-generated governance evidence** under ADR-0321.

## Status

- Architecture Gate Accepted: **Yes**
- Coding Authorization: **Consumed by PHX-G514**
- Implementation Milestone: **PHX-G514 COMPLETE**
- Queue state: **RESOLVED**
- Successor slices G515–G521: **Closed**

## Blocking evidence

The accepted Opportunity Managed UI requires a governed collection surface.
Current Gateway capability provides:

- `POST /v1/crm/opportunities`
- `GET /v1/crm/opportunities/{opportunity_id}`
- `PATCH /v1/crm/opportunities/{opportunity_id}`
- `POST /v1/crm/opportunities/{opportunity_id}/archive`

It does not provide:

- a bounded Opportunity collection endpoint;
- a closed Opportunity list DTO/envelope;
- service-level cursor pagination for Opportunity collection access.

The repository's internal customer-scoped enumeration is not a public API and
must not be called or reconstructed by Smart Terminal.

## Disposition

Fail closed. Do not authorize or implement the G514 managed UI until a separate
Product Gate accepts a minimal Opportunity list-query boundary and a separate
Coding Authorization permits that prerequisite implementation.

Resolved by the separately approved PHX-G514 Coding Authorization and accepted
implementation evidence. No authority is extended to G515+.

## Evidence links

- [Opportunity Managed UI Gate](CRM_OPPORTUNITY_MANAGED_UI_ARCHITECTURE_GATE.md)
- [Opportunity Managed UI Acceptance](CRM_OPPORTUNITY_MANAGED_UI_ACCEPTANCE.md)
- `api/gateway/routers/crm.py`
- `api/gateway/schemas/crm.py`
- `noventi/crm/repository.py`
- [PHX-G514 Acceptance](CRM_OPPORTUNITY_UI_G514_ACCEPTANCE.md)
