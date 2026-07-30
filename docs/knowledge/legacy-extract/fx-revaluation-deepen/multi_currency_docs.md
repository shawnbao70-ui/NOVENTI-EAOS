# 多币种单据字段与传播

## Scope 与结论

本页描述交易单据上 `currency` / `exchange_rate` 的落点与链路传播。可确认：**报价头**与**采购单头**经升级列持有币种/汇率；**资金账户**持有币种；**收款**列可存币种但活动路径硬编码 `"USD"`；**销售订单转换**不写入币种/汇率；**AR/AP/付款/转账**无交易汇率快照。行级异币种未建模。展示层（NDE/打印）可输出报价上的汇率，不等于下游会计传播。

交叉引用：[`../locale-commerce/currency.md`](../locale-commerce/currency.md)、[`../finance/receipts_ar.md`](../finance/receipts_ar.md)。

## 业务规则（稳定 ID）

1. **MCD-R01** `quotes` 经升级持有 `currency`（默认 USD）与 `exchange_rate`（默认 1）。
2. **MCD-R02** 服务层新建报价通过 Zero Duplicate 默认链写入商业头币种/汇率；部分页面路径仍可硬插 USD。
3. **MCD-R03** 复制报价继承源单 `currency`/`exchange_rate`，不按当日字典重取价。
4. **MCD-R04** 报价行 `price/cost/amount` 无独立币种列，隐含继承头币种。
5. **MCD-R05** `convert_so` 仅写 SO 号、客户、销售、日期、总额、状态与收款状态，**不**复制报价币种/汇率。
6. **MCD-R06** `sales_orders` 升级列含收款金额/状态/佣金，**未见** `currency`/`exchange_rate` 升级。
7. **MCD-R07** `purchases` 升级持有 `currency`/`exchange_rate`；采购发票与 AP 创建路径不携带这些字段。
8. **MCD-R08** `purchase_invoices` / `ap_records` / `ar_records` DDL 无币种或汇率列。
9. **MCD-R09** `receipts` 升级可有 `currency`；活动收款插入写死 `"USD"`，不读 SO/报价币种。
10. **MCD-R10** 银行/现金账户创建时保存 `currency`；期初余额直接成为当前余额。
11. **MCD-R11** `treasury_payment_records` / `treasury_transfer_records` 无 `currency`/`exchange_rate` 列。
12. **MCD-R12** 银行转账以单一 `amount` 同额加减两端账户余额，不校验两端币种一致。
13. **MCD-R13** 资金列表 KPI 对各账户 `current_balance` 直接相加，不做折算。
14. **MCD-R14** 报价模板可按 `currency` 筛选；模板币种是选择维度，不是交易金额事实。
15. **MCD-R15** NDE/打印组件可渲染 `doc_info.currency` 与 `exchange_rate`（来自文档上下文，通常为报价）。
16. **MCD-R16** `product_price_rules` 结构可存国家/币种/汇率，但未见活动匹配引擎驱动单据。
17. **MCD-R17** 国家 profile 提供默认币种建议；不自动改写已存单据币种。
18. **MCD-R18** 历史客户价建议不做币种归一，跨币种比较可能失真。

## 校验（强 / 弱 / 缺失）

1. **MCD-V01（弱）** 部分报价模板/表单要求 `currency` Form 必填。
2. **MCD-V02（弱）** 汇率以 float 接收；类型级而非商业级。
3. **MCD-V03（强缺口）** SO 必须继承报价币种——未实现。
4. **MCD-V04（强缺口）** 收款币种必须等于 SO/报价币种——未实现（硬编码 USD）。
5. **MCD-V05（缺失）** 付款账户币种与 AP/发票币种一致。
6. **MCD-V06（缺失）** 转账两端币种一致或强制 FX 明细。
7. **MCD-V07（缺失）** 行级异币种禁止或显式换算。
8. **MCD-V08（缺失）** 单据金额小数位按币种规则。
9. **MCD-V09（缺失）** 停用币种禁止新单。
10. **MCD-V10（缺失）** 本位币金额与原币金额双记并勾稽。
11. **MCD-V11（缺失）** KPI 跨币种合计前必须折算或分组。
12. **MCD-V12（弱）** EOC 展示跳过非正汇率行（仅展示层）。

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| `quotes.currency` | 报价名义币种 |
| `quotes.exchange_rate` | 报价商业头汇率快照/默认值；未见生成本位币金额列 |
| `quote_items.price/amount` | 隐含报价头币种 |
| `sales_orders.total_amount` | 订单金额；币种只能经 `quote_id` 间接追溯（若仍关联） |
| `purchases.currency` / `exchange_rate` | 采购头升级字段；下游发票/AP 未证实消费 |
| `receipts.currency` | 可存储；活动路径常写 USD |
| `treasury_*_accounts.currency` | 账户余额名义币种 |
| `treasury_*_accounts.current_balance` | 账户币金额；不可直接跨币种相加 |
| `treasury_payment_records.amount` | 资金流出，无币种快照 |
| `treasury_transfer_records.amount` | 同额调拨，无 FX 明细 |
| `ar_records.amount` / `ap_records.amount` | 台账金额，无币种维度 |
| `quote_templates.currency` | 模板筛选维度 |
| NDE `doc_info.exchange_rate` | 文档展示用汇率 |
| 国家 profile `currency` | 地区建议，非单据事实 |
| formatter 输出 | 展示字符串，非换算结果 |

## 证据表

| ID | 证据 | 强度 | 只读来源路径 |
|---|---|---|---|
| MCD-E01 | quotes 升级 `currency`/`exchange_rate` | 强 | `runtime/v14/legacy_support.py` |
| MCD-E02 | purchases 升级同名字段 | 强 | 同上 `upgrade_purchases` |
| MCD-E03 | sales_orders 升级无币种列 | 强 | 同上 `upgrade_sales` |
| MCD-E04 | `convert_so` INSERT 列清单无 FX | 强 | `apps/quotation/quote_pages.py` |
| MCD-E05 | 报价创建/复制写商业头 | 强 | `apps/quotation/services.py`、`repository.py` |
| MCD-E06 | 收款 INSERT 硬编码 USD | 强 | `apps/finance/receipt_ar_expense_pages.py` |
| MCD-E07 | 银行/现金账户保存币种 | 强 | `apps/finance/treasury_pages.py`、`services.py` |
| MCD-E08 | 转账同额无币种校验 | 强 | `apps/finance/services.py` `_legacy_add_transfer_record` |
| MCD-E09 | 账户余额直接合计 | 强 | `apps/finance/treasury_pages.py` |
| MCD-E10 | AR/AP/Invoice DDL 无币种 | 强 | `runtime/v14/legacy_support.py` |
| MCD-E11 | NDE/打印展示汇率 | 中 | `templates/documents/components/doc_info.html` 等 |
| MCD-E12 | Zero Duplicate 报告确认报价写 FX | 中 | `docs/reports/V18_P6_Zero_Duplicate_Gate_Report.md` |

## UNKNOWN + 已查路径

1. **采购头 `currency`/`exchange_rate` 是否有活动写入 UI UNKNOWN。** 已查：`apps/procurement/`、`apps/supplier/`、purchase 相关 templates 字段名检索。
2. **历史库是否手工给 `sales_orders` 加过币种列 UNKNOWN。** 已查：`upgrade_sales`、apps/sales；未读生产库。
3. **报价转 SO 后业务是否以备注记录币种 UNKNOWN。** 已查：convert_so、SO 模板、销售服务。
4. **DO / 销售发票路径是否另有币种传播 UNKNOWN。** 已查：`delivery_orders` DDL、finance invoice 路径、inventory DO→AR 交界叙述。
5. **收款硬编码 USD 是否被后续编辑覆盖 UNKNOWN。** 已查：receipts UPDATE、receipt 表单币种字段。
6. **多维 `product_price_rules` 是否曾在插件中匹配 UNKNOWN。** 已查：product/finance 服务、business_modules。
7. **打印汇率与报价头不一致时以谁为准 UNKNOWN。** 已查：NDE 组件、document specs。

## 只读来源路径

`apps/quotation/` · `apps/finance/` · `runtime/v14/legacy_support.py` · `v15/ux/master_defaults.py` · `templates/`（quotes、bank/cash、documents、pricing） · `core/i18n/country_localization.py` · `docs/reports/` · 邻包 locale-commerce/finance
