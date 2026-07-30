# Coding Authorization Summary — Finance PSP Live Network (PSP-NET)

## Milestone

**PHX-G331** — PSP live deepen after F3 stub / tip `0061`.

## Alembic

**None**. Tip remains `0061_crm_return_restock_g330`.

## Authorized

Package `noventi.finance`: deepen F3 PSP adapter so that when
`EAOS_PSP_PROVIDER=stripe_like` (or equivalent live provider),
`EAOS_PSP_NETWORK` / `ENABLE_PSP_NETWORK` is ON, **and**
`EAOS_PSP_URL` is configured, `HttpPspAdapter` may perform outbound HTTP
`apply_receipt` calls (timeout, fail-closed on errors); status reports
`live_transport` / `endpoint_configured` honestly; contracts + gateway G331
with **mocked** HTTP only. Default remains OFF → RejectAll / stub.
Optional `EAOS_PSP_BEARER` from env (never logged). Fake provider unchanged.

## Out

Production PSP vendor certification, webhooks product, PAN storage, refund
automation, Brain/Twin, AP3+, auto credit-note. No host package installs.

## Product Owner response

**Approve — 2026-07-26 explicit “PSP live” authorization.**  
Milestone: **PHX-G331**. Auto-stop at TRACK-PSP-NETWORK COMPLETE.
