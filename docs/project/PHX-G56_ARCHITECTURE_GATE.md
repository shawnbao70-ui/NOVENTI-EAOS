# PHX-G56 Multi-IdP Write Registry Architecture Gate

**日期：** 2026-07-19  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform API Gateway / Identity  
**规范源：** ADR-0075  
**人工确认：** 支付清算另批  

## 1. 门禁目标

平台面可写 IdP 发行方注册表；合并进 JWT 校验；env 优先。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Plane | `/v1/platform/idp/issuers` |
| Store | 进程内（默认）；Alembic `0025` 表契约 |
| Precedence | env issuer 胜出 |
| Version | 包 `0.2.0`；Alembic → `0025` |

## 3. Exit Criteria

1. ADR-0075 Accepted。  
2. 平台 CRUD/disable + 校验合并 + status registry 段。  
3. 全量 contracts 绿；manifest head = `0025`。  

## 4. 验收

见 [PHX-G56_ACCEPTANCE.md](PHX-G56_ACCEPTANCE.md)；契约 `500 passed`。
