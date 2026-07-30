# ADR-0142 — Organization Unit / Membership Thin Probe

**状态：** Accepted  
**日期：** 2026-07-21  
**里程碑：** PHX-G123  
**归属：** Smart Terminal / Organization

## 背景

G122 已覆盖 Organization 状态、tenant get 与 enterprise create/list。运维仍缺 Terminal 内对 unit upsert/tree 与 membership add/list 的薄调用面。

## 决策

1. Terminal Admin 增加 Upsert organization unit、Get unit tree、Add/List memberships。  
2. 仅调用既有 `/v1/organization-units`、`/organization-units/tree`、`/memberships`。  
3. path/query id 经独立输入；禁止 body 上下文提升。  
4. Organization Terminal 运维面齐；unit status / membership suspension 另批；包版本仍 `0.2.0`；Alembic 仍 `0029`。

## Explicit Defer

- Organization unit status / membership suspension Terminal 探针  
- Marketplace 支付清算 / 外部仲裁  
- 自动写 grant / WebAuthn 产品页  

## 关联

- [ADR-0141-organization-status-tenant-enterprise-probe.md](ADR-0141-organization-status-tenant-enterprise-probe.md)
- [../project/PHX-G123_ARCHITECTURE_GATE.md](../project/PHX-G123_ARCHITECTURE_GATE.md)
