# PHX-G210 OpenAPI OIDC Details Per-Code Shapes Honesty Architecture Gate

**日期：** 2026-07-22  
**状态：** Fully Accepted（Foundation）  
**归属：** OpenAPI Inventory / Auth  
**规范源：** ADR-0229  
**授权：** DAL-G003 + DAL-G004（DAL-U083）

## 1. 门禁目标

为 OIDC claim/role/amr/acr denial 码闭合已知 details 形状，不伪称全码穷尽。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Schema | Oidc*Details（auth）+ ErrorResponse.details keys |
| Inventory | G210 / ops 1.0.31 |
| Package / Alembic | `0.2.1` / `0029` |

## 3. Exit Criteria

ADR-0229 + auth schemas + inventory + tests + DAL-U083 + tip/status 齐。  
