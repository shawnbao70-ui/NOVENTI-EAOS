# PHX-G55 Multi-IdP Status UI Architecture Gate

**日期：** 2026-07-19  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform API Gateway / Smart Terminal  
**规范源：** ADR-0074 · BOOK23  
**人工确认：** 支付清算另批  

## 1. 门禁目标

只读 IdP/JWT 状态聚合 + Terminal Admin 探针；配置仍由环境变量持有。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| API | `GET /v1/auth/idp/status` 只读脱敏 |
| UI | Admin 探针，无 CRUD |
| Write | 不交付 |
| Version | 保持 `0.2.0` |

## 3. Exit Criteria

1. ADR-0074 Accepted。  
2. 聚合脱敏正确；Admin 按钮/路径契约绿。  
3. 全量 contracts 绿；无 Alembic / 版本 bump。  

## 4. 验收

见 [PHX-G55_ACCEPTANCE.md](PHX-G55_ACCEPTANCE.md)；契约 `496 passed`。
