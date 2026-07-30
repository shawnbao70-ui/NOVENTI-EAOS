# PHX-G167 Demo Bootstrap Context Architecture Gate

**日期：** 2026-07-22  
**状态：** Fully Accepted（Foundation）  
**归属：** Demo Gateway / Smart Terminal  
**规范源：** ADR-0186  
**授权：** DAL-G003 + DAL-G004（DAL-U040）

## 1. 门禁目标

提供 demo-only bootstrap 上下文以加速 Terminal 联调，且生产 fail-closed 网关保持无该路由。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Route | `GET /v1/demo/bootstrap` demo-only |
| Production | Not mounted on `api.gateway.app` |
| Secrets | Never returned |
| Package / Alembic | `0.2.1` / `0029` |
| Out | HARD HOLDS；production demo surface |

## 3. Exit Criteria

1. ADR-0186 Accepted。  
2. demo mount + Terminal probe + tests + DAL-U040 + tip/status 齐。  
3. `test_api_gateway_g167_*` 绿。  
