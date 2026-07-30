# ADR-0160 — Marketplace Foundation Commercial Terminal Probe

**状态：** Accepted  
**日期：** 2026-07-21  
**里程碑：** PHX-G141  
**归属：** Smart Terminal / Marketplace

## 背景

M17 Gateway 已交付 listing pricing / invoice / dispute / revenue-share。Terminal 在 G101–G103 仅覆盖 status/listing/lifecycle/acquire，未接线 Foundation 商业面。支付清算与外部仲裁仍 fail-closed，不在本切片。

## 决策

1. Terminal Admin 增加薄控件：Set pricing、Create invoice、Open/Resolve dispute、Set revenue share。  
2. 仅调用既有 `/v1/marketplace/listings/{id}/pricing|invoices|disputes|revenue-share` 与 `/v1/marketplace/disputes/{id}/resolve`。  
3. UI/文档明确 ≠ 支付清算 / 外部仲裁 / metering。  
4. 无新 Alembic；包 `0.2.0`。

## Explicit Defer

- Marketplace 支付清算 / 外部仲裁 / metering  
- Role→grant 自动写入  
- Full WebAuthn / MFA registration product page  
- Foundation `0.2.1` 发布列车  

## 关联

- [ADR-0054-marketplace-commercial-policy.md](ADR-0054-marketplace-commercial-policy.md)
- [../project/PHX-G141_ARCHITECTURE_GATE.md](../project/PHX-G141_ARCHITECTURE_GATE.md)
