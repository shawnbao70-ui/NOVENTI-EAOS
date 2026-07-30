# ADR-0241 — OpenAPI Stub Detail Const Honesty

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G222  
**归属：** OpenAPI Inventory / Marketplace / Auth  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U095**；PO cue「充分授权…自主开发…加快」

## 背景

Payment clearing / WebAuthn ceremony stub 503 details 的 live emit 对
`settlement_rail` / `next_action` / `milestone` 等键有固定值，但 OpenAPI
未并列 `const`（或未收紧 enum），与 G206 单值诚实风格不一致。

## 决策

1. `PaymentClearingStubDetail`：`settlement_rail`/`next_action` const `none`；
   required 补齐。  
2. `WebauthnCeremonyStubDetail`：`next_action` enum；`milestone` const
   `PHX-G160`；required 补齐 `attestation_crypto_verified`/`milestone`。  
3. marketplace **1.2.10**；auth **1.3.19**；Inventory `milestone=PHX-G222`；
   `t0188_status=mount_parity_complete_stub_detail_const_honest`；ops **1.0.37**。  
4. `full_openapi_http_complete=false`；包 `0.2.1`；Alembic `0029`。

## Explicit Out

- Enabling live mint / external PSP  
- Semantic-complete claim  
- HARD HOLD openings  

## 关联

- [../project/PHX-G222_ARCHITECTURE_GATE.md](../project/PHX-G222_ARCHITECTURE_GATE.md)  
