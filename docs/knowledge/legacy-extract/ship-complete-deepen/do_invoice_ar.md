# Delivery Order → Type A Invoice / AR

**Evidence strength:** Strong for `ar_records` creation; strong negative for tax-invoice identity  
**Finance cross-reference:** [`../finance/invoices.md`](../finance/invoices.md)、[`../finance/receipts_ar.md`](../finance/receipts_ar.md)

## Scope 与关键结论

DO 详情上的 “Invoice / Post AR” 是 Type A 人工确认页。Approve 后调用 Finance `_legacy_create_ar(do_id)`，以 DO 客户、DO 号和 DO 头总额建立一条全额 `Unpaid` 应收。它不建立正式销售发票主表，不生成税额/票号，也不等于 NDE Invoice 文档。DO 未 Ship 和已有同 source_no AR 都只警告，服务端仍允许再次计提。

本页只深化 DO 交界；Finance 对发票、AR 与收款的整体语义以现有 finance 正文为准，不复制其大段结论。

## 业务规则

| ID | 规则 |
|---|---|
| DIA-R01 | GET Invoice 页要求 AR view 或 Delivery Orders view 任一权限。 |
| DIA-R02 | POST 要求 AR add 或 Delivery Orders edit 任一权限。 |
| DIA-R03 | DO 不存在时确认页 404，Finance 创建返回 DO Not Found。 |
| DIA-R04 | Type A Approve 必须提交 `human_confirm=1`。 |
| DIA-R05 | Cancel 返回 DO 详情；Draft 停留确认页；其他非 approve 不入账。 |
| DIA-R06 | Approve 调用 Finance service，而不是 Inventory 自己直接组装 SQL。 |
| DIA-R07 | AR 客户 id/name来自 DO 与 customer join。 |
| DIA-R08 | `source_no` 写 DO 业务号，不是稳定 DO id 外键。 |
| DIA-R09 | `ar_date` 使用数据库 `date('now')`。 |
| DIA-R10 | `amount` 和初始 `balance` 都取 DO `total_amount`。 |
| DIA-R11 | 新 AR 状态固定为 `Unpaid`。 |
| DIA-R12 | 同 DO 已有 AR 只在页面警告数量，Approve 不阻断重复插入。 |
| DIA-R13 | DO 仍 open/Pending 只提示“可按业务需要计提”，不构成发运前置门。 |
| DIA-R14 | Invoice 页 `can_approve=True`，不依赖 DO stage 或是否有行。 |
| DIA-R15 | Post AR 不写独立 `ar_no`，后续打印可能退化使用来源号。 |
| DIA-R16 | Post AR 不创建税务发票、NDE 商业发票或 sales invoice 主账。 |
| DIA-R17 | 收款仍以 SO 为主对象，未观察到该 AR 与 receipt 的直接核销键。 |
| DIA-R18 | Reopen/Complete 不自动创建、撤销或重算该 AR。 |
| DIA-R19 | Legacy 存在两种 AR 口径：`ar_records` 台账中心与“SO 总额减 receipts”的客户/看板余额；Post AR 不自动统一两者。 |
| DIA-R20 | 未观察到活动服务更新 `ar_records.balance/status` 为 Paid/Closed，DO Post AR 只负责 INSERT。 |

## 流程

1. 用户从 DO 打开 Type A Invoice / Post AR。
2. 页面读取 DO、客户、SO、行、金额和已有来源 AR 数量。
3. 未 Ship 或已有 AR 时显示 warning，但仍可 Approve。
4. 人工确认后 Inventory service 调用 Finance `_legacy_create_ar`。
5. Finance 以 DO 头数据插入全额 Unpaid `ar_records` 并 commit。
6. 跳转 AR Dashboard；收款继续走 SO Receipt 体系。

## 对象边界

| 名称 | Legacy 实际含义 |
|---|---|
| DO Type A Invoice | Post AR 人工确认动作 |
| `ar_records` | 应收计提主记录 |
| NDE Invoice | 可打印商业文档，不自动入账 |
| tax invoice | 此流程明确不是 |
| `purchase_invoices` | 采购发票，与 DO 无关 |
| receipts | SO 维度实收记录 |

## 校验

| ID | 校验 | 强度 |
|---|---|---|
| DIA-V01 | GET 权限：AR view 或 DO view | Hard |
| DIA-V02 | POST 权限：AR add 或 DO edit | Hard |
| DIA-V03 | DO 必须存在 | Hard |
| DIA-V04 | Approve 必须 `human_confirm=1` | Hard |
| DIA-V05 | action 必须为 approve 才写 AR | Hard |
| DIA-V06 | 同 DO 只能存在一条 AR | Warning only / missing |
| DIA-V07 | DO 必须已 Ship/Complete | Warning only / missing |
| DIA-V08 | DO 必须至少有一条有效行 | Missing |
| DIA-V09 | 金额必须大于零 | Missing |
| DIA-V10 | customer 必须存在且一致 | Weak；LEFT JOIN 快照 |
| DIA-V11 | `ar_no` 必填且唯一 | Missing |
| DIA-V12 | 税率、税额、币种和汇率完整 | Missing |
| DIA-V13 | AR 与 receipt 必须可直接核销 | Missing |
| DIA-V14 | 重开/取消必须触发 AR reversal | Missing |

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| `ar_records.customer_id` | DO 关联客户 id |
| `customer_name` | AR 创建时的客户名称快照 |
| `source_no` | DO 号字符串来源 |
| `ar_date` | 数据库当前日期 |
| `amount` | DO 头总额 |
| `balance` | 初始未收余额，等于 amount |
| `status='Unpaid'` | 新计提未收状态 |
| `ar_no` | 独立应收编号；当前 DO 路径未写 |
| `delivery_orders.total_amount` | AR 金额权威来源，不按行重算 |
| `ar_count` / `ar_already` | 按 source_no 统计的重复警告 |
| `human_confirm` | 人工同意 Post AR 的提交标志 |
| `honesty_ar_not_tax` | 页面语义标记：不是税务发票 |
| DO stage | 只影响 warning，不影响 Approve |
| `receipts.so_id` | 收款仍与 SO 关联的事实 |
| `/ar_dashboard` | 成功后的跳转与应收查看入口 |
| SO−Receipts AR 口径 | 由订单和收款派生的另一余额视图，不等于 `ar_records` 台账 |

## 与 Finance 的责任边界

- 发票对象碎片与税务边界：[`../finance/invoices.md`](../finance/invoices.md)
- 收款、AR 与核销缺口：[`../finance/receipts_ar.md`](../finance/receipts_ar.md)
- 本页只确认 DO 触发、字段映射、软门和生命周期脱钩，不把 Post AR 描述成成熟销售发票。

## 证据表

| # | 观察事实 | 强度 | 只读来源 |
|---|---|---|---|
| DIA-E01 | Invoice GET/POST 权限与 Type A 路由 | 强 | `apps/inventory/router.py` |
| DIA-E02 | 人工确认和 action 分支 | 强 | `apps/inventory/services.py::apply_do_invoice` |
| DIA-E03 | 重复 AR 与未 Ship 只生成 warning | 强 | `build_do_invoice_context` |
| DIA-E04 | 页面明确 AR accrual、非税务发票 | 强 | `templates/do_invoice.html` |
| DIA-E05 | Finance 插入七个 AR 字段 | 强 | `apps/finance/services.py::_legacy_create_ar` |
| DIA-E06 | source_no 重复统计 | 强 | `apps/inventory/services.py::_count_ar_for_do` |
| DIA-E07 | Finance AR 汇总读取 Unpaid/balance | 强 | `apps/finance/repository.py`、`services.py` |
| DIA-E08 | Legacy `/create_ar` 已重定向 Type A | 强 | `apps/finance/router.py` |
| DIA-E09 | Type A 报告确认 Post AR 非 tax invoice | 强佐证 | `docs/reports/V18_SO_DO_Invoice_TypeA_Report.md` |
| DIA-E10 | Finance/Inventory 迁移边界 | 中 | `docs/reports/V151E_Volume010_Finance_Inventory_Business_Chain_Extraction_Report.md` |
| DIA-E11 | AR 看板与 records 中心使用不同来源 | 强 | `apps/finance/services.py`、`repository.py` |

## UNKNOWN + 已查路径

1. **同一 DO 重复 AR 是否有数据库唯一约束 UNKNOWN。** 已查：`ar_records` DDL、Inventory duplicate count、Finance insert、升级脚本。
2. **DO 应在 Ship、Complete、签收还是开票时确认 AR UNKNOWN。** 已查：Inventory/Finance services、business modules、Type A/Delivery reports。
3. **`ar_no` 应如何生成及与 DO 号关系 UNKNOWN。** 已查：Finance AR services/repository、打印、runtime DDL。
4. **币种、汇率、税额和舍入如何进入 DO AR UNKNOWN。** 已查：DO/SO schema、Finance Invoice/NDE、templates、reports。
5. **AR 与 SO receipt 的正式核销关系 UNKNOWN。** 已查：Finance receipt service/repository、ar_records、receipts、finance 知识正文。
6. **Reopen/取消/退货后的 AR 冲销与 Credit Note UNKNOWN。** 已查：Inventory reopen、Finance、document credit note、fulfillment reversal。
7. **客户缺失或 DO 总额为零/负数时是否允许计提 UNKNOWN。** 已查：`_legacy_create_ar`、DO create/line logic、validators。
8. **`ar_records` 如何变为 Paid/Closed、余额如何随收款减少 UNKNOWN。** 已查：`apps/finance/**`、`apps/inventory/**` 的 `UPDATE ar_records` 与 receipt 路径；未见活动联动。

## 交叉引用

- Finance 发票边界：[`../finance/invoices.md`](../finance/invoices.md)
- Finance 收款/AR：[`../finance/receipts_ar.md`](../finance/receipts_ar.md)
- Reopen 不冲销：[`do_reopen.md`](do_reopen.md)
- DO 基线：[`../delivery/delivery_order.md`](../delivery/delivery_order.md)
