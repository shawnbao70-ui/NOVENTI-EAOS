# ADR-0202 — Terminal Payment-Clearing Status Surface

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G183  
**归属：** Smart Terminal Admin  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U056**；PO cue「充分授权…自主开发…加快」

## 背景

G162 在 `GET /marketplace/status` 暴露了 `payment_clearing_product`（env-gated；`external_psp=false`），Admin 仅有动作按钮与通用 JSON，缺少一瞥式 posture 摘要（对标 G175 host-acquire status）。

## 决策

1. Terminal Admin 增加 **Payment-clearing status (G183)** 与 `#paymentClearingStatus` 摘要行。  
2. `loadPaymentClearingStatus` 渲染 `enabled` / `settlement_rail` / `external_psp=false` / arbitration / metering。  
3. Demo bootstrap 后自动加载（quiet）。  
4. 不打开 external PSP；包仍 `0.2.1`；Alembic 仍 `0029`。

## Explicit Out

- External PSP capture / refund / settlement  
- Always-on clearing without env  
- Brain / Twin / Cap→grant  

## 关联

- [../project/PHX-G183_ARCHITECTURE_GATE.md](../project/PHX-G183_ARCHITECTURE_GATE.md)  
- [ADR-0181](ADR-0181-marketplace-payment-clearing.md)  
