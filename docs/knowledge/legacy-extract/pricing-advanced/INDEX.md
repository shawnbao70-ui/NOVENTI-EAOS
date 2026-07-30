# Pricing Advanced — Index

| Topic | Primary page | Evidence strength | Key conclusion |
|---|---|---|---|
| 产品主数据价 | [price_lists.md](price_lists.md) | 强 | `cost_price` / `sale_price` 是 SKU 主数据字段 |
| 客户历史价 | [price_lists.md](price_lists.md) | 强 | 是最近报价参考，不是客户合同价目表 |
| 等级/国家价 | [price_lists.md](price_lists.md) | 中（结构）/弱（运行） | `product_price_rules` 有结构，但未接报价主链 |
| 成本快照 | [cost_margin.md](cost_margin.md) | 强 | 报价行保存采用成本，复制时原样保留 |
| 报价毛利 | [cost_margin.md](cost_margin.md) | 强 | 行与头均可计算/持久化；可见性受 Cost Price 权限约束 |
| 成本构成 | [cost_margin.md](cost_margin.md) | 中（结构）/弱（运行） | 成本分解表存在，提交入口是 redirect stub |
| 新增行计价 | [quote_pricing_engine.md](quote_pricing_engine.md) | 强 | 成本 ÷ (1 − 目标毛利率)，再乘数量 |
| Approve 改价 | [quote_pricing_engine.md](quote_pricing_engine.md) | 强 | Draft 可改数量/单价并重算，人工确认后 Sent |
| 折扣计价 | [quote_pricing_engine.md](quote_pricing_engine.md) | 弱 | 独立试算有折扣；报价主链没有折扣字段 |
| 报价币种 | [currency_price.md](currency_price.md) | 强 | 币种/汇率在报价头，行字段隐含继承 |
| FX 换算 | [currency_price.md](currency_price.md) | 中/弱 | 独立试算执行除法；报价主链不产本位币金额 |
| 币种价规则 | [currency_price.md](currency_price.md) | 中（结构）/弱（运行） | 多维价格规则未发现活动匹配器 |

## Reading order

1. [price_lists.md](price_lists.md)：先辨明“价”的来源与权威等级。
2. [cost_margin.md](cost_margin.md)：再确认成本与毛利口径。
3. [quote_pricing_engine.md](quote_pricing_engine.md)：进入报价行实际运行计算。
4. [currency_price.md](currency_price.md)：最后处理币种标签、汇率和换算边界。

## Shared vocabulary

- **主数据价**：产品记录上的 `cost_price` / `sale_price`。
- **成交/报价行价**：`quote_items.price`。
- **客户历史价**：客户既往报价行形成的只读参考。
- **等级价结构**：`product_price_rules.customer_level` 等字段；不等于运行价目表。
- **报价毛利率**：通常为 `(price - cost) / price`。
- **成本加成率**：独立试算中的 `cost × (1 + rate)`；不得与毛利率混称。
