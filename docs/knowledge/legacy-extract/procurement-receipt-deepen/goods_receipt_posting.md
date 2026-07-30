# Goods Receipt Posting

**Evidence strength:** Strong  
**结论：** `/receive_purchase/{id}` 是带 edit 权限的 GET 写动作。Service 检查 PO 存在、stage=open、无既有 `PO Receipt + PO-{purchase_id}` ledger 且有 item，然后逐行过账并置 Received。它不创建 `purchase_receipts` header/item，也不要求 Human Confirm、供应商送货单、质检或实收数量输入；ledger 同时承担库存凭证和应用层幂等锚。

## 调用链

1. 页面在 open stage 展示 Receive。
2. GET route 检查 Purchases edit。
3. Service 读取 PO 并归一化 stage。
4. Received family 返回 `already_received`。
5. 非 open 返回 `bad_status`。
6. 查询 `PO Receipt + PO-{purchase_id}` ledger。
7. 无 purchase item 返回 `no_items`。
8. 逐行执行 stock posting。
9. PO→Received，末尾 commit。

## 业务规则

| ID | 规则 |
|---|---|
| GRP-R01 | Receive route 使用 purchase id。 |
| GRP-R02 | PO 不存在时不执行过账。 |
| GRP-R03 | Received/已入库/Completed 再收返回 already_received。 |
| GRP-R04 | Draft/Open/Pending 都可收货。 |
| GRP-R05 | ledger 判重类型固定 `PO Receipt`。 |
| GRP-R06 | ledger remark 固定 `PO-{purchase_id}`。 |
| GRP-R07 | 判重不使用 po_no、receipt_no、request token。 |
| GRP-R08 | 至少有一条 purchase item 才进入循环。 |
| GRP-R09 | qty<=0 或 product_id 无效的行被跳过，不阻断整单。 |
| GRP-R10 | 全部无效行仍可在零 ledger 情况下把 PO 写 Received。 |
| GRP-R11 | 每个有效行生成一条 PO Receipt ledger。 |
| GRP-R12 | 收货不写 `purchase_receipts` 表。 |
| GRP-R13 | 收货不采集 receipt_no、供应商送货单或实收时间。 |
| GRP-R14 | 收货不执行质检/拒收/隔离状态。 |
| GRP-R15 | 收货成功后统一更新 PO Received。 |
| GRP-R16 | Receive 是 GET，页面 confirm 不能替代 POST/CSRF。 |
| GRP-R17 | Receive 无 Type A human_confirm。 |
| GRP-R18 | 应用层先查后写，公开 DDL 未见 ledger 业务唯一键。 |
| GRP-R19 | Warehouse scan-action 的 Receive 分支最终复用同一采购 receive service。 |
| GRP-R20 | Receive 不写 operation log；路由错误只通过 query 参数反馈。 |
| GRP-R21 | supplier v14 residual 仍有较弱旧 receive，但标准 cutover 通常过滤重复路径。 |
| GRP-R22 | ledger 判重 SQL 未显式加入 tenant_id；若共享表含 tenant 列，隔离依赖外层机制。 |

## “Receipt” 边界

| 概念 | 当前运行事实 |
|---|---|
| Goods receipt | PO Receive service 动作 |
| `purchase_receipts` | 有 DDL，活动链未写 |
| `inventory_ledger` | 实际入库凭证 |
| `receipts` | Sales/Finance 收款，不是收货 |
| purchase invoice | Finance 后续单据，不是收货 |
| supplier delivery note | 未采集 |
| quality receipt | 未建模 |

## 校验

| ID | 校验点 | 实际强度 |
|---|---|---|
| GRP-V01 | Purchases edit 权限 | Hard |
| GRP-V02 | PO 必须存在 | Hard |
| GRP-V03 | stage 必须 open | Hard但含 Draft |
| GRP-V04 | 不得已有 PO Receipt ledger | Application hard |
| GRP-V05 | 至少存在一条 purchase item | Hard |
| GRP-V06 | 至少一条有效正 qty 行 | Missing |
| GRP-V07 | product 必须存在 | Weak；无效/缺产品处理不完整 |
| GRP-V08 | 必须已 Approve | Missing |
| GRP-V09 | receipt number/供应商单号唯一 | Missing |
| GRP-V10 | ledger 业务键 DB unique | Missing |
| GRP-V11 | POST/CSRF/Human Confirm | Missing |
| GRP-V12 | 质检/拒收/短收原因 | Missing |
| GRP-V13 | receipt header/items 与 ledger 原子 | 不适用；header未写 |
| GRP-V14 | 并发 Receive 串行 | Missing |
| GRP-V15 | 幂等查询显式 tenant scope | Missing in SQL |

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| purchase_id | Receive 主键和 remark 来源 |
| po_no | 展示业务号，不参与 receipt判重 |
| PO stage open | Draft/Open/Pending |
| PO status Received | Receive 成功标签 |
| purchase_items | 计划收货行全集 |
| `PO Receipt` | ledger 入库交易类型 |
| `PO-{purchase_id}` | 应用层判重/来源文本 |
| ledger qty | 正数收货量 |
| ledger balance_qty | 过账后 inventory 余额 |
| ledger create_time | Receive 应用时间 |
| purchase_receipts | 未被活动链使用的结构 |
| receipt_no | DDL 槽位但活动路径不生成 |
| supplier delivery note | 未建模 |
| inspection status | 未建模 |
| `receipts` | 客户收款实体，与本动作无关 |
| scan-action receive | Inventory 操作面进入同一 PO Receive 的次入口 |
| tenant_id | schema patch 可能添加，但 Receive insert/count 未显式使用 |

## 证据表

| # | 观察事实 | 强度 | 只读来源 |
|---|---|---|---|
| GRP-E01 | GET Receive route + edit 权限 | 强 | `apps/procurement/router.py` |
| GRP-E02 | stage/ledger/items 前置链 | 强 | `apps/procurement/services.py::receive_purchase` |
| GRP-E03 | ledger count 按 type+remark | 强 | `apps/procurement/repository.py::count_inventory_ledger_for_po` |
| GRP-E04 | 逐有效行写 ledger | 强 | `apps/procurement/services.py` |
| GRP-E05 | 全无效行可落 Received | 强负向 | `apps/procurement/services.py` |
| GRP-E06 | purchase_receipts DDL 存在 | 强结构 | `runtime/v14/legacy_support.py` |
| GRP-E07 | Receive 未调用 purchase_receipts insert | 强负向 | `apps/procurement/**` |
| GRP-E08 | ledger DDL 无业务 unique/FK | 强负向 | `runtime/v14/legacy_support.py` |
| GRP-E09 | 页面 Receive 是 open-stage 动作 | 强 | `templates/purchase_detail.html`、`purchases.html` |
| GRP-E10 | A-004 收货 gate | 中等 | `docs/reports/Business_Strong_A004_Purchase_Report.md` |
| GRP-E11 | Inventory scan Receive 委托同一 service | 强 | `apps/inventory/services.py::apply_scan_action` |
| GRP-E12 | supplier residual 旧 receive 被 canonical 路由优先级隔离 | 强历史 | `apps/supplier/v14_residual.py`、`bootstrap/v14_residual.py` |

## UNKNOWN + 已查路径

1. **purchase_receipts 是否由外部/历史路径写入 UNKNOWN。** 已查：Procurement、Inventory、residual、scripts、reports。
2. **供应商送货单号保存位置 UNKNOWN。** 已查：PO schema/templates、attachments/documents。
3. **Draft 直接 Receive 是否是正式政策 UNKNOWN。** 已查：Approve/Receive、business_modules、reports。
4. **生产 DB 是否私加 ledger unique UNKNOWN。** 已查：公开 DDL/index/migrations。
5. **并发两个 Receive 是否可双写 UNKNOWN。** 已查：service/repository/DB transaction。
6. **全无效行 Received 是否有生产实例 UNKNOWN。** 已查静态路径；未读生产数据。
7. **质检、拒收、短缺和退供应商流程 UNKNOWN。** 已查：Procurement/Inventory/Quality/templates/reports。
8. **GET Receive 是否有全局 CSRF/防预取保护 UNKNOWN。** 已查：router/middleware/security/templates。
9. **标准部署实际 skipped duplicate 路由清单 UNKNOWN。** 已查：enterprise cutover/residual filter；未运行启动探针。
10. **多租户下相同 purchase_id remark 是否跨租户误判 UNKNOWN。** 已查：tenant schema patch、count/insert SQL、repository scope。

## 交叉引用

- Procurement deepen：[`../procurement-deepen/README.md`](../procurement-deepen/README.md)
- 运行权威：[`../ops/procurement.md`](../ops/procurement.md)
