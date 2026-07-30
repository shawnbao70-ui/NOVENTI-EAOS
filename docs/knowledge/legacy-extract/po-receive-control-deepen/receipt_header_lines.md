# 收货头行实体与 PO 行关系

**Evidence strength:** Strong（活动链）；Strong-negative（结构化 GRN 头/行）  
**Verified:** 2026-07-23  
**Authority cross-ref:** [`../procurement-receipt-deepen/goods_receipt_posting.md`](../procurement-receipt-deepen/goods_receipt_posting.md)、[`../procurement-receipt-deepen/receipt_to_stock.md`](../procurement-receipt-deepen/receipt_to_stock.md)

## Scope 与结论

本页区分 DDL 预留与活动收货事实。`purchase_receipts` 有头表 DDL（id / purchase_id / receipt_no / receipt_date / status）但活动 Receive **无 INSERT writer**；未发现 `purchase_receipt_items` / 采购 receipt lines。实际 GR 事实是 **PO 行驱动的 Inventory Ledger**：每有效行一条 `PO Receipt`，`remark='PO-{purchase_id}'` 软链 PO 头；ledger **不存** `purchase_item_id`。Finance 的 `receipts` 是 AR 收款，不得映射为 GRN。

## 业务规则（稳定 ID）

1. **RHL-R01** `purchase_receipts` DDL 仅定义 id / purchase_id / receipt_no / receipt_date / status（默认 Received）。
2. **RHL-R02** 活动 Receive 路径未见 `INSERT INTO purchase_receipts`。
3. **RHL-R03** 全库 DDL 面未见 `purchase_receipt_items` / 采购 receipt line 表。
4. **RHL-R04** 名称含 `receipt_items` 的幽灵引用（若有）不得默认当作采购收货行；需与 AR 域区分。
5. **RHL-R05** Finance `receipts` / 收款流程是客户收款，不能视为 GRN。
6. **RHL-R06** 活动 `receive_purchase` 直接 `fetch_purchase_items_for_receipt` 读 PO 行。
7. **RHL-R07** 每个有效 PO 行（正 qty + 有效 product）产生一条 `inventory_ledger`（`PO Receipt`）。
8. **RHL-R08** ledger 列集无 `purchase_item_id` / `receipt_id` FK。
9. **RHL-R09** ledger `remark = f"PO-{purchase_id}"` 软链 PO 头，非行级 FK。
10. **RHL-R10** 活动收货不生成 `receipt_no`。
11. **RHL-R11** ledger `create_time` 充当过账时间（服务端 now）。
12. **RHL-R12** ledger `product_code` / `product_name` 是过账时点快照。
13. **RHL-R13** ledger `balance_qty` 是过账后库存快照。
14. **RHL-R14** PO `status=Received` 表示头级完成，不是 GRN 头状态机。
15. **RHL-R15** 关系形态是 **一 PO → 多 ledger 行**，而非一 GRN 头 → 多 GRN 行。
16. **RHL-R16** 重复收货按 PO stage=received **与** ledger `trans_type+remark` 双检。
17. **RHL-R17** UI / Purchase360 以 PO 状态与 ledger 表示已入库；无独立 GRN 详情页。
18. **RHL-R18** 开票通过 `purchase_id` 锚 PO 头，不引用 GRN 头/行。
19. **RHL-R19** `procurement/utils.py` 可统计 `purchase_receipts` 行数（监控面），不等于活动 writer。
20. **RHL-R20** `apps/purchase/` 不存在；收货权威仅在 `apps/procurement/` + inventory 委托。

## 流程

```
purchases → purchase_items
        → receive_purchase
        → inventory / products / inventory_ledger (PO Receipt + PO-{id})
        → purchases.status = Received
```

`purchase_receipts` 与采购 receipt lines **不进入**此流程。Invoice/AP 继续从 PO 头追溯，不从 GRN。

## 校验（强 / 弱 / 缺失）

1. **RHL-V01（强）** PO 必须存在且为 open family。
2. **RHL-V02（强）** 至少存在一条 purchase item（空列表 → `no_items`）。
3. **RHL-V03（强）** inventory 行必须存在（`ensure_inventory_for_product` 失败 → `inventory_missing`）。
4. **RHL-V04（强）** status/ledger 双重判重（`already_received`）。
5. **RHL-V05（弱）** 非正 qty / 无效 product 静默 `continue`，不失败整单。
6. **RHL-V06（缺失）** 无 receipt header 必填校验（无 writer）。
7. **RHL-V07（缺失）** 无 `receipt_no` 唯一性 / 生成器。
8. **RHL-V08（缺失）** 无 receipt line → PO line FK。
9. **RHL-V09（缺失）** ledger remark 无 FK / UNIQUE 约束。
10. **RHL-V10（缺失）** 无 GRN header/line 数量守恒。
11. **RHL-V11（缺失）** 无供应商送货单号字段写入。
12. **RHL-V12（缺失）** 无结构化 receipt 状态迁移（Draft GRN → Posted 等）。
13. **RHL-V13（缺失）** 无 GRN 打印独立单据实体（仅 PO print）。
14. **RHL-V14（弱 / 监控）** row_count(`purchase_receipts`) 可观测但无业务门。

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| `purchase_receipts` | 未使用 GRN 头槽（DDL 预留） |
| `receipt_no` | DDL 预留；活动链不生成 |
| `receipt_date` | DDL 预留；活动链不写 |
| `purchase_receipts.status` | 默认 `'Received'` 的空壳字段 |
| `purchase_items.id` | PO 行键；ledger 不引用 |
| `purchase_items.purchase_id` | PO 行 → 头 |
| `purchase_items.qty` | 收货采用的数量（兼订购量） |
| `inventory_ledger.id` | **实际收货行事实主键** |
| `trans_type` | `'PO Receipt'` |
| `remark` | `'PO-{id}'` 软追溯 / 幂等键 |
| `qty` | 本次过账增量 |
| `balance_qty` | 过账后余额快照 |
| `create_time` | 收货过账时间 |
| `receipts`（Finance） | AR 收款头，**非** GRN |

## 状态词汇

| 词汇 | 实际语义 |
|---|---|
| GRN | 无活动独立实体 |
| PO Receipt | Ledger 交易类型 |
| Received | PO 头完成态 |
| receipt header | DDL 空壳 |
| receipt line（采购） | **缺失** |

## 证据表

| ID | 证据 | 强度 | 只读来源路径 |
|---|---|---|---|
| RHL-E01 | `CREATE TABLE purchase_receipts` 五字段 | 强结构 | `runtime/v14/legacy_support.py` |
| RHL-E02 | `CREATE TABLE inventory_ledger` 列集无 PO 行 FK | 强结构 | `runtime/v14/legacy_support.py` |
| RHL-E03 | Receive 主 writer：读 items → 三写 → Received | 强 | `apps/procurement/services.py`（`receive_purchase`） |
| RHL-E04 | ledger 判重 SQL：`trans_type='PO Receipt' AND remark=?` | 强 | `apps/procurement/repository.py` |
| RHL-E05 | procurement 内仅 `get_row_count("purchase_receipts")`，无 INSERT | 强负向 | `apps/procurement/utils.py`；`apps/procurement/` writer 面 |
| RHL-E06 | Finance receipts 为 AR 收款 | 强 | `apps/finance/services.py` |
| RHL-E07 | Purchase360 / detail Receive 文案指向 inventory+ledger | 强 | `templates/purchase360.html`、`purchase_detail.html` |
| RHL-E08 | A-004/A-010 报告 ledger 事实与 dual-write | 强 | `docs/reports/Business_Strong_A004_Purchase_Report.md`、`Business_Strong_A010_Purchase_Ops_Report.md` |
| RHL-E09 | goods-receipt contract 仍待定义（意图非实现） | 中 | `business_modules/procurement.md` |
| RHL-E10 | `apps/purchase/` 目录不存在 | 强负向 | `apps/` 目录枚举 |

## UNKNOWN + 已查路径

1. **生产库 `purchase_receipts` 是否有历史行 UNKNOWN。** 已查：DDL、procurement/inventory writers；未查生产 DB。
2. **历史版本是否写过 GRN 头 UNKNOWN。** 已查：residual、reports、utils row_count。
3. **`receipt_items` 动态 DDL 是否曾存在 UNKNOWN。** 已查：`legacy_support.py` CREATE 面、migrations 命名面、context360 命名面。
4. **标准部署旧 Receive 是否仍挂载 UNKNOWN。** 已查：manifest 命名面、inventory residual、procurement router。
5. **GRN 打印模板位置 UNKNOWN。** 已查：`templates/` purchase/print；documents/print 命名面 — 仅见 PO print。
6. **外部送货单号保存位置 UNKNOWN。** 已查：PO schema、attachments/documents 命名面。
7. **ledger remark 被改后的修复方法 UNKNOWN。** 已查：ledger edit/audit 命名面、repository。
8. **并发收货是否产生重复 ledger UNKNOWN。** 已查：DDL index、transaction commit、无 UNIQUE。
9. **`core/` 是否另有 GRN 实体 UNKNOWN。** 已查：`core/` 检索超时边界；procurement 调用链未见。

## 只读来源路径

- `H:\Workspace\EZAM_CRM - 9.0\apps\procurement\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\inventory\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\finance\`
- `H:\Workspace\EZAM_CRM - 9.0\templates\`
- `H:\Workspace\EZAM_CRM - 9.0\runtime\v14\legacy_support.py`
- `H:\Workspace\EZAM_CRM - 9.0\docs\reports\`
- `H:\Workspace\EZAM_CRM - 9.0\business_modules\procurement.md`
- 已查不存在：`H:\Workspace\EZAM_CRM - 9.0\apps\purchase\`
