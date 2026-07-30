# Legacy Knowledge Extract — Quotation Deepen

**Source:** `H:\Workspace\EZAM_CRM - 9.0`（只读）  
**Mode:** 报价业务知识均衡深挖；不继承 Legacy 架构  
**Verified:** 2026-07-23

## Purpose

本包深化报价从创建、人工发布、洽谈、成交/丢单到转销售订单的业务含义，并把三个容易混淆的边界拆开：

- Quote Approve 是本地 `Draft → Sent` 人工发布门，不等于 Approval Center 审批记录；
- “改状态”与“转销售订单”是两个动作，转单成功又把报价写成中文 `已确认`；
- 报价行保存价格/成本快照，但价格来源、折扣、币种和汇率的完整规则属于 pricing-advanced。

缺证据一律标注 `UNKNOWN + 已查路径`。本文包不改写 `crm/quotation.md`、`sales/`、`pricing-advanced/` 或治理正文。

## Contents

| File | Focus |
|---|---|
| [INDEX.md](INDEX.md) | 主题、证据强度与阅读顺序 |
| [quote_lifecycle.md](quote_lifecycle.md) | Draft / Sent / Negotiating / Won / Lost / 已确认混合生命周期 |
| [quote_approve.md](quote_approve.md) | Quote Approve、人工确认与中心审批边界 |
| [quote_convert_gates.md](quote_convert_gates.md) | 转 SO 门槛、双实现差异和 Sales 交界 |
| [quote_lines_pricing.md](quote_lines_pricing.md) | 行项目、成本/价格快照及计价边界 |

## Cross-package boundary

- 基线报价页：[`../crm/quotation.md`](../crm/quotation.md)
- 横向审批治理：[`../governance/approval.md`](../governance/approval.md)
- 销售订单权威：[`../sales/sales_order.md`](../sales/sales_order.md)
- 报价计价专题：[`../pricing-advanced/INDEX.md`](../pricing-advanced/INDEX.md)

本包只作证据深化和交叉索引，不复制上述正文。
