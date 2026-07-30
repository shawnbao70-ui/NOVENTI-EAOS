# PHX-G162 Marketplace Payment Clearing Architecture Gate

**日期：** 2026-07-22  
**状态：** Fully Accepted（Foundation）  
**归属：** API Gateway / Marketplace / Smart Terminal  
**规范源：** ADR-0181  
**授权：** DAL-G007 Eng Explicit Defer `4` PO（DAL-U035）；AED v1.1；cue「继续Eng 4 支付清算」

## 1. 门禁目标

打开 Eng Explicit Defer `4`：命名 payment clearing 表面，**env-gated fail-closed 默认 OFF**（503 stub）；env ON 时仅 **internal audit record**（绑定 invoice；无外部 PSP）；包仍 `0.2.1`；Alembic 仍 `0029`。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Surface kind | Named stub 503 → env-gated internal clearing |
| Helper | `payment_clearing.py` |
| Router | `POST /v1/marketplace/listings/{id}/payment-clearing` |
| Live rail | `Marketplace.InternalPaymentClearing` audit；`external_psp=false` |
| Env | `EAOS_MARKETPLACE_PAYMENT_CLEARING_ENABLED` default false |
| Package / Alembic | Stay `0.2.1` / `0029` |
| Out | External PSP；metering；arbitration；Brain；Twin；Cap→grant |

## 3. Exit Criteria

1. ADR-0181 Accepted。  
2. Gate / Acceptance + helper/router/service/OpenAPI/Terminal + DAL-G007/U035 齐。  
3. `test_api_gateway_g162_*` 与软化后的 G101/G141/tip 合约绿。  

见 [PHX-G162_ACCEPTANCE.md](PHX-G162_ACCEPTANCE.md)。
