# PHX-E22 Event Webhook HMAC Architecture Gate

**日期：** 2026-07-19  
**状态：** Fully Accepted  
**归属：** Event Bus  
**规范源：** ADR-0056  

## 1. 门禁目标

为 webhook 投递增加可选 HMAC-SHA256 签名，所有权仍归 Event Bus。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Ownership | Event Bus 签名；Gateway 透传 `signing_secret` |
| Compat | 无 secret → 未签名（E21） |
| Replay | 时间戳头；校验侧默认 5 分钟容差 |

## 3. Exit Criteria

1. ADR-0056 Accepted。  
2. 有 secret 时投递含签名头；校验 helper 通过。  
3. Alembic `0023`；契约全量绿。
