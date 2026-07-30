# Workflow Kernel 接口规格（细化）

**文档 ID：** IF-WORKFLOW-001  
**版本：** 1.0  
**阶段：** PHX-K09  
**状态：** Architecture / Interface Gate Accepted  
**仓库：** `NOVENTI-EAOS`

---

## 标题

Workflow Kernel 接口规格

## 目的

细化流程定义、实例、审批、信号、升级、取消与补偿接口，作为 PHX-K09 实现依据，并支撑 AI 人工审批双闸门（ADR-0008 / ADR-0024）。

## 范围

Definition 生命周期、Instance / Task 状态机、批准绑定、并发与幂等、SLA、补偿最小语义、OpenAPI 与事件目录。Foundation Service、ORM、Repository 与事务接线已实现；PHX-K09 按本规格深化。

## 当前状态

**PHX-K09 审批唯一真相源接口与状态机基线已接受**

## 未来扩展

完整 PDL 解释器、多图编排引擎、生产级 timer worker、可靠 event outbox（PHX-P11）、Smart Terminal Approval UX（PHX-T13）、CloseTenant 跨 Kernel 清理执行器。

---

## 不变式

1. Workflow Kernel 是审批、路由、任务、升级与补偿的唯一流程真相源  
2. 业务包、Smart Terminal、AI Runtime 不得维护平行审批状态  
3. Permission allow 与 Workflow approval 是独立双闸门；allow 永不替代 approval  
4. 流程实例状态可查询、可审计、可追溯  
5. Instance / Task 更新必须携带 `expected_version` 并使用乐观锁  
6. Signal 必须携带 `idempotency_key`；同键同指纹重放，同键不同指纹冲突  
7. API 不接受客户端声明 `tenant_id`、`session_id`、`platform_scope` 或 `execution_context`  
8. 所有操作绑定 trusted ExecutionContext 中的 tenant_id 与 correlation_id  

---

## 核心概念

| 概念 | 说明 |
|------|------|
| Definition | 流程定义（版本化；ACTIVE 文档不可变） |
| Instance | 运行中的流程实例（含 approval binding） |
| Task | 人工/系统审批任务（含 `due_at` SLA） |
| Signal | 外部信号推进（强制幂等） |
| Approval Binding | principal + action + resource_ref；可选 plan_version / scope / expires_at |
| Compensation | 显式 compensating → compensated 路径；非 2PC |

---

## Ports（外部真相源）

| Port | 职责 | 归属 |
|------|------|------|
| `PermissionEvaluator` | 各 Workflow 动作是否 allow | Permission |
| `PrincipalEligibility` | 审批人与 assignee 是否 active | Identity |
| `ScopeResolver` | 资源引用是否属于 Tenant | Organization |

缺失、未知或 error 时全部 fail closed。

---

## 接口明细

### Workflow.CreateDefinition

- **HTTP：** `POST /workflow/definitions`  
- **输入：** name、definition_document_ref、version  
- **输出：** definition_id（ACTIVE）  
- **约束：** `(tenant|platform, name, version)` 唯一；需 definition 管理权限  
- **审计：** 是  
- **错误：** `WORKFLOW_DEFINITION_INVALID`、`WORKFLOW_DEFINITION_CONFLICT`  

### Workflow.DeprecateDefinition

- **HTTP：** `POST /workflow/definitions/{definitionId}/deprecation`  
- **输入：** reason、expected_version  
- **输出：** ok  
- **约束：** ACTIVE → DEPRECATED；DEPRECATED 不可 start  
- **审计：** 是  

### Workflow.StartInstance

- **HTTP：** `POST /workflow/instances`  
- **输入：** definition_id、payload、business_key?、approval_principal_id?、approval_action?、approval_resource_ref?、approval_plan_version?、approval_scope?、approval_expires_at?、approval_subject_id?、due_at?  
- **输出：** instance_id、status、task_id?  
- **前置：** Permission.Evaluate 允许 `workflow.instance.start`  
- **约束：** principal / action / resource_ref 三者必须同时出现或同时省略；`approval_subject_id` 存在时进入 `pending_approval` 并创建 Task；同租户活跃 `business_key` 唯一  
- **审计：** 是  
- **错误：** `WORKFLOW_DEFINITION_NOT_FOUND`、`WORKFLOW_BUSINESS_KEY_CONFLICT`  

### Workflow.GetInstance

- **HTTP：** `GET /workflow/instances/{instanceId}`  
- **输入：** instance_id  
- **输出：** 实例状态、binding、current_task_id、payload、version  
- **前置：** Permission.Evaluate 允许 `workflow.instance.read`  

### Workflow.SignalInstance

- **HTTP：** `POST /workflow/instances/{instanceId}/signals`  
- **输入：** signal_name、idempotency_key、payload?、expected_version  
- **输出：** status  
- **约束：** 同键同指纹重放成功；同键不同指纹 `WORKFLOW_SIGNAL_CONFLICT`；并发同键同指纹收敛为幂等成功  
- **审计：** 是  

### Workflow.ApproveTask / Workflow.RejectTask

- **HTTP：** `POST .../approval` / `POST .../rejection`  
- **输入：** comment? 或 reason、expected_instance_version、expected_task_version  
- **输出：** status  
- **约束：** Instance 必须 `pending_approval`；Task 必须 `pending` 且为 `current_task_id`；assignee 必须匹配 caller；逾期不得视为批准  
- **前置：** Permission.Evaluate 允许 `workflow.task.approve` / `workflow.task.reject`  
- **审计：** 是  
- **错误：** `WORKFLOW_TASK_NOT_ASSIGNEE`、`WORKFLOW_APPROVAL_EXPIRED`  

### Workflow.EscalateTask

- **HTTP：** `POST .../escalation`  
- **输入：** to_subject_id、reason、expected_instance_version、expected_task_version  
- **输出：** status  
- **约束：** 仅 `pending_approval` + Task `pending`；改派 assignee  
- **前置：** Permission.Evaluate 允许 `workflow.task.escalate`  

### Workflow.CancelInstance

- **HTTP：** `POST /workflow/instances/{instanceId}/cancellation`  
- **输入：** reason、expected_version  
- **输出：** status  
- **约束：** 终态不可取消；取消权限受控  
- **错误：** `WORKFLOW_CANCEL_FORBIDDEN`、`WORKFLOW_INVALID_STATE`  

### Workflow.CompensateInstance

- **HTTP：** `POST /workflow/instances/{instanceId}/compensation`  
- **输入：** reason、expected_version  
- **输出：** status  
- **约束：** 仅允许的路径进入 `compensating → compensated`；不撤销 Permission Grant  

### Workflow.ListTasks

- **HTTP：** `GET /workflow/tasks?assignee_subject_id=&status=`  
- **输入：** assignee_subject_id?、status?（默认 caller 自己）  
- **输出：** tasks[]  
- **约束：** 查询他人任务需 `workflow.task.read_all`  

### Workflow.VerifyApprovedAction

- **意图：** AI 高影响提交前验证审批  
- **输入：** `approval_ref`（ExecutionContext）、action、resource_ref  
- **输出：** 是否允许提交  
- **约束：** 必须 APPROVED；principal + action + resource_ref 完全匹配；`approval_plan_version` / `approval_scope` / `approval_expires_at` 若存在则强制匹配；过期返回 `WORKFLOW_APPROVAL_EXPIRED`  

---

## 状态机

| 实体 | 允许转换 |
|------|----------|
| Definition | active → deprecated |
| Instance | running / pending_approval / approved / rejected / cancelled / completed / compensating / compensated（见状态机文档） |
| Task | pending → approved / rejected / cancelled；pending → pending（escalate） |

任何未列出的转换返回 `WORKFLOW_INVALID_STATE`。

## 并发与错误

- Instance / Task 更新以 `expected_version` 为条件；冲突返回 `WORKFLOW_VERSION_CONFLICT`。
- 活跃 `business_key` 冲突返回 `WORKFLOW_BUSINESS_KEY_CONFLICT`。
- Signal 缺少幂等键返回 `WORKFLOW_IDEMPOTENCY_REQUIRED`。
- 跨 Tenant 操作返回 `WORKFLOW_CROSS_TENANT_FORBIDDEN`。

---

## 与 Identity / Organization / Permission 的边界

| 关注点 | 归属 |
|--------|------|
| 主体是否存在 / active | Identity |
| Tenant / Resource 归属 | Organization |
| 动作是否 allow | Permission |
| 高影响动作人工批准 | Workflow（Permission allow 不替代） |

Membership role label 不直接产生 Workflow 任务；Workflow 不复制 Permission 决策。

---

## 与 AI Runtime 集成

```text
AI.RequestApproval → Workflow.StartInstance(approval binding + approval_subject_id)
Human Approve/Reject → Workflow.ApproveTask / RejectTask
Permission.Evaluate → allow
Workflow.VerifyApprovedAction → binding match + not expired
AI.CommitAction 仅在双闸门通过后允许
```

CloseTenant 执行前必须存在已批准实例，绑定动作 `organization.tenant.close` 与对应 tenant 资源（ADR-0024）。

---

## 关联文档

- [KERNEL_DATA_MODEL.md](KERNEL_DATA_MODEL.md)
- [IDENTITY_INTERFACE.md](IDENTITY_INTERFACE.md)
- [ORGANIZATION_INTERFACE.md](ORGANIZATION_INTERFACE.md)
- [PERMISSION_INTERFACE.md](PERMISSION_INTERFACE.md)
- [../decisions/ADR-0024-workflow-approval-truth.md](../decisions/ADR-0024-workflow-approval-truth.md)
- [../decisions/ADR-0008-ai-human-approval.md](../decisions/ADR-0008-ai-human-approval.md)
- [WORKFLOW_STATE_MACHINES.md](WORKFLOW_STATE_MACHINES.md)
- [WORKFLOW_EVENTS.md](WORKFLOW_EVENTS.md)
- [../api/workflow.openapi.yaml](../api/workflow.openapi.yaml)
- [../project/PHX-K09_ARCHITECTURE_GATE.md](../project/PHX-K09_ARCHITECTURE_GATE.md)
