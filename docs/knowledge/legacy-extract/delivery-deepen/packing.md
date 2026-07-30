# 装箱、打包与箱单

## Scope与证据强度

本页区分真实 DO 履约实体、NDE Packing List 打印派生、箱唛/箱标签预留，以及 GFIP/GTFIP 单证清单。

- **强证据：** DO 数据模型、NDE 构建器、打印模板、Ship 服务和 A-003/A-008 gates。
- **中证据：** 装箱打印/箱唛/标签配置表存在，但未接入运行解析器。
- **弱证据：** Shipment 模块规格与国际履约平行链不等于 operational DO。
- **核心结论：** Packing List 是 DO 的实时打印视图；系统没有真实箱、包、混箱或拆箱实体。

## 业务规则

1. **PK-R01** Packing List 不是持久化单据，由 DO 实时派生，显示号为 `PL-{do_no}`。
2. **PK-R02** 打印使用 `/print_preview/pl/{do_id}`，并接受 packing 类别名。
3. **PK-R03** PL 头和行来自 DO、客户、SO、产品关联查询。
4. **PK-R04** packing 行模式显示数量、Carton、净重和毛重，不显示价格和付款块。
5. **PK-R05** Carton 值按 DO 行序号生成 `CTN-{i}`，不是物理箱号。
6. **PK-R06** `total_packages` 等于 DO 行数，不是实际箱数。
7. **PK-R07** 行净重、毛重和 shipment CBM 槽存在，但默认为空。
8. **PK-R08** 建 DO 时全量复制 SO 行，不在创建时扣库存。
9. **PK-R09** Ship 时才扣 inventory/products 并写 `DO Ship` 台账。
10. **PK-R10** DO 从 Open 到 Shipped 再到 Delivered，Complete 必须先 Ship。
11. **PK-R11** Complete 会把关联 SO 整单标为 Delivered，不按装箱行判断剩余量。
12. **PK-R12** Reopen 只回退状态，不恢复库存。
13. **PK-R13** Packing List 打印权限映射到 Delivery Orders。
14. **PK-R14** Packing List 只能作为 DO 的 Layer C 打印动作，不建立独立中心。
15. **PK-R15** packing print、shipping mark 和 carton label 配置表未接运行打印链。
16. **PK-R16** GFIP 的 packing list 是 checklist 元数据，不调用 NDE，也不写 DO。

## 流程

1. SO 创建 DO，并复制全部销售订单行。
2. DO 在 Pending 阶段等待 Ship；此时没有装箱录入过程。
3. 用户可从 DO 页面打开 Packing List 预览。
4. NDE 读取 DO 头和行，为每个产品行派生 `CTN-i`，将行数当作 total packages。
5. 模板按 packing 模式渲染；重量和体积没有来源时隐藏或留空。
6. Ship 独立执行库存扣减；打印动作不改业务数据。
7. GFIP/GTFIP 可维护单证 ready 状态，但与该 DO 箱单没有自动同步。

## 校验

1. **PK-V01** 打印要求登录及 Delivery Orders 打印/查看权限。
2. **PK-V02** 来源 DO 不存在时，NDE 不生成业务预览。
3. **PK-V03** Ship 要求 DO 处于 open。
4. **PK-V04** 已有同 DO ledger 时禁止重复 Ship。
5. **PK-V05** Ship 要求库存充足。
6. **PK-V06** Ship 要求库存记录存在或可建立。
7. **PK-V07** Complete 要求 DO 已 Shipped。
8. **PK-V08** 已 Complete 的 DO 不可重复 Complete。
9. **PK-V09** Reopen 只允许 complete 阶段。
10. **PK-V10** NDE 打印构建器不得执行库存或业务写动作。

## 数据含义

| 数据 | 含义 |
|---|---|
| `delivery_orders.do_no` | PL 展示号的来源 |
| `delivery_orders.so_id` | 来源 SO |
| `delivery_orders.status` | 履约阶段，不是装箱状态 |
| `delivery_orders.total_amount` | DO 金额，PL 不显示 |
| `delivery_order_items.qty` | PL 数量和 Ship 扣减依据 |
| `delivery_order_items.product_id` | 产品关联 |
| `nde.lines[].carton` | 行级 `CTN-i` 占位，不是数据库箱号 |
| `net_weight` / `gross_weight` | 打印槽，默认空 |
| `nde.shipment.total_packages` | DO 行数，不是物理箱数 |
| `volume_cbm` | 体积展示槽，无主链采集 |
| `inventory_ledger` 的 `DO Ship` | 出库台账，与 PL 打印独立 |
| `gfip_documents.packing_list` | GFIP 单证 checklist |
| `packing_print_templates` | 未接线的打印配置 |
| `carton_label_templates` | 未接线的箱标签配置 |

## 状态词汇

| 状态 | 含义 |
|---|---|
| `Pending` / `待出库` | DO open |
| `已出库` / `Shipped` | 已扣库存 |
| `Delivered` / `已完成` | 已完成履约 |
| `Delivery Created` | SO 已创建 DO |
| `Open` | DO Reopen 后 SO 状态 |
| `pending` / `ready` | GFIP 单证 checklist 状态 |
| `Active` | 未接线模板表默认状态 |
| `metadata_only` / `implemented=false` | Logistics/Customs 注册层 |

## 证据表

| # | 观察事实 | 强度 | 只读路径 |
|---|---|---|---|
| E1 | PL 由 DO 派生且编号加 PL 前缀 | 强 | `document/nde_engine.py` |
| E2 | CTN 按行生成 | 强 | `document/nde_engine.py`、`templates/delivery_order_detail.html` |
| E3 | packing 模式列结构 | 强 | `templates/documents/components/product_table.html` |
| E4 | DO 只有头和行，无 carton 表 | 强 | `runtime/v14/legacy_support.py` |
| E5 | Ship 执行库存写入 | 强 | `apps/inventory/services.py` |
| E6 | A-008 验证 PL 打印链 | 强 | `docs/reports/Business_Strong_A008_Print_Report.md` |
| E7 | A-003 验证 DO 生命周期 | 强 | `scripts/business_strong_a003_delivery_gate.py` |
| E8 | 装箱模板表只有 DDL 引用 | 中 | `runtime/v14/legacy_support.py` |
| E9 | GFIP 只维护 packing list checklist | 中 | `v15/gfip/documents.py`、`v15/gfip/repository.py` |
| E10 | Customs packing list 标记未实现 | 中 | `core/customs/trade_document.py` |

## UNKNOWN

1. **packing template seed 与 NDE 绑定规则 UNKNOWN。** 已查 Legacy DDL 与 Python 引用。
2. **箱唛实际 UI/打印入口 UNKNOWN。** 已查 apps、templates 中 shipping mark 引用。
3. **carton label template JSON 结构 UNKNOWN。** 已查 DDL、审计数据和解析代码。
4. **生产 canonical DO 状态语言 UNKNOWN。** 已查状态同义词与历史报告，仍中英并存。
5. **GFIP 与 DO 的 ID 桥接规则 UNKNOWN。** 已查 GFIP repository/platform 和 Inventory。
6. **仓库扫码装箱能力 UNKNOWN/未发现。** 已查 Inventory scan 页面和 carton/box 关键词。
7. **同一 SO 多 DO 的剩余量防护 UNKNOWN/未实现。** 已查 Sales 创建 DO 和行查询。
8. **国别模板是否裁剪 PL 块 UNKNOWN。** 已查 country templates 与 NDE enrich。

## 只读来源路径

- `H:\Workspace\EZAM_CRM - 9.0\apps\inventory\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\sales\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\finance\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\customs_center\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\print_center\`
- `H:\Workspace\EZAM_CRM - 9.0\document\nde_engine.py`
- `H:\Workspace\EZAM_CRM - 9.0\templates\`
- `H:\Workspace\EZAM_CRM - 9.0\business_modules\`
- `H:\Workspace\EZAM_CRM - 9.0\docs\reports\`
- `H:\Workspace\EZAM_CRM - 9.0\runtime\v14\legacy_support.py`
- `H:\Workspace\EZAM_CRM - 9.0\v15\gfip\`
- `H:\Workspace\EZAM_CRM - 9.0\v15\gtfip\`
- `H:\Workspace\EZAM_CRM - 9.0\scripts\business_strong_a008_print_gate.py`
