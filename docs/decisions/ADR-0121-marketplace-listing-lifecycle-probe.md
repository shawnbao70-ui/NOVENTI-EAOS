# ADR-0121 — Marketplace Listing Lifecycle Thin Probe

**状态：** Accepted  
**日期：** 2026-07-20  
**里程碑：** PHX-G102  
**归属：** Smart Terminal / Marketplace

## 背景

G101 已提供 Marketplace status 与 listing Create/Get。运维仍缺 Terminal 内技术生命周期推进（signature/submit/review/publish/revoke）。

## 决策

1. Terminal Admin 增加 Attach signature、Submit、Review approve、Publish、Revoke 薄控件。  
2. 仅调用既有 listing 生命周期路径；禁止 body 上下文提升。  
3. 不实现支付清算、acquire 商业结算、定价/发票管理台。  
4. 包版本仍 `0.2.0`；Alembic 仍 `0029`。

## Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批）  
- 自动写 grant / Role→Policy 绑定  
- WebAuthn 注册产品页  

## 关联

- [ADR-0120-marketplace-status-listing-probe.md](ADR-0120-marketplace-status-listing-probe.md)
- [../project/PHX-G102_ARCHITECTURE_GATE.md](../project/PHX-G102_ARCHITECTURE_GATE.md)
