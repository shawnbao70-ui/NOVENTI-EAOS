# ADR-0183 — WebAuthn Env-Gated Live Credential Mint

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G160  
**归属：** API Gateway / Identity / Smart Terminal  
**授权：** **DAL-G008**（explicit PO WebAuthn live mint）+ DAL-G003 + DAL-G004；Usage **DAL-U037**；AED v1.1

## 背景

PHX-G145/G151/G154 交付了 MFA/WebAuthn 只读姿态与 named ceremony stub `POST /auth/webauthn/register/options|verify` → 503。AED / tip 将 **live mint** 与 packed/TPM attestation crypto 分开：challenge-bound mint 可在 explicit PO 下 env-gated 打开；attestation-statement crypto verify 仍 Explicit Out。CA/PO cue「继续WebAuthn live mint」满足该门槛。

## 决策

1. Env `EAOS_WEBAUTHN_REGISTRATION_ENABLED`（default **false**）门控 live mint。  
2. Live mint 另需 `EAOS_WEBAUTHN_RP_ID` + `EAOS_WEBAUTHN_ORIGIN`；否则 503 `GATEWAY_WEBAUTHN_RP_CONFIG_REQUIRED`。  
3. `POST /v1/auth/webauthn/register/options`：disabled → 503；ready → mint PublicKeyCredentialCreationOptions（challenge TTL 300s）。  
4. `POST /v1/auth/webauthn/register/verify`：challenge + origin + type 绑定后 → `Identity.BindCredential(kind=webauthn)`；响应恒 `attestation_crypto_verified=false` / `attestation_mode=challenge_bound`。  
5. Posture milestone **PHX-G160**；auth OpenAPI → **1.3.6**；inventory fence → `webauthn_attestation_crypto_verify`；Terminal 薄行同步 env 文案。  
6. `/auth/webauthn/register` 单路径仍 **ABSENT**；无新 Alembic；包仍 `0.2.1`。

## Explicit Out（本切片不开口）

- Full packed/TPM attestation-statement crypto verify  
- Single-path `/auth/webauthn/register` product page  
- Brain execute / Twin authorize  
- Cap→grant invent / Role→grant regress（G161 独立）  
- Marketplace payment / external PSP（G162 独立）  
- Const/BP rewrite  
- 新 Alembic revision / package bump beyond `0.2.1`

## 后果

- Eng `2` live mint 在 **explicit PO + env ON + RP config** 下可用；默认仍 503。  
- Attestation crypto 与单路径 register 产品页仍 Held；不回归 G161/G162/G163。

## 关联

- [../project/PHX-G160_ARCHITECTURE_GATE.md](../project/PHX-G160_ARCHITECTURE_GATE.md)  
- [../project/PHX-G160_ACCEPTANCE.md](../project/PHX-G160_ACCEPTANCE.md)  
- [ADR-0170-webauthn-ceremony-stub-deepen.md](ADR-0170-webauthn-ceremony-stub-deepen.md)  
- [ADR-0173-webauthn-ceremony-stub-observability.md](ADR-0173-webauthn-ceremony-stub-observability.md)  
- [ADR-0164-webauthn-mfa-product-posture.md](ADR-0164-webauthn-mfa-product-posture.md)  
- [../project/DELEGATED_AUTHORITY_LEDGER.md](../project/DELEGATED_AUTHORITY_LEDGER.md)  
