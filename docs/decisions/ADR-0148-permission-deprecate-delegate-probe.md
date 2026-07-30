# ADR-0148 — Permission Deprecate / Delegate Thin Probe

**状态：** Accepted  
**日期：** 2026-07-21  
**里程碑：** PHX-G129  
**归属：** Smart Terminal / Permission

## 背景

G128 已覆盖 Terminal policy create/activate 与 grant create/revoke 手工写入。运维仍缺对既有 policy deprecation 与 grant delegation 的薄调用面。本切片仍**不是** Role→grant 自动写入。

## 决策

1. Terminal Admin 增加 Deprecate policy、Delegate grant。  
2. 仅调用既有 `POST /v1/permission/policies/{id}/deprecation` 与 `POST /v1/permission/grants/{id}/delegations`。  
3. Create grant 可选发送 `delegable` / `delegation_depth`（便于委托探针）；path/id 经独立输入；禁止 body 上下文提升。  
4. 包版本仍 `0.2.0`；Alembic 仍 `0029`。

## Explicit Defer

- Role→grant 自动写入 / Role→Policy 绑定  
- Marketplace 支付清算 / 外部仲裁  
- WebAuthn 注册产品页  
- Foundation `0.2.1` 发布列车  

## 关联

- [ADR-0147-permission-policy-grant-write-probe.md](ADR-0147-permission-policy-grant-write-probe.md)
- [../project/PHX-G129_ARCHITECTURE_GATE.md](../project/PHX-G129_ARCHITECTURE_GATE.md)
