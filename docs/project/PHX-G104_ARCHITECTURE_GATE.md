# PHX-G104 Workflow Status / Definition / Instance Thin Probe Architecture Gate

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Smart Terminal / Workflow  
**规范源：** ADR-0123  
**人工确认：** 支付清算另批；无审批写路径 UI；无自动写 grant / WebAuthn 产品页；无新 Alembic  

## 1. 门禁目标

Smart Terminal Admin 对 Workflow 做状态 + 定义/实例/任务薄接线；审批任务写路径（approve/reject 等）另批。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Status | `GET /v1/workflow/status` 只读；`writable=false` |
| UI | status / create definition / start instance / get instance / list tasks |
| API | 仅调用既有 definitions / instances / tasks |
| Approval SoT | 仍归 Workflow Kernel |
| Out | Terminal approve/reject/signal/cancel；支付清算 |

## 3. Exit Criteria

1. ADR-0123 Accepted。  
2. Terminal 控件与契约绿。  
3. 全量 contracts 绿；包 `0.2.0`；head `0029`。  

见 [PHX-G104_ACCEPTANCE.md](PHX-G104_ACCEPTANCE.md)。
