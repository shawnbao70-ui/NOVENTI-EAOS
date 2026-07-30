# Permission Kernel 接口规格（细化）

**文档 ID：** IF-PERMISSION-001  
**版本：** 1.0  
**阶段：** PHX-K08  
**状态：** Architecture / Interface Gate Accepted  
**仓库：** `NOVENTI-EAOS`

---

## 标题

Permission Kernel 接口规格

## 目的

细化 Policy、Scope、Delegation、Grant、Evaluate 与 Explain 接口，作为 PHX-K08 实现依据。

## 范围

类型化 Policy / Rule、Direct Grant、Delegation、统一求值、Explain 与 ListEffective 的接口、不变式、状态机与并发契约。Foundation Service、ORM、Repository 与事务接线已实现；PHX-K08 按本规格深化。

## 当前状态

**PHX-K08 Policy / Scope / Delegation / Explain 接口与状态机基线已接受**

## 未来扩展

通用脚本策略语言、Role/Group 自动展开、平台跨 Tenant break-glass 与可靠 Permission domain event outbox；这些能力需要 Workflow / Event 里程碑协调。

---

## 不变式

1. 权限统一计算（单一真相源）；`Permission.Evaluate` 是运行时唯一入口  
2. 默认拒绝；explicit deny overrides  
3. 决策可审计、可解释；Explain 不泄露秘密  
4. 业务包不得平行实现授权真相源  
5. AI / 人类 / 服务主体一体纳入求值  
6. Scope 不得跨 Tenant；Enterprise / Org Unit 必须经 Organization Scope Resolver 验证  
7. `conditions_ref` 未解析或 false 时 Grant 不生效  
8. Delegation 只能缩小 scope / actions / depth；禁止循环  
9. 更新命令必须携带 `expected_version` 并使用乐观锁  
10. API 不接受客户端声明 `tenant_id`、`session_id`、`platform_scope` 或 caller `subject_id` 作为安全上下文  

---

## 核心概念

| 概念 | 说明 |
|------|------|
| Principal | 主体（subject_id + type）；资格由 Identity 证明 |
| Resource | 资源描述符（type + id + tenant_id）；由 Runtime 构造受信 descriptor |
| Action | 动作（如 `read` / `write` / `approve` / `invoke_tool`） |
| Effect | `allow` / `deny` |
| Policy | 可版本化、不可变发布的类型化 Rule 集合 |
| Scope | `resource < org_unit < enterprise < tenant` |
| Grant | 管理员签发的显式 ALLOW entitlement 或 Delegation 派生 Grant |
| Delegation | 带 `parent_grant_id` 的子 Grant；父链持续有效 |

---

## Ports（外部真相源）

| Port | 职责 | 归属 |
|------|------|------|
| `PrincipalEligibility` | 证明 Principal active 且具备同 Tenant 资格 | Identity |
| `ScopeResolver` | 验证 Tenant / Enterprise / Org Unit ancestry 与 Resource 归属 | Organization |
| `ConditionEvaluator` | 解析 `condition_ref` 并返回 true / false / unresolved | 受信条件服务（Kernel port） |

缺失、未知或 error 时全部 fail closed。

---

## 接口明细

### Permission.CreatePolicy

- **输入：** name、rules[]（PolicyRule：effect、actions、resource_type、scope_level、scope_ref_id?、condition_ref?）  
- **输出：** policy_id（DRAFT）  
- **审计：** 是  
- **错误：** `PERMISSION_POLICY_INVALID`  

### Permission.ActivatePolicy / Permission.DeprecatePolicy

- **输入：** policy_id、reason、expected_version  
- **输出：** ok  
- **约束：** DRAFT → ACTIVE；ACTIVE → DEPRECATED；DEPRECATED 终态  
- **审计：** 是  

### Permission.CreateGrant

- **输入：** principal_id、resource_type、resource_id?、scope_level、scope_ref_id?、actions[]、conditions_ref?、expires_at?、delegable?、delegation_depth?  
- **输出：** grant_id  
- **约束：** Principal 必须 eligible；Scope 必须经 ScopeResolver 验证  
- **审计：** 是  
- **错误：** `PERMISSION_PRINCIPAL_INELIGIBLE`、`PERMISSION_SCOPE_INVALID`  

### Permission.RevokeGrant

- **输入：** grant_id、reason、expected_version  
- **输出：** ok  
- **约束：** ACTIVE → REVOKED；REVOKED 终态  
- **审计：** 是  

### Permission.DelegateGrant

- **输入：** parent grant_id、delegatee_principal_id、scope_level、scope_ref_id?、actions[]、expires_at?、expected_version  
- **输出：** delegated grant_id  
- **约束：** 父 Grant 必须 delegable；actions / scope / expiry / depth 只能缩小；禁止循环  
- **审计：** 是  
- **错误：** `PERMISSION_DELEGATION_TOO_BROAD`、`PERMISSION_DELEGATION_CYCLE`  

### Permission.Evaluate

- **输入：** action、resource_type、resource_id?（Principal 与 Tenant 来自 trusted ExecutionContext）  
- **输出：** `{ decision_id, effect, reason_code, policy_version }`  
- **合并：** explicit deny overrides → allow → default deny  
- **审计：** 是（副作用路径必审；高频只读可采样，策略后续 ADR）  
- **约束：** 无有效 Identity / Tenant / Scope / Policy / Condition 时 deny  

### Permission.Explain

- **输入：** decision_id  
- **输出：** matched policy / grant references、scope trace、condition outcome 摘要；不含秘密  
- **可见性：** self-only；受信 evaluation proxy / permission auditor 可读授权范围内决策  
- **审计：** 可选  

### Permission.ListEffective

- **输入：** subjectId（path；被查询 Principal，非 caller 身份）  
- **输出：** effective permissions[]  
- **约束：** 仅返回已验证父链、expiry、condition 与 Scope 后的有效权限；调用方默认只能查询自己  

---

## 状态机

| 实体 | 允许转换 |
|------|----------|
| Policy | draft → active；active → deprecated |
| Grant | active → revoked；expires / parent invalid 为读取时 inactive |

任何未列出的转换返回 `PERMISSION_INVALID_STATE_TRANSITION`。

## 并发与错误

- 更新以 `id + tenant scope + expected_version` 为条件；冲突返回 `PERMISSION_VERSION_CONFLICT`。
- 跨 Tenant grant / scope 返回 `PERMISSION_CROSS_TENANT_FORBIDDEN`。
- condition unresolved / false 返回 `PERMISSION_CONDITION_DENIED`。
- Explain / ListEffective 越权返回 `PERMISSION_VISIBILITY_DENIED`。

---

## 与 Identity / Organization / Workflow 的边界

| 关注点 | 归属 |
|--------|------|
| 主体是否存在 / active | Identity |
| Org Unit / Enterprise ancestry | Organization |
| 动作是否允许 | Permission |
| 高影响动作人工批准 | Workflow（Permission allow 不替代） |

Membership role label、Workflow approval 与 AI assignment 均不直接产生 Permission。

---

## 与 AI 集成

- AI 工具调用前必须 `Evaluate(action=invoke_tool, …)`  
- 高影响动作即使 allow，仍可能需 ADR-0008 人工批准  
- 审批通过不自动等于永久提权  

---

## 关联文档

- [KERNEL_DATA_MODEL.md](KERNEL_DATA_MODEL.md)
- [IDENTITY_INTERFACE.md](IDENTITY_INTERFACE.md)
- [ORGANIZATION_INTERFACE.md](ORGANIZATION_INTERFACE.md)
- [../decisions/ADR-0023-permission-policy-scope-delegation.md](../decisions/ADR-0023-permission-policy-scope-delegation.md)
- [../decisions/ADR-0007-tenant-isolation.md](../decisions/ADR-0007-tenant-isolation.md)
- [../decisions/ADR-0008-ai-human-approval.md](../decisions/ADR-0008-ai-human-approval.md)
- [PERMISSION_STATE_MACHINES.md](PERMISSION_STATE_MACHINES.md)
- [PERMISSION_EVENTS.md](PERMISSION_EVENTS.md)
- [../api/permission.openapi.yaml](../api/permission.openapi.yaml)
- [../project/PHX-K08_ARCHITECTURE_GATE.md](../project/PHX-K08_ARCHITECTURE_GATE.md)
