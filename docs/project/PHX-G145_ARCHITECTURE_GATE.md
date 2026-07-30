# PHX-G145 WebAuthn / MFA Product Posture Architecture Gate

**日期：** 2026-07-21  
**状态：** Fully Accepted（Foundation）  
**归属：** API Gateway / Auth / Smart Terminal  
**规范源：** ADR-0164  
**授权：** DAL-G003 Eng Explicit Defer `2`（DAL-U006）

## 1. 门禁目标

以 **只读产品姿态面** 打开 Eng Explicit Defer `2`：命名 Foundation MFA/WebAuthn 产品面；显式 `webauthn_registration_enabled: false`；保留 G89/G134 IdP enrollment redirect 为唯一 live enroll 路径；Terminal 薄行展示姿态；**不**交付 live WebAuthn ceremony；包仍 `0.2.1`；Alembic 仍 `0029`。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Surface kind | Read-only product posture（thin） |
| Helper | `api/gateway/webauthn_product.py` → posture dict |
| Wire | `oidc_status()` / `GET /v1/auth/oidc/status` → `webauthn_product` |
| Live enroll | IdP redirect G89/G134 only |
| Registration | `webauthn_registration_enabled=false`；`registration_routes=[]`；`/auth/webauthn/register` ABSENT |
| Terminal | Thin MFA / WebAuthn product row |
| Package / Alembic | Stay `0.2.1` / `0029` |
| Out | Live WebAuthn ceremony；Role→grant；支付清算；Brain execute；Twin authorize；新 Alembic |

## 3. Exit Criteria

1. ADR-0164 Accepted。  
2. Gate / Acceptance + helper + OpenAPI + Terminal + DAL-U006 + status sync 齐。  
3. `test_api_gateway_g145_webauthn_product_posture.py` 与相关 G134/auth/DAL/G144 合约绿。  

见 [PHX-G145_ACCEPTANCE.md](PHX-G145_ACCEPTANCE.md)。
