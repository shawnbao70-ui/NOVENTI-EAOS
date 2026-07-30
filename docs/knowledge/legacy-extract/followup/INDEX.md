# Follow-up Knowledge Extract — Index

**Source root:** `H:\Workspace\EZAM_CRM - 9.0`（只读） · **Verified:** 2026-07-23

| Topic | File | Evidence strength |
|---|---|---|
| 客户跟进、Customer360 装配与时间线 | [followup.md](followup.md) | Strong：四字段记录、客户聚合、计数/展示；Weak/Missing：权限、状态、提醒、完成闭环 |

## Assembly summary

- Customer detail 按客户读取跟进并按 id 倒序。
- Customer360 基础区展示跟进总数，Followups tab 展示日期、内容、下一计划及新增表单。
- Timeline 把跟进、报价、订单分组拼接；不是全局按时间排序的统一活动流。
- 另有 `customer_360()` helper 装配 customer/followups/quotes/orders/receipts/samples，但主详情服务还装配交付、余额与生命周期扩展。

## Honesty note

Legacy 跟进表没有状态、负责人、渠道、提醒时间、完成时间或商机/需求外键。相关产品规则均为 `UNKNOWN`，不得从 Customer360 展示推导出来。
