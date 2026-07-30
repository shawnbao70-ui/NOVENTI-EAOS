# PO Lifecycle Gates

**Evidence strength:** Strong  
**结论：** PO 主链是 Draft→Approve→Open→Receive→Received，但运行 stage 把 Draft、Open、Pending 都归为 open。Approve 只接受 Draft、有行和 Human Confirm；Receive 却接受整个 open family，因此 Draft/Pending 可绕过批准直接收货。未见 Sent、Partially Received、Closed、Cancelled 的受控转换。

## 状态矩阵

| DB status | stage | 可增行 | 可 Approve | 可 Receive | 可 Delete |
|---|---|---|---|---|---|
| Draft | open | 是 | 是 | **是** | 是 |
| Open | open | 是 | 否 | 是 | 是 |
| Pending | open | 是 | 否 | 是 | 是 |
| Received | received | 否 | 否 | 重复拒绝 | 否 |
| 已入库 | received | 否 | 否 | 重复拒绝 | 否 |
| Completed | received | 否 | 否 | 重复拒绝 | 否 |
| Other | other | 否 | 否 | bad_status | 否 |

## 业务规则

| ID | 规则 |
|---|---|
| PLG-R01 | 新 PO 以秒级编号、服务器日期、零金额和 Draft 创建。 |
| PLG-R02 | supplier_id 缺失时不创建并回列表。 |
| PLG-R03 | Draft/Open/Pending 被归入同一 open stage。 |
| PLG-R04 | Received/已入库/Completed 被归入 received stage。 |
| PLG-R05 | open stage 均可增加采购行。 |
| PLG-R06 | 行金额直接为 qty×cost_price。 |
| PLG-R07 | 详情读取时按行重算并写回头总额。 |
| PLG-R08 | Approve 只允许 Draft。 |
| PLG-R09 | Approve 要求至少一行和 human_confirm=1。 |
| PLG-R10 | Approve 成功把 PO 写 Open，不改库存。 |
| PLG-R11 | Receive 是独立动作，不调用 Approve。 |
| PLG-R12 | Receive 接受 Draft/Open/Pending，因此批准可旁路。 |
| PLG-R13 | Receive 成功把 PO 写 Received。 |
| PLG-R14 | open 且无 receipt ledger 的 PO 可被级联删除。 |
| PLG-R15 | 删除动作直接删 items/header，不形成 Cancelled。 |
| PLG-R16 | 未见 Sent/Issued/Supplier Acknowledged 状态动作。 |
| PLG-R17 | 未见 Partially Received/Closed/Reopen 受控路径。 |
| PLG-R18 | 本地 Type A Approve 不创建中心 `quote_approval` 类记录。 |
| PLG-R19 | Print PO 不改变状态，不能视为已实现的 Send gate。 |
| PLG-R20 | Finance Create Purchase Invoice 未见服务端强制 PO 已 Received。 |
| PLG-R21 | Received 后的“完成”实际是进入 invoice/AP 后续，没有独立 Complete 写动作。 |

## 校验

| ID | 校验点 | 实际强度 |
|---|---|---|
| PLG-V01 | Create 要 Purchases add | Hard |
| PLG-V02 | supplier_id 必填 | Weak redirect |
| PLG-V03 | Add item 要 Purchases edit | Hard |
| PLG-V04 | Add item PO 必须 open stage | Hard |
| PLG-V05 | qty/cost_price 必须为正 | Missing in service |
| PLG-V06 | Approve 必须 Draft | Hard |
| PLG-V07 | Approve 必须有行 | Hard |
| PLG-V08 | Approve human_confirm=1 | Hard |
| PLG-V09 | Receive 必须已 Approve/Open | Missing；Draft 可收 |
| PLG-V10 | Receive 必须 open stage/有行/无 ledger | Hard但过宽 |
| PLG-V11 | Delete 必须 open 且无 ledger | Hard |
| PLG-V12 | 状态转换矩阵/乐观锁 | Missing |
| PLG-V13 | Receive/Delete 使用 POST/CSRF | Missing；GET |
| PLG-V14 | PO no DB 唯一 | UNKNOWN |
| PLG-V15 | Create invoice 前必须 Received | Missing at Finance service |
| PLG-V16 | Purchase360 访问权限 | Missing in canonical route |

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| `purchases.id` | PO 技术键及 receipt remark 来源 |
| `po_no` | 秒级业务号 |
| `supplier_id` | 上游供方引用 |
| `po_date` | 建单服务器日期 |
| `total_amount` | 行金额汇总镜像 |
| `Draft` | 新建状态，也被 Receive 当 open |
| `Open` | Type A Approve 后状态 |
| `Pending` | 历史兼容 open 值 |
| `Received/已入库/Completed` | received family |
| `purchase_items.qty` | 订购且一次性收货使用的 qty |
| `cost_price` | 采购成本快照 |
| `human_confirm` | Approve 的人工确认输入 |
| operation log | Add/Approve 动作日志；非版本状态历史 |
| purchase_receipts | DDL 有表，但活动 Receive 不写 |
| delete | 物理级联删除，不是取消状态 |
| Print PO | 单据输出，不是 Sent 状态事件 |
| purchase invoice/AP | Received 后 UI 后续，但服务端状态前置较弱 |

## 证据表

| # | 观察事实 | 强度 | 只读来源 |
|---|---|---|---|
| PLG-E01 | 状态集合与 po_stage | 强 | `apps/procurement/services.py` |
| PLG-E02 | 新 PO Draft 创建 | 强 | `apps/procurement/services.py::add_purchase` |
| PLG-E03 | open stage 增行与金额公式 | 强 | `apps/procurement/services.py::add_purchase_item` |
| PLG-E04 | Approve 三项门与 Open 写入 | 强 | `apps/procurement/services.py::apply_purchase_approve` |
| PLG-E05 | Receive 独立且接受 open family | 强 | `apps/procurement/services.py::receive_purchase` |
| PLG-E06 | Delete open/ledger gate | 强 | `apps/procurement/services.py::delete_purchase` |
| PLG-E07 | 路由权限与 GET/POST 方法 | 强 | `apps/procurement/router.py` |
| PLG-E08 | PO/line/receipt DDL | 强 | `runtime/v14/legacy_support.py` |
| PLG-E09 | A-004 采购 gate | 中等 | `docs/reports/Business_Strong_A004_Purchase_Report.md` |
| PLG-E10 | 采购运行权威 | 强交叉 | `../ops/procurement.md` |
| PLG-E11 | Print 路径只读 PO 状态 | 强 | `apps/print_center/v14_residual.py`、`document/nde_engine.py` |
| PLG-E12 | Finance invoice 创建未要求 Received | 强负向 | `apps/finance/services.py`、`router.py` |

## UNKNOWN + 已查路径

1. **Pending 状态由哪个活动路径写入 UNKNOWN。** 已查：Procurement services/repository/router、residual、reports。
2. **Draft 可直接收货是政策还是缺陷 UNKNOWN。** 已查：Approve/Receive、templates、A-004/V18 reports。
3. **Sent/供应商确认是否在线下完成 UNKNOWN。** 已查：Procurement、message/email、templates、business_modules。
4. **PO no 是否生产库唯一 UNKNOWN。** 已查：公开 DDL/index/migrations。
5. **取消 PO 是否用物理删除以外流程 UNKNOWN。** 已查：routes/services/templates/reports。
6. **Completed 与 Received 的历史来源 UNKNOWN。** 已查：status writers、i18n、reports。
7. **中心 Approval 是否在部署插件中拦截 Receive UNKNOWN。** 已查：approval modules、Procurement routes/services。
8. **并发 Approve/Receive/Delete 最终状态 UNKNOWN。** 已查：repository commit、DB adapter、route model。
9. **打印 PO 是否在线下被当作供应商下达 UNKNOWN。** 已查：Print Center、Procurement templates、email/integration。
10. **PO invoice 前置门是否由 Finance 外层补足 UNKNOWN。** 已查：Finance router/service、middleware、templates。

## 交叉引用

- Procurement deepen：[`../procurement-deepen/README.md`](../procurement-deepen/README.md)
- 运行权威：[`../ops/procurement.md`](../ops/procurement.md)
