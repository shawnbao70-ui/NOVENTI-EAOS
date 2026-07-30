# Workflow Overlay — Legacy Knowledge

**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0`（只读）  
**Boundary:** 本文只描述 Legacy 叠加关系；不定义、推导或替代 EAOS Workflow Kernel

---

## 1. Scope 与证据强度

| 范围 | 结论 | 强度 |
|------|------|------|
| Legacy workflow/approval 表与页面 | 存在定义、实例、任务和通用审批记录 | Strong |
| V15.1 `workflow_center` | 默认关闭的元数据目录和展示层 | Strong/Scaffold |
| `apps/approval` | 独立 Approval Hub，可改审批记录，不回写来源单据 | Strong |
| Quote/SO/PO/DO/Finance | 各模块有独立 Type A Human Approved 门 | Strong |
| EAOS Workflow Kernel | 不在本次 Legacy 运行事实范围；不可由这些实现推导 | Out of scope |

Legacy 中至少有 workflow metadata、通用 approval、业务内联门和任务/自动化等并行体系。它们没有形成单一强制工作流引擎。

---

## 2. 业务规则

| ID | 规则描述 | 触发条件 | 例外/缺口 |
|----|----------|----------|-----------|
| W-R1 | Workflow Center 默认不启用，registry 项标记未实现或 metadata-only | Center/API | 不拦截业务 |
| W-R2 | Workflow Engine 的执行决策返回交给 Legacy/automation | Execute | 不运行统一流程 |
| W-R3 | Approval Hub 只更新 `approval_records` 并写审批历史 | Approve/Reject | 不回写 Quote/SO/PO/DO/Finance |
| W-R4 | Legacy `create_approval` 可创建通用审批记录 | Legacy helper | 未观察到当前业务 app 调用 |
| W-R5 | Quote Approve 在本模块内把 Draft 变为 Sent | Quote Type A | 不写通用审批或 quote_approval |
| W-R6 | SO Approve 在 Sales 内把待处理订单变为 Open | SO Type A | 不调用 Workflow Center |
| W-R7 | PO Approve 在 Procurement 内把 Draft 变为 Open | PO Type A | Receive 是独立动作 |
| W-R8 | DO Ship 的 Human Approved 直接调用库存出库 | DO Type A | 不是 Approval Hub 审批 |
| W-R9 | Finance AR Remind 的 Approve 创建催收任务/跟进 | AR Type A | 不代表实际发送通知 |
| W-R10 | Quote 专用 approval helper 存在，但 V18 业务流未调用 | Quote legacy | |
| W-R11 | Workflow Center 页面读取 Legacy workflow 定义、实例和任务 | Center page | 主要是展示 |
| W-R12 | 业务链 traceability 只同步 Quote/Requirement/SO 关联 | Lifecycle enrich | 不是审批门 |
| W-R13 | workflow_center 与 residual 页面可能并存 | Route mount | 最终路由归属需运行时确认 |

---

## 3. 流程

### 3.1 Workflow Center

启动/首次访问 → seed workflow 模块、流程、节点、审批类型和规则目录 → 提供 health/metadata → 页面读取 Legacy workflow 定义、实例和任务。

此流程不执行或强制业务单据状态迁移。

### 3.2 Approval Hub

查看 `approval_records` → Approve/Reject → 更新审批记录状态 → 追加审批历史。

没有观察到根据 `source_module/source_no` 回写来源单据。

### 3.3 业务内联 Human Approved

| 单据 | 本地前置 | 本地副作用 |
|------|----------|------------|
| Quote | Draft、有行、人工确认 | Quote → Sent |
| SO | 待处理、有行、人工确认 | SO → Open |
| PO | Draft、有行、人工确认 | PO → Open |
| DO | Open、人工确认及库存校验 | 库存出库，DO → Shipped |
| AR Remind | 有余额、人工确认 | 创建催收任务/跟进 |

这些动作直接调用所属模块服务，不进入 workflow_center 或 Approval Hub。

---

## 4. 校验

| ID | 校验 | 强度 | 说明 |
|----|------|------|------|
| W-V1 | Workflow metadata module/approval key 属于注册集合 | Medium | 只校验目录 |
| W-V2 | Quote Approve 仅 Draft、有行、人工确认 | Hard | 模块内门 |
| W-V3 | SO Approve 仅待处理、有行、人工确认 | Hard | 模块内门 |
| W-V4 | PO Approve 仅 Draft、有行、人工确认 | Hard | 模块内门 |
| W-V5 | DO Ship 阶段、库存、幂等和人工确认 | Hard | Inventory 内门 |
| W-V6 | AR Remind 余额为正 | Hard | Finance 内门 |
| W-V7 | Approval Hub 的 approver 与 Pending 查询 | Hard | 只作用 approval_records |
| W-V8 | Workflow Center 强制业务状态转移 | Absent | metadata `enforced=False` |
| W-V9 | Approval Hub 批准后回写来源单据 | Absent | |
| W-V10 | 业务 Type A 同时生成审批记录/历史 | Absent | |
| W-V11 | 单一审批状态词汇和跨模块状态机 | Absent | 各模块自有 |

---

## 5. 数据含义

### 5.1 Workflow Center 元数据

| Entity | Meaning |
|--------|---------|
| `workflow_registry` | 逻辑模块目录 |
| `workflow_processes` | 流程/BPMN 元素目录 |
| `workflow_nodes` | 节点类型目录；可能与 Legacy 同名表结构冲突 |
| `workflow_approvals` | 审批类型目录 |
| `workflow_rules` | metadata-only 规则 |
| `workflow_history` | seed/元数据事件，不是业务审批审计 |

### 5.2 Legacy overlay

| Entity | Meaning |
|--------|---------|
| `approval_records` | 通用审批记录，可带来源模块/单号 |
| `approval_history` | Approval Hub 操作历史 |
| `approval_types` | 审批类型字典 |
| `quote_approval` | 报价专用遗留审批表 |
| `workflow_definitions` | Legacy 流程定义 |
| `workflow_instances` | Legacy 流程实例 |
| `workflow_tasks` | Legacy 待办任务 |
| `exec_tasks` | 另一套任务执行台数据 |

### 5.3 业务单据状态

Quote、SO、PO、DO 等主表自身的 `status` 才是 Type A 动作直接修改的数据。它们没有通过 workflow 表形成统一状态权威。

---

## 6. 状态词汇

| Value / family | Meaning | Layer |
|----------------|---------|-------|
| active | registry 元数据状态 | Workflow Center |
| metadata_only | 规则只登记未执行 | Workflow Center |
| implemented=False / enforced=False | 能力未落地/不强制 | Workflow Center |
| DEFER_TO_LEGACY | 引擎不接管执行 | Core workflow scaffold |
| Pending / Approved / Rejected | 通用审批记录状态 | Approval Hub |
| Draft → Sent | Quote 本地批准 | Quotation |
| pending → Open | SO 本地批准 | Sales |
| Draft → Open | PO 本地批准 | Procurement |
| Pending/Open → Shipped | DO 本地出库批准 | Inventory |
| draft/running/completed/failed 等 | 架构层 WorkflowState | 不证明业务接线 |

---

## 7. UNKNOWN 与核查范围

| UNKNOWN | 已核查路径/范围 |
|---------|-----------------|
| `/workflow_center` 最终由当前 router 还是 residual 处理 | `apps/workflow_center/router.py`、`v14_residual.py`、bootstrap 注册；未运行路由表 |
| 实际数据库是否有 workflow definitions/instances/tasks 数据 | 静态 repository 与 DDL；未连接运行数据库 |
| `approval_records` 是否由外部脚本或历史路径持续写入 | 全库 app 调用与 INSERT 检索；当前 app 未见调用，运行 DB 未查 |
| Finance 是否还有其他独立 Type A 批准面 | `apps/finance/services.py` 及相关模板已检索主要 apply/approval 命名；完整历史残留行为仍需运行路由核对 |
| automation 是否从业务 POST 强制触发 | `v15/automation/**` 与 apps 调用检索；未确认强制链 |
| V15.1 同名 workflow 表在实际 DB 的 schema | 静态 DDL 存在冲突可能；未执行数据库 introspection |

---

## 8. 只读来源路径

| Path | Why cited | Strength |
|------|-----------|----------|
| `apps/workflow_center/` | Center 路由、服务、repository 与 registries | Strong |
| `core/workflow/` | 元数据类型、validator 与 defer engine | Strong |
| `core/capabilities/workflow/` | 能力脚手架 | Medium |
| `apps/approval/services.py` / `repository.py` | Approval Hub 行为 | Strong |
| `core/capabilities/approval/` | Approval 能力脚手架 | Medium |
| `apps/quotation/services.py` | Quote Type A | Strong |
| `apps/sales/services.py` | SO Type A | Strong |
| `apps/procurement/services.py` | PO Type A | Strong |
| `apps/inventory/services.py` | DO Ship Type A | Strong |
| `apps/finance/services.py` | AR Remind Type A | Strong |
| `runtime/v14/legacy_support.py` | Legacy approval/workflow 表与 helper | Strong static |
| `database/v151_workflow_center_schema.py` | V15.1 metadata schema | Strong static |
| `templates/workflow_center.html` | Center 展示面 | Medium |
| `templates/approvals.html` / `approval_detail.html` | Approval Hub | Medium |
| `business_modules/approval.md` | 横向审批目标边界 | Intent |
| `docs/reports/Workflow_Catalog.md` | 未接业务链记录 | Medium |
| `docs/reports/Integration_Queue.md` | 待接线项 | Medium |

**Root:** `H:\Workspace\EZAM_CRM - 9.0\` + paths above.

---

## 9. 边界声明

以上是 Legacy 叠加层的事实清单。不得把 workflow_center 的目录、Approval Hub 的记录 CRUD 或 V18 Type A 页直接解释为 EAOS Workflow Kernel 的目标结构、接口或状态机。
