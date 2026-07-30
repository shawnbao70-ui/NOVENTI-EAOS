# ADR-0111 — Terminal Tenant Roles Catalog Read

**状态：** Accepted  
**日期：** 2026-07-20  
**里程碑：** PHX-G92  
**归属：** Smart Terminal / Permission

## 背景

G88/G90 提供租户只读聚合 `GET /v1/permission/roles`；G91 提供平台声明角色写操作。运维仍缺 Terminal 内租户面目录只读探针。

## 决策

1. Terminal Admin 增加「List tenant roles catalog」薄按钮。  
2. 使用租户受信上下文调用既有 `/v1/permission/roles`（`platform: false`）。  
3. 不新增写路径；不自动写 grants；不升版本；不新增 Alembic。

## Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批）  
- 自动写 grant / Role→Policy 绑定  
- WebAuthn 注册产品页  

## 关联

- [ADR-0107-eaos-roles-catalog.md](ADR-0107-eaos-roles-catalog.md)
- [ADR-0110-terminal-roles-admin.md](ADR-0110-terminal-roles-admin.md)
- [../project/PHX-G92_ARCHITECTURE_GATE.md](../project/PHX-G92_ARCHITECTURE_GATE.md)
