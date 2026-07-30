# Legacy Knowledge Extract — Sample Deepen

**Source:** `H:\Workspace\EZAM_CRM - 9.0`（只读）  
**Mode:** Legacy 业务知识均衡深挖；不继承 Legacy 架构  
**Verified:** 2026-07-23

## Purpose

本包深化 Legacy“客户来样”链：收样创建、图片与测量、Sample360 分析块、绑定目录产品后入库，以及从样品创建报价的追溯。

权威概览仍为 [`../sample/sample.md`](../sample/sample.md)。本包不重写该页，而是展开字段、调用边界、校验缺口与运行/壳层差异。缺证据一律记录为 `UNKNOWN + 已查路径`。

## Contents

| File | Focus |
|---|---|
| [INDEX.md](INDEX.md) | 主题、证据强度与阅读顺序 |
| [sample_intake.md](sample_intake.md) | 收样创建、客户绑定、编号与 New |
| [sample_analysis.md](sample_analysis.md) | 测量、图片与 Sample360 分析数据 |
| [sample_stocking.md](sample_stocking.md) | 产品绑定、Sample Receipt 与 Stocked |
| [sample_to_quote.md](sample_to_quote.md) | Draft 报价、商业头与追溯字段 |

## Boundary

- 不覆盖样品外发/POD：见 [`../sample/outbound.md`](../sample/outbound.md)、[`../sample/pod.md`](../sample/pod.md)。
- 不把 Sample360 并行 enrichment、AI participant 或静态能力文案当作自动分析事实。
- 不把 `sample_requirements` 与 `business_requirements` 混为同一实体。
