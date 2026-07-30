# 不合格、让步与隔离（Nonconformance）— Legacy Knowledge

**Evidence strength:** Absent for NCR/concession/quarantine lifecycle; adjacent sample risk and stock controls only  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0` (read-only)

---

## 1. Scope 与证据强度

全库针对 `nonconformance`、`NCR`、`concession`、`deviation`、`waiver`、`quarantine`、`quality hold`、`scrap`、`rework` 的业务检索未发现可确认的质量不合格闭环。出现的 `Rejected` 主要属于审批，`REWORK` 属于工程 sprint 判定，均不能当作产品不合格状态。

可确认的相邻能力只有：

- 样品材料分析中的自由文本 `risk_level`、`quality_grade`；
- 样品质量评价中的人工分数和 `overall_grade`；
- 库存数量、位置和人工调整；
- QC workspace 中仍为 `—` 的 defects/holds/releases KPI；
- GTFIP 中默认 `planned` 的贸易质检记录，但无 fail/hold/NCR 转移；
- 采购收货和样品物化都会直接增加可用库存。

因此本模块主要记录**缺失规则和危险交界**，不把库存 location、审批 Reject 或样品 risk 文本虚构为 NCR/隔离实现。

---

## 2. Business Rules

| ID | Rule / observed boundary | Evidence / consequence |
|----|--------------------------|------------------------|
| NCR-R1 | Legacy 没有可确认的 NCR 主记录、编号或生命周期 | 全库业务搜索无命中 |
| NCR-R2 | `risk_level` 只是样品材料分析文本 | 不创建不合格记录，也不触发隔离 |
| NCR-R3 | `overall_grade` 只是样品综合等级文本 | 未映射 Accepted/Rejected 或处置 |
| NCR-R4 | 多次质量评价以追加记录保存，最新 ID 被展示 | 无“原判作废/复判/关闭 NCR”语义 |
| NCR-R5 | 采购收货直接把正数量写入库存 | 没有不合格数量或待判数量分流 |
| NCR-R6 | 样品物化不检查质量等级 | 低分/空评价样品仍可成为库存 |
| NCR-R7 | inventory.location 是通用库位文本 | 不能推断该库位具有隔离、冻结或权限效果 |
| NCR-R8 | Inventory adjust 可改变数量并写 ledger | 没有原因码证明调整是报废、返工或质量扣减 |
| NCR-R9 | 库存总量未拆分 available/inspection/blocked/quarantine/scrap | 所有数量共享一个 `stock_qty` |
| NCR-R10 | 审批 `Rejected` 是审批结论 | 不代表物料/产品不合格 |
| NCR-R11 | 工程 sprint 的 `REWORK` 是软件交付词汇 | 不代表产品返工 |
| NCR-R12 | QC workspace 的 defects/holds/releases 只是占位 KPI | 不提供不合格事实源 |
| NCR-R13 | NDE Inspection Report 可以打印一般报告壳 | 不创建 NCR，也不执行让步审批 |
| NCR-R14 | 当前系统不能可靠区分退供应商、返工、报废、让步接收和偏差放行 | 这些处置实体/状态均未建模 |
| NCR-R15 | EAOS 迁移不得从备注关键词自动生成已批准让步 | 缺少批准人、依据、范围和有效期 |
| NCR-R16 | GTFIP `inspection_status='planned'` 只表示计划检验 | 未见 failed/hold/released 状态写入或 NCR 生成 |
| NCR-R17 | GTFIP 默认 85 分与“acceptable”文案不得解释为处置批准 | 它们是空值 fallback，不是实测或 MRB 结论 |
| NCR-R18 | 产品 `Healthy/Low Stock/Critical` 是库存阈值 | 不是缺陷严重度、NCR 状态或放行判定 |

---

## 3. Process

### 3.1 可观察的“发现”相邻流程

1. 用户可录入样品材料风险、质量等级、五项分数和综合等级。
2. 系统保存这些文本/分值。
3. 系统不比较规格、不自动判不合格、不生成 NCR。
4. 用户仍可把样品物化库存或把采购订单收货入库。

### 3.2 库存相邻流程

1. PO Receive 或 Sample Receipt 增加单一 `stock_qty`。
2. Inventory Adjust 可由人工改变数量并写库存流水。
3. Location 可被编辑，但只是文本元数据。
4. 未见把不合格数量移入冻结 bucket、阻止出库或等待 MRB 的逻辑。

### 3.3 缺失的标准 NCR 流程

未观察到：发现偏差 → 创建 NCR → 关联批次/供应商/客户 → 隔离 → 原因分析 → 处置评审 → 返工/报废/退货/让步 → 复验 → 放行/关闭 → CAPA。

### 3.4 让步放行边界

未观察到 deviation/concession/waiver 记录、批准矩阵、数量范围、客户授权、有效期或对库存状态的自动释放。

### 3.5 GTFIP 交界

GTFIP 订单会初始化一条计划质检记录，但当前读取引擎只展示默认计划、分数和 checklist。未观察到“检验失败 → hold → NCR → 处置 → release”的写入链，因此该记录不能填补 NCR/MRB 缺口。

---

## 4. Validation

| ID | Validation | Strength | Detail |
|----|------------|----------|--------|
| NCR-V1 | NCR 编号唯一且不可重用 | Not modeled | 无 NCR 实体 |
| NCR-V2 | 不合格必须引用产品、批次、数量和来源 | Not modeled | 无批次/不合格数量 |
| NCR-V3 | 缺陷代码、严重度和检测点须受控 | Missing | 只有自由文本风险/备注 |
| NCR-V4 | 隔离数量不得参与可用库存或出库 | Missing | 单一 stock_qty |
| NCR-V5 | 处置数量之和必须等于不合格数量 | Not modeled | 无处置行 |
| NCR-V6 | 让步必须有授权人、理由、有效期和适用范围 | Missing | 无让步实体 |
| NCR-V7 | 返工后必须复验 | Missing | 无返工/复验状态 |
| NCR-V8 | 报废必须产生受控库存扣减和财务影响 | Missing | 普通 Adjust 无质量原因码 |
| NCR-V9 | 退供应商必须关联 PO/receipt/supplier | Missing | 无采购退货链 |
| NCR-V10 | NCR 关闭前必须完成处置和证据 | Missing | 无关闭状态机 |
| NCR-V11 | 只有授权角色可 release hold | Missing | 无 hold/release 命令 |
| NCR-V12 | 审批 Reject 不得映射为质量 Reject | Semantic guard | 两者属于不同上下文 |
| NCR-V13 | GTFIP 检验失败必须生成或引用 NCR | Missing | 未见失败状态或桥接 |
| NCR-V14 | 默认质量分不得作为让步依据 | Semantic guard | 85 是 fallback 值 |

---

## 5. Data Semantics

| Concept / field | Honest Legacy meaning |
|-----------------|-----------------------|
| `sample_material_analysis.risk_level` | 样品材料风险描述文本 |
| `quality_grade` | 样品材料质量等级文本 |
| `sample_quality_assessment.overall_grade` | 样品人工综合等级 |
| `remark` | 非结构化备注；不是缺陷明细 |
| `inventory.stock_qty` | 单一现存数量，无质量 bucket |
| `inventory.location` | 普通位置文本，无隔离执行语义 |
| `inventory_ledger.trans_type` | 库存动作类型；现有主线是 PO Receipt、Sample Receipt、DO Ship、Adjust |
| `inventory_ledger.remark` | 来源引用/备注；不是 NCR 外键 |
| `PO Receipt` | 收货过账，不等于来料接受 |
| `Sample Receipt` | 样品物化，不等于质量放行 |
| `Rejected` | 在可见实现中主要是审批状态 |
| `REWORK` | V15 sprint 工程判定，不是物料返工 |
| defects/holds/releases KPI | 空占位，不是聚合事实 |
| `gtfip_quality.inspection_status` | 贸易质检阶段槽位；只证实默认 `planned` |
| `gtfip_quality.quality_score` | 贸易质检分值；API 可回退 85 |
| 产品 `stock_status` | 库存数量健康度，不是质量状态 |
| NCR / concession / quarantine | UNKNOWN / 未发现业务实体 |

---

## 6. State Vocabulary

| Value | Meaning / caveat |
|-------|------------------|
| `Received` | 采购已入库存 |
| `Stocked` | 样品已物化 |
| `Rejected` | 审批拒绝，非质量判退 |
| `PASS` / `REWORK` | 工程 sprint 状态，非产品质量 |
| `Open` | 采购可收货；不是 NCR Open |
| `Adjust` | 库存调整动作；原因未结构化 |
| `planned` | GTFIP 计划检验；不是 NCR Open 或质量放行 |
| `Healthy` / `Low Stock` / `Critical` | 库存数量预警，非质量严重度 |
| `Hold`, `Released`, `Quarantined`, `Scrapped`, `Reworked`, `Concession Approved` | 仅期待词汇；活动业务状态 UNKNOWN |

---

## 7. UNKNOWN 与已查路径

| UNKNOWN | Paths searched |
|---------|----------------|
| 是否存在 NCR 表、路由或隐藏模块 | full-repo `NCR/nonconformance/non-conformance` search；`apps/**`, `business_modules/**`, `runtime/v14/legacy_support.py` |
| 是否存在隔离仓/冻结库存 | `apps/inventory/**`, inventory templates, warehouse schemas, `quarantine/hold/isolation` search |
| 是否存在让步/偏差审批 | `apps/approval/**`, governance approval knowledge, `concession/deviation/waiver` search |
| 是否存在返工、报废和复验 | production/sample/inventory paths, `rework/scrap/reinspection` search |
| 是否存在供应商退货处置 | `apps/procurement/**`, purchase templates, `purchase_return/return supplier` search |
| 是否存在客户退回后的质量判定 | `apps/service/**`, inventory/sales paths, `RMA/return/complaint` search |
| 样品低等级是否有隐式阻断 | `apps/sample/services.py`, router, templates, materialize and quote conversion paths |
| Inspection Report 是否会创建 NCR | `document/nde_engine.py`, inspection templates, print/document reports |
| GTFIP 检验失败是否会创建 NCR 或库存 hold | `v15/gtfip/engines/quality.py`, `v15/gtfip/repository.py`, inventory services；未找到桥接 |

---

## 8. Evidence Table

| Read-only path | Evidence |
|----------------|----------|
| `runtime/v14/legacy_support.py` | 样品风险/等级/评分和库存表结构；无 NCR 主表证据 |
| `apps/sample/services.py` | 质量记录只保存，不产生 NCR；物化无质量 gate |
| `apps/sample/router.py` | 质量与风险自由输入入口 |
| `apps/procurement/services.py` | PO 收货直接增加库存 |
| `apps/inventory/repository.py` | 单一库存数量与通用 location/ledger |
| `templates/inventory_detail.html` | 仅数量、安全库存、位置和调整 |
| `templates/purchase360.html` | PO 尚无 live quality score |
| `v15/ux/registry.py` | QC workspace 只有导航定义 |
| `v15/ux/todays_work.py` | defects/holds/releases 均为 `—` |
| `v15/gtfip/repository.py` | 贸易质检记录只证实默认 `planned` |
| `v15/gtfip/engines/quality.py` | 默认计划、85 分与 checklist，不含 NCR 处置 |
| `apps/product/services.py` | 库存健康状态按数量阈值派生 |
| `document/nde_engine.py` | Inspection/QC Report 是文档类型，不是 NCR |
| `templates/documents/inspection_report.html` | 通用报告壳 |
| `business_modules/inventory.md` | Inventory 模块未定义质量 bucket |
| `business_modules/production.md` | Production 边界未定义 NCR/MRB |
| `docs/reports/Business_Strong_A005_Sample_Quote_Report.md` | Sample Receipt 只验证库存链 |
| `docs/reports/Business_Strong_A010_Purchase_Ops_Report.md` | Receive 双写不含质检 |
| `docs/reports/Business_Strong_A018_Inventory_Ops_Report.md` | 调整操作边界，无隔离/放行能力声明 |

**Full-repo negative search terms:** `NCR`, `nonconformance`, `concession`, `waiver`, `quarantine`, `quality hold`, `scrap`, `rework`.  
**Root:** `H:\Workspace\EZAM_CRM - 9.0\` + paths above.
