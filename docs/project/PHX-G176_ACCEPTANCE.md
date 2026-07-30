# PHX-G176 OpenAPI Platform Status-Code Honesty Acceptance

**日期：** 2026-07-22  
**状态：** Fully Accepted（Foundation）  
**归属：** API Gateway / OpenAPI  
**退出门禁：** IdP/roles 命名 400/404/409/503 已文档化；`full_openapi_http_complete=false`；包 `0.2.1`；Alembic `0029`  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U049**

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0195 + Architecture Gate |
| B | platform OpenAPI 1.0.2 status-code honesty |
| C | Inventory + ops 1.0.6 → PHX-G176 |
| D | tip/status/Manifest/DAL-U049 |
| E | `test_api_gateway_g176_*` |

## 2. Explicit Defer

- Full OpenAPI semantic parity  
- Auth OIDC / Identity status-code remainder  
- Attestation crypto / external PSP / Brain / Twin  

## 3. 证据索引

- [PHX-G176 Architecture Gate](PHX-G176_ARCHITECTURE_GATE.md)  
- [ADR-0195](../decisions/ADR-0195-openapi-platform-status-code-honesty.md)  
