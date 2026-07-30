# PHX-G95 Terminal Effective Permissions Thin Probe Architecture Gate

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Smart Terminal / Permission  
**规范源：** ADR-0114  
**人工确认：** 支付清算另批；无自动写 grant / WebAuthn 产品页；无新 Alembic  

## 1. 门禁目标

Smart Terminal Admin 对既有 `GET /v1/permission/principals/{subject_id}/effective-permissions` 做只读薄探针。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| UI | Admin「List effective permissions」+ principal subject 输入 |
| API | 仅调用既有 effective-permissions 路径 |
| Authz | 沿用 Kernel self-or-auditor；不放宽 |
| Write | 禁止 |

## 3. Exit Criteria

1. ADR-0114 Accepted。  
2. Terminal 控件与契约绿。  
3. 全量 contracts 绿；包 `0.2.0`；head `0029`。  

见 [PHX-G95_ACCEPTANCE.md](PHX-G95_ACCEPTANCE.md)。
