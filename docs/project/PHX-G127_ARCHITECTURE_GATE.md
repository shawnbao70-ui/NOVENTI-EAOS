# PHX-G127 Platform Tenant Lifecycle Thin Probe Architecture Gate

**日期：** 2026-07-21  
**状态：** Fully Accepted（Foundation）  
**归属：** Smart Terminal / Platform Organization  
**规范源：** ADR-0146  
**人工确认：** 支付清算另批；无自动写 grant / WebAuthn 产品页；无新 Alembic；包仍 `0.2.0`  

## 1. 门禁目标

Smart Terminal Admin 对平台租户 create / suspend / reactivate 做薄接线。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| UI | Create / Suspend / Reactivate platform tenant |
| API | 仅调用既有 `/v1/platform/tenants*` |
| Context | `platform: true`；path tenant id 独立输入 |
| Out | permission write；支付清算；Role→grant 自动写入 |

## 3. Exit Criteria

1. ADR-0146 Accepted。  
2. Terminal 控件与契约绿。  
3. 全量 contracts 绿；包 `0.2.0`；head `0029`。  

见 [PHX-G127_ACCEPTANCE.md](PHX-G127_ACCEPTANCE.md)。
