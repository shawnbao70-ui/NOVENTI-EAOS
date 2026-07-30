# Coding Authorization Summary — GL AP Bridges (GL6)

## Milestone

**PHX-G338** — GL bridges for AP bill post + AP payment apply, following PHX-G337.

## Alembic

**`0067_finance_gl_ap_bridges_g338`** revising
`0066_crm_return_credit_note_g337`.

## Authorized

Package `noventi.finance` (GL3 extension):

1. Extend `gl_bridge_maps` with `ap_control` + `ap_expense` (or inventory/expense
   control account); reuse `cash` for payment side.
2. Source types: AP bill post + AP payment apply; open-period + map required;
   idempotent `(source_type, source_id)` + key; posted journal lines:
   - bill post: Dr expense / Cr AP control
   - payment apply: Dr AP control / Cr cash
3. HTTP `POST /v1/finance/gl-bridges/ap-bill-post` and
   `.../ap-payment-apply`; bridge-map PUT/GET accept new fields;
   contracts + gateway G338.

No bank import, FX, Brain/Twin, Cap→grant.

## Out

Bank recon deepen, Cap→grant, Brain commercial auto-writes, host installs.

## Product Owner response

**Approve — 2026-07-26 batch “AP payment / RET credit note / GL AP bridge”
includes GL AP bridge (G338).**  
**TRACK complete after G338 green.**
