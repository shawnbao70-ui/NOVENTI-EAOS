# Legacy Knowledge Extract — Engagement Pack

**Source:** `H:\Workspace\EZAM_CRM - 9.0` (read-only)  
**Writable home:** `docs/knowledge/legacy-extract/engagement/**`  
**Verified:** 2026-07-23

## Scope

本包提炼客户触达与体验相关的 Legacy 知识：Marketing、Brand Center、售后/技术服务，以及面向用户的 AI 顾问表面。内容只描述可观察到的规则、流程、校验、数据语义和诚实缺口，不复制源码。

## Modules

- [Marketing](marketing.md)
- [Brand Center](brand.md)
- [Service / After-sales](service.md)
- [AI Advisory Surfaces](ai_advisory.md)
- 汇总见 [INDEX.md](INDEX.md)

## Hard boundaries

- Marketing 的八个渠道是架构注册项，默认 `not_configured`，不是已连接发送通道。
- Brand Center 的活动主线是 Legacy `brand_profiles`；V15.1 `platform_brand`、`company_profiles`、`brand_assets` 是默认未启用的并行基础层。
- Service app 明示为 planned；现有 `tickets` API 脚手架与 TechnicalService360 shadow 不能当作成熟售后闭环。
- AI Decision Center 的 V15.1 表主要保存 metadata；Legacy 决策页包含静态分数与建议，不能当成实时推理结果。
- 所有 AI 输出仅可视为建议、分析、解释、草稿或导航；**不等于 Brain execute、Twin authorize 或 Cap→grant**，本包也不建议开放这些能力。
