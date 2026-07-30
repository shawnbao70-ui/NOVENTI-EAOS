# AR 计提 vs 打印 vs 税票主账分离矩阵

## Scope 与结论

交叉引用：[`../tax-invoice-deepen/nde_vs_ar_invoice.md`](../tax-invoice-deepen/nde_vs_ar_invoice.md)、[`../tax-invoice-deepen/tax_invoice_entity.md`](../tax-invoice-deepen/tax_invoice_entity.md)、[`../ship-complete-deepen/do_invoice_ar.md`](../ship-complete-deepen/do_invoice_ar.md)、[`../document-ops/print_export.md`](../document-ops/print_export.md)。本页把「Invoice」一词拆成三轨并给出可迁移的分离矩阵。

**结论：** Legacy「Invoice」至少分裂为三条互不等价的轨：

1. **AR 计提（Post AR / Type A）** —— `/delivery_order/{id}/invoice` 人工确认后 INSERT `ar_records`；  
2. **商业打印（NDE Invoice）** —— 从 `ar_records`（或 fallback `quotes`）组装 HTML；layouts/printing only；  
3. **销售税票主账** —— **不存在**（`invoices` DDL/活动 CRUD 缺席；honesty 文案明确 AR ≠ tax invoice）。

打印成功不入账；入账成功不等于税票；税票主账缺失时「已开票」无法合法成立。

## 业务规则（稳定 ID）

1. **APS-R01** V18 报告诚实定义：Post AR 表面 wraps `_legacy_create_ar` —— **AR accrual — not tax invoice**。  
2. **APS-R02** Inventory `build_do_invoice_context` 设置 `honesty_ar_not_tax=True`，摘要声明不是 tax / NDE commercial invoice。  
3. **APS-R03** Approve 且 `human_confirm=1` 才调用 Finance `_legacy_create_ar`；否则不入账。  
4. **APS-R04** `_legacy_create_ar` 只写 `ar_records`（customer、source_no=DO、amount=balance=DO total、status=Unpaid）；不写销售税票表。  
5. **APS-R05** 同 DO 已有 AR 仅 warning；`can_approve` 仍为 true —— 重复计提风险，非税票重开。  
6. **APS-R06** NDE 升级报告声明：business logic / schema / routes **unchanged**；仅 layouts/printing。  
7. **APS-R07** NDE 模块别名 `invoice`/`ar` 优先按 `ar_records.id` 取数组装打印上下文。  
8. **APS-R08** AR 路径打印时行项目可为空；金额进 financial；VAT 槽默认 0。  
9. **APS-R09** AR 不存在时可 fallback `quotes` 并派生 `INV-{quote_no}` —— 仍是文档号，不是税票入账。  
10. **APS-R10** `business_modules/finance.md` / repository `primary_table="invoices"` 属规划/phantom 风险，不是第三轨实现。  
11. **APS-R11** 采购发票 `purchase_invoices` 是采购侧实体，**不得**当作销售税票主账。  
12. **APS-R12** `tax_records` 是独立税务台账碎片，**不是**销售税票行。  
13. **APS-R13** 打印预览不更新 `ar_records.status`，也不创建 `invoices` 行。  
14. **APS-R14** Post AR 成功跳转 `/ar_dashboard`；收款走 SO `receipts`，不自动勾兑该 AR（双轨，见 finance 邻包）。  
15. **APS-R15** Proforma Invoice 属 NDE invoice family 商业文件类型，不是 AR 或税票。  
16. **APS-R16** Fixed Link / V41 矩阵：Commercial Invoice 是 Document/Print 输出，**不是** Layer B 销售 hub。  
17. **APS-R17** EAOS 迁移时必须保持三轨分离命名；禁止用单一「Invoice」模块吞并三者。  

## 三轨分离矩阵

| 维度 | A. Post AR 计提 | B. NDE 打印 Invoice | C. 销售税票主账 |
|---|---|---|---|
| 入口 | `/delivery_order/{id}/invoice` | `/print_preview/...` module invoice/ar | **无活动 CRUD** |
| 写库 | INSERT `ar_records` | 通常不写业务主账 | 无 `invoices` DDL |
| 人类确认 | Type A `human_confirm` | 预览/浏览器打印 | — |
| 金额来源 | DO `total_amount` | AR.amount 或 Quote.total | — |
| 税基/税率 | 无 | 展示槽空/0 | — |
| 法定票号 | 无 | 展示号可变（ar_no/source_no/INV-*） | — |
| 诚实语义 | `honesty_ar_not_tax` | commercial print | 规格 phantom |
| 与收款 | 不自动核销 | 可显示 payment 块 | — |
| 报税可用性 | 不可直接申报 | 不可直接申报 | 实体缺失 |

```
DO ──Approve──► ar_records (A: accrual)
                 │
                 └──print_preview──► NDE HTML (B: commercial print)
                 
C: sales tax invoice ledger ── ✕ missing
purchase_invoices / tax_records ── adjacent ≠ C
```

## 流程

### A. Post AR

1. 打开 DO Type A Invoice。  
2. 装载 DO/客户/行/金额/已有 AR 数与 honesty。  
3. Approve + human_confirm → `_legacy_create_ar`。  
4. 跳转 AR Dashboard。  

### B. NDE 打印

1. 请求 invoice/ar 打印预览。  
2. 按 AR id 取数；否则尝试 quote。  
3. `build_nde_context` / invoice builder 组装编号、客户、financial。  
4. 渲染模板；浏览器打印。  
5. 不写税票主账、不改 AR 状态。  

### C. 税票主账（缺失）

规格列出 `/invoices`、`/add_invoice`、`invoice_items`；活动检索未见 DDL 与页面落地。

## 校验（强 / 弱 / 缺失）

1. **APS-V01（强）** Post AR GET/POST 权限门（AR view/add 或 DO view/edit，见邻包）。  
2. **APS-V02（强）** Approve 必须 `human_confirm=1`。  
3. **APS-V03（强）** DO 必须存在。  
4. **APS-V04（强/文案）** honesty 区分 AR vs 税票/NDE。  
5. **APS-V05（缺失）** 同 DO 唯一 AR —— 仅 warning。  
6. **APS-V06（缺失）** 打印前必须已 Post AR —— 可 fallback quote。  
7. **APS-V07（缺失）** 打印金额含税拆分正确 —— VAT 可为 0。  
8. **APS-V08（缺失）** 打印操作回写「已开票」税票状态 —— 无实体。  
9. **APS-V09（缺失）** 税票号法定唯一 / 税控回执 —— 无。  
10. **APS-V10（弱）** 打印编号退化到 source_no 可能导致对外号与应收号混淆。  
11. **APS-V11（强缺席）** `CREATE TABLE invoices` 必须存在 —— 失败。  
12. **APS-V12（弱/架构）** NDE 升级「printing only」约束防止把打印当入账。  

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| `/delivery_order/{id}/invoice` | Post AR 确认面，不是税票命令 |
| `honesty_ar_not_tax` | 服务端上下文标记 |
| `ar_records` | 应收计提主账（A 轨） |
| `ar_records.source_no` | DO 业务号 |
| `ar_records.ar_no` | 打印优先编号；DO 路径常空 |
| NDE module `invoice`/`ar` | 打印解析别名（B 轨） |
| `INV-{quote_no}` | Quote fallback 派生展示号 |
| `nde.financial.vat` | 可选展示槽 |
| `invoices`（声明） | phantom / 规划表名（C 轨缺失） |
| `purchase_invoices` | 采购发票；非销售税票 |
| `tax_records` | 独立税务台账；非税票主账 |
| Proforma Invoice | 形式发票文档类型 |
| Fixed Link G-11 | Invoice 非 Layer B hub |
| V18 Type A report | 官方诚实语义来源 |

## 证据表

| ID | 证据 | 强度 | 只读来源路径 |
|---|---|---|---|
| APS-E01 | V18 Type A：AR accrual not tax invoice | 强 | `docs/reports/V18_SO_DO_Invoice_TypeA_Report.md` |
| APS-E02 | honesty_ar_not_tax + 摘要文案 | 强 | `apps/inventory/services.py`（`build_do_invoice_context`） |
| APS-E03 | `_legacy_create_ar` 仅 INSERT ar_records | 强 | `apps/finance/services.py` |
| APS-E04 | NDE printing-only 升级声明 | 强 | `docs/reports/NDE_INVOICE_DO_UPGRADE_REPORT.md` |
| APS-E05 | NDE tax/vat 槽与 invoice family | 强 | `document/nde_engine.py` |
| APS-E06 | invoices phantom / 规格风险 | 强 | `apps/finance/repository.py`、`business_modules/finance.md`、[`../tax-invoice-deepen/tax_invoice_entity.md`](../tax-invoice-deepen/tax_invoice_entity.md) |
| APS-E07 | V41 Print/Document：Invoice 非 hub | 中 | `docs/reports/V41_Print_Report_Document_Matrix.md` |
| APS-E08 | create_ar 重定向到 Type A | 强 | `apps/finance/router.py` |
| APS-E09 | 邻包 NDE vs AR 双轨叙述 | 强 | [`../tax-invoice-deepen/nde_vs_ar_invoice.md`](../tax-invoice-deepen/nde_vs_ar_invoice.md) |

## UNKNOWN + 已查路径

1. **运营是否用外部税控系统开票后手工改 AR 备注 UNKNOWN。** 已查：apps/finance、inventory Type A、NDE；未读运营 SOP。  
2. **receivables 旁路表是否曾承载发票号语义 UNKNOWN。** 已查：runtime DDL receivables；活动 DO Post AR 写 ar_records。  
3. **某租户是否定制 print 后写第三方票号到 remark UNKNOWN。** 已查：标准 NDE builder；未见票号回写。  
4. **Proforma 是否被客户误当作税票 UNKNOWN（流程风险）。** 已查：NDE family/layout；产品诚实边界已标明 commercial。  
5. **未来是否计划把 C 轨落成独立 tax invoice 模块 UNKNOWN。** 已查：business_modules/finance Future Scope、tax-invoice-deepen；本包不自开模块。  
6. **AR Dashboard「Invoice」列标签是否加剧命名混淆 UNKNOWN。** 已查：Type A/honesty 文案；未审计全部 UI 标签。  

## 只读来源路径

`apps/inventory/services.py` · `apps/finance/services.py` · `apps/finance/router.py` · `apps/finance/repository.py` · `document/nde_engine.py` · `business_modules/finance.md` · `docs/reports/V18_SO_DO_Invoice_TypeA_Report.md` · `docs/reports/NDE_INVOICE_DO_UPGRADE_REPORT.md` · `docs/reports/V41_Print_Report_Document_Matrix.md` · `docs/knowledge/legacy-extract/tax-invoice-deepen/` · `docs/knowledge/legacy-extract/ship-complete-deepen/do_invoice_ar.md`
