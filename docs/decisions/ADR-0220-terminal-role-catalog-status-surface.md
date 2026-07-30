# ADR-0220 — Terminal Role Catalog Status Surface

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G201  
**归属：** Smart Terminal / Admin  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U074**；PO cue「充分授权…自主开发…加快」

## 背景

G195 已诚实文档化 `RoleCatalogStatus.source_counts`；Admin 仍缺一瞥式 strip
展示 catalog_store / role_count / source_counts 与 Cap≠grant 围栏。

## 决策

1. Operator strip + Refresh CTA（`roleCatalogStatusPosture`）。  
2. Admin CTA **Role catalog status (G201)** + `roleCatalogAdminStatus`。  
3. `loadRoleCatalogStatus` 只读 `GET /permission/roles/status`；摘要
   catalog_store / enabled / roles / grant_map / source_counts / auto_grant /
   mint_ready。  
4. Bootstrap quiet refresh。  
5. **不打开** Cap→grant / always-on mint；包 `0.2.1`；Alembic `0029`。  
6. Inventory 不 bump（对标 G194 UI-only）。

## Explicit Out

- Cap→grant invent / always-on mint  
- HARD HOLD openings  
- Inventory semantic-complete claim  

## 关联

- [../project/PHX-G201_ARCHITECTURE_GATE.md](../project/PHX-G201_ARCHITECTURE_GATE.md)  
