# ADR-0257 — OpenAPI DiscoveryRegistryWritePosture Named Honesty

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G238  
**归属：** OpenAPI Inventory / Auth / Platform  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U111**；PO cue「充分授权…自主开发…加快」

## 背景

`IdpRegistryStatusPosture.discovery_write` 与 `DiscoverySyncEnvelope.data` 仍为
opaque object，而 live emit（`maybe_write_discovery_to_registry`）键已稳定。

## 决策

1. 新增 `DiscoveryRegistryWritePosture`（auth + platform 各一份同形 schema）。  
2. auth discovery_write → anyOf `$ref` | null；platform data → `$ref`。  
3. auth **1.3.23**；platform **1.0.9**；ops **1.0.45**；inventory PHX-G238。  
4. `full_openapi_http_complete=false`；包 `0.2.1`；Alembic `0029`。

## Explicit Out

ContextEcho.echo / free-form payload invent；HARD HOLD openings。  
