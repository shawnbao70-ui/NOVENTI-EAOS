# Legacy Knowledge Extract — Sample Pack

**Source system:** `H:\Workspace\EZAM_CRM - 9.0`（只读）  
**Mode:** Legacy 业务知识抽取；不继承 Legacy 架构  
**Writable home:** 仅 `docs/knowledge/legacy-extract/sample/**`  
**Verified:** 2026-07-23

## Purpose

记录样品与客户、需求、商机、报价交界处可由 Legacy 证据支持的业务语义。Legacy 中可确认的是“客户收样/样品分析/样品转报价/样品入库”；独立的样品申请、审批、发样闭环未找到实现证据，详见 [sample.md](sample.md)。

## Hard boundaries

- 只抽取规则、流程、校验、数据含义和状态词汇，不复制源码。
- `Sample360`、AI participant 等实现形态不是 EAOS 架构约束。
- 不把“收样”“入库物化”误写成“向客户发样”。
- 缺失能力保持 `UNKNOWN`，并保留已查路径。

## Package contents

| File | Purpose |
|---|---|
| [INDEX.md](INDEX.md) | 入口、证据强度与交界导航 |
| [sample.md](sample.md) | 样品业务规则、流程、校验、数据语义与缺口 |
| [outbound.md](outbound.md) | 样品出库、发样、派送证据及缺口 |
| [pod.md](pod.md) | 样品签收、POD、回执证据及缺口 |
