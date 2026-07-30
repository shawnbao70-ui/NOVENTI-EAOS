# Legacy Knowledge Extract — Commercial Contract Lifecycle

**Source system:** `H:\Workspace\EZAM_CRM - 9.0`（只读）  
**Mode:** Legacy 业务知识抽取；不继承 Legacy 架构  
**Writable home:** 仅 `docs/knowledge/legacy-extract/contract-lifecycle/**`  
**Verified:** 2026-07-23

## Purpose

核查 Legacy 是否存在超越“合同文档标签”的商业合同实体与生命周期，并将运营实现、通用文档能力、贸易文档词汇、概念阶段和演示占位严格分开。

## Hard boundaries

- Document Center 的 `contract` module key 不等于商业合同主数据。
- `sales_contract` / `purchase_contract` 文档类型不等于已实现合同生命周期。
- AI task、风险卡片、完整性清单不证明合同业务记录存在。
- 缺失字段、流程与校验均标 `UNKNOWN`，不得据此生成 CRUD。

## Package contents

| File | Purpose |
|---|---|
| [INDEX.md](INDEX.md) | 证据分层与入口 |
| [contract.md](contract.md) | 商业合同生命周期规则、流程、校验、数据语义与缺口 |
