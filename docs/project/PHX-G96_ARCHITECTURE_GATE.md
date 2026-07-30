# PHX-G96 JWT Denylist Status Observability Architecture Gate

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform API Gateway / Auth / Smart Terminal  
**规范源：** ADR-0115  
**人工确认：** 支付清算另批；无自动写 grant / WebAuthn 产品页；无新 Alembic  

## 1. 门禁目标

只读暴露 JWT / denylist 运行态摘要（含 runtime revoke 计数）；Terminal Admin 薄探针。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| API | `GET /v1/auth/jwt/status` |
| 内容 | require_jwt、denylist 启用/来源、配置条目数、runtime_revoked_count；不下发 jti 列表/密文 |
| UI | Admin「JWT status」 |
| Write | 禁止 |

## 3. Exit Criteria

1. ADR-0115 Accepted。  
2. 契约绿；Terminal 控件绿。  
3. 全量 contracts 绿；包 `0.2.0`；head `0029`。  

见 [PHX-G96_ACCEPTANCE.md](PHX-G96_ACCEPTANCE.md)。
