# ADR-0197 — OpenAPI Identity/Organization Status-Code Honesty

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G178  
**归属：** API Gateway / OpenAPI  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U051**；PO cue「充分授权…自主开发…加快」

## 背景

G166 对齐 Identity/Org → GatewayDetailError；G176/G177 诚实化 Platform/Auth OIDC 命名状态码。Identity/Organization 写读路径真实 **400/403/404/409/503** 仍多落在 `default`。

## 决策

1. Identity OpenAPI（`1.0.3`）与 Organization OpenAPI（`1.0.2`）为主要写/读路径文档化真实命名状态码（GatewayDetailError）。  
2. 文档跟随现有 gateway 映射（含 AI profile/governor「not found」→ **400** 等 quirks；不在本切片改 `raise_for_result`）。  
3. Inventory：`milestone=PHX-G178`；`t0188_status=mount_parity_complete_identity_org_status_codes_honest`。  
4. `full_openapi_http_complete` **仍为 false**。  
5. 包仍 `0.2.1`；Alembic 仍 `0029`；不打开 HARD HOLDS。

## Explicit Out

- Full OpenAPI semantic parity  
- Remap Identity quirk codes to REST-canonical 404/409  
- Brain / Twin / PSP / attestation crypto  

## 关联

- [../project/PHX-G178_ARCHITECTURE_GATE.md](../project/PHX-G178_ARCHITECTURE_GATE.md)  
- [ADR-0196-openapi-auth-oidc-status-code-honesty.md](ADR-0196-openapi-auth-oidc-status-code-honesty.md)  
