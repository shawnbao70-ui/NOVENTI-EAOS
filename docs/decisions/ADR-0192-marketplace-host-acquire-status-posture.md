# ADR-0192 — Marketplace Host-Acquire Status Posture

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G173  
**归属：** Marketplace Gateway  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U046**；PO cue「充分授权…自主开发…加快」

## 背景

G172 交付了 allowlisted `host-acquire` 路由，但 `GET /v1/marketplace/status` 未以产品姿态字段诚实暴露 host-acquire 边界（arbitrary scripts / package install / allowlist）。

## 决策

1. Status 增加只读 `host_acquire_product`：`mode=allowlisted_first_party`；`arbitrary_scripts=false`；`package_install=false`；`external_psp=false`；列出 allowlist 与 route。  
2. Marketplace OpenAPI → `1.2.3`；里程碑字段 `PHX-G173`。  
3. 包仍 `0.2.1`；Alembic 仍 `0029`；不打开 HARD HOLDS。

## Explicit Out

- Expanding allowlist inventively  
- Package install / PSP / Brain / Twin  

## 关联

- [../project/PHX-G173_ARCHITECTURE_GATE.md](../project/PHX-G173_ARCHITECTURE_GATE.md)  
- [ADR-0191-marketplace-listing-host-acquire.md](ADR-0191-marketplace-listing-host-acquire.md)  
