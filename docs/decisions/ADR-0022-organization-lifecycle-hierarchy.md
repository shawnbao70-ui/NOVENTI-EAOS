# ADR-0022 — Organization Lifecycle, Hierarchy and Concurrency

**状态：** Accepted  
**日期：** 2026-07-18  
**里程碑：** PHX-K07  
**归属：** Core Kernel / Organization

## 背景

PHX-004 已实现 Tenant、Organization Unit、Membership、SQLAlchemy 持久化与 Identity L2 协调，但尚未完整定义层级防环、实体状态机、暂停边界、成员多归属与并发更新语义。PHX-K07 必须在扩大接口前先关闭这些不变量。

## 决策

### 1. L0–L2 模型

- **L0 Tenant Boundary：** 数据、权限、配置与运营的强隔离边界。
- **L0.5 Enterprise：** Tenant 内的法人或组织主体；一个 Tenant 可包含多个 Enterprise，且必须有一个 primary Enterprise。
- **L1 Organization Unit Hierarchy：** Enterprise 内的组织单元森林；每个节点最多一个父节点，可有多个根。
- **L2 Membership：** Identity Subject 与 Tenant / Organization Unit 的受治理关系。
- Organization 角色标签只描述组织关系，不授予 Permission。

### 2. 层级不变量

- 父子单元必须属于同一 Tenant 与 Enterprise。
- 节点不得以自身或自身后代为父节点；层级必须保持无环。
- 跨租户 reparent 永久禁止。
- PHX-K07 不强制单一 HQ；集团可通过多个 Enterprise、多个根或 Group 节点表达。

### 3. Membership 多归属

- Subject 在同一 Enterprise 可拥有至多一个 active 企业级 Membership（`org_unit_id = null`）。
- Subject 可同时属于多个 Organization Unit，但每个 Unit 至多一个 active Membership。
- Membership transfer 是同租户 active Membership 的原子 reparent；不得转移 suspended 或 ended Membership。
- Identity eligibility 在创建 Membership 时必须 fail closed；AI Employee 必须具有同租户 active assignment。

### 4. 状态机

**Tenant**

- `ACTIVE → SUSPENDED → ACTIVE`
- `ACTIVE | SUSPENDED → CLOSED`
- `CLOSED` 为终态。

**Organization Unit**

- `ACTIVE ↔ INACTIVE`
- `ACTIVE | INACTIVE → CLOSED`
- `CLOSED` 为终态。

**Membership**

- `ACTIVE ↔ SUSPENDED`
- `ACTIVE | SUSPENDED → ENDED`
- `ENDED` 为终态。

非法转换必须 fail closed 并返回稳定错误码。

### 5. 暂停与关闭边界

- Tenant 非 ACTIVE 时禁止 Unit 与 Membership 的创建、更新、转移及恢复。
- Tenant 查询与平台治理证据读取仍可进行。
- Tenant、Unit 的关闭不隐式级联删除或结束下级对象；存在 active 下级对象时拒绝关闭，后续由显式 Workflow 协调。
- 合并、拆分、跨企业迁移属于高影响操作，不在 PHX-K07 基础命令中隐式实现。
- CloseTenant 可执行命令延后至 Workflow 人工审批与跨 Kernel 清理协调完成；PHX-K07 仅固定状态语义。

### 6. 乐观并发

- 所有可变实体保留单调递增 `version`。
- 更新命令必须提供 `expected_version`。
- Repository 更新必须以 `id + tenant scope + current version` 为条件；零行更新返回 `ORG_VERSION_CONFLICT`。
- 仅在成功提交时递增版本；审计与实体更新在同一 Unit of Work。

### 7. 跨域边界

- Identity 是 Subject 与 AI assignment 真相源。
- Organization 是 Membership 与层级真相源。
- Permission 是动作授权真相源；PHX-K07 定义 action/resource contract，策略求值深化归 PHX-K08。
- Event 发布与异步投递归 Shared Platform Capability / PHX-P11；PHX-K07 不内嵌 Event Bus 所有权。
- Organization 生命周期使用 terminal status 与时间戳保留历史，不执行物理删除；这是本域对通用软删除要求的显式等价实现。

## 后果

- 需要扩展 Organization 错误码、接口规格、状态机测试和 SQLAlchemy Repository。
- Foundation 中允许的循环层级、ENDED Membership 转移和暂停租户成员写入将被拒绝。
- 现有调用方更新实体时必须携带 `expected_version`；创建命令不需要版本。
- 集团 federation、企业合并拆分、自动级联及 primary admin 权限引导需独立协调规格，不得在本 ADR 中推断。

## 关联

- [BOOK02](../constitution/BOOK02.md)
- [BOOK19](../constitution/BOOK19.md)
- [Organization Interface](../architecture/ORGANIZATION_INTERFACE.md)
- [Kernel Data Model](../architecture/KERNEL_DATA_MODEL.md)
- [ADR-0019](ADR-0019-identity-organization-l2.md)
