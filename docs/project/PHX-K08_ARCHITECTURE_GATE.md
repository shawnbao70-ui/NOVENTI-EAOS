# PHX-K08 Permission Kernel Architecture Gate

**日期：** 2026-07-18  
**状态：** Accepted for Implementation  
**归属：** Core Kernel / Permission  
**规范源：** BOOK05、BOOK10、BOOK19、BOOK22、BOOK23、ADR-0008、ADR-0023

## 1. 门禁目标

将 Foundation positive Grant 提升为统一的 Policy、Scope、Delegation、Explain 授权内核，同时保持默认拒绝、租户隔离、决策审计与 Human Approval 独立边界。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Policy model | 类型化 Policy + Rule；ACTIVE 版本不可变 |
| Combining | Explicit deny overrides；否则 allow；无匹配默认 deny |
| Scope | Tenant → Enterprise → Org Unit → Resource |
| Scope truth | Tenant/Enterprise/Unit 关系由 Organization Resolver 验证 |
| Principal truth | Identity active + same-Tenant eligibility |
| Conditions | 通过 Condition Evaluator port；缺失/未知/error 全部 deny |
| Delegation | 父 Grant 派生、范围只能缩小、depth 递减、父链持续有效 |
| Revoke | ACTIVE → REVOKED，reason + expected_version |
| Explain | 保存匹配引用、Scope trace 与 condition 摘要；不泄露秘密 |
| Query visibility | self-only；受信 proxy / auditor 显式授权 |
| Approval | Permission allow 不替代 Workflow human approval |
| Events | 目录在 K08 定义，可靠 delivery 归 PHX-P11 |

## 3. Permission Action / Resource Contract

### 管理动作

- `permission.policy.create`
- `permission.policy.activate`
- `permission.policy.deprecate`
- `permission.grant.create`
- `permission.grant.revoke`
- `permission.grant.delegate`
- `permission.decision.explain`
- `permission.effective.list`

### 资源

- `permission_policy:{policy_id}`
- `permission_grant:{grant_id}`
- `permission_decision:{decision_id}`
- `principal:{subject_id}:effective_permissions`

Foundation 管理员 bootstrap 集合只用于建立第一条治理路径；持久化 Policy 管理授权完成后不得成为平行真相源。

## 4. 实现切片

### Slice A — Foundation Security Closure

- `conditions_ref` 未解析时 deny
- Principal eligibility fail closed
- Explain / ListEffective self-or-auditor
- Revoke reason + expected_version

### Slice B — Policy and Scope

- Policy / Rule domain、Repository、ORM、Alembic
- Tenant / Enterprise / Org Unit / Resource Scope
- deny-overrides evaluation
- actual policy version and matched evidence

### Slice C — Delegation

- parent Grant、delegator、remaining depth、delegable、expiry narrowing
- parent-chain validity and cycle guard
- delegated Grant audit and Explain

### Slice D — Contracts and PostgreSQL

- Permission OpenAPI 3.1
- Policy / Grant / Delegation state machines
- populated migration and PostgreSQL constraint tests
- concurrency, rollback, cross-Tenant and deny precedence tests

## 5. Exit Criteria

1. 默认拒绝与 explicit deny precedence 全路径成立。
2. Scope 不越过 Tenant / Enterprise / Unit 边界。
3. condition unresolved/error 不产生 allow。
4. Delegation 无扩大、无循环、父链失效即时生效。
5. Revoke / Policy lifecycle 使用数据库原子乐观锁。
6. Explain 具备证据且不泄露秘密。
7. OpenAPI、状态机、Data Model、Migration、Code 一致。
8. Permission 专属 PostgreSQL 与完整回归通过。

## 6. Explicit Defer

- 通用脚本 Policy DSL
- 外部 IAM / OPA 等引擎接入
- 平台跨 Tenant policy / break-glass
- Role/Group expansion
- 法律与商业策略内容
- reliable event outbox
