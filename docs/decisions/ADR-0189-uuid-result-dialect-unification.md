# ADR-0189 — UuidResult Dialect Unification

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G170  
**归属：** API Gateway / OpenAPI  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U043**；PO cue「充分授权…自主开发…加快」

## 背景

G166 诚实记录 UuidResult 双方言（`{id}` vs `{data}`）并 defer 强制统一。跨域客户端与 SDK 需要单一可依赖形状，同时不得破坏既有 Terminal/Package（读 `data`）与 Permission/Knowledge（读 `id`）调用方。

## 决策

1. 引入共享 `api.gateway.serializers.common.uuid_result`：始终同时返回 `id` 与 `data`（同值 UUID）；AI/Event 保留 `ok: true`。  
2. 各域 OpenAPI `UuidResult` 合同改为 `required: [id, data]`（或 `[ok, id, data]`）。  
3. Inventory：`milestone=PHX-G170`；`t0188_status=mount_parity_complete_uuid_result_unified`；移除 defer fence `uuid_result_dialect_unification`。  
4. `full_openapi_http_complete` **仍为 false**（其余语义缺口保留）。  
5. 包仍 `0.2.1`；Alembic 仍 `0029`；不打开 HARD HOLDS。

## Explicit Out

- 删除任一既有键（破坏性）  
- 声称 full OpenAPI semantic parity 完成  
- Brain execute / Twin authorize / Cap→grant / external PSP  

## 关联

- [../project/PHX-G170_ARCHITECTURE_GATE.md](../project/PHX-G170_ARCHITECTURE_GATE.md)  
- [ADR-0185-openapi-semantic-remainder-deepen.md](ADR-0185-openapi-semantic-remainder-deepen.md)  
