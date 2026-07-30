# ADR-0206 — OpenAPI OIDC Login Product-Posture Schema Parity

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G187  
**归属：** API Gateway / Auth / OpenAPI  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U060**；PO cue「充分授权…自主开发…加快」

## 背景

G147/G185 已发出稳定的 `oidc_login_product` / `webauthn_product`，但
`OidcLoginProductPosture` 仍为宽松 `additionalProperties` 与不完整 required。

## 决策

1. Auth OpenAPI **1.3.10**：`OidcLoginProductPosture` → emitted field parity  
   （`additionalProperties: false`；`milestone` const `PHX-G147`；
   `protocol` const `oauth2_authorization_code`）。  
2. Inventory：`milestone=PHX-G187`；
   `t0188_status=mount_parity_complete_oidc_login_product_posture_schema_honest`。  
3. Ops OpenAPI **1.0.14** 同步 inventory const。  
4. `full_openapi_http_complete` **仍为 false**；attestation crypto / Brain /
   Twin / PSP / Cap→grant 仍关闭。  
5. 包仍 `0.2.1`；Alembic 仍 `0029`。

## Explicit Out

- WebAuthn attestation crypto  
- New auth protocol / ceremony invent  
- Full OpenAPI semantic parity  

## 关联

- [../project/PHX-G187_ARCHITECTURE_GATE.md](../project/PHX-G187_ARCHITECTURE_GATE.md)  
- [ADR-0204](ADR-0204-openapi-auth-permission-product-posture-schema-parity.md)  
