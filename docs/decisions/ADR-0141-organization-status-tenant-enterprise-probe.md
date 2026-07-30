# ADR-0141 — Organization Status / Tenant / Enterprise Thin Probe

**状态：** Accepted  
**日期：** 2026-07-21  
**里程碑：** PHX-G122  
**归属：** Smart Terminal / Organization

## 背景

G21 已交付 Organization HTTP（tenant/enterprise/unit/membership）。运维仍缺 Terminal 内对状态、tenant get 与 enterprise create/list 的薄调用面。

## 决策

1. 新增只读 `GET /v1/organization/status`（`writable=false` 与支持面声明）。  
2. Terminal Admin 增加 Organization status、Get organization tenant、Create/List enterprises。  
3. Tenant path id 取自既有 Tenant 输入（与 trusted header 一致）；禁止 body 上下文提升。  
4. Unit / membership Terminal 探针另批；包版本仍 `0.2.0`；Alembic 仍 `0029`。

## Explicit Defer

- Organization unit / membership Terminal 薄探针  
- Marketplace 支付清算 / 外部仲裁  
- 自动写 grant / WebAuthn 产品页  

## 关联

- [ADR-0140-identity-credential-session-probe.md](ADR-0140-identity-credential-session-probe.md)
- [../project/PHX-G122_ARCHITECTURE_GATE.md](../project/PHX-G122_ARCHITECTURE_GATE.md)
