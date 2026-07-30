# ADR-0106 — OIDC Authorize ACR/Prompt Step-Up Gate

**状态：** Accepted  
**日期：** 2026-07-20  
**里程碑：** PHX-G87  
**归属：** Platform API Gateway / OIDC

## 背景

G80 在 token 侧强制 amr/acr。登录 authorize 请求尚未携带 `acr_values` / `prompt`，无法向 IdP 请求 step-up；完整 MFA 注册 UX 另批。

## 决策

1. 可选 `EAOS_OIDC_AUTHORIZE_ACR_VALUES`：非空则写入 authorize `acr_values`。  
2. 可选 `EAOS_OIDC_AUTHORIZE_PROMPT`：非空则写入 authorize `prompt`（如 `login`）。  
3. 二者皆空 = 关闭；status 暴露 `authorize_stepup_enabled` / `authorize_acr_values` / `authorize_prompt`。  
4. 不实现 MFA 注册页 / WebAuthn；与 G80 token 门禁互补；无 Alembic；包版本仍 `0.2.0`。

## Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批）  
- MFA 注册 / WebAuthn UX  
- Role 目录 / 自动写 grant  
- 按请求覆盖 acr_values/prompt（query 提升）  

## 关联

- [ADR-0099-oidc-amr-acr-gate.md](ADR-0099-oidc-amr-acr-gate.md)
- [../project/PHX-G87_ARCHITECTURE_GATE.md](../project/PHX-G87_ARCHITECTURE_GATE.md)
