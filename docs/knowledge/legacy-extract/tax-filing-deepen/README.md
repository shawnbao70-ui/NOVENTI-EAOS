# Legacy Knowledge Extract — Tax Filing Deepen

**Source:** `H:\Workspace\EZAM_CRM - 9.0`（只读）  
**Writable home:** `docs/knowledge/legacy-extract/tax-filing-deepen/**`  
**Verified:** 2026-07-23

## Purpose

本包在 [`../tax-invoice-deepen/`](../tax-invoice-deepen/)、[`../locale-commerce/tax.md`](../locale-commerce/tax.md)、[`../return-reversal-policy-deepen/`](../return-reversal-policy-deepen/) 之上均衡深挖四类报税交界缺口：

1. 单据税基 / 税率字段与计算入口（深化不算税结论，不重写字典权威）；
2. 报税 / 申报期间 / 税号联动有无；
3. AR 计提 vs 打印 vs 税票主账分离矩阵；
4. Credit Note 是否入账 / 冲 AR。

**硬结论（证据驱动）：** Legacy 有税率字典、税务台账列表、品牌税号展示槽与 NDE Tax/VAT 打印槽；**没有**单据税基×税率计算链、申报期间实体、税号驱动选税、销售税票主账、Credit Note 入账或冲 AR。DO「Invoice」= Post AR；NDE Invoice = 打印呈现。

## Contents

| File | Focus |
|---|---|
| [INDEX.md](INDEX.md) | 主题索引与阅读顺序 |
| [tax_base_rate_on_docs.md](tax_base_rate_on_docs.md) | 单据税基/税率字段与计算入口 |
| [filing_linkage.md](filing_linkage.md) | 报税/申报期间/税号联动 |
| [ar_print_separation.md](ar_print_separation.md) | AR 计提 vs 打印 vs 税票主账 |
| [credit_note_accounting.md](credit_note_accounting.md) | Credit Note 入账/冲 AR |

## Authority boundary

- Tax invoice 权威：[`../tax-invoice-deepen/`](../tax-invoice-deepen/)（实体有无、NDE vs AR、单据算税边界、void/credit 缺席）
- 税务字典/台账权威：[`../locale-commerce/tax.md`](../locale-commerce/tax.md)
- 退货/红冲权威：[`../return-reversal-policy-deepen/ar_credit_cancel.md`](../return-reversal-policy-deepen/ar_credit_cancel.md)
- Finance / DO→AR：[`../finance/`](../finance/)、[`../ship-complete-deepen/do_invoice_ar.md`](../ship-complete-deepen/do_invoice_ar.md)

本包只深化报税交界与三轨分离，**不改写邻包正文**，不开业务 CRUD，不拷源码。

## Required search loci（已查）

`apps/finance/` · `invoice`/`tax` 关键词 · `document/nde_engine.py` · `document/country_templates.py` · `templates/`（含 `tax_center.html`、print blocks、`credit_note.html`）· `core/capabilities/tax/` · `business_modules/finance.md` · `docs/reports/`（含 V18 Type A、NDE Invoice 升级报告）· `runtime/v14/legacy_support.py` · `apps/quotation/` · `apps/inventory/` · `apps/brand_center/`
