# Coding Authorization Summary — Remediation P0-1 Tip Helper (G406)

## Milestone

**PHX-G406** — authoritative contract tip helper; eliminate `0049` as current-head claim.

## Alembic

**none** — tip remains `0092_finance_realized_fx_gl_bridge_g372`.

## Authorized

1. Declare REPAIR FREEZE on roadmap（Slice 0；docs only）.
2. Create `tests/contracts/_baseline.py` sourced from Alembic + RELEASE_MANIFEST.
3. Replace copied `get_current_head() == "0049_…"` current-head literals（~113）.
   Historical tests may assert revision exists / ancestry; must not claim current head.
4. Fix G193 tip contradiction；keep tip-match + g405 hygiene green.
5. No package bump；no feature work；no DAL fabrication；no historical ADR tip rewrite spam.

## Out

Docker noventi（G407）；CI shards（G408）；Helm parity（G409）；governance boards（G411）；
PSP / ENABLE_*_NETWORK ON；host OS installs；Brain/Twin invent.

## Product Owner response

**Approve — Remediation Wave A serial instructions pasted 2026-07-27；Milestone PHX-G406；STOP after TRACK-G406（no auto-continue G407 unless separate Approve）。**
