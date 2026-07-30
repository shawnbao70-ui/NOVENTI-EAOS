# PHX-G105 Workflow Task Approve / Reject Thin Probe Architecture Gate

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Smart Terminal / Workflow  
**规范源：** ADR-0124  
**人工确认：** 支付清算另批；signal/cancel 另批；无自动写 grant / WebAuthn 产品页；无新 Alembic  

## 1. 门禁目标

Smart Terminal Admin 对既有 Workflow 任务 approve/reject 做薄接线；审批真相仍归 Kernel。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| UI | Approve / Reject workflow task |
| API | 仅调用既有 approval / rejection |
| SoT | Workflow Kernel |
| Out | signal / cancel / compensate / escalate；支付清算 |

## 3. Exit Criteria

1. ADR-0124 Accepted。  
2. Terminal 控件与契约绿。  
3. 全量 contracts 绿；包 `0.2.0`；head `0029`。  

见 [PHX-G105_ACCEPTANCE.md](PHX-G105_ACCEPTANCE.md)。
