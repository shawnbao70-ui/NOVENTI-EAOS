# Intelligence Knowledge Extract — Index

**Source root:** `H:\Workspace\EZAM_CRM - 9.0`（只读） · **Verified:** 2026-07-23

| Module | File | Evidence strength |
|---|---|---|
| Analytics / BI / Dashboard | [analytics.md](analytics.md) | Strong：分散式实时 SQL KPI；Weak：BI registry/schema；Missing：统一指标治理、语义层与可靠预测 |
| Report Center | [reports.md](reports.md) | Strong：目录/分类/历史读取与统计 API；Weak：V15.1 registry；Missing：通用执行、调度、分发落地 |
| Production Runtime | [production_runtime.md](production_runtime.md) | Medium/Strong：GTFIP 订单级进度 runtime；Missing：制造订单、BOM、工序、物料消耗与车间执行 |

## Evidence model

- **Operational:** 实际查询、持久化、API 或页面装配。
- **Metadata-only:** registry/schema 声明但 `implemented=0` 或未接执行器。
- **Placeholder:** 固定文案、保留图表、演示风险/预测。
- **UNKNOWN:** 已检索但未找到可执行证据。

## Cross-module boundary

Analytics 和 reports 读取销售、财务、客户、库存等业务数据，但不取得这些源数据的所有权。GTFIP Production 记录全球履约订单的工厂进度摘要，不等于完整制造域。
