# 已实现 / 未实现汇兑损益实体有无

## Scope 与结论

本页回答：Legacy 是否存在**已实现**（realized）与**未实现**（unrealized）汇兑损益的数据实体、过账路径或清账时自动确认。交叉引用 [`../fx-revaluation-deepen/clearing_cross_currency.md`](../fx-revaluation-deepen/clearing_cross_currency.md)、[`../fx-revaluation-deepen/revaluation_job.md`](../fx-revaluation-deepen/revaluation_job.md)、[`../finance/ap_payment_clearing.md`](../finance/ap_payment_clearing.md)、[`../finance/ar_receipt_reconciliation.md`](../finance/ar_receipt_reconciliation.md)。

**可确认硬结论：** 全库对 `realized`/`unrealized`/`fx_gain`/`fx_loss`/`exchange gain`/`汇兑损益` 的活动实现**零命中**。收款硬编码 USD 并推进 SO 已收字段，不计算汇差；付款不核销 AP、无清算汇率；转账同额无兑换损益；AR/AP 无原币/本位币双余额；无重估作业可产生未实现损益。价格试算 USD 价与 EOC 风险分均非损益实体。故已实现/未实现 FX **均未建模（强缺口）**。

## 业务规则（稳定 ID）

1. **RUF-R01** 未观察到 `fx_gain_loss` / `realized_fx` / `unrealized_fx` 表或等价列。
2. **RUF-R02** 收款 INSERT 无汇率、无汇差金额字段；币种写死 USD。
3. **RUF-R03** 收款推进 SO `received_amount`/`payment_status`，不写 AR 核销明细，更无 realized FX。
4. **RUF-R04** 付款记录无币种/汇率/汇差；不更新 AP paid/balance，无法在清账点确认已实现汇差。
5. **RUF-R05** 银行转账单一 `amount` 同额加减，不产生兑换损益行。
6. **RUF-R06** `ar_records` / `ap_records` 无原币余额 vs 本位币余额，无法表达未实现敞口。
7. **RUF-R07** 未见 allocation/clearing 表携带单据汇率、清算汇率与汇差。
8. **RUF-R08** 未见尾差 write-off 区分“舍入”与“汇兑”。
9. **RUF-R09** 未见 journal/GL 分录将汇兑损益过入费用/收益科目。
10. **RUF-R10** 未见费用模块标准单据类型标记为 FX gain/loss。
11. **RUF-R11** 未实现损益依赖期末重估；重估作业本身不存在（见 period_revaluation_close.md）。
12. **RUF-R12** Quote FX 快照未传播至 SO/收付，使“单据汇率 vs 清算汇率”差分在结构上不可计算。
13. **RUF-R13** `calculate_price` 的 USD 换算结果不落库，不能充当已实现汇差凭证。
14. **RUF-R14** NDE credit-note / 文档模板不是会计贷项，不能充当汇差调整凭证。
15. **RUF-R15** AP/AR Dashboard KPI 直接汇总金额，不按币种或汇差分解。
16. **RUF-R16** `tax_records` / expense 路径未见 FX gain/loss 专用类型字段消费。
17. **RUF-R17** 邻包 clearing 页已将跨币清账与 realized FX 标为强缺口；本页独立确认实体层仍为零。
18. **RUF-R18** 因此 EAOS 不得将 Legacy 收付款登记解释为已确认汇兑损益能力。

## 校验（强 / 弱 / 缺失）

1. **RUF-V01（缺失）** 清账时必须存在单据币种与账户/清算币种关系。
2. **RUF-V02（缺失）** 已实现汇差 = f(单据汇率, 清算汇率, 清算原币金额) 并过账。
3. **RUF-V03（缺失）** 部分清账同步更新原币与本位币余额。
4. **RUF-V04（缺失）** 未实现汇差仅由期末重估产生且可冲回。
5. **RUF-V05（缺失）** 禁止在无汇差处理下跨币核销。
6. **RUF-V06（缺失）** GL 借贷平衡含汇兑损益科目。
7. **RUF-V07（缺失）** 汇差 write-off 与普通坏账/尾差分类型。
8. **RUF-V08（强缺口）** 收款币种不得静默覆盖为 USD（否则汇差基线失真）。
9. **RUF-V09（缺失）** 转账跨币必须双币金额 + 汇率 + 损益。
10. **RUF-V10（弱）** UI 可显示账户币种，不构成损益控制。
11. **RUF-V11（缺失）** 已实现/未实现分录的期间归属与关账锁定。
12. **RUF-V12（缺失）** 汇兑损益过账权限与审计轨迹。

## 数据含义

| 数据 / 概念 | Legacy 含义 |
|---|---|
| Realized FX gain/loss | **未建模** |
| Unrealized FX gain/loss | **未建模** |
| `fx_gain_loss` / 等价列 | **未观察到** |
| allocation / clearing history | **未建模**（故无汇差挂载点） |
| `receipts.amount` + `"USD"` | 收款事实；非已实现汇差计算输入完备集 |
| `treasury_payment_records.amount` | 未分配资金流出；无汇差 |
| `treasury_transfer_records.amount` | 同额调拨；非兑换损益 |
| AR/AP `amount`/`balance` | 单金额口径；无原币/本位币双轨 |
| SO `received_amount` | 订单收款进度，非核销汇差 |
| 单据汇率（报价快照） | 停在报价；未进入清账差分 |
| 清算汇率 | **未建模** |
| write-off（汇兑 vs 尾差） | **未建模** |
| journal for FX | **未观察到** |
| 价格试算 `usd_price` | 展示换算，非损益实体 |
| EOC exchange risk | 风险启发式，非未实现损益余额 |

## 证据表

| ID | 证据 | 强度 | 只读来源路径 |
|---|---|---|---|
| RUF-E01 | 全库无 realized/unrealized/fx_gain/汇兑损益实现命中 | 强缺口 | 工作区 py/html/md/sql 定向检索 |
| RUF-E02 | 收款无汇率/汇差列与写入 | 强 | `receipt_ar_expense_pages.py`；`upgrade_finance` |
| RUF-E03 | 付款无币种/汇率/AP 核销 | 强 | `treasury_pages.py` / `services.py` |
| RUF-E04 | 转账无 FX 明细 | 强 | `services.py` `_legacy_add_transfer_record` |
| RUF-E05 | AR/AP DDL 无币种双余额 | 强 | `runtime/v14/legacy_support.py` |
| RUF-E06 | 无 allocation 表挂汇差 | 强 | finance DDL + ap-settlement 邻包结论 |
| RUF-E07 | 重估作业不存在 → 未实现无来源 | 强 | [`period_revaluation_close.md`](period_revaluation_close.md) / 邻包 revaluation_job |
| RUF-E08 | Quote→SO FX 不传播 → 差分不可算 | 强 | [`convert_fx_fields.md`](convert_fx_fields.md) |
| RUF-E09 | 跨币清账邻包标强缺口 | 强 | [`../fx-revaluation-deepen/clearing_cross_currency.md`](../fx-revaluation-deepen/clearing_cross_currency.md) |
| RUF-E10 | AP/AR 勾兑邻包确认无自动核销 | 强 | [`../finance/ap_payment_clearing.md`](../finance/ap_payment_clearing.md)、[`../finance/ar_receipt_reconciliation.md`](../finance/ar_receipt_reconciliation.md) |
| RUF-E11 | 价格试算不落库 | 中 | `finance_ops_pages.py` `calculate_price` |
| RUF-E12 | finance 模块规格无汇兑损益交付物 | 中 | `business_modules/finance.md` |

## UNKNOWN + 已查路径

1. **汇差是否记入费用模块手工单据（自由文本）UNKNOWN。** 已查：expense 路径、tax_records、finance services 关键字 `fx`/`exchange`/`gain`/`loss`。
2. **历史付款/收款备注是否曾手写汇差说明 UNKNOWN。** 已查：remark 字段；无结构化类型。
3. **外部总账是否承接汇兑损益 UNKNOWN。** 已查：business_modules、integration/GTFIP 叙述。
4. **NDE 贷项模板是否曾被业务误当作汇差凭证 UNKNOWN。** 已查：templates/documents、print blocks；无会计过账。
5. **多币种客户是否被流程禁止从而规避汇差 UNKNOWN。** 已查：credit control、convert gates、报价币种校验。
6. **`profit_snapshots` 是否隐含汇兑成分 UNKNOWN。** 已查：DDL 命名与 finance 消费；无 FX 字段证据。
7. **库存/成本模块是否另有外币重估损益 UNKNOWN。** 已查：inventory ledger 类型叙述、finance-inventory 链式报告；无 FX gain/loss 类型。

## 只读来源路径

`apps/finance/`（receipt/treasury/services/ops） · `runtime/v14/legacy_support.py` · `business_modules/finance.md` · `templates/`（receipts、payment、documents） · `docs/reports/` · `core/capabilities/currency/` · 本包 convert/receipt/period 页 · 邻包 fx-revaluation-deepen / finance / locale-commerce（只读）
