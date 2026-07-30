# PHX-G168 Demo Signed Extension Seed Architecture Gate

**日期：** 2026-07-22  
**状态：** Fully Accepted（Foundation）  
**归属：** Demo Gateway / Smart Terminal Extensions  
**规范源：** ADR-0187  
**授权：** DAL-G003 + DAL-G004（DAL-U041）

## 1. 门禁目标

在 demo 双轨预置 HMAC 签名并已激活的首方扩展，使 Extensions 面可一键联调，同时生产网关保持无 demo bootstrap / 无 demo HMAC。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Signing | Demo-only HMAC required |
| Extension | `noventi.demo.panel` pre-registered + activated |
| Bootstrap | Optional `extension_id` fields；no secret |
| Production | Not mounted；no demo HMAC in `create_app()` |
| Package / Alembic | `0.2.1` / `0029` |
| Out | Marketplace arbitrary script；HARD HOLDS |

## 3. Exit Criteria

1. ADR-0187 Accepted。  
2. Demo seed + bootstrap fields + Terminal autofill + tests + DAL-U041 + tip/status 齐。  
3. `test_api_gateway_g168_*` 绿。  
