# PHX-G190 OpenAPI OIDC Status Body Field Parity Acceptance

**日期：** 2026-07-22  
**状态：** Fully Accepted  
**里程碑：** PHX-G190  
**规范源：** ADR-0209  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U063**

## Acceptance Matrix

| ID | Criterion | Evidence |
|----|-----------|----------|
| A | ADR-0209 + Architecture Gate | ADR-0209；PHX-G190_ARCHITECTURE_GATE |
| B | auth 1.3.13 OidcStatus schemas + IdP.oidc ref | docs/api/auth.openapi.yaml |
| C | Inventory + ops 1.0.17 → PHX-G190 | openapi_inventory_product.py；ops.openapi.yaml |
| D | tip/status/Manifest/DAL-U063 | ENG tip；PROJECT_STATUS；Manifest；DAL |
| E | Contracts | `test_api_gateway_g190_*` |

## Explicit Non-Goals

- `full_openapi_http_complete=true`
- HARD HOLD openings
- Package / Alembic bump

## Pointers

- [PHX-G190 Architecture Gate](PHX-G190_ARCHITECTURE_GATE.md)  
- [ADR-0209](../decisions/ADR-0209-openapi-oidc-status-body-field-parity.md)  
