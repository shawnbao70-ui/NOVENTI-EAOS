# Coding Authorization Summary — RET → Credit Note Link (RET3)

## Milestone

**PHX-G337** — controlled RMA/restock → AR Credit Note link, following PHX-G336.

## Alembic

**`0066_crm_return_credit_note_g337`** revising
`0065_purchase_ap_payment_g336`.

## Authorized

Package `noventi.crm` (+ Finance credit-note create via existing port/service):

1. Explicit command to create AR Credit Note from a **restocked** Return
   Authorization that already has `invoice_id` (not silent on restock).
2. Persist link: RMA ↔ credit note (idempotent per RMA); amount ≤ invoice total;
   reuse Finance `ARCreditNote` create semantics (draft); issue remains separate
   human-confirm Finance path.
3. HTTP `POST /v1/crm/return-authorizations/{id}/credit-notes` (+ GET link);
   contracts + gateway G337.

No auto-issue, no refund payout, no GL, no Brain/Twin.

## Out

Silent auto-CN on restock, refund/Treasury, tax void coupling, GL, Cap→grant,
Brain/Twin commercial writes, host installs.

## Product Owner response

**Approve — 2026-07-26 batch “AP payment / RET credit note / GL AP bridge”
includes RET credit note (G337).**
