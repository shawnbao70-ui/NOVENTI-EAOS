# Coding Authorization Summary — AP Multi Partial Payment (G341)

## Milestone

**PHX-G341** — deepen G336 multi apply on one ApBill.

## Alembic

**`0068_purchase_ap_partial_payment_g341`** revising
`0067_finance_gl_ap_bridges_g338`.

## Authorized

1. Persist/maintain `paid_amount` on ApBill (updated on each apply).
2. Support multiple partial applies: partially_paid → paid when remaining hits 0;
   reject over-apply / draft / supplier-currency mismatch; idempotent apply_key.
3. HTTP: expose remaining/paid on bill GET (and/or balance sub-resource);
   contracts prove second partial then full settle.
4. No PSP/GL changes beyond keeping existing bridges green.

## Out

AR allocation, CN/RMA, tax, Cap→grant, Brain silent writes.

## Product Owner response

**Approve — batch includes G341.** Auto-continue to G342.
