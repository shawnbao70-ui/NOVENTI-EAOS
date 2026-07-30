# ADR-0200 — OpenAPI AI/Event/Brain/Marketplace Status-Code Honesty

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G181  
**归属：** API Gateway / OpenAPI  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U054**；PO cue「充分授权…自主开发…加快」

## 背景

G176–G180 诚实化多数 Foundation 域命名状态码。AI、Event、Brain/Twin、Marketplace 写读路径真实 **400/403/404/409/503** 仍多落在 `default`（Brain execute / Twin authorize 已有 fail-closed 403 除外）。

## 决策

1. AI `1.0.3`、Event `1.0.3`、Brain `1.0.3`、Marketplace `1.2.5` 文档化真实命名状态码（GatewayDetailError）。  
2. Twin authorize / Brain execute 保持 fail-closed **403**（HARD HOLD；本切片仅补 503）。  
3. Inventory：`milestone=PHX-G181`；`t0188_status=mount_parity_complete_ai_event_brain_marketplace_status_codes_honest`。  
4. `full_openapi_http_complete` **仍为 false**。  
5. 包仍 `0.2.1`；Alembic 仍 `0029`；不打开 HARD HOLDS。

## Explicit Out

- Opening Brain execute / Twin authorize  
- External PSP / attestation crypto / Cap→grant invent  

## 关联

- [../project/PHX-G181_ARCHITECTURE_GATE.md](../project/PHX-G181_ARCHITECTURE_GATE.md)  
- [ADR-0199-openapi-package-terminal-knowledge-status-code-honesty.md](ADR-0199-openapi-package-terminal-knowledge-status-code-honesty.md)  
