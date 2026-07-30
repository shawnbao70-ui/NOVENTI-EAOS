# ADR-0144 — Organization Membership Transfer / End Thin Probe

**状态：** Accepted  
**日期：** 2026-07-21  
**里程碑：** PHX-G125  
**归属：** Smart Terminal / Organization

## 背景

G122–G124 已覆盖 Organization 状态、tenant/enterprise、unit/membership CRUD 与 unit status / membership suspend·reactivate。运维仍缺 Terminal 内对 membership transfer unit 与 end 的薄调用面。

## 决策

1. Terminal Admin 增加 Transfer membership unit、End membership。  
2. 仅调用既有 `PUT /v1/memberships/{id}/unit` 与 `DELETE /v1/memberships/{id}`。  
3. path id / `to_org_unit_id` / reason / expected_version 经独立输入；禁止 body 上下文提升。  
4. 包版本仍 `0.2.0`；Alembic 仍 `0029`。

## Explicit Defer

- Marketplace 支付清算 / 外部仲裁  
- 自动写 grant / Role→Policy  
- WebAuthn 注册产品页  
- Foundation `0.2.1` 发布列车  

## 关联

- [ADR-0143-organization-lifecycle-probe.md](ADR-0143-organization-lifecycle-probe.md)
- [../project/PHX-G125_ARCHITECTURE_GATE.md](../project/PHX-G125_ARCHITECTURE_GATE.md)
