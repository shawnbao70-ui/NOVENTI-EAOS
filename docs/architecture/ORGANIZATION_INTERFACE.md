# Organization Kernel 接口规格（细化）

**文档 ID：** IF-ORG-001  
**版本：** 1.0  
**阶段：** PHX-K07  
**状态：** Architecture / Interface Gate Accepted  
**仓库：** `NOVENTI-EAOS`

---

## 标题

Organization Kernel 接口规格

## 目的

细化租户、组织单元与成员关系接口，作为 PHX-K07 实现依据。

## 范围

L0 Tenant、L1 Organization Unit、L2 Membership 的接口、不变式、状态机与并发契约。Foundation Service、ORM、Repository 与事务接线已实现；PHX-K07 按本规格深化。

## 当前状态

**PHX-K07 L0–L2 接口与状态机基线已接受**

## 未来扩展

集团 federation、合并拆分流程、primary admin 权限引导与异步领域事件；这些能力需要 Workflow / Permission / Event 里程碑协调。

---

## 不变式

1. 每个企业/租户拥有独立身份与数据主权  
2. 跨租户成员关系默认禁止  
3. 组织角色标签 ≠ 权限授予（权限走 Permission Kernel）  
4. 所有写操作可审计并携带执行上下文  
5. Organization Unit 层级必须同租户且无环  
6. Tenant 非 active 时，Organization 数据面写操作 fail closed  
7. ended Membership 与 closed Tenant / Unit 是终态  
8. 更新命令必须携带 `expected_version` 并使用乐观锁  

---

## 接口明细

### L0–L2 Ownership

| 层级 | 实体 | 含义 |
|------|------|------|
| L0 | Tenant | 数据、权限、配置与运营的强隔离边界 |
| L0.5 | Enterprise | Tenant 内法人或组织主体；每 Tenant 一个 primary Enterprise |
| L1 | Organization Unit | Enterprise 内无环组织森林 |
| L2 | Membership | Subject 与 Enterprise / Unit 的受治理关系 |

### Org.CreateTenant

- **输入：** legal_name、region_policy_ref?  
- **输出：** tenant_id  
- **原子副作用：** 创建同名 primary Enterprise  
- **审计：** 是  
- **错误：** `ORG_TENANT_INVALID`、`ORG_TENANT_DUPLICATE_NAME`（若策略要求唯一）  
- **primary admin：** Explicit Defer；PHX-K08 bootstrap coordinator 显式编排 Membership 与 Permission Grant  

### Org.GetTenant

- **输入：** tenant_id  
- **输出：** 租户描述  
- **约束：** 跨租户读取默认 deny（经 Permission）  

### Org.SuspendTenant / Org.ReactivateTenant

- **输入：** tenant_id、reason、expected_version  
- **输出：** ok  
- **约束：** 属平台治理动作，必须高审计；对齐 BOOK01 限制条件  

### Org.CloseTenant

- **输入：** tenant_id、reason、expected_version  
- **输出：** ok  
- **约束：** 属高影响平台治理动作；存在 active Unit 或 Membership 时拒绝；closed 为终态  
- **实现状态：** Explicit Defer；等待 Workflow 人工审批与跨 Kernel 清理协调  

### Org.CreateEnterprise / Org.GetEnterprise / Org.ListEnterprises

- **输入：** legal_name / enterprise_id / 当前 trusted tenant context  
- **输出：** enterprise_id / Enterprise / Enterprises[]  
- **约束：** 跨 Tenant 隐藏为 not found；API/Runtime 先经 Permission  

### Org.SuspendEnterprise / Org.ReactivateEnterprise

- **输入：** enterprise_id、reason、expected_version
- **输出：** ok
- **约束：** active ↔ suspended；suspended Enterprise 不允许 Unit / Membership 写入

### Org.CloseEnterprise

- **输入：** enterprise_id、reason、expected_version
- **输出：** ok
- **约束：** active/suspended → closed；存在非 closed Unit 或 active/suspended Membership 时拒绝；primary Enterprise 随 Tenant 生命周期关闭

### Org.UpsertUnit

- **输入：** tenant_id、enterprise_id?、unit_id?、parent_unit_id?、unit_type、name、status、expected_version?  
- **输出：** unit_id  
- **约束：** enterprise_id 缺省为 primary Enterprise；创建时不传版本；更新时必须传 `expected_version`；parent 必须同 Tenant / Enterprise 且不得形成 self/cycle  

### Org.SetUnitStatus

- **输入：** unit_id、status（active / inactive / closed）、reason、expected_version  
- **输出：** ok  
- **约束：** closed 为终态；存在 active descendant 或 Membership 时拒绝关闭  

### Org.GetUnitTree

- **输入：** tenant_id、root_unit_id?  
- **输出：** 树形单元列表  

### Org.AddMembership

- **输入：** tenant_id、enterprise_id?、subject_id、org_unit_id?、membership_role_label?  
- **输出：** membership_id  
- **错误：** `ORG_CROSS_TENANT_FORBIDDEN`、`ORG_SUBJECT_INELIGIBLE`
- **约束：** enterprise_id 缺省为 primary Enterprise；主体必须存在且 active；租户主体 tenant_id 必须匹配；AI 必须具有同租户 active assignment；Unit 必须属于同一 Enterprise
- **审计：** 是  

### Org.RemoveMembership

- **输入：** membership_id、reason、expected_version  
- **输出：** ok  
- **约束：** active / suspended → ended；ended 不可再次修改  
- **审计：** 是

### Org.SuspendMembership / Org.ReactivateMembership

- **输入：** membership_id、reason、expected_version  
- **输出：** ok  
- **约束：** active ↔ suspended；Tenant 必须 active；ended 不可恢复  

### Org.ListMembership

- **输入：** tenant_id、subject_id?、org_unit_id?、status?  
- **输出：** memberships[]  

### Org.TransferMembershipUnit

- **输入：** membership_id、to_org_unit_id、expected_version  
- **输出：** ok  
- **约束：** 仅 active Membership 可同租户转移；目标 Unit 必须 active  

---

## 状态机

| 实体 | 允许转换 |
|------|----------|
| Tenant | active → suspended；suspended → active；active/suspended → closed |
| Organization Unit | active ↔ inactive；active/inactive → closed |
| Membership | active ↔ suspended；active/suspended → ended |

任何未列出的转换返回 `ORG_INVALID_STATE_TRANSITION`。

## 并发与错误

- 更新以 `id + tenant scope + expected_version` 为条件；冲突返回 `ORG_VERSION_CONFLICT`。
- 层级 self/cycle 返回 `ORG_UNIT_CYCLE_DETECTED`。
- 非 active Membership 的非法修改返回 `ORG_MEMBERSHIP_NOT_ACTIVE`。
- closed Tenant 写入返回 `ORG_TENANT_CLOSED`；suspended Tenant 写入返回 `ORG_TENANT_SUSPENDED`。
- active 下级对象阻止关闭时返回 `ORG_ACTIVE_DEPENDENCIES`。

---

## 与 Identity / Permission 的边界

| 关注点 | 归属 |
|--------|------|
| 主体是否存在 | Identity |
| 主体是否属于租户组织 | Organization |
| 主体能否执行动作 | Permission |

跨租户 AI 改派必须经 L2 Coordinator，在同一事务结束旧 membership 并创建新 assignment；目标 membership 不自动创建。

## 关联文档

- [KERNEL_DATA_MODEL.md](KERNEL_DATA_MODEL.md)
- [IDENTITY_INTERFACE.md](IDENTITY_INTERFACE.md)
- [PERMISSION_INTERFACE.md](PERMISSION_INTERFACE.md)
- [../constitution/BOOK02.md](../constitution/BOOK02.md)
- [../decisions/ADR-0022-organization-lifecycle-hierarchy.md](../decisions/ADR-0022-organization-lifecycle-hierarchy.md)
- [ORGANIZATION_STATE_MACHINES.md](ORGANIZATION_STATE_MACHINES.md)
- [ORGANIZATION_EVENTS.md](ORGANIZATION_EVENTS.md)
- [../api/organization.openapi.yaml](../api/organization.openapi.yaml)
