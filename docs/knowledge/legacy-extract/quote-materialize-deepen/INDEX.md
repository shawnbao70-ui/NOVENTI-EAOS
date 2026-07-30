# Quote Materialize Deepen — Index

| Topic | Primary page | Evidence strength | Key conclusion |
|---|---|---|---|
| sample.product_id | [sample_product_to_line.md](sample_product_to_line.md) | 强负向 | 只服务绑定/入库，不自动建报价行 |
| 行物化 | [sample_product_to_line.md](sample_product_to_line.md) | 强 | 必须后续人工 add_quote_item |
| 空行 Draft | [empty_draft_convert.md](empty_draft_convert.md) | 强 | Sample→Quote 只插头 |
| 空 SO | [empty_draft_convert.md](empty_draft_convert.md) | 强 | Convert 复制空集合仍创建 SO 头 |
| Approve vs Convert | [convert_completeness_matrix.md](convert_completeness_matrix.md) | 强 | Approve 有 Draft/行/人工门，Convert 无 |
| Sent 修订 | [revise_resend.md](revise_resend.md) | 强缺口 | Approve 面只读，但 Quote360 可增删行且无 revision flow |
| 重发 | [revise_resend.md](revise_resend.md) | 缺失 | send_time 未使用，无 resend event |
| 作废 | [revise_resend.md](revise_resend.md) | 缺失/弱 | 无 Void/Cancelled；状态可直接覆盖 |

## Reading order

1. [sample_product_to_line.md](sample_product_to_line.md)
2. [empty_draft_convert.md](empty_draft_convert.md)
3. [convert_completeness_matrix.md](convert_completeness_matrix.md)
4. [revise_resend.md](revise_resend.md)

## Shared vocabulary

- **materialize to line**：把样品绑定产品实际写成 quote item。
- **空行 Draft**：有 quotes 头、无 quote_items。
- **空 SO**：有 sales_orders 头、无 sales_order_items。
- **Approve gate**：Draft→Sent 的 Type A 人工门。
- **Convert gate**：Quote→SO 的存在/防重复门。
- **revision/resend/void**：Legacy 未形成受控闭环的修订、重发、作废动作。
