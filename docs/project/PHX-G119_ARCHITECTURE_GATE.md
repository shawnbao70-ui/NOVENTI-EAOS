# PHX-G119 AI Approval / Commit Thin Probe Architecture Gate

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Smart Terminal / AI Runtime  
**规范源：** ADR-0138  
**人工确认：** commit 无审批仍 fail-closed；支付清算另批；无自动写 grant / WebAuthn 产品页；无新 Alembic  

## 1. 门禁目标

Smart Terminal Admin 对 AI approval request 与 commit 审批门禁做薄接线；AI Runtime Terminal 运维面齐。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| UI | Request approval / Commit（approval-gated） |
| Subject | `ai_employee` trusted header |
| Gate | 无审批 commit → 403 |
| Out | 打开无审批 commit；支付清算 |

## 3. Exit Criteria

1. ADR-0138 Accepted。  
2. Terminal 控件与契约绿。  
3. 全量 contracts 绿；包 `0.2.0`；head `0029`。  

见 [PHX-G119_ACCEPTANCE.md](PHX-G119_ACCEPTANCE.md)。
