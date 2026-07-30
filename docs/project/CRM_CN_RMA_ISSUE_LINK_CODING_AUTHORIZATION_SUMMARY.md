# Coding Authorization Summary — CN Issue ↔ RMA Link (G343)

## Milestone

**PHX-G343** — issue Credit Note only when RMA link valid (deepen G337).

## Alembic

Prefer **`0070_crm_cn_rma_issue_link_g343`** if schema needed (e.g. RMA
`credit_note_issued_at`); otherwise **none** and document in SUMMARY.

## Authorized

1. On Finance `issue_credit_note`, validate credit note is linked from a
   restocked RMA (via existing credit_note_id on RMA) for the same invoice
   lineage; reject issue if CN was not created through RMA link when policy
   requires it — **OR** softer: when an RMA link exists, require matching
   invoice_id and optionally stamp RMA issued trace; when no RMA link,
   legacy CN issue still allowed (document which policy you implement —
   prefer: if CN has RMA link, enforce; unlinked CNs still issuable for
   non-RMA paths).
2. human_confirm unchanged; no silent issue on restock; no refund.
3. Contracts + audit.

## Out

Tax credit link (G344), Cap→grant, Brain silent writes.

## Product Owner response

**Approve — batch includes G343.** Auto-continue to G344.
