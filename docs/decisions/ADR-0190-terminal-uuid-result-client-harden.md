# ADR-0190 — Terminal UuidResult Dual-Key Client Harden

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G171  
**归属：** Smart Terminal UI  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U044**；PO cue「充分授权…自主开发…加快」

## 背景

G170 将 Gateway UuidResult 统一为双键 `{id,data}`。Terminal UI 多数路径只读 `data`，需显式兼容 `id`，避免未来仅一侧存在时联调断裂。

## 决策

1. 引入 `uuidFromResult(payload)`：优先 `id`，回退 `data`。  
2. Operator / Admin / Extensions 创建类 UuidResult 赋值改用该助手。  
3. 包仍 `0.2.1`；Alembic 仍 `0029`；不打开 HARD HOLDS。

## Explicit Out

- Marketplace listing→host acquire  
- Brain execute / Twin authorize  

## 关联

- [../project/PHX-G171_ARCHITECTURE_GATE.md](../project/PHX-G171_ARCHITECTURE_GATE.md)  
- [ADR-0189-uuid-result-dialect-unification.md](ADR-0189-uuid-result-dialect-unification.md)  
