# PHX-G189 OpenAPI IdP Status Body Field Parity Acceptance

**日期：** 2026-07-22  
**状态：** Fully Accepted  
**里程碑：** PHX-G189  
**规范源：** ADR-0208  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U062**

## Acceptance Matrix

| ID | Criterion | Evidence |
|----|-----------|----------|
| A | ADR-0208 + Architecture Gate | ADR-0208；PHX-G189_ARCHITECTURE_GATE |
| B | auth 1.3.12 IdpStatus schemas | docs/api/auth.openapi.yaml |
| C | Inventory + ops 1.0.16 → PHX-G189 | openapi_inventory_product.py；ops.openapi.yaml |
| D | tip/status/Manifest/DAL-U062 | ENG tip；PROJECT_STATUS；Manifest；DAL |
| E | Contracts | `test_api_gateway_g189_*` |

## Explicit Non-Goals

- Full nested OIDC status schema
- `full_openapi_http_complete=true`
- Package / Alembic bump

## Pointers

- [PHX-G189 Architecture Gate](PHX-G189_ARCHITECTURE_GATE.md)  
- [ADR-0208](../decisions/ADR-0208-openapi-idp-status-body-field-parity.md)  
