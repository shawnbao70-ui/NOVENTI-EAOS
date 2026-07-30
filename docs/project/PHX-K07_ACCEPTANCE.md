# PHX-K07 Organization Kernel Acceptance

**日期：** 2026-07-18  
**状态：** Fully Accepted  
**归属：** Core Kernel / Organization  
**退出门禁：** L0–L2 + PostgreSQL

## 1. 交付范围

| 层级 | 交付 |
|------|------|
| L0 | Tenant 隔离边界、平台 Governor 状态治理、暂停写阻断 |
| L0.5 | 独立 Enterprise 主体、primary Enterprise、多 Enterprise 生命周期 |
| L1 | Enterprise 作用域 Unit 森林、同域 FK、防环、生命周期与依赖检查 |
| L2 | Identity eligibility、Membership 生命周期、多 Enterprise 归属、AI 改派协调 |
| Persistence | SQLAlchemy Repository、UoW、Alembic 0011、乐观锁、Enterprise 串行化锁 |
| Contract | OpenAPI 3.1、状态机、领域事件目录、稳定错误码 |

## 2. 核心不变量

- Tenant 与 Enterprise 分离：Tenant 是隔离边界，Enterprise 是边界内法人/组织主体。
- CreateTenant 原子创建 primary Enterprise。
- Unit parent 必须同 Tenant / Enterprise，且层级无 self/cycle。
- Organization 写入在 Tenant 或 Enterprise suspended/closed 时失败关闭。
- Subject 可跨多个 Enterprise 建立 Membership，但每 Enterprise / Unit active 关系唯一。
- Membership role label 不授予 Permission。
- AI Membership 要求同 Tenant active assignment；跨租户改派原子结束旧 Membership。
- Tenant、Enterprise、Unit、Membership 更新使用 `expected_version`。
- Enterprise 行级锁序列化 Unit/Member 写入与生命周期变更；并发操作不得产生关闭对象下的 active 依赖。
- Organization 使用 terminal status + timestamps 保留历史，不执行物理删除。

## 3. 数据库门禁

- `kernel.enterprises` 独立表。
- Unit / Membership 强制 `enterprise_id`。
- Enterprise、parent Unit、Membership→Unit 使用 Tenant + Enterprise 复合约束。
- active Membership 唯一索引包含 `enterprise_id`。
- 0011 可从含 Tenant / Unit / Membership 数据的 0010 schema 回填 primary Enterprise。
- PostgreSQL 并发交叉 reparent 不形成环。
- PostgreSQL Unit 生命周期与并发 AddMembership 只能一个成功。

## 4. 自动化证据

- 本地完整回归：`184 passed`
- 专用 PostgreSQL 17：`10 passed`
- IDE lint：0 errors
- 最终七步复核：Fully Accepted

## 5. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；L0–L2 ownership 唯一 |
| Constitution Review | 通过；符合 BOOK02 / BOOK19 / BOOK22 |
| Cross-reference Review | 通过 |
| Documentation Review | 通过 |
| Consistency Review | 通过；OpenAPI / State Machine / Code / Migration 对齐 |
| Gap Analysis | 阻断项关闭；非 K07 能力显式延后 |
| Second-pass Review | Fully Accepted |

## 6. Explicit Defer

- CloseTenant 的 Workflow 人工审批与跨 Kernel 清理
- primary-admin Permission bootstrap coordinator（PHX-K08）
- 跨 Tenant federation、Enterprise 合并拆分
- region policy enforcement
- reliable event outbox / delivery（PHX-P11）
- Smart Terminal tenant-switch UX（PHX-T13）

上述能力未被当前实现伪装完成。

## 7. 证据索引

- [PHX-K07 Architecture Gate](PHX-K07_ARCHITECTURE_GATE.md)
- [ADR-0022](../decisions/ADR-0022-organization-lifecycle-hierarchy.md)
- [Organization Interface](../architecture/ORGANIZATION_INTERFACE.md)
- [Organization State Machines](../architecture/ORGANIZATION_STATE_MACHINES.md)
- [Organization Event Catalog](../architecture/ORGANIZATION_EVENTS.md)
- [Organization OpenAPI](../api/organization.openapi.yaml)
- [Kernel Data Model](../architecture/KERNEL_DATA_MODEL.md)

## 8. 结论

PHX-K07 满足 Roadmap v3 的企业层级、成员生命周期、同租户跨组织治理与 L0–L2 + PostgreSQL 退出标准。项目可进入 PHX-K08 Permission Kernel。
