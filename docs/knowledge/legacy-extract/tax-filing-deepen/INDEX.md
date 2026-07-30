# Tax Filing Deepen — Index

## 文档导航

| 文档 | 主题 | 稳定 ID 前缀 | 证据强度 |
|---|---|---|---|
| [`tax_base_rate_on_docs.md`](tax_base_rate_on_docs.md) | 单据税基/税率字段与计算入口 | `TBR-*` | 强缺口（相对算税） |
| [`filing_linkage.md`](filing_linkage.md) | 报税/申报期间/税号联动 | `FLK-*` | 强缺口（缺席） |
| [`ar_print_separation.md`](ar_print_separation.md) | AR vs 打印 vs 税票主账 | `APS-*` | 强（三轨分离） |
| [`credit_note_accounting.md`](credit_note_accounting.md) | Credit Note 入账/冲 AR | `CNA-*` | 强缺口（模板≠入账） |

## Reading order

1. [tax_base_rate_on_docs.md](tax_base_rate_on_docs.md) — 先确认单据无税基/税率计算入口  
2. [filing_linkage.md](filing_linkage.md) — 再确认无申报期/税号联动  
3. [ar_print_separation.md](ar_print_separation.md) — 再拆 AR / 打印 / 税票三轨  
4. [credit_note_accounting.md](credit_note_accounting.md) — 最后确认贷项不入账、不冲 AR  

## 邻包交叉引用（只读）

| 权威主题 | 文档 |
|---|---|
| 税务字典/台账 | [`../locale-commerce/tax.md`](../locale-commerce/tax.md) |
| 税票实体 / 算税边界 | [`../tax-invoice-deepen/tax_invoice_entity.md`](../tax-invoice-deepen/tax_invoice_entity.md)、[`../tax-invoice-deepen/tax_calc_on_docs.md`](../tax-invoice-deepen/tax_calc_on_docs.md) |
| NDE vs AR | [`../tax-invoice-deepen/nde_vs_ar_invoice.md`](../tax-invoice-deepen/nde_vs_ar_invoice.md) |
| Void / Credit 模板 | [`../tax-invoice-deepen/invoice_void_credit.md`](../tax-invoice-deepen/invoice_void_credit.md) |
| AR 红冲/贷项缺席 | [`../return-reversal-policy-deepen/ar_credit_cancel.md`](../return-reversal-policy-deepen/ar_credit_cancel.md) |
| DO Post AR | [`../ship-complete-deepen/do_invoice_ar.md`](../ship-complete-deepen/do_invoice_ar.md) |

## 核心结论

1. `tax_settings.tax_rate` 是字典百分比；活动 Quote/SO/DO/PO/PINV/AR 路径**不**读取该表计算税额。  
2. 单据层无统一 `tax_base` / `tax_amount` / `tax_inclusive` 持久化语义；NDE 仅有 `line.tax` / `financial.vat` 展示槽（默认空/0）。  
3. `/tax_center` + `tax_records` **不是**申报引擎；无 filing period、无税号→税码匹配、无进销项汇总。  
4. **三轨分离：** Post AR（`ar_records`）≠ NDE 打印 Invoice ≠ 销售税票主账（后者不存在）。  
5. Credit Note / Debit Note 仅有模板映射；**无**负向 AR、无冲余额、无税票红冲写路径。  

## Shared vocabulary

- **Tax base（税基）：** 应税金额基础；Legacy 活动单据未建模为可计算字段。  
- **Tax rate（税率）：** `tax_settings.tax_rate` 字典值；非交易快照。  
- **Filing / 申报：** 向税务机关汇总申报的期间与义务；Legacy 无活动实体。  
- **Tax ID / 税号：** 品牌 `brand_profiles.tax_number` 与 NDE `customer.tax_number` 展示槽；非申报主体绑定引擎。  
- **Post AR：** DO Type A Invoice 人工确认后 INSERT `ar_records`。  
- **Commercial print invoice：** NDE 组装的对外 HTML；不等于入账或税票。  
- **Credit Note accounting：** 贷项入账并冲减应收；本包结论为缺失。  

## 主要只读证据根

`apps/finance/` · `apps/inventory/services.py` · `apps/quotation/services.py` · `apps/brand_center/` · `document/nde_engine.py` · `document/country_templates.py` · `templates/tax_center.html` · `templates/print/blocks/` · `templates/documents/credit_note.html` · `core/capabilities/tax/` · `runtime/v14/legacy_support.py` · `business_modules/finance.md` · `docs/reports/V18_SO_DO_Invoice_TypeA_Report.md` · `docs/reports/NDE_INVOICE_DO_UPGRADE_REPORT.md`
