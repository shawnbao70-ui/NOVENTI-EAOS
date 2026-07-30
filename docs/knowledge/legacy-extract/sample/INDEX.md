# Sample Knowledge Extract — Index

**Source root:** `H:\Workspace\EZAM_CRM - 9.0`（只读） · **Verified:** 2026-07-23

| Topic | File | Evidence strength |
|---|---|---|
| 样品创建、分析、客户/需求/商机/报价交界 | [sample.md](sample.md) | Strong：客户收样、分析、转报价；Medium：需求/商机追溯；Missing：申请、审批、向客户发样 |
| 样品出库、发样、派送 | [outbound.md](outbound.md) | Missing：样品 outbound；Strong adjacent：Sample Receipt 入库与普通销售发货 |
| 样品签收、POD、回执 | [pod.md](pod.md) | Missing：样品 POD；Strong adjacent：普通 DO 明示未采集 POD；Weak：打印回执空白字段 |

## Boundary map

`Customer → Opportunity → Requirement → Sample → Quotation`

- 客户是 Legacy 样品创建时唯一硬输入。
- 需求、商机是后加的可选追溯字段，存在双向同步的尽力而为逻辑。
- 样品可创建 Draft 报价并传递客户及可用的需求/商机追溯。
- “样品入库物化”是库存收货，不是发样。

## Honesty note

已查实现未发现独立的 sample request、approval、dispatch/shipment 实体或状态机；相应结论在正文中标为 `UNKNOWN`，不得据此推导产品 CRUD。
