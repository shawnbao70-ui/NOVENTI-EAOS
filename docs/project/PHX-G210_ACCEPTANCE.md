# PHX-G210 OpenAPI OIDC Details Per-Code Shapes Honesty Acceptance

**日期：** 2026-07-22  
**状态：** Fully Accepted  
**里程碑：** PHX-G210  
**规范源：** ADR-0229  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U083**

## Acceptance Matrix

| ID | Criterion | Evidence |
|----|-----------|----------|
| A | ADR-0229 + Architecture Gate | ADR-0229；PHX-G210_ARCHITECTURE_GATE |
| B | Four Oidc*Details schemas + details keys | auth.openapi.yaml |
| C | Inventory G210 / ops 1.0.31 | openapi_inventory_product；ops.openapi |
| D | tip/status/Manifest/DAL-U083 | ENG tip；PROJECT_STATUS；Manifest；DAL |
| E | Contracts | `test_api_gateway_g210_*` |

## Explicit Non-Goals

- Exhaustive per-code details map
- Semantic-complete claim
- Package / Alembic bump

## Pointers

- [PHX-G210 Architecture Gate](PHX-G210_ARCHITECTURE_GATE.md)  
- [ADR-0229](../decisions/ADR-0229-openapi-oidc-details-code-shapes-honesty.md)  
