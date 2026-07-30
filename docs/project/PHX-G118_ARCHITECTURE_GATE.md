# PHX-G118 AI Tools / Memory Thin Probe Architecture Gate

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Smart Terminal / AI Runtime  
**规范源：** ADR-0137  
**人工确认：** approval/commit 另批；支付清算另批；无自动写 grant / WebAuthn 产品页；无新 Alembic  

## 1. 门禁目标

Smart Terminal Admin 对 AI tool register/invoke 与 memory write/read 做薄接线。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| UI | Register tool / Invoke tool / Write memory / Read memory |
| Subject | register=human；invoke/memory=`ai_employee` |
| Out | approvals / commits；支付清算 |

## 3. Exit Criteria

1. ADR-0137 Accepted。  
2. Terminal 控件与契约绿。  
3. 全量 contracts 绿；包 `0.2.0`；head `0029`。  

见 [PHX-G118_ACCEPTANCE.md](PHX-G118_ACCEPTANCE.md)。
