# PHX-K07 Organization Kernel Architecture Gate

**日期：** 2026-07-18  
**状态：** Accepted for Implementation  
**归属：** Core Kernel / Organization  
**规范源：** BOOK02、BOOK19、BOOK22、ADR-0019、ADR-0022

## 1. 门禁目标

在实现 PHX-K07 前，固定 Organization 的 L0–L2 模型、状态机、授权边界、跨域协调与 PostgreSQL 验收范围，消除 Tenant / Enterprise 混用。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Tenant / Enterprise | Tenant 是强隔离边界；Enterprise 是 Tenant 内法人或组织主体。二者分离建模。 |
| L0–L2 | L0 Tenant，L0.5 Enterprise，L1 Organization Unit，L2 Membership。 |
| Enterprise 层级 | 一个 Tenant 可含多个 Enterprise；每个 Tenant 必须有一个 primary Enterprise。 |
| Organization Unit | Unit 必须归属一个 Enterprise 与 Tenant；同一 Enterprise 内形成无环森林。 |
| Membership | Membership 归属 Tenant，可选择 Enterprise / Unit；Unit membership 的 Enterprise 由 Unit 唯一确定。 |
| 多归属 | Subject 可同时属于多个 Unit；每个 Unit 至多一个 active Membership，企业级 Membership 每 Enterprise 至多一个 active。 |
| Tenant 生命周期 | active ↔ suspended；active/suspended → closed；closed 终态。 |
| CloseTenant | 语义已定义，但执行依赖 Workflow 人工审批与跨 Kernel 依赖清理，本切片 Explicit Defer。 |
| primary admin | 不由 Organization 隐式创建 Permission Grant；由 PHX-K08 bootstrap coordinator 显式编排。 |
| 读路径授权 | API/Runtime 必须先经 Permission；Organization Repository 继续强制 tenant scope。PHX-K07 固化 action/resource contract，策略引擎归 PHX-K08。 |
| 跨组织治理 | K07 指同一 Tenant 内 Enterprise / Unit 层级治理；跨 Tenant federation、合并拆分 Explicit Defer。 |
| 乐观并发 | Tenant、Enterprise、Unit、Membership 更新均使用 `expected_version`。 |
| 软删除 | Organization 使用 terminal status + timestamps 作为生命周期保留策略，不物理删除；这是本域对通用 `deleted_at` 的显式等价实现。 |
| 领域事件 | 事件目录在 K07 定义；可靠 publish/outbox 归 PHX-P11。 |
| OpenAPI / 状态机 | 作为 K07 退出门禁，规格标准与 PHX-006 Identity 对齐。 |

## 3. Permission Action / Resource Contract

| Action | Resource |
|--------|----------|
| `org.tenant.read` | `tenant:{tenant_id}` |
| `org.enterprise.read` | `enterprise:{enterprise_id}` |
| `org.unit.read` | `org_unit:{unit_id}` / `tenant:{tenant_id}:org_units` |
| `org.membership.read` | `membership:{id}` / `tenant:{tenant_id}:memberships` |
| `org.enterprise.manage` | `enterprise:{enterprise_id}` |
| `org.unit.manage` | `org_unit:{unit_id}` / `tenant:{tenant_id}:org_units` |
| `org.membership.manage` | `membership:{id}` / `tenant:{tenant_id}:memberships` |

Create/Suspend/Reactivate Tenant 继续由 Platform Identity Governor 管理，不由租户 Permission 替代。

## 4. K07 实现切片

### Slice A — Domain Correctness

- 暂停/关闭 Tenant 写阻断
- Unit 层级 self/cycle 防护
- Membership terminal 状态不可变
- 目标 Unit active 守卫

### Slice B — Enterprise Model

- `enterprises` 持久化模型与迁移
- CreateTenant 原子创建 primary Enterprise
- Enterprise 查询与同租户唯一约束
- Unit 显式归属 Enterprise

### Slice C — Lifecycle and Concurrency

- Tenant / Enterprise / Unit / Membership 状态机
- Repository 乐观锁与 `ORG_VERSION_CONFLICT`
- 事务回滚与审计一致性

### Slice D — Contracts and PostgreSQL

- Organization OpenAPI 3.1
- Organization State Machines
- PostgreSQL legal-name、partial unique、composite FK、optimistic-lock 契约
- PHX-K07 七步自审与 Acceptance

## 5. Explicit Defer

- CloseTenant 执行与跨 Kernel 清理
- primary admin Permission Grant
- Tenant federation、Enterprise 合并/拆分
- region policy enforcement
- reliable event outbox / delivery
- Smart Terminal tenant-switch UX

这些能力不得由 Organization Service 静默模拟。

## 6. 退出标准

1. L0–L2 模型与 PostgreSQL schema 一致。
2. 跨租户、层级环、暂停写入与 stale version 均 fail closed。
3. Identity eligibility、AI reassignment 与 role≠permission 契约保持。
4. OpenAPI、状态机、接口、数据模型、ADR 与代码一致。
5. Organization 专属 PostgreSQL 集成测试及完整回归通过。
