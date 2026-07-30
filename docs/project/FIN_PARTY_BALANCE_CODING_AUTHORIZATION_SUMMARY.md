# Coding Authorization Summary — Party Balance Authority (G346)

## Milestone

**PHX-G346** — ADR-0315.6 unique party balance authority (read projection).

**SUMMARY:** TRACK-PARTY-BALANCE COMPLETE — G347 IN QUEUE; Alembic tip remains
`0071_finance_tax_credit_link_g344`.

## Alembic

**none** — balances are computed from issued AR / allocations / AP bills+paid_amount
(event authority). Tip remains `0071` until G347.

## Authorized

1. Customer AR balance-by-currency: issued invoice totals − allocated − written_off
   (written_off=0 until G347); expose unallocated receipt residual as separate
   non-balance field.
2. Supplier AP balance-by-currency: sum(posted|partially_paid remaining) per
   supplier+currency.
3. HTTP: enrich Customer360 and/or `GET .../balances`; new
   `GET /v1/purchase/suppliers/{id}/balances` (or finance party-balance routes).
4. Permission + audit read; contracts; no silent writes.

## Out

Write-off (G347), Workflow (G348), fulfillment (G349), FX cash (G350), Cap widen.

## Product Owner response

**Approve — Constitution closeout batch; G348=Quote.issue.** Auto-continue G347.
