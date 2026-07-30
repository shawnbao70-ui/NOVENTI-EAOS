# PHX-G110 Knowledge Status / Entity Thin Probe Architecture Gate

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Smart Terminal / Knowledge  
**规范源：** ADR-0129  
**人工确认：** 支付清算另批；archive/share/search 另批；无自动写 grant / WebAuthn 产品页；无新 Alembic  

## 1. 门禁目标

Smart Terminal Admin 对 Knowledge 做状态 + entity upsert/get/list 薄接线。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Status | `GET /v1/knowledge/status` 只读 |
| UI | status / upsert / get / list entities |
| API | 仅调用既有 `/entities` |
| Out | archive / share / link / search / provenance；支付清算 |

## 3. Exit Criteria

1. ADR-0129 Accepted。  
2. Terminal 控件与契约绿。  
3. 全量 contracts 绿；包 `0.2.0`；head `0029`。  

见 [PHX-G110_ACCEPTANCE.md](PHX-G110_ACCEPTANCE.md)。
