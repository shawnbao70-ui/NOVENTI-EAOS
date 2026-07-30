# ADR-0147 — Permission Policy / Grant Manual Write Thin Probe

**状态：** Accepted  
**日期：** 2026-07-21  
**里程碑：** PHX-G128  
**归属：** Smart Terminal / Permission

## 背景

G94–G95 已覆盖 Terminal permission evaluate / explain / effective-permissions 只读面。运维仍缺对既有 `POST /v1/permission/policies*` 与 `POST /v1/permission/grants*` 的手工薄调用面。本切片**不是** Role→grant 自动写入。

## 决策

1. Terminal Admin 增加 Create policy、Activate policy、Create grant、Revoke grant。  
2. 仅调用既有 `/v1/permission/policies`、`/policies/{id}/activation`、`/grants`、`/grants/{id}/revocation`。  
3. path/query id 与业务字段经独立输入；禁止 body 上下文提升；不下发 Role→grant map。  
4. Deprecate / Delegate 另批；包版本仍 `0.2.0`；Alembic 仍 `0029`。

## Explicit Defer

- Policy deprecation / grant delegation Terminal 探针  
- Role→grant 自动写入 / Role→Policy 绑定  
- Marketplace 支付清算 / 外部仲裁  
- WebAuthn 注册产品页  
- Foundation `0.2.1` 发布列车  

## 关联

- [ADR-0146-platform-tenant-lifecycle-probe.md](ADR-0146-platform-tenant-lifecycle-probe.md)
- [../project/PHX-G128_ARCHITECTURE_GATE.md](../project/PHX-G128_ARCHITECTURE_GATE.md)
