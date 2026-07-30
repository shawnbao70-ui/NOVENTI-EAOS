# ADR-0203 — Terminal OpenAPI Inventory Posture Deepen

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G184  
**归属：** Smart Terminal  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U057**；PO cue「充分授权…自主开发…加快」

## 背景

G148–G181 已让 `openapi_inventory_product` 携带 `milestone` / `t0188_status`，但 Terminal 摘要行仍只显示 contract count 与布尔旗，操作者无法一眼确认当前 honesty tip。

## 决策

1. `loadOpenapiInventoryProductPosture` 渲染 **milestone + t0188_status** 与既有 mount/full flags。  
2. 增加 **Refresh OpenAPI inventory (G184)** CTA。  
3. 不宣称 `full_openapi_http_complete=true`；包仍 `0.2.1`；Alembic 仍 `0029`。

## Explicit Out

- Full OpenAPI semantic parity  
- HARD HOLD openings  

## 关联

- [../project/PHX-G184_ARCHITECTURE_GATE.md](../project/PHX-G184_ARCHITECTURE_GATE.md)  
