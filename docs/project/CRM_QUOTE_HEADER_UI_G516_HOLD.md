# PHX-G516 HOLD RESOLVED — Quote Header Managed UI

> **System-generated governance evidence** under ADR-0321.

## Status

- Architecture Gate Accepted: **Yes**
- Coding Authorization: **Consumed by PHX-G516**
- Milestone: **PHX-G516 COMPLETE**
- Queue: **RESOLVED**
- PHX-G517–G521: **Closed**

## Blocking evidence

Quote Header currently has create/detail/update/archive plus separately scoped
Issue/Convert and nested Quote Line routes. It has no Quote Header collection
route, list DTO, or cursor-paginated Service/Repository contract.

Nested Quote Line listing cannot serve as a Quote Header collection.

## Disposition

Resolved through the accepted list-query Gate and PHX-G516 Coding
Authorization. No authority extends to G517+.

## Evidence

- [Quote Header UI Gate](CRM_QUOTE_HEADER_MANAGED_UI_ARCHITECTURE_GATE.md)
- `api/gateway/routers/crm.py`
- `api/gateway/schemas/crm.py`
- `noventi/crm/service.py`
- `noventi/crm/repository.py`
- [PHX-G516 Acceptance](CRM_QUOTE_HEADER_UI_G516_ACCEPTANCE.md)
