# PHX-G122 Organization Status / Tenant / Enterprise Thin Probe Architecture Gate

**日期：** 2026-07-21  
**状态：** Fully Accepted（Foundation）  
**归属：** Smart Terminal / Organization  
**规范源：** ADR-0141  
**人工确认：** unit/membership 另批；支付清算另批；无自动写 grant / WebAuthn 产品页；无新 Alembic  

## 1. 门禁目标

Smart Terminal Admin 对 Organization 状态、tenant get 与 enterprise create/list 做薄接线。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Status | `GET /v1/organization/status` 只读 |
| UI | status / Get tenant / Create·List enterprises |
| Path | tenant id 经独立输入，与 Tenant 头一致 |
| Out | units / memberships；支付清算 |

## 3. Exit Criteria

1. ADR-0141 Accepted。  
2. Terminal 控件与契约绿。  
3. 全量 contracts 绿；包 `0.2.0`；head `0029`。  

见 [PHX-G122_ACCEPTANCE.md](PHX-G122_ACCEPTANCE.md)。
