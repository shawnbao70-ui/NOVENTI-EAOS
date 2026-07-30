# PHX-G171 Terminal UuidResult Client Harden Acceptance

**日期：** 2026-07-22  
**状态：** Fully Accepted（Foundation）  
**归属：** Smart Terminal UI  
**退出门禁：** `uuidFromResult` 覆盖创建路径；包 `0.2.1`；Alembic `0029`  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U044**

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0190 + Architecture Gate |
| B | `uuidFromResult` + create-path wiring |
| C | tip/status/Manifest/DAL-U044 |
| D | `test_api_gateway_g171_*` |

## 2. 核心不变量

- 不打开 HARD HOLDS  
- 不执行 Marketplace 任意脚本  

## 3. 自动化证据

- `tests/contracts/test_api_gateway_g171_terminal_uuid_client.py`

## 4. Explicit Defer

- Marketplace listing→host acquire  

## 5. 证据索引

- [PHX-G171 Architecture Gate](PHX-G171_ARCHITECTURE_GATE.md)  
- [ADR-0190](../decisions/ADR-0190-terminal-uuid-result-client-harden.md)  
