# 成本、毛利、利润可见性与缺口

## Scope与证据强度

本页覆盖产品成本、报价成本快照、单位利润、报价总毛利、权限可见性和成本分解预留。报价运行链证据强；产品成本分解只有 DDL 与展示壳，证据中等；运费、税、库存计价、历史成本和会计利润口径证据不足。

此处“毛利”是报价销售额减报价行成本，不等于会计净利润。价格公式详情交叉引用 [`../finance/pricing.md`](../finance/pricing.md)。

## 业务规则（稳定ID）

1. **CM-R01** 产品 `cost_price` 是新增报价行的默认成本来源，用户提交正数成本时可覆盖它。
2. **CM-R02** 报价行保存独立 `cost_price`，形成报价时点的成本快照；产品成本以后变化不会自动改旧行。
3. **CM-R03** 新增行单位利润为 `price - cost_price`，行金额为 `qty × price`，均按两位小数形成。
4. **CM-R04** 报价总成本按每行 `qty × cost_price` 求和。
5. **CM-R05** 报价头 `gross_profit` 按总金额减总成本计算，并在打开详情或批准处理时回写。
6. **CM-R06** Approve 人工改价后，系统保留行成本，重算单位利润和 `(price-cost)/price` 毛利率。
7. **CM-R07** 复制报价原样复制成本、毛利率、单价和金额，不按当前产品成本重估。
8. **CM-R08** 报价详情的总成本、总毛利和行成本/毛利率仅对拥有 `Cost Price.view` 的用户显示。
9. **CM-R09** 新增产品行界面对无成本查看权限者隐藏成本/毛利率输入，并提交成本 0、默认毛利率 30%；服务端因成本不大于零而回退产品成本。
10. **CM-R10** 报价批准上下文会计算 margin percentage 和库存风险；可见的低/负毛利没有形成强制阻断。
11. **CM-R11** `product_costing` 结构可保存材料、人工、包装、运输、制造费用、总成本、目标利润率和建议价，但活动提交入口只重定向，未持久化。
12. **CM-R12** Finance 总览的 `gross_profit = total_sales - total_purchase` 是另一聚合口径，不能与报价头毛利直接等同。
13. **CM-R13** Finance 库存价值按产品 `stock_qty × cost_price` 汇总，属于主数据成本估值，不是批次/移动平均成本。
14. **CM-R14** 产品成本和销售价均可维护，但产品模板只对成本显示实施 `Cost Price.view` 隐藏。

## 流程

### 报价成本与毛利

1. 从产品取默认成本，或接受有权限用户输入的正数成本。
2. 按目标毛利率形成单价，保存成本、利润、毛利率、单价和金额。
3. 打开详情时汇总总额和总成本，计算并回写头毛利。
4. Draft Approve 可改数量/单价；成本不变，盈利字段重新计算。
5. 人工确认后状态进入 Sent；没有最低毛利服务端门槛。
6. 复制时全部金额与成本快照沿用。

### 产品成本结构

DDL 允许五类成本构成及建议价，但当前产品成本页面/提交入口没有形成从分项→总成本→产品成本→报价的可验证闭环。

## 校验（强/弱/缺失）

1. **CM-V01（强）** 产品不存在则不新增报价行。
2. **CM-V02（强）** Approve 修改数量必须大于零。
3. **CM-V03（强）** Approve 修改单价不得小于零；零价仍允许。
4. **CM-V04（强）** 成本可见性由 `Cost Price.view` 控制于产品和报价模板。
5. **CM-V05（弱）** 输入成本不大于零会回退主成本；这不是“成本必须大于零”的阻断。
6. **CM-V06（缺失）** 未见成本为零、负数或异常跳变的服务端拒绝。
7. **CM-V07（缺失）** 未见毛利率小于零或低于阈值的批准阻断。
8. **CM-V08（缺失）** 未见目标毛利率 `<100%` 的新增行校验，公式可能除零或产生负价。
9. **CM-V09（缺失）** 未见成本币种与报价币种一致性校验。
10. **CM-V10（缺失）** 未见成本分项合计必须等于 `total_cost` 的校验。
11. **CM-V11（缺失）** 未见成本变更有效日期、版本、审批与审计原因。
12. **CM-V12（缺失）** 未见运费、税、佣金、折扣是否计入毛利的统一口径校验。

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| `products.cost_price` | SKU 当前主数据成本 |
| `quote_items.cost_price` | 报价采用成本快照 |
| `quote_items.profit` | 单位销售价减单位成本 |
| `quote_items.profit_rate` | 行销售毛利率；新增时作为目标，改价后作为结果 |
| `quote_items.amount` | 数量乘单价；不是毛利额 |
| `quotes.gross_profit` | 报价总额减行成本总额 |
| `total_cost`（页面上下文） | 各行数量乘行成本的合计 |
| `margin_pct` | 报价头毛利占总金额百分比 |
| `product_costing.material_cost` | 预留材料成本 |
| `labor_cost` / `packing_cost` | 预留人工和包装成本 |
| `transport_cost` / `overhead_cost` | 预留运输和制造费用 |
| `product_costing.total_cost` | 预留分解后的总成本，未证明同步产品 |
| `suggested_price` | 预留的成本推导建议价 |
| Finance `total_purchase` | 采购总额聚合，用于另一套全局毛利近似 |
| `stock_qty × cost_price` | Finance 库存价值近似 |

## 状态词汇

| 词汇 | 含义 |
|---|---|
| `Draft` | 可编辑数量和价格、可重算毛利 |
| `Sent` | 人工批准后的报价状态 |
| `High/Medium/Low` | Approve 风险摘要，不是利润审批状态 |
| 成本快照 | 报价行保存的成本 |
| 主数据成本 | 产品当前 `cost_price` |
| 单位利润 | 单价减成本 |
| 报价毛利 | 报价销售总额减报价行成本 |
| 全局毛利近似 | Finance 销售总额减采购总额 |

## 证据表

| # | 观察事实 | 强度 | 只读来源路径 |
|---|---|---|---|
| CM-E01 | 产品保存成本与销售价 | 强 | `runtime/v14/legacy_support.py`、`apps/product/repository.py` |
| CM-E02 | 新增报价行回退产品成本并保存成本快照 | 强 | `apps/quotation/services.py` |
| CM-E03 | 报价总成本和头毛利按行汇总 | 强 | `apps/quotation/services.py`、`apps/quotation/repository.py` |
| CM-E04 | Approve 改价重算单位利润与毛利率 | 强 | `apps/quotation/repository.py` |
| CM-E05 | 成本和毛利展示受 Cost Price 权限保护 | 强 | `templates/quote_detail.html`、`templates/product_detail.html` |
| CM-E06 | 复制报价保留旧成本和盈利字段 | 强 | `apps/quotation/services.py`、`apps/quotation/repository.py` |
| CM-E07 | 产品成本分解有表结构但提交为 redirect stub | 强 | `runtime/v14/legacy_support.py`、`apps/product/router.py`、`services.py` |
| CM-E08 | Finance 另以销售减采购计算聚合毛利 | 强 | `apps/finance/services.py` |
| CM-E09 | 库存估值使用主数据成本 | 强 | `apps/finance/services.py` |
| CM-E10 | 模块报告将 costing/pricing 页面描述为 AI 页面壳 | 中 | `docs/reports/V151E_Volume008_Product_Business_Chain_Extraction_Report.md` |

## UNKNOWN + 已查路径

1. **产品 `cost_price` 的来源（标准、采购末次、移动平均）UNKNOWN。** 已查路径：`apps/product/`、`apps/procurement/`、`apps/inventory/`、Legacy DDL。
2. **采购收货是否在其他入口自动更新产品成本 UNKNOWN。** 已查路径：`apps/procurement/`、`apps/inventory/`、`apps/product/utils.py`。
3. **成本币种及跨币种成本换算 UNKNOWN。** 已查路径：`apps/product/`、`apps/quotation/`、`apps/finance/`、`templates/`。
4. **运费、包装、保险、税、佣金是否进入报价毛利 UNKNOWN。** 已查路径：`product_costing` DDL、报价服务、Finance 服务、打印模板。
5. **负毛利/低毛利的正式批准阈值 UNKNOWN。** 已查路径：`apps/quotation/`、`templates/quote_approve.html`、`docs/reports/V18_Quote_Approve_Gate_Report.md`。
6. **成本历史、有效期和回溯重估规则 UNKNOWN。** 已查路径：`apps/product/history.py`、`product_costing` DDL、`docs/reports/`。
7. **`product_costing.total_cost` 是否应同步 `products.cost_price` UNKNOWN。** 已查路径：`apps/product/router.py`、`services.py`、`repository.py`、DDL。
8. **Finance 的 `total_sales-total_purchase` 是否为管理报表正式毛利口径 UNKNOWN。** 已查路径：`apps/finance/services.py`、`business_modules/finance.md`、`docs/reports/`。

## 只读来源路径

- `H:\Workspace\EZAM_CRM - 9.0\apps\quotation\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\product\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\finance\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\procurement\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\inventory\`
- `H:\Workspace\EZAM_CRM - 9.0\templates\`
- `H:\Workspace\EZAM_CRM - 9.0\business_modules\`
- `H:\Workspace\EZAM_CRM - 9.0\docs\reports\`
- `H:\Workspace\EZAM_CRM - 9.0\runtime\v14\legacy_support.py`
