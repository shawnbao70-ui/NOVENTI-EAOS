# Delivery Order Complete / Delivered

**Evidence strength:** Strong for status conditions and writes; strong risk evidence for GET mutation

## Scope 与关键结论

Complete 不是出库动作。只有已 Ship 的 DO 才能 Complete；成功后把 DO 和关联 SO 都写为 `Delivered`，不再扣库存、不追加流水，也不记录 POD/签收人。动作通过 GET `/complete_do/{do_id}` 直接写库，页面只有 JavaScript confirm，因此链接被重放、预取或跨站触发的风险高于 Type A POST。

## 业务规则

| ID | 规则 |
|---|---|
| DOC-R01 | Complete handler 要求 Delivery Orders edit 权限。 |
| DOC-R02 | DO 不存在时返回 DO 列表，不执行写入。 |
| DOC-R03 | 只有 shipped stage（`已出库 / Shipped`）可 Complete。 |
| DOC-R04 | 已 complete stage（`Delivered / 已完成`）再次调用返回 `already_complete`。 |
| DOC-R05 | open 或其他状态调用 Complete 返回 `ship_first`。 |
| DOC-R06 | 成功时 DO 状态统一写 canonical `Delivered`。 |
| DOC-R07 | DO 有 `so_id` 时，同步把关联 SO 写为 `Delivered`。 |
| DOC-R08 | DO 无 `so_id` 时仍可完成，只跳过 SO 更新。 |
| DOC-R09 | DO 与 SO 更新在同一末尾 commit 中提交。 |
| DOC-R10 | Complete 不读取或修改 inventory、products 或 inventory_ledger。 |
| DOC-R11 | Complete 不校验 AR、收款、承运商、跟踪号、POD 或签收人。 |
| DOC-R12 | Complete 入口为 GET，页面 confirm 只是客户端提示，不是服务端 Human Confirm。 |
| DOC-R13 | 页面只在 shipped stage 展示 Complete CTA，但直链服务端仍自行做状态检查。 |
| DOC-R14 | `delivery_date` 在创建时已赋值；Complete 没有写实际送达时间。 |
| DOC-R15 | Delivered 在 Legacy 中代表人工状态确认，不能当作物流签收证据。 |
| DOC-R16 | Complete 后可 Reopen；重开是另一 GET 状态动作。 |
| DOC-R17 | 列表批量完成通过 JavaScript 对 shipped 行逐个 `fetch("/complete_do/{id}")`，仍复用同一 GET 写入口。 |

## 状态流程

`Pending/待出库 → Ship → 已出库/Shipped → GET Complete → Delivered`

Complete 的实际写入只有：

1. `delivery_orders.status = 'Delivered'`；
2. 若有 SO，`sales_orders.status = 'Delivered'`；
3. commit。

库存事实早在 Ship 形成；AR 可以在 Complete 前后独立计提。

## GET 直链风险

| 风险 | Legacy 现状 |
|---|---|
| HTTP 语义 | GET 改状态 |
| 人工确认 | `onclick=confirm(...)`，可绕过 |
| CSRF token | 未观察到 |
| Human Confirm 字段 | 无 |
| 幂等 | 状态检查可防重复结果，但请求仍是写动作 |
| 审计 | handler 未观察到 operation log |
| 实际送达证据 | 无 POD/签收字段 |
| 批量动作 | 多个 GET fetch 逐条执行；中途失败不形成整体事务 |

## 校验

| ID | 校验 | 强度 |
|---|---|---|
| DOC-V01 | Delivery Orders edit 权限 | Hard |
| DOC-V02 | DO 必须存在 | Hard |
| DOC-V03 | 当前阶段必须 shipped | Hard |
| DOC-V04 | 已 Complete 不得重复完成 | Hard |
| DOC-V05 | 必须先 Ship | Hard |
| DOC-V06 | Complete 应使用 POST/命令 | Missing |
| DOC-V07 | 必须有 CSRF/Human Confirm | Missing |
| DOC-V08 | 关联 SO 必须存在且状态一致 | Weak；无 SO 时跳过 |
| DOC-V09 | 必须记录实际送达时间 | Missing |
| DOC-V10 | 必须记录签收人/POD | Missing |
| DOC-V11 | 必须检查所有行均已发运 | 由单一 DO Ship 状态间接代表；无分批事实 |
| DOC-V12 | 必须写操作审计 | Missing |

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| `delivery_orders.status` | Complete 的主状态字段 |
| `已出库` / `Shipped` | Complete 允许的前序阶段 |
| `Delivered` | Complete 成功写入的 canonical DO/SO 状态 |
| `已完成` | 被识别为 complete 的 legacy 同义值 |
| `sales_orders.status` | Complete 时同步写 Delivered |
| `delivery_orders.so_id` | 决定是否同步 SO 的关联 |
| `delivery_date` | 创建 DO 时的计划/单据日期，不是 Complete 时间 |
| `complete_error=already_complete` | 重复完成反馈 |
| `complete_error=ship_first` | 未出库完成反馈 |
| `do_is_shipped` | 页面派生的 Complete CTA 条件 |
| `do_is_complete` | 页面派生的 Delivered/Reopen 条件 |
| inventory ledger | Ship 已形成的出库事实；Complete 不改 |
| GET `/complete_do/{id}` | 直接执行状态写入的命令式链接 |

## 证据表

| # | 观察事实 | 强度 | 只读来源 |
|---|---|---|---|
| DOC-E01 | 状态同义集合和 canonical 写值 | 强 | `apps/inventory/services.py` 顶部常量 |
| DOC-E02 | Complete 权限、前序和重复校验 | 强 | `apps/inventory/services.py::_legacy_complete_do` |
| DOC-E03 | DO/SO 同步 Delivered | 强 | `apps/inventory/services.py` |
| DOC-E04 | GET 路由直接调用完成服务 | 强 | `apps/inventory/router.py` |
| DOC-E05 | 页面仅 shipped 显示 CTA 且用 JS confirm | 强 | `templates/delivery_order_detail.html` |
| DOC-E06 | Ship 与 Complete 明确分离 | 强 | `templates/do_ship.html`、`delivery_order_detail.html` |
| DOC-E07 | Delivered 页面无签收/POD事实 | 强负向 | `templates/delivery_order_detail.html` |
| DOC-E08 | Delivery Ops 诚实性报告 | 中/强佐证 | `docs/reports/Business_Strong_A009_Delivery_Ops_Report.md` |
| DOC-E09 | A-003 创建/出库边界 | 强佐证 | `docs/reports/Business_Strong_A003_Delivery_Report.md` |
| DOC-E10 | 列表 shipped-only 批量 fetch Complete | 强 | `templates/delivery_orders.html` |

## UNKNOWN + 已查路径

1. **Complete 的业务操作者是否必须是仓管、物流或客户服务角色 UNKNOWN。** 已查：Inventory router、权限矩阵、templates、business modules。
2. **实际送达时间、签收人、POD/电子签名保存位置 UNKNOWN。** 已查：DO schema、Inventory/Sales 服务、模板、文档引擎。
3. **关联 SO 不存在时仍完成 DO 是否为允许政策 UNKNOWN。** 已查：`_legacy_complete_do`、repository、SO/DO DDL。
4. **Complete 是否应等待 AR、发票或收款 UNKNOWN。** 已查：Inventory/Finance services、Type A Invoice、finance 文档。
5. **GET 写动作是否有全局 CSRF/防预取保护 UNKNOWN。** 已查：router、middleware/security、模板 confirm。
6. **Complete 事件是否通知客户或物流人员 UNKNOWN。** 已查：apps/inventory、notification/message 路径、reports。
7. **多 DO 对一 SO 时一个 DO Complete 是否应把整个 SO Delivered UNKNOWN。** 已查：Sales create DO、Inventory complete、partial-delivery 知识页。

## 交叉引用

- Ship 过账：[`do_ship.md`](do_ship.md)
- 分批交付缺口：[`../fulfillment-deepen/partial_delivery.md`](../fulfillment-deepen/partial_delivery.md)
- DO 基线：[`../delivery/delivery_order.md`](../delivery/delivery_order.md)
