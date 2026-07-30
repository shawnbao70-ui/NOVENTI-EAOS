# Legacy Knowledge Extract — Requirement Pack

**Source system:** `H:\Workspace\EZAM_CRM - 9.0`（只读）  
**Mode:** Legacy 业务知识抽取；不继承 Legacy 架构  
**Writable home:** 仅 `docs/knowledge/legacy-extract/requirement/**`  
**Verified:** 2026-07-23

## Purpose

记录业务需求实体、商机一对多关系、下游追溯字段及报价链接规则，供 EAOS 在 Knowledge Driven 原则下重写能力。

## Hard boundaries

- 业务需求 `business_requirements` 与样品附属表 `sample_requirements` 是不同概念。
- Legacy 的静默降级、可选列和缓存计数不是目标架构。
- 状态常量只证明词汇存在，不证明完整转换已实现。
- 只抽取语义，不复制 Legacy 源码或 CRUD 设计。

## Package contents

| File | Purpose |
|---|---|
| [INDEX.md](INDEX.md) | 入口、证据强度与关系摘要 |
| [requirement.md](requirement.md) | 需求规则、流程、校验、追溯字段与报价链接 |
