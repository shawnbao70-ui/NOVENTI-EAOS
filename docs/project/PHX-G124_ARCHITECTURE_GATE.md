# PHX-G124 Organization Lifecycle Thin Probe Architecture Gate

**日期：** 2026-07-21  
**状态：** Fully Accepted（Foundation）  
**归属：** Smart Terminal / Organization  
**规范源：** ADR-0143  
**人工确认：** membership transfer/end 另批；支付清算另批；无自动写 grant / WebAuthn 产品页；无新 Alembic  

## 1. 门禁目标

Smart Terminal Admin 对 Organization unit status 与 membership suspend/reactivate 做薄接线。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| UI | Set unit status / Suspend·Reactivate membership |
| API | 仅调用既有 status / suspension 路径 |
| Out | membership transfer/end；支付清算 |

## 3. Exit Criteria

1. ADR-0143 Accepted。  
2. Terminal 控件与契约绿。  
3. 全量 contracts 绿；包 `0.2.0`；head `0029`。  

见 [PHX-G124_ACCEPTANCE.md](PHX-G124_ACCEPTANCE.md)。
