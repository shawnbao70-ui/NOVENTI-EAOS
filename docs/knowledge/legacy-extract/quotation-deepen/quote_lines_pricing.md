# 报价行项目与计价交界

**Evidence strength:** Strong for active line formula and Approve repricing; weak/missing for discounts, tax and FX execution  
**Pricing cross-reference:** [`../pricing-advanced/INDEX.md`](../pricing-advanced/INDEX.md)

## Scope 与关键结论

本页只说明“报价行如何形成、保存、修订、汇总和转单”，不复制 pricing-advanced 的完整价格来源、毛利、币种和规则分析。活动新增行以产品成本或人工成本为基准，按目标销售毛利率反推单价；Approve 改价则把单价视为人工结果，再按保存成本反算实际毛利。两条路径中 `profit_rate` 语义发生变化。

详细公式、价目来源、成本与币种边界见：

- [`../pricing-advanced/quote_pricing_engine.md`](../pricing-advanced/quote_pricing_engine.md)
- [`../pricing-advanced/price_lists.md`](../pricing-advanced/price_lists.md)
- [`../pricing-advanced/cost_margin.md`](../pricing-advanced/cost_margin.md)
- [`../pricing-advanced/currency_price.md`](../pricing-advanced/currency_price.md)

## 业务规则

| ID | 规则 |
|---|---|
| QLP-R01 | 新增报价行必须先找到产品；产品不存在时不写行。 |
| QLP-R02 | 提交成本大于零时采用人工成本，否则回退产品主数据成本。 |
| QLP-R03 | 新增行单价按 `cost / (1 - profit_rate/100)` 反推。 |
| QLP-R04 | 新增时单位利润为单价减成本，行金额为数量乘单价。 |
| QLP-R05 | 单价、单位利润和行金额形成时舍入两位。 |
| QLP-R06 | 行保存产品、数量、成本、目标/结果毛利率、单价、单位利润和金额快照。 |
| QLP-R07 | 新增或删除行后，报价头总额从数据库行金额 SUM 重算，不信任客户端头总额。 |
| QLP-R08 | 详情加载还会计算总成本和总毛利，并回写报价头。 |
| QLP-R09 | Draft Approve 可人工修改数量和单价；服务端按保存成本重算金额、利润和毛利率。 |
| QLP-R10 | Approve 改价后 `profit_rate=(price-cost)/price`；price=0 时置 0。 |
| QLP-R11 | 非 Draft 的 Approve 页面把数量和单价设为只读。 |
| QLP-R12 | 复制报价沿用原行成本、毛利率、单价和金额，不重新执行定价。 |
| QLP-R13 | 转 SO 只复制产品、数量、单价和金额，不复制成本、利润或毛利率。 |
| QLP-R14 | 客户历史价只作为人工参考，不自动覆盖报价行。 |
| QLP-R15 | 报价行活动模型未见折扣、税、币种或汇率字段；这些语义来自头或其他试算面。 |
| QLP-R16 | 独立 Product Pricing Engine 的成本加成→折扣→FX 结果不写回报价行。 |
| QLP-R17 | 报价头币种/汇率未参与新增行主公式，行价格隐含继承头币种。 |
| QLP-R18 | 删除行后直接重算总额；总成本/毛利通常由详情或批准上下文刷新，存在短暂派生值不同步窗口。 |

## 形成与修订流程

### 新增行

1. 选择产品，输入数量、可选成本和目标毛利率。
2. 服务读取产品；人工成本无效时回退产品成本。
3. 反推单价并形成利润、金额快照。
4. 写入报价行，再按行金额合计刷新头总额。
5. 详情上下文计算总成本、总毛利和 margin percentage。

### Approve 改量/改价

1. 仅 Draft 页面可编辑行数量和单价。
2. 服务端检查数量正数、价格非负。
3. 使用原保存成本重算金额、单位利润和结果毛利率。
4. 重取行并刷新头总额/毛利。
5. Save Draft 停留在 Draft；Approve 还需状态、非空行和 Human Confirm。

## 校验

| ID | 校验 | 强度 |
|---|---|---|
| QLP-V01 | 产品必须存在 | Hard |
| QLP-V02 | Approve 数量必须大于零 | Hard |
| QLP-V03 | Approve 单价不得小于零 | Hard |
| QLP-V04 | Approve 发布前必须至少有一行 | Hard |
| QLP-V05 | 只有 Draft 可在 Approve 发布 | Hard |
| QLP-V06 | 发布必须人工确认 | Hard |
| QLP-V07 | 新增行数量必须大于零 | Weak UI / server missing |
| QLP-V08 | 新增目标毛利率必须小于 100% | Missing；存在除零/负价风险 |
| QLP-V09 | 成本、价格、金额必须为有限数且在上限内 | Missing |
| QLP-V10 | 最低价/最低毛利/最大折扣授权 | Missing |
| QLP-V11 | 头总额必须与行 SUM 一致 | Recomputed in several paths；无并发版本门 |
| QLP-V12 | 折扣、税、运费必须有明确计算次序 | Missing |
| QLP-V13 | 币种与汇率必须在改价时冻结/复核 | Missing |
| QLP-V14 | 转单前行产品仍存在且可售 | Missing |

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| `quote_items.product_id` | 报价行引用的产品 |
| `qty` | 报价数量 |
| `cost_price` | 报价采用的单位成本快照 |
| `profit_rate` | 新增时是目标销售毛利率；改价后是计算结果毛利率 |
| `price` | 报价行单位报出价 |
| `profit` | 单位利润，不乘数量 |
| `amount` | 数量乘单价的行金额 |
| `quotes.total_amount` | 行金额合计的头快照 |
| `total_cost` | 数量乘行成本之和，常在页面上下文计算 |
| `gross_profit` | 头总额减总成本，保存于报价头 |
| `margin_pct` | `gross_profit / total_amount × 100` 的展示值 |
| `products.cost_price` | 人工成本未提供时的默认成本来源 |
| `products.sale_price` | 产品参考销售价；不进入当前新增行主公式 |
| `last_unit_price` | 客户+产品最近正数报价价的人工参考 |
| `currency` | 报价头币种标签；行不重复存储 |
| `exchange_rate` | 报价头汇率；活动行公式未使用 |
| `discount_rate` | 独立试算输入；不是活动报价行字段 |
| SO 行 `price/amount` | 转单时从报价行复制的商业快照 |

## 与 pricing-advanced 的责任边界

本页不重复证明以下专题：

- 产品成本价/销售价与历史价层级：见 [`price_lists.md`](../pricing-advanced/price_lists.md)；
- 成本快照、毛利可见性和成本构成：见 [`cost_margin.md`](../pricing-advanced/cost_margin.md)；
- 两种计价公式及独立试算边界：见 [`quote_pricing_engine.md`](../pricing-advanced/quote_pricing_engine.md)；
- 报价币种、汇率和本位币缺口：见 [`currency_price.md`](../pricing-advanced/currency_price.md)。

此处新增的生命周期交界结论是：Draft Approve 可以改变商业快照；Sent 后专用改价版本流未证实；Convert SO 复制当前快照而不重新定价。

## 证据表

| # | 观察事实 | 强度 | 只读来源 |
|---|---|---|---|
| QLP-E01 | 产品检查、成本回退和反推公式 | 强 | `apps/quotation/services.py` |
| QLP-E02 | 行字段写入与头 SUM | 强 | `apps/quotation/repository.py` |
| QLP-E03 | 详情汇总总成本/毛利并回写 | 强 | `apps/quotation/services.py` |
| QLP-E04 | Approve 行补丁校验和重算 | 强 | `apps/quotation/services.py`、`repository.py` |
| QLP-E05 | Draft 可编辑、非 Draft 只读 | 强 | `templates/quote_approve.html` |
| QLP-E06 | 客户历史价展示与新增行输入 | 强 | `templates/quote_detail.html` |
| QLP-E07 | 复制沿用旧行快照 | 强 | `apps/quotation/services.py`、`repository.py` |
| QLP-E08 | 转 SO 只复制四个行字段 | 强 | `apps/sales/services.py`、`repository.py` |
| QLP-E09 | 报价行 DDL 无折扣/币种/税字段 | 强 | `runtime/v14/legacy_support.py` |
| QLP-E10 | 独立计价试算不写报价 | 强 | `apps/finance/finance_ops_pages.py`、`templates/product_pricing_engine.html` |
| QLP-E11 | Quote Approve 验收允许可选改价 | 中 | `docs/reports/V18_Quote_Approve_Gate_Report.md` |
| QLP-E12 | Quotation 模块声明价格规则与 Finance 共享 | 中（边界） | `business_modules/quotation.md` |

## UNKNOWN + 已查路径

1. **目标毛利率业务上限和越权审批阈值 UNKNOWN。** 已查：`apps/quotation/`、`apps/approval/`、报价模板、`docs/reports/`。
2. **税、折扣、运费和汇率的正式执行顺序 UNKNOWN。** 已查：报价服务/模板、Finance 试算、commercial terms、pricing-advanced 证据源。
3. **Sent/Negotiating 后正式改价和版本生效流程 UNKNOWN。** 已查：`apps/quotation/history.py`、`quote_versions`、状态/Approve 路径。
4. **舍入应按行、按头还是币种最小单位 UNKNOWN。** 已查：报价服务、Finance 试算、locale formatter、打印模板。
5. **头汇率由谁维护、何时锁定 UNKNOWN。** 已查：新增/编辑报价、默认值解析、币种 locale、Finance 路径。
6. **并发新增/删除/Approve 导致头汇总覆盖的处理 UNKNOWN。** 已查：`apps/quotation/repository.py`、`services.py`；未见版本条件。
7. **产品失效或成本更新后旧报价应否重价 UNKNOWN。** 已查：产品、报价复制/转单服务、pricing rules 结构。

## 交叉引用

- Pricing Advanced 索引：[`../pricing-advanced/INDEX.md`](../pricing-advanced/INDEX.md)
- 发布与改价人工点：[`quote_approve.md`](quote_approve.md)
- 转单快照：[`quote_convert_gates.md`](quote_convert_gates.md)
