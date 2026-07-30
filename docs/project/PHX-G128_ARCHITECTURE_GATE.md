# PHX-G128 Permission Policy / Grant Manual Write Thin Probe Architecture Gate

**日期：** 2026-07-21  
**状态：** Fully Accepted（Foundation）  
**归属：** Smart Terminal / Permission  
**规范源：** ADR-0147  
**人工确认：** 非 Role→grant 自动写入；支付清算另批；无 WebAuthn 产品页；无新 Alembic；包仍 `0.2.0`  

## 1. 门禁目标

Smart Terminal Admin 对 Permission policy create/activate 与 grant create/revoke 做手工薄接线。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| UI | Create·Activate policy；Create·Revoke grant |
| API | 仅调用既有 policies / grants 写入路径 |
| Fence | ≠ `EAOS_PERMISSION_ROLE_GRANT_MAP` / Role→Policy |
| Out | deprecate；delegate；Role→grant 自动写入 |

## 3. Exit Criteria

1. ADR-0147 Accepted。  
2. Terminal 控件与契约绿。  
3. 全量 contracts 绿；包 `0.2.0`；head `0029`。  

见 [PHX-G128_ACCEPTANCE.md](PHX-G128_ACCEPTANCE.md)。
