# NDE / 打印发票 vs DO Post AR / ar_records

## Scope 与结论

交叉引用：[`../finance/invoices.md`](../finance/invoices.md)、[`../ship-complete-deepen/do_invoice_ar.md`](../ship-complete-deepen/do_invoice_ar.md)、[`../document-ops/print_export.md`](../document-ops/print_export.md)。

**结论：** 「Invoice」在 Legacy 至少分裂为两条互不等价的轨：

1. **DO Type A Invoice / Post AR** —— 人工确认后 INSERT `ar_records`（应收计提）；
2. **NDE Invoice 打印** —— 从 `ar_records`（或 fallback `quotes`）组装商业发票 HTML，供浏览器打印。

两者共享「Invoice」称呼与部分编号展示，但 **打印不等于入账，入账不等于税票**。NDE 升级报告明确：业务逻辑、schema、routes unchanged。

## 业务规则（稳定 ID）

1. **NVA-R01** GET/POST `/delivery_order/{do_id}/invoice` 是 V18 Type A Human Approved 面，诚实语义为 Post AR。
2. **NVA-R02** 旧别名 `GET /create_ar/{do_id}` 303 重定向到上述 Type A 确认页，禁止静默插入理解。
3. **NVA-R03** Approve 且 `human_confirm=1` 时，Inventory 调用 Finance `_legacy_create_ar(do_id)`。
4. **NVA-R04** `_legacy_create_ar` 只 INSERT `ar_records`：customer、source_no=DO 号、amount=balance=DO `total_amount`、status=`Unpaid`；不写 `ar_no`。
5. **NVA-R05** 页面 `honesty_ar_not_tax=True`；locale：`not a tax invoice or NDE commercial invoice`。
6. **NVA-R06** 同 DO 已有 AR 仅 warning；Approve 不阻断重复计提。
7. **NVA-R07** DO 未 Ship（open stage）仅 warning；不构成 Post AR 硬门。
8. **NVA-R08** NDE 打印模块别名 `invoice` / `invoices` / `ar` 优先按 `ar_records.id` 取数。
9. **NVA-R09** 打印编号优先 `ar_no`，空则退化 `source_no`（DO 号）。
10. **NVA-R10** AR 路径打印时 `items=[]`，行表明细为空；金额进 `subtotal`/`grand_total`。
11. **NVA-R11** 若 AR 不存在，NDE 可 fallback 读 `quotes`，并派生展示号 `INV-{quote_no}` —— 仍是文档号，不是税票入账。
12. **NVA-R12** NDE Invoice layout 启用 financial/payment/workflow/ai_trace；DO layout 禁用 financial/payment。
13. **NVA-R13** NDE 行 `tax` 字段在 quote/delivery line builder 中固定填空字符串 `""`，不从税率引擎计算。
14. **NVA-R14** financial.`vat` 默认 `extra.get("vat", 0)`；AR builder 未传入增值税计算结果时为 0，模板 `{% if nde.financial.vat %}` 不显示。
15. **NVA-R15** NDE 升级「layouts/printing only」——不改业务逻辑、DDL、路由。
16. **NVA-R16** 打印预览成功不更新 `ar_records` 状态，也不创建销售发票主账。
17. **NVA-R17** Post AR 成功跳转 `/ar_dashboard`；收款仍走 SO `receipts`，不自动勾兑该 AR。
18. **NVA-R18** Proforma Invoice 属于 NDE invoice family 的商业文件类型，不是 AR 或税票。

## 双轨对照

| 维度 | DO Post AR | NDE Invoice 打印 |
|---|---|---|
| 入口 | `/delivery_order/{id}/invoice` | `/print_preview/...` 模块 `invoice`/`ar` 等 |
| 写库 | INSERT `ar_records` | 通常不写业务主账 |
| 人类确认 | Type A `human_confirm` | 预览/浏览器打印 |
| 金额来源 | DO `total_amount` | AR.amount 或 Quote.total |
| 行明细 | 确认页可预览 DO 行；入账不存行 | AR 路径 items 空；Quote fallback 有行 |
| 税务身份 | 明确不是税票 | 商业发票呈现，可显示空 tax/VAT 槽位 |
| 与收款关系 | 不直接核销 | 可显示 payment 块，不驱动收款 |

## 流程

### A. Post AR

1. 用户从 DO 打开 Type A Invoice。
2. 系统装载 DO/客户/行/金额/已有 AR 数。
3. 展示 honesty 与 warning。
4. Approve + human_confirm → `_legacy_create_ar`。
5. 跳转 AR Dashboard。

### B. NDE 打印

1. 用户（或链接）请求 invoice/ar 打印预览。
2. 引擎按 `ar_records.id` 取 AR；否则尝试 quote。
3. `build_nde_invoice_context` 组装编号、客户、financial、payment 等。
4. 渲染 `invoice_document` / documents invoice 模板。
5. 浏览器打印；服务端无 PDF 权威资产（见 document-ops）。

## 校验（强 / 弱 / 缺失）

1. **NVA-V01（强）** GET 需 AR view 或 DO view。
2. **NVA-V02（强）** POST 需 AR add 或 DO edit。
3. **NVA-V03（强）** DO 必须存在。
4. **NVA-V04（强）** Approve 必须 `human_confirm=1`。
5. **NVA-V05（弱/文案）** honesty 文案区分 AR vs 税票/NDE。
6. **NVA-V06（缺失）** 同 DO 唯一 AR —— 仅 warning。
7. **NVA-V07（缺失）** DO 必须已 Ship —— 仅 warning。
8. **NVA-V08（缺失）** 打印前必须已 Post AR —— NDE 可 fallback quote。
9. **NVA-V09（缺失）** 打印金额必须等于 AR 且含税拆分正确 —— VAT 槽位可为 0。
10. **NVA-V10（缺失）** 打印操作闭环回写发票状态/审计为「已开票」—— 未见。
11. **NVA-V11（弱）** 打印编号退化到 source_no 可能导致对外号与应收号混淆。
12. **NVA-V12（缺失）** NDE Invoice 与税控开票回执对账 —— 无实体。

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| `/delivery_order/{id}/invoice` | Post AR 确认面，不是税票命令 |
| `honesty_ar_not_tax` | 服务端上下文标记 |
| `v18_do_invoice_honesty` | 多语言诚实文案键 |
| `ar_records.source_no` | DO 业务号来源 |
| `ar_records.amount` / `balance` | 全额未收初始值 |
| `ar_records.status='Unpaid'` | 新计提状态 |
| `ar_no` | 打印优先编号；DO 路径常空 |
| NDE module `invoice`/`ar` | 打印解析别名 |
| `INV-{quote_no}` | Quote fallback 派生展示号 |
| `nde.financial.vat` | 可选展示槽；默认 0 |
| `line.tax` | 行税展示槽；builder 填空 |
| `layout_profile: invoice` | 启用价税金融块的打印配置 |
| `line_mode: priced` | Invoice 表显示价格列 |
| `back_url: /receivables` | AR 打印返回提示 |
| DO `total_amount` | Post AR 金额权威 |
| Proforma Invoice | 形式发票文档类型 |

## 证据表

| ID | 证据 | 强度 | 只读来源路径 |
|---|---|---|---|
| NVA-E01 | DO Invoice GET/POST 与权限 | 强 | `apps/inventory/router.py` |
| NVA-E02 | build/apply_do_invoice + honesty | 强 | `apps/inventory/services.py` |
| NVA-E03 | `_legacy_create_ar` INSERT 字段 | 强 | `apps/finance/services.py` |
| NVA-E04 | create_ar → Type A redirect | 强 | `apps/finance/router.py` |
| NVA-E05 | 确认页 honesty UI | 强 | `templates/do_invoice.html` |
| NVA-E06 | locale honesty 三语 | 强 | `locales/en.json`、`zh_CN.json`、`zh_TW.json` |
| NVA-E07 | NDE invoice/ar 取 AR + quote fallback | 强 | `document/nde_engine.py` |
| NVA-E08 | NDE 升级范围：打印 only | 强 | `docs/reports/NDE_INVOICE_DO_UPGRADE_REPORT.md` |
| NVA-E09 | V18「not tax invoice」 | 强 | `docs/reports/V18_SO_DO_Invoice_TypeA_Report.md` |
| NVA-E10 | financial VAT 条件展示 | 中 | `templates/print/blocks/07_financial.html` |
| NVA-E11 | product table Tax 列 | 中 | `templates/print/blocks/06_product_table.html` |
| NVA-E12 | 打印权威与无服务端 PDF | 中 | [`../document-ops/print_export.md`](../document-ops/print_export.md) |

## UNKNOWN + 已查路径

1. **是否存在未挂载的私有打印入口把 NDE Invoice 与 Post AR 绑成事务 UNKNOWN。** 已查：`document/nde_engine.py`、`apps/inventory/**`、`apps/finance/**`、`docs/reports/NDE_*`、`RENDER_FLOW_REPORT.md`。
2. **运营是否把打印 PDF 存档当作税票正本 UNKNOWN。** 已查：document-ops 打印链、NDE 报告；无服务端 PDF 资产链。
3. **AR 打印 UI 主入口是否与 Quote/DO 同级 UNKNOWN。** 已查：NDE 报告 module 表、document-ops（注明 Invoice/AR 引擎有、UI 入口未同等证明）。
4. **`INV-{quote}` fallback 是否被业务当作正式发票号使用 UNKNOWN。** 已查：nde_engine fallback 分支、finance invoices 知识、reports。
5. **country `cn_fapiao_style` 是否改变入账语义 UNKNOWN。** 已查：`document/country_templates.py`（architecture stubs）、nde_engine apply profile；未见写库。
6. **重复 Post AR 后打印选哪条 AR UNKNOWN。** 已查：打印按 `ar_records.id`；重复策略仅确认页 warning。
7. **payment QR/银行信息是否来自客户税籍还是品牌档案 UNKNOWN。** 已查：nde_engine payment 块取 brand 字段。

## 只读来源路径

`apps/inventory/` · `apps/finance/` · `document/nde_engine.py` · `templates/do_invoice.html` · `templates/print/` · `templates/print/invoice_document.html` · `locales/` · `docs/reports/V18_SO_DO_Invoice_TypeA_Report.md` · `docs/reports/NDE_INVOICE_DO_UPGRADE_REPORT.md` · `docs/knowledge/legacy-extract/document-ops/print_export.md` · `docs/knowledge/legacy-extract/ship-complete-deepen/do_invoice_ar.md`
