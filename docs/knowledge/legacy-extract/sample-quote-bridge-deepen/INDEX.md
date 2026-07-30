# Sample / Quote Bridge Deepen — Index

| Topic | Primary page | Evidence strength | Key conclusion |
|---|---|---|---|
| Sample→Quote 创建 | [line_selection.md](line_selection.md) | 强 | 只建 Draft 头，不建行 |
| 产品带入 | [line_selection.md](line_selection.md) | 强负向 | sample.product_id 不自动成为 quote item |
| 空行草稿 | [line_selection.md](line_selection.md) | 强 | total 0、无行的 Draft 可被创建 |
| 转 SO 完整性 | [quote_completeness.md](quote_completeness.md) | 强负向 | 只检查报价存在和未转过 |
| Approve 完整性 | [quote_completeness.md](quote_completeness.md) | 强 | Draft、有行、Human Confirm；但 Convert 不依赖它 |
| 报价版本 | [quote_versioning.md](quote_versioning.md) | 结构强/运行缺失 | `quote_versions` 可读，未见写入工作流 |
| 复制报价 | [quote_versioning.md](quote_versioning.md) | 强 | 新 Draft/新编号，复制快照但不是 version row |
| 重发 | [quote_versioning.md](quote_versioning.md) | 缺失 | Sent 后正式修订与重发未建模 |
| Sample 追溯 | [source_traceability.md](source_traceability.md) | 强 | quotes.sample_id 直接保存 |
| Requirement/Opportunity 传播 | [source_traceability.md](source_traceability.md) | 强但可降级 | 条件列写入、头指针覆盖、link 追加 |

## Reading order

1. [line_selection.md](line_selection.md)：先确认 Sample→Quote 没有自动行选择。
2. [quote_completeness.md](quote_completeness.md)：再核对空行/缺绑定仍可 Convert 的边界。
3. [quote_versioning.md](quote_versioning.md)：区分复制、版本和重发。
4. [source_traceability.md](source_traceability.md)：最后理解多层追溯与静默降级。

## Shared vocabulary

- **Sample→Quote**：以 sample_id 创建报价头的人工动作。
- **空行草稿**：已存在报价头但 `quote_items` 为空。
- **完整性 gate**：进入 Approve 或 Convert 前实际执行的服务端校验。
- **Copy Quote**：新建独立 Draft，不等于版本修订。
- **Quote Version**：`quote_versions` 中的摘要记录结构；活动写入未证实。
- **直接追溯**：`quotes.sample_id/requirement_id/opportunity_id`。
- **快捷指针**：`business_requirements.quote_id` 等单值下游字段。
- **关系链接**：`requirement_links` 多值记录。
- **silent degrade**：缺表、缺列或异常时不阻断主体报价创建。
