# ADR-0198 — OpenAPI Permission/Workflow Status-Code Honesty

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G179  
**归属：** API Gateway / OpenAPI  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U052**；PO cue「充分授权…自主开发…加快」

## 背景

G178 诚实化 Identity/Org 命名状态码。Permission/Workflow 写读路径真实 **400/403/404/409/503** 仍多落在 `default`（Role→grant mint 与 roles catalog 已部分命名除外）。

## 决策

1. Permission OpenAPI（`1.1.6`）与 Workflow OpenAPI（`1.0.4`）为主要写/读路径文档化真实命名状态码（GatewayDetailError）。  
2. Inventory：`milestone=PHX-G179`；`t0188_status=mount_parity_complete_permission_workflow_status_codes_honest`。  
3. `full_openapi_http_complete` **仍为 false**。  
4. 包仍 `0.2.1`；Alembic 仍 `0029`；不打开 HARD HOLDS；Cap≠grant 不变。

## Explicit Out

- Full OpenAPI semantic parity  
- Cap→grant invent / Brain / Twin / PSP / attestation crypto  

## 关联

- [../project/PHX-G179_ARCHITECTURE_GATE.md](../project/PHX-G179_ARCHITECTURE_GATE.md)  
- [ADR-0197-openapi-identity-org-status-code-honesty.md](ADR-0197-openapi-identity-org-status-code-honesty.md)  
