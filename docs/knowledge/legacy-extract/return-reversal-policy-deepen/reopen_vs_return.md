# DO Reopen 与退货授权边界（Reopen vs Return）— Legacy Knowledge

**Evidence strength:** Strong for status-only Reopen; strong negative for an operational RMA/return authorization lifecycle  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0` (read-only)

## 1. Scope 与证据强度

本页区分已交付 DO 的 Reopen 与销售退货/RMA。Reopen 只把 DO 从 complete 阶段改回 Open，并把关联 SO 改为 Open；它不恢复库存、不撤销 `DO Ship` ledger、不取消 AR、不退款、不冲销佣金，也不建立退货授权。RMA/客诉证据主要停留在 planned Service、graph 词汇和文档类型。

交叉引用 `../fulfillment-deepen/returns_reversal.md` 与 `../quality-compliance/claim_rma.md`。

## 2. Business Rules

| ID | Rule / observed boundary | Consequence |
|----|--------------------------|-------------|
| RVR-R1 | Reopen 只允许 complete-stage DO | 非 complete 被拒 |
| RVR-R2 | Reopen 要求 Delivery Orders edit | 模块级权限门 |
| RVR-R3 | Reopen 使用 GET mutation + browser confirm | 无服务端确认令牌 |
| RVR-R4 | Reopen 把 DO 状态改为 Open | 是状态重开 |
| RVR-R5 | 有关联 SO 时同步改为 Open | 不撤销 SO 或重建行 |
| RVR-R6 | Reopen 明确不恢复 inventory | 页面和服务均声明 status-only |
| RVR-R7 | Reopen 不恢复 products.stock_qty 镜像 | 双写仍保持已出库结果 |
| RVR-R8 | Reopen 不写反向 inventory ledger | 原 DO Ship 永久保留 |
| RVR-R9 | 原 DO Ship ledger 会阻断再次 Ship | Reopen 后不能直接重发 |
| RVR-R10 | Reopen 不检查或撤销 `ar_records` | 已 Post AR 可继续存在 |
| RVR-R11 | Reopen 不检查/删除 receipts | 已收款不变化 |
| RVR-R12 | Reopen 不改变 Pending TC commission | 佣金不冲销 |
| RVR-R13 | Inventory Adjust 可人工正数加回 | 不绑定 DO/RMA/客户 |
| RVR-R14 | Manual Adjustment 不等于 Return Receipt | 缺授权、质检、处置 |
| RVR-R15 | Service app 是 planned/read-oriented scaffold | 未证实 claim/RMA CRUD |
| RVR-R16 | complaint/returns workspace 或 graph 词汇不证明运行流程 | KPI 为占位或 demo |
| RVR-R17 | Credit Note 文档类型不等于入账贷项 | 无金额冲销调用链 |
| RVR-R18 | 无 serial/lot 时无法核验退回件属于原交付 | 产品级追溯不足 |
| RVR-R19 | 未见退货授权号、原因、数量、处置或关闭状态机 | RMA 主实体缺失 |
| RVR-R20 | AI/Graph/Service 建议不能批准退货、退款或换货 | 只读/建议边界 |
| RVR-R21 | EAOS 不得把 Open 状态解释为“货已退回” | 库存/财务事实未反向 |

## 3. Process

### 3.1 已实现 Reopen

1. 读取 DO 并归一化 stage。
2. 校验 Delivery Orders edit 与 complete stage。
3. 写 DO Open。
4. 写关联 SO Open。
5. 一次 commit 后返回 DO 详情。
6. 原库存、ledger、AR、Receipt、TC 保持不变。

### 3.2 人工数量补偿

1. 用户另行打开 Inventory Adjust。
2. 输入正数 delta、自由 trans_type/remark。
3. 更新 inventory、products 镜像和 ledger。
4. 该动作不形成 Customer Return、RMA Receipt 或可售性判定。

### 3.3 缺失闭环

`Claim → RMA Request → Authorization → Return Transit → Receipt → Quality/Quarantine → Restock/Repair/Scrap → Credit/Refund/Replacement → Close` 未观察到活动主链。

## 4. Validation

| ID | Validation | Strength |
|----|------------|----------|
| RVR-V1 | DO 必须存在 | Hard |
| RVR-V2 | DO 必须处于 complete stage | Hard |
| RVR-V3 | 调用者需 Delivery Orders edit | Hard |
| RVR-V4 | Reopen 前确认库存是否回补 | Missing；固定不回补 |
| RVR-V5 | Reopen 前检查 AR/Receipt/TC | Missing |
| RVR-V6 | Return 必须有唯一 RMA number | Not modeled |
| RVR-V7 | Return 必须引用 customer/SO/DO/line/qty | Missing |
| RVR-V8 | Return 必须验证保修和授权 | Missing |
| RVR-V9 | 退回件必须 serial/lot 对应原交付 | Impossible/not modeled |
| RVR-V10 | Return receipt 后必须隔离/质检 | Missing |
| RVR-V11 | Refund/Credit/Replacement 必须受权限审批 | Missing |
| RVR-V12 | Return quantities/stock/financial postings 必须守恒 | Missing |
| RVR-V13 | 重复 return/reopen 必须幂等 | Reopen 状态门部分；RMA missing |

## 5. Data Semantics

| Entity / field | Honest Legacy meaning |
|----------------|-----------------------|
| `delivery_orders.status` | Reopen 的直接状态字段 |
| complete stage | Reopen 唯一允许起点 |
| DO Open | 状态重新开放，不是退货收货 |
| `sales_orders.status=Open` | Reopen 的同步标签 |
| `inventory.stock_qty` | Reopen 不改 |
| `products.stock_qty` | Reopen 不改的镜像 |
| `inventory_ledger` DO Ship | 原出库事件，Reopen 保留 |
| ledger remark `DO-{do_no}` | Ship 防重关联文本 |
| Manual Adjustment | 通用数量补偿 |
| adjustment remark | 自由文本，不是 RMA FK |
| `ar_records` | DO 可产生的应收，Reopen 不撤销 |
| `receipts` | SO 收款事实，Reopen 不退款 |
| `tc_ledger` Pending | Convert 佣金快照，Reopen 不冲销 |
| `CREDIT_NOTE` | 文档 registry 类型 |
| complaint | graph/service 词汇，不是 RMA 主表 |
| RMA/return order | 未建模 |
| disposition | 可售/隔离/维修/报废未建模 |

## 6. State Vocabulary

| State / term | Meaning |
|--------------|---------|
| Delivered / 已完成 | complete stage，可 Reopen |
| Open | Reopen 后 DO/SO 标签 |
| already_shipped | 原 Ship ledger 存在，阻断再次 Ship |
| Manual Adjustment | 通用补偿，不是 Return Received |
| Requested/Authorized/Received/Inspected | 期望 RMA 状态，Legacy 未证实 |
| Refunded/Replaced/Rejected/Closed | 期望结案状态，Legacy 未证实 |

## 7. UNKNOWN 与已查路径

| UNKNOWN | 已查路径 |
|---------|----------|
| 销售退货/RMA 主表和编号 | sales/inventory/service/runtime DDL |
| 退货授权与审批规则 | service/approval/sales/templates |
| 退回件关联原 DO line/serial/lot | inventory/delivery schemas |
| 退货质检、隔离、维修、报废 | inventory/quality/sample/service |
| Credit Note/退款的业务命令 | finance/document/NDE/templates |
| Reopen 后 AR/Receipt/TC 如何处置 | inventory/finance/sales/commission |
| 重开后合法重新 Ship 的策略 | ship/reopen service与 ledger guard |
| complaint graph 是否接真实写入 | enterprise graph/service paths |
| Service ticket/RMA 的生产 DDL | apps/service、runtime/database migrations |

## 8. Evidence Table

| Read-only path | Evidence |
|----------------|----------|
| `apps/inventory/services.py` | Reopen status-only、Ship guard |
| `apps/inventory/repository.py` | DO status 与 ledger 查询 |
| `apps/inventory/router.py` | Reopen GET 权限入口 |
| `templates/delivery_order_detail.html` | stock-not-restored 明示 |
| `templates/adjust_inventory.html` | 手工补偿字段 |
| `apps/service/README.md` | Service planned 边界 |
| `apps/service/repository.py` | ticket scaffold |
| `core/object360/technical_service/` | 只读 shadow |
| `v15/enterprise_business_graph/` | complaint 词汇/demo |
| `runtime/v14/legacy_support.py` | 缺 RMA 表、Credit Note registry |
| `document/nde_engine.py` | Credit Note 文档能力 |
| `apps/finance/services.py` | Receipt/AR 无 Reopen 联动 |
| `apps/sales/services.py` | SO 状态与 commission 边界 |
| `docs/reports/Business_Strong_A003_Delivery_Report.md` | Reopen 不自动恢复 |
| `docs/reports/V18_SO_DO_Invoice_TypeA_Report.md` | AR accrual 边界 |
| `docs/knowledge/legacy-extract/fulfillment-deepen/returns_reversal.md` | EAOS 只读交叉引用 |
| `docs/knowledge/legacy-extract/quality-compliance/claim_rma.md` | EAOS 只读交叉引用 |

**Root:** `H:\Workspace\EZAM_CRM - 9.0\` + paths above（最后两项为 EAOS 只读交叉引用）。
