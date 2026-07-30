# Coding Authorization Summary — Baseline / Release Hygiene (G340)

## Milestone

**PHX-G340** — tip/roadmap/manifest/acceptance alignment after G339.

## Alembic

**none**

## Authorized

Align tip statements across POST_CRM_VERTICAL_ROADMAP, recent SUMMARYs,
Coding Auths/ADRs (no blind historical tip rewrites), and any
`manifest.proposed` / gate packs that still say tip `0064` or empty-queue
after G338 incorrectly. Add a small contract test that roadmap verified tip
matches Alembic ScriptDirectory head. No business CRUD.

## Out

Finance/CRM writes, Cap→grant, host installs, Alembic.

## Product Owner response

**Approve — batch includes G340.** Auto-continue to G341 after COMPLETE.
