# create_approval / 提交审批 — 全库调用点

## Scope 与证据强度

本页固定中央审批 **提交入口** 的符号与路由证据。强结论：`create_approval(...)` 在活动树中 **只有定义、没有业务调用**；规格中的 `POST /submit_approval` **无活动路由**；唯一可见的「造数」路由 `/add_test_approval` 写入旧表 `approvals`，与中央 `approval_records` 脱节。交叉引用（只读不改）：[`../approval-center-deepen/approval_center_runtime.md`](../approval-center-deepen/approval_center_runtime.md)、[`../approval-center-deepen/business_hook_gaps.md`](../approval-center-deepen/business_hook_gaps.md)。

## 业务规则（稳定 ID）

1. **CAS-R01** `create_approval(type_code, source_module, source_no, applicant, approver, remark="")` 定义于 `runtime/v14/legacy_support.py`，INSERT `approval_records` 且初始 `approval_status='Pending'`。
2. **CAS-R02** 新编号由 `generate_no("APR")` 生成；`created_by` 取 `applicant`；写 `create_time`/`update_time`。
3. **CAS-R03** 全库 `*.py`（排除 backup 镜像定义）对 `create_approval(` 的匹配 **仅为定义点**；`apps/quotation`、`apps/sales`、`apps/inventory`、`apps/approval`、`apps/procurement`、`apps/finance` **均无调用**。
4. **CAS-R04** `can_create_approval(request)` 仅按 session `role` ∈ {Admin, Manager, Sales} 返回布尔；**未见**页面路由/service 调用该 helper。
5. **CAS-R05** `business_modules/approval.md` 声称 `POST /submit_approval`；活动 `apps/approval/router.py` **无**该 path、**无** POST approve/reject。
6. **CAS-R06** S013/`APPROVAL_WORKFLOW_MIGRATION_S013.md` 将 `create_approval` 列为仍被 dashboard/API 使用的 helper 名；活动页面决策路径读记录但不调用创建。
7. **CAS-R07** `GET /add_test_approval`（`apps/supplier/v14_residual.py`）INSERT 旧表 `approvals(module_name, document_no, …)`，**不**调用 `create_approval`，**不**写 `approval_records`。
8. **CAS-R08** A-022 诚实性要求 Hub **不以** `/add_test_approval` 作为 primary New CTA；gate 校验 `href="/add_test_approval"` 不在列表模板主 CTA。
9. **CAS-R09** `create_quote_approval` 写 `quote_approval` 辅助表；与中央 `create_approval` **符号分离**；全库亦无 Type A 业务调用点（仅定义 + facade 导出 + v14 bridge）。
10. **CAS-R10** `core/capabilities/approval/service.py` 仅为 Capability 壳（slug/label/bridge），**无** submit/create 实现。
11. **CAS-R11** `apps/approval` repository 提供 fetch/update/search/history insert，**无** `insert_approval_record` / create 方法。
12. **CAS-R12** V15 报告明文：`create_approval()` defined but **never called** from business handlers；Approval before SO/PO = Never triggered。
13. **CAS-R13** 默认类型种子含 `QUOTE`/`PURCHASE`/`PAYMENT`/`EXPENSE`/`LEAVE`，只证明类型可登记，**不**证明提交钩子存在。
14. **CAS-R14** 不得把 Hub「相关链接」到 `/quotes`/`/sales_orders` 解释为提交入口。
15. **CAS-R15** 不得把 JSON 只读 API（`/api/approvals`、dashboard/pending）解释为创建审批。
16. **CAS-R16** EAOS 迁移约束：中央审批提交必须是显式 command（POST + principal + source 绑定）；Legacy 无此闭环可抄。

## 调用点矩阵

| 符号 / 路由 | 位置 | 写何表 | 被业务调用？ |
|---|---|---|---|
| `create_approval(...)` | `runtime/v14/legacy_support.py` | `approval_records` | **否**（仅定义） |
| `create_approval(...)` | `backups/pre_phase2_app.py` | 同左（历史镜像） | 非活动树 |
| `can_create_approval` | `legacy_support.py` | 无写 | **否**（未见路由接线） |
| `POST /submit_approval` | 仅规格 | — | **无路由** |
| `GET /add_test_approval` | `apps/supplier/v14_residual.py` | 旧 `approvals` | 造数路由，非中心提交 |
| `create_quote_approval` | `apps/quotation/utils.py` | `quote_approval` | **否**（未见 Type A 调用） |
| Approval capability service | `core/capabilities/approval/service.py` | 无 | 壳 |
| ApprovalPageService | `apps/approval/services.py` | update/history | 决策侧，非提交 |

## 校验（强/弱/缺失）

1. **CAS-V01（强）** 符号检索 `create_approval(` → 活动代码仅定义。
2. **CAS-V02（强）** `apps/approval/repository.py` 无 INSERT approval_records。
3. **CAS-V03（缺失）** 活动 `POST /submit_approval` 路由。
4. **CAS-V04（强）** `add_test_approval` INSERT 目标为 `approvals` 而非 `approval_records`。
5. **CAS-V05（缺失）** Quote/SO/PO/Ship handler 调用 `create_approval`。
6. **CAS-V06（缺失）** 页面路由调用 `can_create_approval`。
7. **CAS-V07（强）** V15 / Integration 负向报告与代码检索一致。
8. **CAS-V08（弱）** S013 文案称 helper「仍被使用」——活动决策路径未证实创建调用。
9. **CAS-V09（强）** `create_quote_approval(` 活动调用点缺失（仅定义/bridge/facade）。
10. **CAS-V10（缺失）** 高金额/类型自动提交策略引擎绑定 `create_approval`。
11. **CAS-V11（强）** A-022 gate：Hub 不把 test approval 作主 CTA。
12. **CAS-V12（缺失）** Capability API 执行中央 INSERT。

## 数据含义

| 数据 | 在提交语境中的含义 |
|---|---|
| `approval_records` | 中央审批主表；正常应由 `create_approval` 或等价 INSERT 产生 |
| `approval_no` / `APR*` | 中央编号；无业务提交则运营侧难见自然增长 |
| `type_code` | 类型种子键（QUOTE 等）；≠已提交实例 |
| `source_module` / `source_no` | 来源引用字符串；无 FK；业务链不写入 |
| `applicant` / `approver` | 申请/指定审批人用户名 |
| `approval_status=Pending` | 创建后的唯一初始态 |
| 旧表 `approvals` | 早期/测试结构；`add_test_approval` 目标；Hub 已不以之为主绑定 |
| `quote_approval` | 报价辅助审批表；非中央 |
| `can_create_approval` 角色集合 | 意图权限辅助；未接线 ≠ 可提交 |
| `submit_approval`（规格） | 目标 POST 名；运行时缺失 |
| `generate_no("APR")` | 仅在 `create_approval` 体内使用 |
| Capability `BRIDGE=v15/task_execution` | 能力桥标签；非提交实现 |

## 状态词汇

| 术语 | 证据地位 |
|---|---|
| Defined-only | `create_approval` 有函数体无调用方 |
| Spec-only | `POST /submit_approval` |
| Seed-only | `approval_types` 默认行 |
| Test-insert | `/add_test_approval` → 旧 `approvals` |
| Parallel helper | `create_quote_approval` → `quote_approval` |
| Decision-only surface | Center approve/reject 更新已有行 |

## 证据表

| ID | 观察事实 | 强度 | 只读来源路径 |
|---|---|---|---|
| CAS-E01 | `create_approval` INSERT Pending + APR | 强 | `runtime/v14/legacy_support.py` |
| CAS-E02 | 全库 `create_approval(` 仅定义（+backup） | 强 | 全库 `*.py` 符号检索 |
| CAS-E03 | 规格声称 POST submit/approve/reject | 弱/规格 | `business_modules/approval.md` |
| CAS-E04 | 活动 router 仅 GET 列表/详情/决策 | 强 | `apps/approval/router.py` |
| CAS-E05 | repository 无 create INSERT | 强 | `apps/approval/repository.py` |
| CAS-E06 | add_test_approval → 旧 approvals | 强 | `apps/supplier/v14_residual.py` |
| CAS-E07 | A-022 禁止 test CTA 为主入口 | 强 | `docs/reports/Business_Strong_A022_Approval_Ops_Report.md` · gate script |
| CAS-E08 | V15 never called | 强 | `docs/reports/V15_ENTERPRISE_INTELLIGENCE_REPORT.md` |
| CAS-E09 | create_quote_approval 写 quote_approval | 强 | `apps/quotation/utils.py` |
| CAS-E10 | Capability 壳无 submit | 强 | `core/capabilities/approval/service.py` |
| CAS-E11 | can_* helpers 未接页面路由 | 强 | `legacy_support.py` + `apps/approval/router.py` |
| CAS-E12 | S013 helper 清单含 create_approval | 弱 | `APPROVAL_WORKFLOW_MIGRATION_S013.md` |

## UNKNOWN + 已查路径

1. **运营是否用手工 SQL / 外部脚本插入 `approval_records` UNKNOWN。** 已查：`apps/approval/`、`legacy_support.create_approval`、全库 `INSERT INTO approval_records`（仅 create_approval 定义体）、docs/reports。
2. **`/add_test_approval` 在当前 bootstrap 下是否仍挂载可达 UNKNOWN。** 已查：`apps/supplier/v14_residual.py`、Route_Verification_Report、Enterprise_Module_Recovery_Report、A-022、S013 deferred。
3. **backup `pre_phase2_app.py` 内是否曾有历史调用方（活动树外）UNKNOWN。** 已查：活动 `apps/**` + `runtime/v14` 符号；backup 仅见定义。
4. **dashboard/API 路径是否在某启动模式下间接调用 create_approval UNKNOWN。** 已查：`apps/approval/approval_api.py`、`services.py`、S013 文案、routes scaffold。
5. **采购/费用模块是否存在未命名的等价 INSERT（非 create_approval 符号）UNKNOWN。** 已查：`INSERT INTO approval_records` 全库 py、apps/procurement、apps/finance 抽样、Integration 3.3。
6. **GFIP/外部网关是否代建中央审批票 UNKNOWN。** 已查：Integration_Queue、V15、apps/approval、business_modules。
7. **`quote_approval` 是否被报表/UI 误标为中央审批 UNKNOWN。** 已查：quotation utils/dashboard counts、templates/approval*、facade 导出。

## 只读来源路径汇总

`runtime/v14/legacy_support.py` · `apps/approval/router.py` · `apps/approval/services.py` · `apps/approval/repository.py` · `apps/approval/permissions.py` · `apps/supplier/v14_residual.py` · `apps/quotation/utils.py` · `apps/quotation/facade.py` · `core/capabilities/approval/service.py` · `business_modules/approval.md` · `APPROVAL_WORKFLOW_MIGRATION_S013.md` · `docs/reports/V15_ENTERPRISE_INTELLIGENCE_REPORT.md` · `docs/reports/Business_Strong_A022_Approval_Ops_Report.md` · `docs/reports/Integration_Queue.md` · `../approval-center-deepen/`
