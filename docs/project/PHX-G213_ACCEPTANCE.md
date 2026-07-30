# PHX-G213 Terminal OpenAPI Inventory Host-Acquire Details Status Deepen Acceptance

**日期：** 2026-07-22  
**状态：** Fully Accepted  
**里程碑：** PHX-G213  
**规范源：** ADR-0232  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U086**

## Acceptance Matrix

| ID | Criterion | Evidence |
|----|-----------|----------|
| A | ADR-0232 + Architecture Gate | ADR-0232；PHX-G213_ARCHITECTURE_GATE |
| B | Admin CTA + strip host-acquire marker + quiet refresh | `smart_terminal/ui/*` |
| C | tip/status/Manifest/DAL-U086 | ENG tip；PROJECT_STATUS；Manifest；DAL |
| D | Contracts | `test_api_gateway_g213_*` |

## Explicit Non-Goals

- Inventory / ops bump
- Non-allowlist catalog
- Package / Alembic bump

## Pointers

- [PHX-G213 Architecture Gate](PHX-G213_ARCHITECTURE_GATE.md)  
- [ADR-0232](../decisions/ADR-0232-terminal-openapi-inventory-host-acquire-status-deepen.md)  
