# PHX-G47 OIDC IdP Discovery Architecture Gate

**日期：** 2026-07-19  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform API Gateway / Identity  
**规范源：** ADR-0066  
**人工确认：** 支付清算另批  

## 1. 门禁目标

可选 OpenID Provider Metadata Discovery，填充 authorize/token 端点。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Opt-in | `EAOS_OIDC_DISCOVERY` |
| Override | 显式 endpoint env 优先 |
| Safety | issuer 匹配；HTTPS |
| UI | 无多 IdP 管理面 |

## 3. Exit Criteria

1. ADR-0066 Accepted。  
2. Discovery 填充端点；issuer 不匹配拒绝。  
3. G40 默认（discovery off）仍绿；无 Alembic 变更。  

## 4. 验收

见 [PHX-G47_ACCEPTANCE.md](PHX-G47_ACCEPTANCE.md)；契约 `453 passed`。
