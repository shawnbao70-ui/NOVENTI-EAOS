# 一 SO 多 DO：允许性、行复制与剩余量缺口

**Evidence strength:** Strong  
**结论：** `delivery_orders.so_id` 是普通引用，SO detail 读取并展示多张 DO；canonical `/create_do` 和 legacy `/convert_do` 均不检查已有 DO，每次都复制 SO 的全部行和原 qty。Legacy 因此“允许多 DO”，但不是受控分批：没有选择行、本批 qty 或 remaining 计算。

## 两条创建路径

| 维度 | Canonical `/create_do/{so_id}` | Legacy `/convert_do/{so_id}` |
|---|---|---|
| Owner | Sales service | Inventory residual service |
| SO 存在 | 必须 | 必须 |
| 权限 | route 未显式；UI Delivery Orders add | Sales Orders edit |
| DO no | `DO` + 秒级时间戳 | `DO{so_id:04d}` |
| delivery_date | 创建当天 | SO order_date |
| status | Pending | Pending |
| header amount | SO total | SO total |
| items | 全部复制 | 全部复制 |
| existing DO check | 无 | 无 |
| SO status | 写 Delivery Created | 不写 |

另有 `apps/platform/v14_residual.py` 的历史 `/create_do`：同样全量复制，但在创建时直接扣 `products.stock_qty`，其 `/do_ship` 又再次扣产品镜像。标准 enterprise cutover 先挂 canonical business pages，再过滤 residual 重复路径，因此该路径通常被跳过；它仍是识别历史数据/非标准挂载双扣风险的证据，不是当前 partial delivery 能力。

## 业务规则

| ID | 规则 |
|---|---|
| MDS-R01 | SO 不存在时不创建 DO。 |
| MDS-R02 | delivery_orders.so_id 可对应多行。 |
| MDS-R03 | SO detail 按 so_id 列出全部关联 DO。 |
| MDS-R04 | 页面在已有 DO 后仍显示 Create DO。 |
| MDS-R05 | canonical create 不查询 existing DO。 |
| MDS-R06 | legacy convert 也不查询 existing DO。 |
| MDS-R07 | canonical 每次 SELECT 全部 sales_order_items。 |
| MDS-R08 | legacy 每次同样复制全部 SO items。 |
| MDS-R09 | 两路径都不接受 line selection。 |
| MDS-R10 | 两路径都不接受 per-line batch qty。 |
| MDS-R11 | DO header total 直接复制 SO total，不按本批重算。 |
| MDS-R12 | canonical 每次创建后把 SO 写 Delivery Created。 |
| MDS-R13 | legacy 创建后不更新 SO 状态。 |
| MDS-R14 | canonical 秒级编号存在同秒碰撞风险。 |
| MDS-R15 | legacy 对同 SO 固定生成相同 do_no；重复 DO 可同号。 |
| MDS-R16 | Ship 幂等按 do_no remark，legacy 同号 DO 可能互相误判已 Ship。 |
| MDS-R17 | 空 SO 可生成空 DO。 |
| MDS-R18 | SO 当前状态不是创建门，Delivered/Cancelled 等也未见阻断。 |
| MDS-R19 | platform v14 residual 的重复 `/create_do` 曾在创建时扣 product stock，但标准 cutover 会跳过已占用路径。 |

## 校验

| ID | 校验点 | 实际强度 |
|---|---|---|
| MDS-V01 | SO 必须存在 | Hard |
| MDS-V02 | SO 必须 Open | Missing |
| MDS-V03 | SO 不得 Delivered/Cancelled | Missing |
| MDS-V04 | SO 至少一行 | Missing |
| MDS-V05 | 同 SO 不得已有活动 DO | Missing |
| MDS-V06 | 新 DO qty 必须 <= remaining | Missing |
| MDS-V07 | 用户必须选择本批行/qty | Missing |
| MDS-V08 | delivery_orders.so_id DB unique | 未见；且 UI支持多行 |
| MDS-V09 | do_no 必须唯一 | UNKNOWN |
| MDS-V10 | header total 必须等于 DO 行合计 | Missing |
| MDS-V11 | canonical route 服务端 RBAC | Missing |
| MDS-V12 | 创建动作必须 POST/CSRF | Missing；GET |
| MDS-V13 | 重复请求 idempotency token | Missing |
| MDS-V14 | residual 重复路由必须被 cutover 过滤 | Bootstrap guard；非所有非标准挂载已知 |

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| `sales_orders.id` | 多 DO 共同上游 |
| `sales_order_items.qty` | 每次复制的原订单量 |
| `delivery_orders.id` | 每张 DO 独立技术键 |
| `delivery_orders.so_id` | 多 DO 聚合查询键 |
| `delivery_orders.do_no` | 路径相关编号与 Ship remark 来源 |
| `delivery_orders.delivery_date` | canonical 创建日 / legacy SO order_date |
| `delivery_orders.total_amount` | SO 总额快照，不是本批金额 |
| `delivery_orders.status` | 每张 DO 自身阶段 |
| `delivery_order_items.qty` | 每次完整复制的原 SO qty |
| Delivery Created | canonical create 已执行标签，不表示 DO 数量 |
| linked DO count | SO detail 的单据数，不是已发数量 |
| existing DO | 当前创建服务未作为 gate 的数据 |
| remaining qty | 未建模 |
| batch selection | 未建模 |
| route family | canonical 与 legacy 行为差异来源 |
| platform v14 residual | 历史全量复制+创建即扣镜像路径，通常被去重跳过 |

## 证据表

| # | 观察事实 | 强度 | 只读来源 |
|---|---|---|---|
| MDS-E01 | canonical 全量复制 SO items | 强 | `apps/sales/services.py::create_delivery_order` |
| MDS-E02 | canonical SQL 读取全部行 | 强 | `apps/sales/repository.py::fetch_so_items_for_delivery` |
| MDS-E03 | canonical 无 existing DO/status gate | 强负向 | `apps/sales/services.py` |
| MDS-E04 | legacy 固定 do_no 并全量复制 | 强 | `apps/inventory/services.py::_legacy_convert_do` |
| MDS-E05 | SO detail 查询多个关联 DO | 强 | `apps/sales/repository.py::fetch_delivery_orders_by_so` |
| MDS-E06 | 已有 DO 后仍显示 Create DO CTA | 强 | `templates/sales_order_detail.html` |
| MDS-E07 | DO DDL 对 so_id 无唯一约束 | 强负向 | `runtime/v14/legacy_support.py` |
| MDS-E08 | Ship ledger remark 由 do_no 形成 | 强 | `apps/inventory/services.py::ship_delivery_order` |
| MDS-E09 | A-003 只规定创建不扣库存 | 中等 | `docs/reports/Business_Strong_A003_Delivery_Report.md` |
| MDS-E10 | 既有 SO→DO 权威页 | 强交叉 | `../order-chain/so_to_do.md` |
| MDS-E11 | platform residual create/do_ship 可能双扣 products | 强历史 | `apps/platform/v14_residual.py` |
| MDS-E12 | business pages 先挂载，residual duplicate path 被过滤 | 强 | `bootstrap/enterprise_cutover.py`、`bootstrap/v14_residual.py` |

## UNKNOWN + 已查路径

1. **业务是否有意允许一 SO 多 DO UNKNOWN。** 已查：Sales/Inventory services、templates、business_modules、reports。
2. **生产路由中 legacy `/convert_do` 是否仍可达 UNKNOWN。** 已查：routers、residual loader、route reports。
3. **生产 DB 是否私加 so_id/do_no 唯一约束 UNKNOWN。** 已查：公开 DDL、database patches、scripts。
4. **同秒 canonical do_no 碰撞如何处理 UNKNOWN。** 已查：create service/repository、exception handlers。
5. **legacy 同号重复 DO 是否已存在 UNKNOWN。** 已查：静态路径；未读生产 DB。
6. **空 DO 后是否有补行入口 UNKNOWN。** 已查：Delivery routes/templates/services。
7. **Create DO 缺 route RBAC 是否由全局 middleware 补足 UNKNOWN。** 已查：router/bootstrap/security。
8. **两条路径的权威优先级在部署配置中是否变化 UNKNOWN。** 已查：manifest/cutover/residual docs。

## 交叉引用

- Partial delivery 权威：[`../fulfillment-deepen/partial_delivery.md`](../fulfillment-deepen/partial_delivery.md)
- SO→DO 权威：[`../order-chain/so_to_do.md`](../order-chain/so_to_do.md)
