# ADR-0245 — OpenAPI HostAcquirePayload Named Honesty

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G226  
**归属：** OpenAPI Inventory / Marketplace  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U099**；PO cue「充分授权…自主开发…加快」

## 背景

`HostAcquireResult.data` 仍为 nested anonymous object。Live emit keys 已稳定
（host_acquire），应提升为 named `HostAcquirePayload` `$ref`。

## 决策

1. 新增 `HostAcquirePayload`；`HostAcquireResult.data` → `$ref`。  
2. marketplace **1.2.11**。  
3. Inventory `milestone=PHX-G226`；
   `t0188_status=mount_parity_complete_host_acquire_payload_named_honest`；ops **1.0.39**。  
4. `full_openapi_http_complete=false`；包 `0.2.1`；Alembic `0029`。

## Explicit Out

- Host-acquire behavior invent / non-allowlist catalog  
- Semantic-complete claim  
- HARD HOLD openings  

## 关联

- [../project/PHX-G226_ARCHITECTURE_GATE.md](../project/PHX-G226_ARCHITECTURE_GATE.md)  
