# PHX-E19 Domain Event Catalog Wiring Acceptance

**日期：** 2026-07-18  
**状态：** Fully Accepted  
**归属：** Shared Event Capability + K07–K10 生产者  
**退出门禁：** 成功域命令与 outbox enqueue 同事务；目录名与信封模式一致

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0034 + Architecture Gate；命名归一 |
| B | `DomainEventEmitter` + `SQLAlchemyOutboxWriter` |
| C | Organization / Permission / Workflow / Knowledge 同事务接线 |
| D | 契约测试 + 七步自审 |

## 2. 核心不变量

- 事件名强制 `domain.entity.action`；Permission/Workflow/Knowledge 目录已归一
- 域生产者经受信 `enqueue_fact`，不要求调用方持有 `event_stream:publish`
- Transactional* 与 outbox 同 session；平台 `create_tenant` 按新租户写 outbox
- `permission.decision.recorded` 显式未接线（高基数）
- 投递仍依赖 worker `dispatch_due`；无外部 Broker

## 3. 自动化证据

- 本地完整回归：`314 passed`（`tests/contracts`）
- 专用 PostgreSQL 17：`19 passed`
- Alembic head：`0020_marketplace_m16`（无新迁移）

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0034；落点 emitter + 域服务 |
| Constitution Review | 通过；域产生事实、Event 负责投递 |
| Cross-reference Review | 通过；目录与代码名对齐 |
| Documentation Review | 通过；Gate / Acceptance / 四份 EVT 文档 |
| Consistency Review | 通过；head 未漂移 |
| Gap Analysis | DecisionRecorded / Broker 显式延后 |
| Second-pass Review | Fully Accepted |

## 5. Explicit Defer

- `permission.decision.recorded` 接线
- 外部消息中间件 / 多区域投递
- 完整 per-event JSON Schema 注册中心
- Marketplace 商业政策；JWT/OIDC 产品化

## 6. 证据索引

- [PHX-E19 Architecture Gate](PHX-E19_ARCHITECTURE_GATE.md)
- [ADR-0034](../decisions/ADR-0034-domain-event-catalog-wiring.md)
- [Organization Events](../architecture/ORGANIZATION_EVENTS.md)
- [Permission Events](../architecture/PERMISSION_EVENTS.md)
- [Workflow Events](../architecture/WORKFLOW_EVENTS.md)
- [Knowledge Events](../architecture/KNOWLEDGE_EVENTS.md)
