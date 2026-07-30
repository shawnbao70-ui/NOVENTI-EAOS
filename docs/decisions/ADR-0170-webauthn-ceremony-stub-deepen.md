# ADR-0170 — WebAuthn Ceremony Stub Deepen

**状态：** Accepted  
**日期：** 2026-07-21  
**里程碑：** PHX-G151  
**归属：** API Gateway / Auth / Smart Terminal  
**授权：** DAL-G003 + DAL-G004 Eng Explicit Defer `2` deepen（DAL-U023）；AED v1.1

## 背景

PHX-G145 已交付只读 WebAuthn / MFA 产品姿态（`webauthn_registration_enabled=false`；`registration_routes=[]`）。AED deepen order #2 要求加深 Eng `2`：命名 **ceremony stub** 路由并以 503 fail-closed 固定边界，**不** mint live credential create/get。

## 决策

1. 新增 stub helper `api/gateway/webauthn_ceremony.py`：统一 503 + `GATEWAY_WEBAUTHN_REGISTRATION_DISABLED`；**不**读取 env 开启 mint。  
2. 新增 FastAPI 路由 `api/gateway/routers/webauthn.py`，挂到 `app.py`：  
   - `POST /v1/auth/webauthn/register/options` → 503  
   - `POST /v1/auth/webauthn/register/verify` → 503  
3. **`/auth/webauthn/register` 仍 ABSENT**（无单段 register 产品页）。  
4. 更新 `webauthn_product` 姿态：`webauthn_registration_enabled` 仍恒 `false`；`registration_routes` 列出上述两条 stub 路径；里程碑 `PHX-G151`。  
5. 文档化 env `EAOS_WEBAUTHN_REGISTRATION_ENABLED` 为 **future only** — G151 **即使为 true 也不 mint**。  
6. OpenAPI `auth.openapi.yaml` patch bump；去掉 `registration_routes` 的 `maxItems: 0`。  
7. Terminal 薄行文案同步 stub 503 姿态。  
8. **不**新增 Alembic；包版本保持 `0.2.1`。

## Explicit Out（本切片不开口）

- Live WebAuthn credential create/get / attestation mint  
- Honoring `EAOS_WEBAUTHN_REGISTRATION_ENABLED=true` as a mint switch  
- Single-path `/auth/webauthn/register` product page  
- Role→grant mint / 支付清算 / Brain execute / Twin authorize  
- 新 Alembic revision  

## 后果

- Eng `2` 以 **named stub 503 ceremony routes** 加深；live ceremony 仍另批。  
- IdP MFA enrollment redirect（G89/G134）仍是唯一 live enroll 路径。  
- Role→grant mint 仍需 explicit PO；支付 / Brain / Twin 仍关闭。

## 关联

- [../project/PHX-G151_ARCHITECTURE_GATE.md](../project/PHX-G151_ARCHITECTURE_GATE.md)  
- [../project/PHX-G151_ACCEPTANCE.md](../project/PHX-G151_ACCEPTANCE.md)  
- [ADR-0164-webauthn-mfa-product-posture.md](ADR-0164-webauthn-mfa-product-posture.md)  
- [ADR-0169-autonomous-execution-directive.md](ADR-0169-autonomous-execution-directive.md)  
- [../project/DELEGATED_AUTHORITY_LEDGER.md](../project/DELEGATED_AUTHORITY_LEDGER.md)  
