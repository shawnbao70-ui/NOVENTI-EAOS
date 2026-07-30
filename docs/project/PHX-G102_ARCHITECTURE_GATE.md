# PHX-G102 Marketplace Listing Lifecycle Thin Probe Architecture Gate

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Smart Terminal / Marketplace  
**规范源：** ADR-0121  
**人工确认：** 支付清算另批；无自动写 grant / WebAuthn 产品页；无新 Alembic  

## 1. 门禁目标

Smart Terminal Admin 对既有 listing 技术生命周期（signature → submit → review → publish → revoke）做薄接线；不触碰支付清算。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| UI | Attach signature / Submit / Review approve / Publish / Revoke |
| API | 仅调用既有 `/v1/marketplace/listings/{id}/*` |
| Out | acquire 商业清算、定价/发票 UI、支付网关 |

## 3. Exit Criteria

1. ADR-0121 Accepted。  
2. Terminal 控件与契约绿。  
3. 全量 contracts 绿；包 `0.2.0`；head `0029`。  

见 [PHX-G102_ACCEPTANCE.md](PHX-G102_ACCEPTANCE.md)。
