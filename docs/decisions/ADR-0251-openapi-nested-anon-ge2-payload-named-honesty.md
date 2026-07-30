# ADR-0251 — OpenAPI Nested-Anon ≥2 Payload Named Honesty

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G232  
**归属：** OpenAPI Inventory / AI / Ops  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U105**；PO cue「充分授权…自主开发…加快」

## 背景

G230 关闭 federation matrix 后，nested anonymous object ≥2 props 仍余：
ToolInvocationResult.data、HealthEnvelope.data、AdaptersEnvelope.meta、
ContextEchoEnvelope.data。

## 决策

1. 新增 `ToolInvocationPayload` / `HealthPayload` / `AdaptersMeta` / `ContextEchoPayload`。  
2. ai **1.0.7**；ops **1.0.42**。  
3. Inventory `milestone=PHX-G232`；
   `t0188_status=mount_parity_complete_nested_anon_ge2_payload_named_honest`。  
4. `full_openapi_http_complete=false`；包 `0.2.1`；Alembic `0029`。

## Explicit Out

- Handler invent / Brain execute  
- Semantic-complete claim  
- HARD HOLD openings  
