# Coding Authorization Summary — Brain Commercial Handoff (G339)

## Milestone

**PHX-G339** — explicit Brain/Twin → commercial write handoff, following tip `0067`.

## Alembic

**none** — audit via existing `kernel.audit_events`; tip remains until a later
slice bumps it.

## Authorized unique target command

**Only:** `CRMService.create_credit_note_from_return_authorization`
(draft AR Credit Note from restocked RMA). No other commercial writes.

## Authorized

1. Explicit handoff orchestrator + HTTP (not a side effect inside G335
   `request_execution` / `authorize_from_twin`).
2. Flow: Permission-gated Brain execute **or** Twin authorize (exactly one
   source) → separate handoff Permission → call the pinned CRM command with
   `human_confirm=True` → audit intent/result (source id, RMA, CN, idempotency).
3. Tenant fail-closed; idempotent; Z3 advisory still `execution_authority: "none"`.
4. G335 deny codes unchanged when authorize/execute denied; handoff deny has
   stable code; allow path creates draft CN only (no issue/refund/GL).

## Out

Cap→grant (G345); silent writes from G335 methods; SO/DO/AP/GL dispatch;
default `authorize_execution=true`; host installs.

## Product Owner response

**Approve — 2026-07-26 batch “Brain handoff / baseline / finance deepen /
Cap→grant” includes G339.** Auto-continue to G340 after COMPLETE.
