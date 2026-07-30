# PHX-G89 OIDC MFA Enrollment URL Gate Architecture Gate

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform API Gateway / OIDC  
**规范源：** ADR-0108  
**人工确认：** 支付清算另批；无 WebAuthn 注册产品页  

## 1. 门禁目标

可选 IdP MFA 注册 URL 出口 + deny 提示；默认关闭。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Env | `EAOS_OIDC_MFA_ENROLLMENT_URL` |
| API | `GET /v1/auth/oidc/mfa-enrollment` |
| Deny | amr/acr details 可附 URL |
| Schema | 无 Alembic |

## 3. Exit Criteria

1. ADR-0108 Accepted。  
2. 空=off；合法 URL 可 302；非法 fail-closed；Terminal 薄链。  
3. 全量 contracts 绿；包 `0.2.0`；head `0028`。  

见 [PHX-G89_ACCEPTANCE.md](PHX-G89_ACCEPTANCE.md)。
