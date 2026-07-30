# PHX-G156 Role→grant Auto-Write Stub Deepen Architecture Gate

**日期：** 2026-07-21  
**状态：** Fully Accepted（Foundation）  
**归属：** API Gateway / Permission / Smart Terminal  
**规范源：** ADR-0175  
**授权：** DAL-G003 + DAL-G004 Eng Explicit Defer `3` deepen（DAL-U028）；AED v1.1

## 1. 门禁目标

加深 Eng Explicit Defer `3`（相对 G146 thin posture）：命名 Role→grant auto-write **stub** 并以 **503 + `GATEWAY_ROLE_GRANT_AUTO_WRITE_DISABLED`** fail-closed；`auto_grant_from_role_enabled` 仍恒 `false`；**不** mint；live mint 仍需 **explicit PO**；包仍 `0.2.1`；Alembic 仍 `0029`。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Surface kind | Named stub 503（**not** grant mint） |
| Helper | `role_grant_auto_write.py` |
| Router | `POST /v1/permission/role-grants` → 503 |
| Posture | milestone `PHX-G156`；`auto_write_routes` = stub path |
| Package / Alembic | Stay `0.2.1` / `0029` |
| Out | Live mint（needs PO）；支付；Brain execute；Twin authorize；WebAuthn live mint |

## 3. Exit Criteria

1. ADR-0175 Accepted。  
2. Gate / Acceptance + helper/router/posture/OpenAPI/Terminal + DAL-U028 齐。  
3. `test_api_gateway_g156_*` 与软化后的 G146/G136 合约绿。  

见 [PHX-G156_ACCEPTANCE.md](PHX-G156_ACCEPTANCE.md)。
