# 销售订单收款视图（SO Payment View）— Legacy Knowledge

**Evidence strength:** Strong for SO detail live aggregation and Finance receipt write; strong negative for AR allocation  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0` (read-only)

---

## 1. Scope 与证据强度

本模块描述 SO 列表与详情中的 `payment_status`、`received_amount`、`balance_amount`，以及 Finance Receipt 如何更新这些字段。Finance 的 AR 台账与勾兑缺口只交叉引用 `../finance/receivables-payables.md` 和 `../finance/ar_receipt_reconciliation.md`，不复制正文。

关键事实：SO 详情按 receipts 实时求和并重算余额；SO 列表直接读取持久镜像字段。Receipt 创建同时写 receipts 和 SO 镜像，但不分配到 `ar_records`。

---

## 2. Business Rules

| ID | Rule / observed boundary | Evidence / consequence |
|----|--------------------------|------------------------|
| SP-R1 | SO 详情已收金额按该 SO 的所有 receipts 求和 | live aggregation 是详情权威 |
| SP-R2 | SO 详情余额为 SO total 减 receipts sum | 负值在详情截为零 |
| SP-R3 | SO 列表已收与余额直接显示持久字段 | 可能与 receipts 汇总漂移 |
| SP-R4 | Finance 创建收款前也按 receipts sum 计算剩余 | 不信任旧镜像作为输入 |
| SP-R5 | 快捷收款一次收取全部剩余余额 | 无部分金额输入表面 |
| SP-R6 | 余额小于等于零时不新增 receipt | 只把 SO 镜像修正为 Paid |
| SP-R7 | 新 receipt 默认 Bank Transfer | 不是用户选择结果 |
| SP-R8 | 新 receipt 币种固定为 USD | 未继承 SO/Quote currency |
| SP-R9 | receipt 成功后重算 total received 和 balance | 再写 SO 镜像 |
| SP-R10 | balance 为零写 `Paid`，否则写 `Partial` | 初始未收值可能来自翻译 `uncollected` |
| SP-R11 | 收款更新 `received_amount`、`balance_amount`、`payment_status` | Finance 是这些字段的活动写者 |
| SP-R12 | 收款不更新 SO 履约 `status` | 付款与履约状态正交 |
| SP-R13 | 收款不更新或关闭 `ar_records` | 无逐笔 AR allocation |
| SP-R14 | SO 详情 Statement tab 只展示该 SO 与其 receipts | 不是正式客户 AR Statement |
| SP-R15 | SO 详情可列出全部关联 receipts | Receipt 行是支付事实 |
| SP-R16 | Receipt list 普通用户按 SO salesperson name 过滤 | 详情仅见 Receipts.view，未见 owner 复核 |
| SP-R17 | 创建 receipt 需要 Receipts add 的 UI/route 门 | 写入属于 Finance 权限 |
| SP-R18 | 收款编号由 SO ID 与已收金额整数部分组成 | 不是稳定独立流水序列 |
| SP-R19 | SO list collection rate 使用持久 `received_amount` | 详情与 dashboard 可出现口径差 |
| SP-R20 | 客户 AR/Finance dashboard 采用 SO−Receipts 聚合 | 与 `ar_records` Receivable Center 并行 |
| SP-R21 | EAOS 不得把 `payment_status='Paid'` 解读为 AR 台账已核销 | Legacy 无该联动 |
| SP-R22 | Convert 不初始化 `balance_amount=total_amount`，镜像沿用 schema 默认零 | 首笔收款前列表可显示余额零而详情显示全额 |
| SP-R23 | Finance 是 convert 后 SO 三个 payment 镜像字段的活动写者 | Sales 详情只做实时重算 |
| SP-R24 | 快捷收款由 GET `/create_receipt/{so_id}` 触发写入 | 权限存在，但无 POST/确认表单 |
| SP-R25 | Receipt 不存在活动编辑、作废或退款生命周期 | 仅新增与客户级联删除证据 |

---

## 3. Process

### 3.1 SO 详情读取

1. 读取 SO header 和 items。
2. 按 `so_id` 汇总 receipts。
3. 计算 `total_amount - received`；负值显示为零。
4. 同时加载 receipt rows 和 DO rows。
5. 页面展示详情实时值，但 payment badge 仍来自 header `payment_status`。

SO 初建时 `received_amount` 与 `balance_amount` 均可保持零默认；因此尚无收款的列表行可能显示零余额，而详情实时余额为订单全额。

### 3.2 快捷收款

1. 读取 SO；不存在返回订单列表。
2. 汇总已有 receipts 并计算剩余。
3. 若剩余不大于零，修正 SO 镜像为 Paid，不新增 receipt。
4. 否则建立一笔等于全部剩余的 USD/Bank Transfer receipt。
5. 再次汇总 receipts，计算余额并写 SO 镜像状态。

### 3.3 与 AR 的边界

DO Post AR 单独建立全额 `ar_records`；Receipt 只关联 SO/customer，不关联 AR record。SO Paid 与 AR Unpaid 可同时存在。

---

## 4. Validation

| ID | Validation | Strength | Detail |
|----|------------|----------|--------|
| SP-V1 | SO 必须存在才能创建收款 | Hard | 不存在不写 |
| SP-V2 | 创建者必须有 Receipts add | Hard route/UI gate | |
| SP-V3 | 剩余余额必须大于零才新增 receipt | Hard | 防快捷路径超收 |
| SP-V4 | Receipt customer 必须等于 SO customer | Derived | 从 SO header 复制 |
| SP-V5 | 收款金额必须由用户确认 | Missing | GET 快捷动作直接全额收款 |
| SP-V6 | 支持部分收款金额输入 | Missing | 活动创建总是收全额剩余 |
| SP-V7 | Receipt currency 必须等于订单币种 | Missing | 固定 USD |
| SP-V8 | Receipt method/reference/attachment 必须完整 | Missing | 默认或空值 |
| SP-V9 | 镜像字段必须与 receipts sum 一致 | Recomputed only on create | 无周期对账 |
| SP-V10 | Receipt 必须分配到具体 AR | Missing | 无 allocation |
| SP-V11 | Receipt detail 必须复核 salesperson owner | Missing | 仅模块 view |
| SP-V12 | receipt number 必须唯一稳定 | UNKNOWN | 已收金额整数参与编号 |
| SP-V13 | 收款写 receipt 与 SO 镜像必须同一事务 | Mixed | insert 与 update 分别 commit |
| SP-V14 | 已取消 SO 不得收款 | Missing | 未检查履约状态 |

---

## 5. Data Semantics

| Entity / field | Honest Legacy meaning |
|----------------|-----------------------|
| `sales_orders.total_amount` | SO 收款基数 |
| `receipts.amount` | 实际收款事实 |
| `receipts.so_id` | Receipt 对应 SO |
| `receipts.customer_id` | 从 SO 复制的客户归属 |
| `receipts.currency` | 活动快捷收款固定 USD |
| `receipts.payment_method` | 活动快捷收款固定 Bank Transfer |
| `receipts.reference_no` | 可用参考号；快捷路径留空 |
| `sales_orders.received_amount` | receipts sum 的持久镜像 |
| `sales_orders.balance_amount` | 非负剩余余额镜像；convert 后可默认零，首笔收款才同步 |
| `sales_orders.payment_status` | Finance 驱动的 Paid/Partial/初始未收标签 |
| SO detail `received_amount` | 运行时 receipts sum，不是镜像字段 |
| SO detail `balance` | `max(total - receipts, 0)` |
| list collection rate | 持久 received / total |
| receipt history | 同 SO 的 receipts 时间倒序列表 |
| `ar_records.balance` | DO 来源权责台账；Receipt 不更新 |
| `payment_records` | 供应商/资金付款记录，不是客户 Receipt |

---

## 6. State Vocabulary

| Value / term | Meaning / caveat |
|--------------|------------------|
| Uncollected / Unpaid | 转换初始未收语义，存值可能不同 |
| Partial | SO 镜像表示仍有余额且已执行收款 |
| Paid | SO 镜像余额清零 |
| negative live balance | 详情被截零，原始超收语义被隐藏 |
| Unpaid (`ar_records`) | AR 台账状态，可与 SO Paid 并存 |
| Closed (`ar_records`) | 台账词汇；未观察到 Receipt 写入 |

---

## 7. UNKNOWN 与已查路径

| UNKNOWN | Paths searched |
|---------|----------------|
| 持久镜像与 receipts 漂移时哪个报表负责修复 | sales/finance repositories、reports、scheduler |
| Receipt number 在小数与并发场景是否冲突 | finance service、DDL/index、error handling |
| 快捷收款为何使用 GET 且没有金额确认页 | finance router/templates、permission reports |
| 真实订单币种如何传到 Receipt | quotation currency、sales schema、finance service |
| 部分收款是否存在另一活动入口 | finance routers/templates/API/residual searches |
| Receipt void/refund/delete 的正式生命周期 | finance services/routes/templates、reports |
| SO Paid 如何与 `ar_records` Closed 对账 | finance AR/receipt paths、reconciliation docs |
| 已取消或未 Open SO 是否允许收款 | sales status + finance create path |
| SO 列表镜像是否由后台周期重算 | scheduler/tasks/reports |

---

## 8. Evidence Table

| Read-only path | Evidence |
|----------------|----------|
| `apps/sales/services.py` | SO 详情 receipts live sum 和余额截零 |
| `apps/sales/repository.py` | 详情汇总、列表 header 字段、dashboard |
| `apps/sales/router.py` | SO view 权限 |
| `apps/finance/services.py` | 快捷收款规则与 SO 镜像更新 |
| `apps/finance/repository.py` | Receipt 持久化、sum 和 payment fields |
| `apps/finance/router.py` | Receipts view/add 权限 |
| `apps/finance/v14_residual.py` | Finance 残留收款/AR 表面 |
| `apps/finance/receipt_ar_expense_pages.py` | 平行 Receipt/AR 页面与余额逻辑 |
| `apps/inventory/services.py` | DO Post AR 与 Receipt 独立 |
| `templates/sales_order_detail.html` | live KPI、Statement tab、Receipt action |
| `templates/sales_orders.html` | 镜像字段和 collection rate |
| `templates/receipt_detail.html` | Receipt360 的实时汇总 |
| `business_modules/sales.md` | Sales 与 Finance 边界 |
| `business_modules/finance.md` | Finance 模块表面与过时声明边界 |
| `docs/reports/Business_Strong_A011_AR_Ops_Report.md` | AR/Receipt 并行事实 |
| `docs/reports/Business_Strong_A012_SO_Ops_Report.md` | SO payment view 审计 |
| `docs/reports/V151E_Volume010_Finance_Inventory_Business_Chain_Extraction_Report.md` | Finance/Inventory 链证据 |
| `runtime/v14/legacy_support.py` | SO payment 镜像字段 schema 默认值 |
| `docs/knowledge/legacy-extract/finance/ar_receipt_reconciliation.md` | EAOS 只读交叉引用 |

**Root:** `H:\Workspace\EZAM_CRM - 9.0\` + paths above（最后一项为 EAOS 只读交叉引用）。
