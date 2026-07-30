# PHX-G217 Terminal OpenAPI Inventory Error Details Description-Key Status Deepen Acceptance

**日期：** 2026-07-22  
**状态：** Fully Accepted  
**里程碑：** PHX-G217  
**规范源：** ADR-0236  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U090**

## Acceptance Matrix

| ID | Criterion | Evidence |
|----|-----------|----------|
| A | ADR-0236 + Architecture Gate | ADR-0236；PHX-G217_ARCHITECTURE_GATE |
| B | Admin CTA + strip description-key marker + quiet refresh | `smart_terminal/ui/*` |
| C | tip/status/Manifest/DAL-U090 | ENG tip；PROJECT_STATUS；Manifest；DAL |
| D | Contracts | `test_api_gateway_g217_*` |

## Explicit Non-Goals

- Inventory / ops bump
- Package / Alembic bump

## Pointers

- [PHX-G217 Architecture Gate](PHX-G217_ARCHITECTURE_GATE.md)  
- [ADR-0236](../decisions/ADR-0236-terminal-openapi-inventory-error-details-description-key-status-deepen.md)  
