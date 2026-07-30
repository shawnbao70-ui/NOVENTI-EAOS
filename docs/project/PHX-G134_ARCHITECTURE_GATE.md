# PHX-G134 OIDC MFA Enrollment OpenAPI Architecture Gate

**日期：** 2026-07-21  
**状态：** Fully Accepted（Foundation）  
**归属：** API Contracts / Auth  
**规范源：** ADR-0153  
**人工确认：** 仅契约增补既有 G89 重定向出口；≠ WebAuthn 产品页；无运行时/Alembic/版本 bump  

## 1. 门禁目标

将 OIDC MFA enrollment redirect exit 纳入 `auth.openapi.yaml`。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Artifact | 扩展既有 `docs/api/auth.openapi.yaml`（v1.3.0） |
| Path | `GET /auth/oidc/mfa-enrollment` |
| Fence | ≠ WebAuthn / MFA registration product UI |
| Out | WebAuthn 产品页；支付清算；`0.2.1` |

## 3. Exit Criteria

1. ADR-0153 Accepted。  
2. OpenAPI 与契约绿。  
3. 全量 contracts 绿；包 `0.2.0`；head `0029`。  

见 [PHX-G134_ACCEPTANCE.md](PHX-G134_ACCEPTANCE.md)。
