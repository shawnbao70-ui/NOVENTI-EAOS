# 佣金与 Finance 结算边界（Commission–Finance Boundary）— Legacy Knowledge

**Evidence strength:** Strong for Sales writer and absence from Finance services; mixed for registry ownership claims  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0` (read-only)

---

## 1. Scope 与证据强度

本模块回答谁计算、谁保存、谁展示、谁支付佣金，以及 `tc_ledger` 与 Finance/Treasury/AP/Expense/Payroll 的实际关系。Registry 同时把 commission/TC ledger 归给 Sales 和 Finance，但运行时 writer 位于 Sales；Finance service/repository 未观察到 TC 读取、批准或支付。

因此 Legacy 的事实所有权必须分层表达：Sales 拥有计算与原始 TC 行；Finance 只有目录/页面归属声明，没有可证的结算过账闭环。不得把 registry 声明当作实际财务真相。

---

## 2. Business Rules

| ID | Rule / observed boundary | Evidence / consequence |
|----|--------------------------|------------------------|
| CFB-R1 | canonical TC ledger writer 位于 Sales conversion | Finance 不创建该行 |
| CFB-R2 | Sales 决定 salesperson、基数、rate 和 amount | 是计算事实 owner |
| CFB-R3 | TC Ledger 页面也由 Sales residual route 提供 | 虽 registry 同时列入 Finance |
| CFB-R4 | Finance service/repository 未读取或更新 `tc_ledger` | 无结算 service owner |
| CFB-R5 | Treasury payment records 面向 supplier/account | 无 salesperson 或 TC row link |
| CFB-R6 | AP records 面向 purchase invoice/supplier | 不是销售佣金应付 |
| CFB-R7 | Expense records/expense center 未由 TC 自动生成 | 无费用过账桥 |
| CFB-R8 | Payroll/salary 表面未接 TC ledger | readiness 明示 payroll integration 缺失 |
| CFB-R9 | Bank/cash balance 不因 Pending TC 改变 | 无资金动作 |
| CFB-R10 | Finance dashboard 不把 Pending commission 计入 AP/expense/cashflow | 利润可能忽略佣金成本 |
| CFB-R11 | Receipts 不推进 TC status 或重算 canonical amount | 回款与订单额口径并行 |
| CFB-R12 | DO/AR posting 不推进 TC status | 权责应收与佣金确认未联动 |
| CFB-R13 | `commission_periods` 不生成 Finance batch | 只读期间展示 |
| CFB-R14 | `rebates` 也是人工平行表，不进 Treasury | 不能视为已支付返利 |
| CFB-R15 | `salesperson_commissions` calculator 不进入 Finance | 测试/排名事实 |
| CFB-R16 | Registry 的 Finance `tc_ledger` 列项是边界声明，不是代码证据 | 实际 route/writer 仍在 Sales |
| CFB-R17 | 未观察到会计凭证、GL account、税、币种或应付单号 | TC row 不是会计分录 |
| CFB-R18 | 未观察到付款批准、支付批次或银行回执 | Pending 不是资金负债闭环 |
| CFB-R19 | Commission 权限与 Finance/Treasury 权限分离且命名不一致 | 访问治理不统一 |
| CFB-R20 | Legacy 佣金真相是“Sales 计算快照”，不是“Finance 已结算金额” | 使用时必须标明口径 |
| CFB-R21 | EAOS 不得让 Finance 直接重算并覆盖 Sales 原始快照 | 应保留原始事件与独立结算调整 |
| CFB-R22 | legacy Quotation 转换副本也可写 TC，仍属于销售商业链而非 Finance | canonical route 由 Sales 优先 |
| CFB-R23 | `business_modules/sales.md` 与 `finance.md` 均未完整声明 TC 状态机 | 边界规格滞后于 registry 和运行时 |
| CFB-R24 | Salary Center 对 payroll 的相邻读取不构成佣金集成 | 未见 TC→payroll writer |

---

## 3. Process

### 3.1 实际可证链

1. Sales 在 Quote→SO 时计算佣金。
2. Sales 写 Pending `tc_ledger`。
3. Commission/TC 页面只读展示。
4. 流程在此终止；Finance/Treasury 没有消费步骤。

### 3.2 缺失的 Finance 闭环

未观察到：Finance 选择合格 Pending → 核对应收/回款/取消 → Human Approved → 生成 commission payable/expense → 形成支付批次 → 扣银行余额 → 回写 Paid/Settled → 对账。

### 3.3 真相分层

- **计算事实：** `tc_ledger`，由 Sales conversion 产生。
- **展示规则：** `commission_rules`，不执行。
- **演示绩效：** `salesperson_commissions`，按收款样例。
- **财务结算事实：** Legacy 未实现专用实体或链接。

---

## 4. Validation

| ID | Validation | Strength | Detail |
|----|------------|----------|--------|
| CFB-V1 | Finance 支付前必须有 Approved TC row | Missing | 无批准态 |
| CFB-V2 | 每笔 payout 必须链接 TC row | Missing | payment schema 无 link |
| CFB-V3 | commission payable 必须进入 AP/expense | Missing | 无桥 |
| CFB-V4 | 支付必须减少 bank/cash balance | Missing for commission | Treasury 无消费路径 |
| CFB-V5 | payout currency 必须与计算基数一致 | Missing | TC 无 currency |
| CFB-V6 | 税前/税后与代扣必须定义 | Missing | 无税字段 |
| CFB-V7 | 已取消/退款订单不得支付 | Missing | 无 eligibility gate |
| CFB-V8 | 已支付金额不得重复支付 | Missing | 无 payout/unique link |
| CFB-V9 | Finance 与 Sales 总额必须对账 | Missing | 无 report |
| CFB-V10 | period close 后金额不得改动 | Missing | period 未接 |
| CFB-V11 | 所有 settlement 动作必须审计 | Missing | 无 actor/approval |
| CFB-V12 | Commission 权限必须与 Finance ownership 一致 | Missing | 资源名与 route gate 分裂 |

---

## 5. Data Semantics

| Entity / field | Honest Legacy meaning |
|----------------|-----------------------|
| `tc_ledger` | Sales 产生的佣金计算快照 |
| `tc_ledger.status=Pending` | 未定义后续的待处理标签 |
| `commission_rules` | 展示规则主数据，不是执行器 |
| `salesperson_commissions` | calculator/ranking 演示记录 |
| `commission_periods` | 未接 ledger 的期间元数据 |
| `rebates` | 人工返利记录，与 payout 分离 |
| `treasury_payment_records` | 供应商资金付款，不是 salesperson payout |
| `ap_records` | 采购应付，不是佣金应付 |
| `expenses` / `expense_records` | 通用费用，未由 TC 生成 |
| `payroll` / salary surfaces | 薪资相邻实体，未接 TC |
| `treasury_bank_accounts.current_balance` | 资金余额，不因 TC Pending 变化 |
| `ar_records` | DO 来源应收，与 TC 状态无联动 |
| `receipts` | 客户收款，不更新 canonical TC |
| Finance dashboard estimated profit | 销售减采购等粗略口径，未扣 TC |
| commission payable | UNKNOWN / 未实现专用事实 |
| payout reference | UNKNOWN / TC schema 无字段 |

---

## 6. State Vocabulary

| Value / term | Domain | Meaning / caveat |
|--------------|--------|------------------|
| Pending TC | Sales | 计算记录待处理 |
| Pending rebate | Sales/commission surface | 独立返利待处理 |
| Unpaid AP | Finance procurement | 不等于佣金未付 |
| Approved expense | Finance expense | 未接 TC |
| payment record | Treasury supplier payout | 未接 salesperson |
| Paid/Settled commission | Not observed | 不得声称实现 |

---

## 7. UNKNOWN 与已查路径

| UNKNOWN | Paths searched |
|---------|----------------|
| 佣金最终由 payroll、expense、AP 还是线下支付 | finance services/residuals、payroll/salary/treasury templates、reports |
| Registry 同时归属 Sales/Finance 的权威解释 | Business_Module_Registry、business_modules、route ownership reports |
| Finance 是否有未挂载 TC handler | apps/finance、runtime/v14、legacy app decomposition reports |
| 已付款佣金历史存在哪里 | treasury payments、bank transactions、expenses、payroll searches |
| Pending TC 是否应计入利润和现金流预测 | finance dashboards/analytics、reports |
| 收款比例是否是正式支付前置条件 | receipts、calculator、tc writer、blueprint |
| 佣金税与币种的法定处理 | tax/payroll/locale/commission schemas |
| 结算审批是否通过 Approval Center 线下完成 | approval routes/tables/templates、commission searches |
| TC 是否可兑换现金及兑换率 | current_tc/standard_reward_tc、payroll/treasury docs |

---

## 8. Evidence Table

| Read-only path | Evidence |
|----------------|----------|
| `apps/sales/services.py` | Sales 是 canonical 计算 writer |
| `apps/sales/repository.py` | TC insert 与 rate lookup |
| `apps/sales/v14_residual.py` | TC/Commission/period/rebate 页面所有者 |
| `apps/finance/services.py` | Finance AR/AP/Treasury 流程无 TC 消费 |
| `apps/finance/repository.py` | payment/AP/receipt schemas 使用边界 |
| `apps/finance/v14_residual.py` | Finance residual 未见 TC 结算闭环 |
| `apps/finance/finance_ops_pages.py` | payroll/salary 相邻表面无 TC 链接 |
| `runtime/v14/legacy_support.py` | TC、AP、Treasury、payroll 相邻 schemas |
| `templates/tc_ledger.html` | 只读 Sales/Commission 台账 |
| `templates/payment_records.html` | supplier payment 语义 |
| `templates/expense_center.html` | 通用费用未接 TC |
| `Business_Module_Registry.md` | Sales 与 Finance 双重 ownership 声明 |
| `business_modules/sales.md` | Sales 订单与 commission 边界 |
| `business_modules/finance.md` | Finance 声明与实际表面漂移 |
| `docs/reports/V15_ENTERPRISE_READINESS_REPORT.md` | payroll integration 缺失、not production ready |
| `docs/knowledge/legacy-extract/finance/settlement-rules.md` | EAOS 只读交叉引用 |

**Root:** `H:\Workspace\EZAM_CRM - 9.0\` + paths above（最后一项为 EAOS 只读交叉引用）。
