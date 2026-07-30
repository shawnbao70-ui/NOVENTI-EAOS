# TC 台账状态与不完整路径（TC Ledger States）— Legacy Knowledge

**Evidence strength:** Strong for Pending creation and read-only display; strong negative for approval/payout transitions  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0` (read-only)

---

## 1. Scope 与证据强度

本模块描述 `tc_ledger.status` 的实际写入、展示和缺失的审批/发放/冲销路径。可证事实只有：Quote→SO 时建立 `Pending`，TC Ledger 页面按 ID 倒序只读展示。未观察到更新、删除、批准、驳回、支付或期间关闭路由。

`Approved`、`Paid`、`Rejected`、`Settled` 等只可作为期望词汇或 UNKNOWN，不能写成 Legacy 已实现状态。

---

## 2. Business Rules

| ID | Rule / observed boundary | Evidence / consequence |
|----|--------------------------|------------------------|
| TLS-R1 | canonical convert 新建台账状态固定 Pending | 唯一活动写状态 |
| TLS-R2 | TC Ledger 页面读取全部记录并按 ID 倒序 | 无周期、人员或状态过滤 |
| TLS-R3 | 页面展示 salesperson、来源、销售额、费率、佣金和状态 | 不展示批准人或付款信息 |
| TLS-R4 | 页面 KPI 的 `Active` 是静态表面文案 | 不是记录状态汇总 |
| TLS-R5 | 未观察到 `UPDATE tc_ledger` 活动路径 | Pending 无可证后继 |
| TLS-R6 | 未观察到 `DELETE FROM tc_ledger` 活动路径 | 无作废/冲销记录 |
| TLS-R7 | 未观察到 Approved/Paid/Rejected 写入 | 不能宣称闭环 |
| TLS-R8 | `commission_periods` 独立只读展示 | 不约束 TC ledger 范围 |
| TLS-R9 | period status 不自动改变 TC 状态 | 无 foreign key 或 service link |
| TLS-R10 | TC row 不保存 period ID | 不能按原生关联关账 |
| TLS-R11 | TC row 不保存 approval request ID | 未接 Approval Center |
| TLS-R12 | TC row 不保存 payment record ID | 未接 Treasury payout |
| TLS-R13 | TC row 不保存 update time、approver、payer 或 reason | 审计语义不足 |
| TLS-R14 | SO 取消/交付/回款不改变 TC 状态 | 与交易链脱节 |
| TLS-R15 | calculator/ranking 使用 `salesperson_commissions` | 不会推进 TC ledger |
| TLS-R16 | rebate 也以 Pending 新建，但属于另一表 | 不应与 TC 状态合并 |
| TLS-R17 | `commissions` 预留表默认 Pending | 未观察到与 TC 同步 |
| TLS-R18 | `/tc_ledger` 路由未见显式权限检查 | 菜单可见性不构成访问门 |
| TLS-R19 | Commission Center 有 view gate，但 TC Ledger 本身无同等 gate | RBAC 不一致 |
| TLS-R20 | EAOS 不得把 Pending 当作已批准负债或已支付费用 | 它只是转换时计算记录 |
| TLS-R21 | 权限目录登记 `Commission`，Center route 检查 `Commission Center` | 未观察到两者 alias，权限名可能不匹配 |
| TLS-R22 | `/tc_ledger` 仅由 Sales v14 residual 承载 | canonical Sales router 不含该页 |
| TLS-R23 | legacy menu 无 TC Ledger 直链 | 页面可通过深链和 Commission Center breadcrumb 到达 |

---

## 3. Process

### 3.1 已实现路径

1. Quote 转 SO 时计算佣金。
2. 写入 TC row，状态 Pending。
3. 用户访问 `/tc_ledger`。
4. 系统读取所有 rows，连接 salesperson name 并展示。

### 3.2 未实现闭环

未观察到：选择 period → 冻结范围 → 审核差异 → Human Approved → 生成 payable/expense → Treasury payment → 回写 Paid → 失败退回/冲销 → 审计。

### 3.3 相邻状态表

`commission_periods.status`、`rebates.status` 和 `commissions.status` 属于平行实体。相同的 Pending 文字不代表共享状态机。

---

## 4. Validation

| ID | Validation | Strength | Detail |
|----|------------|----------|--------|
| TLS-V1 | 新 row 必须有 status | Hard in writer | 固定 Pending |
| TLS-V2 | Pending→Approved 必须有权限 | Missing | 无 transition |
| TLS-V3 | Approved→Paid 必须有付款凭证 | Missing | 无 payment link |
| TLS-V4 | Rejected/Voided 必须有原因 | Missing | 无字段/路由 |
| TLS-V5 | 同 source 只能一个活动 row | Missing | 无 unique/duplicate check |
| TLS-V6 | period 必须覆盖 create/sales date | Missing | 无 period_id |
| TLS-V7 | 支付前必须锁定金额和币种 | Missing | 无 currency/lock |
| TLS-V8 | 状态变化必须记录 actor/time | Missing | schema 不支持 |
| TLS-V9 | 查看 TC Ledger 必须有 Commission 权限 | Missing at route | |
| TLS-V10 | SO 取消必须冲销 Pending | Missing | 无联动 |
| TLS-V11 | 负/零佣金必须异常标记 | Missing | 可保留 Pending |
| TLS-V12 | 已关闭 period 不得新增 row | Missing | period 不参与 writer |

---

## 5. Data Semantics

| Entity / field | Honest Legacy meaning |
|----------------|-----------------------|
| `tc_ledger.id` | 技术主键和展示排序依据 |
| `tc_ledger.salesperson_id` | 销售员弱关联 |
| joined salesperson name | 页面展示名称，非台账快照 |
| `tc_ledger.source_type` | canonical 为 Sales Order |
| `tc_ledger.source_no` | SO number 文本 |
| `tc_ledger.sales_amount` | 转换时订单额快照 |
| `tc_ledger.commission_rate` | 转换时费率快照 |
| `tc_ledger.commission_amount` | 计算佣金 |
| `tc_ledger.status` | 当前唯一可证写值 Pending |
| `tc_ledger.create_time` | 创建时间；非批准/支付时间 |
| `commission_periods.id` | 平行 period 主键，TC row 不引用 |
| `commission_periods.status` | period 标签，不驱动 TC |
| `commissions.status` | 预留表默认 Pending，与 TC 分离 |
| `rebates.status` | 返利状态，与 TC 分离 |
| `salesperson_commissions` | calculator/ranking 表，无状态列 |
| static KPI `Active` | 模板常量，不是数据库聚合 |

---

## 6. State Vocabulary

| Value / term | Evidence | Meaning |
|--------------|----------|---------|
| Pending | Strong | 转换时新建、等待未定义后续 |
| Active | Template/period/person | 不是 TC transition |
| Approved | Not observed | UNKNOWN / 不得当作实现 |
| Rejected | Not observed | UNKNOWN / 不得当作实现 |
| Paid | Not observed | UNKNOWN / 不得当作实现 |
| Settled | Not observed | UNKNOWN / 不得当作实现 |
| Voided / Reversed | Not observed | UNKNOWN / 不得当作实现 |

---

## 7. UNKNOWN 与已查路径

| UNKNOWN | Paths searched |
|---------|----------------|
| Pending 的正式业务审批人和 SLA | sales/finance commission routes、templates、approval paths |
| Approved/Paid 等状态是否存在于生产数据 | DDL、writers、templates、reports；未见 writer |
| TC 是否现金佣金、积分或混合单位 | level fields、ledger/template、payroll/treasury reports |
| Commission Period 如何锁定 ledger | period routes/templates、tc schema/services |
| 已取消 SO 的 Pending row 如何处理 | sales status、returns、ledger update searches |
| 错误佣金如何更正或冲销 | tc ledger routes、DELETE/UPDATE searches |
| 谁可查看全部 salesperson 的 ledger | permissions catalog、router/menu、reports |
| 历史支付是否记录在其他表 | payroll、expense、treasury payment、bank transaction searches |
| period closing 是否由线下流程完成 | docs/reports、business_modules、scheduler |

---

## 8. Evidence Table

| Read-only path | Evidence |
|----------------|----------|
| `apps/sales/services.py` | 唯一可证 Pending writer |
| `apps/sales/repository.py` | TC row insert fields |
| `apps/sales/v14_residual.py` | `/tc_ledger` 与 periods 只读 routes |
| `runtime/v14/legacy_support.py` | TC/period/commissions/rebates schemas |
| `templates/tc_ledger.html` | 只读列与静态 Active KPI |
| `templates/commission_periods.html` | period 独立展示 |
| `templates/rebate_center.html` | 平行 Pending 返利 |
| `templates/commission_calculator.html` | 平行 calculator 无状态流 |
| `core/permission/module_catalog.py` | Commission 权限目录 |
| `templates/includes/v11/legacy_menu.html` | 菜单角色可见性 |
| `bootstrap/enterprise_cutover.py` | business pages 后挂 residual |
| `bootstrap/v14_residual.py` | method/path 去重与 residual 路由保留 |
| `Business_Module_Registry.md` | Sales/Finance 都声明 TC/commission |
| `docs/reports/V15_ENTERPRISE_READINESS_REPORT.md` | Commission 不适合生产结算 |
| `docs/knowledge/legacy-extract/finance/settlement-rules.md` | EAOS 只读交叉引用 |

**Root:** `H:\Workspace\EZAM_CRM - 9.0\` + paths above（最后一项为 EAOS 只读交叉引用）。
