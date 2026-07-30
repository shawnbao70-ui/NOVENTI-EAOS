# ADR-0110 — Terminal Platform Roles Admin Thin Ops

**状态：** Accepted  
**日期：** 2026-07-20  
**里程碑：** PHX-G91  
**归属：** Smart Terminal / Platform API Gateway

## 背景

G90 已交付声明角色 SQL store 与平台 `/v1/platform/roles`。运维仍需在 Smart Terminal Admin 内完成目录薄操作，避免切到外部工具。

## 决策

1. Terminal Admin 增加声明角色 List / Upsert / Disable 薄控件。  
2. 仅调用既有 Gateway 平台角色路径；不新增业务路由；不自动写 grants。  
3. Disable 复用既有 `POST .../{id}/disable`（或等价 `enabled=false` upsert）语义。  
4. 包版本仍 `0.2.0`；Alembic head 仍 `0029`。

## Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批）  
- 自动写 grant / Role→Policy 绑定  
- WebAuthn 注册产品页  
- 批量导入 / 审计 UI  

## 关联

- [ADR-0109-eaos-declared-roles-sql.md](ADR-0109-eaos-declared-roles-sql.md)
- [../project/PHX-G91_ARCHITECTURE_GATE.md](../project/PHX-G91_ARCHITECTURE_GATE.md)
