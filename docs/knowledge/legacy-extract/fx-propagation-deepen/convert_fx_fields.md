# Quote→SO 币种/汇率是否写入

## Scope 与结论

本页回答：报价头上的 `currency` / `exchange_rate` 在 `convert_so`（及后续 SO→DO）是否被写入下游。交叉引用 [`../fx-revaluation-deepen/multi_currency_docs.md`](../fx-revaluation-deepen/multi_currency_docs.md)（MCD-R05/R06）与 [`../locale-commerce/currency.md`](../locale-commerce/currency.md)。

**可确认硬结论：** `quotes` 经升级持有币种/汇率；`convert_so` 虽 `SELECT *` 读到整行报价（含 FX 字段），但 `INSERT INTO sales_orders` 列清单仅含 so_no / quote_id / customer / salesperson / date / total / status / payment_status——**不复制币种或汇率**。`upgrade_sales` 亦不为 SO 增加 FX 列。行项目只复制 qty/price/amount。`convert_do` 同样无币种/汇率。佣金 `tc_ledger` 用 SO 原币金额口径计算，无 FX 维度。

## 业务规则（稳定 ID）

1. **CFX-R01** `quotes` 升级列含 `currency TEXT DEFAULT 'USD'` 与 `exchange_rate REAL DEFAULT 1`。
2. **CFX-R02** 新建报价经 Zero Duplicate / master_defaults 可写入商业头币种与汇率快照。
3. **CFX-R03** 复制报价继承源单 `currency`/`exchange_rate`，不按当日字典重取价。
4. **CFX-R04** 报价行 `quote_items` 无独立币种列；金额隐含头币种。
5. **CFX-R05** `GET /convert_so/{quote_id}` 以 `SELECT * FROM quotes` 加载源单，故运行时可见 `currency`/`exchange_rate`。
6. **CFX-R06** 同一路径 `INSERT INTO sales_orders` **不包含** `currency` 或 `exchange_rate` 列与绑定值——传播在此断裂。
7. **CFX-R07** `sales_orders` 基表 DDL 无币种/汇率；`upgrade_sales` 仅加收款金额/状态/佣金等，**不加** FX 列。
8. **CFX-R08** SO 行 `sales_order_items` 自 `quote_items` 复制 product/qty/price/amount，无币种列。
9. **CFX-R09** 转换后更新报价 `status='已确认'`，不回写或校验汇率一致性。
10. **CFX-R10** 若同 `quote_id` 已存在 SO，路径直接重定向，不二次传播 FX。
11. **CFX-R11** 转换时按 SO `total_amount` 与职级费率写 `tc_ledger`；金额无币种标签、无折算。
12. **CFX-R12** `apps/sales/` 服务层对 `currency`/`exchange_rate` 关键字检索无活动命中。
13. **CFX-R13** `convert_do` INSERT 列为 do_no/so_id/customer/date/total/status，无 FX。
14. **CFX-R14** `delivery_orders` / `delivery_order_items` DDL 无币种/汇率列。
15. **CFX-R15** 打印/NDE 可展示报价上下文的 `doc_info.currency`/`exchange_rate`，不等于 SO 已落库快照。
16. **CFX-R16** Approve Type A 可读报价币种用于展示条，**不**改写 `convert_so` 列清单（服务注释：additive；does not rewrite convert_so）。
17. **CFX-R17** 因此：Quote→SO FX 传播在 Legacy 为**强缺口**；下游只能经 `quote_id` 间接追溯（若关联仍在）。
18. **CFX-R18** EAOS 不得将“报价有汇率”迁移解释为“订单/交货已继承汇率”。

## 校验（强 / 弱 / 缺失）

1. **CFX-V01（弱）** 部分报价表单要求 `currency` Form 必填。
2. **CFX-V02（弱）** 报价 `exchange_rate` 以 float 接收（类型级）。
3. **CFX-V03（强缺口）** SO 必须继承报价 `currency`——未实现。
4. **CFX-V04（强缺口）** SO 必须继承报价 `exchange_rate`——未实现。
5. **CFX-V05（缺失）** SO 本位币金额 = 原币 × 快照汇率并落库。
6. **CFX-V06（缺失）** 转换时禁止报价汇率 ≤ 0。
7. **CFX-V07（缺失）** DO 必须继承 SO/报价币种。
8. **CFX-V08（缺失）** 行级金额币种与头币种一致（行无币种列可校）。
9. **CFX-V09（缺失）** 佣金计算前按本位币归一。
10. **CFX-V10（弱/展示）** 打印可显示报价汇率，不构成 SO 校验。
11. **CFX-V11（缺失）** 报价币种变更后已转 SO 的一致性告警。
12. **CFX-V12（缺失）** 转换权限与 FX 字段审计（谁在何时冻结汇率）。

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| `quotes.currency` | 报价名义币种快照 |
| `quotes.exchange_rate` | 报价商业头汇率快照/默认；未见生成本位币金额列 |
| `quote_items.price/amount` | 隐含报价头币种的行金额 |
| `sales_orders.quote_id` | 追溯报价的唯一结构化桥梁（非 FX 副本） |
| `sales_orders.total_amount` | 订单金额；**无**伴随币种/汇率列 |
| `sales_orders.received_amount` / `balance_amount` | 收款进度字段；无币种 |
| `sales_order_items.price/amount` | 自报价行复制的数量金额；无币种 |
| `delivery_orders.total_amount` | DO 金额；无币种/汇率 |
| `tc_ledger.sales_amount` | 佣金基数；无 FX 维度 |
| NDE `doc_info.exchange_rate` | 文档展示用，通常来自报价上下文 |
| master_defaults 币种链 | 新建报价默认解析，不作用于 convert |
| Approve strip `currency` | 审批展示，不写入 SO |
| `currency_settings.exchange_rate` | 字典种子值；convert 路径不读取 |
| SO 上缺失的 `currency`/`exchange_rate` | **未建模**（升级路径亦未补） |

## 证据表

| ID | 证据 | 强度 | 只读来源路径 |
|---|---|---|---|
| CFX-E01 | quotes 升级加 `currency`/`exchange_rate` | 强 | `runtime/v14/legacy_support.py`（约 L24592–24606） |
| CFX-E02 | `convert_so` INSERT 列无 FX | 强 | `apps/quotation/quote_pages.py`（`INSERT INTO sales_orders`） |
| CFX-E03 | convert 前 `SELECT *` 可读 FX 但不使用 | 强 | 同上 `convert_so` |
| CFX-E04 | `upgrade_sales` 无币种/汇率列 | 强 | `runtime/v14/legacy_support.py` `upgrade_sales` |
| CFX-E05 | SO 基表 DDL 无 FX | 强 | 同上 `CREATE TABLE sales_orders` |
| CFX-E06 | SO 行复制无币种 | 强 | `quote_pages.py` → `sales_order_items` |
| CFX-E07 | `convert_do` INSERT 无 FX | 强 | `apps/inventory/services.py` `_legacy_convert_do` |
| CFX-E08 | DO DDL 无币种 | 强 | `legacy_support.py` `delivery_orders` |
| CFX-E09 | sales 应用无 currency 关键字命中 | 强 | `apps/sales/**/*.py` 检索 |
| CFX-E10 | Zero Duplicate 报告确认报价写 FX、非 SO | 中 | `docs/reports/V18_P6_Zero_Duplicate_Gate_Report.md` |
| CFX-E11 | Approve 不改写 convert_so | 中 | `apps/quotation/services.py` 注释/Approve 路径 |
| CFX-E12 | 邻包已标 Quote→SO 传播缺口 | 强 | [`../fx-revaluation-deepen/multi_currency_docs.md`](../fx-revaluation-deepen/multi_currency_docs.md) |

## UNKNOWN + 已查路径

1. **历史生产库是否手工 ALTER 给 `sales_orders` 加过币种列 UNKNOWN。** 已查：`upgrade_sales`、`CREATE TABLE sales_orders`、`apps/sales/`；未读生产 SQLite 文件。
2. **业务是否用备注/附件记录订单币种 UNKNOWN。** 已查：`convert_so` 字段清单、SO 模板币种控件、销售服务。
3. **直接创建 SO（非 convert）路径是否另写 FX UNKNOWN。** 已查：`apps/sales/repository.py` INSERT 列、sales 服务 currency 检索（无命中）。
4. **报价转 SO 后若改报价汇率，展示是否仍以报价为准 UNKNOWN。** 已查：NDE/print 组件、convert 后无同步作业。
5. **多公司/品牌默认币种是否曾计划写入 SO UNKNOWN。** 已查：`v15/ux/master_defaults.py`、organization 模板 currency、docs/reports Zero Duplicate。
6. **佣金结算是否线下按本位币重算 UNKNOWN。** 已查：`tc_ledger` INSERT、`commission_periods`、sales 残余路由。
7. **插件/外部系统是否消费 `quote_id` 补全 FX UNKNOWN。** 已查：`business_modules/`、`core/capabilities/currency/`（仅 health/bridge）。

## 只读来源路径

`apps/quotation/quote_pages.py` · `apps/quotation/services.py` · `apps/quotation/repository.py` · `apps/sales/` · `apps/inventory/services.py` · `runtime/v14/legacy_support.py` · `templates/print/` · `docs/reports/V18_P6_Zero_Duplicate_Gate_Report.md` · `v15/ux/master_defaults.py` · 邻包 locale-commerce / fx-revaluation-deepen（只读）
