# Tax Invoice Deepen — Index

## 文档导航

| 文档 | 主题 | 稳定 ID 前缀 | 证据强度 |
|---|---|---|---|
| [`tax_invoice_entity.md`](tax_invoice_entity.md) | 税务发票实体/表/路由有无 | `TIE-*` | 强（缺席 + phantom） |
| [`nde_vs_ar_invoice.md`](nde_vs_ar_invoice.md) | NDE 打印 vs DO Post AR | `NVA-*` | 强（双轨分离） |
| [`tax_calc_on_docs.md`](tax_calc_on_docs.md) | 单据税额与 tax 边界 | `TCD-*` | 强缺口 |
| [`invoice_void_credit.md`](invoice_void_credit.md) | 作废/红冲/贷项有无 | `IVC-*` | 强缺口 |

## Reading order

1. [tax_invoice_entity.md](tax_invoice_entity.md) — 先确认没有销售税票主账
2. [nde_vs_ar_invoice.md](nde_vs_ar_invoice.md) — 再拆打印与 AR
3. [tax_calc_on_docs.md](tax_calc_on_docs.md) — 再看税额是否计算
4. [invoice_void_credit.md](invoice_void_credit.md) — 最后看冲销/贷项

## 邻包交叉引用（只读）

| 权威主题 | 文档 |
|---|---|
| 发票对象碎片 | [`../finance/invoices.md`](../finance/invoices.md) |
| AR / Receipt | [`../finance/receipts_ar.md`](../finance/receipts_ar.md)、[`../finance/ar_receipt_reconciliation.md`](../finance/ar_receipt_reconciliation.md) |
| DO Post AR | [`../ship-complete-deepen/do_invoice_ar.md`](../ship-complete-deepen/do_invoice_ar.md) |
| Tax 字典/台账 | [`../locale-commerce/tax.md`](../locale-commerce/tax.md) |
| 打印/NDE | [`../document-ops/print_export.md`](../document-ops/print_export.md) |
| 采购发票（非销售税票） | [`../ap-settlement-deepen/invoice_po_gr_match.md`](../ap-settlement-deepen/invoice_po_gr_match.md) |

## 核心结论

1. DDL 有 `purchase_invoices`、`ar_records`、`tax_records`、`tax_settings`；**无** `invoices` / `invoice_items` CREATE TABLE。
2. Finance repository 声明 `primary_table = "invoices"` 与 `business_modules/finance.md` 目标路由属 phantom / 规划风险。
3. `/delivery_order/{id}/invoice` 诚实文案声明：过账 AR，不是税务/NDE 商业发票。
4. NDE `invoice`/`ar` 打印从 `ar_records`（或 fallback `quotes`）组装 HTML，不写税票主账。
5. 报价/订单/采购/开票活动路径未见按 `tax_settings` 计算税额。
6. Credit/Debit Note 仅有模板映射；无冲销写路径、无 void 状态机、无红冲实体。

## Shared vocabulary

- **Tax invoice（税务发票）**：法定/可申报销项票据；Legacy 无活动销售税票主账。
- **Commercial invoice（商业发票）**：NDE/打印对外文件；不等于入账。
- **Post AR / Type A Invoice**：DO 人工确认后 INSERT `ar_records`。
- **Purchase invoice**：`purchase_invoices` + AP，采购侧，不是销售税票。
- **Void / Credit / 红冲**：冲销或贷项；检索范围内无活动财务写路径。

## 主要只读证据根

`apps/finance/` · `apps/inventory/` · `document/nde_engine.py` · `document/country_templates.py` · `templates/do_invoice.html` · `templates/print/` · `templates/documents/credit_note.html` · `core/capabilities/tax/` · `runtime/v14/legacy_support.py` · `business_modules/finance.md` · `docs/reports/V18_SO_DO_Invoice_TypeA_Report.md` · `docs/reports/NDE_INVOICE_DO_UPGRADE_REPORT.md` · `locales/`
