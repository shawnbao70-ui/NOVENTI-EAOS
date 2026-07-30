# ADR-0209 — OpenAPI OIDC Status Body Field Parity

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G190  
**归属：** API Gateway / Auth / OpenAPI  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U063**；PO cue「充分授权…自主开发…加快」

## 背景

G189 将 IdP status 顶层与 jwt/registry/federation 对齐，但 nested `oidc` 与
`GET /auth/oidc/status` 仍复用宽松 `AuthStatusEnvelope`。

## 决策

1. Auth OpenAPI **1.3.13**：新增 `OidcStatusEnvelope` / `OidcStatusData`
   （emitted field parity vs `oidc_status()`；含 `OidcLoginProductPosture` /
   `WebauthnProductPosture` refs）。  
2. `GET /auth/oidc/status` 200 → `OidcStatusEnvelope`。  
3. `IdpStatusData.oidc` → `$ref: OidcStatusData`（关闭 G189 nested oidc defer）。  
4. Inventory：`milestone=PHX-G190`；
   `t0188_status=mount_parity_complete_oidc_status_body_field_parity`。  
5. Ops OpenAPI **1.0.17** 同步 inventory const。  
6. `full_openapi_http_complete` **仍为 false**。  
7. 包仍 `0.2.1`；Alembic 仍 `0029`。

## Explicit Out

- Secrets / refresh_token plaintext  
- Attestation crypto / Brain / Twin / PSP / Cap→grant  
- Full OpenAPI semantic parity across all domains  

## 关联

- [../project/PHX-G190_ARCHITECTURE_GATE.md](../project/PHX-G190_ARCHITECTURE_GATE.md)  
- [ADR-0208](ADR-0208-openapi-idp-status-body-field-parity.md)  
