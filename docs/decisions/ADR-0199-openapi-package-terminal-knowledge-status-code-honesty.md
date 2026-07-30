# ADR-0199 — OpenAPI Package/Terminal/Knowledge Status-Code Honesty

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G180  
**归属：** API Gateway / OpenAPI  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U053**；PO cue「充分授权…自主开发…加快」

## 背景

G176–G179 诚实化 Platform/Auth OIDC/Identity/Org/Permission/Workflow 命名状态码。Package、Terminal、Knowledge 写读路径真实 **400/403/404/409/503** 仍多落在 `default`。

## 决策

1. Package（`1.0.3`）、Terminal（`1.1.3`）、Knowledge（`1.0.3`）OpenAPI 为主要写/读路径文档化真实命名状态码（GatewayDetailError）。  
2. Inventory：`milestone=PHX-G180`；`t0188_status=mount_parity_complete_package_terminal_knowledge_status_codes_honest`。  
3. `full_openapi_http_complete` **仍为 false**（AI/Event/Brain/Marketplace remainder 等）。  
4. 包仍 `0.2.1`；Alembic 仍 `0029`；不打开 HARD HOLDS。

## Explicit Out

- Full OpenAPI semantic parity  
- Brain execute / Twin authorize / external PSP / attestation crypto  

## 关联

- [../project/PHX-G180_ARCHITECTURE_GATE.md](../project/PHX-G180_ARCHITECTURE_GATE.md)  
- [ADR-0198-openapi-permission-workflow-status-code-honesty.md](ADR-0198-openapi-permission-workflow-status-code-honesty.md)  
