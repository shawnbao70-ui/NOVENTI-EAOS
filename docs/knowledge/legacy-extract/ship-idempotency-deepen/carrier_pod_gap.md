# Carrier / Tracking / POD 与 Ship / Complete 状态脱节

**Evidence strength:** Strong negative for production DO persistence and gates  
**结论：** 生产 `delivery_orders` 只有 delivery_date，没有 carrier、tracking number、POD、签收人/时间/签名字段。Ship 只过账库存；Complete 只检查已 Shipped 并改 DO/SO 状态，不要求承运信息、轨迹、交付日期更新或 POD。页面明确把 carrier/tracking 视为未采集/可选，把 Complete 当 delivery confirm；NDE 的物流与回执字段只来自 extra 渲染上下文，不能证明持久化。

## 脱节链

1. Create DO 把服务器当天写入 `delivery_date`；它不是实际签收时间。
2. DO 页面 carrier/tracking 显示提示文本，而非数据录入。
3. Ship 校验状态、ledger、库存、Human Confirm，不读取物流字段。
4. Ship 完成后 DO→已出库，但没有 tracking event。
5. Complete 只要求 stage=shipped。
6. Complete 将 DO/SO→Delivered，不写实际 delivered_at/POD。
7. Reopen 也只回退状态，不处理物流证据。
8. NDE 可渲染 carrier/tracking/received_by/signature，但调用方若不传则为空。

## 业务规则

| ID | 规则 |
|---|---|
| CPG-R01 | 生产 DO DDL 无 carrier 字段。 |
| CPG-R02 | 生产 DO DDL 无 tracking_no 字段。 |
| CPG-R03 | 生产 DO DDL 无 POD/e-sign/receipt FK。 |
| CPG-R04 | `delivery_date` 在创建 DO 时写服务器当天，不是 Complete 时间。 |
| CPG-R05 | Ship 不要求 carrier 或 tracking number。 |
| CPG-R06 | Ship 不生成 tracking event 或承运 API 请求。 |
| CPG-R07 | Complete 只以 DO Shipped 状态为前置。 |
| CPG-R08 | Complete 不要求 received_by、签名、照片或异常确认。 |
| CPG-R09 | Complete 不更新 delivery_date 为实际送达时间。 |
| CPG-R10 | Complete 成功把关联 SO 直接写 Delivered。 |
| CPG-R11 | 页面明确声明 carrier/tracking optional/not captured。 |
| CPG-R12 | 页面明确声明 POD/e-sign 未采集，Complete 被当作 confirm。 |
| CPG-R13 | NDE logistics/receipt/signature 字段来自 extra context。 |
| CPG-R14 | 空白 Receipt Confirmation 打印区不等于 POD 数据。 |
| CPG-R15 | GFIP/GTFIP 的 shipment/tracking 是平行模型，未见回写生产 DO。 |
| CPG-R16 | Logistics Center registry/connector 元数据不等于实际承运集成。 |
| CPG-R17 | 样品侧没有 outbound/POD 父实体，不能复用为 DO POD。 |
| CPG-R18 | Reopen 不撤销或校验 carrier/POD，因为生产 DO 未建模这些事实。 |

## 状态与证据矩阵

| 状态/动作 | 库存事实 | 承运事实 | POD 事实 | 时间事实 |
|---|---|---|---|---|
| Create DO | 不变 | 无 | 无 | delivery_date=创建当天 |
| Ship | 三写出库 | 无 carrier booking | 无 | ledger create_time |
| Complete | 不变 | 不查 tracking | 不查签收 | 不写 delivered_at |
| Reopen | 不恢复 | 不处理 | 不处理 | 不处理 |
| NDE Print | 展示当前单据 | extra 可透传 | 空白/extra 可透传 | print_time 是打印时间 |

## 校验

| ID | 校验点 | 实际强度 |
|---|---|---|
| CPG-V01 | Ship 前 DO open/库存充足 | Hard |
| CPG-V02 | Complete 前必须 Shipped | Hard |
| CPG-V03 | Ship/Complete edit 权限 | Hard |
| CPG-V04 | Ship 前 carrier 必填 | Missing |
| CPG-V05 | Ship 前 tracking number 格式/唯一 | Missing |
| CPG-V06 | Complete 前必须有 delivered tracking event | Missing |
| CPG-V07 | Complete 前必须有 POD | Missing |
| CPG-V08 | 签收时间不得早于 Ship | Missing |
| CPG-V09 | 签收数量必须与 DO 数量一致/支持部分签收 | Missing |
| CPG-V10 | 签名/照片文件安全与哈希 | Missing |
| CPG-V11 | 拒收/破损/短缺必须建异常 | Missing |
| CPG-V12 | carrier webhook 身份与重放验证 | Missing |
| CPG-V13 | delivery_date 必须为实际送达时间 | Missing |
| CPG-V14 | GFIP tracking 必须同步 DO | Missing |

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| `delivery_orders.do_no` | 生产出库单业务号 |
| `delivery_orders.status` | 内部业务阶段，不是承运轨迹 |
| `delivery_orders.delivery_date` | 创建 DO 时的服务器日期 |
| `已出库/Shipped` | 库存过账完成，不代表承运揽收 |
| `Delivered/已完成` | 人工 Complete 状态，不是法定 POD |
| ledger create_time | 库存过账时间，不是发车/签收时间 |
| carrier | 生产 DO 未持久化 |
| tracking number | 生产 DO 未持久化 |
| tracking event | 生产 DO 未建模 |
| received_by | NDE extra 渲染槽 |
| receive_date/time | NDE extra 渲染槽 |
| receipt/customer/electronic signature | NDE extra 渲染槽 |
| Receipt Confirmation | 打印表现层区块 |
| `gfip_shipments` | 平行履约数据，不是 DO 子表 |
| logistics registry | 承运商元数据/保留连接能力 |
| sample POD | 缺失的相邻领域能力 |

## 证据表

| # | 观察事实 | 强度 | 只读来源 |
|---|---|---|---|
| CPG-E01 | delivery_orders DDL 仅有 delivery_date/status 等 | 强 | `runtime/v14/legacy_support.py` |
| CPG-E02 | Create DO insert 不含 carrier/tracking/POD | 强 | `apps/sales/repository.py::insert_delivery_order` |
| CPG-E03 | Ship service 不读物流/POD | 强负向 | `apps/inventory/services.py::ship_delivery_order` |
| CPG-E04 | Complete 只查 stage 并更新 DO/SO | 强 | `apps/inventory/services.py::_legacy_complete_do` |
| CPG-E05 | 页面 carrier/tracking 显示未采集/可选 | 强 | `templates/delivery_order_detail.html` |
| CPG-E06 | 页面 Signed 时间线声明 POD/e-sign 未采集 | 强 | `templates/delivery_order_detail.html` |
| CPG-E07 | NDE 从 extra 读取 logistics/receipt/signature | 强 | `document/nde_engine.py` |
| CPG-E08 | GFIP/GTFIP tracking 为平行结构 | 强 | `v15/gfip/**`、`v15/gtfip/**` |
| CPG-E09 | Shipment 模块仍是目标规格 | 中等 | `business_modules/shipment.md` |
| CPG-E10 | 既有 carrier 权威页确认生产 DO 缺字段 | 强交叉 | `../delivery-deepen/carrier_tracking.md` |
| CPG-E11 | Sample POD 权威页确认样品 POD 全链缺失 | 强交叉 | `../sample/pod.md` |

## 风险边界

- **状态提前：** 手工 Complete 可让 SO/DO 显示 Delivered，而客户是否签收未知。
- **日期误读：** delivery_date 可能被误当实际送达日，实际上是创建 DO 的服务器日期。
- **不可追责：** 无承运商、运单号、签收人、签名/照片和异常证据。
- **平行真相：** GFIP/GTFIP 即使有 tracking，也没有可证实的 DO 同步。
- **打印幻觉：** 模板上出现签收栏，不代表系统已采集或固化 POD。

## UNKNOWN + 已查路径

1. **生产库是否有私有 carrier/tracking/POD 列 UNKNOWN。** 已查：公开 DDL、database patches、tenant schema。
2. **Complete 操作者是否被 operation log 记录 UNKNOWN。** 已查：Inventory route/service、logging、templates。
3. **NDE 调用方是否在某部署注入真实 POD extra UNKNOWN。** 已查：Inventory print、Print Center、NDE callers。
4. **GFIP/GTFIP 是否有隐藏 webhook 回写 DO UNKNOWN。** 已查：公开 routes/services/repositories、integration reports。
5. **delivery_date 的业务标签是否刻意表示计划日期 UNKNOWN。** 已查：Create DO、templates、business_modules、reports。
6. **承运商外部连接在生产配置是否启用 UNKNOWN。** 已查：registry、API center、默认配置；未读部署秘密。
7. **客户签字纸本是否离线归档 UNKNOWN。** 已查：attachments/documents/templates；无可证实关联。
8. **部分签收、拒收、破损和重新派送政策 UNKNOWN。** 已查：Inventory/Sales/Sample、shipment spec、reports。

## 交叉引用

- Carrier/tracking 权威：[`../delivery-deepen/carrier_tracking.md`](../delivery-deepen/carrier_tracking.md)
- Sample POD：[`../sample/pod.md`](../sample/pod.md)
- Ship 权威：[`../ship-complete-deepen/do_ship.md`](../ship-complete-deepen/do_ship.md)
- Complete 权威：[`../ship-complete-deepen/do_complete.md`](../ship-complete-deepen/do_complete.md)
