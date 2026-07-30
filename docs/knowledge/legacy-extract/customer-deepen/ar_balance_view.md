# 客户应收余额视图与收款交界（Customer AR Balance View）— Legacy Knowledge

**Evidence strength:** Strong for Customer360 operational balance; strong negative for AR-ledger reconciliation and currency-safe aggregation  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0` (read-only)

---

## 1. Scope 与证据强度

本模块描述客户列表/Customer360 的“AR Balance”经营视图，以及 Statement/Receivable Center 的台账视图与收款交界。经营视图的活动公式为：

**客户经营余额 = 该客户全部销售订单 `total_amount` 合计 − 该客户全部 `receipts.amount` 合计。**

经营视图不读取 `ar_records`，不执行收款到应收记录的核销，也不按发票、交付、到期日或币种拆分。相反，Customer Statement 与 Receivable Center 读取 `ar_records.balance`。两套余额并行且无自动对账；正式 AR 台账及勾兑缺口参见 `../finance/receivables-payables.md` 与 `../finance/ar_receipt_reconciliation.md`。

---

## 2. Business Rules

| ID | Rule / observed boundary | Evidence / consequence |
|----|--------------------------|------------------------|
| CAB-R1 | 客户余额取全部 SO 总额减全部 Receipt | 强：列表和详情使用同一口径 |
| CAB-R2 | 汇总键是 `customer_id` | 不要求 Receipt 与具体 AR 对应 |
| CAB-R3 | Customer360 同时展示 Total Sales、Received、AR Balance | 是经营汇总视图 |
| CAB-R4 | 客户列表也展示同口径余额和订单数 | 便于负责人查看，不是总账 |
| CAB-R5 | 该余额不读取 `ar_records.balance` | 可能与正式应收台账不同 |
| CAB-R6 | 收款事实来自 `receipts.amount` | 不直接使用 SO `received_amount` 镜像字段 |
| CAB-R7 | 收款主流程关联 SO 和 customer | 仍无 AR allocation |
| CAB-R8 | 客户余额可为负数 | Customer service 未像 SO 详情那样截零 |
| CAB-R9 | 负余额没有预收款、退款或贷项语义 | 只能视为口径差异/超收信号 |
| CAB-R10 | 余额大于零时 Customer360 提供 AR Reminder 动作 | 催收仍基于经营余额 |
| CAB-R11 | 余额阈值生成 healthy/watch/risk 展示 | 不是日龄或信用决策 |
| CAB-R12 | Credit tab 的 unpaid/partial/clear 由余额和是否有收款派生 | 不等同 AR 记录状态 |
| CAB-R13 | 客户 Statement 可打印 | 必须披露该视图口径，不能暗示已核销 |
| CAB-R14 | 非 Admin/Manager 客户列表按 `owner=username` 过滤 | 列表有负责人范围 |
| CAB-R15 | 客户详情路由未见 Customers.view 或 owner 复核 | 可直接访问其他客户余额的风险 |
| CAB-R16 | Customer360 运行时 AI 读取同一余额并给催收建议 | `gateway_invoked=False`，不自动收款 |
| CAB-R17 | 首屏把余额币种固定显示为 USD | 实际 SO/Receipt 汇总未做币种转换 |
| CAB-R18 | 多币种订单和收款会被直接数值相加 | 经营余额可能无有效单一币种含义 |
| CAB-R19 | Customer360 只展示最近 20 笔订单/收款，但合计查询覆盖全部记录 | 明细窗口与总额范围不同 |
| CAB-R20 | 删除客户会删除其 Receipts、SO 和 Quotes | 经营余额历史会被破坏，未保留财务审计 |
| CAB-R21 | Customer Statement 从 `ar_records` 取行，并按 `balance` 汇总 | 与同页经营余额可能不同 |
| CAB-R22 | `/ar` 未见路由级权限检查 | 服务内 owner 条件不能替代模块权限 |
| CAB-R23 | 首屏使用 10k/100k 风险阈值，Credit tab 使用 30k 中风险阈值 | 无统一权威政策，且都不是账龄 |

---

## 3. Process

### 3.1 客户余额生成

1. 按客户 ID 汇总所有销售订单金额。
2. 按客户 ID 汇总所有收款金额。
3. 两者相减得到 `balance`。
4. Customer360 将其展示为 AR Balance。
5. 同一值用于风险带、收款状态提示和 AR Reminder 入口。

### 3.2 收款交界

1. 收款从销售订单发起。
2. Receipt 保存 SO 和客户引用。
3. 客户详情重新汇总 Receipt 金额，余额随之下降。
4. 正式 `ar_records` 不随该过程更新。
5. 因此客户余额变化不证明某条应收已核销或关闭。

### 3.3 明细与 Statement

1. Customer360 展示最近 20 张 SO 和最近 20 笔 Receipt。
2. 顶部总额使用无 limit 的聚合。
3. Statement 入口按客户 ID 打开，NDE 引擎读取该客户的 `ar_records`。
4. Statement 总额按 `ar_records.balance` 汇总，而不是 SO−Receipts 经营余额。
5. 未观察到两个口径的差异披露，也未观察到按币种、账龄或 AR 来源切换口径。

### 3.4 缺失的对账流程

未观察到：选择客户经营余额 → 与 `ar_records` 汇总对比 → 定位差异来源 → 分配 Receipt → 处理预收/退款/汇差 → 审批调整 → 冻结月结余额。

---

## 4. Validation

| ID | Validation | Strength | Detail |
|----|------------|----------|--------|
| CAB-V1 | 客户必须存在才展示详情 | Hard | 不存在返回 404 |
| CAB-V2 | 客户列表需 Customers.view | Hard at list | 详情未同样检查 |
| CAB-V3 | 普通用户列表只看本人 owner 客户 | Hard at list query | 详情无 owner gate |
| CAB-V4 | Receipt 客户与 SO 客户必须一致 | Weak / not proven here | 余额只按 receipt.customer_id 汇总 |
| CAB-V5 | Customer balance 必须与 `ar_records` 对账 | Missing | 两套口径独立 |
| CAB-V6 | 不同币种不得直接相加 | Missing | 无转换/分组 |
| CAB-V7 | 负余额必须分类为预收或退款待办 | Missing | 原值直接展示 |
| CAB-V8 | 最近 20 笔明细必须明确非全量 | Weak | 模板未突出窗口限制 |
| CAB-V9 | Statement 必须声明余额来源与截止时间 | Missing | 已证实使用 AR 台账，但未见口径元数据 |
| CAB-V10 | 催收前必须选择具体到期应收 | Missing | 仅客户经营余额 |
| CAB-V11 | 删除客户前必须保留财务记录 | Missing | 当前级联删除 Receipt/SO |
| CAB-V12 | AI 不得自动创建收款或改余额 | Hard boundary | 当前只读建议 |
| CAB-V13 | `/ar` 和客户详情必须有模块及对象级查看门 | Missing | 两入口均未见完整 gate |
| CAB-V14 | Statement 与 Customer360 必须披露或校验差异 | Missing | 同一客户可输出两个总额 |
| CAB-V15 | 同一 DO 重复生成 AR 必须硬拦截 | Missing | 现有路径仅 warning |

---

## 5. Data Semantics

| Entity / field | Honest Legacy meaning |
|----------------|-----------------------|
| `total_so` | 该客户全部 SO `total_amount` 合计 |
| `total_receipt` | 该客户全部 Receipt `amount` 合计 |
| `balance` | `total_so - total_receipt` |
| Customer list `balance` | 相关子查询生成的同口径经营余额 |
| `receipts.customer_id` | 客户收款归属 |
| `receipts.so_id` | 收款对应销售订单 |
| `sales_orders.total_amount` | 经营余额的销售端基数 |
| `sales_orders.received_amount` | SO 镜像累计字段；本客户视图不用于合计 |
| `sales_orders.balance_amount` | SO 镜像余额；本客户视图重新计算 |
| `ar_records.balance` | DO 来源正式 AR 台账余额；本视图不读取 |
| Credit Watch / watch / healthy | 经营余额阈值派生健康标签 |
| clear / partial / unpaid | Customer360 根据余额/Receipt 派生的展示状态 |
| `v18_customer_first.currency='USD'` | 首屏硬编码展示币种，不是聚合转换结果 |
| customer Statement | 从 `ar_records` 生成的客户维度台账文档 |
| Statement `grand_total` | 对该客户 `ar_records.balance` 的汇总 |
| negative balance | 可能的超收/预收或数据差异，未结构化 |
| AR allocation | UNKNOWN / 未实现 |

---

## 6. State Vocabulary

| Value / term | Meaning / caveat |
|--------------|------------------|
| Healthy Customer | 低余额展示标签 |
| Needs Follow-up | 余额大于 10,000 的首屏提示 |
| Credit Watch | 余额大于 100,000 的首屏提示 |
| `clear` | 经营余额小于等于零 |
| `partial` | 余额大于零且存在 Receipt |
| `unpaid` | 余额大于零且未见 Receipt |
| Paid / Partial / Unpaid | SO/AR 相邻状态，不等同本视图自身状态 |
| Closed | AR 台账词汇；客户经营余额不写该状态 |

---

## 7. UNKNOWN 与已查路径

| UNKNOWN | Paths searched |
|---------|----------------|
| Statement 是否应并列披露 SO−Receipt 与 AR 台账两套口径 | customer template、NDE/print preview、finance statement paths；未见披露政策 |
| 客户余额与 `ar_records` 差异是否有报表 | `apps/customer/**`, `apps/finance/**`, docs/reports reconciliation searches |
| 多币种客户余额应使用哪一基准币种 | customer/finance/currency paths、locale-commerce knowledge |
| 负余额如何处理为预收、退款或贷项 | finance receipt/refund/credit-note paths |
| Receipt.customer_id 与 SO.customer_id 是否有硬一致性校验 | finance services/repository、receipt DDL |
| 客户详情是否应执行 owner 级对象权限 | customer router/permissions、permission reports |
| AR Reminder 应关联哪条应收和到期日 | customer actions、finance reminder、`ar_records` |
| 客户删除后财务记录如何恢复或审计 | customer cascade delete、finance history/archive paths |
| 10k、30k 与 100k 风险阈值的权威政策 | Customer360 first、customer Credit tab、AR templates/reports |

---

## 8. Evidence Table

| Read-only path | Evidence |
|----------------|----------|
| `apps/customer/services.py` | Customer360 余额公式、风险带、USD 首屏标签 |
| `apps/customer/repository.py` | 客户 SO/Receipt 聚合和最近 20 笔明细 |
| `apps/customer/router.py` | 列表权限与详情对象权限差异 |
| `templates/customer_detail.html` | AR、Credit、Statement 和收款展示 |
| `templates/customers.html` | 客户列表余额和负责人范围表面 |
| `core/object360/customer/runtime.py` | AI 使用同一余额且不调用 gateway |
| `apps/finance/services.py` | Receipt 主流程和 SO 回写边界 |
| `apps/finance/repository.py` | Receipt/SO 与 AR 台账并行事实源 |
| `apps/finance/router.py` | `/ar` 路由权限缺口及收款路由 |
| `document/nde_engine.py` | Statement 从 `ar_records` 取行并汇总余额 |
| `runtime/v14/legacy_support.py` | Receipts、SO、AR 数据结构 |
| `business_modules/finance.md` | Finance 是财务关闭权威，不是 Customer360 |
| `business_modules/crm.md` | Customer 作为收入链上游主数据 |
| `docs/reports/Business_Strong_A015_Customer_Ops_Report.md` | Customer AR/信用展示诚实性 |
| `docs/reports/Business_Strong_A011_AR_Ops_Report.md` | AR 口径和未完成勾兑 |
| `docs/knowledge/legacy-extract/finance/receivables-payables.md` | 两套应收口径交叉引用 |
| `docs/knowledge/legacy-extract/finance/ar_receipt_reconciliation.md` | `ar_records` 与 Receipt 无勾兑交叉引用 |

**Root:** `H:\Workspace\EZAM_CRM - 9.0\` + paths above（最后两项为当前 EAOS 只读交叉引用）。
