# PHX-K08 Permission Kernel Acceptance

**日期：** 2026-07-18  
**状态：** Fully Accepted  
**归属：** Core Kernel / Permission  
**退出门禁：** Policy / Scope / Delegation / Explain + PostgreSQL

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | conditions_ref fail-closed、Principal eligibility、Explain/ListEffective 可见性、Revoke reason + expected_version |
| B | Policy/Rule、Tenant/Enterprise/OrgUnit/Resource Scope、deny-overrides、Scope Resolver |
| C | Delegation 父链、depth 递减、范围只能缩小、循环防护 |
| D | OpenAPI 3.1、状态机、事件目录、Alembic `0012`、PostgreSQL 约束与决策证据 |

## 2. 核心不变量

- `Permission.Evaluate` 是唯一运行时授权真相入口。
- 默认拒绝；显式 DENY 优先于 ALLOW；无匹配拒绝。
- `conditions_ref` 未知/缺失/错误一律不产生 allow。
- Principal 必须 Identity active 且同 Tenant 合格。
- Scope 不得跨 Tenant；Enterprise/Org Unit 由 Organization Resolver 验证。
- Delegation 只能缩小 actions/scope/expiry/depth；父链失效即时生效。
- Revoke / Policy 生命周期使用 `expected_version` 乐观锁。
- Explain 保存匹配引用与 Scope/condition 摘要，不泄露秘密。
- Permission allow 不替代 Workflow human approval。

## 3. 数据库门禁

- `kernel.policies` / `kernel.policy_rules` 独立表。
- Grant 扩展 scope、delegation 与乐观锁字段。
- `permission_decisions.evidence_json` 保存 Explain 证据。
- 活跃等价 Grant 唯一索引覆盖 scope 与 parent_grant。
- Alembic head：`0012_permission_policy_scope`。

## 4. 自动化证据

- 本地完整回归：`201 passed`
- 专用 PostgreSQL 17：`11 passed`
- 合计含集成：`212 passed`

## 5. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；唯一 ownership 为 Core Kernel / Permission |
| Constitution Review | 通过；符合 BOOK05 / BOOK10 / BOOK19 / ADR-0023 |
| Cross-reference Review | 通过 |
| Documentation Review | 通过 |
| Consistency Review | 通过；OpenAPI / State Machine / Code / Migration 对齐 |
| Gap Analysis | 阻断项关闭；非 K08 能力显式延后 |
| Second-pass Review | Fully Accepted |

## 6. Explicit Defer

- 通用脚本 Policy DSL / 外部 OPA
- 平台跨 Tenant policy / break-glass
- Role/Group expansion
- primary-admin bootstrap coordinator 编排（可与 Organization 后续协作）
- reliable event outbox（PHX-P11）

## 7. 证据索引

- [PHX-K08 Architecture Gate](PHX-K08_ARCHITECTURE_GATE.md)
- [ADR-0023](../decisions/ADR-0023-permission-policy-scope-delegation.md)
- [Permission Interface](../architecture/PERMISSION_INTERFACE.md)
- [Permission State Machines](../architecture/PERMISSION_STATE_MACHINES.md)
- [Permission Event Catalog](../architecture/PERMISSION_EVENTS.md)
- [Permission OpenAPI](../api/permission.openapi.yaml)
- [Kernel Data Model](../architecture/KERNEL_DATA_MODEL.md)
