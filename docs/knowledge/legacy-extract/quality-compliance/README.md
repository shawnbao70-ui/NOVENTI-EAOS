# Legacy Knowledge Extract — Quality & Compliance Pack

**Source:** `H:\Workspace\EZAM_CRM - 9.0` (read-only)  
**Writable home:** `docs/knowledge/legacy-extract/quality-compliance/**`  
**Verified:** 2026-07-23

## Scope

本包提炼 Legacy 中与样品质检、采购来料、成品检验、不合格处置、合规证书、批次追溯、客诉和 RMA 相关的可证知识。对没有业务实现的领域，记录已查路径、相邻事实与诚实缺口，不从页面名称、文档类型、KPI 占位或图谱词汇反推运行能力。

## Modules

- [Quality Check](quality_check.md) — 样品评分、来料/成品检验交界与缺口
- [Nonconformance](nonconformance.md) — NCR、让步、隔离、返工和报废缺口
- [Compliance Records](compliance_records.md) — 认证要求、证书文档与追溯边界
- [Claim / RMA](claim_rma.md) — 客诉、退货授权、保修与售后品质缺口
- 汇总见 [INDEX.md](INDEX.md)

## Evidence posture

- 样品五维质量评价有活动数据表与写入路径，但缺少评分范围、检验员、时间、规格和质量 gate。
- GTFIP 有贸易订单级 `planned` 质检记录、默认 AQL/85 分/checklist 表面，但未见结果写入、失败转移或放行 gate。
- PO Receive 与 Sample Materialize 会直接增加 SKU 汇总库存；未发现来料待检、质量放行或隔离 bucket。
- NCR、让步、偏差、返工、报废、RMA 和客户退货没有可确认的业务主表或闭环。
- Certificate、QC Report、Inspection Report 是 NDE 文档类型/通用模板；不证明证书签发或检验执行。
- GFIP/GTFIP 的贸易文档行可标记 `ready/verified`，但未校验证书内容、签发方、有效期或批次适用性。
- Document Center 的附件、版本、分享、归档多为未实现或 metadata-only。
- Customer Graph 的 complaint 和 QC/customer-service workspace KPI 是词汇、demo 或占位，不是业务台账。

## Hard boundaries

- `Received`、`Stocked`、`PO Receipt`、`Sample Receipt` 不是质量合格或放行状态。
- `inventory.location` 不是隔离控制；审批 `Rejected` 不是质量 Reject；工程 `REWORK` 不是产品返工。
- Warranty 报价条款不是保修资格引擎。
- GTFIP 默认 85 分不是实测质量结论；GFIP/GTFIP `ready/verified` 不是外部证书验真。
- DO Reopen 只重开状态，通用 Inventory Adjust 也不构成 RMA/销售退货闭环。
- 需求追溯、库存来源备注和文档打印日志都不等于批次谱系或证书审计。
- 不从 AI 建议、Graph demo、模板壳或未接线 KPI 生成质量事实。
