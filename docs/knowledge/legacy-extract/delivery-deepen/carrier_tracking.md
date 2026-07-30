# 承运商、运单与跟踪

## Scope与证据强度

本页区分生产 DO、GFIP/GTFIP 平行履约、Logistics/Customs 注册层及目标 Shipment 模块。

- **强证据：** DO DDL/写入/页面、Inventory 状态机、GFIP/GTFIP schema、Logistics registry。
- **中证据：** GFIP/GTFIP 有跟踪结构和查询 API，但缺少与 DO 的写回及完整录入入口。
- **文档证据：** `business_modules/shipment.md` 描述目标态，不能替代运行实现。
- **核心结论：** 生产 DO 不采集 carrier/tracking number；平行平台的字段不能视为 DO 已具备物流跟踪。

## 业务规则

1. **CT-R01** 生产出库单权威表是 `delivery_orders`，没有承运商或运单号字段。
2. **CT-R02** DO 生产状态从待出库推进到已出库、已送达，状态表示业务阶段而非承运轨迹。
3. **CT-R03** 创建 DO 不扣库存，Ship 时才执行库存与台账写入。
4. **CT-R04** Ship 同步更新 inventory、products 库存镜像和 `DO Ship` 台账。
5. **CT-R05** Complete 必须在 Ship 后执行，并将关联 SO 标记为 Delivered。
6. **CT-R06** Reopen 只改状态，不恢复已扣库存。
7. **CT-R07** DO 详情的承运商和运单号区域明确显示尚未采集，而非可编辑字段。
8. **CT-R08** Ship 与 Invoice 属于 V18 Type A 动作，需要人工确认。
9. **CT-R09** GFIP 的 shipment 表有 carrier 和 tracking number，并存在内部创建能力。
10. **CT-R10** GTFIP logistics 有海运/空运相关字段、跟踪号和 ETA，默认运输方式为 sea。
11. **CT-R11** Logistics Center 的承运商/跟踪能力是 metadata-only，默认不启用。
12. **CT-R12** Shipment 模块只见目标规格，未形成 `apps/shipment` 运行包。
13. **CT-R13** 第三方承运商连接器均处于 reserved 状态，没有 live API。
14. **CT-R14** NDE 可从额外上下文显示 carrier、tracking number 和 ETA，但不会从 DO 自动取得。
15. **CT-R15** Complete 只是业务确认；没有 POD、电子签名或承运人回执字段。
16. **CT-R16** GFIP 从 SO 建单不创建或更新 DO，二者是平行链。

## 流程

### 生产 DO

1. SO 转换或销售服务创建 Pending DO 和行项。
2. DO 详情显示 carrier/tracking 尚未采集。
3. 用户人工确认 Ship；系统校验库存，扣减并写台账。
4. 用户 Complete；系统将 DO 和 SO 推进到 Delivered。
5. 用户可另行创建 AR；该财务动作不读取物流跟踪。

### GFIP/GTFIP 平行链

1. SO 可生成 GFIP 订单，但不与 DO 建立 shipment 外键。
2. GFIP/GTFIP 可保存或计算 shipment、tracking event、运输方式和 ETA。
3. 查询 API 返回国际履约视图；未见将结果回写 DO 的桥。

### 注册层

1. Logistics/Customs Center seed 承运商与运输方式元数据。
2. Center 页面和健康接口读取 registry。
3. Registry 不执行承运下单、轨迹拉取或 webhook 消费。

## 校验

1. **CT-V01** Ship 要求 DO 处于 open 阶段。
2. **CT-V02** 已 Ship/Complete 的 DO 不能重复 Ship。
3. **CT-V03** 已存在同 DO 台账时拒绝再次扣库存。
4. **CT-V04** Ship 只处理 product_id 有效且数量大于零的行。
5. **CT-V05** 产品必须存在库存记录或能成功建立库存记录。
6. **CT-V06** 在手量必须不小于出库数量。
7. **CT-V07** Complete 要求 DO 已 Ship。
8. **CT-V08** Type A Ship 必须人工确认。
9. **CT-V09** Type A Invoice 必须人工确认。
10. **CT-V10** Ship 要求 Delivery Orders edit 权限。
11. **CT-V11** Logistics 模块键必须属于 registry 集合。
12. **CT-V12** Carrier validator 只校验元数据键，不校验真实承运账户或运单。

## 数据含义

| 数据 | 含义 |
|---|---|
| `delivery_orders.do_no` | 生产出库单号 |
| `delivery_orders.status` | DO 业务阶段，不是承运轨迹状态 |
| carrier 缺失列 | 生产 DO 不持久化承运商 |
| tracking number 缺失列 | 生产 DO 不持久化运单号 |
| `gfip_shipments.carrier` | GFIP 平行履约承运商 |
| `gfip_shipments.tracking_no` | GFIP 平行履约运单号 |
| `gtfip_logistics.mode` | sea/air/rail/road/courier/multimodal |
| `flight_no` | GTFIP 空运航班号 |
| `vessel_name` / `voyage_no` | GTFIP 海运船名与航次 |
| `gfip_tracking_events` | GFIP 位置/状态/备注事件 |
| `logistics_carriers` | Logistics Center 承运商元数据 |
| `nde.logistics.tracking_number` | 打印透传槽，不是 DO 字段 |
| `inventory_ledger` 的 `DO-{do_no}` remark | Ship 幂等锚点 |
| ETA | GFIP/GTFIP 预测值，不是生产 DO 承诺日期 |

## 状态词汇

| 状态 | 含义 |
|---|---|
| `Pending` / `待出库` | DO 尚未 Ship |
| `已出库` / `Shipped` | 已扣库存 |
| `Delivered` / `已完成` | DO 已 Complete |
| `Cancelled` / `已取消` | 历史/列表可识别值，非完整取消流程 |
| `booked` / `pending` | GFIP shipment 平行状态 |
| `metadata_only` | 物流中心仅注册层 |
| `implemented=0` | 真实连接未实现 |
| `reserved` | 第三方 API 名额预留 |
| `departure` / `arrival` / `customs_clearance` / `final_delivery` | GFIP ETA 里程碑 |

## 证据表

| # | 观察事实 | 强度 | 只读路径 |
|---|---|---|---|
| E1 | DO 表无 carrier/tracking | 强 | `runtime/v14/legacy_support.py` |
| E2 | DO 页面明示尚未采集 | 强 | `templates/delivery_order_detail.html` |
| E3 | DO INSERT 不含物流字段 | 强 | `apps/sales/repository.py` |
| E4 | GFIP shipment 有 tracking 字段 | 强 | `v15/gfip/repository.py` |
| E5 | GTFIP logistics 默认 sea | 强 | `v15/gtfip/repository.py` |
| E6 | `apps/shipment` 未落地 | 强（缺失证据） | `business_modules/shipment.md`、`apps/` |
| E7 | 第三方连接器均 reserved | 强 | `v15/gfip/api_center.py` |
| E8 | Logistics Center 默认关闭 | 强 | `core/logistics/types.py` |
| E9 | Ship 幂等和库存规则有 gate | 强 | `scripts/business_strong_a003_delivery_gate.py` |
| E10 | POD 页面明确未实现 | 强 | `templates/delivery_order_detail.html` |
| E11 | NDE 只从 extra 取物流字段 | 强 | `document/nde_engine.py` |
| E12 | Customs shipping 只是运输方式 registry | 中 | `apps/customs_center/shipping_registry.py` |

## UNKNOWN

1. **生产运行库是否被私有补丁加 carrier 列 UNKNOWN。** 已查公开 upgrade patch 与租户 schema，未见迁移。
2. **巨型 Legacy 残留是否另有 shipment 路由 UNKNOWN。** 已查模块化 apps 和关键 residual，未逐条运行路由表。
3. **GFIP 建单是否在某环境自动创建 shipment UNKNOWN。** 已查 `v15/gfip/platform.py` 和 repository。
4. **GTFIP 是否有隐藏的 tracking 更新 API UNKNOWN。** 已查公开 routes，未见 POST/PATCH。
5. **DO 打印是否在某调用点注入 tracking extra UNKNOWN。** 已查 NDE 和 Print Center 关键链。
6. **目标 `shipments`/`shipment_tracking` 表是否存在于未加载插件 UNKNOWN。** 已查公开 DDL 与数据库 patch。
7. **GFIP 与 DO Ship 事件双向同步 UNKNOWN/未发现。** 已查 GFIP 与 Inventory 交叉引用。
8. **生产环境 Logistics Center 是否启用 UNKNOWN。** 代码默认关闭，未读取部署配置。
9. **物流 registry 是否有启动后业务更新 UNKNOWN。** 已查 repository，seed 仍写 implemented=0。

## 只读来源路径

- `H:\Workspace\EZAM_CRM - 9.0\apps\inventory\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\sales\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\finance\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\customs_center\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\logistics_center\`
- `H:\Workspace\EZAM_CRM - 9.0\v15\gfip\`
- `H:\Workspace\EZAM_CRM - 9.0\v15\gtfip\`
- `H:\Workspace\EZAM_CRM - 9.0\core\logistics\`
- `H:\Workspace\EZAM_CRM - 9.0\runtime\v14\legacy_support.py`
- `H:\Workspace\EZAM_CRM - 9.0\database\v151_logistics_center_schema.py`
- `H:\Workspace\EZAM_CRM - 9.0\document\nde_engine.py`
- `H:\Workspace\EZAM_CRM - 9.0\templates\delivery_order_detail.html`
- `H:\Workspace\EZAM_CRM - 9.0\templates\print\blocks\09_logistics.html`
- `H:\Workspace\EZAM_CRM - 9.0\business_modules\shipment.md`
- `H:\Workspace\EZAM_CRM - 9.0\business_modules\integration.md`
- `H:\Workspace\EZAM_CRM - 9.0\docs\reports\GFIP.md`
- `H:\Workspace\EZAM_CRM - 9.0\docs\reports\GTFIP.md`
