# PHX-G175 Terminal Host-Acquire Status Surface Acceptance

**日期：** 2026-07-22  
**状态：** Fully Accepted（Foundation）  
**归属：** Smart Terminal Admin  
**退出门禁：** Admin 摘要暴露 scripts/install/PSP false；包 `0.2.1`；Alembic `0029`  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U048**

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0194 + Architecture Gate |
| B | `loadHostAcquireStatus` + Admin CTA/status line |
| C | Boot + post host-acquire refresh |
| D | tip/status/Manifest/DAL-U048 |
| E | `test_api_gateway_g175_*` |

## 2. Explicit Defer

- Non-allowlist catalog UI  
- Package install auto-wire  

## 3. 证据索引

- [PHX-G175 Architecture Gate](PHX-G175_ARCHITECTURE_GATE.md)  
- [ADR-0194](../decisions/ADR-0194-terminal-host-acquire-status-surface.md)  
