# PHX-G140 Terminal Ops Echo + Workflow Deprecation Architecture Gate

**日期：** 2026-07-21  
**状态：** Fully Accepted（Foundation）  
**归属：** Smart Terminal  
**规范源：** ADR-0159  
**人工确认：** 仅薄接线既有 API；无 Alembic/版本 bump  

## 1. 门禁目标

补齐 Terminal 对 Ops context echo 与 Workflow definition deprecation 的薄运维控件。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Echo | POST `/v1/context/echo`；elevation → 期望 400 |
| Workflow | POST `/v1/workflow/definitions/{id}/deprecation` |
| Out | Role→grant；WebAuthn；支付清算；`0.2.1` |

## 3. Exit Criteria

1. ADR-0159 Accepted。  
2. Terminal + 契约绿。  
3. 全量 contracts 绿；包 `0.2.0`；head `0029`。  

见 [PHX-G140_ACCEPTANCE.md](PHX-G140_ACCEPTANCE.md)。
