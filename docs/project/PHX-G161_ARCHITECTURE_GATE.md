# PHX-G161 Role→grant Env-Gated Live Mint Architecture Gate

**日期：** 2026-07-22  
**状态：** Fully Accepted（Foundation）  
**归属：** API Gateway / Permission / Smart Terminal  
**规范源：** ADR-0179  
**授权：** **DAL-G006** + DAL-G003 + DAL-G004；Usage **DAL-U032**；AED v1.1

## 1. 门禁目标

在 explicit PO（「继续Role→grant live mint」）下打开 Eng Explicit Defer `3` **live mint**：env-gated `POST /permission/role-grants`；默认 OFF 保持 503；Cap≠grant / title≠permission；包仍 `0.2.1`；Alembic 仍 `0029`。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Surface kind | Env-gated Role→grant mint（default 503） |
| Env | `EAOS_ROLE_GRANT_AUTO_WRITE_ENABLED`（default false） |
| Map prerequisite | Non-empty `EAOS_PERMISSION_ROLE_GRANT_MAP` |
| Router | `POST /v1/permission/role-grants` → mint or 503 |
| Posture | milestone `PHX-G161`；`auto_grant_from_role_enabled` mirrors env |
| Invariants | Cap≠grant；title≠permission；≠ Cap→grant invent |
| Package / Alembic | Stay `0.2.1` / `0029` |
| Out | payment；Brain execute；Twin authorize；full OpenAPI parity；Const/BP；WebAuthn attestation crypto |

## 3. Exit Criteria

1. ADR-0179 Accepted。  
2. Gate / Acceptance + helper/router/posture/OpenAPI/Terminal + DAL-G006/U032 齐。  
3. `test_api_gateway_g161_*` 与软化后的 G146/G156/G136 合约绿。  

见 [PHX-G161_ACCEPTANCE.md](PHX-G161_ACCEPTANCE.md)。
