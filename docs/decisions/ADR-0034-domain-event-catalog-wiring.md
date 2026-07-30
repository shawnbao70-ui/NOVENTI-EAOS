# ADR-0034 — 领域事件目录同事务接线

**状态：** Accepted  
**日期：** 2026-07-18  
**里程碑：** PHX-E19  
**归属：** Shared Event Capability + K07–K10 生产者

## 背景

PHX-P11 已交付 Outbox / Worker / DLQ；K07–K10 已定义领域事件目录。目录此前仅是规范，域服务只写 audit，不调用 `enqueue`。P11 验收显式延后「全量自动发布接线」。

## 决策

### 1. 命名归一

- 信封仍强制 `domain.entity.action`（ADR-0006 / `EVENT_NAME_PATTERN`）
- Permission / Workflow / Knowledge 目录名从 PascalCase 归一为小写三元组，例如：
  - `Permission.PolicyActivated` → `permission.policy.activated`
  - `Workflow.InstanceStarted` → `workflow.instance.started`
  - `Knowledge.EntityUpserted` → `knowledge.entity.upserted`
- Organization 目录已合规，保持不变

### 2. 受信域生产者路径

- 新增 `DomainEventEmitter.enqueue_fact`：域命令成功后写入 outbox，**不**要求调用方持有 `event_stream:publish`
- 客户端 / HTTP 面仍只能通过既有 `EventBus.enqueue`（需权限）
- `producer` 固定为域标识（如 `organization.kernel`）

### 3. 同事务

- Transactional* 服务在同一 `SQLAlchemyUnitOfWork` session 写入领域状态、audit 与 outbox
- 使用无租户绑定的 `SQLAlchemyOutboxWriter`，以支持平台面 `create_tenant` 后按**新租户**写 outbox

### 4. 显式延后（本切片）

- `permission.decision.recorded`：高基数，本切片不接线（目录可保留规范）→ **已由 ADR-0050 / PHX-E20 接线**
- 外部 Broker、区域投递、完整 JSON Schema 注册中心

## 关联

- [ADR-0006-event-envelope.md](ADR-0006-event-envelope.md)
- [ADR-0026-event-outbox-worker-dlq.md](ADR-0026-event-outbox-worker-dlq.md)
- [../project/PHX-E19_ARCHITECTURE_GATE.md](../project/PHX-E19_ARCHITECTURE_GATE.md)
