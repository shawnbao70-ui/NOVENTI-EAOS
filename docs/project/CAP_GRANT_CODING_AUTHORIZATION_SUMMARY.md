# Coding Authorization Summary — Cap→grant Narrow Shell (G345)

## Milestone

**PHX-G345** — explicit Cap→grant command shell (batch-approved).

## Alembic

**none** — reuse existing Permission `Grant` persistence; tip stays at G344 head
unless a dedicated cap ledger is required (prefer none).

## Authorized

1. Explicit Cap→grant HTTP shell over Kernel Permission grant/revoke/list:
   principal + capability/resource_type + actions + tenant scope; audited;
   default-deny evaluation unchanged.
2. Grant administrators only; no Legacy Admin bypass; no cross-tenant grants.
3. Revoke / list for tenant-scoped grants; idempotent where applicable.
4. Contracts: deny/allow/revoke/tenant isolation.
5. Hard rule: Cap→grant MUST NOT auto-execute commercial writes; MUST NOT let
   Brain/Twin bypass G339 handoff (granting `pkg.platform.commercial_handoff`
   still requires the explicit handoff HTTP + human_confirm + authorize).

## Out

Global superuser; cross-tenant; silent expansion of G335/G339 write surface;
host installs; Brain calling grant as side effect of execute.

## Product Owner response

**Approve — batch includes G345.** FINAL STOP at TRACK-G345 COMPLETE.
