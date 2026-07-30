# 多级 / 多步审批证据有无

## Scope 与证据强度

本页核验 Legacy 是否存在可执行的多级、顺序、并行或条件审批。强结论：**仅有 Workflow/Approval 注册元数据，全部 `implemented=false`**；活动 Approval Center 是单记录、单次决策（Pending→Approved/Rejected），无步骤实例、无会签计数、无条件分支执行。DDL 中的 `approval_delegation`、`need_workflow`、settings timeout **不足以**证明多级已上线。

## 业务规则（稳定 ID）

1. **MSE-R01** `APPROVAL_TYPES` 声明：`single_approval`、`multi_approval`、`sequential_approval`、`parallel_approval`、`conditional_approval`。
2. **MSE-R02** `ApprovalRegistry._seed` 对每一类型写入 `implemented: False`。
3. **MSE-R03** `ApprovalRegistry.health()` 返回 `"implemented": False`。
4. **MSE-R04** Workflow Center facade 可把元数据 upsert 到仓储，但仍来自未实现核心列表。
5. **MSE-R05** 活动中心决策路径只更新一条 `approval_records`，无 step_no / level / round 字段消费。
6. **MSE-R06** `approval_history` 记录动作列表，但主路径每次决策插一条 Approved/Rejected；无「进入下一步」动作编排。
7. **MSE-R07** `approval_types.need_workflow=1` 是类型标志，不启动 workflow engine。
8. **MSE-R08** `approval_settings.allow_delegate` / `approval_timeout=72` 为种子值；未见步骤超时或委托路由执行。
9. **MSE-R09** `approval_delegation` 表存在（username/delegate_user/日期），未见 apps/approval 读写。
10. **MSE-R10** 业务模块规格列出 `approval_workflows` / `approval_steps` / `approval_requests` 为目标拥有表；活动 primary_table 是 `approval_records`。
11. **MSE-R11** 单人指定 approver 待办过滤存在，**不等于**多级链。
12. **MSE-R12** V15/Integration 将 Workflow AI / 审批链标记为未接线或 No chain hook。
13. **MSE-R13** 不得把多次打开 Approve 页面或重复 GET `/approve` 解释为多级审批。
14. **MSE-R14** 并行/条件审批无条件表达式求值器挂在 Approval Center 决策路径上。

## 流程（可观察 vs 元数据）

| 层 | 实际行为 |
|---|---|
| 元数据注册 | 列出 5 种审批模型，implemented=false |
| 中心运行时 | 单记录 Pending → 一次 Approve/Reject |
| 多级推进 | **未观察到** next-step / quorum / parallel join |
| 业务回调 | **未观察到** |

## 校验（强/弱/缺失）

1. **MSE-V01（强）** 五类审批键均标记未实现。
2. **MSE-V02（强）** health.implemented == False。
3. **MSE-V03（缺失）** sequential step 表/实例执行。
4. **MSE-V04（缺失）** multi/parallel 法定人数或全员同意校验。
5. **MSE-V05（缺失）** conditional 规则引擎绑定 approval decision。
6. **MSE-V06（缺失）** delegation 生效替换 approver 查询。
7. **MSE-V07（缺失）** timeout 自动升级/过期。
8. **MSE-V08（强）** 活动 UPDATE 无 step 条件。
9. **MSE-V09（弱）** `need_workflow` 默认 1 不产生实例。
10. **MSE-V10（缺失）** `approval_steps` / `approval_workflows` 活动仓库方法。

## 数据含义

| 数据 | 含义 |
|---|---|
| `single_approval` | 元数据键：单人审批（未实现） |
| `multi_approval` | 元数据键：多人审批（未实现） |
| `sequential_approval` | 元数据键：顺序多级（未实现） |
| `parallel_approval` | 元数据键：并行（未实现） |
| `conditional_approval` | 元数据键：条件（未实现） |
| `implemented` | 注册表能力标志；当前恒 false |
| `need_workflow` | 类型是否「需要工作流」的静态标志 |
| `allow_delegate` | 设置种子；非运行委托 |
| `approval_timeout` | 设置种子「72」；单位/执行 UNKNOWN |
| `approval_delegation.delegate_user` | 委托目标列；无消费证据 |
| `approval_history` 多行 | 审计事件，非步骤状态机 |
| `approval_requests` / `approval_steps`（规格） | 目标模型名；非活动 primary |
| `V151_WORKFLOW_VERSION` | 工作流版本标签 |
| HISTORY_EVENTS `approval_requested/granted` | 事件枚举；≠中心已发事件总线 |

## 状态词汇

| 术语 | 证据地位 |
|---|---|
| Pending/Approved/Rejected | **有** — 单级中心状态 |
| Step N / Level N | **无**执行态 |
| Waiting parallel peers | **无** |
| Condition matched | **无** |
| Delegated | DDL only |

## 证据表

| ID | 观察事实 | 强度 | 只读来源路径 |
|---|---|---|---|
| MSE-E01 | APPROVAL_TYPES 五键 | 强 | `core/workflow/types.py` |
| MSE-E02 | registry seed implemented=False | 强 | `core/workflow/approval.py` |
| MSE-E03 | facade 透传核心列表 | 强 | `apps/workflow_center/approval_registry.py` |
| MSE-E04 | 单记录 UPDATE 无步骤 | 强 | `apps/approval/repository.py` |
| MSE-E05 | history 仅 Approved/Rejected 动作 | 强 | `apps/approval/services.py` |
| MSE-E06 | delegation/settings DDL+种子 | 强/弱 | `runtime/v14/legacy_support.py` |
| MSE-E07 | 规格拥有 workflows/steps | 弱/目标 | `business_modules/approval.md` |
| MSE-E08 | governance：多级仅元数据 | 强 | `../governance/approval.md` |
| MSE-E09 | Integration：Approval→SO/Quote 无 hook | 强 | `docs/reports/Integration_Queue.md` |
| MSE-E10 | V15：审批可见但未强制 | 强 | `docs/reports/V15_ENTERPRISE_INTELLIGENCE_REPORT.md` |

## UNKNOWN + 已查路径

1. **Workflow Center DB 中 upsert 的 approval 行是否被任何 UI 渲染为可配流程 UNKNOWN。** 已查：approval_registry facade、workflow center templates/reports 索引、apps/approval。
2. **`approval_queue` / `approval_monitor` DDL 是否服务多级监控 UNKNOWN。** 已查：`legacy_support.py` 邻近 CREATE、apps/approval。
3. **v15/approval/engine.py（规格提及）是否存在并可执行 UNKNOWN。** 已查：`business_modules/approval.md`、`v15/approval/**` glob 意图路径、core/capabilities/approval。
4. **超时 72 的单位（小时/分钟）与触发器 UNKNOWN。** 已查：default_approval_settings、services、jobs/scripts。
5. **是否有外部 BPM 系统承接多级 UNKNOWN。** 已查：Integration_Queue、V15 报告、approval apps。
6. **LEAVE/EXPENSE 类型是否在其他模块实现独立多级 UNKNOWN。** 已查：default types、apps/approval、finance/expense 路径抽样。

## 只读来源路径汇总

`core/workflow/types.py` · `core/workflow/approval.py` · `apps/workflow_center/approval_registry.py` · `apps/approval/repository.py` · `apps/approval/services.py` · `runtime/v14/legacy_support.py` · `business_modules/approval.md` · `docs/reports/Integration_Queue.md` · `docs/reports/V15_ENTERPRISE_INTELLIGENCE_REPORT.md` · `../governance/approval.md`
