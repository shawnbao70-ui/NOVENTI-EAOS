# PHX-E20 Permission DecisionRecorded Wiring Acceptance

**日期：** 2026-07-18  
**状态：** Fully Accepted  
**归属：** Permission Kernel + Shared Event Capability  
**退出门禁：** Evaluate 成功与 outbox enqueue 同路径；摘要 payload

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0050 + Architecture Gate |
| B | `PermissionService.evaluate` → `permission.decision.recorded` |
| C | 目录契约更新 + 专用测试 |
| D | 七步自审 |

## 2. 核心不变量

- 仅在注入 `domain_events` 时发射
- Payload 为摘要；无策略原文 / 秘密
- 高基数由订阅方按 at-least-once 消化
- 无外部 Broker

## 3. 自动化证据

- 本地完整回归：`398 passed`（`tests/contracts`）
- 专用 PostgreSQL 17：`19 passed`
- Alembic head：`0020_marketplace_m16`（无新迁移）

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0050 |
| Constitution Review | 通过；域产生事实、Event 投递 |
| Cross-reference Review | 通过；PERMISSION_EVENTS 对齐 |
| Documentation Review | 通过 |
| Consistency Review | 通过；E19 目录闭合 |
| Gap Analysis | Broker / 采样治理 / OIDC / 商业显式延后 |
| Second-pass Review | Fully Accepted |

## 5. Explicit Defer

- 外部消息中间件 / 多区域投递
- Decision 事件采样或速率治理产品化
- JWT/OIDC；Marketplace 商业政策

## 6. 证据索引

- [PHX-E20 Architecture Gate](PHX-E20_ARCHITECTURE_GATE.md)
- [ADR-0050](../decisions/ADR-0050-permission-decision-recorded-wiring.md)
- [Permission Events](../architecture/PERMISSION_EVENTS.md)
