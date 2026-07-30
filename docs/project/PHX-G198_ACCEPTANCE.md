# PHX-G198 OpenAPI Terminal Extension List Response Parity Acceptance

**日期：** 2026-07-22  
**状态：** Fully Accepted  
**里程碑：** PHX-G198  
**规范源：** ADR-0217  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U071**

## Acceptance Matrix

| ID | Criterion | Evidence |
|----|-----------|----------|
| A | ADR-0217 + Architecture Gate | ADR-0217；PHX-G198_ARCHITECTURE_GATE |
| B | Terminal 1.1.5 list envelope parity | `docs/api/terminal.openapi.yaml` |
| C | Inventory G198 / ops 1.0.24 / tip/status/Manifest/DAL-U071 | inventory；ops；ENG tip；PROJECT_STATUS；Manifest；DAL |
| D | Contracts | `test_api_gateway_g198_*` |

## Explicit Non-Goals

- Arbitrary extension execution
- HARD HOLD openings
- Package / Alembic bump

## Pointers

- [PHX-G198 Architecture Gate](PHX-G198_ARCHITECTURE_GATE.md)  
- [ADR-0217](../decisions/ADR-0217-openapi-terminal-extension-list-response-parity.md)  
