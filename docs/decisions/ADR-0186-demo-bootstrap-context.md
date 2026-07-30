# ADR-0186 — Demo Bootstrap Context (Dev-Only)

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G167  
**归属：** Demo Gateway / Smart Terminal  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U040**；PO cue「充分授权…自主开发…加快」

## 背景

Demo 双轨已预置租户用户与声明式 packages（G165），但操作者仍需手工粘贴 Subject/Tenant。加速联调需要 dev-only 引导面，且不得污染生产 fail-closed 网关。

## 决策

1. 仅在 `api.gateway.demo` 挂载 `GET /v1/demo/bootstrap`（生产 `api.gateway.app` **不**挂载）。  
2. 响应返回 seeded `subject_id` / `tenant_id`、声明式 surface keys、以及非秘密联调提示；**不**返回凭证/令牌。  
3. Terminal UI boot 时探测该端点：成功则自动填充 Subject/Tenant 并刷新 Package surfaces；404/失败则保持现有手工填写。  
4. 包仍 `0.2.1`；Alembic 仍 `0029`；不打开 HARD HOLDS。

## Explicit Out

- 生产网关挂载 `/v1/demo/*`  
- 返回 secrets / JWT / WebAuthn material  
- Brain execute / Twin authorize  

## 关联

- [../project/PHX-G167_ARCHITECTURE_GATE.md](../project/PHX-G167_ARCHITECTURE_GATE.md)  
- [ADR-0184-terminal-declared-package-surface-projection.md](ADR-0184-terminal-declared-package-surface-projection.md)  
