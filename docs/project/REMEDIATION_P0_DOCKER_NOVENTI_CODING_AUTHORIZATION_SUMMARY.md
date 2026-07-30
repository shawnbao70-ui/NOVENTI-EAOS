# Coding Authorization Summary — Remediation P0-3 Docker noventi (G407)

## Milestone

**PHX-G407** — include `noventi/` in gateway image; import smoke.

## Alembic

**none** — tip remains `0092_finance_realized_fx_gl_bridge_g372`.

## Authorized

1. `deploy/docker/Dockerfile`: `COPY noventi ./noventi` (+ smoke script path).
2. Image/layout smoke importing `api.gateway.app`, `noventi.crm`, `noventi.finance`
   （plus purchase/inventory if trivial）.
3. Docs: packaging only ≠ host OS install ≠ Marketplace/Industry host-install runtime.
4. No package bump；no ENABLE_*_NETWORK ON；no PSP invent；no bank-file import.

## Out

P0-2 PR shards（G408）；Helm parity（G409）；CI lock（G410）；governance boards（G411）.

## Product Owner response

**Approve — Milestone PHX-G407（2026-07-27）。STOP after TRACK-G407。**
