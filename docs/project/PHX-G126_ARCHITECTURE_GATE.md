# PHX-G126 Organization Enterprise Lifecycle Thin Probe Architecture Gate

**日期：** 2026-07-21  
**状态：** Fully Accepted（Foundation）  
**归属：** Smart Terminal / Organization  
**规范源：** ADR-0145  
**人工确认：** 支付清算另批；无自动写 grant / WebAuthn 产品页；无新 Alembic；包仍 `0.2.0`  

## 1. 门禁目标

Smart Terminal Admin 对 Organization enterprise suspend / reactivate / close 做薄接线。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| UI | Suspend / Reactivate / Close enterprise |
| API | 仅调用既有 enterprises suspension / DELETE |
| Out | platform tenant lifecycle；permission write；支付清算 |

## 3. Exit Criteria

1. ADR-0145 Accepted。  
2. Terminal 控件与契约绿。  
3. 全量 contracts 绿；包 `0.2.0`；head `0029`。  

见 [PHX-G126_ACCEPTANCE.md](PHX-G126_ACCEPTANCE.md)。
