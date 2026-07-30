# PHX-G112 Knowledge Link / Provenance Thin Probe Architecture Gate

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Smart Terminal / Knowledge  
**规范源：** ADR-0131  
**人工确认：** 支付清算另批；无自动写 grant / WebAuthn 产品页；无新 Alembic  

## 1. 门禁目标

Smart Terminal Admin 对 Knowledge link/provenance 做薄接线；Knowledge Terminal 运维面齐。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| UI | Create link / Get provenance |
| API | 仅调用既有 links / provenance |
| Out | 支付清算；Twin/Brain 另域 |

## 3. Exit Criteria

1. ADR-0131 Accepted。  
2. Terminal 控件与契约绿。  
3. 全量 contracts 绿；包 `0.2.0`；head `0029`。  

见 [PHX-G112_ACCEPTANCE.md](PHX-G112_ACCEPTANCE.md)。
