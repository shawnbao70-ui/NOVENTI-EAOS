# PHX-G345 Cap→grant Summary

**Status:** TRACK-CAP-GRANT COMPLETE / TRACK-G345 COMPLETE  
**Alembic:** none — verified tip remains `0071_finance_tax_credit_link_g344`.

## Delivered

- Added the explicit, grant-administrator-only `/v1/permission/cap-grants`
  create/list/revoke shell.
- A capability is retained as audit evidence (`Permission.CapGrant.Create` /
  `Permission.CapGrant.Revoke`); it is not a role, global superuser, or new
  permission store. The shell mints and revokes normal Kernel `Grant` records.
- The request schema is fixed to tenant scope. Enterprise, platform, resource,
  and cross-tenant variants are rejected.
- The shell does not invoke Brain, Twin, CRM, Finance, or commercial handoff
  services. G339 still requires its explicit handoff endpoint and
  `human_confirm` after Brain/Twin authorization.

## Evidence

- Coding authorization:
  `docs/project/CAP_GRANT_CODING_AUTHORIZATION_SUMMARY.md`
- Boundary: `docs/decisions/ADR-0377-cap-grant-boundary.md`
- Contract test: `tests/contracts/test_api_gateway_g345_cap_grant.py`
