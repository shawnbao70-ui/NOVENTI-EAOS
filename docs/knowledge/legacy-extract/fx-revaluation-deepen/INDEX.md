# FX / Revaluation Deepen — Index

| Topic | Primary page | Evidence strength | Key conclusion |
|---|---|---|---|
| Rate dictionary seed | [fx_rate_source.md](fx_rate_source.md) | 强 | `currency_settings` 有种子汇率，无生效日列 |
| Rate maintenance | [fx_rate_source.md](fx_rate_source.md) | 强缺口 | 未见 UPDATE/维护路由；仅 seed INSERT OR IGNORE |
| Capability scaffold | [fx_rate_source.md](fx_rate_source.md) | 强 | `core/capabilities/currency` 仅 health/bridge |
| Quote FX snapshot | [multi_currency_docs.md](multi_currency_docs.md) | 强 | 报价头持 `currency`/`exchange_rate` |
| Quote→SO propagation | [multi_currency_docs.md](multi_currency_docs.md) | 强缺口 | `convert_so` 不写入 SO 币种/汇率 |
| Receipt/treasury FX | [multi_currency_docs.md](multi_currency_docs.md) | 混合 | 账户有币种；收款硬编码 USD；付款/转账无汇率 |
| Revaluation job | [revaluation_job.md](revaluation_job.md) | 强缺口 | 全库无 revaluation/unrealized/period-close 作业 |
| Cross-currency clearing | [clearing_cross_currency.md](clearing_cross_currency.md) | 强缺口 | 无币种一致性校验、无汇差、无 GL 联动 |

## Reading order

1. [fx_rate_source.md](fx_rate_source.md)
2. [multi_currency_docs.md](multi_currency_docs.md)
3. [revaluation_job.md](revaluation_job.md)
4. [clearing_cross_currency.md](clearing_cross_currency.md)

## Cross-references（只读邻包）

| Neighbor | Use |
|---|---|
| [`../locale-commerce/currency.md`](../locale-commerce/currency.md) | 币种/汇率基线权威 |
| [`../locale-commerce/README.md`](../locale-commerce/README.md) | Locale Commerce 边界 |
| [`../finance/README.md`](../finance/README.md) | Finance 包入口 |
| [`../finance/ap_payment_clearing.md`](../finance/ap_payment_clearing.md) | AP 清账缺口（含多币种 UNKNOWN） |
| [`../finance/ar_receipt_reconciliation.md`](../finance/ar_receipt_reconciliation.md) | AR/收款勾兑缺口 |
| [`../ap-settlement-deepen/partial_clearing_writeoff.md`](../ap-settlement-deepen/partial_clearing_writeoff.md) | 部分清账/write-off 缺失 |

## Shared vocabulary

- **Rate source：** 汇率数值从何处进入系统（字典种子、人工输入、外部提供方）。
- **Effective date：** 汇率对某日/某期间生效的日期边界；Legacy 未建模。
- **Document FX snapshot：** 单据头上冻结的 `currency`/`exchange_rate`，不等于活汇率。
- **Revaluation：** 按期末汇率重估外币货币性项目并确认未实现汇兑损益；Legacy 未观察到。
- **Cross-currency clearing：** 不同币种债权/债务与资金账户之间的核销及汇差处理；Legacy 未观察到。
