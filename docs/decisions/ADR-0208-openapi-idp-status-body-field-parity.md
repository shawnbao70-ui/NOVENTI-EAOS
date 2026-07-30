# ADR-0208 — OpenAPI IdP Status Body Field Parity

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G189  
**归属：** API Gateway / Auth / OpenAPI  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U062**；PO cue「充分授权…自主开发…加快」

## 背景

`GET /auth/idp/status` 聚合 OIDC/JWT/registry/federation，但 OpenAPI 仍复用宽松
`AuthStatusEnvelope`，无法核对顶层与 jwt/registry/federation 形状。

## 决策

1. Auth OpenAPI **1.3.12**：新增 `IdpStatusEnvelope` / `IdpStatusData` /
   `IdpJwtAggregatePosture` / `IdpRegistryStatusPosture` /
   `IdpFederationStatusPosture`。  
2. Nested `oidc` **保持** `additionalProperties: true`（全量 OIDC nested
   field parity 后置）。  
3. Inventory：`milestone=PHX-G189`；
   `t0188_status=mount_parity_complete_idp_status_body_field_parity`。  
4. Ops OpenAPI **1.0.16** 同步 inventory const。  
5. `full_openapi_http_complete` **仍为 false**。  
6. 包仍 `0.2.1`；Alembic 仍 `0029`。

## Explicit Out

- Full nested OIDC status schema invent  
- Secrets / jti dump  
- Full OpenAPI semantic parity  

## 关联

- [../project/PHX-G189_ARCHITECTURE_GATE.md](../project/PHX-G189_ARCHITECTURE_GATE.md)  
- [ADR-0207](ADR-0207-openapi-jwt-status-body-field-parity.md)  
