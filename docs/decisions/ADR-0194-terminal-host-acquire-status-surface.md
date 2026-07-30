# ADR-0194 — Terminal Host-Acquire Status Surface

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G175  
**归属：** Smart Terminal Admin  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U048**；PO cue「充分授权…自主开发…加快」

## 背景

G173 在 `GET /marketplace/status` 暴露了 `host_acquire_product`，但 Admin UI 仅有通用 JSON 探针，操作者不易一眼确认 allowlist / scripts / install / PSP 边界。

## 决策

1. Terminal Admin 增加 **Host-acquire status (G175)** 与 `#hostAcquireStatus` 摘要行。  
2. `loadHostAcquireStatus` 读取 marketplace status 并渲染 `host_acquire_product`；demo bootstrap 后自动加载。  
3. Host-acquire 成功后刷新摘要行。  
4. 包仍 `0.2.1`；Alembic 仍 `0029`；不打开 HARD HOLDS。

## Explicit Out

- Expanding allowlist  
- Package install / PSP / Brain / Twin  

## 关联

- [../project/PHX-G175_ARCHITECTURE_GATE.md](../project/PHX-G175_ARCHITECTURE_GATE.md)  
- [ADR-0192-marketplace-host-acquire-status-posture.md](ADR-0192-marketplace-host-acquire-status-posture.md)  
