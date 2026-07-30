# PHX-G38 JWT JWKS / RS256 Acceptance

**日期：** 2026-07-19  
**状态：** Fully Accepted  
**归属：** Platform API Gateway / Identity  
**退出门禁：** RS256 + JWKS；HS256 回归；无登录页

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0055 + Architecture Gate |
| B | `verify_token` alg 分流；JWKS JSON / HTTPS URL |
| C | `kid` 选择与多密钥；`cryptography` api extra |
| D | 契约测试 + 七步自审 |

## 2. 核心不变量

- Body 仍不可提升  
- 租户面拒 `eaos_platform_scope=true`  
- HS256 与 RS256 并列  
- 非 https JWKS URL 拒绝  

## 3. 自动化证据

- 本地完整回归：`415 passed`（`tests/contracts`）  
- 无 schema 变更；Alembic head 仍为 `0022_marketplace_m17_commercial`  

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0055 |
| Constitution Review | 通过；Gateway 认证边界 |
| Cross-reference Review | 通过；G37 HS256 仍绿 |
| Documentation Review | 通过 |
| Consistency Review | 通过 |
| Gap Analysis | OIDC 登录页 / ES256·EdDSA 显式延后 |
| Second-pass Review | Fully Accepted |

## 5. Explicit Defer

- OIDC Authorization Code 登录页与 IdP 联邦  
- ES256 / EdDSA；密钥吊销列表产品化  
- Terminal Extension Host；Webhook HMAC  

## 6. 证据索引

- [PHX-G38 Architecture Gate](PHX-G38_ARCHITECTURE_GATE.md)
- [ADR-0055](../decisions/ADR-0055-jwt-jwks-rs256.md)
- [ADR-0053](../decisions/ADR-0053-jwt-oidc-trusted-context.md)
