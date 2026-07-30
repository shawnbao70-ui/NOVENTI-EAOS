# ADR-0143 — Organization Lifecycle Thin Probe

**状态：** Accepted  
**日期：** 2026-07-21  
**里程碑：** PHX-G124  
**归属：** Smart Terminal / Organization

## 背景

G122–G123 已覆盖 Organization 状态、tenant/enterprise、unit upsert/tree 与 membership add/list。运维仍缺 Terminal 内对 unit status 与 membership suspend/reactivate 的薄调用面。

## 决策

1. Terminal Admin 增加 Set organization unit status、Suspend/Reactivate membership。  
2. 仅调用既有 `PUT /v1/organization-units/{id}/status` 与 `POST|DELETE /v1/memberships/{id}/suspension`。  
3. path id / reason / expected_version 经独立输入；禁止 body 上下文提升。  
4. membership transfer / end 另批；包版本仍 `0.2.0`；Alembic 仍 `0029`。

## Explicit Defer

- Membership transfer / end Terminal 探针  
- Marketplace 支付清算 / 外部仲裁  
- 自动写 grant / WebAuthn 产品页  

## 关联

- [ADR-0142-organization-unit-membership-probe.md](ADR-0142-organization-unit-membership-probe.md)
- [../project/PHX-G124_ARCHITECTURE_GATE.md](../project/PHX-G124_ARCHITECTURE_GATE.md)
