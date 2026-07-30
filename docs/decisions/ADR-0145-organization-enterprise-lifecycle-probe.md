# ADR-0145 — Organization Enterprise Lifecycle Thin Probe

**状态：** Accepted  
**日期：** 2026-07-21  
**里程碑：** PHX-G126  
**归属：** Smart Terminal / Organization

## 背景

G122–G125 已覆盖 Organization 状态、tenant、enterprise create/list、unit/membership 全链路。运维仍缺 Terminal 内对 enterprise suspend / reactivate / close 的薄调用面。

## 决策

1. Terminal Admin 增加 Suspend / Reactivate / Close enterprise。  
2. 仅调用既有 `POST|DELETE /v1/enterprises/{id}/suspension` 与 `DELETE /v1/enterprises/{id}`。  
3. path id / reason / expected_version 经独立输入；禁止 body 上下文提升。  
4. 包版本仍 `0.2.0`；Alembic 仍 `0029`。

## Explicit Defer

- Platform tenant lifecycle Terminal 探针  
- Permission policy/grant 手工写入 Terminal 探针（≠ Role→grant 自动写入）  
- Marketplace 支付清算 / 外部仲裁  
- WebAuthn 注册产品页  
- Foundation `0.2.1` 发布列车  

## 关联

- [ADR-0144-organization-membership-transfer-end-probe.md](ADR-0144-organization-membership-transfer-end-probe.md)
- [../project/PHX-G126_ARCHITECTURE_GATE.md](../project/PHX-G126_ARCHITECTURE_GATE.md)
