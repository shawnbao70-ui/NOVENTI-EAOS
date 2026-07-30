# Coding Authorization Summary — Fulfillment Qty Conservation (G349)

## Milestone

**PHX-G349** — ADR-0314.2–3 remaining qty / SO fulfillment aggregate.

## Alembic

**`0074_crm_fulfillment_qty_g349`** revising
`0073_crm_quote_issue_approval_g348`.

## Authorized

1. Persist DO lines (or fulfillment allocations) with quantities tied to SO lines.
2. Create DO / ship must respect remaining = ordered − previously shipped
   (and allocated-to-open-DO if modeled); reject over-commit without override.
3. SO fulfillment status aggregated from cumulative ship evidence (e.g.
   `open|partially_shipped|shipped`); not overwritten by a single DO reopen.
4. Keep ship idempotency; no silent double-ship.
5. HTTP + contracts. Reopen≠unship still out unless minimal stamp only.

## Out

FX cash (G350), carrier/POD, WMS, Cap widen, Brain silent writes.

## Product Owner response

**Approve — batch; auto-continue G350.**
