# PHX-G188 OpenAPI JWT Status Body Field Parity Acceptance

**日期：** 2026-07-22  
**状态：** Fully Accepted  
**里程碑：** PHX-G188  
**规范源：** ADR-0207  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U061**

## Acceptance Matrix

| ID | Criterion | Evidence |
|----|-----------|----------|
| A | ADR-0207 + Architecture Gate | ADR-0207；PHX-G188_ARCHITECTURE_GATE |
| B | auth 1.3.11 JwtStatus schemas | docs/api/auth.openapi.yaml |
| C | Inventory + ops 1.0.15 → PHX-G188 | openapi_inventory_product.py；ops.openapi.yaml |
| D | tip/status/Manifest/DAL-U061 | ENG tip；PROJECT_STATUS；Manifest；DAL |
| E | Contracts | `test_api_gateway_g188_*` |

## Explicit Non-Goals

- `full_openapi_http_complete=true`
- IdP status full nested schema
- Package / Alembic bump

## Pointers

- [PHX-G188 Architecture Gate](PHX-G188_ARCHITECTURE_GATE.md)  
- [ADR-0207](../decisions/ADR-0207-openapi-jwt-status-body-field-parity.md)  
