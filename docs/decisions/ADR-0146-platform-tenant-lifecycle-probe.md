# ADR-0146 — Platform Tenant Lifecycle Thin Probe

**状态：** Accepted  
**日期：** 2026-07-21  
**里程碑：** PHX-G127  
**归属：** Smart Terminal / Platform Organization

## 背景

G25 已交付平台面 `POST /v1/platform/tenants` 与 suspension API；G122–G126 覆盖租户面 Organization Terminal。运维仍缺 Terminal Admin 对平台租户 create / suspend / reactivate 的薄调用面。

## 决策

1. Terminal Admin 增加 Create platform tenant、Suspend / Reactivate platform tenant。  
2. 仅调用既有 `/v1/platform/tenants` 与 `/v1/platform/tenants/{id}/suspension`。  
3. 使用 `platform: true` 上下文（不下发 Tenant 头）；path id / legal_name / reason / expected_version 经独立输入；禁止 body 上下文提升。  
4. 包版本仍 `0.2.0`；Alembic 仍 `0029`。

## Explicit Defer

- Permission policy/grant 手工写入 Terminal 探针（≠ Role→grant 自动写入）  
- Marketplace 支付清算 / 外部仲裁  
- WebAuthn 注册产品页  
- Foundation `0.2.1` 发布列车  

## 关联

- [ADR-0145-organization-enterprise-lifecycle-probe.md](ADR-0145-organization-enterprise-lifecycle-probe.md)
- [../project/PHX-G127_ARCHITECTURE_GATE.md](../project/PHX-G127_ARCHITECTURE_GATE.md)
