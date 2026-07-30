# Analytics / BI / Dashboard — Legacy Knowledge

**Evidence strength:** Strong（分散式 SQL 聚合与业务 dashboard）/ Weak（统一 BI metadata）/ Missing（统一语义层、指标版本和预测治理）  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0`（只读）

## 1. Scope 与证据强度

本文件覆盖客户、报价、销售、交付、收款、财务、库存、采购和 GTFIP dashboard 中的聚合语义，以及 V15.1 BI registry/schema。

Legacy 存在可运行的 dashboard，但多数 KPI 是页面处理器直接查询业务表并即时计算。统一 BI Center 默认关闭，其 dashboard、chart、KPI、analytics、dataset 和 indicator 多为 metadata-only。预测分析、AI insights 的可靠训练数据、评估和版本证据不足，标为 `UNKNOWN`。

## 2. 业务规则（稳定 ID）

| ID | 规则 | 触发/例外 | 证据强度 |
|---|---|---|---|
| ANALYTICS-RULE-001 | Analytics 被定义为只读聚合消费者，不应写业务源表 | 规范意图；实际页面主要为 SELECT | Medium |
| ANALYTICS-RULE-002 | Legacy dashboard KPI 多在请求时直接对业务表 COUNT/SUM/AVG/GROUP BY | 无统一 dataset snapshot | Strong |
| ANALYTICS-RULE-003 | 客户 dashboard：总客户、A级、跟进/开发中、成交/长期、销售额、收款额及 top/recent customers | 客户状态中英混用会影响分组 | Strong |
| ANALYTICS-RULE-004 | 报价 win rate = `Won` 报价数 / 全部报价数；open bucket 含 Draft、Sent、空/null | 报价转订单会写 `已确认`，不计入 Won | Strong |
| ANALYTICS-RULE-005 | 销售 dashboard 按多语言状态集合分 pending/completed/cancelled，并计算订单总额与 collection rate | `received_amount` 与 receipts 聚合可能是不同口径 | Strong |
| ANALYTICS-RULE-006 | 财务 dashboard 的 receivable = SO 总额 − receipts；estimated profit = SO 总额 − purchases | 是粗略跨表估算，不是会计利润/AR ledger | Strong |
| ANALYTICS-RULE-007 | 库存价值 = products.stock_qty × cost_price 的总和 | 不含批次、跌价、在途等调整 | Strong |
| ANALYTICS-RULE-008 | legacy executive dashboard 汇总客户、产品、供应商、采购、报价、订单、收款、交付、库存与资金 | 跨域直接查询，口径未集中治理 | Strong |
| ANALYTICS-RULE-009 | 财务健康分数从 100 起按负现金流、低余额等条件扣分并映射 A-D | 各 dashboard 的启发式可能不同 | Strong |
| ANALYTICS-RULE-010 | GTFIP command center 只统计 status=`active` 订单；按阶段识别生产中、海运、清关，并聚合风险和利润 | delayed 实际以 risk score 阈值代理，不是 delay_days | Strong |
| ANALYTICS-RULE-011 | BI registry 列出 executive/sales/purchase/finance/inventory/customer/supplier/warehouse/AI/custom dashboard | registry 明示 `implemented=False` | Strong metadata |
| ANALYTICS-RULE-012 | analytics registry 预置 sales trend、purchase analysis、finance forecast、AI insights | 全部 `metadata_only` | Strong metadata |
| ANALYTICS-RULE-013 | BI Center 默认关闭；schema 可创建配置与历史表 | 表存在不证明图表执行 | Strong |
| ANALYTICS-RULE-014 | 统一 KPI 定义、维度、币种换算、时间区间、tenant/owner 范围、刷新 SLA 为 `UNKNOWN` | 未找到集中语义合同 | Missing |
| ANALYTICS-RULE-015 | forecast/AI insight 的模型、训练集、准确率、置信区间和审批为 `UNKNOWN` | registry 名称不能证明算法 | Missing |

## 3. 流程

### 3.1 运行 dashboard

1. 用户访问领域 dashboard。
2. 路由可能执行模块权限检查。
3. 处理器直接读取多个业务表。
4. 在内存计算比率、风险等级、健康分或 top-N。
5. 模板呈现 KPI、列表和趋势。

### 3.2 BI metadata

1. schema/registry 声明 dashboard、chart、KPI、analytics、dataset、indicator。
2. 记录默认状态 `metadata_only`、`implemented=0`。
3. 未找到通用查询编译、数据集刷新或指标执行链。

### 3.3 GTFIP command analytics

读取 active GFIP orders → 按 current_stage/risk score 分类 → 聚合国家、利润、风险分布 → 生成固定规则建议。

## 4. 校验（强 / 弱 / 缺失）

| ID | 校验 | 强度 | 说明 |
|---|---|---|---|
| ANALYTICS-VAL-001 | Customer、Quote、Finance、Receipt 等 dashboard 有相应 view 权限门 | 部分强 | profit/delivery/sales 等页面未见同等门禁 |
| ANALYTICS-VAL-002 | 比率分母为 0 时返回 0 | 强 | 多个 dashboard 有显式保护 |
| ANALYTICS-VAL-003 | SQL null 金额按 0 处理 | 强 | 广泛使用 IFNULL |
| ANALYTICS-VAL-004 | dashboard key / KPI key 唯一 | 强（metadata DB） | 不校验指标业务口径 |
| ANALYTICS-VAL-005 | 状态值规范化后再聚合 | 弱/缺失 | 多处硬编码中英状态集合 |
| ANALYTICS-VAL-006 | 币种统一后汇总 | 缺失 | 跨币种报价/订单可直接 SUM |
| ANALYTICS-VAL-007 | tenant、owner、时间范围统一过滤 | 缺失/不一致 | dashboard 多为全表聚合 |
| ANALYTICS-VAL-008 | 指标定义有版本、血缘、质量和对账 | 缺失 | `UNKNOWN` |
| ANALYTICS-VAL-009 | 预测模型通过准确率与漂移门禁 | 缺失 | `UNKNOWN` |

## 5. 数据含义

| 指标/实体 | Legacy 含义 |
|---|---|
| quote win rate | `status='Won'` 数 / 全部 quotes |
| collection rate | receipts 或 received_amount / sales order total，页面间口径可能不同 |
| receivable | 常见简化值 SO 总额 − receipts |
| estimated/gross profit | 常见简化值 sales − purchases，非会计毛利 |
| inventory value | products 当前库存数量 × 成本价 |
| expected cashflow | unpaid AR − unpaid AP |
| financial score/grade | 页面启发式扣分与 A-D 映射 |
| GTFIP production_active | active order 当前阶段属于 production/production_tracking/quality_inspection |
| `bi_*` tables | BI 配置和 metadata/history，不是事实表或已计算指标仓库 |

## 6. 状态词汇

| 词汇 | 含义 |
|---|---|
| `metadata_only` | 仅声明元数据，未实现计算 |
| `implemented=0/False` | registry 明确未实现 |
| `active` | BI dashboard metadata 状态；也用于 GFIP order 过滤，语义不同 |
| A/B/C/D | 启发式财务健康等级 |
| LOW/MEDIUM/HIGH | 页面风险等级 |
| Won/Negotiating/Lost/Draft/Sent/`已确认` | 报价聚合输入词汇，存在不一致 |
| Pending/Open/Delivered/Cancelled 及中文变体 | 订单/交付聚合输入词汇 |
| forecast / insight | analytics 类型；实现证据不足 |

## 7. 只读来源路径

- `H:\Workspace\EZAM_CRM - 9.0\business_modules\analytics.md`
- `H:\Workspace\EZAM_CRM - 9.0\apps\ui_center\domain_dashboards.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\customer\services.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\quotation\services.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\sales\services.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\finance\services.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\finance\treasury_pages.py`
- `H:\Workspace\EZAM_CRM - 9.0\core\bi\types.py`
- `H:\Workspace\EZAM_CRM - 9.0\core\bi\dashboard.py`
- `H:\Workspace\EZAM_CRM - 9.0\core\bi\analytics.py`
- `H:\Workspace\EZAM_CRM - 9.0\database\v151_bi_center_schema.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\bi_center\router.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\bi_center\services.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\bi_center\repository.py`
- `H:\Workspace\EZAM_CRM - 9.0\v15\gtfip\engines\command_center.py`
- `H:\Workspace\EZAM_CRM - 9.0\templates\customer_dashboard.html`
- `H:\Workspace\EZAM_CRM - 9.0\templates\quote_dashboard.html`
- `H:\Workspace\EZAM_CRM - 9.0\templates\sales_dashboard.html`
- `H:\Workspace\EZAM_CRM - 9.0\templates\finance_dashboard.html`

**Negative search:** 已查统一 metric/KPI semantic layer、currency normalization、dataset refresh、lineage、forecast model/evaluation/drift；未找到足够运行证据。
