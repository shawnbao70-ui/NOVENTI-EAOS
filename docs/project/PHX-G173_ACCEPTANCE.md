# PHX-G173 Marketplace Host-Acquire Status Posture Acceptance

**日期：** 2026-07-22  
**状态：** Fully Accepted（Foundation）  
**归属：** Marketplace Gateway  
**退出门禁：** status 暴露 host_acquire_product；scripts/install/PSP false；包 `0.2.1`；Alembic `0029`  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U046**

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0192 + Architecture Gate |
| B | `host_acquire_product` on marketplace status |
| C | OpenAPI 1.2.3 |
| D | tip/status/Manifest/DAL-U046 |
| E | `test_api_gateway_g173_*` |

## 2. Explicit Defer

- Allowlist expansion beyond first-party  
- Package install auto-wire  

## 3. 证据索引

- [PHX-G173 Architecture Gate](PHX-G173_ARCHITECTURE_GATE.md)  
- [ADR-0192](../decisions/ADR-0192-marketplace-host-acquire-status-posture.md)  
