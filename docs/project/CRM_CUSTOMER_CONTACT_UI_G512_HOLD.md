# PHX-G512 — CRM Customer + Contact Read-only UI Shell HOLD (RESOLVED)

**Status:** RESOLVED — historical HOLD evidence  
**Date:** 2026-07-28  
**Coding Authorization:** Approved for PHX-G512 only  
**Production Authorization:** None

## Authorized slice

[CRM_CUSTOMER_CONTACT_UI_CODING_AUTHORIZATION_SUMMARY.md](CRM_CUSTOMER_CONTACT_UI_CODING_AUTHORIZATION_SUMMARY.md)
authorizes the Customer/Contact read-only UI shell without backend expansion.

## Verified blocker

The existing CRM Gateway exposes:

- `GET /v1/crm/customers/{customer_id}`
- `GET /v1/crm/customers/{customer_id}/contacts/{contact_id}`

It does not expose:

- a tenant-scoped Customer list query;
- a Customer-scoped Contact list query; or
- list response DTOs for either resource.

Evidence:

- `api/gateway/routers/crm.py`
- `api/gateway/schemas/crm.py`
- `tests/contracts/test_api_gateway_g294_crm_c1.py`

## Fail-closed disposition

PHX-G512 does not:

- fabricate Customer or Contact fixture data as business truth;
- scrape or infer lists from unrelated APIs;
- add API, service, repository, database, or Alembic behavior;
- weaken tenant or Permission controls; or
- claim UI completion.

At the time of this HOLD, the milestone remained the only active serial
milestone and was not Complete. The minimal list-query Product Gate was
Accepted:
[CRM_CUSTOMER_CONTACT_LIST_QUERY_ACCEPTANCE.md](CRM_CUSTOMER_CONTACT_LIST_QUERY_ACCEPTANCE.md).
Independent Coding Authorization is still required before G512 may resume.

## State at HOLD time

- Architecture Gate Accepted: **Yes — UI design boundary only**
- Coding Authorization: **Approved — PHX-G512 only**
- Implementation: **HOLD before frontend change**
- Runtime Manifest: **unchanged**
- Production: **NO-GO remains unchanged**

## Resolution

The separately approved list-query prerequisite and read-only UI were
implemented and verified under the same PHX-G512 milestone. See
[CRM_CUSTOMER_CONTACT_UI_G512_ACCEPTANCE.md](CRM_CUSTOMER_CONTACT_UI_G512_ACCEPTANCE.md).

- Implementation: **COMPLETE**
- HOLD disposition: **Resolved 2026-07-28**
- Production: **NO-GO remains unchanged**
