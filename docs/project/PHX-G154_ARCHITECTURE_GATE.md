# PHX-G154 WebAuthn Ceremony Stub Observability Architecture Gate

**日期：** 2026-07-21  
**状态：** Fully Accepted（Foundation）  
**归属：** API Gateway / Auth / Smart Terminal  
**规范源：** ADR-0173  
**授权：** DAL-G003 + DAL-G004 Eng Explicit Defer `2` deepen（DAL-U026）；AED v1.1

## 1. 门禁目标

加深 Eng Explicit Defer `2`（相对 G151 stub）：503 detail 携带 `ceremony_step` 可观测字段；`registration_minted` / `attestation_verified` 恒 `false`；`next_action=none`；inventory fence 改为 live-mint；包仍 `0.2.1`；Alembic 仍 `0029`。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Surface kind | Stub observability deepen（**not** options minting） |
| Helper | `webauthn_ceremony.raise_webauthn_registration_disabled(ceremony_step=…)` |
| Router | options → `register_options`；verify → `register_verify` |
| Posture | milestone `PHX-G154`；`ceremony_stub_observability=true` |
| Inventory | fence `webauthn_live_credential_mint` |
| Live register page | `/auth/webauthn/register` **ABSENT** |
| Package / Alembic | Stay `0.2.1` / `0029` |
| Out | Live create/get mint；Role→grant mint；支付清算；Brain execute；Twin authorize |

## 3. Exit Criteria

1. ADR-0173 Accepted。  
2. Gate / Acceptance + helper/router/posture/OpenAPI/inventory/Terminal + DAL-U026 齐。  
3. `test_api_gateway_g154_*` 与软化后的 G151 / auth OpenAPI / G148 / DAL 合约绿。  

见 [PHX-G154_ACCEPTANCE.md](PHX-G154_ACCEPTANCE.md)。
