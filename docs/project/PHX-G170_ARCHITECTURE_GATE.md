# PHX-G170 UuidResult Dialect Unification Architecture Gate

**日期：** 2026-07-22  
**状态：** Fully Accepted（Foundation）  
**归属：** API Gateway / OpenAPI  
**规范源：** ADR-0189  
**授权：** DAL-G003 + DAL-G004（DAL-U043）

## 1. 门禁目标

以双键兼容方式统一 UuidResult，关闭 `uuid_result_dialect_unification` fence，且不破坏既有客户端。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Wire | `{id, data}` same UUID（+ optional `ok` / `audit_id`） |
| Contract | OpenAPI UuidResult required includes both keys |
| Inventory | PHX-G170；uuid fence removed |
| full_openapi_http_complete | false |
| Package / Alembic | `0.2.1` / `0029` |

## 3. Exit Criteria

1. ADR-0189 Accepted。  
2. common serializer + OpenAPI + inventory + tests + DAL-U043 齐。  
3. `test_api_gateway_g170_*` 绿。  
