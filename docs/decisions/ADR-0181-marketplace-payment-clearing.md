# ADR-0181 — Marketplace Payment Clearing (Eng Explicit Defer `4`)

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G162  
**归属：** API Gateway / Marketplace / Smart Terminal  
**授权：** **DAL-G007**（PO Eng Explicit Defer `4`）+ DAL-G003 + DAL-G004；Usage **DAL-U035**；cue「继续Eng 4 支付清算」

## 背景

Eng Explicit Defer `4`（Marketplace payment clearing）在 G144–G159 tip boards 上一直 **暂缓（always PO）**。G101/G141 仅声明 `payment_clearing=fail_closed`。PO cue「继续Eng 4 支付清算」打开本切片。不得发明外部支付网关；加深仓库已 defer 的 clearing 边界。

ID 协调：PHX-G161 / ADR-0179 / DAL-G006 = Role→grant mint；PHX-G163 / ADR-0180 = T2/T3 intake；本切片 = **PHX-G162 / ADR-0181 / DAL-G007 / DAL-U035**。

## 决策

1. 新增 helper `api/gateway/payment_clearing.py`：env `EAOS_MARKETPLACE_PAYMENT_CLEARING_ENABLED` **默认 false**；统一 503 + `GATEWAY_PAYMENT_CLEARING_DISABLED`（detail 含 `clearing_step` / `payment_cleared=false` / `external_psp=false`）。  
2. 新增路由 `POST /v1/marketplace/listings/{listing_id}/payment-clearing`：默认 503；env ON 时调用 `MarketplaceService.record_internal_payment_clearing`（审计背书的 **internal record**，绑定已签发 invoice；**无**外部 PSP）。  
3. `GET /v1/marketplace/status` 暴露 `payment_clearing_product`（里程碑 **PHX-G162**）与 `payment_clearing`=`fail_closed`|`internal_env_gated`。  
4. OpenAPI `marketplace.openapi.yaml` → **1.2.0**；inventory fence 从 `marketplace_payment_clearing` 改为 `marketplace_payment_external_psp_and_arbitration`。  
5. Terminal 薄行同步 stub/env 文案。  
6. **不**新增 Alembic；包仍 `0.2.1`；外部 PSP / 计量 / 外部仲裁仍 fail-closed。

## Explicit Out（本切片不开口）

- External PSP capture / refund / settlement rails  
- Subscription metering / external arbitration  
- Brain execute / Twin authorize  
- Cap→grant invent；Const/BP rewrite；新 Alembic  
- 不回归并行 G160 WebAuthn / G161 Role→grant / G163 Research intake  

## 后果

- Eng `4` 以 **env-gated stub→internal live** 打开；默认 fail-closed。  
- Natural Pause 的 Eng `4` PO resume gate 已行使；其余 Held（Brain/Twin/external PSP）仍关闭。

## 关联

- [../project/PHX-G162_ARCHITECTURE_GATE.md](../project/PHX-G162_ARCHITECTURE_GATE.md)  
- [../project/PHX-G162_ACCEPTANCE.md](../project/PHX-G162_ACCEPTANCE.md)  
- [ADR-0054-marketplace-commercial-policy.md](ADR-0054-marketplace-commercial-policy.md)  
- [ADR-0120-marketplace-status-listing-probe.md](ADR-0120-marketplace-status-listing-probe.md)  
- [../project/DELEGATED_AUTHORITY_LEDGER.md](../project/DELEGATED_AUTHORITY_LEDGER.md)  
