# PHX-G77 Tenant IdP Federation Policy Matrix Architecture Gate

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform API Gateway / Terminal  
**规范源：** ADR-0096  
**人工确认：** 支付清算另批；无策略引擎 / social login  

## 1. 门禁目标

跨租户矩阵只读视图 + Terminal 薄表；复用 G66–G69 绑定数据。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| API | `GET /v1/platform/idp/federation/matrix` |
| Cells | active \| disabled \| unbound |
| UI | Admin Matrix 按钮；platform 上下文 |
| Schema | 无 Alembic |

## 3. Exit Criteria

1. ADR-0096 Accepted。  
2. 矩阵可测；Bind/Unbind 仍绿；G66–G69 不回归。  
3. 全量 contracts 绿；包 `0.2.0`；head `0027`。  

见 [PHX-G77_ACCEPTANCE.md](PHX-G77_ACCEPTANCE.md)。
