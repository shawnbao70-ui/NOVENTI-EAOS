# PHX-G182 Terminal Extensions Host-Path Readiness Acceptance

**日期：** 2026-07-22  
**状态：** Fully Accepted  
**里程碑：** PHX-G182  
**规范源：** ADR-0201  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U055**

## Acceptance Matrix

| ID | Criterion | Evidence |
|----|-----------|----------|
| A | ADR-0201 + Architecture Gate | ADR-0201；PHX-G182_ARCHITECTURE_GATE |
| B | Extensions readiness + Acquire→Host + host_actions | `smart_terminal/ui/index.html`；`app.js` |
| C | Demo bootstrap milestone PHX-G182 | `demo_bootstrap.py` |
| D | tip/status/Manifest/DAL-U055 | ENG tip；PROJECT_STATUS；Manifest；DAL |
| E | Contracts | `test_api_gateway_g182_*` |

## Explicit Non-Goals

- Expanding host-acquire allowlist
- HARD HOLD openings / package install / external PSP
- Package / Alembic bump

## Pointers

- [PHX-G182 Architecture Gate](PHX-G182_ARCHITECTURE_GATE.md)  
- [ADR-0201](../decisions/ADR-0201-terminal-extensions-host-path-readiness.md)  
