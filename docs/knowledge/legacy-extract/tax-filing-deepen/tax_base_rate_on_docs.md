# 单据税基 / 税率字段与计算入口

## Scope 与结论

交叉引用权威（不重写）：[`../locale-commerce/tax.md`](../locale-commerce/tax.md)、[`../tax-invoice-deepen/tax_calc_on_docs.md`](../tax-invoice-deepen/tax_calc_on_docs.md)。本页深挖「税基字段落在何处、税率如何进入单据、有无计算入口函数/路由」，服务于报税能力边界判断。

**结论：** Legacy **没有**活动单据税基×税率计算入口。`tax_settings` 仅字典种子；Quote 合计是行 `amount` 累加；DO Post AR 复制 DO `total_amount`；采购发票复制 PO 总额；NDE 预留 `line.tax` / `financial.vat` 槽且 builder 填空/0；`core/capabilities/tax` 只有 health/bridge。不得把打印 Tax 列或国家 `tax_fields` stub 解释为已实现算税。

## 业务规则（稳定 ID）

1. **TBR-R01** `tax_settings` 持久化 `tax_code`（UNIQUE）、`tax_name`、`country_code`、`tax_rate`、`status`；种子含 CN/ID/BD/VN VAT/PPN 百分比。  
2. **TBR-R02** 活动路径未见 `SELECT … FROM tax_settings` 参与 Quote/SO/DO/PO/PINV/AR 金额公式。  
3. **TBR-R03** 报价合计 `_compute_quote_totals` 累加行金额与成本得 `total_amount` / `gross_profit`；无乘 `tax_rate` 步骤。  
4. **TBR-R04** DO Post AR（`_legacy_create_ar`）写入 `ar_records.amount = balance = DO.total_amount`；无税基/税额列。  
5. **TBR-R05** `purchase_invoices.invoice_amount` 取 PO 头总额；无 tax 列写入。  
6. **TBR-R06** `ar_records` DDL 字段为 ar_no/customer/source_no/ar_date/amount/balance/status —— **无** tax_base、tax_rate、tax_amount。  
7. **TBR-R07** NDE `build_product_lines_from_quote_items` / `…_delivery_items` 将 `tax` 固定为 `""`。  
8. **TBR-R08** NDE `financial.vat = extra.get("vat", 0)`；AR/多数 builder 不传入计算结果时为 0。  
9. **TBR-R09** 打印块有 Tax 列与条件 VAT 行；空/0 不构成已算税证明。  
10. **TBR-R10** `document/country_templates.py` 的 `tax_fields` / `invoice_layout`（如 `cn_fapiao_style`）是国家版式意图槽，不改写金额公式。  
11. **TBR-R11** Tax capability `BRIDGE = core.i18n.country_localization`；consume health ≠ 交易算税服务。  
12. **TBR-R12** `/add_test_tax` 固定插入 `VAT` + `1500` + `Pending`，不读 `tax_settings`、不绑定单据税基。  
13. **TBR-R13** `tax_records` 无 taxable base、rate 快照、currency、party、source_doc —— 无法从台账反推税基。  
14. **TBR-R14** 含税价 / 未税价 / `tax_inclusive` 在活动单据字段中未形成统一语义（与 locale-commerce/tax 边界一致）。  
15. **TBR-R15** EAOS 不得把「存在税率字典」或「打印有 Tax 列」迁移为「单据引擎已算税」。  
16. **TBR-R16** 本页相对 tax-invoice-deepen/tax_calc_on_docs 的深化点：明确**计算入口缺席清单**（无服务函数、无路由、无字段快照），而非仅重复「未算税」。  

## 计算入口矩阵（有 / 无）

| 候选入口 | 有无 | 观察 |
|---|---|---|
| Quote totals 服务 | 有合计，无税 | `_compute_quote_totals` |
| DO Post AR | 有计提，无税 | `_legacy_create_ar` |
| Purchase invoice create | 有复制总额，无税 | `_legacy_create_purchase_invoice` |
| Tax Center | 列表 + 测试插入 | 非计算 |
| Tax capability API | health/permissions | 非交易引擎 |
| NDE line/financial tax slots | 展示槽 | 默认空/0 |
| Country tax_fields | 架构 stub | 不驱动公式 |
| DB trigger 算税 | 未在 Python/DDL 证据中出现 | — |

## 流程（实际观察到的）

1. 启动创建 `tax_settings`（若不存在）并 `INSERT OR IGNORE` 种子税率。  
2. 用户维护报价行金额 → 服务累加 `total_amount`（无税）。  
3. DO 发运/完成后，Type A Approve 将 DO 总额写入 `ar_records`（无税拆分）。  
4. 采购开票复制 PO 总额到 `purchase_invoices`（无税）。  
5. NDE 打印可渲染 Tax/VAT 槽；数值通常为空或 0。  
6. Tax Center 可列表 `tax_records`；测试按钮插入固定行。  
7. **全程未见**「选税码 → 确定税基 → 乘税率 → 写单据税字段 → 过账 tax_records」闭环。  

## 校验（强 / 弱 / 缺失）

1. **TBR-V01（强/schema）** `tax_settings.tax_code` 唯一。  
2. **TBR-V02（缺失）** 交易必须选择有效税码 —— 单据路径无。  
3. **TBR-V03（缺失）** 税基字段必须存在且与行金额勾稽 —— 无税基列。  
4. **TBR-V04（缺失）** 税额 = 税基 × 税率并按规则舍入 —— 无公式入口。  
5. **TBR-V05（缺失）** 含税/未税标记一致性 —— 未建模。  
6. **TBR-V06（缺失）** 行税合计 = 头税合计 —— 无行税。  
7. **TBR-V07（缺失）** 单据税额变更必须重算税基快照 —— 无快照。  
8. **TBR-V08（违反）** `/add_test_tax` GET 写库且固定值，非算税校验。  
9. **TBR-V09（弱）** Tax capability health 可响应；与算税无关。  
10. **TBR-V10（弱/展示）** 打印 VAT 行仅在真值时显示，避免把 0 当已计税。  
11. **TBR-V11（缺失）** 多币种税基与汇率时点 —— 算税链不存在。  
12. **TBR-V12（缺失）** 采购进项与销售销项分立计算 —— 无。  

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| `tax_settings.tax_rate` | 字典百分比；非交易快照 |
| `tax_settings.tax_code` | 字典唯一键（如 `CN_VAT`） |
| Quote `total_amount` | 行金额合计；含税属性未定义 |
| Quote 行 `amount` | 业务行金额；非税基快照 |
| DO `total_amount` | Post AR 金额权威；非税基 |
| `ar_records.amount` / `balance` | 应收总额；无税拆分 |
| `purchase_invoices.invoice_amount` | PO 总额镜像 |
| NDE `line.tax` | 打印列槽位（默认 `""`） |
| NDE `financial.vat` | 汇总 VAT 槽（默认 0） |
| NDE `financial.subtotal` / `grand_total` | 常被直接填业务总额 |
| country `tax_fields` | 模板应展示哪些税籍字段名 |
| `invoice_layout: cn_fapiao_style` | 国家版式意图，非开票引擎 |
| Tax capability slug `tax` | 可消费能力名，非单据算税服务 |
| `tax_records.amount` | 未定义组成的台账金额 |

## 证据表

| ID | 证据 | 强度 | 只读来源路径 |
|---|---|---|---|
| TBR-E01 | tax_settings DDL + 种子税率 | 强 | `runtime/v14/legacy_support.py`（~12617–12653） |
| TBR-E02 | ar_records DDL 无税字段 | 强 | `runtime/v14/legacy_support.py`（~1330–1341） |
| TBR-E03 | Quote totals 无税 | 强 | `apps/quotation/services.py`（`_compute_quote_totals`） |
| TBR-E04 | Post AR 复制 DO 总额 | 强 | `apps/finance/services.py`（`_legacy_create_ar`） |
| TBR-E05 | NDE tax/vat 默认空/0 | 强 | `document/nde_engine.py` |
| TBR-E06 | 打印 Tax/VAT 槽 | 中 | `templates/print/blocks/06_product_table.html`、`07_financial.html` |
| TBR-E07 | country tax_fields / fapiao stubs | 中 | `document/country_templates.py` |
| TBR-E08 | Tax capability scaffold | 强 | `core/capabilities/tax/service.py`、`README.md`、`tests/test_tax.py` |
| TBR-E09 | Tax Center + 固定测试插入 | 强 | `apps/finance/finance_ops_pages.py`、`templates/tax_center.html` |
| TBR-E10 | quotation/sales apps 无 tax_rate 业务用法 | 强缺席 | `apps/quotation/**`、`apps/sales/**` 关键词检索（仅 residual activate） |
| TBR-E11 | locale-commerce / tax-calc 权威边界 | 强 | [`../locale-commerce/tax.md`](../locale-commerce/tax.md)、[`../tax-invoice-deepen/tax_calc_on_docs.md`](../tax-invoice-deepen/tax_calc_on_docs.md) |

## UNKNOWN + 已查路径

1. **产品主数据是否另有隐藏税码字段被离线报表使用 UNKNOWN。** 已查：`apps/quotation`、`apps/sales`、`apps/finance` services、runtime DDL 片段、pricing 关键词。  
2. **定价引擎 final_price 业务约定是否「含税」UNKNOWN。** 已查：locale-commerce/tax、quotation totals、product pricing 交界叙述。  
3. **某国部署是否在 DB trigger/存储过程层算税 UNKNOWN。** 已查：Python 服务路径与 DDL；未读生产库 trigger。  
4. **调用方可否经 NDE `extra.vat` 手工注入税额而不留服务端计算 UNKNOWN。** 已查：`nde_engine` `extra.get("vat",0)`；AR/quote builder 未见传入。  
5. **i18n country_localization 是否计划自动选税率 UNKNOWN。** 已查：capability bridge、country_templates 注释意图；无交易调用证据。  
6. **采购成本是否含进项税未拆 UNKNOWN。** 已查：purchase_invoices 字段、finance 开票路径。  
7. **是否存在未合并分支实现 line-tax API UNKNOWN。** 已查：`apps/finance`、`document/`、`core/capabilities/tax`。  

## 只读来源路径

`runtime/v14/legacy_support.py` · `apps/quotation/services.py` · `apps/finance/services.py` · `apps/finance/finance_ops_pages.py` · `document/nde_engine.py` · `document/country_templates.py` · `core/capabilities/tax/` · `templates/print/blocks/` · `templates/tax_center.html` · `docs/knowledge/legacy-extract/locale-commerce/tax.md` · `docs/knowledge/legacy-extract/tax-invoice-deepen/tax_calc_on_docs.md`
