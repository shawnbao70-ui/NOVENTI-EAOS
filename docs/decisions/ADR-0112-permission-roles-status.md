# ADR-0112 — Permission Roles Status Observability

**状态：** Accepted  
**日期：** 2026-07-20  
**里程碑：** PHX-G93  
**归属：** Platform API Gateway / Permission

## 背景

G83/G88/G90 已交付 grant map 与角色目录；运维缺少一处只读摘要（store 模式、是否启用 map、角色计数）。`/v1/permission/roles` 返回完整聚合行，不适合作为轻量探针。

## 决策

1. 新增 `GET /v1/permission/roles/status`（租户受信上下文）。  
2. 返回脱敏摘要：`catalog_store`、`catalog_enabled`、`role_count`、`grant_map_enabled`、`grant_map_role_count`、按 source 计数。  
3. 不返回原始 `EAOS_PERMISSION_ROLE_GRANT_MAP` 字符串；不写 grants。  
4. Terminal Admin 增加「Roles status」薄按钮。  
5. 包版本仍 `0.2.0`；Alembic 仍 `0029`。

## Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批）  
- 自动写 grant / Role→Policy 绑定  
- WebAuthn 注册产品页  

## 关联

- [ADR-0102-permission-role-grant-map.md](ADR-0102-permission-role-grant-map.md)
- [ADR-0107-eaos-roles-catalog.md](ADR-0107-eaos-roles-catalog.md)
- [ADR-0111-terminal-tenant-roles-catalog-read.md](ADR-0111-terminal-tenant-roles-catalog-read.md)
- [../project/PHX-G93_ARCHITECTURE_GATE.md](../project/PHX-G93_ARCHITECTURE_GATE.md)
