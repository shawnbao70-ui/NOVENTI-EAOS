# PHX-G212 OpenAPI Host-Acquire Details Per-Code Shape Honesty Acceptance

**日期：** 2026-07-22  
**状态：** Fully Accepted  
**里程碑：** PHX-G212  
**规范源：** ADR-0231  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U085**

## Acceptance Matrix

| ID | Criterion | Evidence |
|----|-----------|----------|
| A | ADR-0231 + Architecture Gate | ADR-0231；PHX-G212_ARCHITECTURE_GATE |
| B | HostAcquireAllowlistDenialDetails + details.package_key | marketplace.openapi.yaml |
| C | Inventory G212 / ops 1.0.32 | openapi_inventory_product；ops.openapi |
| D | tip/status/Manifest/DAL-U085 | ENG tip；PROJECT_STATUS；Manifest；DAL |
| E | Contracts | `test_api_gateway_g212_*` |

## Explicit Non-Goals

- Non-allowlist catalog deepen
- Semantic-complete claim
- Package / Alembic bump

## Pointers

- [PHX-G212 Architecture Gate](PHX-G212_ARCHITECTURE_GATE.md)  
- [ADR-0231](../decisions/ADR-0231-openapi-host-acquire-details-code-shape-honesty.md)  
