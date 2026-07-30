# Coding Authorization Summary — Finance PSP Provider Adapter (F3)

## Milestone

**PHX-G326** — F3, following PHX-G325 / RET1 (tip `0059`).

## Alembic

**None** (env-gated adapter skeleton, Tax3 pattern). Tip remains
`0059_crm_return_authorization_g325`.

## Authorized

Package `noventi.finance`: PSP provider adapter deepen on existing `PspPort` —
`EAOS_PSP_PROVIDER` (`off|fake|stripe_like`, default `off`), network gate
`EAOS_PSP_NETWORK` / `ENABLE_PSP_NETWORK` default OFF, `StripeLikePspAdapter`
stub with **no live I/O** even when flag ON without secrets, `resolve_psp_port()`
wired into TransactionalFinanceService, read-only
`GET /v1/finance/adapters/psp` status, contracts + gateway G326 tests.
F2 policy + Fake injection remain unchanged.

## Out

Real HTTPS PSP calls, live webhooks, payout/refund automation, PAN storage,
production keys, GL, Brain/Twin, RET2, AP2+.

## Product Owner response

**Approve — 2026-07-26 explicit “F3（PSP deepen）” authorization.**  
Milestone: **PHX-G326**. Auto-stop at TRACK-F3 COMPLETE; PSP network stays OFF.
