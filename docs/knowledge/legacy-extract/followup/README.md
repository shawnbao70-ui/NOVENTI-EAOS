# Legacy Knowledge Extract — Follow-up Pack

**Source system:** `H:\Workspace\EZAM_CRM - 9.0`（只读）  
**Mode:** Legacy 业务知识抽取；不继承 Legacy 架构  
**Writable home:** 仅 `docs/knowledge/legacy-extract/followup/**`  
**Verified:** 2026-07-23

## Purpose

记录客户跟进记录及其在 Customer360 中的装配、计数、展示与时间线规则，并明确权限、状态、提醒和闭环能力的缺口。

## Hard boundaries

- 跟进是客户附属记录，不等于商机、任务或活动引擎。
- Customer360 是读取与装配证据，不作为 EAOS UI/架构模板。
- AI “follow-up” 文案不证明自动创建跟进记录。
- 未找到的状态、负责人、提醒和完成规则保持 `UNKNOWN`。

## Package contents

| File | Purpose |
|---|---|
| [INDEX.md](INDEX.md) | 入口、证据强度与 Customer360 装配摘要 |
| [followup.md](followup.md) | 跟进业务规则、流程、校验、数据语义与缺口 |
