# 收款/付款/账户币种与汇率使用

## Scope 与结论

本页描述资金侧（收款、付款、转账、银行/现金账户）如何使用币种与汇率。交叉引用 [`../fx-revaluation-deepen/multi_currency_docs.md`](../fx-revaluation-deepen/multi_currency_docs.md)、[`../fx-revaluation-deepen/clearing_cross_currency.md`](../fx-revaluation-deepen/clearing_cross_currency.md)、[`../finance/ar_receipt_reconciliation.md`](../finance/ar_receipt_reconciliation.md)、[`../finance/ap_payment_clearing.md`](../finance/ap_payment_clearing.md)。

**可确认硬结论：** 银行/现金账户创建时保存 `currency`；`receipts` 升级可有 `currency` 列，但活动收款 INSERT **写死 `"USD"`**，不读 SO/报价币种，也不写 `exchange_rate`（收款表升级亦无汇率列）。付款与转账记录 DDL/INSERT **均无** `currency`/`exchange_rate`；付款仅扣减银行余额。账户 KPI 对各账户 `current_balance` 直接相加。价格试算中的手输 `exchange_rate` 只出 USD 展示价，不落库到收付。

## 业务规则（稳定 ID）

1. **RPF-R01** `treasury_bank_accounts` / `treasury_cash_accounts` DDL 含 `currency TEXT`；创建表单默认 `"USD"`。
2. **RPF-R02** 账户 `opening_balance` 直接初始化为 `current_balance`；余额名义币=账户币。
3. **RPF-R03** `upgrade_finance` 为 `receipts` 增加 `currency TEXT`（及 bank_name/reference 等），**不**增加 `exchange_rate`。
4. **RPF-R04** 活动收款路径 `INSERT INTO receipts` 将 `currency` 绑定为字面量 `"USD"`。
5. **RPF-R05** 收款金额取 SO 余额/应收口径推进 `received_amount`/`payment_status`，不携带交易汇率。
6. **RPF-R06** 收款不读取关联报价的 `quotes.currency`/`exchange_rate`（SO 本身亦无 FX 列可继承）。
7. **RPF-R07** `treasury_payment_records` DDL 无 `currency`/`exchange_rate`；INSERT 列为 payment_no/date/supplier/account/amount/method/remark。
8. **RPF-R08** 付款成功后 `UPDATE treasury_bank_accounts SET current_balance = current_balance - amount`，不校验账户币与供应商/AP 币。
9. **RPF-R09** 付款不更新 `ap_records` / `purchase_invoices` 的 paid/balance（清账缺口叠加无 FX）。
10. **RPF-R10** `treasury_transfer_records` 以单一 `amount` 同额加减两端账户，无汇率/汇差字段。
11. **RPF-R11** 转账不比较 from/to 账户 `currency` 是否一致。
12. **RPF-R12** 银行/现金列表 KPI 对各账户余额直接 `+=`，不做折算或按币种分组。
13. **RPF-R13** `ar_records` / `ap_records` DDL 无币种或汇率列；收款/付款无法在台账层表达原币 vs 本位币。
14. **RPF-R14** `/calculate_price` 接收手输 `exchange_rate` 算出 `usd_price` 仅模板展示，不写 receipts/payments/currency_settings。
15. **RPF-R15** 收款模板 KPI（Collected 等）汇总 `amount` 字段，无币种维度过滤。
16. **RPF-R16** 资金账户 360 可展示账户币种 KPI 卡，属展示而非交易快照。
17. **RPF-R17** `core/capabilities/currency` 为 health/bridge 脚手架，收付路径不 `consume("currency")` 做换算。
18. **RPF-R18** 因此：收付链路的币种使用是**账户标签 + 收款硬编码 USD**；交易汇率传播为**强缺口**。

## 校验（强 / 弱 / 缺失）

1. **RPF-V01（强）** 付款/转账要求 Treasury.add 权限（资金门禁，非 FX 校验）。
2. **RPF-V02（弱）** 账户创建 `currency` 表单默认 USD（自由文本，未见字典绑定）。
3. **RPF-V03（强缺口）** 收款币种必须等于 SO/报价币种——未实现（硬编码 USD）。
4. **RPF-V04（缺失）** 收款必须记录交易汇率或清算汇率。
5. **RPF-V05（缺失）** 付款账户币种与 AP/发票币种一致，或强制 FX 路径。
6. **RPF-V06（缺失）** 转账两端币种一致，或双币金额+汇率+汇差。
7. **RPF-V07（缺失）** KPI 跨币种合计前必须折算或分组。
8. **RPF-V08（缺失）** 收款金额按账户币与单据币双记勾稽。
9. **RPF-V09（缺失）** 禁止静默把非 USD 订单收款写成 USD。
10. **RPF-V10（弱）** 价格试算汇率为 Form float；零汇率可致除零（展示层风险）。
11. **RPF-V11（缺失）** 停用币种禁止新账户/新收款。
12. **RPF-V12（缺失）** 收付凭证附件币种与系统字段一致。

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| `treasury_bank_accounts.currency` | 账户名义币种标签 |
| `treasury_cash_accounts.currency` | 现金账户名义币种标签 |
| `treasury_*_accounts.current_balance` | 账户币余额；不可安全跨币相加 |
| `receipts.currency` | 可存储；活动路径常为字面 `"USD"` |
| `receipts.amount` | 收款金额；无配套汇率列 |
| `receipts.exchange_rate` | **未建模**（升级未加） |
| `treasury_payment_records.amount` | 资金流出；无币种/汇率快照 |
| `treasury_transfer_records.amount` | 同额调拨；非兑换单 |
| 付款时账户余额扣减 | 隐含按账户币计量，无显式快照到付款行 |
| SO `received_amount` / `payment_status` | 订单收款进度，非多币核销 |
| `ar_records.amount` / `balance` | 应收台账；无币种 |
| `ap_records.amount` / `paid_amount` / `balance_amount` | 应付台账；付款不更新；无币种 |
| `calculate_price` → `usd_price` | 试算展示；非收付事实 |
| 账户 360 Currency KPI | UI 展示账户标签 |
| formatter / i18n 货币符号 | 展示层，不执行换算 |

## 证据表

| ID | 证据 | 强度 | 只读来源路径 |
|---|---|---|---|
| RPF-E01 | 银行账户 INSERT 含 currency | 强 | `apps/finance/treasury_pages.py` `add_bank_account` |
| RPF-E02 | 现金账户 INSERT 含 currency | 强 | 同上 `add_cash_account` |
| RPF-E03 | 收款 INSERT 硬编码 `"USD"` | 强 | `apps/finance/receipt_ar_expense_pages.py` |
| RPF-E04 | receipts 升级有 currency、无 exchange_rate | 强 | `runtime/v14/legacy_support.py` `upgrade_finance` |
| RPF-E05 | 付款 INSERT 无币种/汇率 | 强 | `treasury_pages.py` / `services.py` `add_payment_record` |
| RPF-E06 | 转账同额无 FX 字段 | 强 | `apps/finance/services.py` `_legacy_add_transfer_record` |
| RPF-E07 | 账户余额直接合计 | 强 | `treasury_pages.py` cash/bank 列表循环 |
| RPF-E08 | payment/transfer DDL 无 FX | 强 | `legacy_support.py` treasury_* 段 |
| RPF-E09 | AR/AP DDL 无币种 | 强 | 同上 `ar_records` / `ap_records` |
| RPF-E10 | 价格试算手输汇率不落库 | 强 | `apps/finance/finance_ops_pages.py` `calculate_price` |
| RPF-E11 | 收款/银行模板无交易汇率控件 | 中 | `templates/receipts.html`、`bank_accounts.html` |
| RPF-E12 | currency capability 非收付引擎 | 强 | `core/capabilities/currency/README.md` |

## UNKNOWN + 已查路径

1. **收款硬编码 USD 是否被后续编辑页覆盖 UNKNOWN。** 已查：`receipt_ar_expense_pages.py` UPDATE、`templates/receipts.html` 币种输入；未见活动改币种路径。
2. **多币种银行账户并存时业务是否只使用单币账户 UNKNOWN。** 已查：账户创建表单、payment 模板；无强制单币策略代码。
3. **付款备注是否曾手写汇差说明 UNKNOWN。** 已查：`remark` 字段语义；无结构化汇差列。
4. **现金账户付款路径是否与银行路径对称写币种 UNKNOWN。** 已查：`treasury_pages` / `services` 付款 INSERT（account_type 常为 BANK）。
5. **外部银行回单币种与 `receipts.currency` 不一致时如何处理 UNKNOWN。** 已查：reference_no/attachment、对账关键字检索。
6. **AR Dashboard 汇总是否隐含全公司 USD UNKNOWN。** 已查：`services.py` `_legacy_ar_dashboard` 金额相加、无币种 GROUP BY。
7. **采购侧是否存在对称的“付款写死某币”路径 UNKNOWN。** 已查：付款 INSERT、AP 创建；付款无 currency 列可写死。

## 只读来源路径

`apps/finance/treasury_pages.py` · `apps/finance/receipt_ar_expense_pages.py` · `apps/finance/services.py` · `apps/finance/finance_ops_pages.py` · `apps/finance/repository.py` · `runtime/v14/legacy_support.py` · `templates/bank_accounts.html` · `templates/receipts.html` · `templates/payment_records.html` · `core/capabilities/currency/` · `business_modules/finance.md` · 邻包 finance / fx-revaluation-deepen（只读）
