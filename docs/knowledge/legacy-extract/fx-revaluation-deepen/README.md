# Legacy Knowledge Extract — FX / Revaluation Deepen

**Source:** `H:\Workspace\EZAM_CRM - 9.0`（只读）  
**Writable home:** `docs/knowledge/legacy-extract/fx-revaluation-deepen/**`  
**Verified:** 2026-07-23

## Purpose

本包在 [`../locale-commerce/currency.md`](../locale-commerce/currency.md) 与 [`../finance/`](../finance/) 之上深挖四类缺口：

- 汇率来源是否可维护、是否有生效日/版本；
- 多币种字段在报价→订单→收付单据上的传播边界；
- 期末重估作业与会计期间关闭是否存在；
- 跨币种清账与汇兑损益是否可执行。

**硬结论（证据驱动）：** Legacy 有币种字典种子、报价/采购头汇率快照、资金账户币种与 EOC 展示用汇率快照；**没有**可观察的汇率维护 UI/API、生效日、重估作业、期间关闭或跨币种清账/汇兑损益闭环。`core/capabilities/currency` 仅为 health/bridge 脚手架。

## Contents

| File | Focus |
|---|---|
| [INDEX.md](INDEX.md) | 主题索引与阅读顺序 |
| [fx_rate_source.md](fx_rate_source.md) | 汇率来源 / 维护 / 生效日 |
| [multi_currency_docs.md](multi_currency_docs.md) | 多币种单据字段与传播 |
| [revaluation_job.md](revaluation_job.md) | 重估作业 / 期间有无 |
| [clearing_cross_currency.md](clearing_cross_currency.md) | 跨币种清账 / 汇兑损益 |

## Authority boundary

- Locale Commerce 权威：[`../locale-commerce/currency.md`](../locale-commerce/currency.md)
- Finance 权威：[`../finance/README.md`](../finance/README.md)、[`../finance/ap_payment_clearing.md`](../finance/ap_payment_clearing.md)、[`../finance/ar_receipt_reconciliation.md`](../finance/ar_receipt_reconciliation.md)
- AP 清算深化：[`../ap-settlement-deepen/`](../ap-settlement-deepen/)

本包只深化 FX/重估/跨币清账断点，不重写邻包正文，不打开业务 CRUD。

## Required search loci（已查）

`apps/finance/` · `core/capabilities/currency/` · `runtime/v14/legacy_support.py` · `v15/ux/master_defaults.py` · `v15/template_services/` · `apps/quotation/` · `templates/` · `business_modules/` · `docs/reports/` · `core/i18n/`
