# PHX-G178 OpenAPI Identity/Org Status-Code Honesty Acceptance

**日期：** 2026-07-22  
**状态：** Fully Accepted  
**里程碑：** PHX-G178  
**规范源：** ADR-0197  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U051**

## Acceptance Matrix

| ID | Criterion | Evidence |
|----|-----------|----------|
| A | ADR-0197 + Architecture Gate | ADR-0197；PHX-G178_ARCHITECTURE_GATE |
| B | identity 1.0.3 + organization 1.0.2 status-code honesty | docs/api/*.openapi.yaml |
| C | Inventory + ops 1.0.8 → PHX-G178 | openapi_inventory_product.py；ops.openapi.yaml |
| D | tip/status/Manifest/DAL-U051 | ENG tip；PROJECT_STATUS；Manifest；DAL |
| E | Contracts | `test_api_gateway_g178_*` |

## Explicit Non-Goals

- `full_openapi_http_complete=true`
- HARD HOLD openings
- Package / Alembic bump
- Remap quirk status codes in gateway

## Pointers

- [PHX-G178 Architecture Gate](PHX-G178_ARCHITECTURE_GATE.md)  
- [ADR-0197](../decisions/ADR-0197-openapi-identity-org-status-code-honesty.md)  
