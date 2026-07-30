# ADR-0122 — Marketplace Acquire Technical Thin Probe

**状态：** Accepted  
**日期：** 2026-07-20  
**里程碑：** PHX-G103  
**归属：** Smart Terminal / Marketplace

## 背景

G101–G102 已覆盖 Marketplace status 与 listing 技术生命周期。运维仍缺 Terminal 内对技术 acquire（租户获取已发布 listing）的薄调用面。支付清算仍明确暂缓。

## 决策

1. Terminal Admin 增加「Acquire listing」薄控件。  
2. 仅调用既有 `POST /v1/marketplace/listings/{listing_id}/acquire`。  
3. acquire 保持技术语义；不接入支付网关或清算。  
4. 包版本仍 `0.2.0`；Alembic 仍 `0029`。

## Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批）  
- 自动写 grant / Role→Policy 绑定  
- WebAuthn 注册产品页  

## 关联

- [ADR-0120-marketplace-status-listing-probe.md](ADR-0120-marketplace-status-listing-probe.md)
- [ADR-0121-marketplace-listing-lifecycle-probe.md](ADR-0121-marketplace-listing-lifecycle-probe.md)
- [../project/PHX-G103_ARCHITECTURE_GATE.md](../project/PHX-G103_ARCHITECTURE_GATE.md)
