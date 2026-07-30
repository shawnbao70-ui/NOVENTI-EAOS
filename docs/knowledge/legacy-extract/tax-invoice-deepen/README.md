# Legacy Knowledge Extract — Tax Invoice Deepen

**Source:** `H:\Workspace\EZAM_CRM - 9.0`（只读）  
**Verified:** 2026-07-23

## Purpose

本包均衡深挖 Legacy「税务发票 / 销售发票」语义碎片，回答四个硬问题：

1. 是否存在可入账的税务发票实体、表与路由；
2. NDE/打印发票与 DO Post AR / `ar_records` 是否同一对象；
3. 单据税额是否真正计算，以及与 `locale-commerce/tax` 的边界；
4. 作废、红冲、贷项是否存在活动路径。

结论摘要：Legacy **没有**可核销销售税务发票主账；DO「Invoice」是 AR 计提；NDE Invoice 是打印呈现；税设置与税记录是字典/台账碎片；Credit Note 仅有模板映射、无入账/冲销命令。

## Contents

| File | Focus |
|---|---|
| [INDEX.md](INDEX.md) | 主题、稳定 ID、交叉引用索引 |
| [tax_invoice_entity.md](tax_invoice_entity.md) | 税务发票实体 / 表 / 路由有无 |
| [nde_vs_ar_invoice.md](nde_vs_ar_invoice.md) | NDE 打印发票 vs DO Post AR / `ar_records` |
| [tax_calc_on_docs.md](tax_calc_on_docs.md) | 单据税额计算与 locale-commerce/tax 边界 |
| [invoice_void_credit.md](invoice_void_credit.md) | 作废 / 红冲 / 贷项路径有无 |

## Authority boundary

- Finance 发票总览：[`../finance/invoices.md`](../finance/invoices.md)
- Finance AR/收款：[`../finance/receipts_ar.md`](../finance/receipts_ar.md)
- DO Post AR：[`../ship-complete-deepen/do_invoice_ar.md`](../ship-complete-deepen/do_invoice_ar.md)
- 税务字典/台账：[`../locale-commerce/tax.md`](../locale-commerce/tax.md)
- 打印导出：[`../document-ops/print_export.md`](../document-ops/print_export.md)

本包只深化税务发票缺口与对象边界，不改写邻包正文，不开业务模块，不拷源码。

## Evidence roots (read-only)

`apps/finance/` · `apps/inventory/` · `document/` · `templates/` · `core/capabilities/tax/` · `runtime/v14/legacy_support.py` · `business_modules/finance.md` · `docs/reports/` · `locales/`
