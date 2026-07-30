# Production Runtime — Legacy Knowledge

**Evidence strength:** Medium/Strong（GTFIP 订单级生产进度摘要）/ Missing（完整制造执行域）  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0`（只读）

## 1. Scope 与证据强度

本文件寻找超越 `business_modules/production.md` 规范意图的生产运行证据。

可确认落地位于 GTFIP：每个 GTFIP 全球履约订单初始化一条 `gtfip_production`，可读取/更新工厂、进度百分比、物料状态、延误天数和预测完成日，并在 Digital Twin/Command Center 展示。

未找到独立 `production_orders` / `work_orders` 运营路由、BOM 展开、MRP、工序报工、领退料、产能排程、批次/序列、成本归集或车间终端。GTFIP 证据是订单级里程碑摘要，不是完整 MES/制造模块。

## 2. 业务规则（稳定 ID）

| ID | 规则 | 触发/例外 | 证据强度 |
|---|---|---|---|
| PROD-RT-RULE-001 | 创建 GTFIP order 后初始化一条生产记录，progress=0 | 仅 GTFIP repository create path | Strong |
| PROD-RT-RULE-002 | 生产记录以 `order_id` 关联 GTFIP order，保存 supplier/factory、进度、计划、预测、物料状态、延误和 timeline JSON | schema 未声明 order_id UNIQUE | Strong |
| PROD-RT-RULE-003 | 查询生产状态前必须找到 GTFIP order；不存在返回 `Order not found` | production row 可不存在，此时使用默认摘要 | Strong |
| PROD-RT-RULE-004 | 无生产行时展示 progress 0、factory `—`、material `ok`、delay 0，并生成临时 forecast/timeline | 这些默认值不是持久事实 | Strong |
| PROD-RT-RULE-005 | 默认 forecast = 当前日 + max(7, 30 − progress/3) 天 | 仅当存储 forecast 缺失 | Strong |
| PROD-RT-RULE-006 | 更新进度时 forecast = 当前日 + max(3, (100 − progress)/5) 天，并持久化 progress/delay/forecast | 未使用 schedule_end 或产能数据 | Strong |
| PROD-RT-RULE-007 | progress >= 100 时新增 stage=`production_tracking`、notes=`Production completed` 的订单事件 | 未自动推进到 quality_inspection | Strong |
| PROD-RT-RULE-008 | 采购引擎生成 AI PO 时把 supplier name 当 factory，重置 progress=0，并新增 `ai_purchase_order` 事件 | 若重复调用会覆盖进度 | Strong |
| PROD-RT-RULE-009 | Digital Twin 同时展示 production、quality、logistics、tracking、LC 与成本摘要 | 是订单聚合视图 | Strong |
| PROD-RT-RULE-010 | Command Center 把 current_stage 属 production/production_tracking/quality_inspection 的 active orders 计为 production_active | quality 也计入生产中 | Strong |
| PROD-RT-RULE-011 | `on_schedule` = delay_days <= 0 且 progress >= 0 | 对正常非负进度几乎只由 delay 决定 | Strong |
| PROD-RT-RULE-012 | Production 规范声称拥有生产订单、工单、BOM、排程与物料消耗 | 未找到相应运营实现，不可视为 Legacy 事实 | Weak intent |
| PROD-RT-RULE-013 | BOM、工序、报工、物料消耗、完工入库、生产成本和返工规则为 `UNKNOWN` | 已查未见运行链 | Missing |

## 3. 流程

### 3.1 GTFIP 生产摘要流程

1. 创建 GTFIP global fulfillment order。
2. repository 初始化 production=0 与 quality=planned。
3. 采购/供应商分配可写 factory，并把进度设为 0。
4. GET production API 返回当前进度、工厂、物料状态、延误、预测完成和 timeline。
5. POST progress API 更新 progress 与 delay，重新计算预测完成日。
6. progress >= 100 时写一条 “Production completed” 的 `production_tracking` 事件。
7. Digital Twin 与 Command Center 读取生产摘要。

### 3.2 声明式履约阶段

GTFIP lifecycle 中生产附近阶段为：

`supplier_assignment → production → production_tracking（另一套列表）→ quality_inspection → packing`

不同 lifecycle 文件对是否包含 `production_tracking` 有差异；实际订单阶段可由通用 advance API写入。

### 3.3 完整制造流程

`Production Order → BOM/MRP → Work Orders/Operations → Material Issue → Labor/Machine Reporting → QC → Finished Goods Receipt → Costing`

该流程为 `UNKNOWN`；未找到足够运行证据。

## 4. 校验（强 / 弱 / 缺失）

| ID | 校验 | 强度 | 说明 |
|---|---|---|---|
| PROD-RT-VAL-001 | production 查询要求 order 存在 | 强 | 不存在返回错误 |
| PROD-RT-VAL-002 | progress 范围必须 0..100 | 缺失 | API 接收 float，未见上下界 |
| PROD-RT-VAL-003 | delay_days 必须非负 | 缺失 | 负值会被视为 on schedule |
| PROD-RT-VAL-004 | 更新目标 production row 存在 | 弱 | UPDATE 无 affected-row 检查 |
| PROD-RT-VAL-005 | progress update 权限/人工确认 | 缺失 | 路由未见 RBAC 或 Request actor |
| PROD-RT-VAL-006 | 完工必须 progress=100 且质检通过 | 缺失 | 只按 progress >=100 写事件 |
| PROD-RT-VAL-007 | factory/supplier 必须存在于主数据 | 缺失 | supplier_name 可为自由文本 |
| PROD-RT-VAL-008 | schedule start/end 与 forecast 一致 | 缺失 | 更新公式不使用计划日期 |
| PROD-RT-VAL-009 | order_id 一对一 production 唯一 | 缺失 | schema 无 UNIQUE(order_id) |
| PROD-RT-VAL-010 | BOM/物料/工序/产量/废品/成本校验 | 缺失 | `UNKNOWN` |

## 5. 数据含义

| 字段/实体 | 含义 |
|---|---|
| `gfip_orders` | 全球履约订单；可关联 sales_order |
| `gtfip_production.order_id` | 生产摘要所属 GTFIP order |
| `supplier_id` / `factory_name` | 供应商/工厂摘要；factory 可由 AI PO 写自由文本 |
| `progress_pct` | 手工/API 更新的完成百分比 |
| `schedule_start` / `schedule_end` | 计划时间字段；未见更新流程 |
| `forecast_completion` | 基于简单公式或存储值的预测日期 |
| `material_status` | 自由文本物料摘要，默认 `ok` |
| `delay_days` | 手工/API 提交的延误天数 |
| `timeline_json` | 生产内部 timeline 字段；更新进度未写该字段 |
| `gfip_order_events` | 通用阶段/事件历史；完工写 `production_tracking` |
| `gtfip_quality` | 相邻质检摘要，不是工序内质量记录 |

未找到：production order no、BOM version、routing、operation、work center、planned/actual qty、scrap、material issue、labor/machine time、lot/serial、WIP、finished-goods receipt、cost variance。全部 `UNKNOWN`。

## 6. 状态词汇

| 词汇 | 所属语境 | 含义 |
|---|---|---|
| `active` | gfip order | Command Center 纳入统计 |
| `production` | lifecycle stage | 生产阶段 |
| `production_tracking` | GTFIP stage/event | 跟踪阶段；完工事件也写此 stage |
| `quality_inspection` | lifecycle stage | 生产后的质检阶段 |
| `ok` | material_status 默认 | 仅默认文本，不证明齐料 |
| `planned` | quality 默认 | 质检计划状态 |
| `on_schedule` | 派生布尔值 | delay<=0 且 progress>=0 |
| Planned/Released/In Progress/Paused/Completed/Closed/Cancelled | 完整生产订单 | `UNKNOWN`；未找到 runtime enum |

## 7. 只读来源路径

- `H:\Workspace\EZAM_CRM - 9.0\business_modules\production.md`
- `H:\Workspace\EZAM_CRM - 9.0\v15\gtfip\repository.py`
- `H:\Workspace\EZAM_CRM - 9.0\v15\gtfip\routes.py`
- `H:\Workspace\EZAM_CRM - 9.0\v15\gtfip\platform.py`
- `H:\Workspace\EZAM_CRM - 9.0\v15\gtfip\lifecycle.py`
- `H:\Workspace\EZAM_CRM - 9.0\v15\gfip\lifecycle.py`
- `H:\Workspace\EZAM_CRM - 9.0\v15\gtfip\engines\production.py`
- `H:\Workspace\EZAM_CRM - 9.0\v15\gtfip\engines\procurement.py`
- `H:\Workspace\EZAM_CRM - 9.0\v15\gtfip\engines\quality.py`
- `H:\Workspace\EZAM_CRM - 9.0\v15\gtfip\engines\command_center.py`
- `H:\Workspace\EZAM_CRM - 9.0\v15\gtfip\engines\digital_twin.py`
- `H:\Workspace\EZAM_CRM - 9.0\templates\gtfip_digital_twin.html`
- `H:\Workspace\EZAM_CRM - 9.0\templates\gtfip_command_center.html`
- `H:\Workspace\EZAM_CRM - 9.0\v15\business_lifecycle\constants.py`

**Negative search:** 已查 production_orders、work_orders、BOM、routing、operation、work center、material issue/consumption、shop floor、reporting、WIP、finished goods receipt、production costing 及对应路由/模板/服务；未找到完整制造运行链。
