# ADR-0212 — OpenAPI Package/Terminal/Event Status Mount Parity

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G193  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U066**；PO cue「充分授权…自主开发…加快」

## 决策

1. Package OpenAPI **1.0.4**：`FoundationStatusData` field parity。  
2. Terminal OpenAPI **1.1.4**：`GET /terminal/status` + FoundationStatus schemas。  
3. Event OpenAPI **1.0.4**：`GET /events/status` + FoundationStatus schemas。  
4. Gateway routers mount matching thin status handlers.  
5. Inventory：`milestone=PHX-G193`；ops **1.0.20**。  
6. `full_openapi_http_complete=false`；包 `0.2.1`；Alembic `0029`。

## Explicit Out

- Arbitrary extension script execution  
- HARD HOLD openings  
