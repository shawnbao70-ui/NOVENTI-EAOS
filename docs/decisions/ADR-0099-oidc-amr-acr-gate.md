# ADR-0099 — OIDC amr/acr Auth Context Gate

**状态：** Accepted  
**日期：** 2026-07-20  
**里程碑：** PHX-G80  
**归属：** Platform API Gateway / OIDC boundary

## 背景

G79 提供必填声明门禁。运维仍需对 OIDC `amr` / `acr` 做可选认证上下文校验，而不引入完整 MFA 策略引擎或注册 UI。

## 决策

1. `EAOS_OIDC_REQUIRED_AMR`：逗号分隔方法名；id_token `amr`（数组或字符串）须**至少命中其一**；空=关闭。  
2. `EAOS_OIDC_REQUIRED_ACR`：逗号分隔允许 `acr` 值；id_token `acr` 须**精确命中其一**；空=关闭。  
3. 在 `map_oidc_claims_to_eaos` 中、required-claims 之后校验；缺失/不匹配 → `401` + `GATEWAY_OIDC_AMR_REQUIRED` / `GATEWAY_OIDC_ACR_REQUIRED`。  
4. `GET /v1/auth/oidc/status` 暴露 `required_amr` / `required_amr_enabled` / `required_acr` / `required_acr_enabled`。  
5. 无 Alembic；无 Terminal MFA UI；包版本仍 `0.2.0`。  

## Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批）  
- MFA 注册 / step-up UX / WebAuthn  
- Social login / claim→role 映射  
- 多 issuer 登录重定向  

## 关联

- [ADR-0098-oidc-required-claims-gate.md](ADR-0098-oidc-required-claims-gate.md)
- [../project/PHX-G80_ARCHITECTURE_GATE.md](../project/PHX-G80_ARCHITECTURE_GATE.md)
