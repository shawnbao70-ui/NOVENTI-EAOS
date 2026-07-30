# PHX-G78 Tenant IdP Federation Issuer Priority Architecture Gate

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform API Gateway / Persistence  
**规范源：** ADR-0097  
**人工确认：** 支付清算另批；无 claim/MFA / social login  

## 1. 门禁目标

绑定 `priority` 元数据 + set API + matrix/list；enforce 语义不变。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Default | `100`；越小越优先 |
| API | `POST .../bindings/{id}/priority` |
| Schema | Alembic `0028` |
| Enforce | 不变（任一 active 仍放行） |

## 3. Exit Criteria

1. ADR-0097 Accepted。  
2. memory|sql 优先级可测；G66–G77 不回归。  
3. 全量 contracts 绿；包 `0.2.0`；head `0028`。  

见 [PHX-G78_ACCEPTANCE.md](PHX-G78_ACCEPTANCE.md)。
