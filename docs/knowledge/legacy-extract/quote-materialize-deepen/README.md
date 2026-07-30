# Legacy Knowledge Extract — Quote Materialize Deepen

**Source:** `H:\Workspace\EZAM_CRM - 9.0`（只读）  
**Mode:** 样品产品到报价行、空草稿转单、校验差异与重发深化  
**Verified:** 2026-07-23

## Purpose

本包在既有权威页基础上聚焦四个断点：

- `sample.product_id` 绑定不会自动 materialize 为 `quote_items`；
- Sample→Quote 可形成空行 Draft（头金额未显式写入、依赖默认），Convert 又不检查行；
- Quote Approve 与 Convert SO 的服务端校验集合明显不同；
- Sent 后没有受控修订、重发或作废工作流；Quote360 仍可增删行，Copy/状态覆盖也不能冒充版本治理。

## Contents

| File | Focus |
|---|---|
| [INDEX.md](INDEX.md) | 主题与证据索引 |
| [sample_product_to_line.md](sample_product_to_line.md) | sample.product_id→quote_items 是否带入 |
| [empty_draft_convert.md](empty_draft_convert.md) | 空行 Draft→空 SO 的完整证据链 |
| [convert_completeness_matrix.md](convert_completeness_matrix.md) | Approve vs Convert 校验对照 |
| [revise_resend.md](revise_resend.md) | Sent 后修订、重发、作废缺口 |

## Authority boundary

- Sample/Quote 桥接权威：[`../sample-quote-bridge-deepen/README.md`](../sample-quote-bridge-deepen/README.md)
- Quotation 深化权威：[`../quotation-deepen/README.md`](../quotation-deepen/README.md)

本包只补充物化断点与校验对照，不重写上述正文。
