# Requirement Knowledge Extract — Index

**Source root:** `H:\Workspace\EZAM_CRM - 9.0`（只读） · **Verified:** 2026-07-23

| Topic | File | Evidence strength |
|---|---|---|
| 需求实体、商机 1:N、追溯字段、报价链接 | [requirement.md](requirement.md) | Strong：实体/关系/字段/直连报价；Medium：跨表双向同步；Missing：完整状态转换与反馈持久化 |

## Relationship summary

- 一个商机可拥有多个需求：`business_requirements.opportunity_id` + 按商机查询。
- 商机保存 `requirement_count` 缓存；创建关联需求时递增，未见删除/改挂后的对账。
- 需求可通过 `sample_id`、`quote_id`、`sales_order_id` 保存快捷指针。
- `requirement_links` 保存可扩展的实体链接与角色。
- 从需求创建报价时，报价获得 `requirement_id`，并可继承 `opportunity_id`。

## Honesty note

Legacy 同时使用直接外键和链接表，且多处以表/列存在性检查后静默跳过。正文将这些描述为“尽力而为追溯”，不将其提升为可靠一致性保证。
