# PHX-E19 Domain Event Catalog Wiring Architecture Gate

**日期：** 2026-07-18  
**状态：** Fully Accepted（实现已验收）  
**归属：** Shared Event Capability  
**规范源：** ADR-0006、ADR-0026、ADR-0034、K07–K10 事件目录  
**退出门禁：** 成功域命令与 outbox enqueue 同事务；目录名与信封模式一致

## 1. 门禁目标

将 K07–K10 事件目录从「文档规范」接到 Outbox：命令成功 → 同事务 `enqueue_fact` → worker `dispatch_due` 可投递。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Naming | 全目录 `domain.entity.action` |
| Emit path | 受信 `DomainEventEmitter`（跳过 subject publish 检查） |
| Atomicity | 同 UoW session |
| DecisionRecorded | 延后 |
| Broker | 不引入 |

## 3. Exit Criteria

1. Organization 目录事件在成功命令后进入 pending outbox。  
2. Permission / Workflow / Knowledge 至少覆盖状态变更类事件（DecisionRecorded 除外）。  
3. 目录文档与代码事件名一致；契约测试覆盖命名与至少一条 enqueue→dispatch。  
4. 完整回归通过；无新 Alembic（沿用 `0020`）。  
5. 不宣称外部 Broker 或商业 Marketplace 已交付。

## 4. Explicit Defer

`permission.decision.recorded` 接线、外部消息中间件、OIDC、Marketplace 商业政策
