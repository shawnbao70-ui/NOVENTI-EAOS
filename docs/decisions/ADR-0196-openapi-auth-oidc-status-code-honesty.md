# ADR-0196 — OpenAPI Auth OIDC Status-Code Honesty

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G177  
**归属：** API Gateway / OpenAPI  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U050**；PO cue「充分授权…自主开发…加快」

## 背景

G174 对齐 Auth KernelError→GatewayDetailError，G176 诚实化 Platform 写路径命名状态码；Auth OIDC login/callback/refresh/logout 仍有真实 **400/401/403/502/503** 落在 `default`，或 503 仍引用旧 `ErrorResponse`。

## 决策

1. Auth OpenAPI（`1.3.8`）为 OIDC login/callback/refresh/logout 文档化真实命名状态码（GatewayDetailError）。  
2. Inventory：`milestone=PHX-G177`；`t0188_status=mount_parity_complete_auth_oidc_status_codes_honest`。  
3. `full_openapi_http_complete` **仍为 false**。  
4. 包仍 `0.2.1`；Alembic 仍 `0029`；不打开 HARD HOLDS。

## Explicit Out

- Full OpenAPI semantic parity  
- WebAuthn attestation crypto / Brain / Twin / external PSP  
- Identity/Organization 全矩阵 status-code（下一切片候选）

## 关联

- [../project/PHX-G177_ARCHITECTURE_GATE.md](../project/PHX-G177_ARCHITECTURE_GATE.md)  
- [ADR-0195-openapi-platform-status-code-honesty.md](ADR-0195-openapi-platform-status-code-honesty.md)  
