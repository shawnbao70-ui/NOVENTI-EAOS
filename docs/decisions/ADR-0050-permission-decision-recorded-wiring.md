# ADR-0050 — Permission DecisionRecorded Outbox Wiring

**状态：** Accepted  
**日期：** 2026-07-18  
**里程碑：** PHX-E20  
**归属：** Permission Kernel + Shared Event Capability

## 背景

ADR-0034 / PHX-E19 因高基数显式延后 `permission.decision.recorded`。目录与 Evaluate 持久化决策已存在；投影与审计需要可选同事务事实流。

## 决策

### 1. 接线点

- 在 `PermissionService.evaluate` 成功 `add_decision` 且 audit 记录之后调用 `_emit`
- 事件名：`permission.decision.recorded`
- `producer`：`permission.kernel`
- 仍走 `DomainEventEmitter.enqueue_fact`（无 `event_stream:publish` 要求）
- 未注入 `domain_events` 时行为不变（零发射）

### 2. Payload 约束（摘要）

仅摘要：`decision_id`、principal、action、resource、effect、reason、policy_version、matched grant/policy id 列表。  
禁止：凭证、秘密、策略原文、完整业务实体副本。

### 3. 高基数承认

Evaluate 频繁；订阅方须按 at-least-once / 幂等处理。本切片不引入采样或降采样开关。

### 4. Explicit Defer

- 外部 Broker / 多区域投递
- Decision 事件采样或速率治理产品化
- JWT/OIDC；Marketplace 商业政策

## 关联

- [ADR-0034-domain-event-catalog-wiring.md](ADR-0034-domain-event-catalog-wiring.md)
- [../architecture/PERMISSION_EVENTS.md](../architecture/PERMISSION_EVENTS.md)
- [../project/PHX-E20_ARCHITECTURE_GATE.md](../project/PHX-E20_ARCHITECTURE_GATE.md)
