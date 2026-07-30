# Coding Authorization Summary — Outbox Worker/Lease Status Honesty (G382)

## Milestone

**PHX-G382** — Event Bus `/status` honesty for outbox worker and lease posture.

## Alembic

**none** — tip remains `0092_finance_realized_fx_gl_bridge_g372`.

## Authorized

1. Deepen `GET /v1/events/status` with closed fields stating there is **no**
   persistent background worker daemon; dispatch is on-demand via
   `POST /v1/events/dispatch` with claim-based leases.
2. Align OpenAPI (`event.openapi.yaml`) and runtime DTO (`EventStatusEnvelope`).
3. Correct surface naming honesty (`outbox_enqueue` vs invented `outbox_list`).
4. Contracts proving honesty flags and no worker-daemon invent routes.

## Out

DLQ/replay probe deepen (G383), commercial domain-event emits (G384–G385),
catalog/Terminal projection (G386), baseline (G387), Marketplace PSP, host installs.

## Product Owner response

**Approve — Batch-A; auto-continue G383–G387.**
