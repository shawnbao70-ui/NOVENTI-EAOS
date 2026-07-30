# Legacy Knowledge Extract — Sample / Quote Bridge Deepen

**Source:** `H:\Workspace\EZAM_CRM - 9.0`（只读）  
**Mode:** 样品到报价、完整性、版本与追溯均衡深挖  
**Verified:** 2026-07-23

## Purpose

本包深化四个容易被“Create Quote”名称掩盖的事实：

- Sample→Quote 只建立 Draft 报价头，不选择或生成报价行；
- 转 SO 只硬校验报价存在和未重复，报价完整性多数未被强制；
- `quote_versions` 有表和读取能力，但未形成活动修订/重发工作流；
- Sample/Requirement/Opportunity 追溯依赖条件列和 best-effort helper，失败可静默降级。

缺证据一律标注 `UNKNOWN + 已查路径`。本包不修改 sample、quotation、opportunity、CRM 或任何邻包正文。

## Contents

| File | Focus |
|---|---|
| [INDEX.md](INDEX.md) | 主题、证据强度与阅读顺序 |
| [line_selection.md](line_selection.md) | 样品转报价的行选择、带入、跳过和空行草稿 |
| [quote_completeness.md](quote_completeness.md) | 转 SO 前报价完整性强/弱/缺失矩阵 |
| [quote_versioning.md](quote_versioning.md) | 报价版本、修订、复制与重发缺口 |
| [source_traceability.md](source_traceability.md) | Sample/Requirement/Opportunity→Quote 追溯与静默降级 |

## Cross-package boundary

- 商机/需求深化：[`../opportunity-requirement-deepen/README.md`](../opportunity-requirement-deepen/README.md)
- 样品深化：[`../sample-deepen/README.md`](../sample-deepen/README.md)
- 报价深化：[`../quotation-deepen/README.md`](../quotation-deepen/README.md)

本包只深化桥接规则，不复制上述正文。
