# PHX-G129 Permission Deprecate / Delegate Thin Probe Architecture Gate

**日期：** 2026-07-21  
**状态：** Fully Accepted（Foundation）  
**归属：** Smart Terminal / Permission  
**规范源：** ADR-0148  
**人工确认：** 非 Role→grant 自动写入；支付清算另批；无 WebAuthn 产品页；无新 Alembic；包仍 `0.2.0`  

## 1. 门禁目标

Smart Terminal Admin 对 Permission policy deprecate 与 grant delegate 做手工薄接线。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| UI | Deprecate policy；Delegate grant |
| API | 仅调用既有 deprecation / delegations |
| Fence | ≠ Role→grant 自动写入 |
| Out | Role→grant；支付清算；`0.2.1` |

## 3. Exit Criteria

1. ADR-0148 Accepted。  
2. Terminal 控件与契约绿。  
3. 全量 contracts 绿；包 `0.2.0`；head `0029`。  

见 [PHX-G129_ACCEPTANCE.md](PHX-G129_ACCEPTANCE.md)。
