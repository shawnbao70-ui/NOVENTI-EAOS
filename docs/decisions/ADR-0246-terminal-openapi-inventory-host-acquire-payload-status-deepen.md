# ADR-0246 — Terminal OpenAPI Inventory HostAcquirePayload Status Deepen

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G227  
**归属：** Smart Terminal / OpenAPI Inventory UI  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U100**；PO cue「充分授权…自主开发…加快」

## 背景

G226 将 HostAcquireResult.data 提升为 named HostAcquirePayload。Terminal strip
需表面化该标记，且不 bump inventory。

## 决策

1. Admin CTA + strip 标记 G227 / host acquire payload named honest。  
2. Bootstrap quiet refresh 保持。  
3. Inventory 不 bump（仍为 G226 / ops 1.0.39）。  
4. 包 `0.2.1`；Alembic `0029`。

## Explicit Out

- Inventory bump  
- HARD HOLD openings  

## 关联

- [../project/PHX-G227_ARCHITECTURE_GATE.md](../project/PHX-G227_ARCHITECTURE_GATE.md)  
