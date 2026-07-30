# 审批中心（Approval Center）— Legacy Knowledge

**Evidence strength:** Medium — approval record list/actions are observable; centralized cross-module gate enforcement is weak  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0` (read-only)

---

## 1. Scope 与证据强度

Approval 被边界文档定义为横向治理模块：它不拥有报价、订单、采购、付款或文档等业务记录，只控制其释放。活动页面可确认的能力包括审批类型、审批记录、个人待办、详情、搜索、批准、拒绝和历史。

但 Legacy 中存在两套不同的“人工批准”机制：

1. **Approval Center 记录流**：围绕 `approval_records` 和 `approval_history`，状态为 Pending/Approved/Rejected；
2. **V18 Human Approved 本地确认流**：报价、销售订单、采购单、出库、交付记应收、催收等各自在业务页面校验 `human_confirm` 并直接推进业务状态。

未观察到 V18 本地确认自动建立 Approval Center 记录。多级、顺序、并行、条件审批只存在于 Workflow 注册元数据，均标为未实现。

---

## 2. 业务规则

| ID | 规则描述 | 触发条件 | 例外 / UNKNOWN | EAOS 重写备注 |
|----|----------|----------|----------------|----------------|
| AP-R1 | 审批记录以来源模块和来源单号指向外部业务对象 | 提交/查看审批 | 来源对象外键完整性 UNKNOWN；检索 `apps/approval/` 未见对象存在性校验 | 使用稳定业务引用 |
| AP-R2 | 指定审批人的 Pending 记录进入其个人待办 | 打开审批中心 | 全部记录仍在同页展示 | 查询需兼顾租户和数据权限 |
| AP-R3 | 批准把审批状态和结果置为 Approved，并记录完成时间 | 批准动作 | 未见强制原状态必须 Pending | 状态转换需条件更新 |
| AP-R4 | 拒绝把审批状态和结果置为 Rejected，并记录完成时间 | 拒绝动作 | 未见拒绝原因必填 | 拒绝原因应为治理事实 |
| AP-R5 | 主批准/拒绝路径写审批历史，记录动作、操作人和时间 | `/approve`、`/reject` | 备用 record 路径不写历史 | 所有决策必须统一审计 |
| AP-R6 | 审批搜索按来源 ID、申请人、审批人或来源类型匹配 | 搜索 | 无结构化状态/日期过滤证据 | 搜索不是授权边界 |
| AP-R7 | UI 在批准/拒绝前要求浏览器人工确认 | 页面点击 | 路由本身是 GET 写操作，且服务端没有确认令牌 | 改为带 CSRF/权限/幂等的命令 |
| AP-R8 | AI 不应自动批准 PO、SO、付款或其他业务释放 | Approval Hub 诚实性文案 | AI 审批执行引擎 UNKNOWN；检索 `templates/approvals.html`、`Business_Strong_A022_Approval_Ops_Report.md` | 明确禁止静默批准 |
| AP-R9 | 报价 V18 批准只允许 Draft、有明细、人工确认后转 Sent | Quote Approve | 不写 Approval Center 记录 | 这是本地发布门，不是中心审批 |
| AP-R10 | 销售订单 V18 批准只允许待处理阶段、有明细、人工确认后转 Open | SO Approve | 不写 Approval Center 记录 | 创建交付仍为独立动作 |
| AP-R11 | 采购单 V18 批准只允许 Draft、有明细、人工确认后转 Open | PO Approve | 不写 Approval Center 记录 | 收货仍为独立动作 |
| AP-R12 | DO 出库需 Human Approved，且出库/库存台账只应执行一次 | DO Ship | 属 Inventory 本地门，不进入中心待办 | 区分批准与执行 |
| AP-R13 | DO 记应收需 Human Approved，并明确不是税务发票 | DO→AR | 重复应收仅警告 | 财务过账应有中心或策略门 |
| AP-R14 | AR 提醒需 Human Approved；批准只登记待办，不自动发信 | AR Reminder | 写任务失败可降级为客户跟进 | 对外发送仍应独立授权 |
| AP-R15 | 报价转销售订单与 Quote Approve 是分开的人工动作 | Convert SO | 转单使用独立确认 | 不把 Sent 等同订单创建 |
| AP-R16 | Workflow 注册表列出单人、多级、顺序、并行、条件审批 | 查看元数据 | 全部 `implemented=false` | 不能作为 Legacy 已有能力迁移 |
| AP-R17 | Approval Center 原则上面向 Sales、Procurement、Finance、Documents | 模块边界 | 实际消费者提交闭环不完整 | 逐一建立提交与回调契约 |
| AP-R18 | 宪章要求审批原则上由人负责，AI 只能建议，不得绕过审批 | 所有治理决策 | 授权范围内自动审批的具体委托模型 UNKNOWN | Human First 为上位规则 |
| AP-R19 | 宪章要求审批记录不可篡改，并保留审批人、时间、理由、证据及 AI 建议 | 审批决策 | 活动主路径历史备注为空，证据/AI 建议字段未见 | 审计模型需补齐 |
| AP-R20 | 财务操作必须经过审批 | 付款等财务动作 | Finance 运行路径未观察到 Approval Center gate | 标为治理要求与实现缺口 |
| AP-R21 | `create_approval` 辅助能力存在，但未发现报价、SO、PO 活动 handler 调用 | 业务提交审批 | 已检索全库调用点，仅见定义 | 中央审批记录产生路径偏薄 |
| AP-R22 | Approval Hub 的批准/拒绝诚实边界是“只改审批记录”，不静默创建 PO、SO、付款或发货 | 中心决策 | 不反向推进业务状态 | 业务释放需独立、显式编排 |

---

## 3. 流程

### 3.1 Approval Center 记录流

1. 外部或遗留辅助逻辑建立审批记录，初始为 Pending。
2. 记录保存审批编号、类型、来源模块、来源单号、申请人、审批人和备注。
3. 审批中心展示全部记录，并单列当前用户的 Pending 队列。
4. 审批人打开详情查看记录和历史。
5. 批准或拒绝后更新状态、结果和完成时间。
6. 主动作追加 Approved/Rejected 历史。
7. **业务对象是否同步释放：UNKNOWN。** 已检索 `apps/approval/services.py`、`repository.py`、`router.py`，只观察到审批记录更新，未观察到按来源模块回调业务对象。

### 3.2 报价 Human Approved

1. Draft 报价进入批准页，可保存草稿或调整行数量/价格。
2. 系统验证报价仍为 Draft 且至少有一行。
3. 人工确认后状态变为 Sent。
4. 转销售订单需要另一独立确认，不由该批准自动完成。

### 3.3 销售订单 Human Approved

1. 待处理销售订单进入批准页。
2. 系统要求订单有明细且仍处于待处理阶段。
3. 人工确认后状态变为 Open。
4. 创建交付单和出库是后续独立步骤。

### 3.4 采购单 Human Approved

1. Draft 采购单进入批准页。
2. 系统要求至少有一条采购明细。
3. 人工确认后状态变为 Open。
4. 仓库收货与采购开票不在该批准中执行。

### 3.5 交付与财务人工确认

1. DO Ship 审核交付明细和状态，人工确认后执行库存出库。
2. DO Invoice 页面人工确认后只记一条 AR，应收与税务发票分离。
3. AR Reminder 人工确认后记录催收任务，不自动发送。

---

## 4. 校验

| ID | 校验 | 强度 | 说明 |
|----|------|------|------|
| AP-V1 | Approval Center 待办按 `approver == 当前用户名` 且状态 Pending | Hard query filter | 不等同动作授权 |
| AP-V2 | 批准者必须等于记录审批人 | UNKNOWN | `apps/approval/router.py` 与服务未见校验 |
| AP-V3 | 批准/拒绝必须从 Pending 转换 | Missing | 更新未带旧状态条件 |
| AP-V4 | 批准/拒绝必须使用非 GET 命令 | Missing | 当前可观察路由为 GET |
| AP-V5 | 主批准/拒绝写历史 | Hard on main path | 备用 record 路径无历史 |
| AP-V6 | 拒绝原因必填 | Missing | 历史备注为空 |
| AP-V7 | 来源业务对象必须存在 | UNKNOWN | `apps/approval/` 未见跨模块检查 |
| AP-V8 | 报价批准要求 Draft、有行、Human Confirm | Hard |
| AP-V9 | 报价行补丁要求数量大于零、价格不为负 | Hard | 批准前可保存草稿 |
| AP-V10 | SO 批准要求待处理、有行、Human Confirm | Hard |
| AP-V11 | PO 批准要求 Draft、有行、Human Confirm | Hard |
| AP-V12 | DO Ship 要求适用状态、有行、Human Confirm | Hard |
| AP-V13 | DO→AR 要求 Human Confirm | Hard | 重复来源仅警告 |
| AP-V14 | AR 提醒要求余额大于零且 Human Confirm | Hard |
| AP-V15 | 多级/并行/条件审批步骤执行 | Not implemented | 仅元数据 |
| AP-V16 | 审批动作 RBAC/租户隔离 | UNKNOWN | 已检索 `apps/approval/router.py`、`permissions.py`，活动页面路由未见明确 gate |
| AP-V17 | 审批理由与证据必须留存 | Required by constitution, missing in active path | 主动作历史备注为空 |
| AP-V18 | 审批历史不可篡改 | Required by constitution, enforcement UNKNOWN | 未见防修改/防删除证据 |
| AP-V19 | 财务付款必须有审批 gate | Required by constitution, runtime UNKNOWN | 已检索 `apps/finance/` 未见中心审批调用 |

---

## 5. 数据含义

### 5.1 审批类型

| Field | 含义 |
|-------|------|
| `type_code` / `type_name` | 审批类型编码与名称 |
| `module_name` | 归属或消费业务模块 |
| `need_workflow` | 是否需要工作流的标志 |
| `status` | 类型自身是否活动 |

### 5.2 审批记录

| Field | 含义 |
|-------|------|
| `approval_no` | 审批业务编号 |
| `type_code` | 审批类型 |
| `source_module` | 来源业务域 |
| `source_no` | 来源业务单号 |
| `applicant` | 申请人 |
| `approver` | 指定审批人 |
| `approval_status` | 当前审批状态 |
| `approval_result` | 决策结果；运行结构存在演进差异 |
| `approval_time` / `finish_time` | 申请或完成时间；运行结构存在演进差异 |
| `remark` | 申请或审批备注 |

Legacy 中还存在早期 `approval_records` 与 `approvals` 结构，字段与活动页面使用的新结构不同，说明审批数据模型曾并行演进。

### 5.3 审批历史

| Field | 含义 |
|-------|------|
| `approval_id` | 所属审批记录 |
| `action_name` | Approved / Rejected 等动作 |
| `operator` | 操作人 |
| `remark` | 动作说明；当前主路径为空 |
| `create_time` | 动作时间 |

### 5.4 Human Approved

Human Approved 是业务页面提交时的人类确认来源标记。它证明用户在该动作界面确认，不天然代表：

- 已建立 Approval Center 记录；
- 已经过多级工作流；
- 当前用户具有中心审批人身份；
- 业务对象已完成所有后续释放步骤。

---

## 6. 状态词汇

| Status | 使用位置 | 含义 |
|--------|----------|------|
| `Pending` | 审批记录 | 待指定审批人处理 |
| `Approved` | 审批记录/历史 | 已批准 |
| `Rejected` | 审批记录/历史 | 已拒绝 |
| `Active` | 审批类型 | 类型可用，不是审批结果 |
| `Draft` | 报价、采购单 | 可编辑且可进入本地批准 |
| `Sent` | 报价 | Human Approved 后已发送 |
| `Open` | SO、PO | 本地批准后释放到下一业务阶段 |
| `Human Approved` | Automation Ladder 终点 / V18 来源标记 | 人类最终确认，不是数据库审批状态 |

禁止把 UI 曾出现的“Active”当作所有审批记录的真实状态；诚实性审计明确要求展示持久化 `approval_status`。

---

## 7. 只读来源路径

| Path | Why cited |
|------|-----------|
| `business_modules/approval.md` | 横向审批边界、消费者与目标能力 |
| `apps/approval/services.py` | 列表、详情、批准、拒绝和历史规则 |
| `apps/approval/repository.py` | 待办口径、状态更新、历史与搜索字段 |
| `apps/approval/router.py` | 活动页面动作、GET 写操作及可见权限缺口 |
| `templates/approvals.html` | 个人队列、人工确认、无 AI 自动批准声明 |
| `templates/approval_detail.html` | 状态与历史语义 |
| `runtime/v14/legacy_support.py` | 审批类型、记录、历史及早期并行结构 |
| `core/workflow/approval.py` | 多种审批模型均为未实现元数据 |
| `APPROVAL_WORKFLOW_MIGRATION_S013.md` | 活动路由迁移、备用动作不写历史 |
| `docs/reports/Business_Strong_A022_Approval_Ops_Report.md` | Approval Hub 诚实性与人工确认门禁 |
| `docs/constitution/publication/BOOK01.md` | Automation Ladder 与 Human First |
| `docs/constitution/volume-02-eaos/BOOK03.md` | 财务须审批、AI 不得绕过 |
| `docs/constitution/volume-02-eaos/BOOK05.md` | 审批可追溯 |
| `docs/constitution/volume-02-eaos/BOOK13.md` | 人工审批、不可篡改、理由/证据/AI 建议 |
| `docs/reports/V15_ENTERPRISE_INTELLIGENCE_REPORT.md` | `create_approval` 未接入业务 handler 的负向证据 |
| `apps/quotation/services.py` | 报价 Draft→Sent Human Approved |
| `apps/sales/services.py` | SO 待处理→Open Human Approved |
| `apps/procurement/services.py` | PO Draft→Open Human Approved |
| `apps/inventory/services.py` | DO Ship 与 DO→AR Human Approved |
| `apps/finance/services.py` | AR Reminder Human Approved |
| `docs/reports/V18_SO_DO_Invoice_TypeA_Report.md` | SO、DO、AR 本地确认边界 |

**Root:** `H:\Workspace\EZAM_CRM - 9.0\` + paths above.
