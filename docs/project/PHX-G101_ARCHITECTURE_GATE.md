# PHX-G101 Marketplace Status + Listing Thin Probe Architecture Gate

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform API Gateway / Marketplace / Smart Terminal  
**规范源：** ADR-0120  
**人工确认：** 支付清算另批；无自动写 grant / WebAuthn 产品页；无新 Alembic  

## 1. 门禁目标

1. 只读暴露 Marketplace Foundation 商业门禁姿态（payment clearing 等 fail-closed）。  
2. Terminal Admin 对 listing Create / Get 做薄接线。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Status API | `GET /v1/marketplace/status`（只读脱敏） |
| UI | Create listing + Get listing |
| Payment | 仍 fail-closed；不实现清算/仲裁 |
| Out | 支付网关、外部仲裁、完整商业台 |

## 3. Exit Criteria

1. ADR-0120 Accepted。  
2. 契约绿；Terminal 控件绿。  
3. 全量 contracts 绿；包 `0.2.0`；head `0029`。  

见 [PHX-G101_ACCEPTANCE.md](PHX-G101_ACCEPTANCE.md)。
