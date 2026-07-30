# ADR-0205 — OpenAPI Marketplace Status Body Field Parity

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G186  
**归属：** API Gateway / Marketplace / OpenAPI  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U059**；PO cue「充分授权…自主开发…加快」

## 背景

G162/G173 已在 `GET /marketplace/status` 发出稳定的 `payment_clearing_product`、
`host_acquire_product` 与 `foundation_commercial_policy`，但 OpenAPI
`PaymentClearingProduct` / `FoundationStatusData` 仍为宽松 `additionalProperties`
与不完整 required，客户端无法契约核对称发出的 readiness 形状。

## 决策

1. Marketplace OpenAPI **1.2.6**：`PaymentClearingProduct` → emitted field parity
   （`additionalProperties: false`；required 覆盖 G162 emit；`settlement_rail` enum；
   `external_psp` const false）。  
2. `FoundationStatusData` → emitted field parity（含 `foundation_commercial_policy`
   const `v1`；`payment_clearing` enum；host/payment product refs）。  
3. Inventory：`milestone=PHX-G186`；
   `t0188_status=mount_parity_complete_marketplace_status_body_field_parity`。  
4. Ops OpenAPI **1.0.13** 同步 inventory const。  
5. `full_openapi_http_complete` **仍为 false**；external PSP / arbitration /
   Brain / Twin / Cap→grant / attestation crypto 仍关闭。  
6. 包仍 `0.2.1`；Alembic 仍 `0029`。

## Explicit Out

- External PSP capture / refund / settlement  
- External arbitration / subscription metering  
- Full OpenAPI semantic parity  
- Always-on payment clearing without env  

## 关联

- [../project/PHX-G186_ARCHITECTURE_GATE.md](../project/PHX-G186_ARCHITECTURE_GATE.md)  
- [ADR-0181](ADR-0181-marketplace-payment-clearing.md)  
- [ADR-0204](ADR-0204-openapi-auth-permission-product-posture-schema-parity.md)  
