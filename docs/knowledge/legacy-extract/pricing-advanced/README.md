# Legacy Knowledge Extract — Pricing Advanced

**Source:** `H:\Workspace\EZAM_CRM - 9.0`（只读）  
**Mode:** Legacy 业务知识均衡深挖；不继承 Legacy 架构  
**Verified:** 2026-07-23

## Purpose

本包深挖产品基准价、客户历史价、等级价格结构、成本/毛利可见性、报价行计价和多币种价格交界。重点区分：

- 实际报价运行公式与独立试算页面；
- 产品主数据价、客户历史参考价与真正价目表；
- 成本/毛利持久字段与页面重算；
- 币种标签、汇率快照与真实换算；
- DDL/metadata 预留与已接入运行主链。

缺证据一律使用 `UNKNOWN + 已查路径`。

## Contents

| File | Focus |
|---|---|
| [INDEX.md](INDEX.md) | 主题、强度、交叉引用 |
| [price_lists.md](price_lists.md) | 价目表、客户价、等级价 |
| [cost_margin.md](cost_margin.md) | 成本、毛利、利润可见性 |
| [quote_pricing_engine.md](quote_pricing_engine.md) | 报价行定价、汇总与批准重算 |
| [currency_price.md](currency_price.md) | 币种、汇率和价格换算交界 |

## Cross-package boundary

- 价格公式总览：[`../finance/pricing.md`](../finance/pricing.md)
- 折扣与商业条件：[`../commercial-terms/discount_rules.md`](../commercial-terms/discount_rules.md)
- 币种与汇率主语义：[`../locale-commerce/currency.md`](../locale-commerce/currency.md)

本包只深化，不复制上述正文。
