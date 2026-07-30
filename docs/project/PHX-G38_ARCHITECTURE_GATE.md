# PHX-G38 JWT JWKS / RS256 Architecture Gate

**日期：** 2026-07-19  
**状态：** Fully Accepted  
**归属：** Platform API Gateway / Identity  
**人工批准：** 承接 G37 已批准 OIDC 产品化；JWKS/RS256 为本刀  
**规范源：** ADR-0055  

## 1. 门禁目标

在 Gateway 支持 RS256 + JWKS 密钥选择/轮换，与 HS256 并列。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Alg | HS256 与 RS256 |
| JWKS | JSON 内联优先；HTTPS URL 可选缓存 |
| Elevation | 仍拒租户面 platform claim |
| Login UI | 显式延后 |

## 3. Exit Criteria

1. ADR-0055 Accepted。  
2. RS256 Bearer 可派生上下文；错误 `kid`/签名拒绝。  
3. HS256 回归仍绿。  
4. 契约全量绿。
