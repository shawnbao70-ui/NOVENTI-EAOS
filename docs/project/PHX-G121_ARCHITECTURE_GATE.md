# PHX-G121 Identity Credential / Session Thin Probe Architecture Gate

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Smart Terminal / Identity  
**规范源：** ADR-0140  
**人工确认：** Organization 另批；支付清算另批；无自动写 grant / WebAuthn 产品页；无新 Alembic  

## 1. 门禁目标

Smart Terminal Admin 对 Identity credential bind 与 session create/validate 做薄接线；Identity Terminal 运维面齐。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| UI | Bind credential / Create session / Validate session |
| Subject | session 路径以目标 subject 作 trusted header |
| Secret | 仅 vault ref handle；不下发 raw secret |
| Out | Organization；支付清算；WebAuthn |

## 3. Exit Criteria

1. ADR-0140 Accepted。  
2. Terminal 控件与契约绿。  
3. 全量 contracts 绿；包 `0.2.0`；head `0029`。  

见 [PHX-G121_ACCEPTANCE.md](PHX-G121_ACCEPTANCE.md)。
