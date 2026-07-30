# 应付付款与清算（AP / Payment Clearing）— Legacy Knowledge

**Evidence strength:** Strong for purchase invoice→AP posting and treasury payment→bank deduction; strong negative evidence for missing AP clearing  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0` (read-only)

---

## 1. Scope 与证据强度

本模块描述采购发票形成 `ap_records`、人工登记供应商付款、银行账户扣账，以及三者之间缺失的清算闭环。

可确认的两条链是：

- **应付链**：采购单生成采购发票时，同步建立同额 `ap_records`；
- **资金链**：人工付款记录关联供应商与银行账户，登记后直接扣减银行余额。

付款记录没有可观察到的 AP 或采购发票关联字段，付款后也未观察到更新 `ap_records.paid_amount/balance/status` 或 `purchase_invoices` 付款字段。因此该动作是**资金付款登记**，不是已完成的 AP 核销。

本模块只描述 Legacy 内部 AP 与 Treasury 事实，**不构成 external PSP 产品开口**。

---

## 2. 业务规则

| ID | 规则描述 | 触发条件 | 例外 / 缺口 | EAOS 重写备注 |
|----|----------|----------|--------------|----------------|
| APC-R1 | 一张采购单在服务层最多生成一张采购发票 | 创建采购发票 | 以 `purchase_id` 事前检查；数据库唯一约束证据不足 | 事务内唯一约束 |
| APC-R2 | 采购发票金额取采购单总额 | 创建发票 | 未见税额、运费、贷项调整分拆 | 保留金额构成 |
| APC-R3 | 新采购发票初始 `paid_amount=0`、余额=总额、状态 Unpaid | 创建发票 | 无部分付款初始化 | 建立统一付款状态机 |
| APC-R4 | 发票创建后同步建立同额 AP，初始已付为零、余额为全额、状态 Unpaid | 发票创建 | 两次写入的原子性证据不充分 | 发票与 AP 同一事务 |
| APC-R5 | AP Dashboard 直接汇总 `ap_records` 的总额、已付和余额 | 查看 AP | 不从付款记录反算 | `ap_records` 是仪表盘主口径 |
| APC-R6 | AP 不允许从页面自由建立，来源应为采购/采购发票 | AP 页面 | 资金付款仍可独立登记 | 保留来源约束 |
| APC-R7 | 人工付款选择供应商、银行账户、付款日期、金额、方式和备注 | Treasury add | 不选择 AP 或发票 | 付款申请必须带清算对象 |
| APC-R8 | 付款编号由 `PAY` 加秒级时间戳形成 | 付款登记 | 同秒并发时唯一性证据不足 | 使用原子序列 |
| APC-R9 | 付款登记后直接从所选银行账户余额扣款 | 付款成功 | 未观察到账户余额充足校验 | 禁止负余额或明确透支 |
| APC-R10 | 付款登记不会更新 AP 已付、余额或状态 | 付款成功 | 全库未见对应联动 | 这是主要清算缺口 |
| APC-R11 | 付款登记不会更新采购发票的 paid_amount、balance_amount 或 status | 付款成功 | 全库未见对应联动 | 发票和 AP 状态需单一来源 |
| APC-R12 | Payment360 展示付款事实和供应商，但不展示核销明细 | 查看付款 | 无发票/AP 分配页 | 增加 clearing trace |
| APC-R13 | 供应商付款记录与银行账户构成资金视图 | Treasury 页面 | 不代表总账过账或银行已对账 | 区分登记、执行、清算、对账 |
| APC-R14 | 付款没有可观察到的审批状态机 | 新增付款 | 路由权限不等于逐笔审批 | 财务付款需 Human Approved |
| APC-R15 | AP 逾期供应商与风险汇总使用 AP 余额 | Dashboard | 到期日驱动证据不足，可能仅余额排序 | 不得冒充账龄分析 |
| APC-R16 | 付款不能证明外部银行或支付服务已执行 | 付款记录存在 | 无外部交易状态/回执语义 | 保持内部事实边界 |
| APC-R17 | 多币种清算、汇率和汇兑差额规则 UNKNOWN | AP/Payment | 已检索 Finance 实体、服务和模板，未发现闭环 | 币种与汇率须显式 |
| APC-R18 | 贷项、预付款、保留款、折扣和尾差处理 UNKNOWN | AP clearing | 已检索 `apps/finance/` 与运行时表结构 | 不可用备注替代会计语义 |

---

## 3. 流程

### 3.1 采购发票与 AP 过账

1. 从采购单进入创建采购发票动作。
2. 校验采购单存在。
3. 检查同一采购单是否已有采购发票。
4. 按采购单总额建立 Unpaid 采购发票。
5. 以发票为来源建立同额 Unpaid AP。
6. AP 总额、已付和余额进入 Dashboard 汇总。

### 3.2 人工供应商付款

1. 用户进入 Treasury 付款登记。
2. 选择供应商和银行账户。
3. 填写日期、金额、付款方式与备注。
4. 建立付款记录。
5. 所选银行账户余额直接减少同额。
6. **流程在此终止：不选择采购发票或 AP，不执行核销。**

### 3.3 缺失的 AP 清算流程

以下步骤在活动代码中未观察到：

1. 选择待付 AP / 采购发票；
2. 将一笔付款分配至一条或多条 AP；
3. 支持一条 AP 被多笔付款逐步结清；
4. 校验供应商、币种和可用余额；
5. 更新 AP 与采购发票的累计已付和剩余余额；
6. 将部分付款标为 Partial、结清标为 Paid/Closed；
7. 处理预付款、贷项、折扣、尾差和汇差；
8. 反向冲销错误付款并恢复余额；
9. 将内部付款记录与银行流水对账。

**UNKNOWN 路径：** 已检索 `apps/finance/`、`runtime/v14/legacy_support.py`、付款/AP 模板中的 clearing/allocation/settle/reconcile、AP 更新和采购发票更新行为，未发现活动实现。

---

## 4. 校验

| ID | 校验 | 强度 | 说明 |
|----|------|------|------|
| APC-V1 | 创建采购发票前采购单必须存在 | Hard |
| APC-V2 | 同一采购单不得重复创建采购发票 | Hard at service | 数据库约束 UNKNOWN |
| APC-V3 | 付款新增需 Treasury add 权限 | Hard at route |
| APC-V4 | 付款查看需 Treasury view 权限 | Hard at route |
| APC-V5 | 供应商必须存在 | Weak / FK evidence UNKNOWN | 表单要求选择；服务端显式校验证据不足 |
| APC-V6 | 银行账户必须存在 | Weak | 更新无命中时的完整错误处理证据不足 |
| APC-V7 | 付款金额必须大于零 | Weak / missing server-side | HTML 输入限制与 move-only validator 不等于活动业务校验 |
| APC-V8 | 银行账户余额必须足够 | Missing | 可直接形成负余额风险 |
| APC-V9 | 付款供应商必须与 AP 供应商一致 | Missing | 无 AP 选择 |
| APC-V10 | 分配额不得超过付款额 | Not implemented |
| APC-V11 | 分配额不得超过 AP 余额 | Not implemented |
| APC-V12 | 已结清 AP 不得再次付款 | Not implemented |
| APC-V13 | 发票与 AP 更新必须原子一致 | UNKNOWN | 已检索创建流程，未确认显式事务边界 |
| APC-V14 | 付款与银行扣账必须原子一致 | UNKNOWN | 已检索付款服务，未确认失败回滚保证 |
| APC-V15 | 付款币种与 AP/银行账户币种一致 | Missing / UNKNOWN |
| APC-V16 | 付款需逐笔审批或 Human Confirm | Missing | 权限控制不能替代审批 |
| APC-V17 | 冲销需保留原付款并生成反向记录 | Missing |
| APC-V18 | 银行回执/流水匹配后才标记清算 | Not implemented |

---

## 5. 数据含义

### 5.1 核心实体

| Entity | Legacy 含义 |
|--------|-------------|
| `purchase_invoices` | 由采购单生成的供应商发票头 |
| `ap_records` | 采购发票对应的应付子账 |
| `treasury_payment_records` | 人工登记的供应商资金付款事实 |
| `treasury_bank_accounts` | 内部银行账户及当前余额 |
| Payment Allocation | UNKNOWN / 未发现 |
| Bank Reconciliation | UNKNOWN / 未发现 |
| AP Clearing History | UNKNOWN / 未发现 |

### 5.2 关键关联

| From | To | 关系 |
|------|----|------|
| Purchase Invoice | Purchase | `purchase_id` |
| AP Record | Purchase Invoice | `invoice_id` |
| Payment Record | Supplier | `supplier_id` |
| Payment Record | Bank Account | `bank_account_id` |
| Payment Record | AP Record | 无关联 |
| Payment Record | Purchase Invoice | 无关联 |

### 5.3 金额口径

| Field / metric | 含义 |
|----------------|------|
| Invoice `amount` | 采购发票总额 |
| Invoice `paid_amount` | 发票累计已付字段；付款流程不更新 |
| Invoice `balance_amount` | 发票剩余字段；付款流程不更新 |
| AP `amount` | 应付原始金额 |
| AP `paid_amount` | 应付累计已付；付款流程不更新 |
| AP `balance_amount` | 应付余额；付款流程不更新 |
| Payment `amount` | 本次人工登记付款金额 |
| Bank `balance` | 登记付款后直接扣减的内部账户余额 |

付款总额与 AP 已付总额可以长期不一致，二者在 Legacy 中代表不同且未联结的事实。

---

## 6. 状态词汇

| Status | 使用位置 | 含义 |
|--------|----------|------|
| `Unpaid` | 新采购发票、新 AP | 尚未支付 |
| `Partial` | 页面兼容/预期状态 | 部分支付；活动付款路径未推进 |
| `Paid` | 页面兼容/预期状态 | 已结清；活动付款路径未推进 |
| `Open` | 部分应付/通用台账词汇 | 尚未关闭 |
| `Closed` | 通用结清词汇 | 已关闭 |

`treasury_payment_records` 未观察到 Submitted/Approved/Executed/Cleared/Reversed 等业务状态。记录存在只证明系统内完成登记并扣减内部银行余额，不证明外部执行或 AP 已清算。

---

## 7. 只读来源路径

| Path | Why cited |
|------|-----------|
| `apps/finance/services.py` | 采购发票、AP 创建、Dashboard 汇总、供应商付款和银行扣账 |
| `apps/finance/repository.py` | Finance 数据访问和缺失的 AP clearing 更新 |
| `apps/finance/router.py` | AP/Treasury 路由与权限门槛 |
| `apps/finance/validator.py` | 金额非负校验仅为 move-only scaffold |
| `runtime/v14/legacy_support.py` | purchase_invoices、ap_records、付款和银行账户字段 |
| `templates/ap_dashboard.html` | AP 来源约束、余额汇总与付款入口 |
| `templates/payment_records.html` | 人工付款字段与列表语义 |
| `templates/payment_record_360.html` | Payment360 不展示 AP/发票分配 |
| `templates/purchase_invoices.html` | 采购发票金额、余额和状态展示 |
| `docs/reports/Business_Strong_A020_AP_Ops_Report.md` | AP 人工付款和无静默支付边界 |
| `business_modules/finance.md` | 设计说明与运行事实的差异 |
| `MODULE_BOUNDARY_REPORT.md` | 缺少统一 posting/reconciliation service 的边界风险 |
| `apps/finance/` / `runtime/v14/legacy_support.py` / AP 与付款模板 | 清算、核销、冲销 UNKNOWN 的检索范围 |

**Root:** `H:\Workspace\EZAM_CRM - 9.0\` + paths above.
