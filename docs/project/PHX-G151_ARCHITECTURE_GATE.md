# PHX-G151 WebAuthn Ceremony Stub Deepen Architecture Gate

**日期：** 2026-07-21  
**状态：** Fully Accepted（Foundation）  
**归属：** API Gateway / Auth / Smart Terminal  
**规范源：** ADR-0170  
**授权：** DAL-G003 + DAL-G004 Eng Explicit Defer `2` deepen（DAL-U023）；AED v1.1

## 1. 门禁目标

加深 Eng Explicit Defer `2`（相对 G145 thin posture）：命名 WebAuthn **ceremony stub** 路由并以 **503 + `GATEWAY_WEBAUTHN_REGISTRATION_DISABLED`** fail-closed；`webauthn_registration_enabled` 仍恒 `false`；`registration_routes` 列出 stub 路径；`/auth/webauthn/register` 仍 ABSENT；env `EAOS_WEBAUTHN_REGISTRATION_ENABLED` 仅文档化（future；G151 不 mint）；包仍 `0.2.1`；Alembic 仍 `0029`。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Surface kind | Gate + named stub 503 ceremony routes（**not** options minting） |
| Helper | `api/gateway/webauthn_ceremony.py` → stub raise / route constants |
| Router | `api/gateway/routers/webauthn.py` → `POST …/register/options` + `POST …/register/verify` |
| Wire | `app.py` `include_router`（同 auth router 模式） |
| Posture | `webauthn_product.py` → G151；`registration_enabled=false`；routes = stub paths |
| Live register page | `/auth/webauthn/register` **ABSENT** |
| Env | `EAOS_WEBAUTHN_REGISTRATION_ENABLED` documented future-only；ignored for mint |
| Terminal | Thin row copy: stub 503 / registration still closed |
| Package / Alembic | Stay `0.2.1` / `0029` |
| Out | Live create/get mint；Role→grant mint；支付清算；Brain execute；Twin authorize；新 Alembic |

## 3. Exit Criteria

1. ADR-0170 Accepted。  
2. Gate / Acceptance + ceremony helper + router + posture + OpenAPI + Terminal + DAL-U023 + status sync 齐。  
3. `test_api_gateway_g151_webauthn_ceremony_stub.py` 与相关 G145/G134/auth/DAL/G144 合约绿。  

见 [PHX-G151_ACCEPTANCE.md](PHX-G151_ACCEPTANCE.md)。
