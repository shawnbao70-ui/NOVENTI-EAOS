# PHX-G183 Terminal Payment-Clearing Status Surface Acceptance

**日期：** 2026-07-22  
**状态：** Fully Accepted  
**里程碑：** PHX-G183  
**规范源：** ADR-0202  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U056**

## Acceptance Matrix

| ID | Criterion | Evidence |
|----|-----------|----------|
| A | ADR-0202 + Architecture Gate | ADR-0202；PHX-G183_ARCHITECTURE_GATE |
| B | Admin CTA + status line for payment_clearing_product | `smart_terminal/ui/*` |
| C | tip/status/Manifest/DAL-U056 | ENG tip；PROJECT_STATUS；Manifest；DAL |
| D | Contracts | `test_api_gateway_g183_*` |

## Explicit Non-Goals

- Opening external PSP
- Always-on payment clearing
- Package / Alembic bump

## Pointers

- [PHX-G183 Architecture Gate](PHX-G183_ARCHITECTURE_GATE.md)  
- [ADR-0202](../decisions/ADR-0202-terminal-payment-clearing-status-surface.md)  
