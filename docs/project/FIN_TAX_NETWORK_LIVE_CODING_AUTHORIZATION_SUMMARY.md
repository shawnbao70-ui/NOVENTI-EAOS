# Coding Authorization Summary — Finance Tax Authority Live Network (Tax-NET)

## Milestone

**PHX-G328** — live tax network deepen after Tax3 stub / tip `0059`.

## Alembic

**None** (env-configured transport). Tip remains
`0059_crm_return_authorization_g325`.

## Authorized

Package `noventi.finance`: deepen Tax3 adapter so that when
`EAOS_TAX_NETWORK` / `ENABLE_TAX_NETWORK` is ON **and**
`EAOS_TAX_AUTHORITY_URL` is configured, `HttpTaxAuthorityAdapter` may perform
**outbound HTTP** validate-rate calls (timeout, fail-closed on non-2xx / errors);
status surface reports `live_transport` honestly; contracts + gateway G328 with
**mocked** HTTP only (no real tax authority in CI). Default remains OFF →
RejectAll. Optional `EAOS_TAX_AUTHORITY_BEARER` from env (never logged).

## Out

- `ENABLE_PSP_NETWORK` / live PSP HTTPS (remains PARKED)
- Production tax-authority vendor certification, e-invoice filing product UI
- Storing PAN/secrets in repo; Brain/Twin; AP2/RET2

## Product Owner response

**Approve — 2026-07-26 explicit “ENABLE_*_NETWORK / live tax” authorization
scoped to tax network only.**  
Milestone: **PHX-G328**. Auto-stop at TRACK-TAX-NETWORK COMPLETE.
PSP live transport remains OFF / PARKED.
