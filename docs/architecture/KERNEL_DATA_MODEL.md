# Kernel 数据模型草案

**文档 ID：** DM-KERNEL-001  
**版本：** 0.2  
**阶段：** PHX-004 持久化实现  
**状态：** Shared Audit / Identity / Organization / Permission / Workflow / Event 已映射  
**仓库：** `NOVENTI-EAOS`

---

## 标题

EAOS Kernel 概念数据模型

## 目的

定义 Identity、Organization、Permission 核心实体、关系与不变式，并指导独立 ORM 映射。

## 范围

**范围内：** 概念实体、字段意图、关系、租户范围、审计/软删字段。  
**范围外：** 遗留表映射；未进入当前持久化切片的域。

## 当前状态

**核心持久化域已通过 Alembic `0002`–`0010` 落地**

## 未来扩展

Knowledge 存储模型；物理隔离 vs 逻辑隔离 ADR；PHX-P11 异步投递模型。

---

## 1. 公共字段约定

所有租户作用域实体默认包含：

| 字段 | 类型意图 | 说明 |
|------|----------|------|
| `id` | UUID | 主键 |
| `tenant_id` | UUID | 租户（平台级实体可空，见下） |
| `created_at` | datetime UTC | 创建 |
| `updated_at` | datetime UTC | 更新 |
| `deleted_at` | datetime UTC? | 软删除 |
| `version` | int | 乐观锁 |
| `status` | enum | 生命周期 |
| `created_by` | UUID? | 主体 |
| `updated_by` | UUID? | 主体 |

**平台级实体**（如全局 AI 员工身份主记录）：`tenant_id` 可空，但派驻/授权记录必须有 `tenant_id`。

---

## 2. Identity 域

### 2.1 `subjects`

| 字段 | 说明 |
|------|------|
| `id` | 主体 UUID（全球唯一） |
| `subject_type` | `human` / `ai_employee` / `service` / `device` / `application` / `plugin` |
| `display_name` | 显示名 |
| `is_platform_managed` | AI 等是否平台统一管理 |
| `status` | `active` / `archived` / `revoked` |

**不变式：** 身份不因改派而销毁；AI 身份永久。

### 2.2 `subject_external_refs`

| 字段 | 说明 |
|------|------|
| `id` | UUID |
| `subject_id` | FK → subjects |
| `system` | 外部系统标识 |
| `external_id` | 外部 ID |
| 唯一 | `(system, external_id)` |

### 2.3 `credentials`

| 字段 | 说明 |
|------|------|
| `id` | UUID |
| `subject_id` | FK |
| `tenant_id` | 凭证租户边界 |
| `credential_kind` | password_hash / key_handle / oidc / … |
| `secret_handle` | 句柄或哈希，非明文 |
| `expires_at` | 可选 |
| `status` | active / revoked |

### 2.4 `sessions`

| 字段 | 说明 |
|------|------|
| `id` | UUID |
| `subject_id` | FK |
| `tenant_id` | 会话租户边界 |
| `credential_id` | 可空 FK；PHX-006 新会话必须绑定 Credential |
| `expires_at` | 过期 |
| `revoked_at` | 可选 |
| `correlation_id_at_issue` | 签发关联 |

### 2.5 `ai_assignments`

| 字段 | 说明 |
|------|------|
| `id` | UUID |
| `ai_subject_id` | FK → subjects (ai_employee) |
| `tenant_id` | 派驻租户 |
| `mode` | assign / reassign / inherit / archive |
| `management_policy` | 租户侧管理策略引用 |
| `predecessor_assignment_id` | INHERIT 模式的前序 assignment self-FK |
| `effective_from` / `effective_to` | 有效期 |

**不变式：** 每个 AI 全局最多一个 active assignment；INHERIT 只继承谱系，知识与权限不随 assignment 复制。

### 2.6 `ai_employee_profiles`

| 字段 | 说明 |
|------|------|
| `ai_subject_id` | PK / FK → subjects；与 AI Subject 一对一 |
| `capabilities_profile_ref` | capability profile 策略引用 |
| `owner_policy_ref` | owner policy 策略引用 |
| `version` | 乐观锁版本 |
| `created_at` / `updated_at` | 审计时间 |

**不变式：** Identity 仅保存引用；Permission Kernel 是实际授权真相源。

### 2.7 `platform_identity_governors`

- 平台作用域 Governor 授权历史，无 tenant_id
- 同一 subject 最多一条 active 授权
- 保存 granted/revoked 主体、时间与撤销原因
- 禁止撤销最后一个 active Governor

---

## 3. Organization 域

### 3.1 `tenants`

| 字段 | 说明 |
|------|------|
| `id` | 租户 UUID |
| `legal_name` | 法定/组织名 |
| `status` | active / suspended / closed |
| `region_policy_ref` | 驻留/法域策略引用 |
| `version` | 乐观锁版本 |

### 3.2 `enterprises`

| 字段 | 说明 |
|------|------|
| `id` | Enterprise UUID |
| `tenant_id` | 强隔离边界 FK |
| `legal_name` | 法定/组织名称；Tenant 内大小写不敏感唯一 |
| `status` | active / suspended / closed |
| `is_primary` | 每 Tenant 至多一个 primary |
| `version` | 乐观锁版本 |

**不变式：** Tenant 与 Enterprise 是不同概念；Tenant 是隔离边界，Enterprise 是边界内法人或组织主体。

### 3.3 `org_units`

| 字段 | 说明 |
|------|------|
| `id` | UUID |
| `tenant_id` | 必填 |
| `enterprise_id` | 必填；FK → enterprises |
| `parent_unit_id` | 可选自引用 |
| `unit_type` | hq / group / branch / department / other |
| `name` | 名称 |
| `status` | active / inactive / closed |
| `version` | 乐观锁版本 |

**不变式：** 同租户森林；每个节点最多一个 parent；parent 不得是自身或后代。

### 3.4 `memberships`

| 字段 | 说明 |
|------|------|
| `id` | UUID |
| `tenant_id` | 必填 |
| `enterprise_id` | 必填；FK → enterprises |
| `subject_id` | FK → subjects |
| `org_unit_id` | 可选 |
| `membership_role_label` | 组织角色标签（非权限真相源） |
| `status` | active / suspended / ended |
| `ended_at` | 结束时间 |
| `version` | 乐观锁版本 |

**不变式：** 禁止跨租户 membership；同一 Subject 每个 Unit 最多一个 active Membership，企业级 Membership 最多一个 active；权限以 Permission 域为准；ended 为终态。

### 3.5 Organization 乐观锁

Tenant、Enterprise、Organization Unit 与 Membership 更新必须提供 `expected_version`。Repository 以当前版本为更新条件，成功后版本加一；零行更新返回 `ORG_VERSION_CONFLICT`。

---

## 4. Permission 域

### 4.1 `policies`

**映射状态：** PHX-K08 契约已接受；ORM / Alembic 随 Slice B 落地。

| 字段 | 说明 |
|------|------|
| `id` | UUID |
| `tenant_id` | 租户策略；平台基线策略可另册 |
| `name` | 名称 |
| `policy_version` | 乐观锁版本；Activate / Deprecate 递增 |
| `status` | draft / active / deprecated |
| `created_at` / `updated_at` | 审计时间 |

**不变式：** ACTIVE 版本不可原地修改；DEPRECATED 不参与 Evaluate。

### 4.2 `policy_rules`

| 字段 | 说明 |
|------|------|
| `id` | UUID |
| `policy_id` | 所属 Policy |
| `tenant_id` | 租户隔离 |
| `effect` | allow / deny |
| `actions` | 动作集合 |
| `resource_type` | 资源类型 |
| `scope_level` | resource / org_unit / enterprise / tenant |
| `scope_ref_id` | Org Unit / Enterprise / Resource 引用（tenant scope 可空） |
| `condition_ref` | 条件引用 |
| `rule_order` | 稳定排序 |

**不变式：** Rule 随 Policy 版本不可变发布；禁止 Kernel 内执行任意脚本 / SQL / 动态代码。

### 4.3 `grants`

**映射状态：** Foundation 已映射；PHX-K08 扩展 Scope、Delegation 与乐观锁字段。

| 字段 | 说明 |
|------|------|
| `id` | UUID |
| `tenant_id` | 必填 |
| `principal_subject_id` | 主体 |
| `resource_type` | 资源类型 |
| `resource_id` | 可选（范围授权可空） |
| `scope_level` | resource / org_unit / enterprise / tenant |
| `scope_ref_id` | Scope 引用 |
| `actions` | 动作集合 |
| `conditions_ref` | 条件 |
| `expires_at` | 可选 |
| `status` | active / revoked |
| `version` | 乐观锁；Revoke / Delegate 前置校验 |
| `parent_grant_id` | Delegation 父 Grant（Direct Grant 为空） |
| `delegable` | 是否允许委派 |
| `delegation_depth_remaining` | 剩余委派深度 |
| `delegated_by_subject_id` | 委派者（Direct Grant 为空） |

**不变式：** Delegation 子 Grant 的 actions / scope / expiry / depth 不得宽于父 Grant；父链失效时子 Grant 立即不生效。

### 4.4 `permission_decisions`（审计导向）

| 字段 | 说明 |
|------|------|
| `id` | UUID（decision_id / audit_id） |
| `tenant_id` | 必填 |
| `principal_subject_id` | 主体 |
| `action` | 动作 |
| `resource_type` / `resource_id` | 资源 |
| `effect` | allow / deny |
| `reason_code` | 原因码 |
| `policy_version` | 当时策略版本 |
| `correlation_id` | 关联 |
| `decided_at` | 时间 |
| `evidence_json` | matched policy / grant / rule 引用、scope trace、condition outcome 摘要（Explain 用；不含秘密） |

**不变式：** 默认拒绝；Evaluate 为唯一运行时真相入口；Explain 不得暴露跨 Tenant 资源存在性。

---

## 5. Workflow 域

### 5.1 `workflow_definitions`

**映射状态：** Foundation 已映射；PHX-K09 契约已接受。

| 字段 | 说明 |
|------|------|
| `id` | UUID |
| `tenant_id` | 租户定义必填；平台级定义可空 |
| `name` | 名称；同 scope 内与 version 唯一 |
| `document_ref` | 不可变定义文档引用 |
| `version` | 定义版本字符串（非乐观锁） |
| `status` | active / deprecated |
| `created_at` | 审计时间 |

**不变式：** ACTIVE 文档引用不可变；DEPRECATED 不可 start；`(tenant|platform, name, version)` 唯一。

### 5.2 `workflow_instances`

| 字段 | 说明 |
|------|------|
| `id` | UUID |
| `definition_id` | FK → workflow_definitions |
| `tenant_id` | 必填 |
| `initiator_subject_id` | 发起人 |
| `status` | running / pending_approval / approved / rejected / cancelled / completed / compensating / compensated |
| `payload` | JSON 业务上下文 |
| `business_key` | 可选；同租户活跃实例唯一 |
| `current_task_id` | 当前审批任务 |
| `approval_principal_subject_id` | 批准绑定主体 |
| `approval_action` | 批准绑定动作 |
| `approval_resource_ref` | 批准绑定资源引用 |
| `approval_plan_version` | 可选；提供后强制匹配 |
| `approval_scope` | 可选；提供后强制匹配 |
| `approval_expires_at` | 可选；过期后批准失效 |
| `version` | 乐观锁；Signal / Cancel / Compensate / Approve 前置校验 |
| `created_at` / `updated_at` | 审计时间 |

**不变式：** principal / action / resource_ref 必须同时出现或同时省略；`approval_subject_id` 启动时创建 Task 并进入 pending_approval；compensating → compensated 为显式补偿路径。

### 5.3 `workflow_tasks`

| 字段 | 说明 |
|------|------|
| `id` | UUID |
| `instance_id` / `tenant_id` | 复合 FK → workflow_instances |
| `assignee_subject_id` | 审批处理人 |
| `status` | pending / approved / rejected / cancelled |
| `due_at` | 可选 SLA 截止时间 |
| `decision_comment` | 审批/拒绝备注 |
| `escalated_from_subject_id` | 升级前 assignee |
| `version` | 乐观锁；Approve / Reject / Escalate 前置校验 |
| `created_at` / `updated_at` | 审计时间 |

**不变式：** Escalate 仅 pending 任务；逾期不得视为已批准；Approve 必须匹配 Instance `current_task_id`。

### 5.4 `workflow_signal_receipts`

| 字段 | 说明 |
|------|------|
| `instance_id` / `tenant_id` | 所属实例 |
| `idempotency_key` | 客户端幂等键 |
| `request_fingerprint` | signal_name + payload 指纹 |
| `resulting_status` | 首次处理后的实例状态 |
| `processed_at` | 处理时间 |

**不变式：** 同键同指纹重放；同键不同指纹冲突；并发同键同指纹收敛为幂等成功。

### 5.5 `workflow_history`

| 字段 | 说明 |
|------|------|
| `id` | UUID |
| `instance_id` / `tenant_id` | 所属实例 |
| `action` | started / approved / rejected / escalated / cancelled / completed / compensated 等 |
| `subject_id` | 操作主体 |
| `correlation_id` | 关联 |
| `timestamp` | 时间 |
| `details` | JSON 摘要 |

---

## 6. Knowledge 域（Shared Platform Capability）

**映射状态：** PHX-K10 已映射；所有权属 Shared，表复用 `kernel` schema。

### 6.1 `knowledge_entities`

| 字段 | 说明 |
|------|------|
| `id` | UUID |
| `tenant_id` | 必填 |
| `entity_type` / `name` | 活跃态同租户唯一（大小写不敏感） |
| `layer` | canonical / operational / documentary / derived |
| `status` | active / archived |
| `attributes` / `labels` | JSON；禁止秘密字段 |
| `shared_with_subject_ids` | 租户内共享主体列表 |
| `retain_until` | 可选；到期读取 fail-closed |
| `version` | 乐观锁 |
| `created_at` / `updated_at` | 审计时间 |

**不变式：** derived 不得原地伪装为 canonical；写入必留 provenance。

### 6.2 `knowledge_links`

| 字段 | 说明 |
|------|------|
| `id` | UUID |
| `tenant_id` | 必填 |
| `from_entity_id` / `to_entity_id` | FK → knowledge_entities；禁止自环 |
| `relation_type` | 关系类型 |
| `status` | active / archived |
| `attributes` | JSON |
| `version` | 乐观锁 |
| `created_at` / `updated_at` | 审计时间 |

### 6.3 `knowledge_provenance`

| 字段 | 说明 |
|------|------|
| `id` | UUID |
| `tenant_id` | 必填 |
| `subject_kind` | entity / link |
| `subject_id` | 目标 ID |
| `actor_subject_id` | 写入主体 |
| `source_ref` / `reason` | 出处 |
| `derived` | 是否派生 |
| `recorded_at` | 时间 |
| `details` | JSON 摘要 |

**不变式：** append-only；无更新/删除。

---

## 7. 关系总览

```text
tenants 1─* org_units
tenants 1─* memberships *─1 subjects
subjects 1─* credentials
subjects 1─* sessions
subjects(ai) 1─* ai_assignments *─1 tenants
tenants 1─* grants *─1 subjects
tenants 1─* policies 1─* policy_rules
grants 1─* grants (delegation parent chain)
grants / evaluate ──▶ permission_decisions (audit + evidence_json)
tenants 1─* workflow_definitions
workflow_definitions 1─* workflow_instances 1─* workflow_tasks
workflow_instances 1─* workflow_signal_receipts
workflow_instances 1─* workflow_history
tenants 1─* knowledge_entities 1─* knowledge_links
tenants 1─* knowledge_provenance
tenants 1─* events 1─* event_deliveries
tenants 1─* event_subscriptions
tenants 1─* event_outbox
events 1─* event_dead_letters
tenants 1─* ai_agent_runs 1─* ai_memory_entries
tenants 1─* ai_tool_declarations
```

---

## 8. Event Delivery 域（PHX-P11）

### 8.1 `event_outbox`

| 字段 | 说明 |
|------|------|
| `id` | Outbox 行 ID |
| `tenant_id` | 租户 |
| `event_id` | 预分配事件 ID（唯一） |
| `event_name` / `schema_version` / `producer` / `payload` | 信封字段 |
| `correlation_id` | 关联 |
| `status` | pending / leased / dispatched / dead |
| `attempt_count` / `available_at` | 重试与退避 |
| `leased_until` / `leased_by` | Worker 租约 |
| `last_error_code` | 最近失败 |

### 8.2 `event_dead_letters`

| 字段 | 说明 |
|------|------|
| `id` | DLQ ID |
| `tenant_id` / `event_id` / `subscriber_id` | 失败投递定位 |
| `reason` / `attempt_count` | 失败摘要 |
| `created_at` / `replayed_at` | 生命周期 |

**不变式：** 未重放条目对 `(tenant, event, subscriber)` 唯一；重放需 `replay` 权限。

### 8.3 `event_deliveries` 状态扩展

`status` ∈ {delivered, failed, dead}

## 9. AI Runtime 域（PHX-A12）

### 9.1 `ai_agent_runs`

| 字段 | 说明 |
|------|------|
| `id` / `tenant_id` / `subject_id` | 运行与 AI 主体 |
| `goal` / `plan_summary` | 目标与计划摘要 |
| `status` | planned / running / pending_approval / completed / failed / cancelled |
| `approval_ref` | Workflow instance id |
| `version` | 乐观锁 |

### 9.2 `ai_tool_declarations`

| 字段 | 说明 |
|------|------|
| `tenant_id` / `name` | 租户内唯一（大小写不敏感） |
| `high_impact` | 是否要求审批桥 |

### 9.3 `ai_memory_entries`

| 字段 | 说明 |
|------|------|
| `run_id` / `key` | run 作用域记忆 |
| `value` | JSON；禁止秘密字段 |

## 10. 当前物理映射

- PostgreSQL schema：`kernel`
- 映射表：Audit、Identity、Organization、Permission、Workflow、Knowledge、Event、AI Runtime
- Domain Model 与 SQLAlchemy Model 分离
- 迁移：`0002_shared_audit_identity` 至 `0016_ai_runtime_a12`

Event Bus 物理表：

- `events`：不可变事件事实与 JSONB payload
- `event_subscriptions`：租户绑定订阅元数据，不保存 Python handler
- `event_deliveries`：按 `(event_id, subscriber_id)` 保存 delivered/failed/dead
- `event_outbox`：Transactional Outbox
- `event_dead_letters`：死信队列

## 11. 明确非目标

- 不映射遗留 ERP 表结构  
- 外部 Broker 与多区域 failover 表延后
- Knowledge / Memory 向量索引与摄入管线表延后
- LLM 提供商与提示词库表延后

## 关联文档

- [IDENTITY_INTERFACE.md](IDENTITY_INTERFACE.md)
- [PERMISSION_INTERFACE.md](PERMISSION_INTERFACE.md)
- [ORGANIZATION_INTERFACE.md](ORGANIZATION_INTERFACE.md)
- [WORKFLOW_INTERFACE.md](WORKFLOW_INTERFACE.md)
- [KNOWLEDGE_INTERFACE.md](KNOWLEDGE_INTERFACE.md)
- [../standards/DATABASE_STANDARD.md](../standards/DATABASE_STANDARD.md)
- [../decisions/ADR-0007-tenant-isolation.md](../decisions/ADR-0007-tenant-isolation.md)
- [KERNEL_CONTRACT_TEST_PLAN.md](KERNEL_CONTRACT_TEST_PLAN.md)
