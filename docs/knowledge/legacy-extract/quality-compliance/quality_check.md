# 质检、来料与成品检验（Quality Check）— Legacy Knowledge

**Evidence strength:** Medium for sample scoring; weak/absent for incoming and finished-goods inspection  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0` (read-only)

---

## 1. Scope 与证据强度

Legacy 中唯一可确认的业务质量记录是 Sample Center 的样品测量、材料分析与五维质量评分。它们是样品级、人工录入、追加式记录，并不构成通用 QMS。

- **样品质检：中等证据。** 有表、POST 写入、读取最近一条记录及 Sample360 上下文。
- **来料检验：弱/缺失。** PO Receive 直接把采购数量增加到库存并记 `PO Receipt`，未见检验批、抽样、接收/拒收数量或待检区。
- **成品检验：缺失。** 未发现生产完工检验、放行或出货前 QC gate。
- **贸易质检：中弱证据。** GTFIP 为每个贸易订单建立 `gtfip_quality` 记录，默认 `planned`，GET 引擎可返回 AQL 2.5 文案、五项 checklist 和默认 85 分；未见通过/失败/冻结的写入状态机。
- **报表表面：弱。** NDE 注册 `QC Report`、`Inspection Report`，但 Inspection 模板只组合通用产品表与时间线，未证明检验结果来源。
- **工作区表面：占位。** QC workspace 的 inspections/defects/holds/releases KPI 都显示 `—`，主要动作导航到 GTFIP，不是活动质检台账。

---

## 2. 业务规则

| ID | 规则描述 | Evidence / honesty boundary |
|----|----------|-----------------------------|
| QC-R1 | 样品质量评价按外观、精度、强度、耐久和包装五个分数记录 | `sample_quality_assessment` 明确存在 |
| QC-R2 | 综合等级由人工提交并原样保存 | 未见由五项分数自动计算 |
| QC-R3 | 每次保存都会新增一条评价，Sample360 只取 ID 最新的一条 | 没有版本号、作废或修订关系 |
| QC-R4 | 样品测量与质量评价是不同记录 | 长宽厚重、节距、齿数、材料、硬度不自动形成判定 |
| QC-R5 | 材料分析可记录材料构成、硬度、密度、温度范围、质量等级和风险等级 | 字段均为人工文本，未见规格上下限 |
| QC-R6 | 供应商匹配中的 `quality_score` 是样品供应商候选评分 | 不等同供应商来料合格率或现场检验结果 |
| QC-R7 | 质量评价写入路由未观察到模块权限 gate | 不能推定任何登录用户均应有权限；这是权限缺口 |
| QC-R8 | 样品绑定产品并物化库存时，只检查样品存在、产品绑定、数量、库存行和幂等 | 不检查质量评价、综合等级或认证要求 |
| QC-R9 | 样品物化成功后产生 `Sample Receipt` 台账并把样品状态改为 `Stocked` | `Stocked` 只证明已入库存，不证明检验合格 |
| QC-R10 | PO 收货要求采购单处于 Open、有行且未重复收货 | 不执行进料检验，正数量行直接入可用库存 |
| QC-R11 | PO 收货按订购数量入库，未区分实收、合格、拒收或短缺数量 | 所以 `Received` 不是质量接受结论 |
| QC-R12 | 库存主记录只保存 SKU、数量、安全库存和位置 | 没有质量状态、待检数量或隔离数量 |
| QC-R13 | QC/Inspection 文档类型是可选打印壳 | 文档类型存在不等于检验业务已执行 |
| QC-R14 | 出货流程不应从现有库存数量推断“已通过成品检验” | Delivery/ship 证据只关注库存与人工确认 |
| QC-R15 | 质量 UI 中的 `—` KPI 表示没有接入事实数据 | 不得把 workspace 注册解释为运行中的 QMS |
| QC-R16 | GTFIP 订单初始化时新增一条 `inspection_status='planned'` 的质量记录 | 是贸易订单旁路元数据，不是采购来料检验 |
| QC-R17 | GTFIP Quality GET 在质量分为空/零时回退 85，并生成“可接受”分析文案 | 默认值不是实测结果或质量放行 |
| QC-R18 | GTFIP checklist 固定为外观、尺寸、功能、包装和标签合规五项 | 未见逐项结果、缺陷或签名持久化 |
| QC-R19 | `report_json`、`photos_json` 是结构槽位 | 未发现活动上传/审核或检验结论写入路径 |
| QC-R20 | 产品 `Healthy/Low Stock/Critical` 只按库存数量计算 | 严禁映射为质量合格、不合格或严重度 |

---

## 3. Process

### 3.1 样品质量记录

1. 建立样品并记录照片、测量或客户要求。
2. 人工提交材料分析；系统新增一条材料分析记录。
3. 人工提交五项质量分数、综合等级与备注；系统新增一条质量评价。
4. Sample360 查询各类记录，其中质量评价只取最新一条。
5. 评价不会自动推进样品状态，也不会自动阻断报价或库存物化。

### 3.2 样品物化库存

1. 人工把样品绑定到产品。
2. 人工触发物化并输入正数量。
3. 系统以 `Sample Receipt` 增加 inventory 和 product 两处库存，并写 inventory ledger。
4. 系统将样品状态改为 `Stocked`。
5. 流程没有读取 `sample_quality_assessment` 或 `certification_requirement`。

### 3.3 采购来料

1. PO 经人工批准从 Draft 进入 Open。
2. 用户点击 Receive Goods。
3. 系统检查 PO 状态、行和幂等台账。
4. 对每个正数量行直接增加库存并写 `PO Receipt`。
5. PO 改为 `Received`；未观察到待检、抽样、判定、拒收或质量放行步骤。

### 3.4 成品/出货检验

未发现生产完工报检、成品检验计划、检验结果、放行人或 DO Ship 的 QC 前置条件。NDE Inspection Report 不能填补这一业务缺口。

### 3.5 GTFIP 贸易质检旁路

1. 建立 GTFIP 订单时初始化 `gtfip_quality`，状态为 `planned`。
2. GET 质量接口读取记录；空值时提供默认 AQL 2.5 计划、85 分与固定 checklist。
3. 未发现更新检验状态、分值、报告或照片的活动命令。
4. 因此该旁路只可作为贸易质检表面，不能作为来料/成品放行事实。

---

## 4. Validation

| ID | Validation | Strength | Detail |
|----|------------|----------|--------|
| QC-V1 | 五项评分必须为数值 | Type-level only | Form 转 float；未见业务范围 |
| QC-V2 | 五项评分应限定 0–100 或 0–10 | Missing | 负值和超范围值未被显式拒绝 |
| QC-V3 | 综合等级必须来自受控枚举 | Missing | 自由文本 |
| QC-V4 | 样品必须存在才可写评价 | Missing | 写入前未见 sample existence check |
| QC-V5 | 质量评价需检验员、时间与签名 | Missing | 表中没有这些字段 |
| QC-V6 | 评价需引用规格、方法、仪器和单位 | Missing | 数据模型未包含 |
| QC-V7 | 物化库存前必须有合格评价 | Missing | materialize 不读取质量记录 |
| QC-V8 | PO 收货前必须完成来料检验 | Missing | receive 直接入库 |
| QC-V9 | 实收、抽检、合格、拒收数量须守恒 | Not modeled | 只有 PO qty |
| QC-V10 | 成品出货前必须质量放行 | Missing | 未见 QC gate |
| QC-V11 | 同一检验批只能有一个当前有效判定 | Not modeled | 只有按 ID 取最新 |
| QC-V12 | 质量修改需权限与审计 | Weak / missing | 保存路由无可见 permission check，表无操作者/时间 |
| QC-V13 | GTFIP inspection status 合法转移 | Missing | 只证实默认 `planned`，未见 update |
| QC-V14 | GTFIP 默认 85 分必须与实测分区分 | Missing | API 以 fallback 值呈现 |
| QC-V15 | GTFIP checklist 每项必须有结果和证据 | Missing | 只返回固定名称 |

---

## 5. Data Semantics

| Entity / field | Legacy meaning |
|----------------|----------------|
| `sample_measurements` | 样品尺寸/物性测量容器，不带规格判定 |
| `length/width/thickness/weight` | 人工输入测量值；单位不在字段中 |
| `pitch/teeth` | 产品几何特征，不是自动质量结论 |
| `material/hardness` | 测量记录中的文本属性 |
| `sample_material_analysis` | 样品材料构成和风险描述 |
| `quality_grade` | 材料分析中的人工质量等级 |
| `risk_level` | 材料分析中的人工风险文本 |
| `sample_quality_assessment` | 样品五维评分记录 |
| 五项 `*_score` | 人工分值；量纲、范围、权重均未定义 |
| `overall_grade` | 人工综合等级，不是可证公式结果 |
| `remark` | 非结构化说明，不能代替缺陷明细 |
| `sample_supplier_matching.quality_score` | 候选供应商的样品层评分 |
| `Sample Receipt` | 样品物化库存的 ledger 类型，不表示检验合格 |
| `PO Receipt` | 采购收货 ledger 类型，不表示来料合格 |
| `Received` | PO 已执行收货过账，不等于 QC Accepted |
| `Stocked` | 样品已物化库存，不等于 Released |
| `gtfip_quality.inspection_status` | 贸易订单检验阶段；唯一可证默认值为 `planned` |
| `gtfip_quality.quality_score` | 贸易质检分值；空/零时 API 回退 85 |
| `gtfip_quality.report_json/photos_json` | 报告和照片结构槽位；活动写入未证实 |
| 产品 `stock_status` | 按数量计算的库存健康度，不是质量状态 |

---

## 6. State Vocabulary

| Value | Meaning / caveat |
|-------|------------------|
| `Draft` | 采购单草稿 |
| `Open` | 采购已批准，可收货 |
| `Received` / `已入库` / `Completed` | 采购服务归为 received stage；不是质量状态 |
| `Stocked` | 样品已物化 |
| `Sample Receipt` | 样品库存流水类型 |
| `PO Receipt` | 采购入库流水类型 |
| `overall_grade` values | 自由文本，未发现 canonical 列表 |
| `quality_grade` values | 自由文本，未发现 canonical 列表 |
| `risk_level` values | 自由文本，未发现 canonical 列表 |
| inspections / defects / holds / releases = `—` | QC workspace KPI 未连接事实 |
| `planned` | GTFIP 质检默认阶段；未证实 passed/failed/hold 转移 |
| `Healthy` / `Low Stock` / `Critical` | 产品库存数量预警词汇，非 QC |

---

## 7. UNKNOWN 与已查路径

| UNKNOWN | Paths searched |
|---------|----------------|
| 来料检验单、检验批、抽样方案是否存在 | `apps/procurement/**`, `apps/inventory/**`, `templates/purchase*.html`, `templates/inventory*.html`, `runtime/v14/legacy_support.py` |
| 成品检验与出货放行是否存在 | `apps/inventory/**`, `business_modules/production.md`, delivery/ship services, `templates/delivery*.html` |
| 评分范围、权重和自动综合等级 | `apps/sample/router.py`, `apps/sample/services.py`, `sample_quality_assessment` DDL, sample templates |
| 质量评价的检验员、时间、仪器与方法 | `apps/sample/**`, `runtime/v14/legacy_support.py`, `templates/sample*.html` |
| 质量评价是否应阻断报价、物化或采购 | sample-to-quote、`materialize_sample`, `receive_purchase`, lifecycle reports |
| QC Report / Inspection Report 的真实数据生产者 | `document/nde_engine.py`, `templates/documents/inspection_report.html`, print templates, `docs/reports/V41_Print_Report_Document_Matrix.md` |
| QC workspace 是否有隐藏事实源 | `v15/ux/registry.py`, `v15/ux/todays_work.py`, `/gtfip` references, `business_modules/**` |
| 生产批与成品批质量继承 | `business_modules/production.md`, inventory schema/repository, full-repo batch/lot/QC search |
| GTFIP `planned` 后续如何变为通过/失败/冻结 | `v15/gtfip/engines/quality.py`, `v15/gtfip/repository.py`, GTFIP routes；未找到 update 命令 |

---

## 8. Evidence Table

| Read-only path | Evidence |
|----------------|----------|
| `apps/sample/router.py` | 测量、材料分析、质量评价及供应商评分写入口 |
| `apps/sample/services.py` | 追加写入、最新评价读取与样品物化流程 |
| `apps/sample/repository.py` | 样品到库存的绑定、幂等和状态更新 |
| `runtime/v14/legacy_support.py` | 样品测量、材料、质量与供应商匹配表结构 |
| `templates/sample360.html` | 当前 Sample360 展示及物化入口；未显示质量 gate |
| `templates/sample_detail.html` | 照片/测量定位及未完成能力提示 |
| `apps/procurement/services.py` | PO Receive 直接库存过账，无检验步骤 |
| `templates/purchase_detail.html` | Receive Goods 操作和 Draft/Open/Received 流程 |
| `templates/purchase360.html` | 明示 supplier quality/delivery 尚未在 PO 评分 |
| `apps/inventory/repository.py` | 库存只有 SKU 数量、位置、安全库存和流水 |
| `v15/ux/registry.py` | QC workspace 注册与 GTFIP 导航 |
| `v15/ux/todays_work.py` | inspections/defects/holds/releases KPI 为占位值 |
| `v15/gtfip/repository.py` | `gtfip_quality` 结构及订单初始化为 `planned` |
| `v15/gtfip/engines/quality.py` | AQL 文案、默认 85 分和固定 checklist |
| `apps/product/services.py` | `Healthy/Low Stock/Critical` 仅按库存数量派生 |
| `document/nde_engine.py` | QC/Inspection 文档类型注册 |
| `templates/documents/inspection_report.html` | 通用产品表/时间线壳，不含专用检验结果 |
| `business_modules/inventory.md` | Inventory 边界和结构性风险 |
| `business_modules/production.md` | Production/Sample 边界，未定义成品质检 |
| `docs/reports/Business_Strong_A005_Sample_Quote_Report.md` | 样品物化 gate 只验证库存链 |
| `docs/reports/Business_Strong_A010_Purchase_Ops_Report.md` | 收货双写与状态诚实性范围 |
| `docs/reports/Business_Strong_A018_Inventory_Ops_Report.md` | 库存调整边界，无质量放行声明 |

**Root:** `H:\Workspace\EZAM_CRM - 9.0\` + paths above.
