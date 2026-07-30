# FX Propagation Deepen — Index

| Topic | Primary page | Evidence strength | Key conclusion |
|---|---|---|---|
| Quote FX snapshot exists | [convert_fx_fields.md](convert_fx_fields.md) | 强 | `quotes` 升级持 `currency`/`exchange_rate` |
| Quote→SO FX write | [convert_fx_fields.md](convert_fx_fields.md) | 强缺口 | `convert_so` INSERT 无币种/汇率列 |
| SO schema FX columns | [convert_fx_fields.md](convert_fx_fields.md) | 强缺口 | `upgrade_sales` 无 FX 列；基表无币种 |
| SO→DO FX write | [convert_fx_fields.md](convert_fx_fields.md) | 强缺口 | `convert_do` 无币种/汇率 |
| Receipt currency path | [receipt_payment_fx.md](receipt_payment_fx.md) | 强 | 列可存；活动 INSERT 写死 `"USD"` |
| Payment / transfer FX | [receipt_payment_fx.md](receipt_payment_fx.md) | 强缺口 | 无 `currency`/`exchange_rate` 列与写入 |
| Account currency use | [receipt_payment_fx.md](receipt_payment_fx.md) | 混合 | 账户有币种；KPI/收付不折算 |
| Period revaluation | [period_revaluation_close.md](period_revaluation_close.md) | 强缺口 | 全库无 revaluation/period-close 作业 |
| Fiscal close entity | [period_revaluation_close.md](period_revaluation_close.md) | 强缺口 | 仅有佣金 `commission_periods`，非会计关账 |
| Realized FX entity | [realized_unrealized_fx.md](realized_unrealized_fx.md) | 强缺口 | 清账无汇差、无损益实体 |
| Unrealized FX entity | [realized_unrealized_fx.md](realized_unrealized_fx.md) | 强缺口 | 无敞口重估与未实现损益表 |

## Reading order

1. [convert_fx_fields.md](convert_fx_fields.md)
2. [receipt_payment_fx.md](receipt_payment_fx.md)
3. [period_revaluation_close.md](period_revaluation_close.md)
4. [realized_unrealized_fx.md](realized_unrealized_fx.md)

## Cross-references（只读邻包）

| Neighbor | Use |
|---|---|
| [`../locale-commerce/currency.md`](../locale-commerce/currency.md) | 币种/汇率基线权威 |
| [`../finance/README.md`](../finance/README.md) | Finance 包入口 |
| [`../finance/ar_receipt_reconciliation.md`](../finance/ar_receipt_reconciliation.md) | AR/收款勾兑缺口 |
| [`../finance/ap_payment_clearing.md`](../finance/ap_payment_clearing.md) | AP 清账缺口 |
| [`../fx-revaluation-deepen/multi_currency_docs.md`](../fx-revaluation-deepen/multi_currency_docs.md) | 多币种单据字段总览 |
| [`../fx-revaluation-deepen/revaluation_job.md`](../fx-revaluation-deepen/revaluation_job.md) | 重估作业缺口总览 |
| [`../fx-revaluation-deepen/clearing_cross_currency.md`](../fx-revaluation-deepen/clearing_cross_currency.md) | 跨币清账/汇差缺口 |
| [`../fx-revaluation-deepen/fx_rate_source.md`](../fx-revaluation-deepen/fx_rate_source.md) | 汇率来源/维护缺口 |

## Shared vocabulary

- **FX propagation：** 币种/汇率快照沿 Quote→SO→DO→Receipt/Payment 的写入与消费。
- **Document FX snapshot：** 单据头冻结的 `currency`/`exchange_rate`；不等于活字典汇率。
- **Hardcoded receipt currency：** 活动收款 INSERT 写死 `"USD"`，覆盖潜在上游币种意图。
- **Period close：** 会计期间关闭；Legacy 财务域未观察到对应实体。
- **Realized / unrealized FX：** 清账时确认的已实现汇差 vs 期末重估未实现汇差；二者均未建模。
