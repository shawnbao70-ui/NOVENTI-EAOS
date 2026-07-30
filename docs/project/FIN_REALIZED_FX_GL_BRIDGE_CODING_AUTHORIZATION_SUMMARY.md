# Coding Authorization Summary — Realized FX → GL Bridge (G372)

## Milestone

**PHX-G372** — post G359 realized FX events to GL via fx_gain/fx_loss.

## Alembic

**`0092_finance_realized_fx_gl_bridge_g372`** revising `0091_…`
(extend GlBridgeSourceType / postings if needed).

## Authorized

1. `bridge_realized_fx_event` (or allocation bridge): open period, map must
   have fx_gain/fx_loss; idempotent source_type+source_id; journal Dr/Cr
   gain or loss vs contra (document: e.g. Dr cash/AR clearing vs fx — prefer
   simple: gain credit fx_gain debit ar_control or a realized_fx_clearing —
   use existing ar_control + fx_gain/fx_loss paired lines).
2. HTTP POST `/v1/finance/gl-bridges/realized-fx`
3. Contracts; zero-amount events skipped/rejected.

## Out

Release train (G373), DE thin, baseline.

## Product Owner response

**Approve — batch; auto-continue G373.**
