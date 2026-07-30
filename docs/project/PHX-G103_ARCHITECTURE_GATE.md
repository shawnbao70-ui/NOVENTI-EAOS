# PHX-G103 Marketplace Acquire Technical Thin Probe Architecture Gate

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Smart Terminal / Marketplace  
**规范源：** ADR-0122  
**人工确认：** 支付清算另批；无自动写 grant / WebAuthn 产品页；无新 Alembic  

## 1. 门禁目标

Smart Terminal Admin 对既有技术面 `POST /v1/marketplace/listings/{id}/acquire` 做薄接线；不实现支付清算。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| UI | Acquire listing（技术获取） |
| API | 仅调用既有 acquire |
| Payment | 仍 fail-closed；acquire ≠ 支付清算 |
| Out | 支付网关、外部仲裁、发票清算 UI |

## 3. Exit Criteria

1. ADR-0122 Accepted。  
2. Terminal 控件与契约绿。  
3. 全量 contracts 绿；包 `0.2.0`；head `0029`。  

见 [PHX-G103_ACCEPTANCE.md](PHX-G103_ACCEPTANCE.md)。
