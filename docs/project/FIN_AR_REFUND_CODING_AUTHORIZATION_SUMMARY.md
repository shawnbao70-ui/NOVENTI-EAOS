# Coding Authorization Summary — AR Refund ↔ Credit Note (G361)

## Milestone

**PHX-G361** — ADR-0315.7 refund registration linked to issued CN.

## Alembic

**`0084_finance_ar_refund_g361`** revising `0083_…`.

## Authorized

1. `ARRefund` shell: amount, currency, credit_note_id (must be **issued**),
   customer from CN, status draft|posted, idempotency; human_confirm on post.
2. Amount ≤ CN amount; same currency; no PSP payout / bank transfer execution.
3. HTTP create + post (or create-as-posted); contracts.
4. Print/status alone ≠ refund.

## Out

AP write-off (G362), PSP, baseline.

## Product Owner response

**Approve — batch; auto-continue G362.**
