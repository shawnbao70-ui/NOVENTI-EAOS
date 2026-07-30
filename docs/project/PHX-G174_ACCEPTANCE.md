# PHX-G174 OpenAPI Auth/Marketplace/Platform Detail Align Acceptance

**日期：** 2026-07-22  
**状态：** Fully Accepted（Foundation）  
**归属：** API Gateway / OpenAPI  
**退出门禁：** 三域 KernelError→GatewayDetailError；`full_openapi_http_complete=false`；包 `0.2.1`；Alembic `0029`  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U047**

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0193 + Architecture Gate |
| B | auth 1.3.7 / platform 1.0.1 / marketplace 1.2.4 detail align |
| C | Inventory + ops 1.0.5 → PHX-G174 |
| D | tip/status/Manifest/DAL-U047 |
| E | `test_api_gateway_g174_*` |

## 2. Explicit Defer

- Full OpenAPI semantic parity  
- Attestation crypto / external PSP / Brain / Twin  

## 3. 证据索引

- [PHX-G174 Architecture Gate](PHX-G174_ARCHITECTURE_GATE.md)  
- [ADR-0193](../decisions/ADR-0193-openapi-auth-marketplace-platform-detail.md)  
