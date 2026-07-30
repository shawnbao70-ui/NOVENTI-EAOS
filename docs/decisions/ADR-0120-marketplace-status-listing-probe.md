# ADR-0120 — Marketplace Status + Listing Thin Probe

**状态：** Accepted  
**日期：** 2026-07-20  
**里程碑：** PHX-G101  
**归属：** Platform API Gateway / Marketplace / Smart Terminal

## 背景

Marketplace 技术/商业 Foundation（G34/M17/M18）已交付，但运维缺少一处只读姿态摘要（尤其 payment clearing 仍暂缓），且 Terminal 尚无 listing 薄操作。

## 决策

1. 新增 `GET /v1/marketplace/status`：脱敏摘要，明确 `payment_clearing` / `external_arbitration` / `metering` = `fail_closed`。  
2. Terminal Admin 增加 Create listing / Get listing 薄控件（既有 `/v1/marketplace/listings`）。  
3. 不实现支付清算或外部仲裁；不升版本；不新增 Alembic。

## Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批）  
- 自动写 grant / Role→Policy 绑定  
- WebAuthn 注册产品页  

## 关联

- [ADR-0054-marketplace-commercial-policy.md](ADR-0054-marketplace-commercial-policy.md)
- [../project/PHX-G101_ARCHITECTURE_GATE.md](../project/PHX-G101_ARCHITECTURE_GATE.md)
