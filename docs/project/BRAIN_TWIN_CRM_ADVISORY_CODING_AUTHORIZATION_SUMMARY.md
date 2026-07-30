# Coding Authorization Summary — Brain/Twin CRM Advisory Projection (Z3)

## Milestone

**PHX-G327** — Z3, following PHX-G326 / F3 (tip `0059`).

## Alembic

**None** (live assemble from existing Twin/Brain + CRM records). Tip remains
`0059_crm_return_authorization_g325`.

## Authorized

Package `noventi.crm`: mount read-only customer advisory projection
`GET /v1/crm/customers/{id}/advisory` (closed envelope; refs only;
`execution_authority: "none"`), Permission default-deny read on
`pkg.crm.customer360`, wire TransactionalCustomerAdvisoryService into gateway,
contracts + gateway G327 tests proving advisory allow-path AND that Brain
execute / Twin authorize remain **HTTP 403** with stable forbid codes.
Do **not** embed advisory into Customer360 `/360`.

## Out

Any success path for Brain execute or Twin authorize; Cap→grant; Brain-driven
commercial writes; Twin `authorize_execution=true`; RET2; live NETWORK; AP2+.

## Hard invariants

```text
Brain execute: CLOSED
Twin authorize: CLOSED
```

## Product Owner response

**Approve — 2026-07-26 explicit “Z3（Brain/Twin advisory）” authorization.**  
Milestone: **PHX-G327**. Auto-stop at TRACK-Z3 COMPLETE with execute/authorize CLOSED.
