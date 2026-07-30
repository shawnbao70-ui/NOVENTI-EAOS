# 库存逆向与 Ship 对称性（Inventory Reverse Paths）— Legacy Knowledge

**Evidence strength:** Strong for Ship and Manual Adjustment; strong negative for a symmetric DO Ship reversal  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0` (read-only)

## 1. Scope 与证据强度

本页以 `DO Ship` 为正向基线，核对 Reopen、Inventory Adjust、scan Move、damage write-off、transfer 和可能的 Return 是否能对称撤销。可证结论：没有一条命令按原 Ship ledger 逐行反向、恢复两套库存并重置防重状态。人工正数 Adjust 可以改变数量，但没有原 DO/RMA 外键、行匹配、质量处置或防重复，故不能称为对称 reversal。

## 2. Business Rules

| ID | Rule / observed boundary | Consequence |
|----|--------------------------|-------------|
| IRP-R1 | Ship 仅允许 open-stage DO | 状态硬门 |
| IRP-R2 | shipped/complete stage 再 Ship 被拒 | 状态幂等 |
| IRP-R3 | 任一同 DO remark ledger 会触发 already_shipped | 文本 ledger 防重 |
| IRP-R4 | Ship 按 DO line 顺序处理正数量产品 | 非正数行被跳过 |
| IRP-R5 | Ship 要求 inventory row 存在/可建立 | 缺失时失败 |
| IRP-R6 | 每行要求 on-hand >= qty | 防负库存 |
| IRP-R7 | Ship 同时减少 inventory.stock_qty | 第一事实源 |
| IRP-R8 | Ship 同时减少 products.stock_qty | 镜像双写 |
| IRP-R9 | Ship 写 `DO Ship` ledger，qty 为负 | 正向出库审计 |
| IRP-R10 | 全部行后写 DO Shipped 并 commit | 正常同批提交 |
| IRP-R11 | 循环先改前序行再校验后序行 | 后序失败前已有未提交变更 |
| IRP-R12 | Ship 错误路径未见显式 rollback | 请求结束清理 UNKNOWN |
| IRP-R13 | Complete 只改 DO/SO 状态 | 不再动库存 |
| IRP-R14 | Reopen 只改 DO/SO 状态 | 不恢复库存/ledger |
| IRP-R15 | Reopen 保留 Ship ledger，故再次 Ship 被阻断 | 非对称 |
| IRP-R16 | Adjust 接受正/负 delta | 可人工加回或扣减 |
| IRP-R17 | Adjust 同步 inventory、products 和 ledger 后 commit | 通用数量动作 |
| IRP-R18 | Adjust 要求 delta 非零且结果不为负 | 数量级校验 |
| IRP-R19 | trans_type 是用户可选文本类型 | 不强制 Return |
| IRP-R20 | remark 是自由文本 | 不形成原交易 FK |
| IRP-R21 | scan Move 将正/负量标为 Transfer In/Out | 仍作用同一 inventory row |
| IRP-R22 | Damage Write-off 是通用调整标签 | 不等于客户退货或 ship reversal |
| IRP-R23 | 未见 Customer Return/RMA Receipt ledger 类型的受控 writer | 逆向业务语义缺失 |
| IRP-R24 | 未见按原 Ship quantity 自动生成反向 ledger | 无一键对称撤销 |
| IRP-R25 | 未见批次、序列、仓位或 disposition 级回退 | 无法确认退回原物 |
| IRP-R26 | EAOS 不得把正数 Adjust 解释为已授权 Return | 只证明库存数量变化 |

## 3. Process

### 3.1 正向 Ship

1. 校验 DO 存在、stage=open、无同 DO ledger。
2. 遍历 DO items。
3. 对每个正数量行确认 inventory 与余量。
4. 更新 inventory，更新 product 镜像，写负数 DO Ship ledger。
5. 更新 DO Shipped，commit。

### 3.2 Reopen 后

1. Complete DO 可改回 Open。
2. 原库存与 ledger 保持。
3. 再 Ship 因 ledger count>0 被拒。
4. 用户只能另行 Adjust；该动作不会解除 ledger 防重。

### 3.3 人工 Adjust

1. Inventory edit 权限进入 POST form。
2. 校验非零 delta 与新余额非负。
3. 更新 inventory 和 product mirror。
4. 写自由 trans_type/remark ledger，commit。
5. 不回写 DO、SO、AR、Receipt 或 TC。

## 4. Symmetry Matrix

| Ship fact | Required symmetric reversal | Observed capability | Strength |
|-----------|-----------------------------|---------------------|----------|
| inventory −qty | inventory +same qty | Manual Adjust 可加，但不绑定 source | Weak |
| products −qty | products +same qty | Adjust 镜像可加 | Weak |
| ledger DO Ship −qty | reverse ledger +qty with link | 无专用 writer | Missing |
| DO Shipped/Complete | revert lifecycle | Reopen→Open | Strong status-only |
| Ship dedupe marker | cancel/reversal-aware marker | 原 ledger 永留 | Missing |
| exact lines/qty | derive from original ledger | 人工输入 | Missing |
| warehouse/lot/serial | restore original dimensions | 未建模 | Missing |
| quality disposition | quarantine/restock/scrap | 未建模 | Missing |

## 5. Validation

| ID | Validation | Strength |
|----|------------|----------|
| IRP-V1 | Ship DO 必须存在且 open | Hard |
| IRP-V2 | 同 DO 不得已有 Ship ledger | Hard query |
| IRP-V3 | 每行 qty>0 且 product 有效 | Partial；无效行跳过 |
| IRP-V4 | on-hand 足够 | Hard per line |
| IRP-V5 | Adjust delta 非零 | Hard |
| IRP-V6 | Adjust 后不得负库存 | Hard |
| IRP-V7 | Adjust 需 Inventory edit | Hard |
| IRP-V8 | Reversal 必须引用原 DO Ship ledger | Missing |
| IRP-V9 | Reversal qty 不得超过原出库/未退量 | Missing |
| IRP-V10 | 同一 Ship 只能 reverse 一次 | Missing |
| IRP-V11 | 退回库存必须隔离/检验 | Missing |
| IRP-V12 | Ship 任意行失败必须 rollback 所有前序行 | UNKNOWN/no explicit rollback |
| IRP-V13 | 镜像与 ledger 必须对账 | Missing |
| IRP-V14 | Reversal 必须与 AR/Receipt/TC 协调 | Missing |

## 6. Data Semantics

| Entity / field | Honest Legacy meaning |
|----------------|-----------------------|
| `inventory.stock_qty` | 运行 on-hand |
| `products.stock_qty` | 产品镜像 on-hand |
| `inventory_ledger.trans_type='DO Ship'` | 正向出库事件 |
| ledger qty negative | Ship 扣减量 |
| ledger balance | 当前行处理后的库存余额 |
| ledger remark `DO-{do_no}` | Ship 防重文本键 |
| DO Open | 可 Ship 的状态 |
| DO Shipped | 库存动作已提交标签 |
| DO Complete | 交付确认标签 |
| Reopen | status-only DO/SO 重开 |
| Manual Adjustment | 通用 delta |
| Cycle Count | 调整标签 |
| Damage Write-off | 调整标签，不是 return |
| Transfer In/Out | scan/adjust 标签，未证明跨仓双边 |
| positive delta | 数量增加，不自动等于退库 |
| reverse source ID | 未建模 |
| returned qty | 未建模 |
| disposition/location/lot/serial | 未建模或未进入该链 |

## 7. State Vocabulary

| Term | Meaning |
|------|---------|
| open | Ship 前状态；Reopen 后也可出现 |
| shipped | DO Ship 正向动作已完成 |
| complete | Delivered/已完成归一阶段 |
| already_shipped | 状态或 ledger 防重失败 |
| Manual Adjustment | 通用数量动作 |
| Reversed/Returned/Quarantined | 未见运行库存状态 |

## 8. UNKNOWN 与已查路径

| UNKNOWN | 已查路径 |
|---------|----------|
| Ship 中途 return 后未提交变更如何 rollback | inventory service/repository、database context/middleware |
| 生产是否有 ledger unique/index 防并发双 Ship | runtime DDL/database migrations |
| 并发两个 Ship 请求是否可都通过 ledger guard | inventory service/locking/tests |
| Return Receipt 专用 trans_type 是否在私有部署 | inventory writers/templates/runtime data seeds |
| 库间 Transfer 是否有 source/destination 双边表 | inventory scan/services/schema |
| lot/serial/warehouse/location 维度的退回规则 | inventory schemas/GFIP/GTFIP |
| 人工 Adjust 是否要求审计 actor | router/service/repository/log |
| Reopen 后合法重发如何重置防重 | ship/reopen/ledger paths |
| Inventory Adjust 如何与 Credit/AR 联动 | inventory/finance/service |

## 9. Evidence Table

| Read-only path | Evidence |
|----------------|----------|
| `apps/inventory/services.py` | Ship、Adjust、Complete、Reopen |
| `apps/inventory/repository.py` | 双写、ledger 和 DO status SQL |
| `apps/inventory/router.py` | Adjust/Reopen 权限与 HTTP methods |
| `apps/inventory/validator.py` | adjustment qty 校验 |
| `templates/adjust_inventory.html` | trans types/free remark |
| `templates/delivery_order_detail.html` | status-only Reopen 明示 |
| `runtime/v14/legacy_support.py` | inventory/ledger/DO schemas |
| `database/upgrade_patch.py` | inventory schema 补丁 |
| `apps/sales/services.py` | DO creation 与 SO states |
| `apps/procurement/services.py` | PO Receipt 正向入库对照 |
| `v15/gfip/` | 平行 shipment/warehouse 语义 |
| `v15/gtfip/` | 平行 trade flow，不接主 reversal |
| `business_modules/inventory.md` | Inventory authority |
| `docs/reports/Business_Strong_A003_Delivery_Report.md` | Ship/Reopen 验收 |
| `docs/reports/V18_P3B_Warehouse_Completion_Report.md` | scan/adjust 边界 |
| `docs/knowledge/legacy-extract/fulfillment-deepen/returns_reversal.md` | EAOS 只读交叉引用 |

**Root:** `H:\Workspace\EZAM_CRM - 9.0\` + paths above（最后一项为 EAOS 只读交叉引用）。
