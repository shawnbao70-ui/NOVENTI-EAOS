# 客诉、RMA 与售后品质（Claim / RMA）— Legacy Knowledge

**Evidence strength:** Weak — navigation/graph vocabulary and planned Service scaffold; no operational claim/RMA lifecycle  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0` (read-only)

---

## 1. Scope 与证据强度

Legacy 对客诉/RMA 的可见内容主要是概念和占位：

- Customer Graph 把 `complaint` 列为可关联对象；
- demo graph 种入一条交付延迟 complaint；
- customer-service workspace 声明 requests/complaints/returns/delivery，但 KPI 值为 `—`；
- Service app README 明示 planned，repository 假定 `tickets` 主表，但活动 DDL 与业务写流程未确认；
- TechnicalService360 是只读 shadow，不负责 ticket/RMA 写入；
- 报价条款有默认 `Warranty: 12 Months` 文本。

全库业务检索未发现 RMA 编号、退货授权、客户退货收货、换货、退款、质保判定、客诉原因/责任、8D/CAPA 或结案满意度闭环。本模块交叉引用 `engagement/service.md`，不重复其大段内容。

---

## 2. Business Rules

| ID | Rule / observed boundary | Evidence / caveat |
|----|--------------------------|-------------------|
| RMA-R1 | Service app 的 ticket/SLA/AI response 仍是 planned 范围 | README 明示 planned |
| RMA-R2 | Service repository 假定主表 `tickets` | 活动 DDL、创建和状态推进未发现 |
| RMA-R3 | Service records API 只能尝试读取已有 ticket 行 | 不是客诉/RMA 创建入口 |
| RMA-R4 | Service detail 若 case_id 未命中可能退回第一条记录 | 不可作为可靠 RMA 对象定位 |
| RMA-R5 | TechnicalService360 只读映射已有 case/ticket/record | 不创建投诉、退货或质量处置 |
| RMA-R6 | Customer Graph 允许 `complaint` 作为对象类型 | registry 词汇不证明主数据表存在 |
| RMA-R7 | 可见 complaint `CMP-3` 是 demo seed | 不得当作真实客诉记录 |
| RMA-R8 | AI navigator 可把图中的 complaint 作为客户流失因素 | 仅分析已有关联，不能处理投诉 |
| RMA-R9 | Customer-service workspace 的 complaints/returns KPI 是 `—` | 没有接入实际聚合 |
| RMA-R10 | 默认 Warranty 12 Months 是报价条款文本 | 不是保修起算、覆盖范围或资格引擎 |
| RMA-R11 | 收货主线有 PO Receipt、Sample Receipt，出货主线有 DO Ship，另有通用 Manual Adjustment | 未见 Customer Return / RMA Receipt 专用库存动作 |
| RMA-R12 | 库存没有 serial/lot，因此无法验证退回件是否为原交付件 | 产品级关联不足 |
| RMA-R13 | 未发现销售退货与供应商退货两个独立流程 | 两者不能从普通库存 Adjust 推断 |
| RMA-R14 | 未发现退款、贷项通知单或换货订单由投诉自动生成 | NDE 有 Credit Note 类型也不等于业务闭环 |
| RMA-R15 | 客诉品质问题不会自动形成 NCR/CAPA | NCR 主流程本身未发现 |
| RMA-R16 | AI/Graph 建议不得自动批准退货、质保、退款或换货 | 缺少事实与授权链 |
| RMA-R17 | “return” 在审批/函数返回值/软件替换等语境不构成 RMA 证据 | 必须按业务上下文区分 |
| RMA-R18 | 售后品质结果若存在，必须保持与原销售、交付、产品、客户和证据的关联 | 当前模型未实现该完整关系 |
| RMA-R19 | 完成交付单可被 Reopen，但该动作只把 DO 改回开放并联动 SO 为 Open | 明示不恢复库存、不撤销原流水 |
| RMA-R20 | Reopen 要求 `Delivery Orders` edit 权限且 DO 必须处于 complete stage | 它是状态重开，不是退货授权 |
| RMA-R21 | 如需恢复数量只能另行执行通用 Inventory Adjust | 调整没有 RMA/claim 外键或受控退货原因 |
| RMA-R22 | Manual Adjustment 要求非零数量且结果不得为负库存 | 数量校验不能替代退回件、质量和授权校验 |

---

## 3. Process

### 3.1 当前可观察的只读/概念流程

1. Service API 可返回 health、records、workspace 元数据。
2. 若调用方已有 case/ticket/record，TechnicalService360 可生成只读详情、关系和通用建议。
3. Customer Graph 可展示已写入 graph 的 complaint 关联。
4. AI navigator 可提示“处理开放投诉”，但不执行任何业务动作。

### 3.2 当前交付与库存边界

1. 正向采购收货产生 PO Receipt。
2. 样品物化产生 Sample Receipt。
3. 交付出库产生 DO Ship。
4. 完成 DO 可由有权限用户执行 status-only Reopen，使 DO/SO 回到开放态；原出库流水和库存不回滚。
5. 用户可另行用通用 Inventory Adjust 恢复数量，但该动作不引用 RMA/客诉。
6. 未发现客户退货预授权、专用退货收货、检验、可修/报废判定、重新入库或换货出库动作。

### 3.3 缺失的 RMA 标准流程

未观察到：客户投诉登记 → 验证销售/交付/保修 → 分类与严重度 → RMA 授权 → 退回物流 → 收货隔离 → 技术/质量检查 → 维修/换货/退款/拒绝 → 客户确认 → 关闭 → 供应商追偿/CAPA。

### 3.4 售后服务交界

Service shadow 可表达安装、维护、维修、检查等 section，但这些 section 没有活动工单、备件、工时、SLA 或 RMA 状态机。详见 `../engagement/service.md`。

---

## 4. Validation

| ID | Validation | Strength | Detail |
|----|------------|----------|--------|
| RMA-V1 | 客诉/RMA 编号唯一且永久 | Not modeled | 无主实体 |
| RMA-V2 | 必须引用客户、销售单/DO、产品和数量 | Missing | graph 关联不是强制外键 |
| RMA-V3 | 必须验证保修起算日与覆盖范围 | Missing | 只有条款文本 |
| RMA-V4 | 必须验证退回件 serial/lot 属于原交付 | Impossible | 无 serial/lot |
| RMA-V5 | 重复投诉/RMA 应被检测 | Missing | 无 canonical claim key |
| RMA-V6 | 退回前须经授权，退回后须隔离 | Missing | 无 authorization/quarantine |
| RMA-V7 | 原因、严重度、责任和证据必须完整 | Missing | 无结构化字段 |
| RMA-V8 | 退款/换货/维修需相应权限与审批 | Missing | 无命令/审批桥 |
| RMA-V9 | 退货数量、处置数量和库存变动须守恒 | Not modeled | 无 RMA 行 |
| RMA-V10 | 结案需解决方案和客户确认 | Missing | 无关闭流程 |
| RMA-V11 | case_id 必须命中同一记录 | Violated risk | Service detail 有 fallback 第一条 |
| RMA-V12 | Demo complaint 不得进入生产统计 | Semantic guard | demo seed 与真实事实必须隔离 |
| RMA-V13 | AI 建议不可执行质保/退款/换货 | Hard boundary | 仅建议 |
| RMA-V14 | Complaint、service ticket、NCR、return、refund 必须分实体 | Missing | 当前仅词汇/壳 |
| RMA-V15 | DO Reopen 必须有 Delivery Orders edit 且原状态 complete | Implemented | 只保护状态重开 |
| RMA-V16 | Reopen 前应检查 AR/收款/原出库冲销 | Missing | 未观察到财务或 ledger 反向校验 |
| RMA-V17 | Inventory Adjust 必须非零且不得形成负库存 | Implemented | 无 RMA 来源和质量校验 |

---

## 5. Data Semantics

| Concept / field | Honest Legacy meaning |
|-----------------|-----------------------|
| `tickets` | Service repository 期望的表；活动 DDL UNKNOWN |
| `serviceRecord.status=active` | 通用 DTO 默认值，不是 RMA 状态 |
| `case_id` | Service detail 查找键；命中安全性有缺口 |
| `technical_service` | Object360 只读适配对象 |
| `complaint` object type | Enterprise Business Graph 的关系词汇 |
| `CMP-3` | demo complaint reference |
| requests KPI | Customer-service workspace 占位 |
| complaints KPI | Customer-service workspace 占位 |
| returns KPI | Customer-service workspace 占位 |
| `Warranty: 12 Months` | 报价默认条款文本 |
| `DO Ship` | 正向交付库存动作 |
| DO Reopen | 状态重开：DO→Open、SO→Open；不恢复库存 |
| `Manual Adjustment` | 通用库存增减及流水；不是退货收货 |
| `inventory_ledger.remark` | 自由来源说明；不是 claim/RMA 外键 |
| Customer Return / RMA Receipt | UNKNOWN / 未发现库存动作 |
| Credit Note | NDE 文档类型/别名表面；不证明退款业务 |
| replacement_part | 商机分类选项；不等于换货流程 |
| Service Report | NDE 文档类型；活动 case 数据生成 UNKNOWN |
| complaint graph edge | 通用关系记录，不具备 claim 状态机 |

---

## 6. State Vocabulary

| Value | Meaning / caveat |
|-------|------------------|
| `planned` | Service workspace 未完成 |
| `active` / `Active` | Service DTO 或通用配置默认，不是投诉处理中 |
| `Open` | TechnicalService fixture/通用状态，未形成 RMA 状态机 |
| `registered` / `linked` | TechnicalService360 shadow 展示事件 |
| `shadow` | 只读派生层 |
| requests/complaints/returns = `—` | 无事实 KPI |
| `DO Ship` | 正向出库 |
| DO `complete` | 可执行 status-only Reopen 的前置阶段 |
| DO/SO `Open` | Reopen 后状态；不表示退货已收货或财务已冲销 |
| `Manual Adjustment` | 通用库存动作词，不是 RMA 状态 |
| `Requested`, `Authorized`, `Received`, `Inspected`, `Repair`, `Replace`, `Refund`, `Rejected`, `Closed` | 期待的 RMA 状态；活动实现 UNKNOWN |

---

## 7. UNKNOWN 与已查路径

| UNKNOWN | Paths searched |
|---------|----------------|
| 是否存在真实客诉/claim/RMA 主表 | full-repo `complaint/claim/RMA` search；`apps/service/**`, runtime DDL |
| 是否存在销售退货或客户退货库存动作 | inventory/sales/delivery services、ledger trans types、return searches |
| 保修起算、范围、排除和授权规则 | quote terms、sales/DO/service paths、warranty search |
| 退回件如何关联原交付与 serial/lot | inventory schema/repository、delivery items、batch/serial searches |
| 是否存在维修、换货、退款、贷项业务命令 | service/finance/sales/quotation paths、templates、NDE Credit Note |
| 是否存在客诉严重度、SLA、升级和客户确认 | `apps/service/**`, TechnicalService360, customer-service workspace |
| 是否从客诉生成 NCR/CAPA 或供应商索赔 | nonconformance searches、procurement/supplier/service paths |
| complaint graph 数据是否来自真实业务写入 | enterprise business graph engine/registry/participant paths |
| Service Report 是否绑定真实 ticket/case | NDE engine, service print template, Service repository |
| DO Reopen 后原 AR、收款和出库流水如何冲销 | `apps/inventory/services.py`, finance AR/receipt paths, inventory ledger；未发现自动反向链 |

---

## 8. Evidence Table

| Read-only path | Evidence |
|----------------|----------|
| `apps/service/README.md` | Service ticket/SLA/AI response 标为 planned |
| `apps/service/repository.py` | 假定 `tickets`，仅列表/计数 |
| `apps/service/service.py` | 详情 fallback 风险和 TechnicalService360 附加 |
| `apps/service/schemas.py` | 通用 service DTO |
| `apps/service/routes.py` | 只有 health/records/workspace API |
| `core/object360/technical_service/` | 只读 shadow、通用关系/建议边界 |
| `v15/enterprise_business_graph/registry.py` | complaint 对象在 Customer Graph 词汇中 |
| `v15/enterprise_business_graph/engine.py` | `CMP-3` 是 demo seed |
| `v15/enterprise_business_graph/ai_navigator.py` | complaint 仅用于分析与建议 |
| `v15/ux/registry.py` | customer-service workspace 声明 complaints/returns |
| `v15/ux/todays_work.py` | complaints/returns KPI 为 `—` |
| `runtime/v14/legacy_support.py` | Warranty 12 Months 只是报价条款 |
| `apps/inventory/services.py` | DO status-only Reopen 与通用 Inventory Adjust 的真实边界 |
| `apps/inventory/repository.py` | 正向库存流水，未见 Customer Return/RMA Receipt |
| `apps/procurement/services.py` | PO Receipt 是买方收货，不是客户退货 |
| `document/nde_engine.py` | Service Report/Credit Note 文档类型不等于业务动作 |
| `business_modules/inventory.md` | 库存边界无退货/RMA 责任 |
| `business_modules/production.md` | Sample/Production 边界无售后品质链 |
| `docs/reports/Enterprise_Module_Recovery_Report.md` | Service residual 只含非售后主流程路由 |
| `docs/knowledge/legacy-extract/engagement/service.md` | 售后 scaffold 与缺失闭环交叉引用 |

**Full-repo negative search terms:** `RMA`, `return merchandise`, `return authorization`, `customer complaint`, `quality claim`, `sales_return`, `purchase_return`, `refund`, `replacement`, `warranty claim`.  
**Root:** `H:\Workspace\EZAM_CRM - 9.0\` + paths above（最后一项为当前 EAOS 交叉引用）。
