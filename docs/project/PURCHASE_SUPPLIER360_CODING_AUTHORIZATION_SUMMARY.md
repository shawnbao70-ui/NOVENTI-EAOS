# Coding Authorization Summary — Supplier360 Read Projection (G368)

## Milestone

**PHX-G368** — Supplier360 read projection (symmetric to Customer360).

## Alembic

**none** — compute/assemble from supplier + AP bills/payments/balances.

## Authorized

1. `GET /v1/purchase/suppliers/{id}/360` (or `/balances` enrichment already
   exists — deliver full 360: supplier header + AP balance-by-currency +
   recent bills/payments summaries).
2. Permission read; audit; no writes.
3. Contracts; tip stays `0089` unless migration forced (prefer none).

## Out

Baseline (G369), Brain writes, host installs.

## Product Owner response

**Approve — batch; auto-continue G369.**
