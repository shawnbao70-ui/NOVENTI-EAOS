# PHX-G160 WebAuthn Env-Gated Live Mint Architecture Gate

**日期：** 2026-07-22  
**状态：** Fully Accepted（Foundation）  
**归属：** API Gateway / Identity / Smart Terminal  
**规范源：** ADR-0183  
**授权：** **DAL-G008** + DAL-G003 + DAL-G004；Usage **DAL-U037**；AED v1.1

## 1. 门禁目标

在 explicit PO（「继续WebAuthn live mint」）下打开 Eng Explicit Defer `2` **challenge-bound live mint**：env-gated `POST /auth/webauthn/register/options|verify`；默认 OFF 保持 503；`attestation_crypto_verified=false`；`/auth/webauthn/register` ABSENT；包仍 `0.2.1`；Alembic 仍 `0029`。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Surface kind | Env-gated WebAuthn challenge-bound mint（default 503） |
| Env | `EAOS_WEBAUTHN_REGISTRATION_ENABLED`（default false） |
| RP prerequisite | `EAOS_WEBAUTHN_RP_ID` + `EAOS_WEBAUTHN_ORIGIN` |
| Router | options/verify → mint or 503；single-path register ABSENT |
| Posture | milestone `PHX-G160`；`webauthn_registration_enabled` mirrors env |
| Binding | challenge + origin + `webauthn.create`；opaque attestation presence |
| Inventory | fence → `webauthn_attestation_crypto_verify`（live mint opened） |
| Package / Alembic | Stay `0.2.1` / `0029` |
| Out | packed/TPM attestation crypto；`/auth/webauthn/register`；Brain execute；Twin authorize；Cap→grant；payment regress |

## 3. Exit Criteria

1. ADR-0183 Accepted。  
2. Gate / Acceptance + ceremony/router/posture/OpenAPI/Terminal + DAL-G008/U037 齐。  
3. `test_api_gateway_g160_*` 与软化后的 G145/G151/G154 合约绿。  

见 [PHX-G160_ACCEPTANCE.md](PHX-G160_ACCEPTANCE.md)。
