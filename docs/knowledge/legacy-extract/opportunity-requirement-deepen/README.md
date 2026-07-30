# 商机—需求深化包

## 目的

本包抽取 Legacy 中 `business_opportunities` 与 `business_requirements` 的实际业务知识，重点分离“生命周期声明”与“可执行实现”，并说明需求向样品、报价传播时的条件写入和静默降级。

既有 [`../crm/opportunity.md`](../crm/opportunity.md) 仍是商机权威概览；本包只深化来源、编号、状态实现、1:N 需求创建、缓存计数及追溯一致性，不改写其正文。

## 内容

- [`opportunity_sources.md`](opportunity_sources.md)：来源类型、人工创建、编号和客户/负责人绑定。
- [`opportunity_lifecycle.md`](opportunity_lifecycle.md)：状态词汇、声明链和实际状态变更缺口。
- [`requirement_create.md`](requirement_create.md)：需求创建、商机 1:N 与 `requirement_count`。
- [`requirement_trace.md`](requirement_trace.md)：需求到样品、报价、订单的字段传播及静默降级。
- [`INDEX.md`](INDEX.md)：主题、规则前缀与来源索引。

## 证据口径

- **强**：路由、repository、schema、模板之间可互证的实际路径。
- **中**：查询投影、报告或声明常量支持，但无完整写路径。
- **弱/缺失**：仅 UI 约束、异常吞掉、列可选，或全局搜索未见执行入口。
- 不把 Customer Opportunity Mining 或 Enterprise Opportunity Engine 的洞察卡当作已持久化销售商机。
- 不把 `LIFECYCLE_STAGES`、状态枚举或页面文案当作状态机实现。
- 缺失证据统一记录为 `UNKNOWN + 已查路径`。

## 只读边界

证据根目录：`H:\Workspace\EZAM_CRM - 9.0`。

重点检查：

- `v15/business_lifecycle/`
- `database/business_lifecycle_schema.py`
- `apps/customer/`
- `apps/sample/`
- `apps/quotation/`
- `templates/business/` 与相关 customer/sample/quote 模板
- `business_modules/`
- `docs/reports/`

本包不主张 Legacy 架构是 EAOS 的目标架构，也不复制源码。
