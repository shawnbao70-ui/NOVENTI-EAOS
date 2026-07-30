# Legacy Knowledge Extract — Object360

**Source system:** `H:\Workspace\EZAM_CRM - 9.0`（只读）  
**Mode:** Legacy 业务知识抽取；不继承 Legacy 架构  
**Writable home:** 仅 `docs/knowledge/legacy-extract/object360/**`  
**Verified:** 2026-07-23

## Purpose

记录 Legacy 的 Customer360、Sample360 运行装配和 history/audit 表象，区分业务对象详情、展示型聚合、并行 Object360 context、对象日志与平台审计。

## Hard boundaries

- “360”表示围绕对象装配多个读取结果，不自动意味着统一对象存储、统一事件模型或完整生命周期。
- Customer360 与 followup/CRM 仅交叉引用，不复制既有知识包。
- Sample360 的旧页面、并行 runtime bundle 与未接线 shadow/metadata 必须分层描述。
- history、timeline、audit log、技术 operation log 不可互相替代。
- 本包不形成 EAOS Audit、Kernel 或 Object360 架构定论。
- 缺证据写 `UNKNOWN + 已查路径`。

## Package contents

| File | Purpose |
|---|---|
| [INDEX.md](INDEX.md) | 主题入口、证据层级与交叉引用 |
| [customer360.md](customer360.md) | Customer360 字段、区块、装配与业务交界 |
| [sample360.md](sample360.md) | Sample360 页面/runtime 观察与缺口 |
| [history_audit.md](history_audit.md) | 对象 history、timeline 与审计轨迹的业务含义和缺口 |
