# ADR-0155 — Permission Roles List OpenAPI

**状态：** Accepted  
**日期：** 2026-07-21  
**里程碑：** PHX-G136  
**归属：** API Contracts / Permission boundary

## 背景

G88/G90 已交付只读 `GET /v1/permission/roles`（聚合 catalog / oidc_map / grant_map）。`permission.openapi.yaml` 已有 `/permission/roles/status`，但缺 list 路径。G135 平台声明角色 OpenAPI 与此 tenant 面聚合目录不同。

## 决策

1. 在 `permission.openapi.yaml` 增补 `GET /permission/roles`（v1.1.0）。  
2. 响应 schema 对齐运行时扁平载荷 `{enabled, roles}`（非 `{data:...}` envelope）。  
3. 明确 ≠ Role→grant 自动写入；≠ `/platform/roles` 管理面。  
4. Manifest 仍 13 份；无运行时变更；包 `0.2.0`；Alembic `0029`。

## Explicit Defer

- Role→grant 自动写入 / Role→Policy 绑定  
- Full WebAuthn / MFA registration product page  
- Marketplace 支付清算 / 外部仲裁  
- Foundation `0.2.1` 发布列车  

## 关联

- [ADR-0154-platform-openapi-catalog.md](ADR-0154-platform-openapi-catalog.md)
- [../project/PHX-G136_ARCHITECTURE_GATE.md](../project/PHX-G136_ARCHITECTURE_GATE.md)
