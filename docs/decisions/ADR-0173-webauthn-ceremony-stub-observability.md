# ADR-0173 — WebAuthn Ceremony Stub Observability Deepen

**状态：** Accepted  
**日期：** 2026-07-21  
**里程碑：** PHX-G154  
**归属：** API Gateway / Auth / Smart Terminal  
**授权：** DAL-G003 + DAL-G004 Eng Explicit Defer `2` deepen（DAL-U026）；AED v1.1

## 背景

PHX-G151 已交付 named ceremony stub 路由并以 503 fail-closed。AED deepen order #2 允许在 **不 mint** 的前提下继续加深 Eng `2`：为客户端与运维提供 `ceremony_step` 可观测字段，并修正 OpenAPI inventory defer fence 为 `webauthn_live_credential_mint`（反映 stub 已存在、live mint 仍 Held）。

## 决策

1. `raise_webauthn_registration_disabled(*, ceremony_step=…)` 仍返回 503 + code
   **`GATEWAY_WEBAUTHN_REGISTRATION_DISABLED`**，并在 `detail` 中增加：  
   `ceremony_step` · `registration_minted: false` · `attestation_verified: false` · `next_action: "none"`。  
2. Router 分别传入 `register_options` / `register_verify`。  
3. `webauthn_product` 里程碑 → **PHX-G154**；`ceremony_stub_observability: true`；registration 仍恒 `false`。  
4. OpenAPI `auth.openapi.yaml` → **1.3.4**；新增 `WebauthnCeremonyStubDetail` / `WebauthnCeremonyStubError`。  
5. Inventory fence：`webauthn_registration_ceremony` → **`webauthn_live_credential_mint`**。  
6. `/auth/webauthn/register` 仍 ABSENT；env `EAOS_WEBAUTHN_REGISTRATION_ENABLED` 仍 future-only（不 mint）。  
7. **不**新增 Alembic；包版本保持 `0.2.1`。

## Explicit Out（本切片不开口）

- Live WebAuthn credential create/get / attestation mint  
- Honoring `EAOS_WEBAUTHN_REGISTRATION_ENABLED=true` as a mint switch  
- Single-path `/auth/webauthn/register` product page  
- Role→grant mint / 支付清算 / Brain execute / Twin authorize  
- 新 Alembic revision  

## 后果

- Eng `2` 以 **stub observability** 加深；live mint 仍另批。  
- IdP MFA enrollment redirect（G89/G134）仍是唯一 live enroll 路径。

## 关联

- [../project/PHX-G154_ARCHITECTURE_GATE.md](../project/PHX-G154_ARCHITECTURE_GATE.md)  
- [../project/PHX-G154_ACCEPTANCE.md](../project/PHX-G154_ACCEPTANCE.md)  
- [ADR-0170-webauthn-ceremony-stub-deepen.md](ADR-0170-webauthn-ceremony-stub-deepen.md)  
- [ADR-0169-autonomous-execution-directive.md](ADR-0169-autonomous-execution-directive.md)  
- [../project/DELEGATED_AUTHORITY_LEDGER.md](../project/DELEGATED_AUTHORITY_LEDGER.md)  
