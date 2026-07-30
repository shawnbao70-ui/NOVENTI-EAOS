# PHX-G141 Marketplace Foundation Commercial Terminal Probe Architecture Gate

**日期：** 2026-07-21  
**状态：** Fully Accepted（Foundation）  
**归属：** Smart Terminal / Marketplace  
**规范源：** ADR-0160  
**人工确认：** ≠ 支付清算 / 外部仲裁；无 Alembic/版本 bump  

## 1. 门禁目标

将既有 M17 Gateway 商业路径接到 Terminal Admin 薄控件。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Paths | pricing · invoices · disputes · resolve · revenue-share |
| Fence | 支付清算 / 外部仲裁 / metering 仍另批 |
| Docs | `docs/api/README.md` 纠正「commercial fail-closed」表述 |
| Out | Role→grant；WebAuthn；`0.2.1`；支付清算实现 |

## 3. Exit Criteria

1. ADR-0160 Accepted。  
2. Terminal + 契约绿。  
3. 全量 contracts 绿；包 `0.2.0`；head `0029`。  

见 [PHX-G141_ACCEPTANCE.md](PHX-G141_ACCEPTANCE.md)。
