# PHX-G37 JWT/OIDC Trusted Context Architecture Gate

**日期：** 2026-07-19  
**状态：** Fully Accepted（HS256 基础面）  
**归属：** Platform API Gateway / Identity  
**人工批准：** 2026-07-18 用户指示启动 JWT/OIDC 产品化  
**规范源：** ADR-0053  

## 1. 门禁目标

以 OIDC/JWT 在 Gateway 派生受信 `ExecutionContext`，并列开发态显式头注入。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Derivation | Bearer 优先；否则开发头（可关） |
| Alg | HS256（`EAOS_JWT_SECRET`）；JWKS/RS256 延后 |
| Elevation | tenant 面拒 `eaos_platform_scope=true` |
| Body | 仍不可提升 |

## 3. Exit Criteria

1. ADR-0053 Accepted。  
2. Bearer → subject/tenant/correlation 派生。  
3. 开发头默认保留；`EAOS_REQUIRE_JWT=1` 可强制 JWT。  
4. 伪造签名拒绝契约通过。

## 4. Explicit Defer

OIDC 登录页 / Authorization Code；JWKS / RS256 轮换；Marketplace 商业（M17）
