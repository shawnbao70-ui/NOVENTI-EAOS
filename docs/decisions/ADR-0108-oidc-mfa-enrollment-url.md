# ADR-0108 — OIDC MFA Enrollment URL Gate

**状态：** Accepted  
**日期：** 2026-07-20  
**里程碑：** PHX-G89  
**归属：** Platform API Gateway / OIDC

## 背景

G80/G87 覆盖 token/authorize 侧 MFA 要求。仍缺指向 IdP 注册页的薄出口；完整 WebAuthn/MFA 产品 UX 另批。

## 决策

1. 可选 `EAOS_OIDC_MFA_ENROLLMENT_URL`：HTTPS（或 http loopback 测试）；空=关闭。  
2. `GET /v1/auth/oidc/mfa-enrollment` → 302；未配置 → `503` + `GATEWAY_OIDC_MFA_ENROLLMENT_UNCONFIGURED`；非法 URL → `GATEWAY_OIDC_MFA_ENROLLMENT_INVALID`。  
3. status 暴露 `mfa_enrollment_enabled` / `mfa_enrollment_url`。  
4. G80 amr/acr deny 的 `details` 可选附带 `mfa_enrollment_url`。  
5. Terminal 在 enabled 时显示薄链接；无 WebAuthn 注册实现；无 Alembic；包版本仍 `0.2.0`。

## Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批）  
- WebAuthn / MFA 注册产品页  
- Role SQL / 自动写 grant  

## 关联

- [ADR-0099-oidc-amr-acr-gate.md](ADR-0099-oidc-amr-acr-gate.md)
- [ADR-0106-oidc-authorize-stepup.md](ADR-0106-oidc-authorize-stepup.md)
- [../project/PHX-G89_ARCHITECTURE_GATE.md](../project/PHX-G89_ARCHITECTURE_GATE.md)
