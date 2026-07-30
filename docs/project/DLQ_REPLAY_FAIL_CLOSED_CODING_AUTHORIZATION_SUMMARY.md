# Coding Authorization Summary — DLQ/Replay Fail-Closed Probe (G383)

## Milestone

**PHX-G383** — Event Bus DLQ/replay fail-closed honesty on status + probe contracts.

## Alembic

**none** — tip remains `0092_finance_realized_fx_gl_bridge_g372`.

## Authorized

1. Extend `GET /v1/events/status` with closed fields:
   `dead_letter_*_access=permission_gated`, `event_replay_access=permission_gated`,
   `fail_closed_without_grant=true`.
2. Contracts proving unauthenticated → 401 and ungated subject → 403
   `PERMISSION_DENIED` on dead-letter list/replay and event replay.
3. OpenAPI parity; no invent of ungated DLQ write paths.

## Out

Commercial domain-event emits (G384–G385), catalog/Terminal projection (G386),
baseline (G387), Marketplace PSP, host installs.

## Product Owner response

**Approve — Batch-A; auto-continue G384–G387.**
