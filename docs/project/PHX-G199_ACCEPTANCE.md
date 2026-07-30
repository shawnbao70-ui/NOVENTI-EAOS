# PHX-G199 OpenAPI Terminal Extension Invoke Response Parity Acceptance

**日期：** 2026-07-22  
**状态：** Fully Accepted  
**里程碑：** PHX-G199  
**规范源：** ADR-0218  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U072**

## Acceptance Matrix

| ID | Criterion | Evidence |
|----|-----------|----------|
| A | ADR-0218 + Architecture Gate | ADR-0218；PHX-G199_ARCHITECTURE_GATE |
| B | Terminal 1.1.6 invoke envelope parity | `docs/api/terminal.openapi.yaml` |
| C | Inventory G199 / ops 1.0.25 / tip/status/Manifest/DAL-U072 | inventory；ops；ENG tip；PROJECT_STATUS；Manifest；DAL |
| D | Contracts | `test_api_gateway_g199_*` |

## Explicit Non-Goals

- Arbitrary extension execution
- HARD HOLD openings
- Package / Alembic bump

## Pointers

- [PHX-G199 Architecture Gate](PHX-G199_ARCHITECTURE_GATE.md)  
- [ADR-0218](../decisions/ADR-0218-openapi-terminal-extension-invoke-response-parity.md)  
