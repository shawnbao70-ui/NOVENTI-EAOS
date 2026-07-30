# PHX-G111 Knowledge Archive / Share / Search Thin Probe Architecture Gate

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Smart Terminal / Knowledge  
**规范源：** ADR-0130  
**人工确认：** 支付清算另批；link/provenance 另批；无自动写 grant / WebAuthn 产品页；无新 Alembic  

## 1. 门禁目标

Smart Terminal Admin 对 Knowledge archive/share/search 做薄接线。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| UI | Archive / Share entity / Search |
| API | 仅调用既有 archive / share / search |
| Out | link / provenance；支付清算 |

## 3. Exit Criteria

1. ADR-0130 Accepted。  
2. Terminal 控件与契约绿。  
3. 全量 contracts 绿；包 `0.2.0`；head `0029`。  

见 [PHX-G111_ACCEPTANCE.md](PHX-G111_ACCEPTANCE.md)。
