# Legacy Knowledge Extract — FX Propagation Deepen

**Source:** `H:\Workspace\EZAM_CRM - 9.0`（只读）  
**Writable home:** `docs/knowledge/legacy-extract/fx-propagation-deepen/**`  
**Verified:** 2026-07-23

## Purpose

本包在 [`../locale-commerce/currency.md`](../locale-commerce/currency.md)、[`../finance/`](../finance/) 与 [`../fx-revaluation-deepen/`](../fx-revaluation-deepen/) 之上，专挖 **FX 沿交易链的传播断点**：

- Quote→SO 转换是否写入币种/汇率；
- 收款/付款/资金账户如何使用（或不使用）币种与汇率；
- 期间重估与期末关账是否存在可观察证据；
- 已实现/未实现汇兑损益实体有无。

**硬结论（证据驱动）：** 报价头持有 `currency`/`exchange_rate` 快照，但 `convert_so` **不**写入 SO；收款活动路径硬编码 `"USD"`；付款/转账无交易汇率；资金账户有币种但不驱动折算；期间重估、关账与已实现/未实现汇兑损益实体均为**强缺口**。邻包 `fx-revaluation-deepen` 的多币种/重估结论在此按传播链加深，不改写邻包正文。

## Contents

| File | Focus |
|---|---|
| [INDEX.md](INDEX.md) | 主题索引与阅读顺序 |
| [convert_fx_fields.md](convert_fx_fields.md) | Quote→SO 币种/汇率是否写入 |
| [receipt_payment_fx.md](receipt_payment_fx.md) | 收款/付款/账户币种与汇率使用 |
| [period_revaluation_close.md](period_revaluation_close.md) | 期间重估/期末关账证据 |
| [realized_unrealized_fx.md](realized_unrealized_fx.md) | 已实现/未实现汇兑损益实体有无 |

## Authority boundary

- Locale Commerce：[`../locale-commerce/currency.md`](../locale-commerce/currency.md)
- Finance：[`../finance/README.md`](../finance/README.md)、[`../finance/ar_receipt_reconciliation.md`](../finance/ar_receipt_reconciliation.md)、[`../finance/ap_payment_clearing.md`](../finance/ap_payment_clearing.md)
- FX/重估邻包（只读）：[`../fx-revaluation-deepen/multi_currency_docs.md`](../fx-revaluation-deepen/multi_currency_docs.md)、[`../fx-revaluation-deepen/revaluation_job.md`](../fx-revaluation-deepen/revaluation_job.md)、[`../fx-revaluation-deepen/clearing_cross_currency.md`](../fx-revaluation-deepen/clearing_cross_currency.md)

本包只深化 FX **传播**断点，不打开业务 CRUD，不改邻包/代码/tip/STATUS。

## Required search loci（已查）

`apps/finance/` · `apps/quotation/`（含 `convert_so`） · `apps/sales/` · `apps/inventory/`（`convert_do`） · `runtime/v14/legacy_support.py`（DDL/upgrade） · `core/capabilities/currency/` · `templates/` · `business_modules/finance.md` · `docs/reports/` · `v15/ux/master_defaults.py` · `v15/template_services/`
