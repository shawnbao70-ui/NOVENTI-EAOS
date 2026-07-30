# 应收与收款勾兑（AR / Receipt Reconciliation）— Legacy Knowledge

**Evidence strength:** Strong for observed SO receipt posting; strong negative evidence for missing `ar_records` reconciliation  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0` (read-only)

---

## 1. Scope 与证据强度

本模块专门描述 `ar_records` 应收台账与 `receipts` 客户收款之间的勾兑关系。

Legacy 实际存在两条并行链：

- **收款链**：收款关联销售订单（SO），汇总后回写 SO 的已收、余额和付款状态；
- **应收链**：交付单（DO）经 Human Approved 后建立 `ar_records`，初始全额未收。

全库未观察到收款后更新 `ar_records.balance/status`、建立收款分配明细、关闭应收或反向冲销的活动代码。因此“勾兑”在 Legacy 中是**缺失能力**，不是隐藏自动化。

本结论基于 `apps/finance/`、`apps/inventory/`、`runtime/v14/legacy_support.py` 及 AR/Receipt 页面交叉检查。无法证实的行为均标为 UNKNOWN。

---

## 2. 业务规则

| ID | 规则描述 | 触发条件 | 例外 / 缺口 | EAOS 重写备注 |
|----|----------|----------|--------------|----------------|
| ARR-R1 | 收款以 `so_id` 关联销售订单，不以 AR 记录关联 | 新增收款 | `receipts` 无 `ar_id` 或分配记录 | 建立 Receipt Allocation |
| ARR-R2 | 快捷收款金额等于该 SO 的全部剩余余额 | 从 SO 创建收款 | 没有自由输入部分收款金额的主流程 | 部分收款需明确支持 |
| ARR-R3 | SO 剩余余额 = SO 总额 − 同 SO 收款合计 | 收款前后 | 不读取 `ar_records` | 订单余额不是 AR 子账余额 |
| ARR-R4 | 收款后回写 SO 的累计已收、余额和付款状态 | 收款成功 | 只更新 SO | 应同时生成可审计核销 |
| ARR-R5 | SO 余额为零时状态为 `Paid`，否则为 `Partial` | 收款后 | 初始未收词汇另有 `Unpaid` / `Uncollected` | 统一状态词汇 |
| ARR-R6 | SO 已无余额时不再新增收款，并修正为 Paid | 重复触发收款 | 没有预收款或贷项余额语义 | 不用截断替代预收 |
| ARR-R7 | DO 记应收以 DO 号为来源，金额和余额均取 DO 总额，状态 `Unpaid` | Human Approved | 不要求 DO 已发运，仅警告 | 明确应收确认点 |
| ARR-R8 | 同一 DO 已有 AR 时只警告，仍可重复记账 | 再次记应收 | 会造成重复债权 | 来源应唯一或显式冲销 |
| ARR-R9 | 客户 AR360 余额按客户全部 SO 总额减客户全部收款 | 查看客户应收 | 不使用 `ar_records` | 标为经营汇总口径 |
| ARR-R10 | Receivable Center 余额取 `ar_records` | 查看台账 | 不因收款自动下降 | 标为权责台账口径 |
| ARR-R11 | Receipt360 的余额、回款率和历史都按 SO 收款计算 | 查看收款 | “Invoice”标签页也只展示 SO 上下文 | 不应误称发票勾兑 |
| ARR-R12 | AR Statement 可从客户维度打印 | 查看/打印 | 是否以 SO 口径还是 AR 台账口径为唯一账单依据 UNKNOWN；已检索 `document/nde_engine.py`、收款/AR模板 | 账单必须披露口径 |
| ARR-R13 | `ar_records` 的开放统计以状态不等于 Closed 判断 | AR Center KPI | 没有观察到 Closed 写入流程 | 开放数可能永久累积 |
| ARR-R14 | 收款不更新 `ar_records` 的 balance、status 或关闭时间 | 收款成功 | 全库未发现相应更新 | 这是主要勾兑缺口 |
| ARR-R15 | 多笔收款可以汇总到同一 SO | 收款历史 | 当前快捷动作通常一次收清，历史结构仍支持多笔 | 核销应按笔保存 |
| ARR-R16 | 非 Admin/Manager 的收款列表按 SO 销售归属过滤 | 列表查看 | AR Center 的同粒度归属控制不一致 | 应收与收款权限需一致 |
| ARR-R17 | AR 风险带按余额阈值，不是账龄 | 查看 AR | 无可靠到期日驱动 | 不把风险带用于核销优先级 |
| ARR-R18 | 催收基于 SO−receipts 客户余额，并非某条到期 AR | AR Reminder | 无应收明细绑定 | 催收应关联待核销应收 |
| ARR-R19 | DDL 存在 `collections` 表，可按 `receivable_id` 表达收款分配意图 | 数据结构初始化 | 未发现活动业务写入；且它关联 `receivables`，不是主链 `ar_records` | 只视为未启用设计，不视为已实现勾兑 |

---

## 3. 流程

### 3.1 现有收款过账流程

1. 从销售订单发起收款。
2. 读取 SO 总额及该 SO 的既有收款合计。
3. 计算剩余余额。
4. 若余额不大于零，只把 SO 修正为 Paid。
5. 若有余额，按全额剩余建立 Receipt。
6. 重新汇总该 SO 收款。
7. 回写 SO 的累计已收、剩余余额和 Paid/Partial。
8. **流程结束，不访问或更新 `ar_records`。**

### 3.2 现有应收计提流程

1. 从交付单进入“Post AR”人工确认页。
2. 展示客户、DO、SO、明细和金额。
3. 提示重复来源或尚未发运，但不硬阻断。
4. Human Approved 后建立全额 `Unpaid` AR。
5. 进入 AR Dashboard。
6. **后续收款仍从 SO 发起，不从该 AR 发起。**

### 3.3 客户经营余额流程

1. 按客户汇总销售订单总额。
2. 按客户汇总全部 Receipt。
3. 两者相减得到 AR360 客户余额。
4. 该结果用于余额风险带和催收草稿。
5. 该结果与 `ar_records` 合计不自动对账。

### 3.4 缺失的勾兑流程

以下流程在活动代码中均未观察到：

1. 选择一笔 Receipt；
2. 选择一条或多条 AR；
3. 按金额分配；
4. 处理尾差、折扣、坏账或汇差；
5. 更新 AR 已收与余额；
6. 将结清 AR 改为 Paid/Closed；
7. 生成可撤销的核销审计记录。

**UNKNOWN 路径：** 已检索 `apps/finance/`、`apps/inventory/`、`runtime/v14/legacy_support.py` 中 reconcile/allocation/writeoff/settle 及 AR 更新行为，未发现活动实现。

---

## 4. 校验

| ID | 校验 | 强度 | 说明 |
|----|------|------|------|
| ARR-V1 | 创建收款前 SO 必须存在 | Hard |
| ARR-V2 | SO 剩余余额必须大于零才新增收款 | Hard |
| ARR-V3 | 收款查看/新增需 Receipts 权限 | Hard at route |
| ARR-V4 | DO 记应收需 Human Confirm | Hard |
| ARR-V5 | 同一 DO 不得重复产生 AR | Missing | 仅警告 |
| ARR-V6 | 收款必须关联 AR | Missing | 只关联 SO |
| ARR-V7 | 分配金额合计不得超过 Receipt 金额 | Not implemented |
| ARR-V8 | 分配金额不得超过 AR 未收余额 | Not implemented |
| ARR-V9 | 已关闭 AR 不得再次核销 | Not implemented |
| ARR-V10 | 收款币种与 AR 币种必须一致或记录汇率 | Missing | 快捷收款默认 USD；AR 无可靠币种字段 |
| ARR-V11 | 超收必须形成预收/退款/贷项 | Missing | 显示余额会截为零 |
| ARR-V12 | 冲销必须反向恢复 SO 与 AR | Missing |
| ARR-V13 | 部分核销必须保持 Partial 状态 | Missing for `ar_records` |
| ARR-V14 | AR 到期日/账龄参与核销 | Missing | 页面明确非 day-aging |
| ARR-V15 | Receipt 与 AR 客户必须一致 | Not implemented | 无分配对象 |
| ARR-V16 | 勾兑动作需审批与审计 | UNKNOWN | 已检索 `apps/approval/` 与 Finance，未见 reconciliation gate |

---

## 5. 数据含义

### 5.1 核心实体

| Entity | Legacy 含义 |
|--------|-------------|
| `receipts` | 客户现金收款事件；关联客户与 SO |
| `sales_orders.received_amount` | SO 维度累计已收 |
| `sales_orders.balance_amount` | SO 维度剩余未收 |
| `sales_orders.payment_status` | SO 维度收款进度 |
| `ar_records` | DO 来源的权责应收台账 |
| `receivables` | 另一套带发票号和到期日的遗留结构；主流程未见持续使用 |
| `collections` | 面向 `receivables` 的收款明细设计表；仅见 DDL/计数，未见活动写入 |
| Receipt→`ar_records` Allocation | UNKNOWN / 未发现 |
| Reconciliation History | UNKNOWN / 未发现 |

### 5.2 关键关联

| From | To | 关系 |
|------|----|------|
| Receipt | Sales Order | `so_id` 直接关联 |
| Receipt | Customer | `customer_id` 直接关联 |
| AR Record | Delivery Order | 仅以 `source_no=do_no` 记录来源 |
| AR Record | Customer | `customer_id` 直接关联 |
| Receipt | AR Record | 无直接关联 |

### 5.3 三种余额

| 余额 | 计算口径 |
|------|----------|
| SO balance | SO 总额 − 同 SO Receipts |
| Customer operational AR | 客户全部 SO − 客户全部 Receipts |
| Formal AR ledger balance | `ar_records.balance` 合计 |

三者没有可观察到的自动一致性约束。

---

## 6. 状态词汇

| Status | 使用位置 | 含义 |
|--------|----------|------|
| `Uncollected` | SO 转换后的本地化付款状态 | 尚未收款 |
| `Unpaid` | SO 默认或新 AR | 尚未收/付 |
| `Partial` | SO | 已部分收款、仍有余额 |
| `Paid` | SO | SO 余额清零 |
| `Open` | 遗留 receivables / AR 页面兼容 | 开放 |
| `Closed` | AR Center 的关闭判断 | 理论已关闭；未发现写入路径 |

Receipt 本身没有可观察到的核销状态；`ar_records` 新建为 Unpaid，但收款不会推进其状态。

---

## 7. 只读来源路径

| Path | Why cited |
|------|-----------|
| `apps/finance/services.py` | Receipt 创建、SO 回写、AR 汇总和催收 |
| `apps/finance/repository.py` | Receipt 与 SO 聚合、AR Center 查询及无 AR 更新 |
| `apps/finance/router.py` | Receipt/AR 页面与权限入口 |
| `apps/finance/receipt_ar_expense_pages.py` | 迁移前同口径收款逻辑的交叉证据 |
| `apps/inventory/services.py` | DO→AR Human Approved、重复仅警告 |
| `runtime/v14/legacy_support.py` | receipts、ar_records、receivables、SO 付款字段 |
| `templates/receipt_detail.html` | SO 余额、回款率、历史与非账龄说明 |
| `templates/receipts.html` | 收款只能从 SO 发起的诚实说明 |
| `templates/ar.html` | 客户 SO−Receipts 口径与非账龄风险带 |
| `templates/receivable_center.html` | `ar_records` 台账及状态词汇 |
| `docs/reports/V18_SO_DO_Invoice_TypeA_Report.md` | DO Invoice 实为 AR accrual |
| `docs/reports/Business_Strong_A011_AR_Ops_Report.md` | AR 诚实性和未完成项 |
| `MODULE_BOUNDARY_REPORT.md` | Finance 缺少统一 posting/reconciliation service 的边界风险 |
| `apps/finance/` / `apps/inventory/` / `runtime/v14/legacy_support.py` | 勾兑、核销、冲销 UNKNOWN 的检索范围 |

**Root:** `H:\Workspace\EZAM_CRM - 9.0\` + paths above.
