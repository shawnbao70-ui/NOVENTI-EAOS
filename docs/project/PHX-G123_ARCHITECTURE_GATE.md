# PHX-G123 Organization Unit / Membership Thin Probe Architecture Gate

**日期：** 2026-07-21  
**状态：** Fully Accepted（Foundation）  
**归属：** Smart Terminal / Organization  
**规范源：** ADR-0142  
**人工确认：** unit status / membership suspension 另批；支付清算另批；无自动写 grant / WebAuthn 产品页；无新 Alembic  

## 1. 门禁目标

Smart Terminal Admin 对 Organization unit upsert/tree 与 membership add/list 做薄接线；Organization Terminal 运维面齐。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| UI | Upsert unit / Get tree / Add·List memberships |
| API | 仅调用既有 units/tree/memberships |
| Out | unit status / membership suspension；支付清算 |

## 3. Exit Criteria

1. ADR-0142 Accepted。  
2. Terminal 控件与契约绿。  
3. 全量 contracts 绿；包 `0.2.0`；head `0029`。  

见 [PHX-G123_ACCEPTANCE.md](PHX-G123_ACCEPTANCE.md)。
