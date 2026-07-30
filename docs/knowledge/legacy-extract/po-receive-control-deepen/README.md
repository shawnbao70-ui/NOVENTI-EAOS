# PO 收货控制深化包（po-receive-control-deepen）

**Source:** `H:\Workspace\EZAM_CRM - 9.0`（永久只读）  
**Verified:** 2026-07-23  
**Evidence strength:** Strong for approve/receive gate、GR 事实形态、全量收货；Strong-negative for 部分/短收/超收与来料质检处置

## Purpose

本包核验 Legacy 采购收货控制四件事，只记录可执行事实：

1. 收货前审批是否强制（Approve 是否 Receive 前置）
2. 收货头/行实体有无，以及与 PO 行的关系
3. 部分收货 / 短收 / 超收数量模型是否存在
4. 收货质检处置 vs 直接入库可用库存

禁止把 UI 引导、DDL 空壳、质量工作台占位 KPI 解释为强门禁。

## Authority boundary

| 邻包 | 角色 | 本包做法 |
|---|---|---|
| [`../procurement-receipt-deepen/`](../procurement-receipt-deepen/) | 采购收货基础权威（生命周期、过账、数量、入库） | 交叉引用，深化控制缺口，不重写权威 |
| [`../quality-compliance/`](../quality-compliance/) | 质量合规权威（样品评分、非符合、合规记录） | 交叉引用，仅判定与 PO Receive 是否汇合 |

本包不修改邻包正文；不开 CRUD；不碰 Brain/Twin。

## Contents

| File | Focus | Stable ID |
|---|---|---|
| [`INDEX.md`](INDEX.md) | 主题索引与交叉引用 | — |
| [`mandatory_approve_before_receive.md`](mandatory_approve_before_receive.md) | 收货前审批是否强制 | `MAP-*` |
| [`receipt_header_lines.md`](receipt_header_lines.md) | GRN 头/行实体与 PO 追溯 | `RHL-*` |
| [`partial_short_over.md`](partial_short_over.md) | 部分 / 短收 / 超收数量模型 | `PSO-*` |
| [`quality_disposition_on_receive.md`](quality_disposition_on_receive.md) | 来料质检处置 vs 直接入库 | `QDR-*` |

## Core verdict

- `Draft` / `Open` / `Pending` 均归入可收货 `open` family → **Approve 不是 Receive 强制前置**。
- 活动收货直接读 `purchase_items`，三写 `inventory.stock_qty` / `products.stock_qty` / `inventory_ledger`；**不写** `purchase_receipts`。
- **无**采购收货行、**无** ordered/received/remaining 三元组、**无** partial/short/over/tolerance。
- **无** inspection / quarantine / hold / release / reject 处置；收货即增加单一可用库存。

## Mandatory search coverage（本包已查）

| 路径 | 结果摘要 |
|---|---|
| `apps/procurement/` | Receive/Approve 主权威；`PO_OPEN`、`receive_purchase`、ledger 判重 |
| `apps/purchase/` | **不存在**（采购在 `apps/procurement/`） |
| `apps/inventory/` | 扫码收货委托同一 service；单一 `stock_qty` |
| `templates/`（purchase*） | Draft/Open/Pending 显示 Receive；Approve 才有 human_confirm |
| `business_modules/procurement.md` | goods-receipt contract 仍为待定义意图 |
| `docs/reports/`（A-004 / A-010） | Draft 可测通收货；无质检步骤 |
| `runtime/v14/legacy_support.py` | `purchase_receipts` / `inventory` / `inventory_ledger` DDL |
| `v15/`（ai brief / ux / gtfip） | brief 引导 Receive；QC KPI 占位；GTFIP 与 PO 隔离 |
| `apps/approval/` | Approval Center 不接 PO Receive gate |
| `apps/finance/` | 开票不强制 PO Received |
| `apps/sample/` | 样品评分与 materialize 不接 PO Receive |
| `core/` | 未见 PO Receive / GRN / quarantine 控制实现（检索超时边界记 UNKNOWN） |
