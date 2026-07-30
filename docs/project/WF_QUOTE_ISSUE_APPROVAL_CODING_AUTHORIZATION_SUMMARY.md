# Coding Authorization Summary — Workflow Approval Wiring Quote.issue (G348)

## Milestone

**PHX-G348** — ADR-0318 wiring; **unique command: Quote.issue only**.

## Alembic

Prefer **`0073_crm_quote_issue_approval_g348`** if tenant policy / link table
needed; else **none** and document.

## Authorized

1. Tenant-configurable policy: when enabled, `issue_quote` requires an approved
   Workflow instance bound to that quote (`verify_approved_action` or equivalent)
   before issue succeeds (still needs human_confirm + Permission).
2. Explicit submit/start Workflow for quote-issue action; approve/reject via
   existing Workflow HTTP; approval ≠ auto-issue.
3. When policy disabled, existing issue_quote path unchanged.
4. Contracts: policy on → issue denied without approval; after approve → issue OK;
   approve alone does not issue.

## Out

Convert/Ship wiring, fulfillment (G349), FX, Cap widen, Brain silent writes.

## Product Owner response

**Approve — G348=Quote.issue.** Auto-continue G349.
