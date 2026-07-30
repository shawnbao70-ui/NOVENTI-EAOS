# 多币种标价与换算交界

## Scope与证据强度

本页只讨论“价格如何带币种、何处实际换算”。币种字典、资金账户和本地化总览见 [`../locale-commerce/currency.md`](../locale-commerce/currency.md)。

报价头币种/汇率的保存、默认和复制证据强；行价属于头币种是模型上的隐含语义；真正 FX 换算只在独立 Product Pricing Engine 中明确执行。未发现报价主链生成本位币金额、汇率日期、来源或汇兑差额。

## 业务规则（稳定ID）

1. **CP-R01** 报价头保存 `currency` 和 `exchange_rate`；报价行没有独立币种或汇率字段。
2. **CP-R02** 新报价商业头默认优先级为：客户最近报价→活动品牌币种→平台 USD/1.0。
3. **CP-R03** 最近报价可同时复用币种和汇率；品牌默认只替换币种，未证明自动取得对应市场汇率。
4. **CP-R04** 报价复制原样继承源报价币种和汇率，不按复制日期重新取汇率。
5. **CP-R05** 从样品建报价也调用商业默认解析，并把币种和汇率写入报价头。
6. **CP-R06** 报价新增行按成本与毛利率计价，不读取报价头汇率；成本、单价和金额隐含处于同一头币种。
7. **CP-R07** 客户历史价格统计不按币种过滤或归一，客户跨币种报价会被直接混合。
8. **CP-R08** 客户+SKU 最近价提示同样不返回源币种/汇率，不能证明可安全跨币种复用。
9. **CP-R09** 独立 Pricing Engine 以 `final_price / exchange_rate` 得到 `usd_price`，其方向只在该试算上下文成立。
10. **CP-R10** 独立试算汇率由用户输入，结果不写回报价、产品或汇率主数据。
11. **CP-R11** 报价模板可按报价类型、语言、币种和 Active 状态筛选；模板币种是版式/推荐维度，不执行换算。
12. **CP-R12** `product_price_rules` 可保存国家、币种、国别系数和汇率，但未发现报价运行路径匹配该表。
13. **CP-R13** 产品 `cost_price` / `sale_price` 不带自身币种字段，故产品价币种只能由外部约定推断。
14. **CP-R14** 报价详情与 Approve 用头币种标签展示总额；金额数值本身仍是原报价行汇总。
15. **CP-R15** 代码意图明确“不虚构 FX”；默认 1.0 是平台回退，不是实时市场汇率证据。

## 流程

### 新建报价

1. 先建立 USD/1.0 平台默认。
2. 有活动品牌币种时替换币种。
3. 客户有历史报价时，以最近报价商业头覆盖币种和汇率。
4. 报价头持久化币种/汇率。
5. 行定价不执行换算，只形成单一数值单价和金额。

### 复制与样品转报价

- 复制：继承源商业头快照。
- 样品转报价：按客户默认链解析，再更新完整商业头。
- 两者均未见按当日市场汇率刷新。

### 独立价格换算

1. 用户输入成本、加成率、折扣率和汇率。
2. 计算折后价。
3. 折后价除以输入汇率，展示 USD 价。
4. 不保存、不批准、不传播到报价。

## 校验（强/弱/缺失）

1. **CP-V01（强/类型）** 报价商业头路径将汇率转换为浮点数。
2. **CP-V02（强）** 报价模板推荐要求模板状态为 Active，并精确匹配币种。
3. **CP-V03（弱）** 多个报价入口使用 USD/1 回退，保证字段可有值，但不保证业务正确。
4. **CP-V04（缺失）** 未见报价币种只能取活动币种字典的校验。
5. **CP-V05（缺失）** 未见汇率必须大于零；独立试算可发生除零。
6. **CP-V06（缺失）** 未见基准币汇率必须为 1 的报价校验。
7. **CP-V07（缺失）** 未见汇率方向、来源、报价类型、日期和有效期校验。
8. **CP-V08（缺失）** 未见产品成本币种与报价币种一致性校验。
9. **CP-V09（缺失）** 未见历史价格比较前同币种过滤/折算。
10. **CP-V10（缺失）** 未见按币种定义小数位和舍入规则；价格普遍固定两位。
11. **CP-V11（缺失）** 未见复制报价时提示汇率过期或要求刷新。
12. **CP-V12（缺失）** 未见转 SO/发票时汇率锁定和差异检查的完整证据。

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| `quotes.currency` | 报价金额名义币种 |
| `quotes.exchange_rate` | 报价商业头的裸汇率值/快照 |
| `quote_items.price` | 隐含属于报价头币种的单位价 |
| `quote_items.cost_price` | 隐含与行价同币种的成本；无显式保证 |
| `quote_items.amount` | 头币种下的数量乘单价 |
| `products.sale_price` | 无币种字段的产品参考售价 |
| `products.cost_price` | 无币种字段的产品主成本 |
| `brand_profiles.currency` | 新报价默认币种候选 |
| 最近报价商业头 | 客户币种/汇率默认来源 |
| `quote_templates.currency` | 模板筛选维度 |
| `product_price_rules.currency` | 未接线的规则币种 |
| `product_price_rules.exchange_rate` | 未接线的规则汇率 |
| `country_factor` | 未证实参与运行换算的国别系数 |
| `usd_price` | 独立试算的显示结果 |
| `currency_settings.exchange_rate` | 币种设置汇率；与报价取值的自动关联未证实 |

## 状态词汇

| 状态/词汇 | 含义 |
|---|---|
| `Active` | 模板/币种/品牌可用状态，不等于汇率当前有效 |
| `Draft` | 报价商业头和价格仍处草稿 |
| `Sent` | 报价已人工批准；不等于 FX 已结算 |
| 快照 | 报价头保存并在复制时沿用的币种/汇率 |
| 基准币 | Currency 设置中的 `is_base` 概念 |
| 名义币种 | 金额标签币种，未必伴随本位币金额 |
| USD 试算价 | 独立页面除法结果，不是报价字段 |

## 证据表

| # | 观察事实 | 强度 | 只读来源路径 |
|---|---|---|---|
| CP-E01 | 报价头新增币种和汇率列 | 强 | `runtime/v14/legacy_support.py` |
| CP-E02 | 新报价默认链复用最近报价/品牌/平台 | 强 | `v15/ux/master_defaults.py`、`apps/quotation/services.py` |
| CP-E03 | 报价复制继承源币种和汇率 | 强 | `apps/quotation/services.py`、`repository.py` |
| CP-E04 | 行价公式不读取汇率 | 强 | `apps/quotation/services.py` |
| CP-E05 | 历史价查询不带币种过滤/返回 | 强 | `apps/quotation/repository.py` |
| CP-E06 | 报价详情显示币种/汇率，Approve 以币种标签显示总额 | 强 | `templates/quote_detail.html`、`templates/quote_approve.html` |
| CP-E07 | 独立试算以折后价除汇率生成 USD 价 | 强 | `apps/finance/finance_ops_pages.py`、`templates/product_pricing_engine.html` |
| CP-E08 | 模板推荐按类型、语言、币种、Active 匹配 | 强 | `apps/quotation/utils.py`、`quote_api.py` |
| CP-E09 | 产品价格字段无币种列 | 强 | `runtime/v14/legacy_support.py` |
| CP-E10 | 多维价格规则含币种/汇率但无活动匹配调用 | 中/缺失证据 | `runtime/v14/legacy_support.py`、`apps/product/`、`apps/quotation/` |

## UNKNOWN + 已查路径

1. **报价汇率的来源、维护人和生效日期 UNKNOWN。** 已查路径：`apps/quotation/`、`apps/finance/`、`currency_settings` DDL、`docs/reports/`。
2. **报价汇率的方向（外币/本位币或反向）UNKNOWN。** 已查路径：`v15/ux/master_defaults.py`、报价服务、独立试算；只有试算除法可见。
3. **产品成本价/销售价的名义币种 UNKNOWN。** 已查路径：`apps/product/`、产品 DDL、产品模板。
4. **历史客户价跨币种应如何比较 UNKNOWN。** 已查路径：`apps/quotation/repository.py`、`services.py`、`master_defaults.py`。
5. **报价转 SO 后是否完整继承币种与汇率 UNKNOWN。** 已查路径：`apps/quotation/`、`apps/sales/`、Sales DDL、Volume 009 报告。
6. **SO→发票时采用报价汇率、开票日汇率还是收款日汇率 UNKNOWN。** 已查路径：`apps/sales/`、`apps/finance/`、`business_modules/finance.md`。
7. **汇率差额、重估和汇兑损益 UNKNOWN。** 已查路径：`apps/finance/`、`templates/`、`docs/reports/`。
8. **`currency_settings.exchange_rate` 是否自动供报价或价格规则使用 UNKNOWN。** 已查路径：币种设置调用点、`apps/quotation/`、`apps/finance/`。
9. **按币种小数位（如零位或三位）舍入 UNKNOWN。** 已查路径：报价服务、独立试算、`core/i18n/formatter.py`、模板。

## 只读来源路径

- `H:\Workspace\EZAM_CRM - 9.0\apps\quotation\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\product\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\finance\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\sales\`
- `H:\Workspace\EZAM_CRM - 9.0\templates\`
- `H:\Workspace\EZAM_CRM - 9.0\business_modules\`
- `H:\Workspace\EZAM_CRM - 9.0\docs\reports\`
- `H:\Workspace\EZAM_CRM - 9.0\runtime\v14\legacy_support.py`
- `H:\Workspace\EZAM_CRM - 9.0\v15\ux\master_defaults.py`
- `H:\Workspace\EZAM_CRM - 9.0\core\i18n\formatter.py`
# 币种与价格换算交界（Currency × Pricing）— Legacy Knowledge

**Evidence strength:** Strong for quote-header FX snapshot and quote-line pricing; medium for standalone calculator; weak for governed cross-document conversion  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0` (read-only)  
**Cross-ref:** [`../locale-commerce/currency.md`](../locale-commerce/currency.md)（币种字典、formatter、资金账户语义）；[`../finance/pricing.md`](../finance/pricing.md)（报价行定价公式）；[`../finance/ar_receipt_reconciliation.md`](../finance/ar_receipt_reconciliation.md)（收款链与 AR 缺口）

---

## 1. Scope 与证据强度

本文件聚焦 **价格事实** 与 **币种/汇率** 的交界：报价头币种、汇率快照、产品基准价隐含币种、换算方向、舍入、以及 Quote → SO → Receipt/AR 的传递链。

| 层级 | 结论 | 强度 |
|------|------|------|
| **运行（持久化/计算）** | 报价头保存 `currency` + `exchange_rate`；行价/金额在头币种下计算；独立试算页执行 `折后价 ÷ 汇率 → USD`；复制/新建继承商业头 | 强 |
| **运行（未接通）** | 产品主数据、`product_price_rules` 无活动换算引擎；`currency_settings` 未自动写入报价头 | 中 |
| **仅格式化** | `core/i18n/formatter.format_currency`、NDE 模板展示、EOC FX 快照字符串 | 强（负向：不换算） |
| **传递断裂** | Quote→SO 不传 `currency`/`exchange_rate`；AR 无币种；Receipt 币种硬编码 USD | 强（负向证据） |

`core/capabilities/currency` 仅为 health/bridge 脚手架，**不是**可消费的换算服务（详见 locale-commerce 交叉引用）。

---

## 2. 业务规则（≥12）

| ID | 规则描述 | 运行 / 格式化 | 证据 / 缺口 |
|----|----------|---------------|-------------|
| CPX-R1 | 报价头 `currency` 为全单行价、成本、金额、总额的**名义币种**；行表无独立币种列 | 运行 | `quotes`/`quote_items` DDL；行金额按单价×数量持久化 |
| CPX-R2 | 报价头 `exchange_rate` 为**商业头快照**，随新建/复制/样单创建写入；不是按报价日行实时重算 | 运行 | `v15/ux/master_defaults.py`、`repository.update_quote_commercial_header` |
| CPX-R3 | 新报价默认优先级：**客户最近报价（含汇率）→ 品牌活动币种（仅币种）→ 平台 USD/1.0** | 运行 | `resolve_quote_header_defaults`；品牌路径不自动补汇率 |
| CPX-R4 | 复制报价**完整继承**源报价 `currency` + `exchange_rate`，不重新取 `currency_settings` | 运行 | `services.copy_quote` → `fetch_quote_commercial_header` |
| CPX-R5 | 产品 `cost_price`/`sale_price` **无币种字段**；与报价头币种隐含一致，跨币种比较未归一 | 运行（隐含） | `products` DDL；`resolve_product_line_hint` 不读币种 |
| CPX-R6 | 报价行定价公式（成本反推毛利率、行金额合计）**不使用** `exchange_rate`；汇率不参与行价计算 | 运行 | `services.add_quote_item`、`repository` 行 insert |
| CPX-R7 | 独立价格试算：`USD价 = 折后价 ÷ exchange_rate`；方向为**本地/输入币种 → USD** | 运行（试算，不持久） | `finance_ops_pages.calculate_price` |
| CPX-R8 | 试算页 `product_id` 不参与换算；结果不写产品/报价/汇率主数据 | 运行边界 | 同上 + `product_pricing_engine.html` |
| CPX-R9 | 金额舍入：**统一两位小数**（`round(..., 2)`）用于行价、行金额、总额、毛利、试算结果 | 运行 | `services.py`、`repository.py`、`finance_ops_pages.py` |
| CPX-R10 | Quote→SO：`convert_so` 复制 `total_amount` 与行 `price`/`amount`，**不复制** `currency`/`exchange_rate` | 运行（断裂） | `quote_pages.convert_so` INSERT 列；`sales_orders` 无 FX 列 |
| CPX-R11 | SO→Receipt：收款 INSERT 含 `currency` 列，但活动路径**硬编码 `"USD"`**，与 SO/报价币种脱钩 | 运行（错误默认） | `receipt_ar_expense_pages.py` 快捷收款 |
| CPX-R12 | DO→AR：`ar_records` 只存 `amount`/`balance`，**无币种**；与报价/SO 币种无显式关联 | 运行（缺失） | `legacy_support.py` AR DDL；`services._legacy_create_ar` |
| CPX-R13 | 文档打印（NDE）：`doc_info.currency` 与 `exchange_rate` 来自报价行，**原样展示**，不做本位币换算 | 格式化 + 快照传递 | `document/nde_engine.py` |
| CPX-R14 | EOC 财务指挥台 FX 行读取 `currency_settings` 生成**可读快照字符串**，不参与交易过账 | 格式化 | `v15/template_services/_helpers.load_currency_rates`、`eoc.py` |
| CPX-R15 | 报价模板维度含 `currency`（与语言、类型并列），仅用于模板筛选/AI 模板查询，不是行价事实 | 元数据 | `quote_templates`、`utils.get_ai_quote_templates` |
| CPX-R16 | V18 路由 `POST /add_quote` 经 `master_defaults` 写 FX；遗留 `quote_pages.add_quote` 仍**硬编码 USD/1** | 运行（双轨） | `router.py` vs `quote_pages.py` 并存 |

---

## 3. 校验（≥8）

| ID | 校验 | 强度 | 说明 |
|----|------|------|------|
| CPX-V1 | 报价头币种非空 | 部分 | 服务层默认 `"USD"`；遗留页硬编码 |
| CPX-V2 | 汇率必须为数值 | 类型级 | Form/float 接收；无 schema 约束 |
| CPX-V3 | 汇率 > 0 | **缺失** | 试算除零；负数无商业意义 |
| CPX-V4 | 币种代码绑定 `currency_settings` 活动字典 | **缺失** | 报价/试算/账户多为自由文本 |
| CPX-V5 | 行价币种与头币种一致 | **缺失** | 无行级币种，无法检测异币种行 |
| CPX-V6 | 复制/默认汇率不得 AI 虚构 | 意图 + 部分实现 | `master_defaults` 注释禁止 Fabricated FX |
| CPX-V7 | Quote→SO 传递币种/汇率 | **缺失** | SO 表结构不支持 |
| CPX-V8 | Receipt 币种与 SO/报价一致 | **缺失** | 硬编码 USD |
| CPX-V9 | 客户历史价比较前归一币种 | **缺失** | `fetch_last_quote_header` / 行 hint 跨币种混合 |
| CPX-V10 | 舍入策略按币种小数位 | **缺失** | JPY/VND 等仍两位小数 |
| CPX-V11 | `currency_settings.is_base` 唯一 | **缺失** | 无 DB 唯一约束 |
| CPX-V12 | 批准页展示币种/汇率但 Type A 不静默改 FX | 部分 | Approve 上下文读头字段；无专用 FX 编辑表单证实 |

---

## 4. 数据含义（≥10）

| Concept / Field | Legacy 含义 | 币种语境 |
|-----------------|-------------|----------|
| `quotes.currency` | 报价名义币种；行价/总额均在此币种下表达 | 交易事实 |
| `quotes.exchange_rate` | 报价商业头汇率快照；默认 1.0；不参与行价公式 | 快照，非市场自动价 |
| `quotes.total_amount` | 行 `amount` 合计；**未存**本位币金额 | 头币种金额 |
| `quote_items.price` / `amount` | 单价与行金额；隐含继承头币种 | 无行级 FX |
| `products.cost_price` / `sale_price` | 产品基准价；**无币种列** | 隐含公司/默认币 |
| `product_price_rules.currency` / `exchange_rate` | 多维价规则结构字段 | DDL 存在，活动引擎未证实 |
| `currency_settings.*` | 币种字典与相对基准汇率配置 | 见 locale-commerce CUR 数据表 |
| `brand_profiles.currency` | 公司/品牌默认报价币种候选 | 不携带汇率 |
| `customers.country` | 客户国家；**无** `currency` 列 | 仅 party 展示，非交易币 |
| `system_settings.DEFAULT_CURRENCY` | 平台默认 USD | 与品牌/租户默认并存 |
| `tenant_currency` | 租户中心配置默认币 | V151 schema；与报价链接通 UNKNOWN |
| `sales_orders.total_amount` | SO 总额；币种**未持久化** | 隐含继承报价币，无字段 |
| `receipts.currency` | 收款记录币种列 | 迁移后存在；活动路径常写 USD |
| `ar_records.amount` / `balance` | 应收金额；无币种 | 无法表达外币 AR |
| `treasury_* .currency` | 账户余额名义币种 | 见 locale-commerce |
| NDE `doc_info.exchange_rate` | 打印/文档展示用字符串或数值 | 格式化展示 |
| 试算 `usd_price` | 折后价按输入汇率折算的 USD 参考价 | 非持久事实 |

---

## 5. 流程

### 5.1 新建报价（V18 主路径）

1. `POST /add_quote` → `resolve_quote_header_defaults`（最近报价 → 品牌 → USD/1.0）。
2. `insert_quote_record` 写入 `currency`、`exchange_rate` 及付款/交期。
3. 加行时按成本/毛利率算 `price`、`amount`（**不用**汇率）。
4. 详情/批准页展示 `{currency} {total}`（字符串拼接，非 `format_currency` 强制）。

### 5.2 独立价格试算（Finance Ops）

1. 用户输入成本、加成率、折扣率、汇率（默认 1，步长 0.0001）。
2. 售价 = 成本 × (1 + 加成率%)；折后价 = 售价 × (1 − 折扣率%)。
3. **USD价 = 折后价 ÷ 汇率**（round 2 位）。
4. 返回 `product_pricing_engine.html`；**不写入**任何业务表。

### 5.3 Quote → SO → Receipt / AR

1. `convert_so`：INSERT `sales_orders`（`so_no`, `quote_id`, `customer_id`, `total_amount`, …）— **无 currency/FX**。
2. 复制 `quote_items` → `sales_order_items`（`price`, `amount` 原样）。
3. 快捷收款：INSERT `receipts` 带 `currency='USD'` 硬编码，`amount` = SO 剩余余额。
4. Post AR：INSERT `ar_records` 仅金额字段，**无币种**。
5. **全链未观察到**按 `exchange_rate` 生成本位币或汇兑损益。

### 5.4 文档与仪表盘（格式化）

1. NDE 构建 `doc_info.currency` / `exchange_rate` 供模板展示。
2. EOC `format_exchange_snapshot` 从 `currency_settings` 拼 `USD/CNY 7.20` 类字符串。
3. `format_currency` / `format_number` 仅影响 UI/文档字符串。

---

## 6. 运行 vs 仅格式化

| 能力 | 分类 | 说明 |
|------|------|------|
| 报价头 FX 持久化 | **运行** | 写入 `quotes` |
| 报价行计价/汇总 | **运行** | 与 FX 无关 |
| 试算 USD 换算 | **运行（非持久）** | 单次 HTTP 响应 |
| `currency_settings` 种子/查询 | **运行（主数据）** | 不自动推送报价 |
| Quote→SO 金额传递 | **运行** | 无 FX 字段 |
| Receipt USD 硬编码 | **运行（缺陷）** | 非格式化 |
| NDE/模板 exchange_rate 展示 | **仅格式化** | 读快照展示 |
| EOC FX snapshot | **仅格式化** | 仪表盘文案 |
| `core/i18n/formatter.format_currency` | **仅格式化** | 符号/RTL/千分位 |
| `v15/template_services.format_currency` | **仅格式化** | 简单 `$` 前缀 |
| GFIP exchange_rate API | **未实现** | status `reserved` |

---

## 7. 证据（≥8）

| # | 结论 | 绝对路径 |
|---|------|----------|
| E1 | 报价头含 `currency`、`exchange_rate` 列（默认 USD/1） | `H:\Workspace\EZAM_CRM - 9.0\runtime\v14\legacy_support.py`（`upgrade_quotes` / ALTER） |
| E2 | 新报价默认链：最近报价 → 品牌 → 平台；禁止虚构 FX | `H:\Workspace\EZAM_CRM - 9.0\v15\ux\master_defaults.py` |
| E3 | V18 `add_quote` 经 resolver 写 FX；API `/api/v18/master/defaults` 暴露预览 | `H:\Workspace\EZAM_CRM - 9.0\apps\quotation\services.py`、`router.py` |
| E4 | 复制报价继承源 `currency` + `exchange_rate` | `H:\Workspace\EZAM_CRM - 9.0\apps\quotation\services.py`（`copy_quote`） |
| E5 | 行价公式不用汇率；round 2 位 | `H:\Workspace\EZAM_CRM - 9.0\apps\quotation\services.py`、`repository.py` |
| E6 | 试算 `usd_price = final_price / exchange_rate` | `H:\Workspace\EZAM_CRM - 9.0\apps\finance\finance_ops_pages.py` |
| E7 | `convert_so` 不传 currency/FX；SO 表无 FX 列 | `H:\Workspace\EZAM_CRM - 9.0\apps\quotation\quote_pages.py`；`legacy_support.py` `sales_orders` DDL |
| E8 | Receipt 快捷路径 `currency='USD'` 硬编码 | `H:\Workspace\EZAM_CRM - 9.0\apps\finance\receipt_ar_expense_pages.py` |
| E9 | AR 插入无币种字段 | `H:\Workspace\EZAM_CRM - 9.0\apps\finance\services.py`（`_legacy_create_ar`） |
| E10 | NDE 将报价 `exchange_rate` 传入 `doc_info` 供模板 | `H:\Workspace\EZAM_CRM - 9.0\document\nde_engine.py` |
| E11 | 产品表无币种；`product_price_rules` 含 currency/FX 列 | `H:\Workspace\EZAM_CRM - 9.0\runtime\v14\legacy_support.py` |
| E12 | 遗留 `quote_pages.add_quote` 硬编码 USD/1（与 V18 双轨） | `H:\Workspace\EZAM_CRM - 9.0\apps\quotation\quote_pages.py` |
| E13 | V18-P6 门控报告确认 PI/NDE 读报价商业字段、无二次录入 | `H:\Workspace\EZAM_CRM - 9.0\docs\reports\V18_P6_Zero_Duplicate_Gate_Report.md` |

---

## 8. UNKNOWN（≥7，含已查路径）

| ID | 问题 | 已查绝对路径 | 说明 |
|----|------|--------------|------|
| CPX-U1 | 用户能否在报价详情**编辑**币种/汇率（非复制/样单）？ | `H:\Workspace\EZAM_CRM - 9.0\apps\quotation\quote_pages.py`、`router.py`、`templates\quote_detail.html` | 仅有展示列；`update_quote_commercial_header` 仅被 copy/sample 调用 |
| CPX-U2 | `currency_settings` 管理 UI 与更新审计 | `H:\Workspace\EZAM_CRM - 9.0\templates\`（无 match）、`apps\finance\`、`runtime\v14\legacy_support.py` | 表与种子存在；管理路由未证实 |
| CPX-U3 | 租户 `tenant_currency` 是否写入报价默认 | `H:\Workspace\EZAM_CRM - 9.0\database\v151_tenant_center_schema.py`、`v15\ux\master_defaults.py` | 租户字段存在；master_defaults 未引用 |
| CPX-U4 | 客户是否有隐含偏好币种（除 country profile 建议） | `H:\Workspace\EZAM_CRM - 9.0\runtime\v14\legacy_support.py`（customers DDL）、`core\i18n\country_localization.py` | customers 无 currency 列 |
| CPX-U5 | 采购单 `currency`/`exchange_rate` 是否参与 AP/成本 | `H:\Workspace\EZAM_CRM - 9.0\runtime\v14\legacy_support.py`（`upgrade_purchases`）、`apps\finance\` | 列已加；活动 AP 换算未证实 |
| CPX-U6 | 实时汇率 API 是否 ever 接入 | `H:\Workspace\EZAM_CRM - 9.0\v15\gfip\api_center.py`、`v15\gtfip\engines\api_center.py` | 标记 `reserved` |
| CPX-U7 | 打印金额用 `format_currency` 还是裸数值 | `H:\Workspace\EZAM_CRM - 9.0\templates\documents\`、`document\nde_engine.py` | NDE financial 块传数值；模板层不完全统一 |
| CPX-U8 | `business_modules/*.md` 是否记录 FX 规则 | `H:\Workspace\EZAM_CRM - 9.0\business_modules\quotation.md`、`finance.md`、`product.md` | 模块规格无 currency 语义（边界文档级） |

---

## 9. EAOS 迁移提示（摘要）

1. **单一汇率对象**：方向、日期、来源、基准币；报价头存快照 ID 而非裸 float。
2. **Quote→SO→Invoice/Receipt 全链携带 document_currency + functional_currency + fx_snapshot**。
3. **行价与 FX 分离**：行公式保持；本位币金额 = 行金额 × 快照汇率（若需要）。
4. **Receipt/AR 禁止硬编码 USD**；与 SO 币种或核销账户币一致。
5. **formatter 与换算服务分离**：沿用 locale-commerce 的 CUR-R12；换算走 domain service。
6. **收敛双轨入口**：废弃 `quote_pages.add_quote` 硬编码路径或统一走 resolver。

---

**Root:** `H:\Workspace\EZAM_CRM - 9.0\`  
**Package:** `H:\Workspace\NOVENTI-EAOS\docs\knowledge\legacy-extract\pricing-advanced\`
