# Legacy Knowledge Extract — Intelligence Pack

**Source system:** `H:\Workspace\EZAM_CRM - 9.0`（只读）  
**Mode:** Legacy 业务知识抽取；不继承 Legacy 架构  
**Writable home:** 仅 `docs/knowledge/legacy-extract/intel/**`  
**Verified:** 2026-07-23

## Purpose

记录 Legacy 中 Analytics/BI/dashboard、Report Center 以及 Production runtime 的真实业务语义，并区分运行聚合、元数据注册、占位页面、预测/演示数据和规范意图。

## Hard boundaries

- dashboard 数值必须追溯到查询或计算，不能把 UI 标签当业务事实。
- BI/Report registry 的 `implemented=0` / `metadata_only` 不得提升为已实现分析。
- Report Center 目录不等于报表执行引擎。
- Production 规范文件与样品模块不等于生产运行时；仅记录 GTFIP 可执行证据。
- 缺失证据写 `UNKNOWN` 并列已查路径。

## Package contents

| File | Purpose |
|---|---|
| [INDEX.md](INDEX.md) | 模块入口与证据强度 |
| [analytics.md](analytics.md) | Analytics、BI、dashboard 业务含义与缺口 |
| [reports.md](reports.md) | Report Center 目录、触发与财务/销售交界 |
| [production_runtime.md](production_runtime.md) | Production 运行时落地、流程与缺口 |
