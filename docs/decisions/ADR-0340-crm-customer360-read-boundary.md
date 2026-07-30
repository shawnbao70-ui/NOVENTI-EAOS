# ADR-0340 — CRM Customer360 Read Boundary

**状态：** Accepted（design boundary only）  
**日期：** 2026-07-25  
**里程碑（coding）：** PHX-G313

## Decision

Wave Z / Z1 adds a read-only Customer360 projection under `noventi.crm` with
Permission resource `pkg.crm.customer360`. The gateway exposes
`GET /v1/crm/customers/{customer_id}/360` returning a closed envelope of live-
assembled facts: customer identity and commercial hold, opportunity count, open
sales-order and delivery-order counts, AR invoice status traces, and applied
receipt / credit-note traces from Finance when present.

Z1 uses zero-migration live assembly. Inventory ship postings may close DO/SO
open counts when present. No commercial writes are authorized from this
surface.

## Out

Commission ledger and payout (future Z2); Brain execute / Twin authorize /
capability→grant invent; write APIs that mutate CRM or Finance from 360;
external CDP/marketing sync.

## Consequences

- Contiguous coding milestone PHX-G313 after N1 / PHX-G312.
- Alembic tip remains `0048_finance_ar_credit_note_g312` unless a later wave
  authorizes a projection table.
- TRACK-Z1 COMPLETE ends the F1/I1/N1/Z1 first-slice program; Z2/Z3 require new
  Product Owner text.
