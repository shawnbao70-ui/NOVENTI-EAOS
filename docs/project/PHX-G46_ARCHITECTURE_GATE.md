# PHX-G46 JWT Denylist Architecture Gate

**日期：** 2026-07-19  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform API Gateway / Identity  
**规范源：** ADR-0065  
**人工确认：** 支付清算另批  

## 1. 门禁目标

Foundation denylist：按 `jti`（可选 `iss`）拒绝已吊销 Bearer JWT。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Boundary | Gateway 认证边界 |
| Source | JSON env 和/或 HTTPS URL |
| Match | jti；可选 iss 限定 |
| Fail | `GATEWAY_JWT_REVOKED` |

## 3. Exit Criteria

1. ADR-0065 Accepted。  
2. 命中 denylist → 401；未配置时行为不变。  
3. G37/G45 回归绿；无 Alembic 变更。
