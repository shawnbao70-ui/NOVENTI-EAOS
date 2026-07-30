# PHX-G92 Terminal Tenant Roles Catalog Read Architecture Gate

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Smart Terminal / Permission  
**规范源：** ADR-0111  
**人工确认：** 支付清算另批；无自动写 grant / WebAuthn 产品页；无新 Alembic  

## 1. 门禁目标

Smart Terminal 提供租户面 `GET /v1/permission/roles` 只读薄接线，与 G91 平台写操作互补。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| UI | Admin「List tenant roles catalog」 |
| API | 仅调用既有 `/v1/permission/roles`（租户上下文） |
| Write | 禁止；不调用 platform roles 写路径 |
| Schema / Version | Alembic `0029`；包 `0.2.0` |

## 3. Exit Criteria

1. ADR-0111 Accepted。  
2. Terminal 控件与契约绿。  
3. 全量 contracts 绿。  

见 [PHX-G92_ACCEPTANCE.md](PHX-G92_ACCEPTANCE.md)。
