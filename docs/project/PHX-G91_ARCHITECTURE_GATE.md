# PHX-G91 Terminal Platform Roles Admin Thin Ops Architecture Gate

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Smart Terminal / Platform API Gateway  
**规范源：** ADR-0110  
**人工确认：** 支付清算另批；无自动写 grant / WebAuthn 产品页；无新 Alembic  

## 1. 门禁目标

Smart Terminal Admin 对声明角色目录做 List / Upsert / Disable 薄接线。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| UI | Admin 控件绑定既有 `/v1/platform/roles` |
| API | 不新增业务语义 |
| Schema | 沿用 Alembic `0029` |
| Version | 包 `0.2.0` |

## 3. Exit Criteria

1. ADR-0110 Accepted。  
2. Terminal Admin 控件与 `app.js` 路径契约绿。  
3. 全量 contracts 绿；包 `0.2.0`；head `0029`。  

见 [PHX-G91_ACCEPTANCE.md](PHX-G91_ACCEPTANCE.md)。
