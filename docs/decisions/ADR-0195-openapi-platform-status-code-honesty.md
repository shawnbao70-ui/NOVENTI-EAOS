# ADR-0195 — OpenAPI Platform IdP/Roles Status-Code Honesty

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G176  
**归属：** API Gateway / OpenAPI  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U049**；PO cue「充分授权…自主开发…加快」

## 背景

G174 已对齐 platform KernelError→GatewayDetailError，但 IdP/roles 写路径的 **404/400/409/503** 仍多落在 `default`，与路由已发出的命名状态码不一致。

## 决策

1. Platform OpenAPI（`1.0.2`）为 roles upsert/disable、IdP create/disable、federation create/unbind/priority 文档化真实 **400/404/409/503**（GatewayDetailError）。  
2. Inventory：`milestone=PHX-G176`；`t0188_status=mount_parity_complete_platform_status_codes_honest`。  
3. `full_openapi_http_complete` **仍为 false**。  
4. 包仍 `0.2.1`；Alembic 仍 `0029`；不打开 HARD HOLDS。

## Explicit Out

- Full OpenAPI semantic parity  
- Auth OIDC/Identity 全矩阵 status-code（下一切片候选）  
- Brain / Twin / PSP / attestation crypto  

## 关联

- [../project/PHX-G176_ARCHITECTURE_GATE.md](../project/PHX-G176_ARCHITECTURE_GATE.md)  
- [ADR-0193-openapi-auth-marketplace-platform-detail.md](ADR-0193-openapi-auth-marketplace-platform-detail.md)  
