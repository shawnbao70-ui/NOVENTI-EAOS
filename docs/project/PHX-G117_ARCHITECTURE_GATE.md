# PHX-G117 AI Runtime Status / Run Thin Probe Architecture Gate

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Smart Terminal / AI Runtime  
**规范源：** ADR-0136  
**人工确认：** tools/memory/approval 另批；支付清算另批；无自动写 grant / WebAuthn 产品页；无新 Alembic  

## 1. 门禁目标

Smart Terminal Admin 对 AI Runtime 状态与 run create/get 做薄接线；AI subject 经 trusted header。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Status | `GET /v1/ai/status` 只读 |
| UI | status / Create run / Get run |
| Subject | create/get 使用 `ai_employee` trusted header |
| Out | tools / memory / approvals / commits；支付清算 |

## 3. Exit Criteria

1. ADR-0136 Accepted。  
2. Terminal 控件与契约绿。  
3. 全量 contracts 绿；包 `0.2.0`；head `0029`。  

见 [PHX-G117_ACCEPTANCE.md](PHX-G117_ACCEPTANCE.md)。
