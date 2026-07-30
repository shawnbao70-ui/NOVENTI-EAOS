# ADR-0255 — OpenAPI Opaque Auth Array-Item Named Honesty

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G236  
**归属：** OpenAPI Inventory / Auth  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U109**；PO cue「充分授权…自主开发…加快」

## 背景

三处 auth array items 仍为 opaque `additionalProperties: true`：
OidcStatusData.login_providers、IdpRegistryStatusPosture.issuers、
OidcProvidersPayload.providers。另有未引用 `AuthStatusEnvelope`/`AuthStatusData`
孤儿（G188–G190 已改用专用信封）。

## 决策

1. 新增 `OidcLoginProviderPublicItem`；login_providers + providers items → `$ref`。  
2. 新增 `IdpRegistryIssuerStatusItem`；issuers items → `$ref`。  
3. 删除孤儿 `AuthStatusEnvelope` + `AuthStatusData`。  
4. auth **1.3.22**；Inventory `milestone=PHX-G236`；
   `t0188_status=mount_parity_complete_opaque_auth_array_items_named_honest`；ops **1.0.44**。  
5. `full_openapi_http_complete=false`；包 `0.2.1`；Alembic `0029`。

## Explicit Out

HARD HOLD openings；handler invent；semantic-complete claim。  
