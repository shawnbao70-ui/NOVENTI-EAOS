# Coding Authorization Summary — AP Payment Shell (AP6)

## Milestone

**PHX-G336** — AP payment / allocation shell, following PHX-G335 / tip `0064`.

## Alembic

**`0065_purchase_ap_payment_g336`** revising
`0064_purchase_three_way_match_g334`.

## Authorized

Package `noventi.purchase`:

1. `ApBill` status expand: `draft|posted|partially_paid|paid`;
   `POST /v1/purchase/ap-bills/{id}/post` (draft → posted; fail-closed).
2. `ApPayment` shell: create (unallocated) + apply to posted/partially_paid
   bill; payment ≠ clearing until applied; amount ≤ remaining bill balance;
   bill → `partially_paid|paid`; idempotent; HTTP under `/v1/purchase/ap-payments`.
3. Contracts + gateway G336.

Three-way match remains draft-only (post after match). No PSP, GL bridge,
Brain/Twin, bank file import.

## Out

PSP, GL AP bridge (G338), RET credit note (G337), Cap→grant,
Brain/Twin commercial writes, host installs.

## Product Owner response

**Approve — 2026-07-26 batch “AP payment / RET credit note / GL AP bridge”
includes AP payment (G336).**  
Auto-stop only after G338 green unless interrupted.
