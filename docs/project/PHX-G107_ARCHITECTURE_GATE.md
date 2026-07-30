# PHX-G107 Workflow Compensate / Escalate Thin Probe Architecture Gate

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Smart Terminal / Workflow  
**规范源：** ADR-0126  
**人工确认：** 支付清算另批；无自动写 grant / WebAuthn 产品页；无新 Alembic  

## 1. 门禁目标

Smart Terminal Admin 对既有 Workflow compensate 与 task escalate 做薄接线；Workflow Terminal 运维面齐。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| UI | Compensate instance / Escalate task |
| API | 仅调用既有 compensation / escalation |
| SoT | Workflow Kernel |
| Out | 支付清算；Package/Knowledge 另域 |

## 3. Exit Criteria

1. ADR-0126 Accepted。  
2. Terminal 控件与契约绿。  
3. 全量 contracts 绿；包 `0.2.0`；head `0029`。  

见 [PHX-G107_ACCEPTANCE.md](PHX-G107_ACCEPTANCE.md)。
