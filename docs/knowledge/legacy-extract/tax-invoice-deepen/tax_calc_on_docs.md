# 单据税额计算与 locale-commerce/tax 边界

## Scope 与结论

交叉引用权威：[`../locale-commerce/tax.md`](../locale-commerce/tax.md)、[`../finance/invoices.md`](../finance/invoices.md)。本页不重写税率字典正文，只深挖「业务单据是否计算税额」以及与 locale-commerce/tax 的边界。

**结论：** 活动报价/订单/采购/采购发票/DO Post AR 路径 **不** 按 `tax_settings` 计算或拆分税额。NDE 仅预留 `line.tax` 与 `financial.vat` 展示槽。`core/capabilities/tax` 是 health/bridge 脚手架。`document/country_templates.py` 提供国家税字段与发票 layout **架构意图**，不驱动交易算税。locale-commerce/tax 覆盖的是字典与台账；本页覆盖的是单据计算缺口。

## 业务规则（稳定 ID）

1. **TCD-R01** `tax_settings` 保存 `tax_code`（唯一）、`tax_name`、`country_code`、`tax_rate`、`status`；种子含 CN/ID/BD/VN VAT/PPN。
2. **TCD-R02** `tax_records` 保存独立金额行，无 taxable base、rate 快照、currency、party、source_doc。
3. **TCD-R03** Tax Center 只列表 `tax_records`；不汇总申报、不从单据过账。
4. **TCD-R04** `/add_test_tax` 写入固定 `VAT` + 金额 `1500` + `Pending`，不读 `tax_settings`。
5. **TCD-R05** 报价合计由行 `amount` 累加成本/售价/利润；未见乘税率步骤。
6. **TCD-R06** 销售/库存侧 DO Post AR 金额取 DO 头 `total_amount`，无税拆分字段写入 `ar_records`。
7. **TCD-R07** 采购发票金额取 PO 头总额；`purchase_invoices` 无 tax 列。
8. **TCD-R08** NDE `build_product_lines_from_quote_items` 将 `tax` 设为 `""`。
9. **TCD-R09** NDE financial 默认 `vat=extra.get("vat", 0)`；AR/多数 builder 不计算 VAT。
10. **TCD-R10** 打印模板有 Tax 列与 VAT 行，但空/0 时不构成已算税证明。
11. **TCD-R11** Country template profile 可声明 `tax_fields`、`invoice_layout`（如 `cn_fapiao_style`）、`legal_footer_key` —— 标注为 architecture stubs。
12. **TCD-R12** Tax capability `BRIDGE = core.i18n.country_localization`；consume health ≠ 交易算税。
13. **TCD-R13** locale-commerce/tax 权威范围：税率设置、税务记录、与价格交界缺口；**不**声称单据引擎已算税。
14. **TCD-R14** 本 deepen 边界：单据（Quote/SO/DO/PO/PINV/AR/NDE）是否调用税码算税；结论为否。
15. **TCD-R15** 含税价/未税价/`tax_inclusive` 在活动单据字段中未形成统一语义。
16. **TCD-R16** 不得把 UI 翻译中的「税」「VAT」标签或国家 footer key 解释为已实现算税引擎。

## 边界图

```
locale-commerce/tax          tax-invoice-deepen (本页)
-----------------            ---------------------------
tax_settings 字典     --->   单据是否匹配税码？  NO
tax_records 台账      --->   单据是否过账税额？  NO
capability scaffold   --->   是否交易引擎？      NO
country profile 意图  --->   是否改写金额公式？  NO（架构槽位）
NDE tax/vat 展示槽    --->   是否计算填充？      默认空/0
```

## 流程（实际观察到的）

1. 启动写入 `tax_settings` 种子（若表新建）。
2. 用户可打开 Tax Center 看 `tax_records`；或 GET 添加测试税行。
3. 报价保存行金额并汇总 `total_amount`（无税）。
4. DO 发运/完成与 Post AR 使用业务总额（无税拆分）。
5. 采购开票复制 PO 总额（无税）。
6. NDE 打印可渲染 Tax/VAT 槽位；数值通常为空或 0。
7. 全程未见「读 tax_settings → 算行税 → 写单据税字段 → 写 tax_records」闭环。

## 校验（强 / 弱 / 缺失）

1. **TCD-V01（强/schema）** `tax_settings.tax_code` 唯一。
2. **TCD-V02（缺失）** 交易必须选择有效税码 —— 单据路径无。
3. **TCD-V03（缺失）** 税额 = 税基 × 税率并按规则舍入 —— 无公式。
4. **TCD-V04（缺失）** 含税/未税标记一致性 —— 未建模。
5. **TCD-V05（缺失）** 单据税额合计 = 行税合计 —— 无行税。
6. **TCD-V06（缺失）** `tax_records` 必须来源于单据过账 —— 测试路径手工插。
7. **TCD-V07（缺失）** 国家 profile 变化不得静默改已入账税额 —— 无入账税字段。
8. **TCD-V08（弱）** Tax capability health 可响应；与算税无关。
9. **TCD-V09（违反）** `/add_test_tax` GET 写库且固定值，非校验算税。
10. **TCD-V10（缺失）** 采购进项税与销售销项税分立科目 —— 无。
11. **TCD-V11（弱/展示）** 打印 VAT 行仅在真值时显示，避免把 0 当成已计税。
12. **TCD-V12（缺失）** 多币种税基与汇率时点 —— 单据算税链不存在。

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| `tax_settings.tax_rate` | 字典百分比；非交易快照 |
| `tax_settings.status` | 字典 Active/非 Active |
| `tax_records.amount` | 未定义组成的台账金额 |
| `tax_records.tax_type` | 自由文本税种 |
| Quote `total_amount` | 行金额合计；含税属性未定义 |
| DO/AR `amount` | 业务总额快照；非税额 |
| `purchase_invoices.invoice_amount` | PO 总额镜像 |
| NDE `line.tax` | 打印列槽位 |
| NDE `financial.vat` | 汇总 VAT 槽位 |
| NDE `financial.subtotal`/`grand_total` | 常被直接填业务总额 |
| `customer.tax_number`（经 extra） | 打印身份字段意图 |
| country `tax_fields` | 模板应展示哪些税籍字段 |
| `invoice_layout: cn_fapiao_style` | 国家版式意图，非开票引擎 |
| `legal_footer_key` | 页脚法务文案键 |
| Tax capability slug `tax` | 可消费能力名，非单据服务 |
| locale-commerce/tax | EAOS 知识权威：字典/台账边界 |

## 证据表

| ID | 证据 | 强度 | 只读来源路径 |
|---|---|---|---|
| TCD-E01 | tax_settings / tax_records DDL 与种子 | 强 | `runtime/v14/legacy_support.py` |
| TCD-E02 | Tax Center + 测试插入 | 强 | `apps/finance/finance_ops_pages.py` |
| TCD-E03 | 报价合计无税 | 强 | `apps/quotation/services.py` |
| TCD-E04 | AR/采购发票无税字段写入 | 强 | `apps/finance/services.py` |
| TCD-E05 | NDE tax/vat 默认空/0 | 强 | `document/nde_engine.py` |
| TCD-E06 | 打印 Tax/VAT 槽 | 中 | `templates/print/blocks/06_product_table.html`、`07_financial.html` |
| TCD-E07 | country tax_fields / fapiao layout stubs | 中 | `document/country_templates.py` |
| TCD-E08 | Tax capability scaffold | 强 | `core/capabilities/tax/service.py`、`README.md` |
| TCD-E09 | locale-commerce/tax 权威缺口叙述 | 强 | [`../locale-commerce/tax.md`](../locale-commerce/tax.md) |
| TCD-E10 | sales/quotation apps 无 tax_rate 业务用法（相对命中） | 强缺席 | `apps/quotation/**`、`apps/sales/**` 关键词检索 |

## UNKNOWN + 已查路径

1. **产品主数据是否另有隐藏税码字段被报表使用 UNKNOWN。** 已查：quotation/sales/finance services、runtime DDL 片段、pricing 模板关键词。
2. **定价引擎 final_price 业务约定是否「含税」UNKNOWN。** 已查：locale-commerce/tax、product_pricing_engine 交界叙述、quotation totals。
3. **某国部署是否在 DB trigger 层算税 UNKNOWN。** 已查：Python 服务路径与 DDL；未读生产 trigger。
4. **`tax_records` 人工录入 SOP 是否替代单据算税 UNKNOWN。** 已查：Tax Center、add_test_tax、finance reports。
5. **NDE extra 是否可被调用方手动传入 vat 而不留服务端计算 UNKNOWN。** 已查：nde_engine `extra.get("vat",0)`；调用方 AR/quote 分支未见传入。
6. **i18n country_localization 是否在未来版本自动选税率 UNKNOWN。** 已查：capability bridge 声明、country_templates 注释「V15 implements full rules」；当前无交易调用证据。
7. **采购成本是否含进项税未拆 UNKNOWN。** 已查：purchase_invoices 字段、procurement/finance 开票路径。

## 只读来源路径

`runtime/v14/legacy_support.py` · `apps/finance/finance_ops_pages.py` · `apps/finance/services.py` · `apps/quotation/services.py` · `document/nde_engine.py` · `document/country_templates.py` · `core/capabilities/tax/` · `templates/print/blocks/` · `templates/tax_center.html` · `docs/knowledge/legacy-extract/locale-commerce/tax.md` · `docs/reports/audit/07_I18N_AUDIT.md`（locale-commerce 已引）
