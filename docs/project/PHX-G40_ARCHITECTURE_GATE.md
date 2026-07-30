# PHX-G40 OIDC Authorization Code Login Architecture Gate

**日期：** 2026-07-19  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform API Gateway / Identity  
**人工批准：** 承接已批准 JWT/OIDC 产品化  
**规范源：** ADR-0058  

## 1. 门禁目标

以 Authorization Code + PKCE 完成 IdP 登录并签发 EAOS Bearer JWT。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Boundary | Gateway 认证边界；Kernel 不解析 IdP 协议 |
| PKCE | S256 必选 |
| Token | 回调后签发 EAOS HS256（需 `EAOS_JWT_SECRET`） |
| UI | Terminal 可存 Bearer；开发头并存 |

## 3. Exit Criteria

1. ADR-0058 Accepted。  
2. login → callback → EAOS JWT 契约通过。  
3. 未配置时 503；伪造 state 拒绝。  
4. 全量 contracts 绿。
